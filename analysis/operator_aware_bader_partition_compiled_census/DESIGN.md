# QOAC-B3 full 50-material descriptive census

Freeze date: 2026-10-05

Status: exhaustive descriptive census authorized by the successful 12-material QOAC-B3 engineering study.

This census is **not** an independent holdout experiment. All 50 analyzable materials were previously used in WP-G/WP-I and/or QOAC-B2 evidence. The purpose is to determine whether the compiled exact-partition representation has any material-level exceptions across the complete analyzable all-electron-reference population.

## Frozen representation

No B3 encoding change is allowed.

For each exact Henkelman on-grid partition map:
- encode with packed smallest-unsigned-label + zlib level 6;
- encode with run-length + zlib level 6;
- count complete headers;
- use the smaller complete serialized stream;
- require bit-exact decoded labels.

The exact-reference comparator remains:
- combined AE = AECCAR0 + AECCAR2;
- float64 Fortran-order payload;
- zlib level 6;
- fixed 32-byte header.

## Population

Exactly the 50 WP-G materials with successful finite all-electron-reference analysis.

The three published AECCAR failures remain excluded and are not silently replaced.

## Semantic equivalence

For each material:
1. run exact Henkelman Bader 1.05 using exact CHGCAR and exact combined AE reference;
2. save the exact AtIndex partition;
3. losslessly encode/decode the partition;
4. directly integrate atomic charges from the exact CHGCAR using the decoded map:

       Q_i = (1/N_grid) * sum_{r:L(r)=i} rho(r);

5. compare with Henkelman ACF charge.

The census is valid only if:
- 50/50 map streams decode exactly;
- max direct-map/Henkelman atomic-charge error <= 2e-6 e.

## Complete archive accounting

For every material, the frozen B2 kappa=4 CHGCAR bytes are imported without retuning:
- 12 development materials: the kappa=4 rows from
  analysis/operator_aware_bader_projection/results/engineering_frontier.csv;
- 38 frozen holdout materials: the rows from
  analysis/operator_aware_bader_projection_confirmatory/results/confirmatory_material.csv.

There must be exactly one B2 record per material.

Baseline exact-reference archive:

    bytes(best frozen G1 CHGCAR at tau_B=1e-3)
    + bytes(lossless combined AE).

Compiled Bader archive:

    bytes(frozen B2 kappa=4 projected CHGCAR stream)
    + bytes(lossless exact partition map).

Common structure metadata are excluded from both.

## Required descriptive outputs

Across all 50 materials report:
- exact-map decode count;
- max direct-map/Henkelman charge error;
- packed vs RLE method counts;
- lossless-AE / partition-map byte ratio: min, P05, median, P95, max;
- partition-map fraction of compiled archive;
- baseline/compiled complete-archive byte ratio: win count, min, P05, median, P95, max;
- B2 source counts (engineering vs frozen holdout).

No new GO/NO-GO performance threshold is introduced after authorization. Completeness and semantic equivalence are mandatory validity conditions.
