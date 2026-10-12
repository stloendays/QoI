# Self-contained joint Hartree + Bader storage on the P2 confirmatory crystals — frozen protocol

Freeze date: 2026-10-12. Branch `research/hb-selfcontained-bytes-20261012`, created from
`paper/nc-scientific-audit-20261009` at `a5bf0ce`. This protocol is committed and pushed before any label map of any P2
confirmatory material is computed for this work item. After the run starts, only infrastructure may change, and every
such change goes into `DEVIATIONS.md` before the rerun.

## 1. Question

The joint contract of the HB v2 confirmation (`analysis/qoac_hb_v2`, protocol `8a784a4`, results
`analysis/qoac_hb_v2/results/P2_CONFIRMATORY_MANIFEST/`) integrates the charge density over the Bader basins of the
exact all-electron reference AECCAR0 + AECCAR2. Its compression ratios count the compressed charge stream (payload,
side channel, flag) and not the partition. This item measures the stored size when the partition travels with the
stream, so that the archive is self-contained:

stored bytes = compressed charge-stream bytes + lossless basin-label map bytes.

It is a byte accounting on the 48 confirmed materials. It has no pass/fail criterion.

## 2. Label map

For each material:

1. Download CHGCAR, AECCAR0 and AECCAR2 exactly as `run_joint_v2.process` does (`b1.fetch` of the manifest URL and of
   `aeccar0s/<task_id>.json.gz`, `aeccar2s/<task_id>.json.gz`), with the same validity checks.
2. Run Henkelman Bader 1.05, built from `mechanism/independent_bader_20260908/reference_source` as in
   `.github/workflows/qoac_hb_v2.yml`, on the exact CHGCAR with `-b ongrid -vac 0.001 -ref <AECCAR0 + AECCAR2>
   -p atom_index`. The atom-index map it writes is the partition label map L (one integer per voxel, the owning atom;
   vacuum voxels keep the binary's own label).
3. **Stored label bytes (primary):** `len(lzma.compress(L.astype("<u2").tobytes(order="C"), preset=9 | lzma.PRESET_EXTREME))`
   plus a fixed 16-byte header (grid shape as three uint32 and the atom count as uint32). This is an actual,
   decodable stream.
4. **Context-model estimate (secondary, descriptive):** `ctx_bytes` of `analysis/qoac_b3_design/b3_correct.label_map_cost(L)`,
   the ideal adaptive-context code length used in Supplementary Note 3. Reported, never used in the primary metric.

**Checks, per material (a failure is recorded, not hidden):**
- **Round trip.** Decompressing the stored stream returns L exactly.
- **Charges from the stored labels.** Per-atom charges obtained by summing the exact CHGCAR over the voxels of each
  label of the decoded L and dividing by the voxel count, exactly as the binary does, match the binary's `ACF.dat`
  CHARGE column within 1e-5 e for every atom.

## 3. Charge-stream bytes

From the committed `analysis/qoac_hb_v2/results/P2_CONFIRMATORY_MANIFEST/joint_v2_best_post.csv` (commit `4340767`;
SHA-256 of the committed bytes `d740c09a906a85f351f06c9adf8845e3261d64cc834171f5cf9b053caf1a307f`) and `materials.csv`
(SHA-256 `e302831dc8c133dc674c21581bc5c759dc994c4baf481cdaa5eb7307628da73b`), checked by the workflow:

- `raw_bytes` per material is the float64 grid size (`materials.csv`).
- For each material, base b in {R3, J, T1, GF, GP} and tau_B in {1e-3, 1e-4, 1e-5} e, the joint stream bytes are
  S(b, tau_B) = round(raw_bytes / best_joint_cr). A row with no certified joint stream stays uncertified.
- The Hartree-only R3 stream bytes are S_H = round(raw_bytes / hartree_only_cr) of the R3 rows.

No stream is recompressed in this item.

## 4. Metrics (per material, then medians)

With L_m the primary stored label bytes of material m:

- **Self-contained joint CR:** CR_sc(b, tau_B) = raw_bytes / (S(b, tau_B) + L_m).
- **Self-contained overhead of R3:** O_sc(tau_B) = (S(R3, tau_B) + L_m) / S_H, the stored size of the self-contained
  joint archive relative to the Hartree-only stream.
- **Partition share:** L_m / (S(R3, tau_B) + L_m).
- **Self-contained utility:** U_sc(tau_B) = CR_sc(R3, tau_B) / max over the other bases b' of CR_sc(b', tau_B), the
  same "best other base" rule as `aggregate_joint_v2.ratio_vs_best_other`; reported with the number of materials in
  which R3 is highest and the minimum.
- **Versus the best pointwise codec:** CR_sc(R3, tau_B) / CR_sc(GF, tau_B).

Medians over the 48 materials with bootstrap 95% CIs (10,000 resamples, seed 20261012), at each tau_B; tau_B = 1e-4 e
is the reporting tolerance, as in the HB v2 confirmation. Also reported: median, minimum and maximum L_m (primary and
context estimate), and the check counts of section 2.

## 5. Population and code

**Population.** The 48 materials of `analysis/fresh_population_20261006/P2_CONFIRMATORY_MANIFEST.csv` (commit
`2739b93`; SHA-256 of the committed bytes `361202189512883931c90a9fe62d7cb48fd4f7294a55ae019d781c7c89aafab5`, checked by
the workflow). Every downloaded object must pass the same checks as in the HB v2 run.

**Code reused unmodified** (imported, not copied):

| file | last commit | SHA-256 (committed bytes) |
|---|---|---|
| `analysis/qoac_hb_v2/run_joint_v2.py` | `77caf5d` | `7527629d56f41da21b88eb8f5967550619ab56a317c80ac622b53ad9c69b51aa` |
| `analysis/operator_aware_bader_fixed_partition/run_engineering.py` | `3c11ccc` | `56004e8af05777bbf0bd44be3347c4bad5283d5c93aa30698e898896bd4e5d75` |
| `analysis/qoac_b3_design/b3_correct.py` | `0c87360` | `2eb51e8db2569557a4899513f13fb814d6ca390e4f91e74521ada70b02f7c3eb` |

**New code** in this directory: `run_selfcontained.py` (per-material label map, checks and bytes), `aggregate_selfcontained.py`
(section 4), `test_selfcontained.py` (unit tests: header and round trip on synthetic maps; charge summation against a
hand-computed case; CR arithmetic on a two-material table). Workflow `.github/workflows/hb_selfcontained_bytes.yml`,
started by a push to this branch that changes `analysis/hb_selfcontained_bytes_20261012/RUN_SENTINEL`, or by
`workflow_dispatch` from this branch. Results are committed to `results/`.

**Smoke tests** before the run may use only the P2 engineering manifest
(`analysis/fresh_population_20261006/P2_ENGINEERING_MANIFEST.csv`), whose label maps are already reported in
Supplementary Note 3.

## 6. Reporting

`RESULTS.md` reports the numbers of section 4 at all three tau_B, the label-map sizes and the check counts. The
manuscript uses the tau_B = 1e-4 e values. No material is excluded after the run; a material whose checks fail is
reported with its failure and enters the medians with its stored bytes only if both checks pass, otherwise it is listed
as unaccounted.
