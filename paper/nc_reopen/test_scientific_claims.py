"""Regression tests for claim boundaries in the NC QoI manuscript.

This is a manuscript QA test, not a replacement for the numerical experiment
register. It checks a proof under the stated probability assumptions and
checks that each definition and number in the text matches the committed results.
Run: python paper/nc_reopen/test_scientific_claims.py
"""
from __future__ import annotations

import math
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAIN = (ROOT / "paper/MANUSCRIPT.md").read_text(encoding="utf-8")
SI = (ROOT / "paper/SUPPLEMENTARY_INFORMATION.md").read_text(encoding="utf-8")


def iid_joint_max(n: int) -> float:
    """Sharp P(n qualification passes followed by one failure), conditionally i.i.d."""
    return n**n / (n + 1) ** (n + 1)


def finite_exchangeable_joint_max(n: int) -> float:
    """Sharp bound without conditional independence."""
    return 1 / (n + 1)


class ScientificClaimTests(unittest.TestCase):
    def test_iid_joint_bound(self) -> None:
        for n, pct in ((5, 6.70), (10, 3.50), (19, 1.89), (37, 0.98)):
            with self.subTest(panel_size=n):
                self.assertAlmostEqual(100 * iid_joint_max(n), pct, delta=0.015)
                p_star = 1 / (n + 1)
                self.assertAlmostEqual(p_star * (1 - p_star) ** n, iid_joint_max(n))

    def test_exchangeability_counterexample(self) -> None:
        # Uniformly choose the unique exceedance position among n+1 draws.
        # This is a finite exchangeable sequence, not i.i.d.
        n = 5
        event_outcomes = [int(k == n) for k in range(n + 1)]
        joint_probability = sum(event_outcomes) / (n + 1)
        self.assertAlmostEqual(joint_probability, finite_exchangeable_joint_max(n))
        self.assertGreater(joint_probability, iid_joint_max(n))
        self.assertAlmostEqual(joint_probability, 1 / 6)

    def test_iid_joint_is_not_conditional_risk(self) -> None:
        n, p = 5, 0.5
        admission_prob = (1 - p) ** n
        joint_prob = admission_prob * p
        self.assertAlmostEqual(joint_prob / admission_prob, 0.5)
        self.assertLess(joint_prob, iid_joint_max(n))
        self.assertGreater(p, iid_joint_max(n))

    def test_main_theorem_assumptions(self) -> None:
        # The bound needs independent draws; QSQ probes and fresh perturbations are independent by construction.
        self.assertIn("independent draws from one perturbation law", MAIN)
        self.assertIn("independent draws of the same uniform perturbation", MAIN)
        self.assertIn("6.70%", MAIN)
        self.assertIn("<sup>37</sup>", MAIN)
        self.assertNotIn("A finite panel carries a distribution-free guarantee: for exchangeable", MAIN)
        self.assertNotIn("If the $n$ qualification responses and a later response are exchangeable", MAIN)

    def test_si_theorem(self) -> None:
        self.assertIn("by construction", SI)
        self.assertIn("`iid_uniform`", SI)
        self.assertIn("Independence is what the bound uses", SI)
        self.assertIn("conditional risk among admitted materials is reported separately", SI)

    def test_population_rates(self) -> None:
        self.assertAlmostEqual(100 * (135 / 8437), 1.600, delta=0.001)
        self.assertAlmostEqual(100 * (5326 / 6549), 81.325, delta=0.001)
        self.assertAlmostEqual(100 * (135 / 14986), 0.901, delta=0.001)
        self.assertIn("135/8,437", MAIN)
        self.assertIn("5,326/6,549", MAIN)

    def test_joint_contract_definition(self) -> None:
        self.assertIn("exact all-electron partition reference", MAIN)
        self.assertIn("exact-partition Bader contract", MAIN)
        self.assertIn("label map", SI)

    def test_work_function_definition_and_window(self) -> None:
        # Definition: electrostatic vacuum level minus the stored Fermi energy, ionic potential exact.
        self.assertIn("electrostatic vacuum level minus the stored Fermi energy", MAIN)
        self.assertIn("with the stored Fermi energy and the exact ionic potential", MAIN)
        self.assertIn("`LVHAR`", SI)
        # Window maxima quoted in the text equal the committed run summary.
        import csv
        with open(ROOT / "analysis/p3b_vacuum_level_20261007/results/summary.csv", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        wmax = {(r["arm"], float(r["tau"])): float(r["max_max_abs_dV_window_meV"]) for r in rows}
        self.assertEqual(f"{wmax[('A1', 1e-6)]:.2f}", "0.45")
        self.assertEqual(f"{wmax[('A6', 1e-6)]:.1f}", "2.8")
        self.assertIn("at most 0.45 meV (pointwise: up to 2.8 meV)", MAIN)
        self.assertIn("| A1 law | 15.3 / 59.0 | 0.090 / 0.45 |", SI)
        self.assertIn("27/27", MAIN)

    def test_qpet_host_precision(self) -> None:
        import csv
        from statistics import median
        with open(ROOT / "paper/nc_reopen/derived/qpet_best_host.csv", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        for cohort, n_float64, ratio in (("P1", 60, "6.31"), ("P3B", 26, "9.47")):
            with self.subTest(cohort=cohort):
                sel = [r for r in rows if r["cohort"] == cohort and float(r["tau"]) == 1e-6]
                self.assertEqual(sum(r["best_host_float64"] == "True" for r in sel), n_float64)
                self.assertFalse(any(r["best_host"] == "hpez" for r in sel))
                self.assertEqual(f"{median(float(r['A1_over_Q_sperr']) for r in sel):.2f}", ratio)
                self.assertEqual(f"{median(float(r['A1_over_Q']) for r in sel):.2f}", ratio)
        self.assertIn("60/60 bulk crystals and 26/32 slabs", MAIN)
        self.assertIn("60/60 bulk crystals and 26/32 slabs", SI)
        self.assertIn(r"the best of $s\in\{\infty,0,-1,-2\}$", MAIN)

    def test_archive_attribution(self) -> None:
        self.assertIn("lossless binary storage accounts for 2.00-fold", MAIN)
        self.assertIn("certified compression adds 2.66-fold", MAIN)

    def test_manuscript_word_limits(self) -> None:
        out = subprocess.check_output(
            [sys.executable, str(ROOT / "paper/nc_reopen/word_count.py")],
            text=True, cwd=ROOT,
        )
        abstract = re.search(r"(?m)^Abstract\s+(\d+)\s*$", out)
        total = re.search(r"\| total\s+(\d+)", out)
        self.assertIsNotNone(abstract, out)
        self.assertIsNotNone(total, out)
        self.assertLessEqual(int(abstract.group(1)), 150)
        self.assertLessEqual(int(total.group(1)), 5000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
