"""The criteria evaluator reproduces HB v2's reported confirmatory numbers (P2, N = 48) and handles failures."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import evaluate_criteria as ev  # noqa: E402

P2 = HERE.parent / "qoac_hb_v2" / "results" / "P2_CONFIRMATORY_MANIFEST"
P2_MANIFEST = HERE.parent / "fresh_population_20261006" / "P2_CONFIRMATORY_MANIFEST.csv"


class TestReproducesHBv2(unittest.TestCase):
    """analysis/qoac_hb_v2/results/P2_CONFIRMATORY_MANIFEST/RESULTS.md:
    1. 48/48; 2. median 1.000, CI [1.000, 1.000]; 3. 48/48 wins, median 1.317, CI [1.269, 1.360], min 1.096."""

    @classmethod
    def setUpClass(cls):
        ids = pd.read_csv(P2_MANIFEST, dtype={"material_id": str})["material_id"].tolist()
        cls.r = ev.evaluate(P2, ids)

    def test_criterion_1(self):
        c = self.r["criterion_1"]
        self.assertEqual((c["value"], c["n"], c["required"], c["pass"]), (48, 48, 46, True))

    def test_criterion_2(self):
        c = self.r["criterion_2"]
        self.assertEqual(c["n"], 48)
        self.assertEqual([round(c[k], 3) for k in ("median", "ci_low", "ci_high")], [1.0, 1.0, 1.0])
        self.assertTrue(c["pass"])

    def test_criterion_3(self):
        c = self.r["criterion_3"]
        self.assertEqual((c["wins"], c["n"], c["required_wins"]), (48, 48, 36))
        self.assertEqual([round(c[k], 3) for k in ("median", "ci_low", "ci_high", "min")], [1.317, 1.269, 1.360, 1.096])
        self.assertTrue(c["pass"])
        self.assertEqual(self.r["verdict"], "PASS")


class TestDenominators(unittest.TestCase):
    def test_required_counts(self):
        self.assertEqual([ev.required(n, ev.C1_FRACTION) for n in (48, 32, 17, 12)], [46, 31, 17, 12])
        self.assertEqual([ev.required(n, ev.C3_FRACTION) for n in (48, 32, 17, 12)], [36, 24, 13, 9])

    def test_failed_material_counts_against(self):
        rows, mats = [], []
        for i, m in enumerate(["a", "b", "c", "d"]):
            ok = m != "d"
            mats.append({"material_id": m, "status": "SUCCESS" if ok else "FAILED"})
            for t in (0.001, 0.0001, 1e-05):
                for b, cr in (("R3", 300.0 + i), ("J", 200.0), ("T1", 150.0), ("GF", 20.0)):
                    rows.append({"material_id": m, "base": b, "tau_bader": t, "best_joint_post": "none" if ok else "",
                                 "best_joint_cr": cr if ok else np.nan, "hartree_only_cr": cr if ok else np.nan,
                                 "joint_overhead": 1.0 if ok else np.nan})
        with tempfile.TemporaryDirectory() as td:
            pd.DataFrame(rows).to_csv(Path(td) / "joint_v2_best_post.csv", index=False)
            pd.DataFrame(mats).to_csv(Path(td) / "materials.csv", index=False)
            r = ev.evaluate(Path(td), ["a", "b", "c", "d"])
        self.assertEqual((r["criterion_1"]["value"], r["criterion_1"]["required"]), (3, 4))
        self.assertFalse(r["criterion_1"]["pass"])
        self.assertEqual((r["criterion_3"]["wins"], r["criterion_3"]["required_wins"]), (3, 3))
        self.assertEqual(r["criterion_2"]["n"], 3)
        self.assertEqual(r["not_analysed"], {"d": "FAILED"})
        self.assertEqual(r["verdict"], "FAIL")


if __name__ == "__main__":
    unittest.main()
