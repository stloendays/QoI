# Story and figure architecture for a high-impact submission (planning draft)

Date: 2026-10-06. Alternative draft from a second run of the same routine (fired 16:12 UTC), kept beside the draft in `paper/program_draft/` (`500203a`) for comparison; neither overwrites the other. Branch `paper/program-story-draft-20261007` (from `origin/research/general-qoac-law-confirm-20261006` @
`62e62ce`). Companion ledger: `paper/program_draft/alt_run_1612/CLAIM_EVIDENCE_MAP.md` (row ids A*, S*, R*, F*, O* below refer to it).
Target venues: Nature Computational Science or Nature Communications.

This document plans a manuscript. It does not change the frozen manuscript (`paper/MANUSCRIPT.md` on
`paper/qoac-integration-20261005` @ `10d3d37`). Every number below is copied from the file cited in the evidence map. Risks
and boundaries belong to the evidence map. The proposed manuscript text below carries only the claims and the scope they
are stated for.

## 1. Proposed title and abstract

**Title (proposal):** *Qualified measurement operators predict and shape the certified compression of electronic densities*

Alternative: *The downstream measurement operator qualifies, predicts and designs scientific data compression*

**Abstract (149 words):**

> Scientific-compression benchmarks score reconstructions against downstream quantities of interest (QoIs) and assume
> that the reference analysis resolves the requested tolerance. QoI Stability Qualification (QSQ) qualifies the complete
> measurement contract before any codec is scored. Across 254 electronic densities, a five-probe QSQ screen separated
> prospective Bader threshold-exceedance risks of 1.600% in qualified and 81.325% in rejected materials at 10^-3 e. Once
> the contract is qualified, the downstream operator sets where compression error belongs. For six reciprocal-space
> operators, gains predicted from the operator symbol and reference spectrum, committed before any compression, matched
> measurements on 60 never-used materials (median absolute log error 0.024, Spearman 0.978), spanning 1.011-fold for the
> density gradient to 12.1-fold for Gaussian smoothing. For the Hartree potential, the closed-form operator law came within
> 1.105-fold of the operational rate-distortion optimum and certified 10.2-fold more compression than pointwise codecs
> under equal search. Every decoded field is recertified under its original contract.

Sources, in order: A6 (`p2_fresh_probe_cohort_summary.csv`, frozen-paper); A5, A1, A3
(`analysis/general_qoac_law/results/run_P1_CONFIRMATORY/SUMMARY.json` @ `f10490f`). The abstract uses only
prospective-confirmed rows. The wording "committed before any compression" is a timing statement licensed by
`d5fc30b` → CI run 37488577302. It is not a priority claim. If P3b (O1) passes, the phrase "on 60 never-used materials"
becomes "on 60 never-used bulk materials and 32 never-used surface slabs from a second database".

**Thesis sentence (for the Introduction's last paragraph):** The operator that defines a scientific measurement decides
whether a tolerance can be scored (qualification), which reconstruction errors matter (diagnosis), how much an
operator-aware codec will gain before it is run (prediction), and where error should be placed (design); certification
closes the loop on the decoded field.

## 2. Main-text section order

1. **Introduction.** Downstream fidelity is established as a requirement (credit Jiao, MGARD-QoI, QPET, TOPIQ, Compression
   Safeguards, FFCz). The open question is two-sided: when is a tolerance a valid ruler, and can the operator behind the
   ruler tell us where compression error may go and how much that is worth before compressing? Measurement-science
   analogy (limit of quantification, gauge R&R). Contributions listed without "first" or "novel".
2. **Results 1: Qualification decides whether a tolerance can be scored.** QSQ definition on the complete contract; P2
   prospective risk separation (A6); partition-field control of Bader instability (A10).
3. **Results 2: The operator explains codec-dependent error.** Matched-distortion Fourier mechanism for the Hartree control
   (S1), stated as a mechanism for one operator and one codec pair.
4. **Results 3: A closed-form operator law and its distance from the optimum.** Operator-weighted distortion → Delta_G ∝
   w^(-1/2) (credited as classical high-rate allocation) → P1 Part A: near-optimality at tau = 1e-6 (A1), operator metric
   vs blind metric under identical optimization (A2), equal-search comparison with pointwise codecs and truncation across
   three tolerances, including the 1e-4 truncation result (A3, A4).
5. **Results 4: The gain is predictable before compression.** Six operators, predictions committed before the run (A5).
   Null-gain operators (gradient, Laplacian), moderate (Hartree field), large (Hartree potential, Gaussian smoothing).
   P3b slab panel if O1 passes.
6. **Results 5: Certified compression against the strongest baselines.** Disjoint 48-material confirmation and
   254-material census (A7), decomposition into eigenbasis gain vs allocation gain (A8). Equal-search numbers (A3) lead;
   ladder-searched numbers (A7) are labelled as such.
7. **Results 6: Non-spectral QoIs enter through constraint projection.** Exact-partition Bader charges by minimum-norm
   basin-sum projection, certified with the production Bader code (A9). Joint Hartree + Bader certification only if O2
   produces a confirmed result.
8. **Discussion.** What each stage licenses; the operator as the organizing object; where the closed-form law is and is not
   near-optimal (tolerance dependence); operator classes for which operator-aware allocation buys nothing (derivative
   operators, A5) as a practical result.
9. **Methods.** QSQ protocol; operator library and symbols; policy codec and certificate (historical and Nyquist-safe);
   RDO reference; equal-search rule; gain predictor (finite-rate Laplacian ECSQ, credited); pre-registration and
   population freeze (WS-0 rule, exclusion set, prediction-commit order); B2 projection; statistics (fixed-seed bootstrap).

## 3. Main figures (at most six)

| Fig. | Single message | Panels | Exact data file(s) |
|---|---|---|---|
| 1 | A scientific tolerance can be scored only after the measurement contract resolves it, and QSQ's verdict predicts fresh risk. | (a) Workflow: qualify → diagnose → predict/design → certify, three outcome labels (schematic). (b) Fresh exceedance risk, eligible vs rejected, at 1e-4 / 1e-3 / 1e-2 e. (c) Per-material floor vs fresh risk. (d) All-electron-reference contract decomposition (50/50 vs 3/50 vs 3/50). | (b) frozen-paper `analysis/research_upgrade/p2_fresh_probe_cohort_summary.csv`; (c) frozen-paper `analysis/extensions_20260928/WP-A/material_risk.csv`; (d) frozen-paper `analysis/extensions_20260930/WP-G/summary.csv` and `reference.csv` |
| 2 | Matched pointwise distortion is not matched operator fidelity: the operator's spectral weighting explains the codec effect. | (a) Radial error spectra, ZFP vs SZ3 at matched realized Linf. (b) Decomposition into total spectral energy (0.376) and Hartree susceptibility (0.203). (c) Material-level share of the effect from frequency structure (median 62.0%). | `analysis/hartree_spectral_mechanism/results/radial_spectrum_summary.csv`, `matched_pair_mechanism.csv`, `mechanism_ratio_summary.csv` (law-confirm; identical on frozen-paper) |
| 3 | The closed-form operator law is within 1.105-fold of the operational optimum at tau = 1e-6, and the operator metric, not the optimizer, carries the gain. | (a) Per-material CR of A1 (law), A3 (optimum), A5 (blind metric), A2 (truncation), A6 (pointwise) at tau = 1e-6. (b) Medians and CIs of A3/A1, A3/A5, A1/A6, A1/A2 across tau = 1e-4, 1e-6, 1e-8, with the 1e-4 truncation result shown. (c) P3b slab panel (if O1 passes). | `analysis/general_qoac_law/results/run_P1_CONFIRMATORY/part_a_material.csv`, `SUMMARY.json` (`part_A`); P3b: the corresponding `run_P3B_*` directory once committed |
| 4 | The compression gain of operator-aware allocation is predicted before compression, across operators spanning no gain to twelvefold. | (a) G_pred vs G_obs, 300 pairs, coloured by operator, identity line. (b) Per-operator medians (predicted vs observed) with the null-gain band [0.90, 1.11]. (c) Same at tau = 1e-4. | `analysis/general_qoac_law/results/run_P1_CONFIRMATORY/part_b_material.csv` (columns `G_obs`, `G_pred`); predictions as committed in `analysis/general_qoac_law/results/predictions/` (`d5fc30b`) |
| 5 | Operator-aware coding certifies an order of magnitude more compression than pointwise codecs on unseen and full populations; most comes from the operator eigenbasis and a further factor from the allocation. | (a) Disjoint 48: QOAC-H vs best ZFP/SZ3/SPERR (15.016x, ladder search). (b) Census: ratio distribution across six Hartree tolerances (254 materials). (c) Strongest baselines: QOAC-H vs T1, MGARD, stored V_H (1.564x over T1). | `analysis/operator_aware_codec_hartree_v02_confirmatory/results/confirmatory_material.csv`; `analysis/operator_aware_codec_hartree_v02_census/results/census_material_tau.csv`; `analysis/qoac_h_strong_baselines/results/baseline_material.csv` |
| 6 | A non-spectral, partition-defined QoI is certified exactly by generic compression plus minimum-norm basin-sum projection. | (a) Schematic of the projection and the auxiliary density budget kappa. (b) CR ratio per material, 38 holdout (median 1.8646, 34/38). (c) Bader error and reassignment after projection (0 e, 0 in 38/38). | `analysis/operator_aware_bader_projection_confirmatory/results/confirmatory_material.csv`, `SUMMARY.json` |

If the authors want five figures, Fig. 2 can merge into Fig. 1 as a mechanism panel, or Fig. 5 can move to Extended Data
because the frozen manuscript already carries it (decision D1).

## 4. Supplementary Information

- QSQ supporting validations: equal-search control, implementation transfer (S3), grid-local extrema (S4), finite-panel
  admission bound and certifying writer (S6), external cohort (S5), probe-family robustness, P4 chemical-direction case.
- QOAC-H mechanism test (S2, 0.0767117), sanity audit, Nyquist-safe certificate definition.
- P1 shakedown cohort (12 materials; A3/A1 = 1.156) and full per-tolerance Part A and Part B tables.
- Predictor development: retrospective calibration (R3), high-rate vs finite-rate predictor comparison, model absolute
  rate accuracy.
- Finite-rate diagnosis: dead-zone fractions and marginal slopes (R2).
- RDO reference construction (v0.3 codec as the A3 arm), with the prior-shape ablation A3/A4 = 0.999 at 1e-6
  (`qoac_v03_rdo` engineering, development data).
- B2 engineering and kappa sweep (`analysis/operator_aware_bader_projection/results/RESULTS.md`).
- Joint Hartree + Bader certification (S7, S8), only once O2 resolves.
- Population construction: WS-0 selection rule, exclusion set, P3b rule, provenance hashes
  (`analysis/fresh_population_20261006/REPORT.md`, `P3B_SELECTION_RULE.md`).
- Pre-registration register: every frozen protocol with its freeze commit and outcome, including the gates in
  `CLAIM_EVIDENCE_MAP.md` section D, as a neutral table of protocols and outcomes. Whether this register is in the SI or
  only in the repository is decision D6.

Not in the manuscript or SI text: electric-field gates (F1, F2), v0.3 G2 (F3), HB-joint confirmatory median (F4), B1
residual transform (F5). They remain in the repository and in the evidence ledger as provenance.

## 5. Open items that must be finished before submission

1. **P3b slab cohort (O1, running).** 32 fresh NOMAD VASP slabs; predictions committed `c1e6564`; run launched `62e62ce`.
   Needed for any surface or second-database wording and for Fig. 3c. If it fails a criterion, the paper states the law
   for bulk materials from one database, and the failure is recorded in the ledger.
2. **Joint Hartree + Bader v2 (O2).** Code at `origin/research/qoac-hb-v2-20261006` @ `af25f77`. Requires: a frozen protocol
   (Hartree-aware projection and/or certify-then-project, applied identically to every arm), engineering on P2 engineering
   (12), and confirmation on P2 confirmatory (48). Until a pass, the "one stream, several QoIs" result stays out of the
   main text.
3. **B3 real-material Gate 0 (O3).** Triggered at `94d06cf`. Gate 0 (emulator = binary voxel for voxel on 12/12, R1 and R2
   regular) must pass before any B3 gate is evaluated. B3 is not needed for the proposed main text. It decides whether
   the Bader line can claim compression of the partition field (currently stored exact).
4. **Full-text verification of citations (O4).** The following are UNVERIFIED in the prior-art audits and must be checked
   against the publisher page or full text before use:
   - Sullivan & Wiegand 1998 (DOI); Gersho & Gray 1992 (section for Delta ∝ w^(-1/2)); Witsenhausen 1980 (DOI); Cover &
     Thomas (edition, DOI); Shlezinger et al. 2019 (DOI); MGARD multivariate-case paper (DOI); Wu et al. SC24 (proceedings
     DOI; whether its selection is Lagrangian);
   - Huang & Schultheiss 1963 (DOI); Wei, Shaw & Varley ICASSP 1997 (title, pages, weighted AM/GM form); Mallat & Falzon
     1998 (pages, DOI); Sullivan 1996 (DOI); He & Mitra 2002 (DOI); Underwood et al. 2023 (DOI); the NJIT
     compression-ratio-modelling paper (authors, venue);
   - Lee et al. 2022 (exact norm and weighting of the constraint step); Banerjee et al. (journal version); Gong et al. 2022
     (DOI); Jiao 2022 and QPET 2025 (multi-QoI single bound); Dunlap et al. 1979 and Vahtras et al. 1993 (DOIs; charge
     constraint); moment-conserving omnitrees arXiv:2607.04881 (authors); Tang et al. 2009 (full citation);
   - BlockMGARD arXiv:2609.00205 (full text, beyond the verified abstract); Compression Safeguards (full text: do its QoI
     safeguards cover exact region sums?);
   - every B3 entry (MSz, pMSz, discrete MS complex, EXaCTz, TopoSZ, Soler et al., Gorski et al., Liang et al. ×2, Xia et
     al. ×2, Henkelman 2006, Tang 2009, Yu & Trinkle 2011).
   - In addition, re-run the targeted search for (i) MGARD follow-ups with negative-Sobolev allocation after 2023 and
     (ii) lossy compression of plane-wave DFT densities in 2025–2026 materials-database work (PA-P residual risks), now
     including "compression gain prediction" + "operator".
5. **Prior-art audit update.** PA-P C1 and C2 predate the P1 confirmation (`ebfe465` vs `f10490f`). Their "development
   only / not prospective / finite-rate model untested" constraints must be rewritten for P1 before rows A1–A5 enter a
   manuscript. The credit lists stay.
6. **Within-operator rank agreement for Part B.** The committed summary has only the pooled Spearman (0.978). A
   per-operator rank statistic is a computation on committed files (`part_b_material.csv`), not a new experiment, but it is
   not yet done.

## 6. Decisions the authors must make

- **D1. Reopen the frozen manuscript, or write a second paper?**
  - Option (a), reopen `paper/qoac-integration-20261005`. The P1 law and prediction results (A1–A5) would replace or extend
    Fig. 8. This needs the full scope-reopening procedure (prior-art audit, claim–evidence map, figure architecture, story
    review, submission QA), and it delays a manuscript that has passed final audit with 0 blockers.
  - Option (b), submit the frozen QSQ + QOAC-H paper as it stands, and write a second, operator-centred paper (this draft)
    that cites it for QSQ and QOAC-H. Then A6, A7 and A10 are cited results, not new ones, and the second paper's headline
    is A1–A5 (+ O1), with A9 as the non-spectral case. This keeps the two papers' numbers apart (15.0x ladder vs 10.2x equal
    search).
  - Option (c), hold the frozen manuscript and submit one combined paper after O1 and O2. Strongest single story;
    largest delay and overlap risk.
- **D2. Lead claim.** The task brief leads with QSQ plus the operator law. If D1 = (b), QSQ should shrink to one paragraph
  of motivation, and the lead becomes "the gain is predictable before compression" (A5).
- **D3. Which headline compression number:** equal-search 10.2x on P1 (A3) or ladder-searched 15.016x on the disjoint 48
  (A7). Recommendation: 10.2x in the abstract, 15.016x only with its search label.
- **D4. Scope of "operator".** Six diagonal reciprocal-space operators plus one partition-integral QoI. Decide whether the
  title says "operators" in general or "linear reciprocal-space operators".
- **D5. Bader role.** Main-text Fig. 6 (A9) or SI. A9 is confirmatory but methodologically incremental (PA-P C3).
- **D6. Pre-registration register.** Publish the full protocol-and-outcome register (including F1–F5) in the SI, or only in
  the repository with a pointer from Methods.
- **D7. Venue.** Nature Computational Science (method + principle) vs Nature Communications (broader). The equal-search
  and pre-registration design suits either; the operator-prediction result is the stronger fit for Nat. Comput. Sci.
- **D8. Wait for P3b?** Recommended: yes. One more database and one more structural class are the cheapest increase in
  generality available, and the run is already launched.
- **D9. Whether to run the HB v2 confirmation before submission** or to drop the joint-certification line from this paper.
