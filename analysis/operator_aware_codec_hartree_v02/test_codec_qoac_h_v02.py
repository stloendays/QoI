#!/usr/bin/env python3
from __future__ import annotations

import unittest

import numpy as np

import codec_qoac_h_v02 as q


class QoacHV02Tests(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(7)
        self.field = 2.0 + 0.2 * rng.normal(size=(8, 10, 12))
        self.lattice = np.array([
            [5.1, 0.4, 0.2],
            [0.1, 6.3, 0.5],
            [0.3, 0.2, 7.7],
        ])

    def test_orbit_partition_and_self_count(self):
        prepared = q.prepare(self.field, self.lattice, shell_count=8)
        geometry = prepared.geometry
        expected = (self.field.size + int(geometry.self_mask.sum())) // 2
        self.assertEqual(geometry.canonical_flat.size, expected)
        self.assertEqual(int(geometry.self_mask.sum()), 8)

    def test_alias_safe_g2_is_partner_invariant(self):
        prepared = q.prepare(self.field, self.lattice, shell_count=8)
        geometry = prepared.geometry
        partner_g2 = q.alias_safe_g2_for_flat(
            geometry.partner_flat, geometry.shape, self.lattice
        )
        np.testing.assert_allclose(
            geometry.g2_cons, partner_g2, rtol=1e-13, atol=1e-13
        )

    def test_non_nyquist_g2_equals_continuum_value(self):
        prepared = q.prepare(self.field, self.lattice, shell_count=8)
        geometry = prepared.geometry
        i, j, k = q._coords_from_flat(geometry.canonical_flat, geometry.shape)
        nx, ny, nz = geometry.shape
        nyquist = (
            (i == nx // 2)
            | (j == ny // 2)
            | (k == nz // 2)
        )
        f1 = np.fft.fftfreq(nx) * nx
        f2 = np.fft.fftfreq(ny) * ny
        f3 = np.fft.fftfreq(nz) * nz
        a, b, c = f1[i], f2[j], f3[k]
        B = 2.0 * np.pi * np.linalg.inv(self.lattice).T
        M = B @ B.T
        direct = (
            M[0, 0] * a * a
            + M[1, 1] * b * b
            + M[2, 2] * c * c
            + 2 * M[0, 1] * a * b
            + 2 * M[0, 2] * a * c
            + 2 * M[1, 2] * b * c
        )
        np.testing.assert_allclose(
            geometry.g2_cons[~nyquist], direct[~nyquist], rtol=1e-13, atol=1e-13
        )

    def test_roundtrip_is_exactly_hermitian_and_preserves_dc(self):
        prepared = q.prepare(self.field, self.lattice, shell_count=8)
        blob, _ = q.encode_prepared(prepared, alpha=1e-2, beta=2.0, zlib_level=1)
        recon, spectrum, _, stats = q.decode_blob(
            blob, return_spectrum=True, geometry=prepared.geometry
        )
        geometry = prepared.geometry
        flat = spectrum.ravel()
        np.testing.assert_array_equal(
            flat[geometry.partner_flat],
            np.conj(flat[geometry.canonical_flat]),
        )
        self.assertEqual(
            float(np.max(np.abs(flat[geometry.canonical_flat[geometry.self_mask]].imag))),
            0.0,
        )
        self.assertLess(stats["max_ifft_imag"], 1e-12)
        self.assertAlmostEqual(float(np.mean(recon)), float(np.mean(self.field)), places=12)

    def test_standalone_and_cached_geometry_decode_match(self):
        prepared = q.prepare(self.field, self.lattice, shell_count=8)
        blob, _ = q.encode_prepared(prepared, alpha=1e-2, beta=2.0, zlib_level=1)
        a, fa, _, _ = q.decode_blob(blob, True, geometry=prepared.geometry)
        b, fb, _, _ = q.decode_blob(blob, True)
        np.testing.assert_allclose(a, b, rtol=0.0, atol=0.0)
        np.testing.assert_allclose(fa, fb, rtol=0.0, atol=0.0)

    def test_all_zero_shell_path_and_alpha_dependence(self):
        prepared = q.prepare(self.field, self.lattice, shell_count=8)
        fine, _ = q.encode_prepared(prepared, alpha=1e-3, beta=2.0, zlib_level=1)
        coarse, _ = q.encode_prepared(prepared, alpha=1e6, beta=2.0, zlib_level=1)
        r1, _, _ = q.decode_blob(fine, geometry=prepared.geometry)
        r2, _, _ = q.decode_blob(coarse, geometry=prepared.geometry)
        self.assertGreater(float(np.max(np.abs(r1 - r2))), 0.0)
        self.assertLess(len(coarse), len(fine))

    def test_conservative_hartree_norm_is_finite(self):
        prepared = q.prepare(self.field, self.lattice, shell_count=8)
        blob, _ = q.encode_prepared(prepared, alpha=1e-2, beta=2.0, zlib_level=1)
        _, spectrum, _, _ = q.decode_blob(
            blob, return_spectrum=True, geometry=prepared.geometry
        )
        value = q.conservative_hartree_relative(prepared, spectrum)
        self.assertTrue(np.isfinite(value) and value >= 0.0)


if __name__ == "__main__":
    unittest.main()
