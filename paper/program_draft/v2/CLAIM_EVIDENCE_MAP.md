# Claim–evidence map, consolidated v2 (planning ledger, 2026-10-07)

Branch `research/program-integration-20261007` (head before this commit: `eb388c2`). Companion of
`paper/program_draft/v2/STORY_AND_FIGURES.md`. It merges `paper/program_draft/CLAIM_EVIDENCE_MAP.md` and
`paper/program_draft/alt_run_1612/CLAIM_EVIDENCE_MAP.md` and updates them with:
- P3b slab cohort, `analysis/general_qoac_law/results/RESULTS.md` (`b9fd735`) and
  `analysis/general_qoac_law/results/run_P3B_CONFIRMATORY/` (`eaa3267`);
- QOAC-HB v2, `analysis/qoac_hb_v2/results/P2_ENGINEERING_MANIFEST/RESULTS.md` (`e095a0c`) and
  `analysis/qoac_hb_v2/results/P2_CONFIRMATORY_MANIFEST/RESULTS.md` (`e4d9d0b`), protocol
  `analysis/qoac_hb_v2/DESIGN.md` (`8a784a4`);
- B3 real materials, `analysis/qoac_b3_design/results/real_engineering/RESULTS.md` (`01a3d54`);
- prior-art verification, `paper/QOAC_PROGRAM_PRIOR_ART_AUDIT_20261006_VERIFICATION.md` (`ff9283e`);
- status, `sync/PROGRAM_STATUS_20261007.md` (`47f3201`).

It changes no file outside `paper/program_draft/v2/`. The frozen manuscript is `paper/MANUSCRIPT.md` (`efd1e2c`).

## How to read this map

- **Numbers.** Every number is copied from the file in the "source" column; the hash is the last commit that changed
  that file on this branch. No number in this map is computed for this map.
- **Status labels.**
  - *prospective-confirmed*: protocol (and, where applicable, predictions) committed before any outcome, on a
    population never used in the project; every pre-registered criterion passed.
  - *confirmatory*: frozen protocol on a holdout or untouched cohort; passed. The cohort may be non-naive, or the
    test may have no separate prediction step.
  - *engineering*: development data; gates frozen before the run; no confirmation.
  - *retrospective*: analysis, census or calibration written after outcomes were known.
  - *descriptive*: reported without a pass/fail gate.
  - *FAIL / NO-GO*: a frozen criterion or gate was not met.
- **Manuscript eligibility.** Only *prospective-confirmed* and *confirmatory* rows may enter the abstract. Section G
  (failures and NO-GOs) is provenance: none of its rows is proposed as manuscript text.
- **Prior-art keys.** audit-H = `paper/QOAC_PRIOR_ART_NOVELTY_AUDIT_20261005.md`; audit-P =
  `paper/QOAC_PROGRAM_PRIOR_ART_AUDIT_20261006.md` (claims C1–C4); PAV = its verification addendum (`ff9283e`).
- **Forbidden everywhere** (audit-H "Avoid"; audit-P "Wording to avoid everywhere"): "first" or "novel" for any claim;
  "first QoI-aware / operator-aware / physics-informed / frequency-weighted compressor"; "new bit-allocation method";
  "new coding-gain theory"; "first multi-QoI certified compression"; "a priori" as a timing word.
- **Risk column.** Anticipated reviewer objections, for the authors. Not manuscript text.

## A. QSQ qualification (frozen-manuscript evidence)

| id | claim | status | exact numbers (denominators) | source | prior-art boundary | reviewer risk |
|---|---|---|---|---|---|---|
| **Q1** | A five-probe QSQ screen, frozen before the test, separates fresh Bader threshold-exceedance risk between qualified and rejected materials. | prospective-confirmed (fresh perturbations; the 254 development materials) | 14,986/14,986 valid trials. 1e-3 e: 143/254 admitted; qualified 135/8,437 = 1.600% (cluster CI 0.782–2.596%); rejected 5,326/6,549 = 81.325% (75.981–86.257%); ≥1 exceedance in 20/143 vs 110/111. 1e-4 e: 46/254, 4.016% vs 86.938%. 1e-2 e: 229/254, 0.148% vs 79.593%. | `paper/MANUSCRIPT.md` lines 55–57 (`efd1e2c`); `analysis/research_upgrade/p2_fresh_probe_cohort_summary.csv` (`912ad5e`) | Credit limit of quantification and measurement-system analysis; Compression Safeguards, TOPIQ, Jiao et al. as the QoI-control line QSQ precedes. Never "QSQ certifies stability". | Prospective in perturbations, not in materials; iid-uniform perturbation model; three thresholds share one set of response vectors. |
| Q2 | Under equalized search, failure to find a passing reconstruction concentrates in QSQ-rejected pairs. | confirmatory control | 1,332/1,332 added reconstructions; 1e-3 e: 3.3% vs 66.4%, 20.34x; 1e-4 e: 10.9% vs 79.3%; 1e-2 e: 0.0% vs 68.0%. | `paper/MANUSCRIPT.md` line 43; `analysis/research_upgrade/p1_common_tight_summary.csv` (`912ad5e`) | Association, not causal codec attribution. | Ladder density between groups. |
| Q3 | Evaluability belongs to the contract: with the partition-defining reference exact, the Bader contract is eligible; perturbing that reference removes eligibility. | confirmatory (pre-declared criterion met) | 50/53 analyzable; 1e-3 e: exact reference 50/50, both perturbed 3/50, reference only 3/50; median floor ratio 1.000. | `paper/MANUSCRIPT.md` line 81; `analysis/extensions_20261001/WP-I/summary.csv` (`9a79ea2`) | Bader topology background (Bader 1990; Henkelman/Tang). | Bader-specific; one implementation. |
| Q4 | The qualification principle transfers to grid-local density extrema; evaluability is QoI-specific. | prospective (fresh perturbations) | 118/254 qualified; maximum-count changes 0/6,962 vs 6,444/8,024 = 80.31%; Bader–extrema eligibility κ = 0.1337 (0.0164–0.2542). | `paper/MANUSCRIPT.md` lines 65–67; `analysis/extensions_20260928/WP-B/summary.csv` | TopoSZ, MSz family (topology preservation). | Grid extrema are not QTAIM critical points. |
| Q5 | QSQ classification transfers to an independent on-grid Bader implementation. | confirmatory (24-system panel) | On-grid 24/24 at 1e-4, 1e-3, 1e-2 e, κ = 1.000, ρ = 0.995; near-grid 82.6% / 83.3% / 95.8%, ρ = 0.754. | `paper/CURRENT_PAPER_STORY.md` "P3A" | — | Near-grid disagreement shows algorithm dependence. |
| Q6 | Frozen rules reproduce on an untouched external cohort; the finite panel bounds false admission; a certifying writer is near-oracle. | confirmatory / analytic | External: 63 systems, eligible 16/63, 42/63, 57/63 at 1e-4, 1e-3, 1e-2 e. Bound n^n/(n+1)^(n+1) = 6.70% (n = 5), observed 0.901%. Writer: 98.5% of oracle (14.90x vs 15.13x), 0/143 misses. | `paper/MANUSCRIPT.md` lines 59, 157, 161–163; `validation/final_external_confirmatory63_20260908/confirmatory63/external_summary_a1.csv` | Wilks tolerance limits; trial-and-error verification is standard practice. | SI material. |

## B. Mechanism and the operator law (Hartree potential)

Arms (protocol `analysis/general_qoac_law/DESIGN.md`, `fe2e08a`): A0 frozen-ladder QOAC-H v0.2; A1 closed-form law with
continuous search; A2 spectral truncation; A3 operational optimum (v0.3 Lagrangian, operator metric); A5 the same
optimum under the operator-blind metric; A6 best of ZFP/SZ3/SPERR. A1, A2, A6 have equal search.

| id | claim | status | exact numbers (denominators) | source | prior-art boundary | reviewer risk |
|---|---|---|---|---|---|---|
| M1 | At matched realized distortion, the ZFP/SZ3 Hartree-error difference is explained by where each codec places error in reciprocal space, weighted by the Hartree symbol. | retrospective (exact reproduction) | 457 pairs, 214 materials; center 0.0776221, Nyquist-safe 0.0776219; Parseval closure 1.296e-15; total spectral-energy factor 0.375963; susceptibility factor 0.202683; frequency structure = material-median 62.0% of the absolute-log effect. | `analysis/hartree_spectral_mechanism/results/REPORT.md`, `matched_pair_mechanism.csv` (`dc2b167`) | Parseval/Poisson identity is textbook; FFCz must be cited. | Mechanism for one codec pair; does not transfer to Bader. |
| **L1** | For bulk crystals, the closed-form law is within 10.5% of the operational optimum at tau = 1e-6. | **prospective-confirmed** (A-H1, P1) | 60 fresh MP bulk materials; 0 pipeline failures; A1 and A3 certified 60/60; median CR_A3/CR_A1 **1.105**, 95% CI [1.090, 1.146] (criterion ≤ 1.15, CI upper ≤ 1.20). | `analysis/general_qoac_law/results/RESULTS.md` (`b9fd735`); `run_P1_CONFIRMATORY/SUMMARY.json` (`4164519`); predictions `d5fc30b`; CI run 37488577302 | Δ ∝ w^(-1/2) is classical high-rate weighted-MSE allocation (Gersho & Gray 1992; Goyal 2001); Lagrangian operational allocation is Shoham–Gersho / Ortega–Ramchandran / RDOQ (audit-P C1). | One database for bulk. A3 is an operational optimum over a fixed shell set and ladder, not a global optimum. |
| **L1s** | For surface slabs, operational allocation adds 22% over the closed-form law at tau = 1e-6. | **prospective, measured** (the value is the A-H1 measurement on P3b; the A-H1 criterion itself failed, see G1) | 32 fresh NOMAD slabs; 0 pipeline failures; A1 and A3 certified 32/32; median CR_A3/CR_A1 **1.222**, 95% CI [1.138, 1.359]; A3 > A1 in 32/32. tau 1e-4 / 1e-6 / 1e-8: 2.22 / 1.22 / 1.08. | `analysis/general_qoac_law/results/RESULTS.md` (P3b section); `run_P3B_CONFIRMATORY/SUMMARY.json` `part_A.tau_1e-06.A3_over_A1` (`eaa3267`); predictions `c1e6564`; CI run 37493518929 | As L1. | The proposed text states the slab value as a measured property of the class (system-class scope), never as near-optimality. Near-optimality is claimed for bulk only. |
| **L2** | The operator metric, not the optimizer, carries the gain. | **prospective-confirmed** (A-H2, both cohorts) | tau = 1e-6: CR_A3/CR_A5 **2.12**, CI [1.92, 2.46], 60/60 (bulk); **3.43**, CI [2.89, 4.08], 32/32 (slabs). Bulk 1e-4 / 1e-8: 1.33 / 1.60; slab 1e-4 / 1e-8: 1.82 / 3.04. | `RESULTS.md` (both sections); both `SUMMARY.json` (`A3_over_A5`) | Indirect RD (Witsenhausen 1980); task-based quantization (Shlezinger et al. 2019, DOI 10.1109/TSP.2019.2935864, verified in PAV); MGARD negative-Sobolev norms (Ainsworth et al. 2019). Permitted: "no retrieved work reports this ablation for an electronic-structure QoI". | Definition of A5 must be stated exactly (`analysis/qoac_v03_rdo/DESIGN.md`). |
| **L3** | Under equal search, the closed-form law certifies an order of magnitude more than the best pointwise codec. | **prospective-confirmed** (A-H3, both cohorts) | tau = 1e-6: CR_A1/CR_A6 **10.2**, CI [9.13, 12.09], 60/60 (bulk); **18.5**, CI [15.8, 23.1], 32/32 (slabs). Bulk 1e-4 / 1e-8: 9.10 / 3.30; slab: 15.9 / 7.0. | `RESULTS.md`; both `SUMMARY.json` (`A1_over_A6`) | audit-H list (MGARD-QoI, Jiao, QPET, Lee, TOPIQ); FFCz must be cited and discussed (PAV). | Must not be mixed with the frozen manuscript's ladder-searched 15.016x (H1). |
| **L4** | Under equal search, the law beats spectral truncation at tau = 1e-6. | **prospective-confirmed** (A-H4, both cohorts) | CR_A1/CR_A2 **1.32**, CI [1.27, 1.35], 52/60 (bulk); **1.41**, CI [1.28, 1.72], 27/32 (slabs). | `RESULTS.md`; both `SUMMARY.json` (`A1_over_A2`) | Low-rate transform coding (Mallat–Falzon 1998; Sullivan 1996). | See L5 for tau = 1e-4. |
| L5 | The size of each advantage depends on tolerance. | prospective data, descriptive | A1/A2 at 1e-4 / 1e-6 / 1e-8: bulk 0.79 / 1.32 / 1.59; slab 0.69 / 1.41 / 2.16. A3/A1: bulk 1.58 / 1.10 / 1.03; slab 2.22 / 1.22 / 1.08. A3/A0: bulk 1.71 / 1.33 / 1.16. | `RESULTS.md` (Part A tables, both cohorts) | Dead-zone / low-rate theory (Mallat–Falzon; Sullivan; He–Mitra). | At 1e-4 truncation beats the pure power law in both cohorts; the figure (Fig. 3c) shows it. Every law claim names its tau. |

## C. Gain predicted before compression

| id | claim | status | exact numbers (denominators) | source | prior-art boundary | reviewer risk |
|---|---|---|---|---|---|---|
| **P1** | For five downstream operators (plus the density control), the gain of operator-weighted over operator-blind allocation, predicted before compression, matched the measured gain on bulk crystals. | **prospective-confirmed** (B-H1–B-H4, P1) | tau = 1e-6, 60 materials × 5 operators = 300 pairs: median \|ln(G_pred/G_obs)\| **0.024** (≤ 0.223); Spearman **0.978** (≥ 0.85); all operator pairs ordered as predicted; null-gain operators within [0.90, 1.11]: gradient 100%, Laplacian 98.3% (≥ 80%); density G_obs = 1. tau = 1e-4: 0.034, Spearman 0.944. | `RESULTS.md`; `run_P1_CONFIRMATORY/SUMMARY.json`, `part_b_material.csv` (`4164519`); predictions `analysis/general_qoac_law/results/predictions/` (`d5fc30b`) | Coding gain (Huang–Schultheiss 1963; Jayant–Noll 1984); perceptual coding gain (Wei et al. 1997, UNVERIFIED); dead-zone theory; CR prediction (Underwood et al. 2023). "Predicted before compression" is a timing statement. Forbidden: "new coding-gain theory". | Pooled Spearman spans operators whose gains differ ~10x: mostly between-operator order. A within-operator statistic is not committed. |
| **P2** | The same prediction holds on surface slabs from a second database. | **prospective-confirmed** (B-H1–B-H4, P3b) | tau = 1e-6, 32 slabs × 5 = 160 pairs: median abs log error **0.029**; Spearman **0.979**; B-H3, B-H4 and control hold. tau = 1e-4: 0.040, Spearman 0.914. | `RESULTS.md` (P3b section); `run_P3B_CONFIRMATORY/SUMMARY.json`, `part_b_material.csv` (`eaa3267`); predictions `c1e6564` | As P1. | As P1. |
| P3 | Which operators gain is set by the operator symbol: derivative operators gain little, smoothing operators gain an order of magnitude. | prospective data (per-operator medians) | G_pred / G_obs, bulk; slab: gradient 1.014 / 1.011; 1.012 / 1.015. Laplacian 1.040 / 1.042; 1.031 / 1.047. Hartree field 1.151 / 1.149; 1.164 / 1.165. Hartree potential 2.72 / 2.61; 3.55 / 3.14. Gaussian (σ = 0.5 Å) 17.6 / 12.1; 22.0 / 15.3. | `RESULTS.md`; `sync/PROGRAM_STATUS_20261007.md` | As P1. | Gaussian gain overstated about 1.45x in both cohorts (`STATUS`); bulk per-operator median abs log error 0.431 (`RESULTS.md`). Fig. 6 plots it at its measured position. |

## D. Joint certification and the Bader contract

Joint contract (`analysis/qoac_hb_v2/DESIGN.md`, `8a784a4`): Hartree relative RMSE < 1e-6 (historical and
Nyquist-safe) on the final stream; Henkelman Bader 1.05 (`-b ongrid -vac 0.001`, exact AECCAR0 + AECCAR2 reference),
max atomic-charge error ≤ tau_B and zero basin reassignment; tau_B ∈ {1e-3, 1e-4, 1e-5} e, primary 1e-4. Bases: R3
(v0.3 operational optimum), J (QOAC-H v0.2), T1 (truncation), GF (ZFP/SZ3/SPERR). Population P2: fresh MP bulk with
AECCAR (12 engineering + 48 confirmatory).

| id | claim | status | exact numbers (denominators) | source | prior-art boundary | reviewer risk |
|---|---|---|---|---|---|---|
| **J1** | One operator-aware stream is certified for the Hartree potential and Bader charges together, with no measurable byte overhead, and beats every other base under the joint contract. | **confirmatory** (protocol and criteria frozen `8a784a4` before any P2 run; fresh population; all criteria pass) | 48/48 successful, 0 setting failures. C1: jointly certified at all three tau_B **48/48** (≥ 46). C2: overhead at 1e-4 median **1.000**, CI [1.000, 1.000] (≤ 1.10, CI upper ≤ 1.15). C3: R3 vs best of J, T1, GF **48/48** wins, median **1.317**, CI [1.269, 1.360], min 1.096 (≥ 36/48, > 1.10, CI lower > 1.00). Bootstrap seed 20261007, 10,000 resamples. CI run 37497825261. | `analysis/qoac_hb_v2/results/P2_CONFIRMATORY_MANIFEST/RESULTS.md` (`e4d9d0b`); `joint_v2_best_post.csv`, `joint_v2_material.csv`, `SUMMARY.json` | Gong et al. 2022 (multi-QoI XGC); Lee et al. 2022; Jiao et al.; QPET (PAV); Wu et al. SC24, arXiv:2411.05333 (several derivable QoIs at once, PAV); Compression Safeguards. Forbidden: "first multi-QoI certified compression". | Under an exact partition Bader is not binding at 1e-3 and 1e-4 e (best post `none` in 48/48), so the joint result shows the Hartree-certified stream already carries Bader. Population is bulk only. |
| J2 | Projection is needed only at the tightest Bader tolerance; engineering agrees. | confirmatory cohort, descriptive / engineering gates | Confirmatory: best post `none` 48/48 at 1e-3 and 1e-4; at 1e-5 `none` 33/48, `hap:0.0001` 15/48. CTP projected 0/192, 0/192, 31/165. Median joint CR at 1e-4: R3 298, J 213, T1 212, GF 18.6; median R3 joint CR 298 at every tau_B. HAP vs uniform at 1e-5: median 1.00 (n = 35). Engineering (12): E1 12/12, E2 1.000 (12/12), E4 12/12 wins, median 1.355 (min 1.167); median overhead at 1e-5 1.0032; R3 297, J 224, T1 191, GF 17.1. | `HBC` descriptive list; `analysis/qoac_hb_v2/results/P2_ENGINEERING_MANIFEST/RESULTS.md` (`e095a0c`) | As J1. | Hartree-aware projection did not change certified rates (1.00); do not present HAP as a gain. |
| D1 | With the partition-defining reference held exact, a minimum-norm per-basin correction after generic compression gives certified Bader charges with zero reassignment. | confirmatory (38-material holdout) | 38/38 analyzable; max Bader error 0.0 e; max reassigned 0.0; 34/38 wins; median CR ratio 1.86462 (CI 1.75916–1.98549); min 0.99666; max side channel 0.999%; κ = 4. Engineering 11/12, 1.782x. | `analysis/operator_aware_bader_projection_confirmatory/results/SUMMARY.json` (`8e4b5e8`); `analysis/operator_aware_bader_projection/results/RESULTS.md` (`892bedb`) | Lee et al. 2022 (DOI 10.3390/app12136718, metadata verified in PAV) is the same construction; Compression Safeguards (DOI 10.5194/egusphere-2026-4266, verified). Uniform-shift optimality is elementary. Forbidden: "novel projection". | κ = 4 permits about 3x the baseline L∞; see G6. |
| D2 | On real materials, the Henkelman partition can be stored either as a partition-faithful AECCAR (identical partition, zero reassignment) or as a lossless label map at about 1/17 of the size. | descriptive engineering (no gate) | Gate 0: partition identical voxel for voxel 11/11 (0 mismatching voxels); maxima 3,339/3,339; R1/R2 0 violations; atom map identical 9/11 (min 97.9%); literal transcription 3/3. Arms 12/12 each, zero reassignment and max Bader error 0 e: A2 1e-3 total/label map 17.3; A2 1e-2 16.3; A2 5e-2 27.1; A1 1e-3 21.1; A1 1e-2 29.5; A1 5e-2 56.9. Base quantizer alone reassigns a median 45–91% of voxels. Label map: exact round trip 12/12; charges match binary 12/12 (max 5.0e-7 e); median 12.9 kB (atom), 21.8 kB (volnum). | `analysis/qoac_b3_design/results/real_engineering/RESULTS.md` (`01a3d54`); `rows.csv`, `gate0.csv` | Topology-preserving compression (MSz, pMSz, TopoSZ, EXaCTz; all UNVERIFIED in the B3 design study). | 12 materials, no confirmation; 1 Gate 0 comparison failed in the comparison code (mp-2302539, 74 GiB array), not in the partition. Recommended contract per source: Hartree-certified CHGCAR + lossless label map. |

## E. Development-scale QOAC-H evidence and populations (SI candidates)

| id | claim | status | exact numbers (denominators) | source | prior-art boundary | reviewer risk |
|---|---|---|---|---|---|---|
| H1 | QOAC-H (frozen ladder) beats each material's best certified ZFP/SZ3/SPERR on a disjoint cohort. | confirmatory | 48/48 wins; median 15.016x (11.204–21.461); bulk 11.203x, slab 25.699x; Nyquist-safe 48/48. | `analysis/operator_aware_codec_hartree_v02_confirmatory/results/RESULTS.md` (`31def38`) | audit-H in full. | Baselines on a ladder, not bisected; never in one sentence with L3. Already in the frozen manuscript. |
| H2 | The direction holds across six Hartree tolerances. | retrospective census | 254 materials, 6,350/6,350 settings; tau = 1e-6: 253/253 wins, median 12.463x, P05 4.459x. | `analysis/operator_aware_codec_hartree_v02_census/results/RESULTS.md` (`cc5d7a1`) | As H1. | Development population. |
| H3 | The operator allocation adds a factor over spectral truncation; MGARD and stored V_H are far weaker. | confirmatory (frozen `1c5c819`) | 45/48 wins, median 1.564x (1.376–1.622), min 0.843x; median CR QOAC-H 383, T1 233, ZFP/SZ3/SPERR 22.1, MGARD 16.0; vs MGARD 19.4x (48/48); vs stored V_H 19.4x (48/48). | `analysis/qoac_h_strong_baselines/results/RESULTS.md` (`0c8b550`) | MGARD Sobolev control (Ainsworth et al. 2019). | MGARD tested only to s = -1. |
| E1 | Confirmatory populations were drawn under rules frozen before download, excluding every id and formula used before. | infrastructure | Rule `10e7863`. P1 12 + 60 MP bulk; P2 12 + 48 MP bulk with AECCAR; exclusion 833 ids, 291 reduced formulas. P3b: 32 NOMAD slabs, selection `d1c1050`, rule `39ba728`. | `analysis/fresh_population_20261006/REPORT.md` (`708dd37`); `analysis/general_qoac_law/results/RESULTS.md` (P3b header) | Positioning only. | Most MP materials identified by task id only. |

## F. Engineering, retrospective and calibration rows (provenance; SI at most)

| id | what | status | exact numbers | source | use |
|---|---|---|---|---|---|
| C1 | Finite-rate Laplacian-ECSQ predictor calibration before P1. | retrospective calibration | Hartree β2/β0: observed 0.0767; finite-rate (b) 0.0832 (median \|log err\| 0.148), ρ = 0.96; high-rate (a) 0.0496. E-field β1/β0: (b) 0.790 vs 0.806. | `analysis/general_qoac_operators/results/RESULTS.md` (`f4baa7a`); `STATUS` | Methods: the predictor form was fixed here and tested only prospectively on P1 and P3b. |
| C2 | Operator-derived exponent beats operator-blind allocation at matched storage (QOAC-H mechanism test). | engineering | 12/12; median Hartree-error ratio β2/β0 0.0767117. | `analysis/operator_aware_codec_hartree/results/SUMMARY.json` (`a1351d1`) | Design history. |
| C3 | v0.3 operational optimum built as reference A3. | engineering (G1 GO, G3 GO; G2 NO-GO, see G3) | 12 materials, tau 1e-6: A3/A5 2.206; A3/A4 0.999. | `analysis/qoac_v03_rdo/results/RESULTS.md` (`06d0d78`) | Methods (definition of A3). |
| C4 | P1 shakedown cohort (12; not in any criterion). | descriptive | A3/A1 1.156; A3/A5 2.26; A1/A6 9.80; A1/A2 1.24; Part B 0.024, Spearman 0.979. | `analysis/general_qoac_law/results/RESULTS.md` | SI, separately per protocol. |
| C5 | Joint certification on the old 50 (v1). | confirmatory criteria 1–3 pass; criterion 4 FAIL (G4) | 50/50 jointly certified; before projection the QOAC-H stream met Bader at ≤ 5.3e-5 e in 50/50. | `analysis/qoac_hb_joint/results/RESULTS.md` (`d843151`) | Motivated HB v2; superseded by J1. |

## G. Failures and NO-GOs (provenance ledger — not manuscript text)

| id | what was tested | status | exact numbers | source | consequence for wording |
|---|---|---|---|---|---|
| **G1** | P3b A-H1: closed-form law near the operational optimum on 32 fresh NOMAD slabs (median CR_A3/CR_A1 ≤ 1.15, CI upper ≤ 1.20). | **FAIL** (all other P3b criteria pass) | median **1.222**, CI [1.138, 1.359]; 32/32 certified. | `analysis/general_qoac_law/results/RESULTS.md` (P3b section, `b9fd735`); `run_P3B_CONFIRMATORY/SUMMARY.json` (`part_A_pass`) | Near-optimality is claimed for bulk only (L1). For slabs the measurement is stated as system-class scope (L1s: "operational allocation adds 22%"). Never "near-optimal for electronic densities" in general. |
| G2 | Electric-field β = 1 law, engineering gates A, B, C. | NO-GO | Gate A 0.8064 (< 0.70 required); Gate B 0.928 (< 0.90); Gate C 7/12, 1.031x. | `analysis/general_qoac_electric_field/results/RESULTS.md` (`9d33d24`) | No "cross-operator confirmation" from it; the Hartree field enters only through P1–P3. |
| G2b | Electric-field finite-rate β map (M2). | NO-GO | β* = 1.25; M2 vs β0 0.770, vs β2 0.963. | `analysis/general_qoac_electric_field_beta_map/results/RESULTS.md` (`81e4760`) | As G2. |
| G3 | v0.3 as a better codec (G2 gate: median R3 > 1.20). | NO-GO | 12/12 wins, median 1.099, min 1.046. | `analysis/qoac_v03_rdo/results/RESULTS.md` (`06d0d78`) | v0.3 appears as the operational optimum A3 and as joint base R3, both under frozen protocols; never "improved codec" from this run. |
| G4 | QOAC-HB v1 joint advantage (median R_J > 1.25). | FAIL | 1.224; 30/38 wins; CI 1.131–1.478. | `analysis/qoac_hb_joint/results/RESULTS.md` (`d843151`) | Superseded by J1 on a fresh population with a new frozen protocol; v1 numbers are not quoted. |
| G5 | B1 basin-mean + zero-sum residual transform. | NO-GO (Gates B, C) | Gate B 0/12, 0.401x; Gate C 0.299x. | `analysis/operator_aware_bader_fixed_partition/results/RESULTS.md` (`ac374ba`) | Replaced by D1. |
| G6 | B2 at tight density budget κ = 1, 2. | descriptive | κ = 1: 4/12, 0.803x; κ = 2: 5/12, 0.999x. | `analysis/operator_aware_bader_projection/results/RESULTS.md` | D1 names κ = 4. |
| G7 | QOAC-H v0.1 competitive gate. | NO-GO (mechanism GO) | median 1.004 (0.921–1.586). | `analysis/operator_aware_codec_hartree/results/RESULTS.md` (`a1351d1`) | v0.2 (H1) is the confirmed codec. |
| G8 | Original P3 slab cohort (72 under WS-0). | infeasible, not run | ≤ 23 drawable. | `analysis/fresh_population_20261006/REPORT.md` (`708dd37`) | Replaced by P3b (amendment 1). |
| G9 | Frozen-manuscript historical claims withdrawn or falsified. | FALSIFIED | see `paper/CLAIM_EVIDENCE_MATRIX.md` claims 3, 6, 9–12 | frozen-paper ledger | Must not be cited. |

The consolidated status lists the same failure record: "E-field beta=1 gates (A, B, C); beta-map M2; v0.3 G2;
QOAC-HB confirmatory median; B1 residual transform; P3b A-H1" (`sync/PROGRAM_STATUS_20261007.md`).

## H. Prior art to credit and citation status

| work | verified facts (PAV unless stated) | credit in | status |
|---|---|---|---|
| Shlezinger, Eldar & Rodrigues, "Hardware-limited task-based quantization", IEEE TSP 67 (2019), DOI 10.1109/TSP.2019.2935864, arXiv:1807.08305 | Quantizers designed to recover a task vector, not the input. | Introduction; L2. Difference: stored physical field, quantizer shaped by an operator symbol and recertified under that operator. | verified |
| FFCz, arXiv:2601.01596 (Ren et al., 2026) | Post-processing projection onto spatial and frequency-domain error bounds for SZ3/ZFP/SPERR output; no physical-operator weighting in the abstract. | Introduction; M1; L3. | abstract verified |
| Compression Safeguards, DOI 10.5194/egusphere-2026-4266 (Tyree et al.) | Pointwise and QoI-based safeguards, corrections as binary differences. Exact region sums not stated in the abstract. | D1; Introduction. | DOI verified; full text open |
| Wu et al., SC'24, arXiv:2411.05333 | Error-controlled progressive retrieval under derivable QoIs; several QoIs controlled at once. | J1 (several QoIs). | arXiv verified; proceedings DOI open |
| QPET, arXiv:2412.02799 (PVLDB 18, 2025) | QoI preservation for differentiable QoIs inside error-bounded compressors. | Introduction; J1. | verified |
| Lee et al., Appl. Sci. 12(13) 2022, DOI 10.3390/app12136718 | Constraint-satisfaction post-processing to preserve QoIs on XGC. | D1. | metadata verified; norm of constraint step open (full text) |
| BlockMGARD, arXiv:2609.00205 | Region-of-interest error control on GPUs; no operator-norm allocation in the abstract. | Introduction (if retained). | abstract verified; full text open |
| Classical allocation and coding gain: Gersho & Gray 1992; Goyal 2001; Shoham–Gersho 1988; Ortega–Ramchandran 1998; Sullivan–Wiegand 1998; Huang–Schultheiss 1963; Jayant–Noll 1984; Wei, Shaw & Varley 1997; Mallat–Falzon 1998; Sullivan 1996; He–Mitra 2002; Underwood et al. 2023; Witsenhausen 1980; Ainsworth et al. 2019 | — | L1–L5, P1–P3. | UNVERIFIED details per audit-P (DOIs, pages, chapters) |
| B3 / topology: MSz, pMSz (arXiv:2601.01787), discrete MS complex (arXiv:2409.17346), EXaCTz (arXiv:2604.01397), TopoSZ; Henkelman 2006; Tang 2009; Yu & Trinkle 2011 | — | D2; Q3. | UNVERIFIED (B3 design study) |
