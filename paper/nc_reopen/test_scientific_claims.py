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
        self.assertIn("<sup>38</sup>", MAIN)  # Wilks
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

    def test_self_contained_storage(self) -> None:
        # Recompute the self-contained numbers from the HB v2 stream sizes and the measured label maps.
        import csv
        from statistics import median
        hb = ROOT / "analysis/qoac_hb_v2/results/P2_CONFIRMATORY_MANIFEST"
        sc = ROOT / "analysis/hb_selfcontained_bytes_20261012/results"
        with open(hb / "materials.csv", encoding="utf-8") as fh:
            raw = {r["material_id"]: float(r["raw_bytes"]) for r in csv.DictReader(fh)}
        with open(sc / "materials.csv", encoding="utf-8") as fh:
            lab = list(csv.DictReader(fh))
        self.assertEqual(len(lab), 48)
        self.assertTrue(all(r["roundtrip_ok"] == "True" and r["charge_check_ok"] == "True" for r in lab))
        L = {r["material_id"]: float(r["label_bytes_primary"]) for r in lab}
        cr = {}
        with open(hb / "joint_v2_best_post.csv", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if float(r["tau_bader"]) == 1e-4 and r["best_joint_cr"]:
                    m = r["material_id"]
                    s = round(raw[m] / float(r["best_joint_cr"]))
                    cr.setdefault(m, {})[r["base"]] = raw[m] / (s + L[m])
        r3 = [cr[m]["R3"] for m in cr]
        util = [cr[m]["R3"] / max(v for b, v in cr[m].items() if b != "R3") for m in cr]
        vs_gf = [cr[m]["R3"] / cr[m]["GF"] for m in cr]
        self.assertEqual(f"{median(L.values()) / 1000:.1f}", "11.8")
        self.assertEqual(f"{median(r3):.0f}", "188")
        self.assertEqual(f"{median(vs_gf):.1f}", "10.2")
        self.assertEqual(sum(u > 1 for u in util), 48)
        self.assertEqual(f"{median(util):.2f}", "1.17")
        self.assertIn("median compression ratio of 188 (95% CI 172–200), 10.2-fold", MAIN)
        self.assertIn("10.2-fold smaller than the pointwise alternative", MAIN)

    def test_whole_object_hartree_archive(self) -> None:
        """Check the whole-object and decoded-moment result against the committed run."""
        import json
        from pathlib import Path
        base = ROOT / "analysis/scope_expansion_20261022/results"
        with open(base / "s2b_archive_hartree_decframe/SUMMARY.json", encoding="utf-8") as fh:
            law = json.load(fh)["estimates"][0]
        self.assertEqual(law["m_certified_objects"], 300)
        self.assertAlmostEqual(law["R_whole_decframe"], 316.407836194927)
        self.assertIn("316-fold", MAIN)
        self.assertIn("34.6-fold", MAIN)
        self.assertIn("9.15-fold", SI)                 # law/pointwise ratio, now stated in Supplementary Note 3.4
        self.assertIn("20.3-fold", MAIN)
        self.assertIn("22.7-fold", MAIN)
        self.assertIn("Supplementary Note 5", MAIN)  # whole-object note, renumbered after Note 3
        self.assertNotIn("356-fold", MAIN)

    def test_operational_archive(self) -> None:
        """Truncation and operational allocation in the archive, with every decoded partition rebuilt (study 5)."""
        import json
        s = json.loads((ROOT / "analysis/archive_w2_20261025/results/SUMMARY.json").read_text(encoding="utf-8"))
        e, pr = s["estimates"], s["paired"]
        self.assertEqual(s["objects_success"]["T"], 300)
        self.assertEqual(round(e["O_1e-06"]["R"]), 347)
        self.assertEqual([round(v) for v in e["O_1e-06"]["ci95"]], [317, 387])
        self.assertEqual(round(e["T_1e-06"]["R"]), 232)
        self.assertEqual(round(e["O_0.0001"]["R"]), 1325)
        self.assertEqual([round(v) for v in e["O_0.0001"]["ci95"]], [1158, 1511])
        self.assertEqual(round(e["T_0.0001"]["R"]), 1115)
        self.assertEqual(round(pr["L/T_0.0001"]["ratio"], 2), 0.93)
        self.assertEqual(round(pr["O/T_0.0001"]["ratio"], 2), 1.19)
        self.assertEqual(round(pr["O/L_0.0001"]["ratio"], 2), 1.28)
        for t in ("347-fold for operational allocation in the zlib container", "232-fold for truncation",
                  "1,325-fold for operational allocation"):
            self.assertIn(t, MAIN)
        for t in ("1,115 (992–1,255)", "**1,325 (1,158–1,511)**", "(law/truncation 0.93, 0.89–0.96)",
                  "| 1.19 (1.15–1.23) | 1.28 (1.23–1.34) |"):
            self.assertIn(t, SI)
        for old in ("1,371", "1,142", "1,818", "1,813", "558.4"):
            self.assertNotIn(old, MAIN + SI)

    def test_writer_archive(self) -> None:
        """The water-filling writer W and its operational variant Q in the archive, partitions rebuilt (study 5)."""
        import json
        s = json.loads((ROOT / "analysis/archive_w2_20261025/results/SUMMARY.json").read_text(encoding="utf-8"))
        e, pr = s["estimates"], s["paired"]
        self.assertEqual(s["objects_success"]["W"], 300)
        self.assertEqual(round(e["W_1e-06"]["R"]), 555)
        self.assertEqual([round(v) for v in e["W_1e-06"]["ci95"]], [492, 635])
        self.assertEqual(round(e["W_0.0001"]["R"]), 1735)
        self.assertEqual([round(v) for v in e["W_0.0001"]["ci95"]], [1470, 2048])
        self.assertEqual(round(e["Q_0.0001"]["R"]), 1726)
        self.assertEqual(round(pr["W/O_1e-06"]["ratio"], 2), 1.60)
        self.assertEqual(round(pr["W/O_0.0001"]["ratio"], 2), 1.31)
        self.assertEqual(round(100 * s["m_share"]["W_0.0001"]), 65)
        self.assertEqual(round(8.4976e12 / e["W_1e-06"]["R"] / 1e9, 1), 15.3)
        self.assertIn("the water-filling writer's 555-fold", MAIN)
        self.assertIn("against 1,735-fold for the water-filling writer", MAIN)
        self.assertIn("**1,735 (1,470–2,048)** | 1,726 (1,457–2,041) | 1.31 (1.26–1.37)", SI)
        self.assertIn("65.2% at $10^{-4}$", SI)
        # the committed revision-10/11 records stay unchanged; the corrected values come from the rebuilt partitions
        c = s["committed"]
        self.assertEqual(round(c["W_0.0001"]["committed_R"]), 1818)
        self.assertAlmostEqual(c["W_1e-06"]["change"], 0.0, places=9)

    def test_predictive_archive(self) -> None:
        """The archive under the predictive and magnetization writers (V) and its attribution (study 4)."""
        import json
        s = json.loads((ROOT / "analysis/archive_w2_20261025/results/SUMMARY.json").read_text(encoding="utf-8"))
        e, pr, ms = s["estimates"], s["paired"], s["moment_stream"]
        self.assertEqual(s["objects_success"]["V"], 300)
        self.assertEqual(round(e["V_1e-06"]["R"]), 1401)
        self.assertEqual([round(v) for v in e["V_1e-06"]["ci95"]], [1245, 1594])
        self.assertEqual(round(e["V_0.0001"]["R"]), 4719)
        self.assertEqual([round(v) for v in e["V_0.0001"]["ci95"]], [3585, 6052])
        self.assertEqual(round(8.4976e12 / e["V_1e-06"]["R"] / 1e9, 1), 6.1)
        self.assertEqual(round(pr["V/W_1e-06"]["ratio"], 2), 2.52)
        self.assertEqual([round(v, 2) for v in pr["V/W_1e-06"]["ci95"]], [2.38, 2.68])
        self.assertGreaterEqual(pr["V/W_1e-06"]["ci95"][0], 1.10)                 # criterion A1
        self.assertGreaterEqual(pr["V/W_0.0001"]["ci95"][0], 1.3)
        self.assertEqual(round(pr["VP/W_1e-06"]["ratio"], 2), 1.74)
        self.assertEqual(round(pr["V/VP_1e-06"]["ratio"], 2), 1.45)
        self.assertEqual(round(pr["V/VP_0.0001"]["ratio"], 2), 2.40)
        self.assertAlmostEqual(pr["VP/W_1e-06"]["ratio"] * pr["V/VP_1e-06"]["ratio"], pr["V/W_1e-06"]["ratio"])
        for k in ("1e-06", "0.0001"):                                              # criterion M1
            x = ms[k]["pw_over_w2m"]
            self.assertGreaterEqual(x["median"], 2)
            self.assertGreaterEqual(x["wins"], 0.7 * x["n"])
        self.assertEqual((ms["0.0001"]["pw_over_w2m"]["wins"], ms["0.0001"]["pw_over_w2m"]["n"]), (291, 293))
        self.assertEqual((ms["0.0001"]["w2m_bytes_median"], ms["0.0001"]["pw_bytes_median"]), (63.0, 3174.0))
        self.assertEqual(round(100 * s["m_share"]["W_0.0001"]), 65)
        self.assertEqual(round(100 * s["m_share"]["V_0.0001"]), 34)
        self.assertEqual(round(s["porod_exponent"]["median"], 2), -2.96)
        self.assertEqual(s["porod_exponent"]["n"], 299)
        for t in ("6.1 GB, 1,401-fold (95% CI 1,245–1,594) and 2.52-fold (2.38–2.68)",
                  "Density prediction contributed 1.74-fold and the magnetization writer 1.45-fold",
                  "4,719-fold (3,585–6,052)", "carries the gain (2.40-fold)", "median 63 bytes per object against 3,174",
                  "(smaller in 291/293)", "fell from 65% to 34%", "$q^{-2.96}$ (median over 299 objects"):
            self.assertIn(t, MAIN)
        self.assertIn("1,401-fold", MAIN.split("## Introduction")[0])                # abstract
        self.assertIn("1,401-fold smaller than the public one", MAIN)               # Discussion
        self.assertIn("a median 30-fold smaller than pointwise codecs", MAIN)
        self.assertEqual(round(ms["1e-06"]["pw_over_w2m"]["median"]), 30)
        for old in ("555-fold (95% CI 492–635)", "15.3 GB"):
            self.assertNotIn(old, MAIN)

    def test_predictive_writer(self) -> None:
        """Structure-factor prediction on the 92 law-protocol materials (study 3)."""
        import json
        s = json.loads((ROOT / "analysis/sfp_spin_writer_20261025/results/SUMMARY.json").read_text(encoding="utf-8"))
        R = s["ratios"]
        self.assertEqual(s["materials_success"], 92)
        self.assertTrue(all(v["met"] for v in s["criteria"].values()))
        self.assertEqual(s["reproduction"]["W1S_equals_rev11_1e-06"]["equal"], 92)
        self.assertEqual(s["reproduction"]["W1S_equals_rev11_0.0001"]["equal"], 92)
        g = lambda k, d=2: round(R[k]["median"], d)  # noqa: E731
        self.assertEqual(g("W2S/W1S_1e-06_all"), 1.95)
        self.assertEqual([round(v, 2) for v in R["W2S/W1S_1e-06_all"]["ci95"]], [1.79, 2.07])
        self.assertEqual(R["W2S/W1S_1e-06_all"]["wins"], 89)
        self.assertEqual(g("W2S/W1S_0.0001_all"), 1.28)
        self.assertEqual(g("W2S/W1S_1e-06_ops1"), 2.40)
        self.assertEqual(R["W2S/W1S_1e-06_ops1"]["n"], 18)
        self.assertEqual(g("W2S/W1S_1e-06_ops>24"), 1.06)
        self.assertEqual(g("O2S/W2S_1e-06_all", 3), 0.995)
        self.assertEqual(g("O2S/W2S_0.0001_all", 3), 0.947)
        self.assertEqual(g("W2S/A3_1e-06_all"), 4.47)
        for t in ("1.95-fold more than the water-filling writer at $10^{-6}$ (95% CI 1.79–2.07; 89/92) and 1.28-fold",
                  "2.40-fold on the 18 cells with one symmetry operation, 1.06-fold above 24 operations",
                  "(median ratio 0.995 at $10^{-6}$, 0.947 at $10^{-4}$)", "4.47-fold more than operational allocation"):
            self.assertIn(t, MAIN)
        self.assertIn("## Supplementary Note 4 — Structure-factor prediction and the magnetization writer", SI)

    def test_water_filling_writer(self) -> None:
        """The water-filling writer on the 92 law-protocol materials (revision 11) against the committed run."""
        import json
        s = json.loads((ROOT / "analysis/waterfill_writer_20261025/results/SUMMARY.json").read_text(encoding="utf-8"))
        R = s["ratios"]
        self.assertEqual(s["materials_success"], 92)
        self.assertTrue(all(v["met"] for v in s["criteria"].values()))
        g = lambda k, d=2: round(R[k]["median"], d)  # noqa: E731
        self.assertEqual(g("O1S/W1S_1e-06_all", 3), 0.999)
        self.assertEqual([round(v, 3) for v in R["O1S/W1S_1e-06_all"]["ci95"]], [0.997, 1.001])
        self.assertEqual(g("O1S/W1S_1e-06_P1", 3), 0.998)
        self.assertEqual(g("O1S/W1S_1e-06_P3B", 3), 1.001)
        self.assertEqual(g("O1S/W1S_0.0001_all", 3), 0.979)
        for t, v in (("0.0001", 1.34), ("1e-06", 1.45)):
            self.assertEqual(g(f"W1S/T1S_{t}_all"), v)
            self.assertEqual(R[f"W1S/T1S_{t}_all"]["wins"], 92)
        self.assertEqual(g("W1S/A3_1e-06_all"), 2.34)
        self.assertEqual([round(v, 2) for v in R["W1S/A3_1e-06_all"]["ci95"]], [2.14, 2.69])
        self.assertEqual(R["W1S/A3_1e-06_all"]["wins"], 92)
        self.assertEqual(g("L1/A1_1e-06_all"), 1.34)
        self.assertEqual(g("L1/A1_0.0001_all"), 2.51)
        self.assertEqual(g("W1S/W1_1e-06_all"), 1.91)
        self.assertEqual(round(R["W1S/A6_1e-06_all"]["median"], 1), 35.7)
        self.assertEqual(s["symmetry"]["with_symmetry"], 74)
        for t in ("92/92 materials at $10^{-4}$ (median 1.34-fold) and $10^{-6}$ (1.45-fold)",
                  "median ratio 0.999 (95% CI 0.997–1.001)", "(bulk 0.998, slabs 1.001) and 0.979",
                  "added 1.34-fold at $10^{-6}$ (2.51-fold at $10^{-4}$)",
                  "a further median 1.91-fold", "2.34-fold more than operational allocation in the zlib "
                  "container (95% CI 2.14–2.69; 92/92) and 35.7-fold"):
            self.assertIn(t, MAIN)

    def test_exchange_correlation_contract(self) -> None:
        """L/P under the XC contract and the Hartree certificate's XC error on slabs (revision 10)."""
        import json
        s = json.loads((ROOT / "analysis/nonlinear_xc_20261024/results/SUMMARY.json").read_text(encoding="utf-8"))
        pr = {(r["cohort"], r["tau_x_meV_per_atom"], r["ratio"]): r for r in s["paired"]}
        self.assertEqual(s["success"], 92)
        self.assertEqual(round(pr[("P1", 1.0, "L/P")]["median"], 1), 5.4)
        self.assertEqual(round(pr[("P1", 0.1, "L/P")]["median"], 1), 6.9)
        self.assertEqual(round(pr[("P3B", 1.0, "L/P")]["median"], 1), 2.9)
        self.assertEqual(round(pr[("P3B", 0.1, "L/P")]["median"], 1), 1.9)
        a1 = [r for r in s["transfer"] if r["cohort"] == "P3B" and r["arm"] == "A1" and r["tau_H"] == 1e-6][0]
        self.assertEqual(round(a1["median_dE_pbe_meV_per_atom"], 1), 3.9)
        self.assertIn("5.4- and 6.9-fold more than the best pointwise codec on bulk crystals and 2.9- and 1.9-fold more on slabs", MAIN)
        self.assertIn("median error 3.9 meV per atom", MAIN)

    def test_linearized_exchange_correlation_allocation(self) -> None:
        """X/L medians quoted in Results and Supplementary Note 8 (revision 10)."""
        import json
        s = json.loads((ROOT / "analysis/xc_linearized_law_20261025/results/SUMMARY.json").read_text(encoding="utf-8"))
        pr = {(r["cohort"], r["tau_x_meV_per_atom"], r["ratio"]): r["median"] for r in s["paired"]}
        self.assertEqual(s["success"], 92)
        bulk = sorted(round(pr[("P1", t, "X/L")], 2) for t in (1.0, 0.1))
        slab = sorted(round(pr[("P3B", t, "X/L")], 2) for t in (1.0, 0.1))
        self.assertEqual(bulk, [0.99, 1.0])
        self.assertEqual(slab, [0.93, 0.96])
        self.assertIn("(median ratios 0.99–1.00; 0.93–0.96 on slabs)", MAIN)
        self.assertEqual(round(pr[("P1", 0.1, "X/F")], 2), 1.16)
        self.assertIn("1.16 (1.06–1.22; 41/60)", SI)

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
        self.assertIn("at most 0.45 meV (pointwise: up to 2.8 meV)", SI)
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
        self.assertIn("60/60 bulk crystals and 26/32 slabs", SI)
        self.assertIn(r"the best of $s\in\{\infty,0,-1,-2\}$", SI)

    def test_archive_attribution(self) -> None:
        self.assertIn("Lossless binary storage alone gives 0.99-fold", MAIN)
        self.assertIn("5.35-fold", MAIN)

    def test_codec_order_at_matched_distortion(self) -> None:
        """Recompute the codec-order counts from the committed matched pairs."""
        import csv
        with open(ROOT / "analysis/contract_codec_order_20261023/inputs/matched_real_material_pairs.csv",
                  encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(len({r["material_id"] for r in rows}), 185)
        fixed = [float(r["Bader_fixed_error_SZ3_e"]) / float(r["Bader_fixed_error_SPERR_e"]) for r in rows]
        rederived = [float(r["Bader_resolved_error_SZ3_e"]) / float(r["Bader_resolved_error_SPERR_e"]) for r in rows]
        self.assertTrue(all(abs(float(r["log10_Linf_mismatch_abs"])) <= 0.10 and
                            abs(float(r["log10_RMSE_mismatch_abs"])) <= 0.10 for r in rows))
        self.assertEqual(sum(f > 1 for f in fixed), 185)
        self.assertEqual(sum(f > 1 and g < 1 for f, g in zip(fixed, rederived)), 109)
        self.assertIn("185/185 materials", MAIN)
        self.assertIn("SZ3 did in 109/185", MAIN)
        self.assertIn("(Spearman 0.607)", MAIN)
        self.assertIn("109/185 (58.9%", SI)

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
