# Story and figure architecture for a program-level submission (draft, 2026-10-07)

Target: Nature Computational Science / Nature Communications. Planning document on branch
`paper/program-story-draft-20261007` (from `research/general-qoac-law-confirm-20261006` at `ce2973a`).
Nothing here changes the frozen manuscript `origin/paper/qoac-integration-20261005:paper/MANUSCRIPT.md`.

Every number below is copied from a committed file. The claim IDs (A1, B4, C1, …) point to
`paper/program_draft/CLAIM_EVIDENCE_MAP.md`, which gives the source path, commit, prior-art boundary and
reviewer risk for each. Risks and failures live in that map, not in the manuscript text proposed here.

## 1. Proposed title and abstract

### Title

**Downstream operators qualify, shape and predict the compression of electronic densities**

Alternatives:
- *Qualified measurement contracts and operator-derived compression laws for electronic densities*
- *Scientific compression should be qualified, designed and certified by the downstream operator*

### Abstract (149 words)

> Lossy compression of scientific fields is judged by quantities of interest (QoIs) computed from the
> reconstruction, yet the reference analysis may itself be unable to resolve the requested tolerance. We
> introduce QoI Stability Qualification (QSQ), which qualifies the complete measurement contract before any
> codec is scored. Across 254 electronic densities, a five-probe screen separated prospective Bader
> threshold-exceedance risks of 1.600% in qualified and 81.325% in rejected materials. For linear downstream
> operators, the operator's reciprocal-space symbol then fixes where compression error should go. In a
> pre-registered test on 60 previously unused materials, this closed-form law certified the Hartree potential
> (relative error 10⁻⁶) at a median 10.2-fold higher compression ratio than equal-search ZFP, SZ3 and SPERR
> and 1.32-fold higher than spectral truncation, within a factor 1.105 of the operational optimum. Gains
> predicted before compression for five operators matched the measured gains (Spearman 0.978). Each decoded
> field is recertified under its contract.

Number sources:
- 254, 1.600%, 81.325%: A1 (`paper/MANUSCRIPT.md` line 55, paper branch `efd1e2c`).
- 60, 10.2, 1.32, 1.105: B4 (`analysis/general_qoac_law/results/RESULTS.md`, `f10490f`;
  `results/run_P1_CONFIRMATORY/SUMMARY.json`, `4164519`).
- "five operators", 0.978: C1 (same files; 5 non-control operators, 300 pairs, τ = 1e-6).

Word choice follows the prior-art audits: no "first" or "novel"; "pre-registered" and "predicted before
compression" are timing statements backed by `fe2e08a` (protocol) and `d5fc30b` (predictions). Audit-P C2
asked that "a priori" not be used as a timing claim; the abstract avoids that phrase.

**If P3b passes (O1),** replace "60 previously unused materials" with "92 previously unused bulk materials
and surfaces from two databases" only after the P3b SUMMARY is committed, and re-copy every number. If it
fails, keep the bulk wording (see decision Q3).

### One-sentence thesis

The downstream operator decides whether a scientific tolerance can be resolved (qualification), where
compression error may be placed (design) and how much is gained (prediction); the decoded field is then
certified under the same contract.

## 2. Main-text section order

1. **Introduction.** Compression is scored against downstream analyses; the logically prior question is
   whether the analysis resolves the tolerance. Position against QoI-preserving compression (MGARD-QoI,
   Jiao et al., QPET, Lee et al., TOPIQ, Compression Safeguards, FFCz) and measurement science
   (limit of quantification, gauge capability). Close with the three roles of the operator.
2. **Results 1 — The same reconstruction is faithful for one operator and not another** (A11). Short;
   motivation only.
3. **Results 2 — QSQ prospectively separates resolvable from unresolvable contracts** (A1, A2, A3).
4. **Results 3 — Evaluability belongs to the contract and the QoI** (A4, A5, A7 eligibility counts).
5. **Results 4 — The Hartree symbol explains the codec effect and defines a closed-form allocation law**
   (B1, B2). Credit the classical high-rate weighted-MSE law; the contribution is the physical weight and
   the qualify–design–certify loop.
6. **Results 5 — The law is confirmed prospectively on never-used materials** (B4, B5): near-optimality
   (A-H1), metric not optimizer (A-H2), equal-search advantage over pointwise codecs (A-H3) and over
   truncation (A-H4), tolerance dependence.
7. **Results 6 — The gain is predictable before compression across operators** (C1, C2).
8. **Results 7 — Development-scale breadth and strongest baselines** (B6, B7, B8). Could merge into
   Results 5 as one paragraph with Fig. 5.
9. **Results 8 — Non-spectral contracts: exact-partition Bader charges** (D1; D2 only after decision Q5).
   One paragraph; figure in SI unless decision Q5 decides otherwise.
10. **Discussion.** What each outcome licenses (contract change, coarser decision, tolerance matching, codec
    design); the operator as the unit of design; how per-operator gain prediction lets a user decide whether
    operator-aware coding is worth deploying before compressing anything; the scope stated as definitions
    (bulk/surface, operators tested, Bader contract), not as hedges.
11. **Methods.** Contract definition and QSQ; perturbation model; admission bound; Bader settings;
    Hermitian-orbit Fourier representation and Nyquist-safe certificate; policy codec and arms A0–A6;
    operational optimum (v0.3 Lagrangian, used as reference A3); gain predictor (finite-rate Laplacian
    ECSQ); fresh-population selection rule and exclusion; pre-registration chronology (commit hashes);
    statistics (bootstrap seeds, criteria).

## 3. Figure architecture (6 main figures)

Data paths are relative to the repository root. "paper branch" = `origin/paper/qoac-integration-20261005`;
otherwise the file is on this branch.

| fig | single message | panels | exact data files |
|---|---|---|---|
| **1** | The downstream operator enters three times: it qualifies the ruler, shapes the codec, and defines the certificate. | (a) schematic contract → QSQ → operator-derived design → decode → certify, with outcomes certified / not certified / non-evaluable; (b) same reconstructions, three operators (electron count vs Bader vs Hartree). | (a) schematic, no data; (b) `analysis/electron_count_qoi/electron_bader_decoupling.csv` and `benchmark/master_benchmark_full.csv` (paper branch; inputs of `figures/R/figure2_qoi_hierarchy.R`) |
| **2** | A five-probe QSQ screen prospectively separates fresh Bader exceedance risk: 1.600% vs 81.325% at 1e-3 e. | (a) per-material floor vs fresh risk; (b) admission bound 6.70% with every material; (c) equal-search control (3.3% vs 66.4%); (d) three thresholds. | `analysis/research_upgrade/p2_fresh_probe_cohort_summary.csv`, `analysis/research_upgrade/p1_common_tight_summary.csv` (paper branch; inputs of `figures/R/figure3_certification_landscape.R`) |
| **3** | Evaluability is a property of the contract and the QoI, not of the material. | (a) all-electron-reference decomposition 50/50 vs 3/50 vs 3/50; (b) Bader vs grid-extrema eligibility (κ = 0.1337); (c) external 63-system eligibility 16 / 42 / 57 and the contract-dependent codec ranking. | (a) `analysis/extensions_20261001/WP-I/summary.csv`; (b) `analysis/extensions_20260928/WP-B/summary.csv`; (c) `validation/final_external_confirmatory63_20260908/confirmatory63/external_summary_a1.csv`, `best_certified_external.csv` (all paper branch) |
| **4** | The Hartree symbol explains the measured codec effect and yields a closed-form allocation that sits near the operational optimum. | (a) matched-pair spectral decomposition (457 pairs; susceptibility factor 0.202683); (b) operator symbol \|G\|^-4 → Δ_G ∝ \|G\|^2 schematic; (c) P1 per-material CR_A3/CR_A1 at three tolerances (1.58 / 1.105 / 1.03); (d) CR_A3/CR_A5 operator vs blind metric (1.33 / 2.12 / 1.60). | (a) `analysis/hartree_spectral_mechanism/results/matched_pair_mechanism.csv`; (c, d) `analysis/general_qoac_law/results/run_P1_CONFIRMATORY/part_a_material.csv` (columns A1, A3, A5 by `tau`) |
| **5** | Pre-registered on 60 never-used materials, the law beats equal-search pointwise codecs (10.2×) and spectral truncation (1.32×) at 1e-6; development-scale cohorts agree. | (a) P1 CR_A1 vs CR_A6 and vs CR_A2 per material, three tolerances; (b) disjoint 48-material QOAC-H confirmation (15.016×); (c) 254-material census across six tolerances; (d) strongest baselines (T1 233, MGARD 16.0, QOAC-H 383 median CR). | (a) `analysis/general_qoac_law/results/run_P1_CONFIRMATORY/part_a_material.csv` (A1, A2, A6); (b) `analysis/operator_aware_codec_hartree_v02_confirmatory/results/confirmatory_material.csv`; (c) `analysis/operator_aware_codec_hartree_v02_census/results/census_tau_summary.csv`; (d) `analysis/qoac_h_strong_baselines/results/baseline_material.csv` |
| **6** | The gain from operator-aware allocation is predicted before compression from the operator symbol and the reference spectrum. | (a) G_pred vs G_obs, 300 pairs, coloured by operator, τ = 1e-6, identity line; (b) the same at τ = 1e-4; (c) per-operator medians ordered by predicted gain (gradient 1.011 → Gaussian 12.1). | `analysis/general_qoac_law/results/run_P1_CONFIRMATORY/part_b_material.csv` (columns `operator`, `tau`, `G_obs`, `G_pred`); frozen predictions `analysis/general_qoac_law/results/predictions/` (`d5fc30b`) for the timestamp annotation |

Notes:
- Fig. 6 panel (a) must show the Gaussian operator at its true position (G_pred 17.6 vs G_obs 12.1); the
  figure states the measurement, and the evidence map carries the risk discussion.
- If P3b passes, Fig. 5a and Fig. 6a gain a second marker set for slabs, from the P3b SUMMARY and its
  `part_a_material.csv` / `part_b_material.csv` (paths to be created by the P3b run).
- Fig. 4b is the only schematic panel outside Fig. 1.

## 4. What moves to the Supplementary Information

From the frozen manuscript (paper branch figures 4–9 and SI notes):
- order-preserving control vs QSQ perturbation (old Fig. 4);
- Bader basin-migration mechanism, panels a–e (old Fig. 5), with panel f data in main Fig. 3a;
- nominal vs matched realized L∞ confounding (old Fig. 6);
- full Fourier audit (old Fig. 7) beyond Fig. 4a;
- P3A implementation transfer (A6), P4 chemical-decision null (A9), analysis-limited regime (A10),
  probe-family robustness, continuous risk calibration and reference-density predictors (Discussion-only in
  the frozen story);
- certifying writer (A8) and its Supplementary Fig. S10;
- full external-cohort tables (A7).

From the program:
- the 12-material QOAC-H mechanism pilot (B2) and the v0.3 Lagrangian engineering run as the definition of
  the operational optimum (B3);
- P1 shakedown cohort (12 materials), reported separately per protocol;
- per-operator Part B tables at τ = 1e-4 and 1e-6;
- predictor calibration on the 12 engineering materials (C3), labelled as calibration before the frozen test;
- strongest-baseline per-arm tables (MGARD, stored V_H);
- fresh-population construction (E1): selection rule, exclusion set, provenance hashes;
- exact-partition Bader projection (D1), with the κ frontier, unless decision Q5 moves it to main text;
- pre-registration chronology table: protocol, prediction and result commits for every confirmatory test.

## 5. Open items that must be finished before submission

| item | state at `ce2973a` | what "finished" means | blocks |
|---|---|---|---|
| **O1 — P3b slab cohort** | 32 fresh NOMAD slabs drawn (`analysis/fresh_population_20261006/P3B_CONFIRMATORY_MANIFEST.csv`, `d1c1050`); amendment 1 frozen (`39ba728`); `analysis/general_qoac_law/P3B_PHASE = predict` (`ce2973a`). No predictions or results committed here. | Predictions committed before the run; run complete; SUMMARY with the unchanged criteria (validity ≥ 30/32). | Abstract scope; Fig. 5, Fig. 6; title wording "electronic densities" vs "bulk" |
| **O2 — joint Hartree + Bader v2** | Hartree-aware projection and certify-then-project implemented on `origin/research/qoac-hb-v2-20261006` (head `af25f77`); no frozen protocol result. Intended population: fresh P2 (12 + 48, `analysis/fresh_population_20261006/P2_*_MANIFEST.csv`). | Protocol and gates frozen before execution; engineering → confirmatory on P2; same projection for every arm. | Whether D2 enters main text (decision Q5) |
| **O3 — B3 real-material Gate 0** | Design + synthetic prototype only (`origin/research/qoac-b3-design-20261006:analysis/qoac_b3_design/DESIGN_STUDY.md`, `42937da`); Gate 0 run triggered in `94d06cf`; no `results/real_engineering/` committed. | Gate 0 (emulator equals compiled Bader 1.05 voxel for voxel on 12/12 P2 engineering materials) reported. A Gate 0 failure stops B3 (design study §7). | Whether the Bader paragraph can mention partition-field compression at all; otherwise D1 keeps "exact reference partition" |
| **O4 — full-text citation check** | All UNVERIFIED tags below stand (audit-P §0; verification addendum checked only FFCz, BlockMGARD abstract, Compression Safeguards DOI). | Each entry opened and checked against the publisher page; content claims confirmed. | Introduction, Methods, positioning |
| **O5 — prior-art audit update** | Audit-P (C1, C2) predates P1. It made confirmatory wording conditional on a frozen fresh run, and "finite-rate" / "before compression" wording conditional on a frozen, tested model; both conditions are now met. | Audit-P addendum that re-states the permitted wording for B4 and C1, plus a targeted search for prospective gain prediction in scientific compression. | Abstract verbs |

UNVERIFIED citations to check in full text (from audit-P and the B3 design study):
- Sullivan & Wiegand 1998 DOI; Gersho & Gray 1992 exact chapter for Δ ∝ w^(-1/2); MGARD multivariate
  companion paper DOI; Wu et al. SC24 proceedings DOI and whether its selection is Lagrangian; Witsenhausen
  1980 DOI; Cover & Thomas edition; Shlezinger et al. 2019 DOI.
- Huang & Schultheiss 1963 DOI; Wei, Shaw & Varley ICASSP 1997 title/pages and which paper carries the
  weighted AM/GM form; Mallat & Falzon 1998 pages and DOI; Sullivan 1996 DOI; He & Mitra 2002 DOI;
  Underwood et al. 2023 DOI; the NJIT compression-ratio-modelling paper (authors, venue).
- Lee et al. 2022: norm and weighting of the constraint step (content claim); Banerjee et al. journal
  version; Dunlap, Connolly & Sabin 1979 DOI and the charge constraint; Vahtras et al. 1993 DOI; omnitrees
  arXiv:2607.04881 authors; Tang, Sanville & Henkelman 2009 full citation; Gong et al. 2022 (SMC) DOI;
  whether Jiao et al. / QPET derive one bound for several QoIs.
- Full texts still to read: BlockMGARD (arXiv:2609.00205), Compression Safeguards (QoI-safeguard semantics
  for region sums).
- B3 prior art, all UNVERIFIED in the design study: MSz (TVCG 2025), pMSz (arXiv:2601.01787), discrete MS
  complex preservation (arXiv:2409.17346), EXaCTz (arXiv:2604.01397), TopoSZ (TVCG 2024), and the rest of
  its §1 table.

## 6. Decisions the authors must make

| id | decision | options and consequences |
|---|---|---|
| **Q1** | **Reopen the frozen manuscript, or write a second paper?** | (a) *Reopen* `paper/qoac-integration-20261005`: the confirmed law (B4) and gain prediction (C1) replace the development-only QOAC-H headline; the nine-figure architecture shrinks to six; requires the scope-reopening steps in `sync/RESEARCH_PROGRAM_20261006.md` (prior-art audit, claim–evidence map, figure architecture, story review, submission QA) and discards the completed submission QA. (b) *Submit the frozen manuscript as is* and write a second paper on the operator law and gain prediction: the second paper needs QSQ only as a cited precondition, but QOAC-H (B6–B8) is already published in paper 1, so paper 2's results are B4, B5, C1, C2 and P3b; reviewers may see the split as incremental. (c) *Frozen manuscript to a specialist venue, program paper to the high-impact venue*: same split, different targets. This document is written for (a) and maps onto (b) by dropping §2 items 2–4 to a summary paragraph. |
| Q2 | Target journal | Nature Computational Science vs Nature Communications; check current display-item and word limits before fixing six figures. |
| Q3 | How to report P3b whatever its outcome | Pre-commit now: if P3b passes, scope becomes bulk + surfaces from two databases; if it fails a criterion, the abstract states bulk scope and the P3b result is reported with its numbers in SI. Deciding after seeing the result would weaken the pre-registration claim. |
| Q4 | Gaussian-operator miss in Part B | Pooled criteria passed; per-operator log error 0.431. Decide whether Fig. 6 annotates per-operator calibration or only the pooled statistics. |
| Q5 | Place of the Bader design pattern (D1, D2) | Main-text paragraph + SI figure (recommended in this draft), or main figure (requires dropping a panel set elsewhere to stay at six), or omit until O2/O3 finish. The joint-advantage claim is unavailable (F4). |
| Q6 | Whether any NO-GO/FAIL (F1–F8) is reported in SI | This map keeps them as provenance. The journal's reporting standards and the authors' pre-registration framing may favour an SI ledger; the manuscript text proposed here does not cite them. |
| Q7 | MGARD with s < -1 | Run more negative s under a frozen protocol, or state the tested range in Methods (B8 risk). |
| Q8 | Name of the method | Keep QOAC-H / "QoI- and operator-aware compression", or present the method as "operator-law allocation" with QOAC-H as its frozen-ladder implementation. Must be consistent with `paper/NAMING_AND_TERMINOLOGY_POLICY.md` on the paper branch. |
| Q9 | Which implementation is the headline codec | A0 (frozen-ladder QOAC-H, B6–B7) or A1 (law with continuous search, B4). B4 confirms A1; mixing them in one sentence would conflate two arms. |
| Q10 | Archival and data release | Fresh MP/NOMAD populations, predictions and SUMMARY files need an archival DOI alongside the existing one; confirm source-database licence terms for redistribution of derived files. |
| Q11 | AI-assistance disclosure | Much of the analysis code and these planning documents were produced with an AI coding assistant; check the target journal's disclosure policy. |
