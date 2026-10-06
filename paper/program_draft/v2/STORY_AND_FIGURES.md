# Story and figure architecture, consolidated v2 (program-level submission; planning document, 2026-10-07)

Branch `research/program-integration-20261007` (head before this commit: `eb388c2`). This version replaces the two
earlier drafts, `paper/program_draft/STORY_AND_FIGURES.md` (with `CLAIM_EVIDENCE_MAP.md`) and
`paper/program_draft/alt_run_1612/`, which stay in place as history. It adds the results committed since those drafts:
P3b slabs, QOAC-HB v2, B3 real-material engineering, the second prior-art verification batch and the consolidated
status. It does not change the frozen manuscript `paper/MANUSCRIPT.md` (`efd1e2c`).

Rules followed here:
- Every number is copied from a committed file. The path is given beside it or in the claim row of
  `paper/program_draft/v2/CLAIM_EVIDENCE_MAP.md` (claim ids below, e.g. L1, J1, Q1).
- The proposed manuscript text (sections 1–3) contains only claims with status *prospective-confirmed* or
  *confirmatory*. Scope is written as a definition. Failures, NO-GOs, risks and reviewer objections are in the
  evidence map (sections F and G there), not in the proposed text.
- No "first", "novel" or "a priori". "Pre-registered" and "predicted before compression" are timing statements backed
  by commit order (protocol `fe2e08a`, P1 predictions `d5fc30b`, P3b predictions `c1e6564`, HB v2 protocol `8a784a4`).

Short file keys used below:
- `LAW` = `analysis/general_qoac_law/results/RESULTS.md` (`b9fd735`)
- `P1/` = `analysis/general_qoac_law/results/run_P1_CONFIRMATORY/` (`4164519`)
- `P3B/` = `analysis/general_qoac_law/results/run_P3B_CONFIRMATORY/` (`eaa3267`)
- `HBC` = `analysis/qoac_hb_v2/results/P2_CONFIRMATORY_MANIFEST/RESULTS.md` (`e4d9d0b`)
- `HBE` = `analysis/qoac_hb_v2/results/P2_ENGINEERING_MANIFEST/RESULTS.md` (`e095a0c`)
- `B3R` = `analysis/qoac_b3_design/results/real_engineering/RESULTS.md` (`01a3d54`)
- `PAV` = `paper/QOAC_PROGRAM_PRIOR_ART_AUDIT_20261006_VERIFICATION.md` (`ff9283e`)
- `STATUS` = `sync/PROGRAM_STATUS_20261007.md` (`47f3201`)
- `MS` = `paper/MANUSCRIPT.md` (frozen, `efd1e2c`)

## 1. Title and abstract

### Title

**The downstream operator qualifies, predicts and shapes the certified compression of electronic densities**

Alternatives:
- *Operator-derived laws predict and certify the compression of electronic densities*
- *Scientific compression qualified, designed and certified by the downstream operator*

### Abstract (150 words)

> Compressed scientific fields are judged by quantities computed from the reconstruction, yet the reference analysis
> may not resolve the requested tolerance. QoI Stability Qualification (QSQ) qualifies the measurement
> contract before any codec is scored: across 254 electronic densities, a five-probe screen separated fresh Bader
> threshold-exceedance risks of 1.600% (135/8,437 trials) in qualified and 81.325% (5,326/6,549) in rejected
> materials. For linear operators, the operator symbol fixes where compression error belongs and what that
> gains. In pre-registered tests on 60 unused bulk crystals and 32 unused surface slabs, gains predicted before
> compression for five operators matched measurement (Spearman 0.978 and 0.979). For the Hartree potential, the
> closed-form law certified 10.2-fold (60/60) and 18.5-fold (32/32) more compression than equal-search pointwise
> codecs, and for bulk crystals it lies within 10.5% of the operational optimum. On 48 further unused crystals, one
> stream certified Hartree potential and Bader charges together (48/48) at median byte overhead 1.000.

Every number and its source:

| abstract number | claim | status | source |
|---|---|---|---|
| 254; 1.600% (135/8,437); 81.325% (5,326/6,549) | Q1 | prospective-confirmed (fresh perturbations, development materials) | `MS` line 55; `analysis/research_upgrade/p2_fresh_probe_cohort_summary.csv` (`912ad5e`), rows `0.001,True,eligible` and `0.001,True,screen_rejected` |
| 60 bulk, 32 slabs; five operators; Spearman 0.978 and 0.979 | P1, P2 | prospective-confirmed (B-H2 in both cohorts) | `LAW` (P1 verdict table; P3b verdict table); `STATUS` first table |
| 10.2-fold (60/60); 18.5-fold (32/32) | L3 | prospective-confirmed (A-H3 in both cohorts) | `LAW`; `P3B/SUMMARY.json` `part_A.tau_1e-06.A1_over_A6` (wins 32 of n 32) |
| within 10.5% of the operational optimum, bulk | L1 | prospective-confirmed (A-H1, P1 only) | `LAW`: median CR_A3/CR_A1 1.105, CI [1.090, 1.146] |
| 48 crystals; 48/48; overhead 1.000 | J1 | confirmatory (frozen protocol `8a784a4`, fresh P2 population) | `HBC` criteria 1 and 2 |

"Unused" means never used anywhere in the project before the protocol froze (selection rule `10e7863`; exclusion of
833 ids and 291 reduced formulas, `analysis/fresh_population_20261006/REPORT.md`, `708dd37`; P3b selection
`d1c1050` under rule `39ba728`). The Hartree tolerance behind the abstract numbers is relative error 1e-6 (`LAW`,
tau = 1e-6; joint contract in `analysis/qoac_hb_v2/DESIGN.md`). "10.5%" is the abstract form of the median ratio
1.105. The abstract carries no number from an engineering, retrospective or failed test.

### One-sentence thesis

The operator that defines a scientific measurement decides whether a tolerance can be scored (qualification), how much
an operator-aware codec gains before it is run (prediction) and where compression error goes (design); the decoded
field is then certified under the same contract, for one operator or several at once.

## 2. Main-text section order

1. **Introduction.** Downstream fidelity is an accepted requirement (credit MGARD-QoI, Jiao et al., QPET, Lee et al.
   2022, TOPIQ, Compression Safeguards, FFCz, Wu et al. SC24). Task-based quantization (Shlezinger, Eldar & Rodrigues
   2019, DOI 10.1109/TSP.2019.2935864) established that a quantizer should be designed for the task rather than for
   the signal; this work applies that principle to stored physical fields, where the task is a physical operator and
   every decoded field is recertified under it. Measurement-science analogy (limit of quantification, gauge
   capability) for qualification. Contributions listed without priority words.
2. **Results 1 — A tolerance is scored only after the contract resolves it.** QSQ on the complete contract; fresh
   risk separation (Q1); equal-search control (Q2); evaluability belongs to the contract (Q3). (Fig. 1)
3. **Results 2 — The operator symbol explains the codec effect and defines a closed-form law.** Matched-distortion
   spectral mechanism for the Hartree potential (M1); |G|^-4 squared-error weight → Δ_G ∝ |G|^2, credited as the
   classical high-rate weighted-MSE allocation; the contribution is the physical weight and the certification loop.
   (Fig. 2)
4. **Results 3 — The law, tested prospectively on bulk crystals and surface slabs.** Equal-search advantage over
   pointwise codecs (L3) and spectral truncation (L4) in both cohorts and across tolerances (L5). (Fig. 3)
5. **Results 4 — The operator metric carries the gain; the optimizer's share depends on the system class.** A3/A5 in
   both cohorts (L2); distance from the operational optimum stated per class (L1, L1s). The operational allocation
   (A3) is the recommended encoder for surfaces and the closed-form law the recommended encoder for bulk crystals.
   (Fig. 4)
6. **Results 5 — One stream, two contracts.** Joint Hartree + Bader certification on fresh P2 (J1, J2): 48/48, joint
   overhead 1.000, 1.317x over the best other base. Bader contract options under an exact partition: basin-sum
   projection (D1) and, when the partition itself is needed, a partition-faithful AECCAR versus a lossless label map
   (D2). (Fig. 5)
7. **Results 6 — The gain is predicted before compression.** Five operators plus the density control; P1 and P3b
   (P1, P2, P3). Derivative operators gain little (measured gradient 1.011 / 1.015, Laplacian 1.042 / 1.047, bulk /
   slab); smoothing operators gain an order of magnitude (Gaussian 12.1 / 15.3). (Fig. 6)
8. **Discussion.** What each stage licenses (contract change, codec choice, encoder choice per system class, whether
   operator-aware coding is worth deploying for a given operator); the operator as the unit of design. Scope stated as
   definitions: linear reciprocal-space operators of the valence density and the exact-partition Bader contract;
   bulk crystals (Materials Project) and surface slabs (NOMAD); Hartree tolerances 1e-4 to 1e-8.
9. **Methods.** Contract definition and QSQ; perturbation model; admission bound; Bader settings; Hermitian-orbit
   Fourier representation and Nyquist-safe certificate; arms A0–A6 and the operational optimum (A3); gain predictor
   (finite-rate Laplacian ECSQ, credited); fresh-population selection rules (P1, P2, P3b) and exclusion set;
   pre-registration chronology (commit table); joint-contract arms, post-processors and certify-then-project;
   statistics (bootstrap seeds and criteria).

### Proposed wording for the system-class scope (Results 4 and Discussion)

> For bulk crystals the closed-form law is within 10.5% of the operational optimum (median ratio 1.105, 95% CI
> 1.090–1.146, 60 crystals); for surface slabs operational allocation adds 22% (median ratio 1.222, 95% CI
> 1.138–1.359, 32 slabs), at a Hartree tolerance of 1e-6. In both classes the operator metric carries most of the
> gain: the optimum under the operator metric exceeds the optimum under the blind metric 2.12-fold (60/60) and
> 3.43-fold (32/32).

Sources: `LAW` (P1 verdict table; P3b verdict table); `P3B/SUMMARY.json` `part_A.tau_1e-06` (`A3_over_A1`,
`A3_over_A5`).

### Proposed wording for joint certification (Results 5)

> On 48 fresh bulk crystals, one stream from the operational Hartree encoder (R3), certified for the Hartree
> potential at 1e-6, was also certified for Bader charges with zero basin reassignment at 1e-3, 1e-4 and 1e-5 e in
> 48/48 materials. At 1e-4 e its joint compression ratio equalled its Hartree-only ratio (median overhead 1.000, 95% CI
> 1.000–1.000) and exceeded that of the best other base codec under the same joint contract in 48/48 materials
> (median 1.317-fold, 95% CI 1.269–1.360). A projection was needed only at 1e-5 e (31/165 decisions).

Sources: `HBC` (criteria table and descriptive list). Bader contract: Henkelman Bader 1.05, exact AECCAR0 + AECCAR2
reference (`analysis/qoac_hb_v2/DESIGN.md`).

## 3. Main figures (six)

All paths are relative to the repository root on this branch. Commits are the last change to the file.

| fig | single message | panels | exact data files |
|---|---|---|---|
| **1** | A scientific tolerance can be scored only once the measurement contract resolves it; the QSQ verdict predicts fresh risk. | (a) schematic: contract → QSQ → operator-derived design → decode → certify; outcomes certified / not certified / non-evaluable. (b) fresh exceedance risk, qualified vs rejected, at 1e-4 / 1e-3 / 1e-2 e (1e-3: 1.600% vs 81.325%). (c) per-material floor vs fresh risk. (d) equal-search control: no-pass 3.3% vs 66.4%. | (a) schematic; (b) `analysis/research_upgrade/p2_fresh_probe_cohort_summary.csv` (`912ad5e`); (c) `analysis/extensions_20260928/WP-A/material_risk.csv` (`f81b223`); (d) `analysis/research_upgrade/p1_common_tight_summary.csv` (`912ad5e`) |
| **2** | Matched pointwise distortion is not matched Hartree fidelity; the operator's spectral weight explains the codec effect and fixes the allocation law. | (a) radial error spectra, ZFP vs SZ3 at matched realized L∞. (b) decomposition: total spectral-energy factor 0.375963, Hartree susceptibility factor 0.202683 (457 pairs, 214 materials). (c) symbol \|G\|^-4 → Δ_G ∝ \|G\|^2 (schematic). | (a) `analysis/hartree_spectral_mechanism/results/radial_spectrum_summary.csv`; (b) `analysis/hartree_spectral_mechanism/results/matched_pair_mechanism.csv` (both `dc2b167`); (c) schematic |
| **3** | Under equal search, the closed-form law certifies an order of magnitude more than pointwise codecs and beats spectral truncation, on bulk crystals and on surface slabs. | (a) per-material CR_A1 vs CR_A6 at tau = 1e-6, bulk (60) and slab (32) markers (medians 10.2x, 18.5x). (b) CR_A1/CR_A2 at tau = 1e-6 (1.32x, 52/60; 1.41x, 27/32). (c) medians with CIs of A1/A6 and A1/A2 at tau = 1e-4, 1e-6, 1e-8 per cohort. | `analysis/general_qoac_law/results/run_P1_CONFIRMATORY/part_a_material.csv` and `analysis/general_qoac_law/results/run_P3B_CONFIRMATORY/part_a_material.csv` (columns `material_id, tau, A0…A6`); medians and CIs from `run_P1_CONFIRMATORY/SUMMARY.json` and `run_P3B_CONFIRMATORY/SUMMARY.json` (`part_A`) |
| **4** | The operator metric carries the gain; the optimizer's added share is set by the system class (bulk 1.105, slabs 1.222 at 1e-6). | (a) CR_A3/CR_A5 per material, both cohorts, three tolerances (1e-6: 2.12x, 3.43x). (b) CR_A3/CR_A1 per material by class, three tolerances (1e-6: 1.105 bulk, 1.222 slab). | same two `part_a_material.csv` files (columns A1, A3, A5); same two `SUMMARY.json` files (`A3_over_A5`, `A3_over_A1`) |
| **5** | One operator-aware stream certifies the Hartree potential and Bader charges together at no measurable extra bytes and beats every other base under the joint contract. | (a) joint overhead CR_hartree_only / CR_joint per material at tau_B = 1e-3, 1e-4, 1e-5 e (median 1.000 at each). (b) joint CR at tau_B = 1e-4: R3 vs J, T1, GF (medians 298, 213, 212, 18.6; R3 wins 48/48, 1.317x). (c) certify-then-project decisions per tau_B (projected 0/192, 0/192, 31/165). (d) Bader storage contracts on real materials: lossless label map vs partition-faithful AECCAR (median total / label map 16.3 to 56.9 across arms; label map median 12.9 kB, atom map). | (a–c) `analysis/qoac_hb_v2/results/P2_CONFIRMATORY_MANIFEST/joint_v2_best_post.csv` (columns `base, tau_bader, best_joint_post, best_joint_cr, hartree_only_cr, joint_overhead, cr_ratio_vs_best_other`) and `.../P2_CONFIRMATORY_MANIFEST/joint_v2_material.csv` (`ctp_decision, bader_error_e, reassigned_frac`) (`e4d9d0b` tree); engineering overlay: same files under `.../P2_ENGINEERING_MANIFEST/`; (d) `analysis/qoac_b3_design/results/real_engineering/rows.csv` (columns `arm, delta, total_bytes, label_ctx_bytes_atom, label_ctx_bytes_volnum, reassigned_volnum_frac`) (`01a3d54` tree) |
| **6** | The gain from operator-aware allocation is predicted before compression from the operator symbol and the reference spectrum, for bulk crystals and surface slabs alike. | (a) G_pred vs G_obs at tau = 1e-6, 300 bulk pairs and 160 slab pairs, colour = operator, marker = cohort, identity line; density control at (1, 1). (b) the same at tau = 1e-4. (c) per-operator medians, predicted vs measured, ordered by predicted gain, with the null-gain band [0.90, 1.11]. | `analysis/general_qoac_law/results/run_P1_CONFIRMATORY/part_b_material.csv` and `analysis/general_qoac_law/results/run_P3B_CONFIRMATORY/part_b_material.csv` (columns `material_id, operator, tau, blind, opt, G_obs, G_pred`); prediction timestamps: `analysis/general_qoac_law/results/predictions/` (P1 `d5fc30b`, P3b `c1e6564`) |

Figure notes (for the figure builder, not manuscript text):
- Fig. 6 plots every operator at its measured position, the Gaussian included (G_pred / G_obs medians 17.6 / 12.1
  bulk, 22.0 / 15.3 slab; `LAW`). Caption statistics are per cohort (median abs log error 0.024 and 0.029;
  Spearman 0.978 and 0.979; `LAW`). No pooled 92-material statistic is committed; none may be printed until one is.
- Fig. 4b shows both classes on one axis; its caption uses the system-class wording in §2.
- Fig. 5 is the joint-certification figure. Panel (d) may move to Extended Data (decision 6); the message stands on
  (a–c).
- Figs 3 and 4 use the arm A1 (law with continuous search). A0 (frozen-ladder QOAC-H) numbers are not drawn into
  these panels.

## 4. Supplementary Information / Extended Data

- QSQ validations: admission bound (6.70% for n = 5), implementation transfer (24 systems), grid-local extrema,
  evaluability decomposition (50/50 vs 3/50 vs 3/50), external 63-system cohort, certifying writer, chemical-direction
  case (frozen-manuscript evidence; rows Q3–Q6 of the evidence map).
- Disjoint 48-material QOAC-H confirmation (15.016x, ladder search), 254-material census and strongest baselines
  (T1, MGARD, stored V_H), each labelled with its search rule (rows H1–H3).
- Exact-partition Bader projection, 38-material holdout (D1), and the B3 Gate 0 transcription check (D2).
- Joint-certification engineering cohort (12) and the per-tau_B descriptive table (J2).
- P1 shakedown cohort (12 materials), reported separately per protocol.
- Part A and Part B tables per tolerance and per operator for both cohorts.
- Predictor development and calibration on the engineering materials, labelled as calibration that preceded the
  frozen tests (row C1 of the evidence map).
- Population construction: WS-0 rule, exclusion set, P2 and P3b rules, provenance hashes.
- Pre-registration register: every protocol with freeze commit, prediction commit, run id and outcome (decision 5).

## 5. Open items before submission

| item | state | source |
|---|---|---|
| Full-text check of UNVERIFIED citations | Verified: FFCz and BlockMGARD abstracts, Compression Safeguards DOI, Shlezinger et al. 2019, Wu et al. SC24 (arXiv), QPET, Lee et al. 2022 metadata. Open: Wu et al. SC24 proceedings DOI; the norm of Lee et al.'s constraint step (full text); BlockMGARD and Compression Safeguards full texts; the classical-coding citations listed in section H of the evidence map. | `PAV` |
| Prior-art audit addendum for P1 + P3b + HB v2 | Audit-P C1/C2 predate the P1 and P3b results; permitted wording for L1–L5, P1–P3 and J1 must be restated, with task-based quantization added under C1 and Wu et al. SC24 under C4. | `PAV`; `STATUS` "Running / next" |
| Statistics needed by Fig. 6 captions beyond the per-cohort values | A within-operator rank statistic or a pooled 92-material value needs a committed computation on the two `part_b_material.csv` files first. | `LAW` |

## 6. Decisions the authors must make

1. **Reopen the frozen manuscript or write a second paper.** (a) Reopen `paper/qoac-integration-20261005`: the
   confirmed law, gain prediction and joint certification replace the development-only QOAC-H headline; requires the
   full scope-reopening procedure and discards the completed submission QA. (b) Submit the frozen QSQ + QOAC-H
   manuscript as is and write this as a second, operator-centred paper that cites it for QSQ and QOAC-H; its headline
   is then L1–L5, P1–P3 and J1, and Fig. 1 shrinks to one motivating panel. (c) One combined paper: the strongest
   single story and the longest delay.
2. **Venue.** Nature Computational Science (method and principle; the prediction result fits best) or Nature
   Communications (broader readership). Check current display-item and word limits before fixing six figures.
3. **Title.** Choose among the three in §1; decide whether "electronic densities" stays (bulk crystals and surface
   slabs from two databases) or the title names "linear operators" explicitly.
4. **Headline encoder per system class.** This draft recommends the closed-form law for bulk and the operational
   allocation (A3) for surfaces. Confirm, or present A3 as the single encoder with the law as its closed-form
   approximation.
5. **Pre-registration register.** Publish the full register (including every NO-GO and FAIL in section G of the
   evidence map) in the SI, or only in the repository with a pointer from Methods.
6. **Place of the Bader storage comparison.** Keep Fig. 5d (label map vs partition-faithful AECCAR) in the main
   figure or move it to Extended Data.
