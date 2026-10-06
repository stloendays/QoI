#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ANALYSIS = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ANALYSIS / "operator_aware_codec_hartree_v02"))
sys.path.insert(0, str(ANALYSIS / "general_qoac_electric_field"))

import operators as ops  # noqa: E402
import codec_qoac_h_v02 as qoac  # noqa: E402
import electric_field_operator as ef  # noqa: E402

LATTICES = (
    np.array([[5.0, 0.2, 0.1], [0.4, 6.0, 0.3], [0.2, 0.5, 7.0]]),
    np.array([[4.0, 0.0, 0.0], [-2.0, 3.4641, 0.0], [0.3, -0.2, 9.0]]),
)
SHAPES = ((8, 7, 10), (6, 9, 8), (7, 9, 11), (10, 8, 6))
RTOL = 1e-10


def _cases():
    rng = np.random.default_rng(20261006)
    for lat in LATTICES:
        for shape in SHAPES:
            x = rng.normal(size=shape) + 3.0
            e = 1e-3 * rng.normal(size=shape)
            yield lat, shape, x, e


class OperatorMetricTests(unittest.TestCase):
    def test_spectral_metrics_match_explicit_realspace(self):
        for op in ops.standard_operators(gaussian_sigmas=(0.3, 0.8)):
            for lat, shape, x, e in _cases():
                ref = ops.reference_energies(x, lat, op)
                rel = ops.relative_error(e, lat, op, ref)
                for variant, safe in (("safe", True), ("historical", False)):
                    explicit = ops.explicit_realspace_rms(e, lat, op, safe) / ops.explicit_realspace_rms(x, lat, op, safe)
                    with self.subTest(op=op.label, shape=shape, variant=variant):
                        self.assertLess(abs(rel[variant] / explicit - 1.0), RTOL)

    def test_energy_is_parseval_of_realspace(self):
        for op in ops.standard_operators():
            for lat, shape, x, _ in _cases():
                n = int(np.prod(shape))
                for variant, safe in (("safe", True), ("historical", False)):
                    y = ops.apply_realspace(x, lat, op, safe)
                    with self.subTest(op=op.label, shape=shape, variant=variant):
                        self.assertLess(abs(ops.operator_energy(x, lat, op, variant) / (n * np.sum(y * y)) - 1.0), RTOL)

    def test_hartree_potential_reproduces_frozen_v02(self):
        op = ops.hartree_potential()
        for lat, shape, x, e in _cases():
            rh, rs = qoac.reference_hartree_rms(x, lat)
            frozen = qoac.hartree_error_metrics(e, lat, rh, rs)
            mine = ops.legacy_relative_error(e, lat, op, ops.reference_energies(x, lat, op))
            for a, b in zip(mine, frozen):
                self.assertLess(abs(a / b - 1.0), 1e-12)

    def test_hartree_field_reproduces_frozen_electric_field(self):
        op = ops.hartree_field()
        for lat, shape, x, e in _cases():
            frozen = ef.relative_error(e, lat, *ef.reference_energies(x, lat))
            mine = ops.legacy_relative_error(e, lat, op, ops.reference_energies(x, lat, op))
            for a, b in zip(mine, frozen):
                self.assertLess(abs(a / b - 1.0), 1e-12)

    def test_historical_variants_agree_on_orthogonal_or_odd_grids(self):
        rng = np.random.default_rng(5)
        cases = ((np.diag([4.0, 5.0, 6.0]), (8, 10, 12)), (LATTICES[0], (7, 9, 11)))
        for op in ops.standard_operators():
            for lat, shape in cases:
                if op.n_components > 1 and shape[0] % 2 == 0:
                    continue
                x = rng.normal(size=shape)
                a = ops.operator_energy(x, lat, op, "historical")
                b = ops.operator_energy(x, lat, op, "historical_spectral")
                self.assertLess(abs(a / b - 1.0), 1e-12)

    def test_weight_matches_amplitudes(self):
        lat, shape = LATTICES[0], (8, 7, 10)
        gvec, g2 = ops.reciprocal_vectors_rfft(shape, lat)
        for op in ops.standard_operators(gaussian_sigmas=(0.4,)):
            mask = op.support(g2) & (g2 > 0)
            s = sum(np.abs(a) ** 2 for a in op.amplitudes(gvec, g2))
            r = s[mask] / op.weight(g2)[mask]
            self.assertLess(float(np.ptp(r) / np.mean(r)), 1e-12, op.label)

    def test_constant_field(self):
        x = np.ones((7, 8, 9))
        lat = np.eye(3) * 5.0
        for op in (ops.hartree_potential(), ops.hartree_field(), ops.density_gradient(), ops.density_laplacian()):
            self.assertLess(ops.operator_energy(x, lat, op, "historical"), 1e-20)


if __name__ == "__main__":
    unittest.main()
