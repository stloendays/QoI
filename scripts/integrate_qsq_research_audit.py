#!/usr/bin/env python3
"""Integrate executed audit findings without changing frozen scientific data.

All edits are prepared in memory and checked before any file is written.
Historical Figure 3 outputs retain their original counts and are labelled
full-record analyses; new validation work orders are not claimed as results.
"""
from pathlib import Path
import hashlib
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MARKER = "<!-- QSQ_RESEARCH_AUDIT_INTEGRATED -->"
NAMES = {
    "manuscript": "paper/MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md",
    "readme": "README.md",
    "story": "paper/CURRENT_PAPER_STORY_20260911.md",
    "matrix": "paper/CLAIM_EVIDENCE_MATRIX.md",
}


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"Expected one exact target, found {text.count(old)}: {old[:85]}")
    return text.replace(old, new, 1)


def section(text, start, end, replacement):
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError(f"Ambiguous section boundaries: {start} / {end}")
    a, b = text.index(start), text.index(end)
    if b <= a:
        raise ValueError("Reversed section boundaries")
    return text[:a] + replacement.rstrip() + "\n\n" + text[b:]


def main():
    old = {k: (ROOT / p).read_text() for k, p in NAMES.items()}
    if all(MARKER in s for s in old.values()):
        print("Research audit already integrated; no changes")
        return
    if any(MARKER in s for s in old.values()):
        raise ValueError("Partial integration requires manual review")
    stats = pd.read_csv(ROOT / "analysis/research_upgrade/ladder_summary.csv")
    z = stats[(stats.scope == "all") & (stats.design == "base_only")].sort_values("tau_e")
    if list(z.no_pass_observed) != [740, 524, 119] or list(z.non_evaluable_no_pass) != [616, 296, 61]:
        raise ValueError("Audit numbers changed; regenerate scientific prose explicitly")
    new = dict(old)
    m = old["manuscript"]
    abstract = r'''## Abstract

Numerical agreement with a fixed reference does not by itself establish that a downstream scientific interpretation is robust to small input changes. We investigate this distinction for Bader charges derived from compressed electronic densities using 6,343 frozen reconstructions of 254 bulk and slab systems, together with an earlier frozen 63-system external confirmation. QoI Stability Qualification (QSQ) screens reference sensitivity using five fixed-seed perturbations. On the common base tolerance ladder, 616 of 740 numerical no-pass decisions (83.2%) at $10^{-4}\,e$ and 296 of 524 (56.5%) at $10^{-3}\,e$ occur on material-threshold pairs rejected by QSQ. The previously higher fractions of 97.2% and 95.5% arise in a full record with eligibility-targeted tight-ladder access, demonstrating that search opportunity must also be controlled. A retrospective four-seed/one-seed holdout audit detects further exceedances in 18 of 338 admitted material-splits at the strictest threshold; this is not independent validation of the deployed five-seed rule. Re-derived Bader charges respond irregularly through basin migration, whereas Hartree-potential error behaves more regularly; realized-distortion matching separates nominal-tolerance effects from residual codec differences. The results motivate reporting reference stability and fixed-pipeline fidelity as distinct benchmark axes. QSQ provides an auditable operational screen, while calibrated robust certification requires independent validation of the stated perturbation model.'''
    m = section(m, "## Abstract\n", "**Keywords:**", abstract)
    m = replace_once(m,
        "A downstream tolerance is meaningful only if the reference analysis can distinguish changes at that scale. Otherwise, a reconstruction that exceeds the tolerance may reflect either compression-induced error or numerical instability of the analysis used to define the target. A binary pass/fail benchmark cannot separate these possibilities. We therefore treat numerical identifiability as a prerequisite for codec scoring: the reference QoI is first qualified at the requested tolerance, and only qualified material–threshold pairs are assigned compression success or failure (Fig. 1).",
        "Two targets must be distinguished. Fixed-pipeline fidelity asks whether the decoded field reproduces the numerical result obtained from the exact reference input; this comparison remains well defined even for a sensitive analysis. Robust scientific fidelity additionally asks whether the interpretation survives a declared class of small input changes. We use QSQ to screen this second requirement and report its outcome alongside numerical agreement (Fig. 1). A failed screen does not show that a particular codec discrepancy was not compression-induced, and a successful finite probe panel is not a worst-case stability guarantee.")
    m = replace_once(m,
        "The resulting framework replaces an unconditional codec leaderboard with a stability-qualified rate–fidelity benchmark in which a compressor is judged only against scientific tolerances that the downstream analysis can independently resolve.",
        "The resulting framework reports reference qualification alongside rate-fidelity performance. The new research audit also checks whether unequal tolerance-ladder access and finite probe coverage affect this interpretation; previously observed external outcomes are not reused as untouched tests of a revised method.")
    results = r'''### Reference stability and numerical agreement are distinct benchmark axes

QSQ applies five fixed-seed, non-order-preserving perturbations to each reference density at that material's float32 $L_\infty$ scale. The maximum Bader response is an operational susceptibility scale, historically called the stability floor. A material passes the frozen eligibility screen when this measured response is below the requested tolerance. This is a finite-panel definition, not an upper bound on every admissible perturbation. The original implementation and calibration remain in Supplementary Table S2 and Supplementary Fig. S2.

Across the 319-system development and external descriptive stability universe, the frozen gate rejects 79.9%, 41.4% and 9.7% at $10^{-4}$, $10^{-3}$ and $10^{-2}\,e$. These are screen-rejection fractions, not codec failure rates or universal material properties. The corresponding development-only fractions are 81.9%, 43.7% and 9.8% (Supplementary Table S3; research audit).

Figure 3 and Supplementary Table S4/Fig. S7 retain the historical full-record analysis: 762 material-codec decisions at each threshold, with 518/533 (97.2%), 296/310 (95.5%) and 61/108 (56.5%) numerical no-pass outcomes on non-evaluable targets. At $10^{-4}\,e$, 106/229 numerical passes also fail the reference screen. The numerical agreement of those passes remains a valid fixed-pipeline observation; they do not establish reference robustness.

The full record, however, combines the base ladder with an additional tight ladder available only for 143 materials admitted at $10^{-3}\,e$. We therefore repeated the analysis using the base ladder alone, and then using only within-material base rungs observed for all three codecs. Both controls give the same pooled counts: 616/740 (83.2%), 296/524 (56.5%) and 61/119 (51.3%) numerical no-pass outcomes on QSQ-non-evaluable materials. All 762 material-codec decisions have at least one valid observation in each analysis. This is observed-support sensitivity, not proof that all missing-rung mechanisms have been eliminated.

The tight extension creates 214 additional numerical passes at $10^{-3}\,e$, all in the eligible group. The original >95% result is therefore ladder-design-sensitive and cannot be interpreted as a design-independent causal misattribution rate. At $10^{-4}\,e$, the base-only 83.2% fraction must also be read against 81.9% non-evaluable prevalence. The frozen QSQ labels remain unchanged; the audit changes the strength of the inference. Full decisions, per-codec summaries, material-cluster bootstrap intervals and search-opportunity transitions are provided in `analysis/research_upgrade/`.'''
    m = section(m, "### Stability qualification changes the benchmark from binary to three-state\n", "### A valid stability probe must excite the numerical failure mode\n", results)
    m = replace_once(m,
        "The lesson is methodological: a QoI can be declared numerically identifiable only with a qualification probe that is capable of exciting the numerical instability relevant to that operator.",
        "The lesson is methodological: a reference-sensitivity screen should excite relevant perturbation directions, but a finite probe panel cannot by itself certify all such directions.\n\n### Reused-seed holdouts reveal finite-panel fragility\n\nA retrospective four-training-seed/one-held-out-seed audit on the 319-system stability universe yields 18/338 (5.33%), 12/947 (1.27%) and 1/1441 (0.0694%) held-out exceedances among admitted material-splits at 1e-4, 1e-3 and 1e-2 e. Each material contributes five correlated splits; bootstrap resampling uses materials rather than treating splits as independent systems. Since all five seeds were already used in development, these results diagnose four-seed screening fragility and do not estimate the prospective error rate of the deployed five-seed QSQ rule. Fresh-seed confirmation is specified separately and has not yet been executed.")
    m = m.replace("The tight tolerance ladder provides an independent view of the transition", "The eligibility-targeted tight tolerance ladder provides a conditional diagnostic of the transition")
    first = "Scientific-compression benchmarks usually treat the downstream tolerance as given. Our results show that this assumption can fail before the codec is evaluated. At strict Bader contracts, more than 95% of apparent binary failures occur where the reference analysis itself is not independently resolvable at the requested precision. The same qualification also invalidates apparent passes. The central issue is therefore not how to make a codec look more successful, but whether a binary scientific label is defined at all."
    m = replace_once(m, first,
        "Scientific-compression benchmarks should distinguish numerical agreement with a specified reference from robustness of the reference interpretation. Our common-ladder audit shows that the magnitude of label reclassification is sensitive to which codec settings were made available. The original full-record percentages remain reproducible descriptive statistics, but do not by themselves identify causal misattribution or establish the predictive value of a stability gate. Useful qualification must be validated by held-out risk, useful coverage and computational cost, not by a large rejection fraction alone.")
    old_end = "Our framework adds a logically prior step to these lines of work: before a QoI error is bounded, preserved or interpreted against a target tolerance, the target itself must be shown to lie above the numerical resolution of the reference analysis. This separates a **measurement question**—is the QoI identifiable at the requested scale?—from a **compression question**—conditional on that identifiability, does the reconstruction satisfy the contract? Only the second question supports attribution of failure to the codec."
    m = replace_once(m, old_end,
        "QSQ adds an explicit reference-sensitivity assessment to the measurement contract. It separates a reference-robustness question from a fixed-pipeline compression-agreement question. These questions can have different answers, including exact numerical reproduction of a sensitive reference. This distinction must not be interpreted as proof that compression caused none of the observed deviations.")
    m = replace_once(m,
        "The five-seed maximum used here is intentionally conservative and qualification-defined; its purpose is to make the eligibility decision explicit and auditable rather than to estimate an intrinsic material constant independent of algorithm and representation.",
        "The five-seed maximum is conservative relative to using any one of those seeds, but not an upper bound on unseen perturbations. It defines an auditable empirical screen, not an intrinsic material constant or a calibrated probability of safety. The reused-seed audit motivates genuinely independent validation. Moreover, separate reference-response and reconstruction-error tests below the same tolerance do not automatically imply a combined robust error below that tolerance; an explicit target and error budget are needed.")
    m = replace_once(m,
        "Numerical identifiability is therefore not an auxiliary diagnostic of scientific compression; it is a prerequisite for assigning scientific success or failure.",
        "Reference robustness and numerical fidelity should therefore be reported together, with any stronger scientific certificate tied to an independently validated uncertainty model and an explicit error budget.")
    methods = r'''### Common-ladder and retrospective seed-holdout audits

The common-ladder audit reads the frozen master table without changing eligibility, thresholds or reconstruction outputs. We compare the full record, base-only rows, and the subset of base rungs observed for all three codecs within each material. Numerical pass means that at least one available reconstruction has re-derived Bader error below the threshold; no-pass means that no available rung passes, not that the codec could never pass under another setting. Missing material-codec observations are labelled unavailable. The audit validates all stored flags and reproduces the original Figure 3 counts before computing controls.

For seed holdout, each of five seeds is withheld in turn and the remaining four define the retrospective screen. A false-safe split passes the four-seed screen but exceeds the threshold on the held-out seed. We use 2,000 deterministic material-cluster bootstrap replicates for descriptive intervals. These reused-seed diagnostics are not prospective tests, and the external descriptive subset is not substituted for the 63-system confirmatory population. Source hashes and complete tables are in `analysis/research_upgrade/`.

'''
    m = replace_once(m, "### Bader mechanism decomposition\n", methods + "### Bader mechanism decomposition\n")
    m = replace_once(m,
        "If $f_m\\geq\\tau$, the material–threshold pair is assigned `NON_EVALUABLE_BADER_UNSTABLE` and is counted as neither a codec success nor a codec failure at that tolerance.",
        "If $f_m\\geq\\tau$, the material–threshold pair is assigned `NON_EVALUABLE_BADER_UNSTABLE` in the frozen operational QSQ classification. Numerical agreement or disagreement is still retained on a separate axis. The word certified in historical tables denotes this finite-panel operational rule, not a worst-case or calibrated probabilistic guarantee.")
    new["manuscript"] = MARKER + "\n" + m
    r = old["readme"]
    headline = '''## Headline benchmark-validity result

**Research audit correction:** numerical fidelity to a fixed reference and robustness of that reference are distinct targets. A QSQ rejection does not prove that an observed discrepancy was not caused by compression. The historical full-record Figure 3 remains reproducible but is not a design-independent causal attribution result.

| Bader tolerance | Historical full record | Common base ladder | Non-evaluable prevalence |
|---|---:|---:|---:|
| 1e-4 e | 518/533 = 97.2% | 616/740 = 83.2% | 624/762 = 81.9% |
| 1e-3 e | 296/310 = 95.5% | 296/524 = 56.5% | 333/762 = 43.7% |
| 1e-2 e | 61/108 = 56.5% | 61/119 = 51.3% | 75/762 = 9.8% |

The fractions are numerical no-pass outcomes occurring on QSQ-non-evaluable targets. Eligibility-targeted access to the tight ladder changes these fractions substantially. The common observed base-rung sensitivity gives the same pooled counts as base-only analysis. At 1e-3 e, the full record adds 214 numerical passes, all among eligible targets.

The retrospective four-seed/one-seed holdout finds 18/338, 12/947 and 1/1441 exceedances among admitted material-splits. This diagnoses finite-panel fragility, not prospective five-seed reliability. No new probe measurements are asserted.

Executed analysis: `analysis/research_upgrade/REPORT.md`; source `scripts/audit_qsq_research.py`. Current research plan: `paper/RESEARCH_UPGRADE_PLAN.md`; target definitions: `paper/ROBUST_FIDELITY_FOUNDATIONS.md`. Frozen Figure 3 data and assertions remain unchanged and must be labelled full-record results.
'''
    r = section(r, "## Headline benchmark-validity result\n", "## Layout\n", headline)
    r = replace_once(r,
        "2. **Central benchmark-validity result:** the downstream tolerance itself must be independently qualified for numerical identifiability before codec scoring. Figure 3 shows that 97.2% and 95.5% of naive failures at `1e-4 e` and `1e-3 e` are non-evaluable rather than genuine eligible codec failures.",
        "2. **Audited benchmark interpretation:** reference stability and numerical agreement are separate axes. The full-record Figure 3 percentages are sensitive to targeted tight-ladder access; common-base fractions are 83.2% and 56.5%, and must be interpreted with exclusion prevalence. See the research audit rather than quoting >95% as a universal correction.")
    r = replace_once(r,
        "If `eligible(m, tau)` is false, the correct benchmark state is **non-evaluable**, not codec failure. This distinction is essential at strict tolerances, where the Bader analysis itself may not be numerically identifiable at the requested precision.",
        "If `eligible(m, tau)` is false, the frozen QSQ operational state is **non-evaluable**. Fixed-pipeline numerical agreement remains separately measurable; this classification is not a causal attribution test or a worst-case guarantee.")
    new["readme"] = MARKER + "\n" + r
    notice = "\n> **Research interpretation superseded in part (2026-09-11).** The common-ladder and reused-seed audits require a stronger research programme, not just submission assembly. Full-record 97.2%/95.5% are historical ladder-dependent fractions, not causal misattribution estimates. Common-base values are 83.2%/56.5%; numerical agreement remains defined even when the reference fails QSQ. The authoritative next-step plan is `paper/RESEARCH_UPGRADE_PLAN.md`; executed evidence is `analysis/research_upgrade/REPORT.md`. Older quantitative claims below retain their original data scope.\n\n"
    story = old["story"]
    firstline, remainder = story.split("\n", 1)
    new["story"] = MARKER + "\n" + firstline + "\n" + notice + remainder
    matrix = old["matrix"]
    lines = matrix.splitlines()
    for number, replacement in {
        "7": "| 7 | Reference sensitivity and fixed-pipeline numerical agreement are distinct assessment targets | Frozen QSQ screen fractions remain measured; they do not establish that fixed-reference Bader comparisons are undefined. An exact reconstruction can reproduce a sensitive reference. | `paper/ROBUST_FIDELITY_FOUNDATIONS.md`; `stability/eligibility_by_threshold_A1.csv` | F3/F4 with revised scope | **CONFIRMED** for the stated distinction | Finite-seed acceptance is not a universal stability certificate |",
        "14": "| 14 | Full-record reclassification is strongly ladder-design-dependent | Full-record 97.2%/95.5%/56.5% reproduce, but common-base fractions are 83.2%/56.5%/51.3%; 214 added 1e-3 e passes all belong to the eligible group. Causal misattribution interpretation withdrawn. | `analysis/research_upgrade/ladder_summary.csv`; `analysis/research_upgrade/ladder_transitions.csv` | F3 historical full record | **CONFIRMED** for the audited design dependence | Complete a uniform tight ladder; report rejection prevalence and validate held-out usefulness |",
    }.items():
        targets = [i for i, line in enumerate(lines) if line.startswith(f"| {number} |")]
        if len(targets) != 1:
            raise ValueError(f"Missing or ambiguous claim {number}")
        lines[targets[0]] = replacement
    matrix = "\n".join(lines) + "\n"
    head, rest = matrix.split("\n", 1)
    new["matrix"] = MARKER + "\n" + head + "\n" + notice + rest
    if "more than 95% of apparent binary failures" in new["manuscript"] or "Only the second question supports attribution" in new["manuscript"]:
        raise ValueError("Unqualified causal claim remains")
    receipt = {}
    for key, text in new.items():
        path = ROOT / NAMES[key]
        receipt[NAMES[key]] = dict(before_sha256=hashlib.sha256(old[key].encode()).hexdigest(), after_sha256=hashlib.sha256(text.encode()).hexdigest())
        path.write_text(text)
    (ROOT / "analysis/research_upgrade/integration_manifest.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("Integrated executed research audit into four active documents; frozen data and figures unchanged")


if __name__ == "__main__":
    main()
