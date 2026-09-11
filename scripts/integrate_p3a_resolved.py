#!/usr/bin/env python3
"""Guarded integration of resolved P3A evidence into active paper-facing records.

This script is intentionally narrow: it verifies the machine-readable resolved
P3A outputs first, then performs exact-anchor edits. It does not alter any
benchmark, QSQ, P1/P2, P3A measurement, panel, seed, solver or threshold data.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "validation/qsq_prospective/p3a_implementation_transfer_resolved"


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"{label}: expected exactly one anchor, found {n}")
    return text.replace(old, new, 1)


def verify_results() -> dict:
    manifest = json.loads((RES / "execution_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("status") != "COMPLETE":
        raise RuntimeError("resolved P3A manifest is not COMPLETE")
    expected = {
        "retry_planned_solver_evaluations": 360,
        "retry_success_rows": 360,
        "retry_failed_rows": 0,
        "panel_materials": 24,
        "retry_materials": 20,
        "scientific_definition_changed_for_retry": False,
    }
    for k, v in expected.items():
        if manifest.get(k) != v:
            raise RuntimeError(f"manifest drift: {k}={manifest.get(k)!r}, expected {v!r}")

    cls = read_csv(RES / "p3a_classification_transfer_combined.csv")
    ranks = read_csv(RES / "p3a_floor_rank_transfer_combined.csv")
    if len(cls) != 6:
        raise RuntimeError("classification table must contain 6 solver-threshold rows")

    on = sorted((r for r in cls if r["solver"] == "henkelman_ongrid"), key=lambda r: float(r["tau_e"]))
    near = sorted((r for r in cls if r["solver"] == "henkelman_neargrid"), key=lambda r: float(r["tau_e"]))
    if len(on) != 3 or len(near) != 3:
        raise RuntimeError("missing implementation rows")
    for r in on:
        if int(r["comparable_materials"]) != 24 or int(r["unresolved_materials"]) != 0:
            raise RuntimeError("on-grid full-panel accounting drift")
        if float(r["agreement_fraction"]) != 1.0 or float(r["cohen_kappa"]) != 1.0:
            raise RuntimeError("on-grid classification no longer has exact agreement")
    near_agree = [float(r["agreement_fraction"]) for r in near]
    expected_near = [0.8260869565217391, 0.8333333333333334, 0.9583333333333334]
    if any(abs(a-b) > 1e-12 for a, b in zip(near_agree, expected_near)):
        raise RuntimeError(f"near-grid agreement drift: {near_agree}")

    rank = {r["solver"]: float(r["spearman_rho_vs_frozen_baderkit_floor"]) for r in ranks}
    if abs(rank["henkelman_ongrid"] - 0.995) > 0.001:
        raise RuntimeError(f"unexpected on-grid rank transfer {rank['henkelman_ongrid']}")
    if abs(rank["henkelman_neargrid"] - 0.754) > 0.001:
        raise RuntimeError(f"unexpected near-grid rank transfer {rank['henkelman_neargrid']}")

    material = read_csv(RES / "p3a_material_floors_combined.csv")
    complete = [r for r in material if str(r["complete_five_seed"]).lower() == "true"]
    if len(material) != 72 or len(complete) != 72:
        raise RuntimeError(f"expected 72/72 complete summaries, got {len(complete)}/{len(material)}")
    recre = [float(r["frozen_recreated_abs_delta_e"]) for r in material if r["solver"] == "baderkit_ongrid"]
    max_recreated = max(recre)
    if abs(max_recreated - 8.71338e-11) > 1e-15:
        raise RuntimeError(f"unexpected BaderKit recreation delta {max_recreated}")

    return {"rank": rank, "max_recreated": max_recreated}


def update_manuscript() -> None:
    path = ROOT / "paper/MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md"
    text = path.read_text(encoding="utf-8")
    if "<!-- P3A_RESOLVED_EVIDENCE -->" in text:
        return

    results_anchor = (
        "Holding the reference basin fixed suppresses the latter contribution and changes the downstream operator being evaluated. "
        "We therefore use re-derived basins for scientific certification and retain fixed-basin calculations only as a mechanistic diagnostic. "
        "Representative per-atom decompositions show that domain migration can dominate large Bader deviations at tight perturbations, while full tolerance ladders contain abrupt charge changes despite smoothly varying field distortion. "
        "This mechanism explains why Bader response can be discontinuous even when smoother observables remain well behaved. It is specific to density-dependent partitioning and is not assumed to generalize to arbitrary QoIs."
    )
    results_new = results_anchor + (
        "\n\n<!-- P3A_RESOLVED_EVIDENCE -->\n"
        "We next tested whether the QSQ stability classification was specific to the primary Bader implementation. A deterministically stratified 24-system panel spanning bulk and slab densities and four frozen stability-floor bands was re-evaluated with independent Henkelman on-grid and near-grid implementations using the same five historical perturbation fields. A first execution blocked 20 systems before solver evaluation because a provenance check compared source-rederived amplitudes with decimal-serialized historical values at binary-ULP precision; all 360 blocked cells were classified before an engineering-only retry, and no scientific setting was changed. The retry completed 360/360 cells with zero recorded failures. Across the resolved panel, Henkelman on-grid reproduced the frozen QSQ eligibility classification for all 24 systems at $10^{-4}$, $10^{-3}$ and $10^{-2}\,e$ (100% agreement; Cohen's $\kappa=1.000$ at each threshold) and preserved the stability-floor ordering (Spearman $\rho=0.995$). By contrast, Henkelman near-grid agreement was 82.6%, 83.3% and 95.8% across the same thresholds, with $\rho=0.754$. The QSQ risk stratification is therefore not an artifact of one on-grid implementation on this targeted panel, while the near-grid differences show that the downstream numerical algorithm remains part of the measurement contract. This implementation-transfer test does not establish electronic-structure grid convergence or a unique physical Bader reference (Supplementary Table S11)."
    )
    text = replace_once(text, results_anchor, results_new, "manuscript results P3A insertion")

    discussion_anchor = (
        "Bader charge makes this distinction visible because its numerical sensitivity has a concrete structural origin. The atomic partition is defined by the topology of the density field [17], and practical grid-based implementations necessarily approximate both basin assignment and integration [18–21]. Reconstructing the density can therefore move basin boundaries as well as alter values within the basins. Fixed-domain scoring removes this channel and can underestimate the response obtained by rerunning the actual downstream analysis. The tightest certified reconstructions also approach the independently measured Bader stability floor, consistent with a crossover towards an analysis-limited regime. Neither feature should be universalized: a smooth QoI may remain identifiable at much tighter tolerances, and a different topology-sensitive algorithm may require a different qualification probe."
    )
    discussion_new = discussion_anchor + (
        "\n\nThe implementation-transfer experiment sharpens that scope. Exact threshold classifications were retained across the independent Henkelman implementation when the on-grid basin-assignment class was held fixed, whereas the near-grid variant produced threshold switches and weaker floor-rank concordance. Thus, numerical identifiability is neither merely a software-package artifact nor an implementation-free material constant: the downstream algorithm is an explicit component of the scientific measurement contract."
    )
    text = replace_once(text, discussion_anchor, discussion_new, "manuscript discussion P3A insertion")

    methods_anchor = "### QoI Stability Qualification and eligibility\n"
    methods_section = (
        "### Independent implementation-transfer validation\n\n"
        "Implementation dependence was evaluated on a deterministic 24-system panel stratified by system type (bulk or slab) and four frozen QSQ stability-floor bands, with three systems selected per stratum by a fixed hash order. The original five perturbation seeds and archived material-specific amplitudes were reused without retuning. For each system we evaluated the baseline and five perturbed densities with BaderKit on-grid, independent Henkelman on-grid and Henkelman near-grid analyses. Eligibility-transfer statistics were computed at the same $10^{-4}$, $10^{-3}$ and $10^{-2}\,e$ thresholds used elsewhere.\n\n"
        "The first execution and its recorded failures remain archived. Before retry, all 360 failed cells were shown to share a pre-solver provenance-check signature caused by comparing decimal-serialized historical amplitudes at binary-ULP precision. The retry modified only serialization-aware compatibility checking and reliable exit-code capture; the panel, perturbation amplitudes and seeds, density identities, solvers and scientific thresholds were unchanged. The final combined analysis reuses the four complete first-run systems and the 20 predeclared retry systems. This test evaluates transfer across numerical Bader implementations on fixed density grids; it is not an electronic-structure grid-convergence test.\n\n"
        + methods_anchor
    )
    text = replace_once(text, methods_anchor, methods_section, "manuscript methods P3A insertion")
    path.write_text(text, encoding="utf-8")


def update_plan() -> None:
    path = ROOT / "paper/RESEARCH_UPGRADE_PLAN.md"
    text = path.read_text(encoding="utf-8")
    old = """**Status: P3A COMPLETE_WITH_RECORDED_FAILURES; P3B NOT EXECUTED.** P3A run **34605557997** accounted all **432/432** planned solver cells on the frozen 24-system panel, but only **72** rows succeeded and **360** are recorded failed/unresolved. Aggregate results were retained and committed in **99f5adcaf08f7556b5d05fdb16f75b465592f52b**. Only **4/24 materials** currently have complete five-seed implementation-transfer results, so P3A has not passed the full-panel gate.

Among those four complete materials, recreated BaderKit floors match the frozen floors to a maximum absolute difference of **1.54445e-11 e**. Henkelman on-grid classifications agree 100% with frozen BaderKit at `1e-4`, `1e-3` and `1e-2 e` (Cohen kappa 1.0; floor-rank Spearman rho 1.0). Henkelman near-grid is less consistent (agreement 50% / 75% / 75%; floor-rank rho 0.4), which currently defines an implementation-sensitive boundary rather than a universal reference.

One inspected failed shard shows a provenance-gate issue rather than a Bader-solver failure: the source-rederived float32 amplitude and the historical CSV value differ only at serialized decimal precision, while the hard ULP-based equality check was far tighter than the stored text precision. This finding cannot yet be extrapolated to all 360 failures. Every failed row must be classified by stage/signature before deciding which cells are eligible for an engineering-only rerun.

The deterministic 24-system panel remains frozen. Any rerun may repair only infrastructure/provenance validation logic; material selection, perturbation fields, solver definitions and scientific thresholds must not be changed because of observed outcomes. The original failed run remains provenance.

P3B grid convergence requires genuinely recomputed electronic-density grids where convergence is claimed; interpolation of an existing coarse grid is not accepted as a new DFT convergence result.

**Gate:** full-panel implementation-transfer evidence remains open until unresolved P3A rows are correctly classified/recovered. At least one genuine grid-convergence comparison is still required for P3B."""
    new = """**Status: P3A COMPLETE; P3B NOT EXECUTED.** The original P3A run **34605557997** and its 360 recorded failures remain preserved. Before retry, all **360/360** failures were frozen and classified as the same pre-solver archived-amplitude serialization/provenance-gate signature; no recorded Bader-solver, atom-mapping, vacuum, grid-shape or source-download failure was present. A predeclared engineering-only retry, run **34608648393**, changed only serialization-aware amplitude compatibility and shell exit-code capture. It completed **360/360 retry cells successfully with 0 failures**, producing **72/72 complete material–solver five-seed summaries** across the 24-system panel.

Resolved P3A results are strong but deliberately implementation-specific. Recreated BaderKit floors match the frozen values to maximum absolute difference **8.71338e-11 e**. Henkelman on-grid reproduces the frozen QSQ classification for **24/24 materials at all three thresholds** (`1e-4`, `1e-3`, `1e-2 e`; agreement 100%, Cohen kappa 1.000 throughout) and preserves floor ordering with Spearman **rho = 0.995**. Henkelman near-grid is measurably less concordant: **82.6% / 83.3% / 95.8%** agreement and floor-rank **rho = 0.754**.

**Gate outcome for P3A: PASSED for targeted implementation transfer.** The frozen QSQ stratification is not an artifact of the original BaderKit package when the same on-grid assignment class is used, but the near-grid comparison demonstrates that the downstream numerical implementation remains part of the measurement contract. This 24-system hash-stratified panel is a mechanism/robustness panel, not a prevalence sample.

P3B grid convergence remains open and requires genuinely recomputed electronic-density grids where convergence is claimed; interpolation of an existing coarse grid is not accepted as a new DFT convergence result. P3A must not be described as grid convergence or as defining a unique physical Bader reference.

**Gate:** P3A closed; at least one genuine grid-convergence comparison is still required for P3B before the numerical-reference question is considered fully closed."""
    if old not in text and "**Status: P3A COMPLETE; P3B NOT EXECUTED.**" in text:
        return
    text = replace_once(text, old, new, "research plan P3 status")
    path.write_text(text, encoding="utf-8")


def update_s11() -> None:
    path = ROOT / "paper/SUPPLEMENTARY_TABLES_S10_S11_20260911.md"
    text = path.read_text(encoding="utf-8")
    if "### S11f. Resolved 24-system QSQ classification transfer" in text:
        return
    anchor = "**Interpretation boundary.** This deliberately stratified 12-system panel is a mechanism/implementation robustness study, not a prevalence estimate."
    section = """### S11f. Resolved 24-system QSQ classification transfer

This second, deterministic panel is distinct from the 12-system mechanism matrix above. It contains 24 development systems stratified by bulk/slab and four frozen QSQ stability-floor bands. The same five historical perturbation fields were analyzed with independent Bader implementations.

| Bader threshold | Independent solver | Comparable systems | Ambiguous | Agreement with frozen QSQ classification | Cohen kappa | Eligible -> rejected | Rejected -> eligible |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1e-4 e | Henkelman on-grid | 24 | 0 | **100.0%** | **1.000** | 0 | 0 |
| 1e-4 e | Henkelman near-grid | 23 | 1 | 82.6% | 0.593 | 1 | 3 |
| 1e-3 e | Henkelman on-grid | 24 | 0 | **100.0%** | **1.000** | 0 | 0 |
| 1e-3 e | Henkelman near-grid | 24 | 0 | 83.3% | 0.667 | 0 | 4 |
| 1e-2 e | Henkelman on-grid | 24 | 0 | **100.0%** | **1.000** | 0 | 0 |
| 1e-2 e | Henkelman near-grid | 24 | 0 | 95.8% | 0.882 | 0 | 1 |

Floor-rank Spearman correlation with frozen BaderKit is **0.995** for Henkelman on-grid and **0.754** for Henkelman near-grid. Recreated BaderKit floors agree with their frozen values to a maximum absolute difference of **8.71338e-11 e**.

The first execution is retained as provenance. Its 360 recorded failures were all classified before retry as a single pre-solver decimal-serialization compatibility-gate failure family. The predeclared engineering retry completed 360/360 blocked cells with zero failures and changed no scientific panel, perturbation, solver or threshold definition.

**Sources:** `validation/qsq_prospective/p3a_implementation_transfer_resolved/p3a_classification_transfer_combined.csv`; `p3a_floor_rank_transfer_combined.csv`; `P3A_IMPLEMENTATION_TRANSFER_RESOLVED_REPORT.md`; failure provenance in `analysis/research_upgrade/P3A_FAILURE_TAXONOMY.md`.

---

""" + anchor
    text = replace_once(text, anchor, section, "S11f insertion")
    path.write_text(text, encoding="utf-8")


def update_si_index() -> None:
    path = ROOT / "paper/SUPPLEMENTARY_INFORMATION_DRAFT_20260911.md"
    text = path.read_text(encoding="utf-8")
    old = "| **Table S11** | Cross-implementation Bader robustness | `mechanism/independent_bader_20260908/` | **READY, needs compact aggregation** |"
    new = "| **Table S11** | Cross-implementation Bader robustness + resolved 24-system QSQ classification transfer | `mechanism/independent_bader_20260908/`; `validation/qsq_prospective/p3a_implementation_transfer_resolved/` | **BUILT** — `paper/SUPPLEMENTARY_TABLES_S10_S11_20260911.md` |"
    if old in text:
        text = replace_once(text, old, new, "SI Table S11 status")
    elif new not in text:
        raise RuntimeError("SI Table S11 status anchor not found")
    old2 = "6. Independent Bader implementation results validate robustness but do not redefine the frozen primary metric."
    new2 = "6. The resolved 24-system P3A panel validates classification transfer across the tested independent on-grid implementation, while near-grid threshold switches demonstrate implementation dependence. It does not redefine the frozen primary metric and does not establish grid convergence."
    if old2 in text:
        text = replace_once(text, old2, new2, "SI P3A boundary")
    elif new2 not in text:
        raise RuntimeError("SI P3A boundary anchor not found")
    path.write_text(text, encoding="utf-8")


def update_claim_matrix() -> None:
    path = ROOT / "paper/CLAIM_EVIDENCE_MATRIX.md"
    text = path.read_text(encoding="utf-8")
    if "| 16 | QSQ classification transfers across an independent on-grid Bader implementation" in text:
        return
    anchor = "\n## Retracted numbers — must not be cited\n"
    rows = (
        "\n| 15 | The frozen five-seed QSQ screen prospectively stratifies unseen response risk under the declared iid-uniform perturbation model | 254 development materials × 59 pre-registered fresh perturbations = 14,986/14,986 valid outcomes. At 1e-3 e, coverage is 143/254 (56.3%); fresh exceedance risk is 1.600% in eligible vs 81.325% in screen-rejected materials, rejected/eligible RR 50.83×. | `analysis/research_upgrade/P2_FRESH_PROBE_REPORT.md`; `validation/qsq_prospective/p2_fresh_probes/` | F3 | **CONFIRMED** | Validates risk stratification for unseen iid-uniform draws on studied materials, not worst-case stability, simultaneous material-wise certification, or new-material generalization |\n"
        "| 16 | QSQ classification transfers across an independent on-grid Bader implementation but is not implementation-free | Resolved deterministic 24-system panel: Henkelman on-grid agrees with frozen BaderKit classification in 24/24 materials at 1e-4, 1e-3 and 1e-2 e (100%, kappa 1.000), floor-rank rho=0.995. Henkelman near-grid agreement is 82.6%/83.3%/95.8%, rho=0.754. Engineering retry recovered 360/360 pre-solver-blocked cells after the failure family was frozen, without changing scientific definitions. | `validation/qsq_prospective/p3a_implementation_transfer_resolved/`; `analysis/research_upgrade/P3A_FAILURE_TAXONOMY.md` | S11 / F5 support | **CONFIRMED** for targeted implementation transfer | Deterministic mechanism panel, not prevalence sample; P3A does not establish density-grid convergence or a unique physical Bader reference |\n"
        + anchor
    )
    text = replace_once(text, anchor, rows, "claim matrix P2/P3A claims")
    path.write_text(text, encoding="utf-8")


def main() -> int:
    verify_results()
    update_manuscript()
    update_plan()
    update_s11()
    update_si_index()
    update_claim_matrix()
    print("P3A resolved evidence integrated successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
