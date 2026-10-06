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
| `smoke_stub_bader.py` | runner smoke test with a stub Bader solver on `mp-10761` |

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
    [--shard-count N --shard-index i] [--material-id mp-...] [--base J T1 GP] [--mu 1e-6 1e-4 1e-2 1]
```

- Base codecs: `J` (QOAC-H v0.2 ladder), `T1` (truncation ladder) and `GP` (WP-G generic rows). They live in
  the registry `REGISTRY`; a new codec is added with
  `register(BaseCodec(name, candidates(ctx) -> [(param, spec)], decode(ctx, spec) -> (field, payload_bytes)))`.
- Post-processors: `none`, `uniform`, `hap:<mu>`, `ctp-uniform`, `ctp-hap:<mu>`. Every base codec gets the
  same set.
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
- Bader solves are cached per (row, stored field), so post-processors share them.
- Outputs per shard:

  | file | contents |
  |---|---|
  | `rows_*.csv` | every (row, post, stored) |
  | `bader_*.csv` | every attempt, with unprojected Bader as a control |
  | `selected_*.csv` | certified result per (material, base, post) |
  | `failures_*.csv` | failures |
  | `materials_*.csv` | runtime, HAP precompute time, kappa and Gram condition per mu |

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
