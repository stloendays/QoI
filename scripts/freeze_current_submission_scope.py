#!/usr/bin/env python3
"""Synchronize reader-facing planning/story files after the submission scope freeze.

This script changes no scientific data, figures, thresholds, or manuscript
results. It removes stale planning language after P1-P4 completion and records
the P5 NO-GO decision for the current submission.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"{label}: expected one exact anchor, found {n}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def insert_before_once(path: Path, anchor: str, block: str, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    n = text.count(anchor)
    if n != 1:
        raise RuntimeError(f"insert {marker}: expected one anchor, found {n}")
    path.write_text(text.replace(anchor, block + anchor, 1), encoding="utf-8")


def main() -> None:
    status = ROOT / "analysis/research_upgrade/CURRENT_STATUS.md"
    plan = ROOT / "paper/RESEARCH_UPGRADE_PLAN.md"
    story = ROOT / "paper/CURRENT_PAPER_STORY_20260911.md"
    editorial = ROOT / "paper/EDITORIAL_POLISH_NOTES_20260911.md"
    claims = ROOT / "paper/CLAIM_EVIDENCE_MATRIX.md"
    scope = ROOT / "paper/RESEARCH_SCOPE_FREEZE_20260911.md"
    audit = ROOT / "paper/SUBMISSION_UPGRADE_CROSS_REFERENCE_AUDIT_20260911.md"

    if "Status: **FROZEN_FOR_SUBMISSION**" not in scope.read_text(encoding="utf-8"):
        raise RuntimeError("scope-freeze decision missing")
    if "Status: **PASS**" not in audit.read_text(encoding="utf-8"):
        raise RuntimeError("submission-upgrade audit is not PASS")

    replace_once(
        status,
        "- **P5 — second sensitive task: OPTIONAL / NOT STARTED.** It should be added only if it materially strengthens transfer without diluting the electronic-density story.",
        "- **P5 — second sensitive task: NO-GO FOR CURRENT SUBMISSION.** Repository asset audit found no already-frozen, independently implemented second nonlinear/topology-sensitive QoI that could be added outcome-blind at modest scope. Opening a new endpoint after the completed Bader/P4 results would create avoidable outcome-driven-selection risk.",
        "CURRENT_STATUS P5",
    )
    replace_once(
        status,
        "## Immediate next actions\n\n1. Integrate the **resolved P3A** result into the manuscript/SI as implementation-transfer evidence, maintaining the grid-convergence boundary.\n2. Integrate **P4 as a negative/control-boundary case study** in Discussion/SI: no sign errors at common-tight settings, QSQ conservative for this coarse endpoint, optional audit-call reduction only.\n3. Re-run the claim/evidence matrix and manuscript–Figure–SI numeric cross-reference audit after these additions.\n4. Decide whether P5 is scientifically worth the scope expansion. Do not add a second task merely to obtain a positive result after P4's frozen null endpoint.\n5. If no compelling P5 can be specified outcome-blind with low scope cost, freeze the research scope and move to submission assembly.\n",
        "## Submission-chain closure\n\nP3A and P4 have been integrated into the active manuscript/SI without changing the Abstract or Figure 3 headline. `paper/SUBMISSION_UPGRADE_CROSS_REFERENCE_AUDIT_20260911.md` cross-checks P1–P4 machine-readable results against the manuscript, Figure 3 source, SI, Claim–Evidence Matrix and active status files and is **PASS**. Claims 15–17 are the current upgrade-era claim records.\n\nThe current research scope is now **FROZEN_FOR_SUBMISSION** by `paper/RESEARCH_SCOPE_FREEZE_20260911.md`. P5 is NO-GO for this submission; P3B remains deferred.\n\n## Immediate next actions\n\n1. Keep the scientific scope frozen unless an explicit reviewer-requested or scope-reopening addendum is created.\n2. Finish submission assembly from the locked manuscript, real data-driven figures and current SI.\n3. Create a persistent archival release/DOI and freeze repository provenance for the submitted version.\n4. Apply journal-specific formatting and final reference/figure-count requirements without changing the locked scientific estimands.\n5. Generate the final Word/PDF package only after these non-scientific checks are complete.\n",
        "CURRENT_STATUS next actions",
    )

    replace_once(
        plan,
        "## P5 — Transfer beyond Bader\n\n**Status: OPTIONAL / NOT STARTED.**\n\nA second topology-sensitive task should be attempted only if it can be specified outcome-blind, executed with modest additional scope and genuinely tests transfer beyond the current density/Bader setting. It must not be introduced merely to search for a positive result after P4's frozen null endpoint.\n\nIf no compelling second task meets those conditions, freeze the research scope and proceed to submission assembly.\n\n## Execution order from the current checkpoint\n\n1. Integrate resolved P3A as implementation-transfer evidence in the active manuscript and SI, preserving the grid-convergence boundary.\n2. Integrate P4 as Discussion/SI **contract-boundary / negative-control evidence**, not as a main-figure headline.\n3. Re-run the claim–evidence and numeric manuscript–Figure–SI cross-reference audits after P3A/P4 integration.\n4. Make one explicit P5 go/no-go decision. Prefer scope freeze if a second task would dilute the paper or require outcome-driven selection.\n5. After scope freeze, move to final submission assembly, archival DOI and journal-specific formatting.\n",
        "## P5 — Transfer beyond Bader\n\n**Status: NO-GO FOR CURRENT SUBMISSION.**\n\nA repository asset audit found no already-frozen, independently implemented second nonlinear/topology-sensitive QoI with a reference implementation, outcome-blind cohort and low marginal execution cost. Electron count and Hartree potential remain intentional controls rather than a second sensitive-task validation. Defining a new endpoint after observing the completed Bader evidence and the prespecified P4 null result would materially widen the scope and create avoidable outcome-driven-selection risk.\n\nThe current submission therefore stops at P4. P5 may be reconsidered only through an explicit scope-reopening addendum or a targeted reviewer request. The decision record is `paper/RESEARCH_SCOPE_FREEZE_20260911.md`.\n\n## Execution order from the current checkpoint\n\n1. Preserve the **FROZEN_FOR_SUBMISSION** scientific scope: P0–P4 resolved, P3B deferred, P5 no-go.\n2. Maintain the PASS state of `paper/SUBMISSION_UPGRADE_CROSS_REFERENCE_AUDIT_20260911.md` while performing only non-scientific editorial changes.\n3. Create a persistent archival release/DOI and record the submitted repository commit.\n4. Apply target-journal figure-count, reference and formatting requirements without altering the locked estimands or primary evidence hierarchy.\n5. Build the final Word/PDF submission package from the polished manuscript, locked real-data figures and current SI.\n",
        "RESEARCH_UPGRADE_PLAN P5 and execution order",
    )

    p4_story = """### P4 — outcome-blind chemical-decision boundary case\n\nA chemistry/provenance/geometry-only audit of the 68 NOMAD development slabs froze **five paired chemical states** before QSQ, codec, P2/P3A or Bader outcomes were used for inclusion. All five passed the pre-specified BaderKit/Henkelman on-grid reference gate. The resolved compression analysis contains **216/216 successful solver cells** and **60/60** common-tight qualitative target-atom charge-transfer directions matching the frozen reference.\n\nThis is a deliberately useful **null correctness result**. The unqualified baseline already has zero sign errors, while QSQ at `1e-3 e` retains **36/60 trials from 3/5 pairs** and also has zero errors. QSQ therefore does not improve this coarse endpoint; instead, P4 demonstrates that strict numerical Bader fidelity and preservation of a large-margin qualitative chemical direction are distinct measurement contracts. Under the pre-specified optional independent-solver audit, QSQ-targeted escalation uses 48 Henkelman reconstructed-state calls / 397.2 s versus 108 / 733.3 s for blanket escalation; this is audit-cost reduction only, not a correctness gain.\n\n"""
    insert_before_once(story, "## Supporting evidence chain\n", p4_story, "### P4 — outcome-blind chemical-decision boundary case")
    replace_once(
        story,
        "## Current research boundary and next gate\n\n**P3A is complete. P3B is not.** The next high-value research task is true electronic-structure grid convergence on cases for which the original calculation inputs or an equivalent reproducible calculation protocol can be recovered. Interpolation of an existing density does not count.\n\nThe P4 chemistry-decision utility protocol has already been frozen outcome-blind. It should be executed after the P3 numerical-reference question is closed sufficiently to define the high-precision reference.\n\nP5, transfer to a second topology-sensitive task, remains optional and should be undertaken only if it can be added without diluting the electronic-density story.\n",
        "## Current research scope\n\n**The current submission scope is frozen.** P0–P4 are resolved. P3B new-DFT grid convergence is explicitly deferred and is not required for the current claim; P5 is NO-GO for this submission after a repository asset audit found no already-frozen second sensitive QoI that could be added outcome-blind at modest scope.\n\nThe evidence hierarchy is locked: **P1 equal-search control → P2 prospective fresh-perturbation validation → P3A independent on-grid implementation transfer**, with P4 as a secondary measurement-contract boundary/null case. The historical 97.2%/95.5% full-record fractions remain sensitivity/provenance results rather than the headline.\n\nNo new scientific endpoint, perturbation family, primary cohort, DFT convergence experiment or primary threshold should be added before submission without an explicit scope-reopening addendum. Remaining work is archival DOI, journal-specific formatting, figure/SI assembly and final Word/PDF generation.\n",
        "CURRENT_PAPER_STORY research boundary",
    )

    replace_once(
        editorial,
        "3. **Make Figure 3 the narrative pivot.** The central quantitative result is now reached quickly: 97.2% and 95.5% of naive failures at the two strictest Bader contracts are non-evaluable, and 46.3% of naive passes at `1e-4 e` are also non-evaluable.",
        "3. **Make Figure 3 the narrative pivot.** The central quantitative result is prospective rather than retrospective: after equalizing codec search opportunity, QSQ-rejected targets remain much more likely to lack a numerical pass, and the frozen gate then separates 1.600% from 81.325% fresh-perturbation exceedance risk at the primary `1e-3 e` endpoint (50.83× risk ratio). Historical 97.2%/95.5% full-record fractions remain secondary design-sensitivity provenance.",
        "EDITORIAL Figure 3 strategy",
    )
    replace_once(
        editorial,
        "`problem → benchmark design → headline reclassification → mechanism/confound controls → implication`",
        "`problem → benchmark design → prospective qualification evidence → mechanism/confound controls → implication`",
        "EDITORIAL Abstract sequence",
    )
    replace_once(
        editorial,
        "Secondary numerical details such as the full floor-normalized distributions were removed from the abstract because they compete with the main 97.2% / 95.5% result.",
        "Secondary numerical details such as implementation transfer and the P4 chemical-direction null case remain outside the abstract because they would compete with the stronger P1/P2 validation sequence. The Abstract keeps the 14,986-trial prospective result as the quantitative anchor.",
        "EDITORIAL Abstract detail",
    )
    replace_once(
        editorial,
        "- **Figure 3:** binary benchmark → three-state certification (**central result**);",
        "- **Figure 3:** equal-search benchmark control + prospective fresh-perturbation risk stratification (**central validation result**);",
        "EDITORIAL Results Figure 3",
    )
    replace_once(
        editorial,
        "## Remaining pre-submission items\n\n1. Replace the repository-only Data and Code Availability statement with a persistent archival DOI (for example, a frozen release deposited in an archival repository) before publication.\n2. Perform a final reference audit against `paper/REFERENCES.md` and the selected journal's reference requirements.\n3. Decide whether the target journal needs 5, 6 or 7 main-text figures before building the final Word/PDF submission package.\n4. Run one consistency audit across manuscript, captions, Figure Map and Supplement for the terms `QSQ`, `stability floor`, `eligible`, `certified`, `eligible but not certified`, and `non-evaluable`.\n5. Build the final Word manuscript only from the polished draft and the locked data-driven figures.\n",
        "## Remaining pre-submission items\n\nThe scientific scope is now frozen by `paper/RESEARCH_SCOPE_FREEZE_20260911.md`; P3B is deferred and P5 is no-go for the current submission. The P1–P4 submission-chain cross-reference audit is PASS. Remaining tasks are non-scientific submission work:\n\n1. Replace the repository-only Data and Code Availability statement with a persistent archival DOI/frozen release and record the submitted commit.\n2. Perform the journal-specific final reference-format audit against `paper/REFERENCES.md`.\n3. Decide whether the target journal requires 5, 6 or 7 main-text figures; consolidate only at the presentation level, with Figure 3 retained as the central validation figure.\n4. Re-run terminology/cross-reference checks only if editorial changes touch claims, captions or SI numbering; scientific estimands remain locked.\n5. Build the final Word/PDF manuscript only from the polished draft and locked real data-driven figures.\n",
        "EDITORIAL remaining items",
    )

    replace_once(
        claims,
        "> **Research interpretation superseded in part (2026-09-11).** The common-ladder and reused-seed audits require a stronger research programme, not just submission assembly. Full-record 97.2%/95.5% are historical ladder-dependent fractions, not causal misattribution estimates. Common-base values are 83.2%/56.5%; numerical agreement remains defined even when the reference fails QSQ. The authoritative next-step plan is `paper/RESEARCH_UPGRADE_PLAN.md`; executed evidence is `analysis/research_upgrade/REPORT.md`. Older quantitative claims below retain their original data scope.",
        "> **Submission-scope interpretation lock (2026-09-11).** The research-strengthening programme is complete through P4 and the current scientific scope is frozen. Full-record 97.2%/95.5% values remain historical ladder-dependent fractions, not causal misattribution estimates. The central evidence is P1 equal-search separation plus P2 prospective fresh-perturbation discrimination, supported by P3A independent on-grid implementation transfer. P4 is a prespecified null correctness result for a coarse chemical-direction endpoint and is retained as measurement-contract boundary evidence. P3B new DFT is deferred and P5 is no-go for the current submission. Numerical agreement remains defined even when the reference fails QSQ.",
        "CLAIM matrix interpretation lock",
    )
    replace_once(
        claims,
        "Last updated: 2026-09-11 (Claim 14 added after the frozen binary-to-three-state certifiability audit; Claim 1 remains restated after within-material matching on realized L∞).",
        "Last updated: 2026-09-11 (Claims 15–17 record the completed prospective, implementation-transfer and chemical-contract-boundary upgrades; Claim 14 is retained as the audited historical ladder-design sensitivity result).",
        "CLAIM matrix last updated",
    )
    replace_once(
        claims,
        "| 14 | Full-record reclassification is strongly ladder-design-dependent | Full-record 97.2%/95.5%/56.5% reproduce, but common-base fractions are 83.2%/56.5%/51.3%; 214 added 1e-3 e passes all belong to the eligible group. Causal misattribution interpretation withdrawn. | `analysis/research_upgrade/ladder_summary.csv`; `analysis/research_upgrade/ladder_transitions.csv` | F3 historical full record | **CONFIRMED** for the audited design dependence | Complete a uniform tight ladder; report rejection prevalence and validate held-out usefulness |",
        "| 14 | Full-record reclassification is strongly ladder-design-dependent | Full-record 97.2%/95.5%/56.5% reproduce, but common-base fractions are 83.2%/56.5%/51.3%; 214 added 1e-3 e passes all belong to the eligible group. Causal misattribution interpretation withdrawn. | `analysis/research_upgrade/ladder_summary.csv`; `analysis/research_upgrade/ladder_transitions.csv` | F3 historical full record | **CONFIRMED** for the audited design dependence | Uniform tight-ladder completion and prospective validation are now completed in P1/P2; the historical fractions remain secondary sensitivity/provenance evidence |",
        "CLAIM 14 remaining risk",
    )

    print("Current submission scope synchronization: PASS")


if __name__ == "__main__":
    main()
