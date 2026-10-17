# Closed-form Hartree law on the Materials Project archive

τ_H = 1e-06: R_L = 356.038 [326.613, 394.645]; R_P = 34.999 [32.746, 37.670]; R_L/R_P = 10.173 [9.352, 11.179]; law saving = 8.474 TB.
τ_H = 0.0001: R_L = 1750.893 [1654.679, 1865.226]; R_P = 168.057 [153.382, 186.184]; R_L/R_P = 10.418 [9.622, 11.200]; law saving = 8.493 TB.
τ_H = 1e-08: R_L = 7.796 [6.166, 10.105]; R_P = 6.084 [5.139, 7.262]; R_L/R_P = 1.281 [1.202, 1.398]; law saving = 7.408 TB.

Frame: 415,289 objects and 8.4976 TB of current MP JSON bytes; the sample has 300 objects.

## All tolerance estimates

| tau_H | R_L_vs_json | R_P_vs_json | R_L_over_R_P | saving_TB_L | R_L_vs_float64 | R_L_vs_lossless | eligible_fraction_count | eligible_fraction_bytes | median_certified_stream_ratio_L_over_P |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1e-06 | 356.0380 | 34.9988 | 10.1729 | 8.4737 | 202.4718 | 178.2074 | 1.0000 | 1.0000 | 0.1023 |
| 0.0001 | 1750.8929 | 168.0566 | 10.4185 | 8.4927 | 995.6982 | 876.3730 | 1.0000 | 1.0000 | 0.1191 |
| 1e-08 | 7.7965 | 6.0841 | 1.2815 | 7.4077 | 4.4337 | 3.9024 | 0.7675 | 0.7741 | 0.2824 |

The float64 and lossless comparisons use successful/evaluable objects because §5 defines failed objects only by their current MP JSON storage; the fixed design weights and all sample rows are retained.

## Eligibility and failures

| tau_H | eligible_count_all | eligible_bytes_all | eligible_count_evaluable | eligible_bytes_evaluable | median_L_over_P | n_both |
| --- | --- | --- | --- | --- | --- | --- |
| 1e-06 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.1023 | 300.0000 |
| 0.0001 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.1191 | 300.0000 |
| 1e-08 | 0.7675 | 0.7741 | 0.7675 | 0.7741 | 0.2824 | 231.0000 |

Failure records: 0.

No failure records.

## Per-stratum results

| stratum | N_frame | n_sample | n_success | n_failed | R_L_vs_json_1e-06 | R_P_vs_json_1e-06 | eligible_count_1e-06 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D01 | 41527 | 30 | 30 | 0 | 248.5040 | 25.9808 | 30 |
| D02 | 41531 | 30 | 30 | 0 | 300.7992 | 29.6782 | 30 |
| D03 | 41529 | 30 | 30 | 0 | 314.2352 | 33.8781 | 30 |
| D04 | 41529 | 30 | 30 | 0 | 264.2727 | 26.2759 | 30 |
| D05 | 41528 | 30 | 30 | 0 | 304.3011 | 34.5842 | 30 |
| D06 | 41529 | 30 | 30 | 0 | 278.8255 | 29.3885 | 30 |
| D07 | 41529 | 30 | 30 | 0 | 317.4004 | 33.7543 | 30 |
| D08 | 41529 | 30 | 30 | 0 | 292.4190 | 34.6502 | 30 |
| D09 | 41529 | 30 | 30 | 0 | 308.5646 | 36.1262 | 30 |
| D10a | 33105 | 15 | 15 | 0 | 452.1128 | 35.3639 | 15 |
| D10b | 6741 | 10 | 10 | 0 | 665.7976 | 37.0210 | 10 |
| D10c | 1683 | 5 | 5 | 0 | 3439.0639 | 112.1202 | 5 |

## Wall time and memory per stratum

| stratum | wall_seconds_median | wall_seconds_total | peak_rss_GB_max |
| --- | --- | --- | --- |
| D01 | 55.9817 | 1713.9616 | 0.4623 |
| D02 | 45.3222 | 1403.2260 | 0.4987 |
| D03 | 59.4070 | 1817.2205 | 0.6227 |
| D04 | 84.2137 | 2356.0660 | 0.7202 |
| D05 | 91.6879 | 2692.9557 | 0.7395 |
| D06 | 111.1886 | 3311.5601 | 0.8058 |
| D07 | 138.8243 | 4278.1347 | 1.0714 |
| D08 | 166.0300 | 5086.2211 | 1.2859 |
| D09 | 174.7540 | 5321.1064 | 1.4121 |
| D10a | 315.7821 | 4773.8322 | 1.9150 |
| D10b | 488.7758 | 4971.9915 | 3.0092 |
| D10c | 1268.7005 | 6599.3655 | 8.2186 |

Bootstrap: 2,000 within-stratum resamples, `numpy.random.default_rng(20261012)`, percentile 95%; R_L, R_P and R_L/R_P use the same resample.

No object is dropped or reweighted after its outcome is known, and no pass/fail gate is applied by this aggregation script.
