"""Consistency of the frozen wide-cohort tables with PROTOCOL.md section 2 (unittest + pandas; no network, no baderkit).

Checks manifest.csv, aeccar_sources.csv and selection/: N = min(32, qualified) with one entry per reduced formula and at
most six per upload; no excluded NOMAD id (exact or `nomad-` prefix) or slab formula; every entry inside the npoints
window, with AECCAR0 + AECCAR2 on the CHGCAR grid that passed the input QC; and the slab adapter reads the table.
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
NPOINTS_MIN, NPOINTS_MAX = 150_000, 3_870_720


def load_adapter():
    if "run_joint_slab" in sys.modules:
        return sys.modules["run_joint_slab"]
    spec = importlib.util.spec_from_file_location("run_joint_slab", ADAPTER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["run_joint_slab"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestWideCohortTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.man = pd.read_csv(HERE / "manifest.csv", dtype=str)
        cls.src = pd.read_csv(HERE / "aeccar_sources.csv", dtype=str)
        cls.draw = pd.read_csv(SEL / "draw.csv", dtype=str)
        cls.qc = pd.read_csv(SEL / "qc.csv", dtype=str)
        cls.cand = pd.read_csv(SEL / "candidates.csv", dtype=str)
        cls.log = json.loads((SEL / "selection_log.json").read_text(encoding="utf-8"))
        ids = set(pd.read_csv(SEL / "exclusion_nomad_ids.csv", dtype=str).id)
        cls.ids = ids
        cls.prefixes = [i[len("nomad-"):] for i in ids if i.startswith("nomad-")]
        cls.forms = set(pd.read_csv(SEL / "exclusion_slab_formulas.csv", dtype=str).reduced_formula)

    def test_sizes(self):
        n = len(self.man)
        qual = self.qc[self.qc.qc_pass == "1"]
        self.assertEqual(n, self.log["N"])
        self.assertLessEqual(n, 32)
        self.assertEqual(len(self.src), n)
        self.assertEqual(n, int((self.draw.decision == "accept").sum()))
        self.assertEqual(int(len(qual)), self.log["qc_passed"])
        if n < 32:   # every qualified formula was visited
            self.assertEqual(self.log["draw_formulas_visited"], self.log["qc_passed_formulas"])

    def test_hashes_match_log(self):
        for name, path in (("manifest.csv", HERE / "manifest.csv"), ("aeccar_sources.csv", HERE / "aeccar_sources.csv"),
                           ("draw.csv", SEL / "draw.csv"), ("qc.csv", SEL / "qc.csv"),
                           ("candidates.csv", SEL / "candidates.csv"),
                           ("exclusion_nomad_ids.csv", SEL / "exclusion_nomad_ids.csv"),
                           ("exclusion_slab_formulas.csv", SEL / "exclusion_slab_formulas.csv"),
                           ("relisted_entries.csv", SEL / "relisted_entries.csv")):
            data = path.read_bytes().replace(b"\r\n", b"\n")
            self.assertEqual(hashlib.sha256(data).hexdigest(), self.log["sha256"][name], name)

    def test_one_per_formula_and_upload_cap(self):
        self.assertTrue(self.man.material_id.is_unique)
        self.assertTrue(self.man.selection_stratum.is_unique)
        acc = self.draw[self.draw.decision == "accept"]
        self.assertEqual(set(acc.entry_id), set(self.man.task_id))
        if len(acc):
            self.assertLessEqual(int(acc.upload_id.value_counts().max()), 6)

    def test_no_excluded_id_or_formula(self):
        for r in self.man.itertuples():
            self.assertNotIn(r.task_id, self.ids)
            self.assertFalse(any(r.task_id.startswith(p) for p in self.prefixes), r.task_id)
            self.assertNotIn(r.formula, self.forms)
            self.assertNotIn(r.selection_stratum.removeprefix("formula:"), self.forms)
            self.assertEqual(r.material_id, "nomad-" + r.task_id[:12])

    def test_window_and_qc(self):
        q = self.qc.set_index("entry_id")
        for r in self.man.itertuples():
            self.assertTrue(NPOINTS_MIN <= int(r.npoints) <= NPOINTS_MAX)
            x = q.loc[r.task_id]
            self.assertEqual(x.qc_pass, "1")
            for k in "02":
                self.assertEqual(x[f"aeccar{k}_ngrid"], r.ngrid)
                self.assertEqual(x[f"aeccar{k}_parsed_shape"], r.ngrid)
                self.assertEqual(int(float(x[f"aeccar{k}_nonfinite"])), 0)
                self.assertEqual(int(float(x[f"aeccar{k}_no_E_tokens"])), 0)

    def test_aeccar_table_matches_manifest(self):
        man = self.man.set_index("task_id")
        for r in self.src.itertuples():
            self.assertEqual(r.material_id, man.loc[r.entry_id, "material_id"])
            self.assertEqual(r.aeccar_available, "1")
            for k in "02":
                self.assertEqual(getattr(r, f"aeccar{k}_ngrid"), man.loc[r.entry_id, "ngrid"])
                self.assertRegex(getattr(r, f"aeccar{k}_sha256"), r"^[0-9a-f]{64}$")
                self.assertGreater(int(getattr(r, f"aeccar{k}_bytes")), 0)

    def test_adapter_reads_table(self):
        tab = load_adapter().read_sources(HERE / "aeccar_sources.csv")
        self.assertEqual(set(tab), set(self.man.task_id))


if __name__ == "__main__":
    unittest.main()
