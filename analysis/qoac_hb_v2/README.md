# QOAC-HB v2 — Hartree-aware projection and certify-then-project

Code, derivation and unit tests for the next iteration of the joint Hartree + Bader contract
(`analysis/qoac_hb_joint/DESIGN.md`). No real-material experiment has been run with this code; the only
execution on a real material is the plumbing smoke test below, which uses a stub Bader solver, so its numbers
carry no scientific meaning. Frozen modules are imported unchanged:
- `operator_aware_codec_hartree_v02`
- `operator_aware_bader_fixed_partition/qoac_b_core.py`
- `run_engineering.py`
- `qoac_h_strong_baselines`
- `qoac_hb_joint`

## Contents

| file | what |
|---|---|
| `projection_v2.py` | HAP (`HartreeAwareProjector`, `hartree_multiplier_rfft`, `objective`, HAP side channel) and CTP (`certify_then_project`) |
| `DERIVATION.md` | derivation of HAP, including the explicit G = 0 elimination |
| `test_projection_v2.py` | unit tests (stdlib `unittest`) |
| `run_joint_v2.py` | runner: pluggable base codecs x post-processors |
| `codec_qoac_v03.py` | QOAC v0.3 RDO codec, copied unchanged from `research/qoac-v03-rdo-20261006` at `7ca412e` (base codec `R3`) |
| `test_codec_qoac_v03.py` | its unit tests, copied unchanged from the same commit |
| `test_runner_v2.py` | data-free runner + aggregator tests on fabricated fields (stub download, stub codecs, stub Bader) |
| `aggregate_joint_v2.py` | aggregates the shard outputs (descriptive; no gates) |
| `smoke_stub_bader.py` | runner smoke test with a stub Bader solver on `mp-10761` |
| `.github/workflows/qoac_hb_v2.yml` | CI: `workflow_dispatch` (inputs `manifest`, `mu`, `tau_bader`) or a push of the sentinel `RUN_MANIFEST` |
| `../fresh_population_20261006/P2_*_MANIFEST.csv` | fresh P2 engineering (12) and confirmatory (48) manifests, copied unchanged from `research/fresh-population-20261006` |

## Hartree-aware projection (HAP)

`c = argmin ||V_H[c]||^2/||V_H[rho_ref]||^2 + mu ||c||^2/||rho_ref||^2  s.t.  A c = t - A x`. V_H is the
historical Hartree operator (G = 0 removed). It is applied as an exact real-symmetric Fourier multiplier; the
kz = 0 and kz = Nyquist planes are symmetrized to match what `irfftn` does in the canonical function. The
solution is `c = M^-1 A^T lambda`, `(A M^-1 A^T) lambda = d`.

The G = 0 mode is eliminated explicitly. Because the regions tile the cell, mean(c) = sum(d)/N. The remaining
zero-mean part is solved with the Gram `A P M^-1 P A^T`, whose all-ones null direction is closed by a
`gamma 1 1^T` term. A final uniform pass restores floating-point closure. See `DERIVATION.md`.

Use:

```python
import projection_v2 as pv
s_h, s_rho = pv.reference_scales(rho_ref, lattice)
projs = pv.HartreeAwareProjector.build_many(labels, lattice, [pv.kappa_from_mu(mu, s_h, s_rho) for mu in mus])
y = projs[0].project(decoded, side.sums)          # reuse for every decoded candidate of this material
blob = pv.hap_side_channel_bytes(side, projs[0].kappa)  # QOAC-B1 sums + 8-byte kappa
```

The precompute costs one forward FFT per populated region and one inverse FFT per (region, mu). Applying it
to a candidate costs one FFT pair, a bincount and an (L+1)-sized triangular solve. The B_j are never stored.

Decoder information: the labels come from the exact AECCAR partition, as in B1/B2, and are not charged. The
decoder also needs t and kappa = mu s_H / s_rho. kappa is serialized, so HAP's side channel is 8 bytes larger
than the uniform one.

## CTP

`certify_then_project(field, bader_ok, projector, side_bytes)` returns `(field, extra_bytes, decision)`:
- `("unprojected", 1)` if the unprojected stream meets the Bader contract;
- otherwise the projected field with `1 + side_bytes`.

## Runner

```
python run_joint_v2.py --repo-root <repo> --frozen-root D:\Research\QoI-final4-local\frozen_repo \
    --manifest <manifest.csv> --bader <henkelman bader> --output-dir <dir> \
    [--shard-count N --shard-index i] [--material-id mp-...] [--base J T1 GP R3 GF] [--mu 1e-6 1e-4 1e-2 1] \
    [--tau-bader 1e-3 1e-4 1e-5]
```

- Base codecs: `J` (QOAC-H v0.2 ladder), `T1` (truncation ladder), `GP` (WP-G generic rows), `R3`
  (QOAC v0.3) and `GF` (fresh generic ladder). They live in the registry `REGISTRY`; a new codec is added with
  `register(BaseCodec(name, candidates(ctx) -> [(param, spec)], decode(ctx, spec) -> (field, payload_bytes)))`.
  `ctx.cache` holds per-material codec state.
- `R3`: `analyze(rho, lattice, operator="hartree_potential", prior="operator",
  reference_historical_rms=reference_hartree_rms(rho, lattice)[0], d_floor_rel=1e-3*1e-12/32)`, computed once
  per material. Six candidates `select(an, 1e-6, margin=0.995*0.995**k, polish=True)`, k = 0..5 (least to most
  conservative), stored with `encode` and reconstructed with `decode`.
- `GP` needs the frozen WP-G rows, which exist only for the 50 old materials; on any other material it has no
  candidates. `GF` needs no frozen rows: ZFP, SZ3 and SPERR through the frozen
  `external_end_to_end.codec_roundtrip` of `893f931` (the same call and decode as `GP`) at absolute tolerances
  `abs_tol / ptp(rho) = logspace(-9, -1, 25)`, 75 candidates, labelled `<CODEC>;tol_rel=<r>`.
- Post-processors: `none`, `uniform`, `hap:<mu>`, `ctp-uniform`, `ctp-hap:<mu>`. Every base codec gets the
  same set. In addition, the pseudo post-processor `hartree_only` records, per base codec, the best
  Hartree-certified unprojected row (no Bader requirement, no side channel). It is the reference for the joint
  overhead `CR_hartree_only / CR_joint`; its `selected` row is repeated for every tau_B and has `attempts = 0`.
- Bader tolerances: `--tau-bader` (default `1e-3 1e-4 1e-5` e). Selection and Bader verification of every
  (base, post) are done separately for each tau_B, so CTP decisions depend on tau_B. Decoding, Hartree metrics
  and projections are computed once per candidate, independent of tau_B; Bader solves are cached per
  (row, stored field) and shared across tau_B and post-processors, so a further tau_B only adds solves (and the
  re-decode each one needs) for rows that the looser tau_B did not reach. The Hartree certificate stays
  `TAU_H = 1e-6` (historical and Nyquist-safe) for every tau_B.
- Bytes:

  | post-processor | bytes |
  |---|---|
  | `none` | payload |
  | projection | payload + side channel (HAP: +8 bytes) |
  | CTP | payload + 1 flag byte + side channel only when projected |

- Selection per (base, post):
  - Options passing the Hartree certificate are ordered by CR. Options that store a projection must also pass
    closure <= 1e-9.
  - Each option is verified with actual Bader, up to 5 attempts. For `none`, that Bader check is the
    certification.
  - For CTP, each row offers an unprojected option and a projected option. Bader on the unprojected stream
    decides which one the encoder stores. A projected option is certified only if CTP would actually project
    that row.
- Bader solves are cached per (row, stored field), so post-processors and tau_B values share them.
- Outputs per shard:

  | file | contents |
  |---|---|
  | `rows_*.csv` | every (row, post, stored); independent of tau_B |
  | `bader_*.csv` | every attempt per tau_B (`tau_bader`), with unprojected Bader as a control |
  | `selected_*.csv` | certified result per (material, base, post, tau_B), including `hartree_only` |
  | `failures_*.csv` | failures |
  | `materials_*.csv` | runtime, HAP precompute time, kappa and Gram condition per mu, `bader_solves`, `decodes_for_bader`, `tau_bader` |

## Aggregation

```
python aggregate_joint_v2.py --manifest <manifest.csv> --shards-root <dir with *_shard_*.csv> --output-dir <dir>
```

| file | contents |
|---|---|
| `joint_v2_material.csv` | one row per (material, base, post, tau_B): certified CR, Bader attempts, Bader error, reassignment, unprojected Bader control, Hartree errors before and after post-processing, closure, density errors, bytes, `cr_ratio_vs_best_other`, `hartree_only_cr`, `joint_overhead`, and for rows storing a HAP projection the uniform-projection Hartree errors of the same row and `hap_over_uniform_hartree_{hist,safe}` |
| `joint_v2_best_post.csv` | one row per (material, base, tau_B): best joint CR over the joint post-processors, which post achieves it, its overhead and its ratio to the best other base |
| `SUMMARY.json` | per tau_B (`by_tau`), see below |
| `rows.csv.gz`, `bader_attempts.csv`, `selected.csv`, `failures.csv`, `materials.csv` | concatenated shard outputs |

`SUMMARY.json["by_tau"][tau_B]`:
- `by_base_post[base][post]`: `n_certified`, `median_cr`, `cr_ratio_vs_best_other` (`n`, `n_sole_certifier`,
  `median`); for joint posts `joint_overhead` (median of `CR_hartree_only / CR_joint` over materials where both
  certify); for CTP posts `ctp_projected_fraction` among the certified selected streams and among all Bader
  attempts; for HAP posts `hap_over_uniform_hartree` (`hist`, `safe`: n, median, max) on the certified selected
  rows that store a HAP projection.
- `best_joint_post_by_base[base]`: the same at each base's best joint post-processor per material, with the
  distribution of which post was best.
- `focus_vs_others`: for `R3`, the ratio of its joint CR to the best joint CR of the other bases with the same
  post-processor (`same_post[post]`), and at the best joint post-processor of each base (`best_post`).

`cr_ratio_vs_best_other` = certified CR / best certified CR among the other base codecs with the same
post-processor (and tau_B). It is defined where the base certifies; a sole certifier gets +inf, which enters the median
as 1e9 (the `aggregate_joint.py` convention). Failed and missing materials appear with `material_status`
FAILED / MISSING and are not certified. No pass/fail gates are applied.

CI: `.github/workflows/qoac_hb_v2.yml`, dispatched from this branch with `manifest` (repository-relative
CSV), `mu` (default `1e-4 1e-2 1`) and `tau_bader` (default `1e-3 1e-4 1e-5`). It also starts on a push to this
branch that changes `analysis/qoac_hb_v2/RUN_MANIFEST`; the first non-empty, non-`#` line of that file is the
manifest path, and `mu` / `tau_bader` take their defaults. This allows a run without the workflow being on
the default branch. The sentinel is not committed here. It runs 19 hash shards (`shard_for`) with the frozen environment and
Henkelman Bader build of `qoac_hb_joint.yml`, then commits the aggregate to
`analysis/qoac_hb_v2/results/<manifest stem>/`.

## Test results

`python test_projection_v2.py`: 11 tests, all pass (about 1-3 s). The synthetic fields are periodic and use
random Voronoi partitions with 4-6 regions on triclinic and hexagonal cells. The grids are 8x6x10, 7x9x6 and
6x6x5 (even and odd sizes).

1. Region sums are restored to scaled relative error <= 1e-12 for mu in {1e-6, 1e-3, 1, 1e3}.
2. As mu runs over 1e2 ... 1e10, the relative difference from the uniform correction decreases monotonically
   to < 1e-7.
3. J(c_HAP) <= J(c_uniform) and ||V_H[c_HAP]|| <= ||V_H[c_uniform]|| for every case. J also does not decrease
   under feasible perturbations. Measured ratio ||V_H[c_HAP]|| / ||V_H[c_uniform]||:

   | mu | min | median | max |
   |---|---|---|---|
   | 1e-6 | 0.088 | 0.134 | 0.272 |
   | 1e-3 | 0.088 | 0.134 | 0.272 |
   | 1 | 0.109 | 0.147 | 0.294 |
   | 1e3 | 0.642 | 0.747 | 0.944 |

4. A dense KKT solve, with H built column by column from the canonical Hartree function, agrees with HAP to
   1e-9 relative.

Additional tests:
- the multiplier reproduces `hartree_potential_from_field` to 1e-12, and H is symmetric;
- the G = 0 split matches the literal Gram `A M^-1 A^T`;
- mu = 0 is well posed;
- empty regions are ignored;
- the HAP side channel round-trips;
- CTP decisions and byte counts are correct.

`python -m unittest test_codec_qoac_v03.py` (copied location): 2 tests, both pass (about 3 s). The copied
codec imports `codec_qoac_h_v02` from `analysis/operator_aware_codec_hartree_v02/` with its original
`sys.path` line, and inside the runner it resolves to the same module object as `pv.qoac`.

`python -m unittest test_runner_v2.py`: 15 tests, all pass (about 6 s; numpy and pandas only, no download, no
Bader binary). Three fabricated 16x16x18 densities on a triclinic cell run through `run_joint_v2.main`
(2 shards, bases J, GF, R3, GP, mu {1e-4, 1}, tau_B {1e-3, 1e-4, 1e-5}), with stubs for the download, the
CHGCAR/AECCAR parsing, `codec_roundtrip` (a uniform quantizer with |error| <= abs_tol that accepts only zfp,
sz3 and sperr) and Bader (octant stub, charges scaled so that tau_B is decisive). The aggregator then runs on the
shard outputs. Checked:
- GF has 75 candidates at `ptp * logspace(-9, -1, 25)` and uses GP's decode; GP has 0 candidates on new
  materials; candidate and row counts; closure of every stored projection;
- one `selected` row per (material, base, post incl. `hartree_only`, tau_B); `hartree_only` is the best
  Hartree-passing `none` row and is never below the certified `none` CR;
- for every attempt: CTP decision = (unprojected Bader error <= tau_B and no reassignment); certified rows meet
  tau_B; for non-CTP posts a stricter tau_B never selects a larger CR; the fixture has a CTP decision that
  changes with tau_B;
- decodes = one per candidate + one per new Bader solve at most; Bader solves equal the distinct (row, stored)
  pairs, i.e. nothing is recomputed for a further tau_B;
- aggregate counts, median CR, joint overhead, CTP projected fraction, R3 best-post ratio and HAP / uniform
  Hartree ratios recomputed independently from the shard outputs; no gates in `SUMMARY.json`;
- `--tau-bader` default and rejection of 0, NaN and duplicates.

## Runtime (fabricated field, real codecs, stub Bader)

`process` on a fabricated 64x64x80 density (327,680 points, the size of mp-10761) with the real frozen
`codec_roundtrip` (zfpy 1.0.1, pysz 1.0.3, hdf5plugin 7.0.0), the stub Bader, mu {1e-4, 1e-2, 1} and
tau_B {1e-3, 1e-4, 1e-5}, on a 4-core cloud container:

| bases | candidates | total | decode | projections |
|---|---|---|---|---|
| J, T1, GF, R3, GP | 331 (GP 0) | 183 s | 29 s | 1,324 in 28.5 s |
| GF only | 75 | 39 s | 4.5 s | 300 in 6.4 s |

The rest is Hartree and closure metrics (5 Hartree evaluations per candidate with 3 mu). Per material the
cost is about 0.55 s per candidate at 327,680 points, i.e. linear in candidates x (2 + n_mu) and
O(N log N) in grid points; it does not depend on the number of tau_B. Real Henkelman Bader adds one solve
per distinct (row, stored field) verified; a further tau_B adds solves only for rows the looser tau_B did not
reach (at most `MAX_ATTEMPTS` x 2 per (base, post) per tau_B).

## Smoke test (stub Bader)

```
python smoke_stub_bader.py --frozen-root D:\Research\QoI-final4-local\frozen_repo --output-dir <dir>
```

The stub labels are octants and the stub charges are octant sums. Result on `mp-10761` (FeTe, 64x64x80 =
327,680 points; mu in {1e-6, 1e-2, 1}):

| item | value |
|---|---|
| status | SUCCESS, 0 failures |
| candidates | 270 (J 25, T1 225, GP 20) |
| rows | 3,510 (= 270 x 13 (post, stored) combinations) |
| `selected` rows | 27 (= 3 bases x 9 post-processors) |

This table predates GF, R3, `hartree_only` and `--tau-bader`; `smoke_stub_bader.py` now expects all five
bases and one `selected` row per (base, post incl. `hartree_only`, tau_B), and has not been re-run (it needs
the material download).
| stub Bader solves | 17 |
| runtime per material | 284 s on this laptop, almost all of it decoding and Hartree metrics |
| HAP precompute | 0.55 s for 3 mu |
| projections | 1,080 projections (uniform + 3 HAP) in 42 s |

The certified counts in this run are an artefact of the stub and are not reported. With real Henkelman Bader,
each new (row, stored field) adds one solve.

## Numerical notes

- **Conditioning.** The literal Gram A M^-1 A^T has a rank-one (s_rho/mu) n n^T / N term from the G = 0
  mode, so it becomes ill-conditioned as mu -> 0. That term is removed analytically. The remaining Jacobi-scaled
  Gram has condition numbers of 15-21 on mp-10761 for mu = 1e-6 ... 1, so small mu is not a numerical problem
  for this partition. Very fragmented partitions (many tiny basins) can still raise the condition number of
  G_perp. The runner records `gram_cond[mu]` for every material, and the final uniform pass guarantees
  closure regardless.
- **Memory.** The precompute holds:
  - the int64 labels: 8 bytes per grid point;
  - m^2: 4 bytes per point (half grid);
  - one inverse multiplier per mu: 4 bytes per point each;
  - one complex half-grid FFT and one real field at a time: about 24 bytes per point.

  That is roughly (36 + 4 n_mu) x N bytes, for example about 0.4 GB at 200^3 with 4 mu. The B_j are never
  stored, so memory does not scale with the number of basins. Runtime does: precompute FFTs scale as
  (L+1)(1 + n_mu).
- The runner keeps at most 4 decoded fields (LRU) during Bader verification.
- The first smoke attempt hit `MemoryError` in 3 of 270 decodes while the whole machine had 1.5 GB of
  physical memory free (other sessions were running). The rerun had 0 failures. Production runs belong on
  the cluster.
- HAP minimizes the historical Hartree norm only. The Nyquist-safe metric is still certified separately, as
  before.
