#!/usr/bin/env python3
"""Unit tests for HAP and CTP on small synthetic periodic fields (random partitions, non-orthogonal cells)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import projection_v2 as pv  # noqa: E402

qb = pv.qb
qoac = pv.qoac

LATTICES = (
    np.array([[4.1, 0.0, 0.0], [1.3, 3.7, 0.0], [0.6, -0.9, 5.2]]),          # triclinic
    np.array([[3.0, 0.0, 0.0], [-1.5, 2.598076211353316, 0.0], [0.0, 0.0, 4.8]]),  # hexagonal
)
SHAPES = ((8, 6, 10), (7, 9, 6), (6, 6, 5))
RATIOS: dict[float, list[float]] = {}  # ||V_H[c_HAP]|| / ||V_H[c_uniform]|| per mu, filled by test 3


def random_partition(shape, n_regions, rng):
    """Voronoi-like partition from random seeds under periodic minimum image (connected-ish basins)."""
    grid = np.stack(np.meshgrid(*[np.arange(n) / n for n in shape], indexing="ij"), axis=-1)
    seeds = rng.random((n_regions, 3))
    d = grid[..., None, :] - seeds[None, None, None, :, :]
    d -= np.rint(d)
    lab = np.argmin(np.sum(d * d, axis=-1), axis=-1).astype(np.int64)
    return lab


def case(seed, shape, lattice, n_regions=5):
    rng = np.random.default_rng(seed)
    labels = random_partition(shape, n_regions, rng)
    ref = 1.0 + rng.random(shape) ** 2
    x = ref + 0.05 * rng.normal(size=shape)
    side = qb.side_channel_from_field(ref, labels)
    s_h, s_rho = pv.reference_scales(ref, lattice)
    return labels, ref, x, side, s_h, s_rho


def scaled_closure(y, labels, target):
    got = qb.region_sums(y, labels)
    return float(np.max(np.abs(got - target)) / max(1.0, float(np.max(np.abs(target)))))


class MultiplierTests(unittest.TestCase):
    def test_multiplier_reproduces_historical_hartree(self):
        rng = np.random.default_rng(3)
        for lat in LATTICES:
            for shape in SHAPES + ((6, 8, 8),):
                x = rng.normal(size=shape)
                m = pv.hartree_multiplier_rfft(shape, lat)
                ref = qoac.hartree_potential_from_field(x, lat, safe=False)
                np.testing.assert_allclose(pv.apply_hartree(x, m), ref, rtol=0, atol=1e-12 * np.max(np.abs(ref)))

    def test_operator_is_symmetric(self):
        rng = np.random.default_rng(4)
        for lat in LATTICES:
            shape = (6, 8, 8)
            m = pv.hartree_multiplier_rfft(shape, lat)
            u, v = rng.normal(size=shape), rng.normal(size=shape)
            a = np.sum(pv.apply_hartree(u, m) * v); b = np.sum(u * pv.apply_hartree(v, m))
            self.assertAlmostEqual(a / b, 1.0, places=12)


class HapTests(unittest.TestCase):
    MUS = (1e-6, 1e-3, 1.0, 1e3)

    def test_1_region_sums_restored(self):
        for seed, (shape, lat) in enumerate((s, l) for s in SHAPES for l in LATTICES):
            labels, ref, x, side, s_h, s_rho = case(10 + seed, shape, lat)
            kappas = [pv.kappa_from_mu(mu, s_h, s_rho) for mu in self.MUS]
            for p in pv.HartreeAwareProjector.build_many(labels, lat, kappas):
                y = p.project(x, side.sums)
                self.assertLessEqual(scaled_closure(y, labels, side.sums), 1e-12)
                cm = qb.closure_metrics(ref, y, labels)
                self.assertLessEqual(cm["max_rel_region_sum_error_scaled"], 1e-12)

    def test_2_large_mu_converges_to_uniform(self):
        lat = LATTICES[0]; shape = SHAPES[0]
        labels, ref, x, side, s_h, s_rho = case(21, shape, lat)
        cu = qb.project_to_region_sums(x, labels, side.sums) - x
        prev = np.inf
        for mu in (1e2, 1e4, 1e6, 1e8, 1e10):
            p = pv.HartreeAwareProjector.build(labels, lat, pv.kappa_from_mu(mu, s_h, s_rho))
            ch = p.project(x, side.sums) - x
            rel = float(np.linalg.norm(ch - cu) / np.linalg.norm(cu))
            self.assertLess(rel, prev * 1.0001)
            prev = rel
        self.assertLess(prev, 1e-7)

    def test_3_optimality_against_uniform(self):
        for seed, lat in enumerate(LATTICES):
            for shape in SHAPES:
                labels, ref, x, side, s_h, s_rho = case(31 + seed, shape, lat, n_regions=6)
                cu = qb.project_to_region_sums(x, labels, side.sums) - x
                for mu in self.MUS:
                    p = pv.HartreeAwareProjector.build(labels, lat, pv.kappa_from_mu(mu, s_h, s_rho))
                    ch = p.project(x, side.sums) - x
                    jh, hh, _ = pv.objective(ch, lat, mu, s_h, s_rho)
                    ju, hu, _ = pv.objective(cu, lat, mu, s_h, s_rho)
                    self.assertLessEqual(jh, ju * (1 + 1e-10))
                    self.assertLessEqual(hh, hu * (1 + 1e-10))
                    RATIOS.setdefault(mu, []).append(np.sqrt(hh / hu))
                    # perturbation within the feasible set never lowers J
                    rng = np.random.default_rng(seed)
                    z = rng.normal(size=shape)
                    z = qb.project_to_region_sums(z, labels, np.zeros_like(side.sums))
                    for eps in (1e-3, -1e-3):
                        self.assertGreaterEqual(pv.objective(ch + eps * z, lat, mu, s_h, s_rho)[0], jh * (1 - 1e-12))

    def test_4_dense_kkt_closure(self):
        for lat in LATTICES:
            for shape in ((4, 5, 6), (5, 4, 4)):
                labels, ref, x, side, s_h, s_rho = case(41, shape, lat, n_regions=4)
                n = int(np.prod(shape))
                # dense H from the canonical function, applied to unit vectors (independent of the multiplier)
                H = np.empty((n, n))
                for k in range(n):
                    e = np.zeros(n); e[k] = 1.0
                    H[:, k] = qoac.hartree_potential_from_field(e.reshape(shape), lat, safe=False).ravel()
                act = np.flatnonzero(qb.region_counts(labels) > 0)
                A = (labels.ravel()[None, :] == act[:, None]).astype(float)
                d = (side.sums - qb.region_sums(x, labels))[act]
                for mu in self.MUS:
                    M = H.T @ H / s_h + mu * np.eye(n) / s_rho
                    K = np.block([[2.0 * M, A.T], [A, np.zeros((act.size, act.size))]])
                    sol = np.linalg.solve(K, np.concatenate([np.zeros(n), d]))
                    c_dense = sol[:n].reshape(shape)
                    p = pv.HartreeAwareProjector.build(labels, lat, pv.kappa_from_mu(mu, s_h, s_rho))
                    c = p.correction(x, side.sums)
                    np.testing.assert_allclose(c, c_dense, rtol=0, atol=1e-9 * np.max(np.abs(c_dense)))

    def test_gram_matches_literal_definition(self):
        # G_ij = sum_{region i} B_j with B_j = M^{-1} 1_j (literal, G=0 included), compared on c
        lat = LATTICES[1]; shape = (6, 6, 5)
        labels, ref, x, side, s_h, s_rho = case(51, shape, lat)
        mu = 0.1; kappa = pv.kappa_from_mu(mu, s_h, s_rho)
        m2 = pv.hartree_multiplier_rfft(shape, lat) ** 2
        inv = 1.0 / (m2 + kappa)
        act = np.flatnonzero(qb.region_counts(labels) > 0)
        B = [np.fft.irfftn(np.fft.rfftn((labels == j).astype(float)) * inv, s=shape, axes=(0, 1, 2)) for j in act]
        G = np.array([[np.sum(Bj[labels == i]) for Bj in B] for i in act])
        lam = np.linalg.solve(G, (side.sums - qb.region_sums(x, labels))[act])
        c_lit = sum(l * Bj for l, Bj in zip(lam, B))
        c = pv.HartreeAwareProjector.build(labels, lat, kappa).correction(x, side.sums)
        np.testing.assert_allclose(c, c_lit, rtol=0, atol=1e-8 * np.max(np.abs(c_lit)))

    def test_zero_mu_limit_well_posed(self):
        lat = LATTICES[0]; shape = SHAPES[1]
        labels, ref, x, side, s_h, s_rho = case(61, shape, lat)
        p0 = pv.HartreeAwareProjector.build(labels, lat, 0.0)
        y = p0.project(x, side.sums)
        self.assertLessEqual(scaled_closure(y, labels, side.sums), 1e-12)
        self.assertTrue(np.isfinite(p0.condition))

    def test_empty_region_ignored(self):
        lat = LATTICES[0]; shape = SHAPES[0]
        labels, ref, x, side, s_h, s_rho = case(71, shape, lat)
        labels = labels + 1  # label 0 unpopulated
        side = qb.side_channel_from_field(ref, labels)
        p = pv.HartreeAwareProjector.build(labels, lat, pv.kappa_from_mu(1.0, s_h, s_rho))
        self.assertEqual(p.active.tolist(), list(range(1, int(labels.max()) + 1)))
        self.assertLessEqual(scaled_closure(p.project(x, side.sums), labels, side.sums), 1e-12)

    def test_side_channel_roundtrip(self):
        side = qb.BasinSideChannel(np.array([1.5, -2.0, 3.25]))
        blob = pv.hap_side_channel_bytes(side, 0.125)
        self.assertEqual(len(blob), len(side.to_bytes()) + 8)
        got, k = pv.parse_hap_side_channel(blob)
        np.testing.assert_array_equal(got.sums, side.sums); self.assertEqual(k, 0.125)


class CtpTests(unittest.TestCase):
    def test_decisions_and_bytes(self):
        lat = LATTICES[0]
        labels, ref, x, side, s_h, s_rho = case(81, SHAPES[0], lat)
        proj = lambda f: qb.project_to_region_sums(f, labels, side.sums)
        nside = len(side.to_bytes())
        f, extra, dec = pv.certify_then_project(x, lambda f: True, proj, nside)
        self.assertEqual((dec, extra), ("unprojected", 1)); np.testing.assert_array_equal(f, x)
        f, extra, dec = pv.certify_then_project(x, lambda f: False, proj, nside)
        self.assertEqual((dec, extra), ("projected", 1 + nside))
        self.assertLessEqual(scaled_closure(f, labels, side.sums), 1e-12)


if __name__ == "__main__":
    prog = unittest.main(verbosity=2, exit=False)
    for mu, r in sorted(RATIOS.items()):
        print(f"Hartree-norm ratio HAP/uniform  mu={mu:g}: min {min(r):.4f} median {np.median(r):.4f} max {max(r):.4f} (n={len(r)})")
    raise SystemExit(0 if prog.result.wasSuccessful() else 1)
