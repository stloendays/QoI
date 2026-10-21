#!/usr/bin/env python3
"""Offline test of the B4 real-material arms: the compiled binary is replaced
by the vectorized on-grid transcription, which Gate 0 of QOAC-B3 showed to be
voxel-identical to the binary on regular fields."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "qoac_b3_design"))

import run_b4_engineering as b4r  # noqa: E402
from b3_correct import make_reference  # noqa: E402
from ongrid import atom_map, ongrid_partition  # noqa: E402
from synthetic import make_lattice, random_field  # noqa: E402

VAC = 1e-3


class FakeBinary:
    def __init__(self, chg, lattice, frac):
        self.chg, self.lattice, self.frac = chg, lattice, frac
        self.natoms = frac.shape[0]

    def __call__(self, ref_field):
        p = ongrid_partition(np.asarray(ref_field, float).reshape(self.chg.shape), self.lattice, VAC)
        atom = atom_map(p, self.lattice, self.frac)
        s = np.bincount(atom.ravel(), weights=self.chg.ravel(), minlength=self.natoms + 2)
        return s[1:self.natoms + 1] / self.chg.size, p.volnum, atom, p.nbasins


class TestRealArms(unittest.TestCase):
    def test_rows_and_aggregate(self):
        rng = np.random.default_rng(11)
        L = make_lattice("monoclinic", rng, scale=9.0)
        f, frac = random_field((20, 22, 18), L, rng, n_atoms=5)
        chg = f * 0.97                       # charges integrated from a different field than the partition
        ref = make_reference(f, L, VAC)
        B = FakeBinary(chg, L, frac)
        ref_out = B(f)
        natoms = frac.shape[0]
        q = ref_out[0]
        b4r.TAUS_E = (1e-2 * float(np.abs(q).max()),)
        rows, fails = b4r.run_arms_b4("syn-1", ref, chg.size, natoms, {}, {"label_roundtrip_xz_bytes_atom": 1000},
                                       ref_out, B, deltas=(1e-2,))
        self.assertFalse(fails, fails)
        self.assertEqual(len(rows), 1 + len(b4r.TAUS_E) * len(b4r.THETAS))
        for r in rows:
            self.assertEqual(r["status"], "OK")
            self.assertEqual(r["atom_changed_outside_R"], 0)
            self.assertLessEqual(r["bader_err_max_e"], r["bound_e"] + 1e-12)
        summary, out_rows, out_fails = b4r.aggregate([{"material_id": "syn-1", "rows": rows, "failures": []}],
                                                     ["syn-1"])
        self.assertEqual(summary["materials_with_rows"], 1)
        for g in summary["groups"].values():
            self.assertEqual(g["bound_violations"], 0)
            self.assertEqual(g["atom_changes_outside_R"], 0)


if __name__ == "__main__":
    unittest.main()
