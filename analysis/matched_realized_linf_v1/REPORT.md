# Matched realized-L∞ comparison — V1

This analysis compares codecs within the **same material** after matching on `log10(realized_Linf)`. 
Primary caliper: **0.10 dex** (maximum realized-L∞ mismatch ≈ **1.259×**). 
Matching is without replacement. Uncertainty intervals bootstrap **materials**, not rows.

## Detected schema

- usable rows: **6343**
- material: `material_id`; codec: `codec`; realized L∞: `realized_Linf`
- nominal: `nominal_tolerance_absolute`
- Bader error columns: `Bader_error_fixed_e`, `Bader_error_resolved_e`
- compression ratio: `compression_ratio`; bits/value: `bits_per_value`

## Match quality at the primary 0.10-dex caliper

| pair | matched pairs | materials | median |Δ log10 L∞| | p95 |Δ log10 L∞| | median larger/smaller L∞ |
|---|---:|---:|---:|---:|---:|
| zfp_vs_sz3 | 457 | 214 | 0.055962 | 0.09642 | 1.1375× |
| zfp_vs_sperr | 465 | 206 | 0.055252 | 0.096651 | 1.1357× |
| sz3_vs_sperr | 1848 | 254 | 4.6875e-06 | 0.00047988 | 1× |

## Equal-nominal baseline

| pair | pairs | materials | median realized L∞ A/B | median |Δ log10 L∞| |
|---|---:|---:|---:|---:|
| zfp_vs_sz3 | 1936 | 254 | 0.17025× | 0.76892 |
| zfp_vs_sperr | 1952 | 254 | 0.16952× | 0.77077 |
| sz3_vs_sperr | 1848 | 254 | 1× | 4.6875e-06 |

## Effects after matching realized L∞

For positive-valued metrics, `effect` is the median across materials of the within-material median **A/B ratio**. 
Thus values below 1 mean codec A is lower than codec B after controlling realized L∞. Certification effects are A−B rate differences among jointly A.1-eligible pairs when the eligibility flag exists.

| pair | metric | materials | effect | 95% material-bootstrap CI |
|---|---|---:|---:|---:|
| zfp_vs_sz3 | Bader_error_fixed_e | 214 | 0.05668 | [0.052033, 0.06061] |
| zfp_vs_sz3 | Bader_error_resolved_e | 214 | 0.55745 | [0.52505, 0.59838] |
| zfp_vs_sz3 | compression_ratio | 214 | 0.32552 | [0.31212, 0.33943] |
| zfp_vs_sz3 | bits_per_value | 214 | 3.072 | [2.9461, 3.2038] |
| zfp_vs_sz3 | certified_at_0.0001 | both eligible_A1_at_0.0001=TRUE | 42 | 0.026984 | [0.0079365, 0.050794] |
| zfp_vs_sz3 | certified_at_0.0001_ignoring_eligibility | 214 | 0.005296 | [0.00093458, 0.010592] |
| zfp_vs_sz3 | certified_at_0.001 | both eligible_A1_at_0.001=TRUE | 128 | 0.034375 | [0.0096354, 0.058854] |
| zfp_vs_sz3 | certified_at_0.001_ignoring_eligibility | 214 | 0.021729 | [0.0065421, 0.038707] |
| zfp_vs_sz3 | certified_at_0.01 | both eligible_A1_at_0.01=TRUE | 200 | 0.14867 | [0.10916, 0.1895] |
| zfp_vs_sz3 | certified_at_0.01_ignoring_eligibility | 214 | 0.14984 | [0.11254, 0.18988] |
| zfp_vs_sperr | Bader_error_fixed_e | 206 | 0.70897 | [0.66546, 0.80121] |
| zfp_vs_sperr | Bader_error_resolved_e | 206 | 0.60075 | [0.53386, 0.6618] |
| zfp_vs_sperr | compression_ratio | 206 | 2.6687 | [2.524, 2.7577] |
| zfp_vs_sperr | bits_per_value | 206 | 0.37472 | [0.36262, 0.39619] |
| zfp_vs_sperr | certified_at_0.0001 | both eligible_A1_at_0.0001=TRUE | 42 | 0.026984 | [0.0047619, 0.055595] |
| zfp_vs_sperr | certified_at_0.0001_ignoring_eligibility | 206 | 0.0055016 | [0.00097087, 0.011974] |
| zfp_vs_sperr | certified_at_0.001 | both eligible_A1_at_0.001=TRUE | 124 | 0.015457 | [-0.0013441, 0.034274] |
| zfp_vs_sperr | certified_at_0.001_ignoring_eligibility | 206 | 0.0093042 | [-0.0020227, 0.021036] |
| zfp_vs_sperr | certified_at_0.01 | both eligible_A1_at_0.01=TRUE | 193 | 0.16986 | [0.12806, 0.2133] |
| zfp_vs_sperr | certified_at_0.01_ignoring_eligibility | 206 | 0.16561 | [0.12298, 0.20874] |
| sz3_vs_sperr | Bader_error_fixed_e | 254 | 10.775 | [10.115, 11.418] |
| sz3_vs_sperr | Bader_error_resolved_e | 254 | 1.0325 | [0.97624, 1.0717] |
| sz3_vs_sperr | compression_ratio | 254 | 3.5819 | [3.3481, 3.8164] |
| sz3_vs_sperr | bits_per_value | 254 | 0.27918 | [0.26203, 0.29867] |
| sz3_vs_sperr | certified_at_0.0001 | both eligible_A1_at_0.0001=TRUE | 46 | -0.033262 | [-0.059976, -0.0077178] |
| sz3_vs_sperr | certified_at_0.0001_ignoring_eligibility | 254 | -0.010408 | [-0.017172, -0.0043113] |
| sz3_vs_sperr | certified_at_0.001 | both eligible_A1_at_0.001=TRUE | 143 | -0.048387 | [-0.065666, -0.029938] |
| sz3_vs_sperr | certified_at_0.001_ignoring_eligibility | 254 | -0.030077 | [-0.040949, -0.019769] |
| sz3_vs_sperr | certified_at_0.01 | both eligible_A1_at_0.01=TRUE | 229 | -0.014821 | [-0.035922, 0.0065709] |
| sz3_vs_sperr | certified_at_0.01_ignoring_eligibility | 254 | -0.014215 | [-0.034168, 0.004387] |

## Sensitivity

The same analysis is repeated at 0.05, 0.10, 0.20 and 0.30 dex. A codec effect should not be interpreted as robust if its sign/direction changes materially with the caliper or if common support collapses at tighter calipers.

## Interpretation rule

- If a codec advantage seen at equal nominal tolerance shrinks toward an A/B ratio of 1 after realized-L∞ matching, the nominal-tolerance result was largely a **realized-distortion confound**.
- If a substantial codec effect persists at tightly matched realized L∞, then a scalar L∞ magnitude is insufficient; **error geometry / spatial structure** is implicated.

