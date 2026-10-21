#!/usr/bin/env python3
"""Unit tests for QOAC-B4 budgeted leaf relaxation (synthetic fields only)."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "qoac_b3_design"))

from b3_correct import correct, make_reference, rel_quantize  # noqa: E402
from b4_relax import (Budget, atom_charges, changed_only_in_R, correct_budgeted,  # noqa: E402
                      reference_leaves, remap_volnum)
from ongrid import atom_map, ongrid_partition  # noqa: E402
from synthetic import make_lattice, random_field  # noqa: E402

VAC = 1e-3
SHAPE = (22, 20, 24)


def case(seed: int, kind: str = "triclinic", slab: bool = False):
    rng = np.random.default_rng(seed)
    L = make_lattice(kind, rng, scale=9.0)
    f, frac = random_field(SHAPE, L, rng, n_atoms=int(rng.integers(4, 7)), vacuum_slab=slab)
    ref = make_reference(f, L, VAC)
    amap = atom_map(ref.part, L, frac).ravel()
    charge = f.ravel() / f.size
    return L, f, frac, ref, amap, charge


def run(ref, amap, charge, natoms, delta, limit):
    _, g0, eps = rel_quantize(ref.f, delta, 1e-9 * ref.f.max())
    bud = Budget.make(amap, charge, limit, natoms)
    return correct_budgeted(ref, eps, bud, natoms, g0=g0), g0, eps


class TestB4(unittest.TestCase):
    def test_leaves_exclude_successors(self):
        _, _, _, ref, _, _ = case(1)
        leaf = reference_leaves(ref)
        s = ref.part.succ
        moving = s != np.arange(s.size)
        self.assertFalse(np.any(leaf[s[moving]]))
        self.assertTrue(leaf.any())

    def test_guarantee_holds(self):
        for seed, kind, slab in [(2, "triclinic", False), (3, "hexagonal", True), (4, "cubic", False)]:
            L, f, frac, ref, amap, charge = case(seed, kind, slab)
            natoms = frac.shape[0]
            q_ref = atom_charges(charge, amap, natoms)
            for delta in (1e-2, 5e-2):
                tau = 1e-2 * float(np.abs(q_ref).max())
                for theta in (0.0, 0.5):
                    r, _, eps = run(ref, amap, charge, natoms, delta, theta * tau)
                    p = ongrid_partition(r.g, L, VAC)
                    dec_atom = atom_map(p, L, frac).ravel()
                    with self.subTest(seed=seed, delta=delta, theta=theta):
                        self.assertEqual(p.nbasins, ref.part.nbasins)
                        self.assertEqual(set(p.maxima.tolist()), set(ref.part.maxima.tolist()))
                        self.assertTrue(changed_only_in_R(remap_volnum(p, ref.part), ref.part.volnum, r.relaxed))
                        dq = np.abs(atom_charges(charge, dec_atom, natoms) - q_ref)
                        self.assertLessEqual(r.max_atom_bound_e, theta * tau + 1e-15)
                        self.assertLessEqual(float(dq.max()), r.max_atom_bound_e + 1e-12)
                        err = np.abs(r.g.ravel() - ref.f)
                        self.assertTrue(np.all(err <= np.broadcast_to(eps, err.shape) * (1 + 1e-9)))
                        if theta == 0.0:
                            self.assertTrue(np.array_equal(dec_atom, amap))

    def test_relaxation_never_costs_side_bytes_on_average(self):
        """Descriptive sanity check: with a generous budget B4 should need no
        more side information than B3 on most cases (not a guarantee)."""
        wins = 0
        n = 0
        for seed in (5, 6, 7):
            L, f, frac, ref, amap, charge = case(seed)
            natoms = frac.shape[0]
            q_ref = atom_charges(charge, amap, natoms)
            _, g0, eps = rel_quantize(ref.f, 1e-2, 1e-9 * ref.f.max())
            b3 = correct(ref, eps, tier="B", g0=g0)
            r, _, _ = run(ref, amap, charge, natoms, 1e-2, 0.5 * 1e-2 * float(np.abs(q_ref).max()))
            wins += int(r.side_bytes <= b3.side_bytes)
            n += 1
        self.assertGreaterEqual(wins, 2)


if __name__ == "__main__":
    unittest.main()
