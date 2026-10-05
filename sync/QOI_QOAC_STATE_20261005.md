# QSQ / QOAC project state — 2026-10-05

Status: synchronized research snapshot for GitHub, Notion, Supabase, and agent handoff.

## System of record

- Repository: `stloendays/QoI`
- Current integration/research branch: `research/general-qoac-electric-field-20261005`
- Current branch head before this snapshot: `3e0dc72a70b5393583656373ea91a64a035d4057`
- Canonical paper branch: `paper/qoac-integration-20261005`
- Paper branch head: `10d3d3755a50f9884c93fa2d7267adbcb9fecc31`

GitHub is the authoritative source for code and machine-readable results. Notion is the human-readable project log. Supabase stores a structured experiment/provenance index; it must reference GitHub branch + commit + path rather than becoming a second source of code truth.

## 1. QSQ / manuscript

Active manuscript title:

> Numerical stability qualification and operator-aware compression of electronic densities

Scientific story:

`measurement-contract qualification -> diagnosis -> operator/measurement-structure-aware compression -> decoded-field certification`.

QSQ remains logically prior to codec scoring.

Paper status:
- QOAC-H integrated into canonical manuscript.
- Main figures are Fig. 1–9.
- Fig. 8 = QOAC-H diagnosis-to-design.
- Fig. 9 = untouched external confirmation.
- main manuscript final audit: 0 blockers / 0 warnings.
- SI final audit: 0 blockers / 0 warnings.
- final DOCX/PDF release QA remains.

## 2. QOAC-H — Hartree operator-aware compression

Branch lineage is already contained in the current research branch.

Core code:
- `analysis/operator_aware_codec_hartree_v02/codec_qoac_h_v02.py`

Mechanism:
- Hartree squared-error weight: `|G|^-4`.
- frozen high-rate law: `Delta_G propto |G|^2`.
- operator-derived `beta=2` vs operator-blind `beta=0`: 12/12 engineering materials favor beta=2.
- median Hartree error ratio beta2/beta0 = **0.0767117**.

Disjoint confirmation:
- 48/48 unseen materials win against each material's best certified ZFP/SZ3/SPERR baseline.
- median certified CR ratio = **15.016x**.
- bootstrap 95% CI = **[11.204, 21.461]**.
- all 48 pass the Nyquist-safe guardrail.

Full development-population census:
- 254 materials.
- 6,350/6,350 settings successful.
- 0 failures.
- at Hartree relative RMSE `1e-6`: 253/253 comparable wins.
- median CR ratio = **12.463x**.
- P05 = **4.459x**.
- minimum = **2.444x**.

Interpretation:
- positive demonstration of diagnosis-to-design.
- Hartree-specific; do not transfer the `|G|^2` law to Bader.

## 3. QOAC-B1 — fixed-partition basin-nullspace engineering

Branch: `research/qoac-b-fixed-partition-20261005`
Head: `ac374bac459fe4d02f44ad708bacd09d63cd69b5`

Core code:
- `analysis/operator_aware_bader_fixed_partition/qoac_b_core.py`
- `analysis/operator_aware_bader_fixed_partition/run_engineering.py`
- `analysis/operator_aware_bader_fixed_partition/aggregate_engineering.py`

Population:
- 12 engineering materials.
- 38-material holdout frozen before execution.

Result:
- scientific mechanism Gate A = GO:
  - max actual Bader error = 0.
  - max reassignment = 0.
  - max scaled basin-sum closure error = 8.30e-16.
- residual-transform Gate B = NO-GO:
  - 0/12 beat the generic G1 baseline.
  - median CR ratio R/G1 = **0.4010x**.
- transform-over-projection Gate C = NO-GO:
  - median CR ratio R/P = **0.2985x**.

Conclusion:
- fixed-partition Bader sensitive-subspace idea is valid.
- explicit basin-mean + zero-sum residual representation is compression-hostile and was rejected.
- holdout was not touched by B1.

## 4. QOAC-B2 — projection-aware Bader compression

Engineering branch: `research/qoac-b2-projection-aware-20261005`
Head: `892bedbe87715ecd8152dc9e0d8f6b1038845c1c`

Confirmatory branch: `research/qoac-b2-confirmatory-20261005`
Head: `34076deb9b7de19b922b0dd2d4a51ea449eebf51`

Core method:
- keep AECCAR exact / partition fixed.
- compress CHGCAR with generic backend.
- decode.
- apply uniform basin correction that restores each fixed region sum.
- this correction is simultaneously minimum-Linf and minimum-L2 among unconstrained corrections satisfying the region-sum constraint.
- count complete side-channel bytes.
- run actual Henkelman Bader after reconstruction.

Frozen primary engineering contract:
- Bader tolerance `tau_B = 1e-3 e`.
- auxiliary density budget `kappa = 4`, meaning final CHGCAR Linf <= 4 x the best frozen generic Bader-certified baseline Linf.

Engineering result:
- Gate A scientific closure = GO.
- Gate B useful rate gain = GO.
- Gate C side-channel practicality = GO.
- 12/12 actual Bader error = 0.
- 12/12 zero reassignment.
- 11/12 beat baseline.
- median CR ratio = **1.7820x**.
- max side-channel fraction = **0.7117%**.

Frozen 38-material confirmatory result:
- **PASS**.
- 38/38 analyzable, zero pipeline failures.
- 38/38 actual Bader error = 0.
- 38/38 zero reassignment.
- 34/38 wins.
- win fraction = **89.47%**.
- median CR ratio = **1.86462x**.
- bootstrap median 95% CI = **[1.75916, 1.98549]**.
- minimum CR ratio = **0.99666x**.
- P05 = **0.99944x**.
- maximum CR ratio = **10.9781x**.
- max side-channel fraction = **0.9990%**.

Interpretation:
- Bader is not discarded.
- it defines a second QOAC design pattern: `generic compression -> minimum-disturbance scientific constraint projection -> actual certification`.
- compression of AECCAR / partition topology is still a separate future problem.

## 5. General-QOAC case 3 — Hartree electric field

Current branch: `research/general-qoac-electric-field-20261005`
Engineering result head before sync: `3e0dc72a70b5393583656373ea91a64a035d4057`

Code:
- `analysis/general_qoac_electric_field/electric_field_operator.py`
- `analysis/general_qoac_electric_field/run_engineering.py`
- `analysis/general_qoac_electric_field/aggregate_engineering.py`

Prospective theory:
- `E_H(G) propto G rho(G) / |G|^2`.
- squared electric-field error weight `propto 1/|G|^2`.
- predicted first-order allocation: `Delta_G propto |G|`.
- therefore frozen predicted exponent: `beta = 1`.
- compare against `beta=0` and Hartree-specific `beta=2`.

Metric correction before any material result:
- electric-field derivative has even-grid Nyquist ambiguity.
- Nyquist-safe electric-field relative RMSE became the primary field metric before material execution.
- the formal all-mode historical quantity is diagnostic/guardrail only.

Engineering execution:
- 12 materials.
- 900 settings.
- 0 failures.

Frozen gates:
- Gate A beta=1 vs beta=0: **NO-GO** under the pre-specified effect-size threshold.
  - beta=1 better in 12/12 materials.
  - median matched-storage error ratio = **0.80637**.
  - directional prediction correct, effect smaller than required (<0.70).
- Gate B beta=1 vs beta=2: **NO-GO**.
  - beta=1 better in 10/12 materials.
  - median matched-storage error ratio = **0.92805**.
  - effect smaller than required (<0.90).
- Gate C certified-rate ablation: **NO-GO**.
  - 7/12 wins.
  - median CR ratio beta1 / best(beta0,beta2) = **1.03128x**.

Confirmatory authorization:
- **False**.
- no new electric-field holdout may be executed under the current protocol.

Interpretation:
- the operator-predicted direction is visible but not strong enough to pass the frozen mechanism thresholds.
- do not claim General-QOAC cross-operator confirmation from this experiment.
- next work should diagnose why beta=1 gives only a modest advantage: coefficient statistics, rate model, shell discretization, non-high-rate behavior, or vector-field/Nyquist structure.
- any redesigned electric-field method must be a new engineering iteration; do not reuse a future holdout until a new protocol is frozen.

## 6. Current conceptual model

Three distinct levels now exist:

1. **QSQ qualification** — is the scientific ruler itself numerically resolvable?
2. **QoI-specific compression design**:
   - Hartree: operator-induced spectral allocation.
   - fixed-partition Bader: scientific-constraint projection.
3. **post-decode certification** — compute the actual downstream QoI on the reconstructed field.

Current evidence supports two design patterns, not yet a universal General-QOAC theorem.

## 7. Immediate next decisions

1. Preserve the current QOAC-H manuscript as a valid frozen submission story; QOAC-B2/electric-field work should not silently alter it.
2. Decide whether QOAC-B2 becomes:
   - a second manuscript / extension, or
   - a later scope reopening after prior-art audit and manuscript architecture review.
3. For electric field, perform diagnosis on the engineering data only:
   - inspect optimal beta continuously or over a predeclared finer beta grid;
   - estimate actual entropy/rate sensitivity by spectral shell;
   - compare high-rate theory against finite-rate quantization;
   - test whether the predicted beta=1 is weakened by the actual coefficient distribution.
4. Do not execute an electric-field confirmatory cohort yet.
5. A future topology-aware AECCAR codec remains QOAC-B3, not part of the current validated B2 claim.

## 8. Addendum (2026-10-05, later the same day)

### 8a. Electric-field finite-rate beta map — NO-GO (already executed before this snapshot; previously unrecorded here)

Branch `research/general-qoac-electric-field-beta-map-20261005`, commit `81e4760`.
- 12 materials, beta in {0, 0.25, ..., 2}, 2,700 settings, 0 failures.
- beta_star = 1.25; M1 GO, M3 GO (beta1/beta_star = 1.009), M2 NO-GO (vs beta0 0.770, vs beta2 0.963).
- confirmatory_authorized = false.

### 8b. Electric-field finite-rate diagnosis — diagnosis only

Branch `research/general-qoac-electric-field-diagnosis-20261005`, commit `e819813`.
- High-rate theory evaluated on each orbit set predicts beta1/beta0 = 0.783 and beta1/beta2 = 0.913
  (median), close to the observed 0.806 / 0.928. Frozen gates 0.70 / 0.90 lie beyond the theory in 11/12 and
  9/12 materials. Hartree calibration: theory 0.050 vs observed 0.077.
- ~90% of orbits sit in the quantizer dead zone; actual error is 0.19–0.75x the high-rate prediction.
- Ideal entropy coding removes the beta1-over-beta2 edge (ratio 1.02–1.03); packing does not mask beta = 1.
- Marginal slopes imply a finite-rate exponent of about 1.56.
- Reading: the operator direction holds, but the electric field is too weak an operator to separate exponents.
  The frozen NO-GO stands; no electric-field confirmatory cohort.

### 8c. QOAC-H strongest-baseline study — in progress

Branch `research/qoac-h-strong-baselines-20261005`. The protocol was frozen (`1c5c819`, amendment 1 for the
MGARD install route) before any baseline result. Arms on the 48 frozen confirmatory materials: T1 spectral
truncation, M MGARD with s in {inf, 0, -1}, and V (stored Hartree potential, a contract-changing reference).
Motivation: the certified QOAC-H rows have median density Linf 1.89, so a low-pass baseline is the relevant
competitor. Not part of the frozen manuscript.
