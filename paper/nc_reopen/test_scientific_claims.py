"""Regression tests for claim boundaries in the NC QoI manuscript.

This is a manuscript QA test, not a replacement for the numerical experiment
register. It checks a proof under the stated probability assumptions and
prevents unsupported extensions of the archived experiment claims.
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
        self.assertIn("conditionally independent and identically distributed", MAIN)
        self.assertIn("Exchangeability without conditional independence", MAIN)
        self.assertIn("16.7%", MAIN)
        self.assertIn("<sup>37</sup>", MAIN)
        self.assertNotIn("A finite panel carries a distribution-free guarantee: for exchangeable", MAIN)

    def test_si_theorem_and_limitations(self) -> None:
        self.assertIn("finite-exchangeability upper bound | 16.67%", SI)
        self.assertIn("exactly one exceedance uniformly positioned", SI)
        self.assertIn("conditional independence holds within each pair", SI)
        self.assertIn("not sampled by the same perturbation mechanism", SI)

    def test_population_rates(self) -> None:
        self.assertAlmostEqual(100 * (135 / 8437), 1.600, delta=0.001)
        self.assertAlmostEqual(100 * (5326 / 6549), 81.325, delta=0.001)
        self.assertAlmostEqual(100 * (135 / 14986), 0.901, delta=0.001)
        self.assertIn("135/8,437", MAIN)
        self.assertIn("5,326/6,549", MAIN)

    def test_bader_partition_storage_scope(self) -> None:
        self.assertIn("exact partition reference excluded from both sizes", MAIN)
        self.assertIn("did not measure these combined self-contained bytes", SI)
        self.assertIn("reused for reference and decoded Bader solves", SI)
        self.assertIn("not for slabs", MAIN)

    def test_vacuum_work_function_scope(self) -> None:
        self.assertIn("not a self-consistently recalculated work function", MAIN)
        self.assertIn("Fermi energy, ionic and exchange-correlation terms are fixed", SI)
        self.assertIn("not a direct flat-potential-plateau criterion", SI)
        self.assertIn("27/27", MAIN)

    def test_qpet_and_archive_comparison_scope(self) -> None:
        self.assertIn("not a Hartree-specific QPET encoder", MAIN)
        self.assertIn("required float32 input", SI)
        self.assertIn("the best of $s\\in\\{\\infty,0,-1,-2\\}$", MAIN)
        self.assertIn("not the operator-aware Fourier codec", MAIN)
        self.assertIn("No operator-aware Fourier codec was run", SI)

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
