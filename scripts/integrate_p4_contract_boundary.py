#!/usr/bin/env python3
"""Integrate the frozen P4 null result into the submission chain.

This script is deliberately narrow: it inserts a secondary P4 result, a
Discussion boundary paragraph and a Methods subsection; generates SI Tables
S15-S16 and a numeric audit; and adds one claim-matrix row. It does not change
the Abstract, title, Figure 3, P1/P2/P3A results, or any scientific data.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
VAL = ROOT / "validation" / "qsq_prospective"

MANUSCRIPT = PAPER / "MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md"
SI = PAPER / "SUPPLEMENTARY_INFORMATION_DRAFT_20260911.md"
CLAIMS = PAPER / "CLAIM_EVIDENCE_MATRIX.md"
REF = VAL / "p4_reference_adjudication" / "p4_reference_valid_pairs.csv"
TRIALS = VAL / "p4_chemical_decisions_resolved" / "p4_trial_decisions.csv"
POLICY = VAL / "p4_chemical_decisions_resolved" / "p4_policy_summary.csv"
ESC = VAL / "p4_chemical_decisions_resolved" / "p4_escalation_summary.csv"
MANIFEST = VAL / "p4_chemical_decisions_resolved" / "execution_manifest.json"


def rows(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def replace_once(text: str, anchor: str, repl: str, label: str) -> str:
    n = text.count(anchor)
    if n != 1:
        raise RuntimeError(f"{label}: expected one anchor, found {n}")
    return text.replace(anchor, repl, 1)


def pct(x: str | float) -> str:
    return f"{100 * float(x):.1f}%"


def main() -> None:
    ref = rows(REF); trials = rows(TRIALS); policy = rows(POLICY); esc = rows(ESC)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    # Hard numeric gates before touching prose.
    if manifest.get("status") != "COMPLETE_RESOLVED":
        raise RuntimeError("P4 resolved manifest not complete")
    expected_manifest = {
        "reference_valid_pairs": 5,
        "planned_compressed_solver_evaluations": 216,
        "final_successful_solver_rows": 216,
        "final_failed_solver_rows": 0,
        "first_run_success_rows_reused": 72,
        "first_run_failed_rows_preserved": 144,
        "retry_success_rows": 144,
        "retry_failed_rows": 0,
    }
    for k, v in expected_manifest.items():
        if manifest.get(k) != v:
            raise RuntimeError(f"P4 manifest drift {k}: {manifest.get(k)!r} != {v!r}")
    if len(ref) != 5 or any(r["reference_status"] != "REFERENCE_VALID" for r in ref):
        raise RuntimeError("P4 reference cohort drift")
    if len(trials) != 60:
        raise RuntimeError(f"P4 trial count drift: {len(trials)}")
    if any(str(r["direct_valid"]).lower() != "true" for r in trials):
        raise RuntimeError("not all P4 direct trials are valid")
    if any(str(r["direct_adverse"]).lower() != "false" for r in trials):
        raise RuntimeError("P4 sign endpoint is no longer null")
    if any(str(r["direct_zero_unresolved"]).lower() != "false" for r in trials):
        raise RuntimeError("P4 zero/unresolved sign appeared")

    p_all = {(r["scope"], r["policy"]): r for r in policy}
    q = p_all[("ALL", "frozen_qsq")]
    nq = p_all[("ALL", "no_qualification")]
    if int(nq["retained_trials"]) != 60 or int(nq["decision_errors_or_zero"]) != 0:
        raise RuntimeError("P4 no-qualification summary drift")
    if int(q["retained_trials"]) != 36 or int(q["unique_retained_pairs"]) != 3 or int(q["decision_errors_or_zero"]) != 0:
        raise RuntimeError("P4 QSQ summary drift")
    e_all = {(r["scope"], r["policy"]): r for r in esc}
    qt = e_all[("ALL", "qsq_targeted")]; ea = e_all[("ALL", "escalate_all")]
    if int(qt["henkelman_reconstructed_state_calls"]) != 48 or int(ea["henkelman_reconstructed_state_calls"]) != 108:
        raise RuntimeError("P4 escalation call-count drift")

    result_block = r'''<!-- P4_CONTRACT_BOUNDARY_RESULT -->
### A coarse chemical direction can remain stable outside a strict numerical contract

We next tested whether strict numerical qualification translates directly into a coarse chemical decision. Before inspecting QSQ or compression outcomes, a chemistry-, provenance- and geometry-only audit of the 68 NOMAD development slabs froze five paired states from GaN electrochemical-surface and RuO$_2$ CO$_2$RR datasets, together with a persistent local target atom for each pair. All five pairs passed a pre-specified source-reference gate requiring BaderKit on-grid and independent Henkelman on-grid analyses to agree on the non-zero sign of the target-atom charge change, with $|\Delta q|\ge 0.02\,e$ in both implementations and inter-implementation disagreement no greater than $0.01\,e$.

Across the three codecs and the four common tight settings, all 60 reconstructed BaderKit decisions preserved the frozen reference sign. The unqualified baseline therefore has 0/60 adverse or unresolved sign decisions. QSQ at $10^{-3}\,e$ retains 36/60 trials from three of the five pairs and also has zero sign errors. Thus QSQ does not improve correctness for this deliberately coarse endpoint; instead, the result demonstrates that a strict per-atom numerical-fidelity contract and preservation of a qualitative charge-transfer direction are different scientific targets. Under a separately frozen optional independent-solver audit, QSQ-targeted escalation resolves all 60 trials with 48 Henkelman reconstructed-state calls (397.2 s measured solver time), compared with 108 calls (733.3 s) for auditing every trial. This is a reduction in audit burden relative to blanket second-solver checking, not a correctness gain over the direct decisions, which were already error-free (Supplementary Tables S15-S16).

'''

    discussion_block = r'''<!-- P4_CONTRACT_BOUNDARY_DISCUSSION -->
The outcome-blind chemical-pair experiment supplies a useful negative control on what QSQ should and should not be expected to predict. All 60 common-tight reconstructions preserved the sign of a well-separated local charge-transfer decision even though the strict $10^{-3}\,e$ QSQ screen retained only three of the five pairs. Numerical certifiability at a specified charge tolerance is therefore not interchangeable with preservation of a coarser qualitative interpretation. This is not evidence against qualification; it is evidence that the measurement contract must match the scientific question. QSQ can be conservative for a coarse decision whose margin is much larger than the numerical tolerance. In this small case-study cohort it offered no correctness benefit over the unqualified baseline, although it reduced the number of independent-solver calls required by a pre-specified optional audit relative to checking every reconstruction. We therefore treat this result as a scope boundary rather than a performance headline.

'''

    methods_block = r'''<!-- P4_CONTRACT_BOUNDARY_METHODS -->
### Outcome-blind chemical-decision case study

The P4 case-study cohort was constructed before reading QSQ, codec, P2/P3A or Bader outcomes for candidate inclusion. Starting from the 68 NOMAD development slab states, primary pairs were required to share the same NOMAD upload provenance, density-grid shape and lattice within fixed tolerances; state B had to add one to four H/C/O atoms; all state-A atoms had to map to same-element atoms in state B within 0.35 Å; and a persistent host atom within 3.0 Å of an added atom was selected as the target using geometry only. This froze five pairs across two source uploads.

For each pair and solver $s$, the qualitative endpoint was the sign of $\Delta q_s=q_s(B,\mathrm{target}_B)-q_s(A,\mathrm{target}_A)$. A binary source reference was accepted only when BaderKit 0.10.2 on-grid and Henkelman Bader 1.05 on-grid gave the same non-zero sign, both had $|\Delta q|\ge0.02\,e$, and their $\Delta q$ values differed by at most $0.01\,e$. All five frozen pairs met this rule. Each state was then compressed with ZFP, SZ3 and SPERR at the common tight relative-tolerance ladder $\{10^{-7},3\times10^{-7},10^{-6},3\times10^{-6}\}$, giving 60 pair-codec-setting decisions. QSQ retention required both states in a pair to pass the frozen five-seed QSQ gate at $10^{-3}\,e$.

The first compressed-stage execution and its failures remain archived. Before retry, all 144 failed solver cells were assigned to two missing-work-directory engineering families with zero unclassified failures. The retry executed exactly those failed keys and changed no candidate, target atom, reference margin, codec setting, solver definition, QSQ threshold or decision policy. The resolved analysis contains 216/216 successful compressed solver cells. No new electronic-structure calculation was used in this case study; the source reference is a two-implementation on-grid consensus rather than a grid-converged physical Bader truth.

'''

    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    if "<!-- P4_CONTRACT_BOUNDARY_RESULT -->" not in manuscript:
        anchor = "### Realized distortion, not nominal tolerance, is required for fair codec comparison\n"
        manuscript = replace_once(manuscript, anchor, result_block + anchor, "P4 Results insertion")
    if "<!-- P4_CONTRACT_BOUNDARY_DISCUSSION -->" not in manuscript:
        anchor = "The QSQ perturbation test illustrates a second consequence of the framework: the stability test itself is part of the measurement contract."
        manuscript = replace_once(manuscript, anchor, discussion_block + anchor, "P4 Discussion insertion")
    if "<!-- P4_CONTRACT_BOUNDARY_METHODS -->" not in manuscript:
        anchor = "### QoI Stability Qualification and eligibility\n"
        manuscript = replace_once(manuscript, anchor, methods_block + anchor, "P4 Methods insertion")
    MANUSCRIPT.write_text(manuscript, encoding="utf-8")

    # SI tables are generated from the machine-readable resolved outputs.
    trial_by_pair = {}
    for r in trials:
        trial_by_pair.setdefault(r["pair_id"], r)
    t = [
        "# Supplementary Tables S15-S16 — P4 chemical-decision boundary case study",
        "",
        "These tables are generated directly from the frozen P4 reference and resolved compressed-decision outputs. The five-pair cohort is a targeted case study, not a prevalence sample.",
        "",
        "## Supplementary Table S15 | Outcome-blind chemistry pairs and two-implementation source references",
        "",
        "| Pair | Source chemistry | State A → State B | Added atoms | Target | Δq BaderKit (e) | Δq Henkelman (e) | Pair QSQ eligible at 1e-3 e |",
        "|---|---|---|---|---|---:|---:|---:|",
    ]
    for r in ref:
        tr = trial_by_pair[r["pair_id"]]
        t.append(
            f"| {r['pair_id']} | {r['upload_description']} | {r['state_A_formula']} → {r['state_B_formula']} | {r['added_composition']} | {r['target_species']} | {float(r['delta_q_baderkit_ongrid_e']):.6f} | {float(r['delta_q_henkelman_ongrid_e']):.6f} | {tr['pair_qsq_eligible']} |"
        )
    t += [
        "",
        "Reference acceptance was frozen before charge outcomes: identical non-zero sign in BaderKit and Henkelman on-grid, minimum |Δq| ≥ 0.02 e, and inter-solver |Δq| disagreement ≤ 0.01 e. All five pairs passed.",
        "",
        "## Supplementary Table S16 | Frozen direct-selection and optional escalation policies",
        "",
        "### Direct decision policies, pooled across codecs",
        "",
        "| Policy | Retained / valid | Coverage | Adverse or zero-direction decisions | Error rate | Unique retained pairs |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    order = ["no_qualification", "realized_linf_coverage_matched", "archived_float32_probe", "frozen_qsq"]
    for name in order:
        r = p_all[("ALL", name)]
        t.append(f"| {name} | {r['retained_trials']} / {r['computationally_valid_trials']} | {pct(r['coverage_of_valid'])} | {r['decision_errors_or_zero']} | {pct(r['retained_error_rate'])} | {r['unique_retained_pairs']} |")
    t += [
        "",
        "### Optional independent-solver escalation",
        "",
        "| Policy | Resolved / valid | Needs review | Errors among resolved | Henkelman state calls | Henkelman wall time (s) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name in ("qsq_targeted", "escalate_all"):
        r = e_all[("ALL", name)]
        t.append(f"| {name} | {r['resolved_trials']} / {r['valid_trials']} | {r['needs_review_trials']} | {r['errors_among_resolved']} | {r['henkelman_reconstructed_state_calls']} | {float(r['henkelman_wall_seconds_policy_calls']):.1f} |")
    t += [
        "",
        "Interpretation: no policy improves sign correctness because the unqualified common-tight baseline already has zero adverse decisions. QSQ is more conservative than this coarse sign contract. The lower independent-solver call count for targeted escalation is an audit-cost comparison only.",
    ]
    tables_path = PAPER / "SUPPLEMENTARY_TABLES_S15_S16_20260911.md"
    tables_path.write_text("\n".join(t) + "\n", encoding="utf-8")

    # Append a compact SI note without rewriting existing SI structure.
    si = SI.read_text(encoding="utf-8")
    if "<!-- P4_CONTRACT_BOUNDARY_SI -->" not in si:
        si += r'''

<!-- P4_CONTRACT_BOUNDARY_SI -->
## Supplementary Note | Outcome-blind chemical-decision boundary case study

An outcome-blind chemistry/provenance/geometry audit of the 68 NOMAD development slabs froze five paired states before QSQ, codec or Bader outcomes were inspected for inclusion. All five passed the independently frozen two-implementation source-reference rule. Across ZFP, SZ3 and SPERR on the four common tight settings, all 60 direct qualitative target-atom charge-transfer directions were preserved after compression. QSQ at $10^{-3}\,e$ retained 36/60 trials from three pairs, while the unqualified baseline retained all 60; both had zero observed sign errors. This deliberately negative result shows that the strict numerical Bader contract and a coarse sign-level chemical interpretation are different fidelity targets. Full pair-level reference values and policy accounting are provided in Supplementary Tables S15-S16.

The resolved compressed analysis contains 216/216 successful solver cells. The first execution's 144 failures were classified before retry as missing-work-directory engineering errors, and the retry executed exactly those failed keys without changing the scientific design. P3B new-DFT grid convergence was not used; the source reference is a BaderKit/Henkelman on-grid consensus under the declared density representation.
'''
        SI.write_text(si, encoding="utf-8")

    claims = CLAIMS.read_text(encoding="utf-8")
    if "| 17 | Strict QSQ numerical qualification is not equivalent" not in claims:
        row = (
            "| 17 | Strict QSQ numerical qualification is not equivalent to preservation of a coarse qualitative chemical direction | "
            "Outcome-blind P4 case study: 5/5 frozen chemistry pairs pass the two-implementation source-reference gate; 216/216 compressed solver cells resolve; all 60/60 common-tight pair-codec-setting BaderKit sign decisions preserve the reference direction. QSQ at 1e-3 e retains 36/60 trials from 3/5 pairs, while no qualification retains 60/60; both have 0 observed sign errors. Optional QSQ-targeted independent-solver audit uses 48 Henkelman state calls / 397.2 s versus 108 / 733.3 s for escalate-all. | "
            "`validation/qsq_prospective/p4_candidate_audit/`; `validation/qsq_prospective/p4_reference_adjudication/`; `validation/qsq_prospective/p4_chemical_decisions_resolved/` | S15-S16 / Discussion | **CONFIRMED** for the frozen case-study endpoint | Small 5-pair cohort; sign endpoint has a large chemical margin and is not a prevalence estimate; QSQ shows no correctness gain because the baseline is already error-free; no DFT grid-convergence claim |\n"
        )
        claims = replace_once(claims, "\n## Retracted numbers — must not be cited", "\n" + row + "\n## Retracted numbers — must not be cited", "claim 17 insertion")
        CLAIMS.write_text(claims, encoding="utf-8")

    audit = [
        "# P4 submission-chain numeric audit",
        "",
        "Status: **PASS**",
        "",
        "The integration script stopped unless all of the following machine-readable conditions were true:",
        "",
        "- reference-valid pairs = 5/5;",
        "- resolved compressed solver cells = 216/216, final failures = 0;",
        "- immutable first-run successes reused = 72; preclassified failed cells = 144; retry successes = 144, retry failures = 0;",
        "- direct chemistry trials = 60/60 valid; adverse or zero-direction decisions = 0;",
        "- no-qualification retention = 60/60 with 0 adverse decisions;",
        "- frozen QSQ retention = 36/60 from 3/5 pairs with 0 adverse decisions;",
        "- QSQ-targeted independent-solver calls = 48 versus 108 for escalate-all.",
        "",
        "The manuscript insertion is intentionally secondary: no Abstract, title or Figure 3 headline was changed. P4 is represented as a null correctness result and measurement-contract boundary.",
    ]
    (PAPER / "P4_NUMERIC_AUDIT_20260911.md").write_text("\n".join(audit) + "\n", encoding="utf-8")

    print("P4 submission-chain integration: PASS")


if __name__ == "__main__":
    main()
