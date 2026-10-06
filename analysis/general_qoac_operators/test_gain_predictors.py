#!/usr/bin/env python3
from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gain_predictors as gp  # noqa: E402
import operators as ops  # noqa: E402

LATTICE = np.array([[5.0, 0.2, 0.1], [0.4, 6.0, 0.3], [0.2, 0.5, 7.0]])
SHAPE = (24, 20, 28)


def synthetic_field(seed=7):
    """Random real field with a power-law spectrum (smooth, density-like decay)."""
    rng = np.random.default_rng(seed)
    x = rng.normal(size=SHAPE)
    _, g2 = ops.reciprocal_vectors_rfft(SHAPE, LATTICE)
    f = np.fft.rfftn(x) / (1.0 + g2) ** 2
    return np.fft.irfftn(f, s=SHAPE, axes=(0, 1, 2)) + 1.0


class LaplaceECSQTests(unittest.TestCase):
    def test_matches_monte_carlo(self):
        rng = np.random.default_rng(20261006)
        x = rng.laplace(scale=1.0 / math.sqrt(2.0), size=4_000_000)     # unit variance
        for r in (0.05, 0.3, 1.0, 2.0, 4.0, 8.0):
            k = np.rint(x / r)
            _, cnt = np.unique(k, return_counts=True)
            p = cnt / cnt.sum()
            h_mc = float(-np.sum(p * np.log2(p)))
            mse_mc = float(np.mean((x - k * r) ** 2))
            se = float(np.std((x - k * r) ** 2) / math.sqrt(x.size))
            H, M = gp.laplace_ecsq_exact(np.array([r]))
            with self.subTest(r=r):
                self.assertLess(abs(H[0] - h_mc), 3e-3)
                self.assertLess(abs(M[0] - mse_mc), 5 * se + 1e-12)

    def test_limits(self):
        H, M = gp.laplace_ecsq_exact(np.array([1e-6, 1e-4, 1e3]))
        h_inf = math.log2(math.sqrt(2.0) * math.e)
        self.assertLess(abs(H[0] - (h_inf - math.log2(1e-6))), 1e-5)
        self.assertLess(abs(M[0] / (1e-12 / 12.0) - 1.0), 1e-6)
        self.assertLess(abs(M[1] / (1e-8 / 12.0) - 1.0), 1e-4)
        self.assertLess(H[2], 1e-100)
        self.assertLess(abs(M[2] - 1.0), 1e-12)

    def test_series_and_closed_form_agree(self):
        r = np.array([0.5 * math.sqrt(2.0) * (1 - 1e-9), 0.5 * math.sqrt(2.0) * (1 + 1e-9)])
        _, M = gp.laplace_ecsq_exact(r)
        self.assertLess(abs(M[1] / M[0] - 1.0), 1e-7)

    def test_table_matches_exact(self):
        lr = np.log(np.logspace(-9, 5, 5001)) + 1e-4
        H, M = gp.ecsq(lr)
        He, Me = gp.laplace_ecsq_exact(np.exp(lr))
        self.assertLess(float(np.max(np.abs(H - He))), 1e-6)
        self.assertLess(float(np.max(np.abs(M / Me - 1.0))), 1e-6)


class PredictorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = gp.spectrum_model(synthetic_field(), LATTICE, bins=64)
        cls.orbit = gp.orbit_model(SHAPE, LATTICE)

    def test_grouping_preserves_orbits(self):
        topo, m, n, safe = gp._orbit_arrays(SHAPE, LATTICE)
        self.assertEqual(int(self.model.count.sum()), topo.rep_flat.size)
        self.assertEqual(float(np.sum(self.model.count * self.model.n)), float(n.sum()))

    def test_highrate_matches_diagnosis_formula(self):
        """(a) for power laws equals the D1 expression of run_diagnosis.theory_rows."""
        topo, m, n, safe = gp._orbit_arrays(SHAPE, LATTICE)
        q = topo.q
        mean_lq = float(np.sum(n * np.log(q)) / np.sum(n))
        def d1(b, wexp):
            return -2 * b * mean_lq + math.log(float(np.sum((m * n * np.power(q, 2 * b + wexp))[safe])))
        lw = gp.log_weight(ops.hartree_field().weight, self.orbit)
        ratio = gp.highrate_rmse_ratio(self.orbit, lw, gp.power_law(1.0)(self.orbit), gp.power_law(0.0)(self.orbit))
        self.assertLess(abs(ratio / math.exp(0.5 * (d1(1.0, -2.0) - d1(0.0, -2.0))) - 1.0), 1e-9)

    def test_finite_rate_approaches_highrate(self):
        """As Delta/sigma -> 0 the finite-rate matched-rate ratio converges to the high-rate ratio."""
        for op, (ba, bb) in ((ops.hartree_field(), (1.0, 0.0)), (ops.hartree_potential(), (2.0, 0.0)),
                             (ops.density_gradient(), (-1.0, 0.0))):
            lw = gp.log_weight(op.weight, self.model)
            ua, ub = gp.power_law(ba)(self.model), gp.power_law(bb)(self.model)
            hr = gp.highrate_rmse_ratio(self.model, lw, ua, ub)
            errs = []
            for tau in (1e-3, 1e-5, 1e-7):
                res = gp.finite_rate_gain(self.model, lw, ua, ub, tau)
                errs.append(abs(res["matched_rate_rmse_ratio"] / hr - 1.0))
            with self.subTest(op=op.name):
                self.assertLess(errs[-1], 1e-4)
                self.assertLess(errs[-1], errs[0])

    def test_dead_zone_increases_with_alpha(self):
        lw = gp.log_weight(ops.hartree_field().weight, self.model)
        lu = gp.power_law(1.0)(self.model)
        dz = [gp.finite_rate_point(self.model, lw, lu, la)["dead_zone_fraction"] for la in (-20, -10, -5, 0)]
        self.assertTrue(all(a <= b for a, b in zip(dz, dz[1:])))

    def test_operator_optimal_equals_power_law(self):
        lw = gp.log_weight(ops.hartree_potential().weight, self.orbit)
        a = gp.highrate_rmse_ratio(self.orbit, lw, gp.operator_optimal(ops.hartree_potential().weight)(self.orbit),
                                   gp.blind()(self.orbit))
        b = gp.highrate_rmse_ratio(self.orbit, lw, gp.power_law(2.0)(self.orbit), gp.blind()(self.orbit))
        self.assertLess(abs(a / b - 1.0), 1e-12)


if __name__ == "__main__":
    unittest.main()
