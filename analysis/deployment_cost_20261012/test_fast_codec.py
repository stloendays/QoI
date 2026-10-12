#!/usr/bin/env python3
"""fast_codec reproduces the reference QOAC-H v0.2 / QOAC v0.3 implementations."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fast_codec as F  # noqa: E402
v02, v3 = F.v02, F.v3

SHAPES = [(12, 14, 16), (11, 13, 15), (16, 9, 20), (10, 10, 7), (24, 18, 30), (45, 48, 50), (56, 96, 108)]


def lattice(seed):
    r = np.random.default_rng(seed)
    a = np.diag(r.uniform(4, 12, 3)) + r.uniform(-1.5, 1.5, (3, 3)) * (seed % 2)
    return a


def field(shape, seed):
    r = np.random.default_rng(seed)
    x = r.random(shape)
    k = np.fft.fftn(x); k *= np.exp(-0.01 * np.arange(x.size).reshape(shape) % 7)
    return np.real(np.fft.ifftn(k)) + 1.0


class T(unittest.TestCase):
    def test_metric_and_topology_bit_identical(self):
        for n, shape in enumerate(SHAPES):
            lat = lattice(n)
            np.testing.assert_array_equal(F.conservative_g2(shape, lat), v02.conservative_g2(shape, lat))
            ref = v02.build_topology(shape, lat, 32)
            got = F.Orbits(shape, lat, 32).to_reference(lat)
            for name in ("rep_flat", "partner_flat", "self_conjugate", "q", "shell_ids", "g2_safe_rep"):
                np.testing.assert_array_equal(getattr(got, name), getattr(ref, name), err_msg=f"{shape} {name}")
            self.assertEqual(got.g2_safe_max, ref.g2_safe_max)

    def test_streaming_layout(self):
        if F._nb is None:
            self.skipTest("numba path only")
        for n, shape in enumerate(SHAPES):
            lat = lattice(n); ref = v02.build_topology(shape, lat, 32)
            ax, ay, az = (v02._freq_axis(k).astype(np.float64) for k in shape)
            nq = [k // 2 if k % 2 == 0 else -1 for k in shape]
            g2c, shell, gmax, counts = F._stream_layout(*shape, v02.reciprocal_metric(lat), ax, ay, az, *nq, 32)
            self.assertEqual(gmax, ref.g2_safe_max)
            np.testing.assert_array_equal(shell[shell >= 0], ref.shell_ids)
            np.testing.assert_array_equal(counts, np.bincount(ref.shell_ids, minlength=32))

    def test_law_stream_and_decode(self):
        for n, shape in enumerate(SHAPES[:5]):
            lat, x = lattice(n), field(shape, n)
            for alpha in (1e-6, 1e-3, 1e-1):
                ref, _ = v02.encode_prepared(v02.prepare_field(x, lat), alpha=alpha, beta=2.0, zlib_level=6)
                self.assertEqual(F.encode_law(x, lat, alpha), ref)
                a, b = F.decode_law(ref), v02.decode_blob(ref)[0]
                self.assertLess(np.max(np.abs(a - b)), 1e-13 * np.max(np.abs(b)))

    def test_operational_decode(self):
        for n, shape in enumerate(SHAPES[:3]):  # A3 analysis is slow; small grids suffice
            lat, x = lattice(n), field(shape, n)
            rh, _ = v02.reference_hartree_rms(x, lat)
            an = v3.analyze(x, lat, prior="operator", reference_historical_rms=rh, d_floor_rel=1e-3 * 1e-16 / 32)
            for tau in (1e-4, 1e-6):
                blob = v3.encode(an, v3.select(an, tau))
                a, b = F.decode_operational(blob), v3.decode(blob)
                self.assertLess(np.max(np.abs(a - b)), 1e-13 * np.max(np.abs(b)))


class TNumpyPath(T):
    """The same checks on the numpy fallback (no numba)."""
    def setUp(self):
        self._nb = F._nb; F._nb = None

    def tearDown(self):
        F._nb = self._nb


if __name__ == "__main__":
    unittest.main()
