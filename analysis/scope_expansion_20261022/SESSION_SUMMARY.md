# Session summary — 2026-10-21 23:50 → 2026-10-22 04:30 SGT

## Branches

- `research/scope-expansion-20261022`: everything below. The plan and timeline are in `PLAN.md`.
- `research/qoac-b4-budgeted-relaxation-20261021`: QOAC-B4.
- `paper/nc-rev5-hartree-archive-si-20261022`: SI Note 3.4 plus a SOURCE_FILES row. Audit: 0 failures,
  0 warnings. **Not merged.**

The manuscript (`paper/MANUSCRIPT.md`) is unchanged. No holdout population was used. FFCz was not repeated.

## Results

| id | question | result | file |
|---|---|---|---|
| B4 | budgeted relaxation of B3's partition correction | bound validated on the compiled binary (144/144); byte effect small (≥ 0.989×) → not carried forward | B4 branch `results/real_engineering/RESULTS.md` |
| S0 | is a magnetization block stored? | 210/210 objects; 87 with an atom ≥ 0.1 mu_B | `results/s0_spin_census/` |
| S0b | how much of the archive is it? | 300/300 objects; 52% of bytes. The published estimates store rho only. Block-only reading: Bader 2.10×, Hartree 171× | `FINDING_magnetization_block.md`, independently confirmed |
| S1 | per-atom moments as a contract | eligible 16/16 at 1e-2 mu_B; certified m costs a median 0.3% of lossless rho | `results/s1_spin_engineering/RESULTS.md` |
| S2 | whole-object archive (reference-frame m) | Bader 4.36× (4.34× with the map); Hartree law 317× (232× with the map) | `results/s2_archive_whole_object/READING.md` |
| S3 | do the charge and moment contracts compose without the map? | decoded-frame certification composes in 60/62 pairs at 1.00× bytes | `results/s3_joint_contracts_v2/RESULTS.md` |
| S4 | same question under a Hartree-law rho' | 16/16 at 1e-6 (m at 1e-2 mu_B) | `results/s4_hartree_decoded_frame/READING.md` |
| S2b | map-free Hartree archive, 1e-6 | **316× [290, 350]**; law streams reproduced within 0.016% | `results/s2b_archive_hartree_decframe/READING.md` |
| S2c | the same at 1e-4 | map-free 76×; hybrid (map where needed) **1,036×** | `results/s2c_archive_hartree_decframe_1e-4/READING.md` |
| S2d | pointwise writer, like-for-like | **34.6×**; law/pointwise **9.15×** | `results/s2d_archive_pointwise_decframe_1e-6/READING.md` |
| A0 | what the MP bucket holds | 26.1 TB, of which about 17.1 TB is volumetric | `results/a0_bucket_census/READING.md` |
| all | whole-object counterpart of every manuscript archive number | table and sentence map | `results/whole_object_estimates/TABLE.md`, `OPTION2_number_map.md` |

## Drafts for the owner

- `WS_S_SI_note_draft.md`: SI note on the spin channel.
- `results/figures/supp_fig_spin_channel_draft.*`: Supplementary Fig. Y.
- `SCOPE_V6_STORYLINE_DRAFT.md`: broader-scope storyline.
- `OPTION1_archive_wording_draft.md`: minimal fix (charge-density-only wording), plus alternative D (whole
  object).
- `WS_T_turbulence_SI_note_draft.md`: turbulence generality note.

## Decisions needed

1. **Archive claims.** Option 1 (charge-density content only), option 2 (whole served object, all numbers
   measured), or both.
2. **Spin channel.** Bring it into the paper (SI note + figure + one Methods and one Discussion sentence),
   or keep it for a follow-up.
3. **Side branch.** Merge `paper/nc-rev5-hartree-archive-si-20261022`.
4. **Turbulence generality.** Keep it out (10-03 decision) or add it as an SI note.
