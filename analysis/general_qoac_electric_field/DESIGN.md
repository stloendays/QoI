# General-QOAC case 3 — electric-field operator engineering test

Freeze date: 2026-10-05

Status: prospective mechanism test. This study is not yet integrated into the active manuscript.

## Question

Does the downstream operator select a different compression geometry when the target changes from Hartree potential to Hartree electric field?

For periodic electrostatics,

    V_H(G) = 4*pi*rho(G) / |G|^2,

and

    E_H(G) = -i G V_H(G)
           = -i 4*pi G rho(G) / |G|^2.

Therefore the squared vector-field error is proportional to

    D_E^2  propto  sum_{G != 0} |delta rho(G)|^2 / |G|^2.

Under the same frozen high-rate scalar-quantization model used for QOAC-H,

    E |delta rho(G)|^2 propto Delta_G^2,

so the operator-derived first-order allocation is

    Delta_G propto |G|.

Because the existing Hermitian-orbit codec parameterizes

    Delta_G = alpha * q_G^beta,

the electric-field prediction is fixed prospectively as

    beta = 1.

This differs from:
- operator-blind spectral quantization: beta = 0;
- Hartree-potential allocation: beta = 2.

The scientific test is therefore not merely whether frequency weighting helps. It is whether the **operator-predicted exponent beta=1** outperforms both adjacent wrong geometries at matched serialized storage.

## Engineering population

Use exactly the existing 12-material QOAC-H engineering manifest:
- 6 bulk;
- 6 slab.

This is deliberate paired-operator development, not a confirmatory cohort. Reusing the same materials makes the only conceptual change the downstream operator.

No electric-field outcome was used to select these 12 materials.

## Frozen representation

Reuse the audited QOAC-H Hermitian-orbit codec without changing:
- conservative Nyquist metric;
- one canonical coefficient per Hermitian orbit;
- G=0 exact;
- shell_count = 32;
- zlib_level = 6;
- 25-point alpha ladder.

Evaluate exactly:

    beta in {0, 1, 2}

and

    alpha / ptp(rho) = logspace(1e-7, 1e1, 25).

Total planned settings:

    12 * 3 * 25 = 900.

No adaptive tuning or intermediate alpha insertion is allowed.

## Electric-field metric

For an rFFT representation, Parseval gives the exact vector electric-field energy up to constants that cancel in a relative error:

    ||E_H||_2^2 propto
        sum_G m_G |rho(G)|^2 / |G|^2,

where m_G is the rFFT multiplicity.

Primary metric:

    electric_field_error_rel_RMSE_historical

computed with the historical reciprocal-grid convention.

Nyquist-safe guardrail:

    electric_field_error_rel_RMSE_safe

computed after excluding the even-grid Nyquist planes, matching the existing safe Hartree audit convention.

No claim may rely on a mode that exists only because of the historical Nyquist representation.

## Matched-storage mechanism test

Within each material, compare beta=1 against beta=0 and beta=2 independently.

Pairs are formed by the same greedy serialized-rate matching rule used in the frozen Hartree pilot:
- distance = absolute difference in log10(compression ratio);
- maximum caliper = 0.05 dex;
- each setting used at most once;
- minimum 3 matched pairs for a material to be evaluable.

For every matched pair record

    R_10 = D_E(beta=1) / D_E(beta=0)

and

    R_12 = D_E(beta=1) / D_E(beta=2).

Material summaries are the median matched-pair ratios.

## Frozen engineering gates

### Gate A — operator-blind ablation

GO requires:
- at least 9/12 evaluable materials have median R_10 < 1;
- median across evaluable materials of median R_10 < 0.70.

### Gate B — operator-specific exponent

GO requires:
- at least 9/12 evaluable materials have median R_12 < 1;
- median across evaluable materials of median R_12 < 0.90.

This is the key generality gate. Passing it means the Hartree-specific beta=2 law is not merely a universally good low-frequency bias; the electric-field operator selects a different optimum.

### Gate C — certified-rate ablation

At the engineering certificate

    tau_E = 1e-6 relative electric-field RMSE,

select the highest-CR evaluated row for each beta.

For materials with certified rows for all three beta values, compare beta=1 against the better of beta=0 and beta=2.

GO requires:
- at least 9/12 materials favor beta=1;
- median CR ratio beta=1 / best(beta=0,beta=2) > 1.05.

Gate C is secondary to the matched-storage mechanism gates because the fixed 25-point alpha ladder is discrete.

## What happens after engineering

Only if Gates A and B pass:
1. freeze a new disjoint electric-field confirmatory cohort;
2. exclude the 12 engineering materials;
3. also exclude the 48 QOAC-H confirmatory materials so that the new operator test is not reusing the previous holdout;
4. freeze confirmatory thresholds before execution.

The confirmatory cohort is not selected or executed in this engineering workflow.

## Interpretation boundary

Passing this study supports:

> the downstream operator determines the preferred reciprocal-space error geometry, and the exponent changes from beta=2 for Hartree potential to beta=1 for Hartree electric field as predicted from the operator symbol.

It does not yet establish:
- superiority to ZFP/SZ3/SPERR for electric-field fidelity;
- a universal QOAC law for nonlinear QoIs;
- electric-field QSQ qualification across all 254 materials.

Those require separate prospective experiments.
