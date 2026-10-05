# QOAC-H v0.2 held-out confirmation

Date frozen: 2026-10-05

Status: **prospective confirmatory evaluation**. The QOAC-H v0.2 algorithm is frozen before this population is executed.

## Frozen algorithm authority

Algorithm: QOAC-H v0.2 conservative Nyquist-aware Hermitian-orbit codec.

Frozen source path:

    analysis/operator_aware_codec_hartree_v02/codec_qoac_h_v02.py

Frozen Git blob SHA:

    0a37a3cad2eeb94706ddfbed289229f8c0f4aa78

Historical/Nyquist-safe Hartree evaluation helper:

    analysis/operator_aware_codec_hartree/codec_qoac_h.py

Frozen evaluation-helper Git blob SHA:

    1d50b591aac5e5adee8c2813b435ad7a9bbc791f

Parent engineering result commit:

    4f24b3c9672b0b2367792dd50a2bf858c7959c41

No codec parameter, reciprocal-space allocation law, Nyquist treatment, shell count, entropy backend or certification rule may be changed on the basis of held-out results.

The allocation remains

    Delta_G = alpha * (|G|_cons / Gmax_cons)^2,

where |G|_cons is the conservative minimum reciprocal magnitude across alias-equivalent Nyquist sign choices.

## Population

The exact population is frozen in:

    analysis/operator_aware_codec_hartree_v02_confirm/HELDOUT_MANIFEST.csv

It contains **242 materials**:
- 180 bulk;
- 62 slab.

Construction:
- start from the exact 254-material development population in the completed full Hartree-QSQ study;
- exclude the exact 12 materials used for QOAC-H v0.1/v0.2 engineering and tuning;
- retain every remaining material.

At the primary Hartree contract tau_H = 1e-6, the completed Hartree-QSQ authority reports 254/254 materials eligible. The manifest records each held-out material's frozen QSQ response scale and requires it to be below 1e-6.

The 242 materials are assigned to 24 execution shards before QOAC-H held-out execution. Assignment is deterministic and outcome-blind: materials are sorted by decreasing npoints and greedily assigned to the shard with the smallest accumulated npoints, with shard index as the tie breaker.

## Frozen alpha ladder

For every held-out material:

    beta = 2

and

    alpha / ptp(rho) = logspace(1e-7, 1e1, 25).

All 25 settings are executed. No adaptive search, per-material tuning or early stopping is allowed.

## Dual scientific-use certificate

A QOAC-H reconstruction is certified at the primary contract only if both are true:

    historical Hartree relative RMSE < 1e-6

and

    conservative alias-safe Hartree relative norm < 1e-6.

The Nyquist-safe historical-mechanism metric is reported as a diagnostic.

For each material, the QOAC-H candidate is the highest actual serialized compression ratio among dual-certified evaluated settings.

## Frozen comparator

Comparator authority:

    analysis/hartree_qsq_full/results/hartree_codec_rows.csv

For each material, the existing-codec comparator is the highest reproduced compression ratio among ZFP, SZ3 and SPERR rows satisfying:
- scientific_reproduction_gate_pass = true;
- historical Hartree relative RMSE < 1e-6.

This is the strongest certified evaluated existing-codec baseline, not a single hand-picked codec.

Before QOAC-H held-out execution, the frozen comparator authority yields a certified baseline for 241/242 held-out materials.

The one pre-identified material with no certified existing-codec point is:

    mp-1038991

It remains in all QOAC-H certification and robustness accounting, but is excluded from paired QOAC-H/baseline compression-ratio statistics. Its outcome cannot change that rule.

## Pipeline/accounting gate

Confirmatory inference is permitted only if:
- all 242 manifest materials are accounted for;
- all 6050 planned QOAC-H settings are accounted for;
- there are zero material-level or setting-level execution failures;
- the frozen codec Git blob SHA matches exactly;
- source SHA-256 and byte-count checks pass for every material.

Any infrastructure or reproduction defect is repaired transparently and requires a fresh run; it is not interpreted as a scientific NO-GO.

## Primary confirmatory statistics

For each of the 241 pre-comparable materials define

    R_i = CR_QOAC-H,i / CR_best-existing,i.

If a pre-comparable material has no dual-certified QOAC-H setting on the frozen ladder, it remains in the primary paired population and is assigned R_i = 0, i.e. a competitive failure. It is never dropped from primary ratio or win-fraction statistics. A certified-only sensitivity summary is reported separately.

Primary summaries:
- median R;
- geometric mean R;
- fraction R > 1;
- fixed-seed nonparametric bootstrap 95% CI for median R;
- fixed-seed nonparametric bootstrap 95% CI for geometric mean R;
- Wilson 95% confidence interval for the win fraction.

Bootstrap seed: 20261005.
Bootstrap replicates: 20000.

## Confirmatory GO criteria

The held-out competitive claim is supported only if all are true:

1. pipeline/accounting gate passes exactly;
2. at least 95% of all 242 held-out materials have at least one dual-certified QOAC-H setting;
3. among the 241 pre-comparable materials, median R > 1 and the bootstrap 95% CI lower bound for median R is > 1;
4. QOAC-H beats the best existing baseline on at least 75% of comparable materials, and the Wilson 95% lower bound of the win fraction is > 0.50;
5. bulk and slab subgroups each separately have median R > 1 and bootstrap 95% CI lower bound > 1.

These criteria test robust competitive superiority, not equality to the very large effect observed on the 12-material tuning cohort.

No confirmatory criterion is changed after held-out execution starts.

## Secondary outcomes

Report without changing the primary decision:
- distribution of best QOAC-H CR;
- R quantiles (p10, median, p90);
- historical, Nyquist-safe and conservative errors at the selected QOAC-H point;
- density Linf/RMSE, mean-density deviation and negative-density fraction;
- encode/decode timing;
- per-codec identity of the strongest existing baseline;
- the QOAC-H outcome for mp-1038991, which lacks a certified existing comparator;
- bulk/slab effect sizes separately.

A QOAC-H reconstruction is a Hartree-specific scientific representation. Strong Hartree fidelity does not imply Bader, topology, local-density or universal field fidelity.

## Interpretation

A GO supports the statement that, on a disjoint held-out development population, the frozen operator-derived QOAC-H v0.2 design provides higher compression than the strongest certified evaluated ZFP/SZ3/SPERR baseline while preserving the specified Hartree scientific-use contract.

A NO-GO is retained as a scientific result. No post-hoc retuning on the 242 held-out materials is allowed for the same confirmatory claim.
