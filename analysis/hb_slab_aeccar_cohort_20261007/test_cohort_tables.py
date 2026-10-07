"""Consistency of the frozen cohort tables with the selection rule (stdlib unittest + pandas; no network, no baderkit).

Checks manifest.csv, aeccar_sources.csv and selection/ against PROTOCOL.md section 2: one entry per reduced formula,
at most six per upload, no excluded id or formula, every entry with AECCAR0 + AECCAR2 on the CHGCAR grid that passed
the input QC, N = accepted rows <= 32, and the slab adapter reads the table.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
SEL = HERE / "selection"
ADAPTER = HERE.parent / "qoac_hb_slab_20261007" / "run_joint_slab.py"


def load_adapter():
    if "run_joint_slab" in sys.modules:
        return sys.modules["run_joint_slab"]
    spec = importlib.util.spec_from_file_location("run_joint_slab", ADAPTER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["run_joint_slab"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestCohortTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.man = pd.read_csv(HERE / "manifest.csv", dtype=str)
        cls.src = pd.read_csv(HERE / "aeccar_sources.csv", dtype=str)
        cls.att = pd.read_csv(SEL / "attempts.csv", dtype=str)
        cls.log = json.loads((SEL / "selection_log.json").read_text(encoding="utf-8"))
        cls.ex_ids = set(pd.read_csv(SEL / "exclusion_ids.csv", dtype=str).id)
        cls.ex_f = set(pd.read_csv(SEL / "exclusion_formulas.csv", dtype=str).reduced_formula)

    def test_sizes(self):
        n = len(self.man)
        self.assertLessEqual(n, 32)
        self.assertEqual(n, self.log["N"])
        self.assertEqual(n, int((self.att.decision == "accept").sum()))
        self.assertEqual(len(self.src), n)

    def test_hashes_match_log(self):
        for name, path in (("manifest.csv", HERE / "manifest.csv"), ("aeccar_sources.csv", HERE / "aeccar_sources.csv"),
                           ("exclusion_ids.csv", SEL / "exclusion_ids.csv"),
                           ("exclusion_formulas.csv", SEL / "exclusion_formulas.csv")):
            data = path.read_bytes().replace(b"\r\n", b"\n")
            self.assertEqual(hashlib.sha256(data).hexdigest(), self.log["sha256"][name], name)

    def test_one_per_formula_and_upload_cap(self):
        self.assertEqual(self.man.material_id.nunique(), len(self.man))
        self.assertEqual(self.man.selection_stratum.nunique(), len(self.man))
        acc = self.att[self.att.decision == "accept"]
        self.assertEqual(set(acc.entry_id), set(self.man.task_id))
        self.assertLessEqual(int(acc.upload_id.value_counts().max()) if len(acc) else 0, 6)

    def test_no_excluded_id_or_formula(self):
        for r in self.man.itertuples():
            self.assertNotIn(r.task_id, self.ex_ids)
            self.assertNotIn(r.material_id, self.ex_ids)
            self.assertNotIn(r.formula, self.ex_f)
            self.assertNotIn(r.selection_stratum.removeprefix("formula:"), self.ex_f)
            self.assertEqual(r.material_id, "nomad-" + r.task_id[:12])

    def test_aeccar_table_matches_manifest(self):
        man = self.man.set_index("task_id")
        for r in self.src.itertuples():
            self.assertIn(r.entry_id, man.index)
            self.assertEqual(r.material_id, man.loc[r.entry_id, "material_id"])
            self.assertEqual(r.aeccar_available, "1")
            self.assertTrue(r.aeccar0_path and r.aeccar2_path)
            self.assertEqual(r.chgcar_ngrid, man.loc[r.entry_id, "ngrid"])
            self.assertEqual(r.aeccar0_ngrid, man.loc[r.entry_id, "ngrid"])
            self.assertEqual(r.aeccar2_ngrid, man.loc[r.entry_id, "ngrid"])
            for k in "02":
                self.assertRegex(getattr(r, f"aeccar{k}_sha256"), r"^[0-9a-f]{64}$")
                self.assertGreater(int(getattr(r, f"aeccar{k}_bytes")), 0)

    def test_input_qc_recorded_for_accepted(self):
        acc = self.att[self.att.decision == "accept"].set_index("entry_id")
        for e, r in acc.iterrows():
            for k in "02":
                self.assertEqual(r[f"aeccar{k}_qc_shape"], self.man.set_index("task_id").loc[e, "ngrid"])
                self.assertEqual(int(float(r[f"aeccar{k}_qc_nonfinite"])), 0)

    def test_adapter_reads_table(self):
        rs = load_adapter()
        tab = rs.read_sources(HERE / "aeccar_sources.csv")
        self.assertEqual(set(tab), set(self.man.task_id))


if __name__ == "__main__":
    unittest.main()
