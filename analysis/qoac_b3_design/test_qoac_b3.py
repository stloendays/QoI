#!/usr/bin/env python3
"""Unit tests for the QOAC-B3 prototype. Run: python3 -m pytest -q test_qoac_b3.py"""
from __future__ import annotations

import itertools
import unittest

import numpy as np

from b3_correct import (EXACT, check_constraints, correct, label_map_cost, make_reference,
                        oneshot_allowance, oneshot_levels, quantize, rel_quantize)
from ongrid import (OFFSETS, atom_map, lat_i_dist, make_stencil, ongrid_literal,
                    ongrid_partition, regularity_report, successor)
from synthetic import LATTICES, make_lattice, random_field

VAC = 1e-3


def _case(seed, kind, shape=(12, 11, 13), n_atoms=5, scale=9.0):
    rng = np.random.default_rng(seed)
    L = make_lattice(kind, rng, scale=scale)
    f, frac = random_field(shape, L, rng, n_atoms=n_atoms, vacuum_slab=bool(seed % 2))
    return L, f, frac


class LatticeWeights(unittest.TestCase):
    def test_orthorhombic_weights_are_inverse_distances(self):
        L = np.diag([4.0, 5.0, 6.0])
        n = (8, 10, 12)
        w = lat_i_dist(L, n)
        h = np.array([0.5, 0.5, 0.5])
        for d in OFFSETS:
            self.assertAlmostEqual(w[d], 1.0 / np.linalg.norm(np.array(d) * h), places=13)

    def test_weights_are_inversion_symmetric_on_skewed_cells(self):
        rng = np.random.default_rng(0)
        for kind in LATTICES:
            w = lat_i_dist(make_lattice(kind, rng), (9, 10, 11))
            for d in OFFSETS:
                self.assertAlmostEqual(w[d], w[tuple(-x for x in d)], places=12)


class FastVersusLiteral(unittest.TestCase):
    """The vectorized partition must reproduce the transcription of the
    Fortran control flow voxel for voxel on regular fields."""

    def test_random_smooth_fields(self):
        for seed, kind in itertools.product(range(4), LATTICES):
            L, f, _ = _case(seed, kind)
            self.assertTrue(regularity_report(f, L, VAC)["regular"])
            lit, nb = ongrid_literal(f, L, VAC)
            p = ongrid_partition(f, L, VAC)
            self.assertEqual(nb, p.nbasins)
            np.testing.assert_array_equal(lit, p.volnum, err_msg=f"{kind} seed {seed}")

    def test_quantized_fields_with_plateaus_and_ties(self):
        # coarse quantization creates exact ties and plateaus -> exercises the
        # strict ">" loop-order tie-break and plateau maxima
        for seed, kind in itertools.product(range(3), LATTICES):
            L, f, _ = _case(seed + 10, kind)
            for rel in (3e-3, 3e-2):
                g = quantize(f, rel * f.max())[1].reshape(f.shape)
                if not regularity_report(g, L, VAC)["regular"]:
                    continue
                lit, nb = ongrid_literal(g, L, VAC)
                p = ongrid_partition(g, L, VAC)
                np.testing.assert_array_equal(lit, p.volnum)

    def test_without_vacuum_option(self):
        L, f, _ = _case(7, "triclinic")
        lit, nb = ongrid_literal(f, L, None)
        p = ongrid_partition(f, L, None)
        np.testing.assert_array_equal(lit, p.volnum)

    def test_explicit_tie_break_first_in_loop_order(self):
        L = 6.0 * np.eye(3)
        f = np.zeros((5, 5, 5)) + 1.0
        c = (2, 2, 2)
        f[c] = 2.0
        # two face neighbours with identical value -> identical weighted value
        f[1, 2, 2] = 3.0   # offset (-1,0,0): earlier in loop order
        f[3, 2, 2] = 3.0   # offset (+1,0,0)
        st = make_stencil(L, f.shape)
        s = successor(f, st)
        self.assertEqual(s[np.ravel_multi_index(c, f.shape)], np.ravel_multi_index((1, 2, 2), f.shape))

    def test_periodic_wrap(self):
        L = 5.0 * np.eye(3)
        f = np.ones((6, 6, 6))
        f[0, 0, 0] = 5.0
        f[5, 5, 5] = 4.0
        st = make_stencil(L, f.shape)
        s = successor(f, st)
        self.assertEqual(s[np.ravel_multi_index((5, 5, 5), f.shape)], 0)

    def test_regularity_flags_vacuum_crossing(self):
        # non-vacuum negative density next to a vacuum voxel (R2)
        L = 5.0 * np.eye(3)
        V = 125.0
        rng = np.random.default_rng(1)
        f = (-0.02 - 0.01 * rng.uniform(size=(6, 6, 6))) * V   # non-vacuum, negative
        f[3, 3, 4] = 0.0            # one vacuum voxel, the global maximum
        rep = regularity_report(f, L, VAC)
        self.assertGreater(rep["R2_violations"], 0)
        self.assertFalse(rep["regular"])
        # and in this irregular case the vectorized shortcut indeed departs from
        # the literal Fortran semantics, which is why regularity is a gate
        lit, _ = ongrid_literal(f, L, VAC)
        self.assertFalse(np.array_equal(lit, ongrid_partition(f, L, VAC).volnum))


class Correction(unittest.TestCase):
    """Zero basin reassignment after correction on random smooth fields with
    several maxima on non-orthogonal lattices."""

    def _assert_identical(self, g, f, L, frac, ref, literal=False):
        p = ongrid_partition(g, L, VAC)
        np.testing.assert_array_equal(p.volnum, ref.part.volnum)
        np.testing.assert_array_equal(p.maxima, ref.part.maxima)
        np.testing.assert_array_equal(atom_map(p, L, frac), atom_map(ref.part, L, frac))
        if literal:
            lit, _ = ongrid_literal(g, L, VAC)
            np.testing.assert_array_equal(lit, ref.part.volnum)

    def test_iterative_absolute_bound(self):
        for seed, kind in itertools.product(range(3), LATTICES):
            if kind == "cubic":
                continue
            L, f, frac = _case(seed, kind, shape=(20, 18, 22), n_atoms=6)
            ref = make_reference(f, L, VAC)
            self.assertGreaterEqual(ref.part.nbasins, 2)
            for rel in (1e-4, 1e-3, 1e-2):
                eps = rel * f.max()
                g0 = quantize(f, eps)[1]
                before = ongrid_partition(g0.reshape(f.shape), L, VAC).volnum
                for tier in ("B", "S"):
                    r = correct(ref, eps, tier=tier, g0=g0)
                    self.assertLessEqual(np.max(np.abs(r.g - f)), eps * (1 + 1e-9))
                    self._assert_identical(r.g, f, L, frac, ref, literal=(rel == 1e-2 and seed == 0))
                    self.assertTrue(check_constraints(r.g, ref, tier).ok)
                if rel == 1e-2:
                    self.assertGreater(np.mean(before != ref.part.volnum), 0.0)

    def test_iterative_relative_bound(self):
        for seed, kind in itertools.product(range(3), ("hexagonal", "triclinic", "monoclinic", "sheared")):
            L, f, frac = _case(seed + 20, kind, shape=(20, 18, 22), n_atoms=6)
            ref = make_reference(f, L, VAC)
            for delta in (1e-3, 1e-2, 5e-2):
                _, g0, eps = rel_quantize(f.ravel(), delta, 1e-9 * f.max())
                r = correct(ref, eps, tier="B", g0=g0)
                self.assertTrue(np.all(np.abs(r.g.ravel() - f.ravel()) <= eps * (1 + 1e-9)))
                self._assert_identical(r.g, f, L, frac, ref)

    def test_oneshot_needs_no_iteration(self):
        for seed, kind in itertools.product(range(2), ("hexagonal", "triclinic", "sheared")):
            L, f, frac = _case(seed + 30, kind, shape=(20, 18, 22), n_atoms=6)
            ref = make_reference(f, L, VAC)
            allow = oneshot_allowance(ref)
            for mode in ("abs", "rel"):
                if mode == "abs":
                    eps = 1e-3 * f.max()
                    g0 = quantize(f, eps)[1]
                else:
                    _, g0, eps = rel_quantize(f.ravel(), 1e-2, 1e-9 * f.max())
                lv = oneshot_levels(allow, eps)
                r = correct(ref, eps, tier="B", g0=g0, level0=lv)
                self.assertEqual(r.iterations, 0, "one-shot allowance must certify without iteration")
                self._assert_identical(r.g, f, L, frac, ref)

    def test_oneshot_certifies_any_perturbation_within_allowance(self):
        # the one-shot certificate is codec-agnostic: adversarial-ish random
        # perturbations inside the allowance must never reassign a voxel
        rng = np.random.default_rng(5)
        L, f, frac = _case(41, "triclinic", shape=(16, 15, 17), n_atoms=5)
        ref = make_reference(f, L, VAC)
        allow = np.minimum(oneshot_allowance(ref), 1e-2 * f.max()).reshape(f.shape)
        for _ in range(20):
            u = rng.choice([-1.0, 1.0], size=f.shape) * rng.uniform(0.0, 1.0, f.shape) ** 0.1
            g = f + u * allow
            self._assert_identical(g, f, L, frac, ref)

    def test_robust_margin_mode(self):
        L, f, frac = _case(51, "sheared", shape=(18, 18, 18), n_atoms=5)
        ref = make_reference(f, L, VAC)
        eps = 1e-3 * f.max()
        margin = 1e-6 * f.max()
        r = correct(ref, eps, tier="B", margin=margin, vac_margin=1e-7)
        self._assert_identical(r.g, f, L, frac, ref)
        self.assertTrue(check_constraints(r.g, ref, "B", margin=margin, vac_margin=1e-7,
                                          exact=r.level.ravel() >= EXACT).ok)


class CheckerSoundness(unittest.TestCase):
    def test_passing_check_implies_identical_partition(self):
        rng = np.random.default_rng(9)
        n_pass = 0
        for trial in range(40):
            kind = LATTICES[trial % len(LATTICES)]
            L, f, _ = _case(100 + trial, kind, shape=(12, 12, 12), n_atoms=4)
            ref = make_reference(f, L, VAC)
            amp = 10 ** rng.uniform(-7, -3) * f.max()
            g = f + amp * rng.uniform(-1, 1, f.shape)
            for tier in ("B", "S"):
                if check_constraints(g, ref, tier).ok:
                    n_pass += 1
                    np.testing.assert_array_equal(ongrid_partition(g, L, VAC).volnum, ref.part.volnum)
        self.assertGreater(n_pass, 0)


class LabelMap(unittest.TestCase):
    def test_label_cost_is_positive_and_small(self):
        L, f, _ = _case(3, "hexagonal", shape=(20, 18, 22))
        ref = make_reference(f, L, VAC)
        c = label_map_cost(ref.part.volnum)
        self.assertGreater(c["ctx_bytes"], 0)
        self.assertLess(c["ctx_bytes"], f.size * 2)


if __name__ == "__main__":
    unittest.main()
