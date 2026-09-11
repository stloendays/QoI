#!/usr/bin/env python3
"""Cross-check P1-P4 machine outputs against the active submission chain."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
AN = ROOT / "analysis" / "research_upgrade"
VAL = ROOT / "validation" / "qsq_prospective"


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def close(a: float, b: float, tol: float = 5e-12) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tol)


def must(text: str, needle: str, label: str):
    if needle not in text:
        raise RuntimeError(f"missing {label}: {needle!r}")


def must_not(text: str, needle: str, label: str):
    if needle in text:
        raise RuntimeError(f"stale/prohibited {label}: {needle!r}")


def main():
    manuscript = (PAPER / "MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md").read_text(encoding="utf-8")
    si = (PAPER / "SUPPLEMENTARY_INFORMATION_DRAFT_20260911.md").read_text(encoding="utf-8")
    claims = (PAPER / "CLAIM_EVIDENCE_MATRIX.md").read_text(encoding="utf-8")
    status = (AN / "CURRENT_STATUS.md").read_text(encoding="utf-8")
    plan = (PAPER / "RESEARCH_UPGRADE_PLAN.md").read_text(encoding="utf-8")
    fig3 = (ROOT / "figures/R/figure3_certification_landscape.R").read_text(encoding="utf-8")
    fig3_caption = (PAPER / "FIGURE3_CAPTION_FINAL_20260911.md").read_text(encoding="utf-8")

    checks = []
    def ok(name: str, detail: str): checks.append((name, detail))

    # P1 machine evidence.
    p1 = read_csv(AN / "p1_common_tight_summary.csv")
    p1p = [r for r in p1 if close(float(r["tau_e"]), 1e-3)]
    if len(p1p) != 1: raise RuntimeError("P1 primary row missing")
    r = p1p[0]
    if not close(float(r["no_pass_risk_eligible"]), 0.03263403263403263): raise RuntimeError("P1 eligible risk drift")
    if not close(float(r["no_pass_risk_non_evaluable"]), 0.6636636636636637): raise RuntimeError("P1 rejected risk drift")
    if not close(float(r["risk_ratio_non_evaluable_vs_eligible"]), 20.34, 0.01): raise RuntimeError("P1 RR drift")
    must(manuscript, "3.3% for QSQ-eligible versus 66.4% for screen-rejected", "P1 manuscript risks")
    must(fig3, 'rr_lab <- c("7.30×", "20.34×", "∞")', "P1 Figure 3 RR labels")
    ok("P1 equal-search", "3.3% vs 66.4%; RR 20.34x; Figure 3 uses completed common-tight summary")

    # P2 machine evidence.
    p2 = read_csv(AN / "p2_fresh_probe_cohort_summary.csv")
    p2p = [r for r in p2 if close(float(r["tau_e"]), 1e-3)]
    if len(p2p) != 2: raise RuntimeError("P2 primary cohort rows missing")
    by = {r["gate_group"]: r for r in p2p}
    e, q = by["eligible"], by["screen_rejected"]
    if int(e["n_materials"]) != 143 or int(q["n_materials"]) != 111: raise RuntimeError("P2 material counts drift")
    if int(e["valid_trials"]) != 8437 or int(q["valid_trials"]) != 6549: raise RuntimeError("P2 trial counts drift")
    if int(e["exceedance_events"]) != 135 or int(q["exceedance_events"]) != 5326: raise RuntimeError("P2 event counts drift")
    if not close(float(e["valid_trial_exceedance_fraction"]), 0.016000948204338034): raise RuntimeError("P2 eligible risk drift")
    if not close(float(q["valid_trial_exceedance_fraction"]), 0.8132539318979997): raise RuntimeError("P2 rejected risk drift")
    must(manuscript, "14,986/14,986 valid", "P2 manuscript accounting")
    must(manuscript, "50.83-fold", "P2 manuscript RR")
    must(fig3, "14,986/14,986 fresh trials", "P2 Figure 3 accounting")
    must(fig3_caption, "The primary Figure 3 claim is prospective risk stratification after a separate equal-search control.", "Figure 3 caption hierarchy")
    must(fig3_caption, "50.83-fold", "Figure 3 caption prospective RR")
    ok("P2 prospective", "14,986/14,986; 143 vs 111 materials; 1.600% vs 81.325%; RR 50.83x")

    # P3A machine evidence.
    p3 = read_csv(VAL / "p3a_implementation_transfer_resolved" / "p3a_classification_transfer_combined.csv")
    on = [r for r in p3 if r["solver"] == "henkelman_ongrid"]
    if len(on) != 3: raise RuntimeError("P3A on-grid threshold rows missing")
    for r in on:
        if int(r["comparable_materials"]) != 24 or int(r["unresolved_materials"]) != 0 or not close(float(r["agreement_fraction"]), 1.0):
            raise RuntimeError("P3A on-grid transfer drift")
        if not close(float(r["cohen_kappa"]), 1.0): raise RuntimeError("P3A kappa drift")
    ranks = {r["solver"]: r for r in read_csv(VAL / "p3a_implementation_transfer_resolved" / "p3a_floor_rank_transfer_combined.csv")}
    if not close(float(ranks["henkelman_ongrid"]["spearman_rho_vs_frozen_baderkit_floor"]), 0.995, 0.002): raise RuntimeError("P3A rho drift")
    must(manuscript, "24 systems at $10^{-4}$, $10^{-3}$ and $10^{-2}\\,e$ (100% agreement; Cohen's $\\kappa=1.000$ at each threshold)", "P3A manuscript classification")
    must(status, "P3A — independent implementation transfer: COMPLETE", "P3A authoritative status")
    ok("P3A implementation transfer", "24/24 on-grid at all thresholds; kappa 1.000; rho 0.995; near-grid retained as boundary")

    # P3B scope boundary.
    p3b = (VAL / "P3B_SCOPE_DECISION.md").read_text(encoding="utf-8")
    must(p3b, "DEFERRED_NO_NEW_DFT", "P3B scope decision")
    must(status, "P3B — new-DFT grid convergence: DEFERRED_NO_NEW_DFT", "P3B status")
    must(plan, "P3B — Genuine electronic-structure grid convergence", "P3B plan section")
    must(manuscript, "does not establish electronic-structure grid convergence or a unique physical Bader reference", "P3A/P3B manuscript boundary")
    ok("P3B claim boundary", "new DFT deferred; no grid-independent-floor or unique-physical-reference claim")

    # P4 machine evidence and reader-facing wording.
    p4m = json.loads((VAL / "p4_chemical_decisions_resolved" / "execution_manifest.json").read_text(encoding="utf-8"))
    if p4m.get("status") != "COMPLETE_RESOLVED" or p4m.get("final_successful_solver_rows") != 216 or p4m.get("final_failed_solver_rows") != 0:
        raise RuntimeError("P4 resolved accounting drift")
    p4 = read_csv(VAL / "p4_chemical_decisions_resolved" / "p4_trial_decisions.csv")
    if len(p4) != 60 or any(r["direct_adverse"].lower() != "false" for r in p4): raise RuntimeError("P4 sign endpoint drift")
    ps = {(r["scope"], r["policy"]): r for r in read_csv(VAL / "p4_chemical_decisions_resolved" / "p4_policy_summary.csv")}
    if int(ps[("ALL", "no_qualification")]["retained_trials"]) != 60 or int(ps[("ALL", "frozen_qsq")]["retained_trials"]) != 36:
        raise RuntimeError("P4 policy retention drift")
    must(manuscript, "all 60 reconstructed BaderKit decisions preserved the frozen reference sign", "P4 manuscript null result")
    must(manuscript, "QSQ does not improve correctness for this deliberately coarse endpoint", "P4 no-overclaim wording")
    must(si, "all 60 direct qualitative target-atom charge-transfer directions were preserved", "P4 SI null result")
    must(claims, "| 17 | Strict QSQ numerical qualification is not equivalent", "Claim 17")
    abstract = manuscript.split("## Introduction", 1)[0]
    must_not(abstract, "P4", "P4 in Abstract")
    ok("P4 chemistry boundary", "5/5 references; 216/216 solver cells; 60/60 sign decisions; QSQ 36/60; represented as null correctness result")

    # Reader-facing active-state consistency.
    for name, text in (("CURRENT_STATUS", status), ("RESEARCH_UPGRADE_PLAN", plan), ("MANUSCRIPT", manuscript)):
        must_not(text, "P3A = COMPLETE_WITH_RECORDED_FAILURES", f"stale P3A status in {name}")
        must_not(text, "P4 — chemistry decision utility: protocol frozen; outcome not executed", f"stale P4 status in {name}")
    must(claims, "| 15 | The frozen five-seed QSQ screen prospectively stratifies unseen response risk", "Claim 15")
    must(claims, "| 16 | QSQ classification transfers across an independent on-grid Bader implementation", "Claim 16")
    ok("Active-document state", "Claims 15-17 present; no stale P3A/P4 active status phrases")

    lines = [
        "# Submission research-upgrade cross-reference audit",
        "",
        "Status: **PASS**",
        "",
        "Scope: machine-readable P1-P4 results versus the active manuscript, Figure 3 source and caption, Supplementary Information, Claim–Evidence Matrix, authoritative status and research plan. Historical provenance files are intentionally not required to adopt current status wording.",
        "",
        "| Check | Result |",
        "|---|---|",
    ]
    for name, detail in checks:
        lines.append(f"| {name} | PASS — {detail} |")
    lines += [
        "",
        "## Submission interpretation lock",
        "",
        "- Central evidence remains P1 equal-search separation plus P2 prospective fresh-perturbation discrimination.",
        "- P3A supports implementation transfer under matched on-grid semantics and simultaneously demonstrates an analysis-definition boundary through near-grid results.",
        "- P3B new-DFT grid convergence is deferred; no grid-independent material-floor claim is permitted.",
        "- P4 is a prespecified null correctness result for a coarse sign-level chemical endpoint. It is used as contract-boundary evidence, not as a positive screening-performance headline.",
        "- Historical 97.2%/95.5% full-record fractions remain provenance/sensitivity results rather than the central design-independent claim.",
    ]
    out = PAPER / "SUBMISSION_UPGRADE_CROSS_REFERENCE_AUDIT_20260911.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Submission upgrade consistency audit: PASS")


if __name__ == "__main__":
    main()
