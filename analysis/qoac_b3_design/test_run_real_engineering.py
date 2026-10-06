#!/usr/bin/env python3
"""Offline tests for run_real_engineering.py (no network, no binary).

The compiled Henkelman binary is replaced by the on-grid emulator plus
per-atom sums of a fabricated CHGCAR, so the Gate 0, arm and aggregate code
paths run end to end on synthetic fields.
Run: python3 -m unittest -q test_run_real_engineering.py
"""
from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

import run_real_engineering as rr
from ongrid import atom_map, ongrid_partition
from synthetic import make_lattice, random_field

ACF = """    #         X           Y           Z       CHARGE      MIN DIST   ATOMIC VOL
 --------------------------------------------------------------------------------
    1    0.000000    0.000000    0.000000   10.123456     1.000000    12.000000
    2    1.500000    1.500000    1.500000    7.876544     1.100000    13.000000
 --------------------------------------------------------------------------------
    VACUUM CHARGE:               0.0000
    VACUUM VOLUME:               0.0000
    NUMBER OF ELECTRONS:        18.0000
"""
BCF = """    #         X           Y           Z        CHARGE     ATOM    DISTANCE
  -------------------------------------------------------------------------
    1      0.0000      0.0000      0.0000     10.1235       1      0.0000
    2      1.5000      1.5000      1.5000      7.8765       2      0.0000
  -------------------------------------------------------------------------
"""
LOG = "  NUMBER OF BADER MAXIMA FOUND:             2\n    SIGNIFICANT MAXIMA FOUND:             2\n"


def _material(seed=3, kind="triclinic", shape=(14, 13, 15), n_atoms=4):
    rng = np.random.default_rng(seed)
    L = make_lattice(kind, rng, scale=8.0)
    ae, frac = random_field(shape, L, rng, n_atoms=n_atoms, vacuum_slab=False)
    chg = 0.3 * ae + 0.01 * ae.mean()
    return L, frac, ae, chg


def _fake_binary(chg, L, frac):
    """(charges, volnum, atom map, nbasins) as the binary would report them."""
    n = len(frac)

    def run(field):
        p = ongrid_partition(np.asarray(field).reshape(chg.shape), L, rr.VACVAL)
        am = atom_map(p, L, frac)
        q = np.bincount(am.ravel(), weights=chg.ravel(), minlength=n + 2)[1:n + 1] / chg.size
        return np.round(q, 6), p.volnum, am, p.nbasins
    return run


class Parsing(unittest.TestCase):
    def test_acf_bcf_log(self):
        np.testing.assert_allclose(rr.parse_acf(ACF, 2), [10.123456, 7.876544])
        with self.assertRaises(RuntimeError):
            rr.parse_acf(ACF, 3)
        self.assertEqual(rr.parse_bcf(BCF).shape, (2, 3))
        self.assertEqual(rr.parse_nbasins(LOG), 2)
        with self.assertRaises(RuntimeError):
            rr.parse_nbasins("nothing")


class Gate0Helpers(unittest.TestCase):
    def test_basin_argmax_ties_and_empty(self):
        f = np.array([1.0, 3.0, 3.0, 2.0, 5.0, 0.0])
        v = np.array([1, 1, 1, 2, 2, 4])          # basin 3 empty, 4 = vacuum
        np.testing.assert_array_equal(rr.basin_argmax(f, v, 3), [1, 4, -1])

    def test_match_positions_periodic(self):
        L = 4.0 * np.eye(3)
        pts = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
        tgt = np.array([[3.99999, 0.0, 4.0]])
        self.assertEqual(rr.match_positions(pts, tgt, L), 1)

    def test_gate0_identical_and_perturbed(self):
        L, frac, ae, chg = _material()
        q, vol, am, nb = _fake_binary(chg, L, frac)(ae)
        p = ongrid_partition(ae, L, rr.VACVAL)
        bcf = rr.maxima_cartesian(p.maxima, ae.shape, L)
        g0, ref = rr.gate0_record("m", ae, L, frac, vol, am, nb, bcf)
        self.assertTrue(g0["literal_run"])
        self.assertEqual(g0["fast_volnum_mismatch_voxels"], 0)
        self.assertEqual(g0["literal_volnum_mismatch_voxels"], 0)
        self.assertEqual(g0["fast_volnum_agreement"], 1.0)
        self.assertTrue(g0["fast_maxima_match"])
        self.assertEqual(g0["bcf_maxima_matched"], nb)
        bad = vol.copy(); bad.ravel()[:5] = (bad.ravel()[:5] % nb) + 1
        g1, _ = rr.gate0_record("m", ae, L, frac, bad, am, nb, bcf, literal_max_npoints=10)
        self.assertFalse(g1["literal_run"])
        self.assertIn("skipped", g1["literal_note"])
        self.assertGreater(g1["fast_volnum_mismatch_voxels"], 0)
        self.assertLess(g1["fast_volnum_agreement"], 1.0)


class ArmsEndToEnd(unittest.TestCase):
    def test_arms_and_label_arm(self):
        L, frac, ae, chg = _material(seed=5, shape=(16, 15, 17), n_atoms=5)
        binary = _fake_binary(chg, L, frac)
        ref_out = binary(ae)
        q_ref, vol, am, nb = ref_out
        g0, ref = rr.gate0_record("m", ae, L, frac, vol, am, nb, np.zeros((0, 3)))
        lab = rr.arm_l_record(chg, vol, am, q_ref, len(frac))
        self.assertTrue(lab["label_roundtrip_exact"])
        self.assertTrue(lab["label_charges_match_binary"])
        self.assertTrue(lab["vol_to_atom_is_function"])
        rows, fails = rr.run_arms("m", ref, chg.size, len(frac), g0, lab, ref_out, binary, deltas=(1e-2, 5e-2))
        self.assertEqual(fails, [])
        self.assertEqual(len(rows), 4)
        for r in rows:
            self.assertEqual(r["status"], "OK")
            self.assertEqual(r["reassigned_volnum_frac"], 0.0)
            self.assertEqual(r["reassigned_atom_frac"], 0.0)
            self.assertLessEqual(r["bader_charge_err_max_e"], 1e-12)
            self.assertLessEqual(r["linf_over_bound"], 1.0 + 1e-9)
            self.assertGreater(r["base_bytes"], 0)
            self.assertEqual(r["total_bytes"], r["base_bytes"] + r["side_bytes"])

    def test_arm_failure_is_recorded_not_raised(self):
        L, frac, ae, chg = _material(seed=6)
        good = _fake_binary(chg, L, frac)
        ref_out = good(ae)
        g0, ref = rr.gate0_record("m", ae, L, frac, ref_out[1], ref_out[2], ref_out[3], np.zeros((0, 3)))

        def broken(field):
            raise RuntimeError("Henkelman exit 1")
        rows, fails = rr.run_arms("m", ref, chg.size, len(frac), g0, {}, ref_out, broken, deltas=(1e-2,))
        self.assertEqual([r["status"] for r in rows], ["FAILED", "FAILED"])
        self.assertEqual(len(fails), 1)


def _fake_result(mid, reass=0.0, regular=True, mism=0, literal=True, status="SUCCESS", fail=False):
    rows = []
    for arm in rr.ARMS:
        for d in rr.DELTAS:
            rows.append({"material_id": mid, "arm": arm, "delta": d, "status": "OK", "error": "",
                         "base_bytes": 1000, "side_bytes": 100, "side_over_base": 0.1, "total_bytes": 1100,
                         "label_ctx_bytes_atom": 550, "reassigned_volnum_frac": reass,
                         "reassigned_atom_frac": reass, "reassigned_volnum_frac_before": 0.01,
                         "bader_charge_err_max_e": 0.0, "linf_over_bound": 0.9, "iterations": 2,
                         "encode_seconds": 1.5, "npoints": 1000})
    return {"material_id": mid, "status": status, "rows": rows,
            "gate0": {"material_id": mid, "status": "OK", "regular": regular, "R1_violations": 0,
                      "R2_violations": 0 if regular else 3, "nbasins_binary": 4, "nbasins_fast": 4,
                      "fast_volnum_agreement": 1.0 - mism / 1000, "fast_volnum_mismatch_voxels": mism,
                      "fast_atom_agreement": 1.0, "fast_atom_mismatch_voxels": 0, "fast_maxima_match": True,
                      "bcf_maxima_matched": 4, "bcf_maxima_total": 4, "literal_run": literal,
                      "literal_volnum_mismatch_voxels": 0 if literal else None,
                      "literal_vs_fast_mismatch_voxels": 0 if literal else None},
            "arm_L": {"label_charges_match_binary": True, "label_charge_err_max_e": 4e-7,
                      "label_roundtrip_exact": True, "label_ctx_bytes_atom": 550, "label_ctx_bytes_volnum": 600},
            "failures": [{"stage": "A1 delta=0.05", "error": "boom"}] if fail else []}


class Aggregate(unittest.TestCase):
    def test_summary_counts(self):
        res = [_fake_result("mp-1"), _fake_result("mp-2", reass=0.002, regular=False, mism=7, literal=False,
                                                  status="PARTIAL", fail=True)]
        s, rows, g0, fails = rr.aggregate(res, ["mp-1", "mp-2", "mp-3"])
        self.assertEqual(s["materials_expected"], 3)
        self.assertEqual(s["materials_with_results"], 2)
        self.assertEqual(s["materials_success"], 1)
        self.assertEqual(len(rows), 2 * len(rr.ARMS) * len(rr.DELTAS))
        self.assertEqual({f["stage"] for f in fails}, {"A1 delta=0.05", "missing"})
        g = s["gate0"]
        self.assertEqual(g["regular_R1_R2"], 1)
        self.assertEqual(g["fast_volnum_identical"], 1)
        self.assertEqual(g["fast_volnum_mismatch_voxels_total"], 7)
        self.assertAlmostEqual(g["fast_volnum_agreement_min"], 0.993)
        self.assertEqual((g["literal_run"], g["literal_skipped"]), (1, 1))
        a = s["arms"]["A2@0.01"]
        self.assertEqual((a["rows"], a["ok"], a["zero_reassignment_volnum"]), (2, 2, 1))
        self.assertAlmostEqual(a["max_reassigned_volnum_frac"], 0.002)
        self.assertAlmostEqual(a["median_side_over_base"], 0.1)
        self.assertAlmostEqual(a["median_total_over_label_ctx_atom"], 2.0)
        self.assertEqual(s["arm_L"]["charges_match_binary"], 2)
        for k in s:
            self.assertNotIn("pass", k.lower())
        json.dumps(s)

    def test_csv_roundtrip_and_files(self):
        res = [_fake_result("mp-1"), _fake_result("mp-2", fail=True, status="PARTIAL")]
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            for r in res:
                rr.write_material(r, td / "in" / r["material_id"])
            loaded = [json.loads(p.read_text()) for p in sorted((td / "in").rglob("*.json"))]
            s = rr.write_aggregate(loaded, ["mp-1", "mp-2"], td / "out")
            for name in ("rows.csv", "gate0.csv", "failures.csv", "SUMMARY.json"):
                self.assertTrue((td / "out" / name).exists(), name)
            rows = list(csv.DictReader((td / "out" / "rows.csv").read_text().splitlines()))
            self.assertEqual(list(rows[0].keys()), rr.ROW_FIELDS)
            self.assertEqual(len(rows), 2 * len(rr.ARMS) * len(rr.DELTAS))
            self.assertEqual(float(rows[0]["base_bytes"]), 1000)
            self.assertEqual(rows[0]["edits"], "")        # missing field -> empty cell
            per = list(csv.DictReader((td / "in" / "mp-1" / "mp-1_rows.csv").read_text().splitlines()))
            self.assertEqual(len(per), len(rr.ARMS) * len(rr.DELTAS))
            self.assertEqual(json.loads((td / "out" / "SUMMARY.json").read_text())["failures"], 1)
            self.assertEqual(s["failures"], 1)

    def test_cli_aggregate(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            rr.write_material(_fake_result("mp-1"), td / "in")
            man = td / "m.csv"
            man.write_text("material_id,task_id\nmp-1,mp-1\n")
            self.assertEqual(rr.main(["aggregate", "--manifest", str(man), "--inputs-root", str(td / "in"),
                                      "--output-dir", str(td / "out")]), 0)
            s = json.loads((td / "out" / "SUMMARY.json").read_text())
            self.assertEqual(s["materials_with_results"], 1)
            self.assertEqual(s["failures"], 0)


if __name__ == "__main__":
    unittest.main()
