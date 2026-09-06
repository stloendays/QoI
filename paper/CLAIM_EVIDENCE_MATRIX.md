# Claim–evidence matrix

Status vocabulary is restricted to **CONFIRMED**, **PROVISIONAL**, **FALSIFIED**,
**PENDING**. Words like "promising", "encouraging" or "seems to work" are not
permitted. Every claim names the data file that supports it; a claim with no
data file cannot leave PENDING.

Last updated: 2026-09-06 (master table + tight rungs complete; all statistics under Protocol A.1).

**Correction of record (2026-09-04).** An earlier statement that bulk crystals
show "0% above 1e-3" came from a 10-material pilot and is **false on the full
254-material corpus**, where 4.3% of bulk sits above 1e-3 and one bulk material
reaches 2.14e-02. The bulk/slab contrast survives as a *relative* difference of
roughly 2-3x in non-evaluable rate, not as a dichotomy. Claims 5 and 6 are
worded accordingly.

**Correction of record (2026-09-05).** The Protocol A stability probe (float32
round trip) is order-preserving and blind to the on-grid watershed's tie
resolution; it understates the stability floor by a median factor of ~8 700.
Protocol A is archived unchanged; **Protocol A.1** (`results/stability/PROTOCOL_A1.md`,
five pre-registered noise seeds, floor = max over seeds) replaces it. Every
probe-dependent number below is restated under A.1, with the archived A value
kept in brackets and marked *archived*. Codec rows of the master table are
probe-independent and unaffected.

| # | Claim | Evidence | Dataset | Figure | Status | Remaining risk |
|---|---|---|---|---|---|---|
| 1 | Pointwise error bounds do not control chemical fidelity | Full master table, A.1-admitted materials, matched nominal tolerance: SZ3's re-derived Bader error exceeds ZFP's by a per-material median **6.4x** (1e-4, n=140), **9.2x** (1e-3, n=130), **12.4x** (1e-2, n=29); SZ3 worse on 98-100 % of materials; SPERR 6.8-8.9x worse than ZFP. Bulk and slab agree | `results/honest_benchmark/rate_chemical_master.csv` (254 materials, 4627 rows) | F6 | **CONFIRMED** | The pilot's 8.9-22x is superseded by 6-12x; direction and near-universality are not in doubt |
| 2 | Fixed-basin evaluation is systematically biased | Same operating points scored both ways: fixed-basin deviation is 9-11x smaller across all codecs and both strata | `results/verify/primary_claim.jsonl`, `results/adaptive/boundary.jsonl` | F2 | **CONFIRMED** | Magnitude may shift with corpus; direction is not in doubt |
| 3 | Codec ranking reverses between the two metrics | On the full table the *best* codec at matched tolerance is ZFP under **both** metrics (fixed: 170/171 at 1e-3; resolved: 164/171); the winner changes in only 4 % (1e-3) and 2 % (1e-2) of materials. What does change is the order of the two worse codecs: the full 3-codec order differs between metrics in 44 % (1e-3) and 16 % (1e-2) of materials | `results/honest_benchmark/rate_chemical_master.csv` | F2 | **FALSIFIED** (as stated) | The 10-material pilot's "SPERR best under fixed basins, worst under re-derived" was a sampling artefact. The surviving, weaker statement — the fixed-basin metric mis-orders the non-winning codecs in a large minority of materials — is folded into claim 2 |
| 4 | Domain migration dominates tight-tolerance error | At 1e-4 the domain term is 0.00911 e against an integrand term of 0.00041 e, i.e. 100% of the total; at 1e-3 it is 65% | `results/adaptive/boundary.jsonl` (6 materials) | F3 | **PROVISIONAL** | 6 materials. Needs the representative-case matrix of Task 4 |
| 5 | Bader charge is *typically* stable for bulk crystals, but not universally | **A.1**, development bulk n=186: non-evaluable 77.4% at 1e-4, 44.6% at 1e-3, 9.7% at 1e-2 [archived A: 16.7% / 4.3% / 0.5%]. "Typically stable" holds only at the 1e-2 e contract | `results/stability/eligibility_summary_a1.csv` [archived: `results/stability/stability_floor.csv`] | F4 | **CONFIRMED** (restated) | The A wording "median floor 6e-9" is withdrawn: it was a property of the probe. Under A.1 the bulk median floor is 3.3e-04 e |
| 6 | Bader instability is markedly more common for slabs than for bulk | Under A.1 the development contrast is weak (rank effect 0.564; non-evaluable 94% vs 77% at 1e-4, 41% vs 45% at 1e-3) and **reverses externally** (0.382; ext vacuum 71% / 21% / 0% vs ext bulk 73% / 41% / 16%). [archived A: dev 0.672 / ext 0.419] | `results/stability/eligibility_summary_a1.csv` | F8 | **FALSIFIED** as a generalisation (unchanged) | Same verdict under both probes |
| 6b | Bader instability is common and not predictable from cheap proxies | **A.1**: 71-94% of every stratum non-evaluable at 1e-4, 21-45% at 1e-3, 0-16% at 1e-2; correlation of log floor with log points/atom +0.08, atom count +0.17 [archived A: 25-27% at 1e-4; +0.20 / +0.12] | `results/stability/eligibility_summary_a1.csv`, `results/stability/stability_floor_noise_seeds.csv` (319 systems x 5 seeds) | F4, F8 | **CONFIRMED** (strengthened) | None on the measurement; the floor is defined at the float32 L-inf amplitude (S4 gives amplitude sensitivity) |
| 7 | A QoI must be stability-qualified before it can serve as a fidelity contract | **A.1**: 41% of all 319 systems have no Bader charge defined to 1e-3 e; 80% not to 1e-4 e; and the qualification is not predictable by inspection [archived A: 7.2% / 23.2%] | `results/stability/PROTOCOL_A1.md`, `results/stability/eligibility_by_threshold_a1.csv` | F4, F8 | **CONFIRMED** | None |
| 8 | Lossy compression remains worthwhile over exact alternatives | Lossless: bulk f64+zstd 2.1x, f64+xz 3.0x, f32+zstd 4.6x; slab 1.1x / 1.2x / 2.2x. Lossy, **Protocol A.1, τ = 1e-2 e, best certified ratio, median [95 % CI]**: bulk SZ3 52.0x [48.0, 61.7], ZFP 30.0x [27.2, 31.7], SPERR 11.6x [10.1, 13.4]; slab SZ3 69.6x [65.9, 72.3], ZFP 40.5x [37.0, 44.9]; certified fraction 94-99 % bulk, 70-97 % slab; 18 bulk and 7 slab materials non-evaluable and reported as such | `results/baseline/lossless.jsonl`, `results/honest_benchmark/summary_a1.csv` | F7 | **CONFIRMED** | With the tight rungs (1e-7..3e-6) merged: at τ = 1e-3 e bulk SZ3 12.9x [12.0, 14.3] and ZFP 13.5x [12.8, 14.5] tie (SZ3 wins 41 % [31, 51]), both certifying 99 % of admitted materials; at 1e-4 e ZFP 7.6x > SZ3 6.3x > SPERR 4.2x, certified 100 / 86 / 90 %. The 1e-3 shortfall seen with the base ladder was ladder censoring of *admitted* materials, not codec failure |
| 9 | Boundary-aware allocation improves compression | 12 slabs, median 0.99x against uniform allocation, 17% helped, 25% hurt | `results/negative/boundary_allocation/` | S2 | **FALSIFIED** | None. Mechanism recorded: reassignment appears at boundaries but is caused by error along non-local ascent paths |
| 10 | Promolecule prior improves compression | 12 materials, median 0.47x, wins on 0% | `results/stage0/g0c_promolecule.jsonl` | S3 | **FALSIFIED** | None |
| 11 | Symmetry folding helps on slabs | 68 slabs, median 1.04x against the best generic codec, 51% win rate; 54% of systems are effectively P1 | `results/slabs/slab.jsonl` | S4 | **FALSIFIED** | Measured under the fixed-basin metric, but the result is a null and the corrected metric cannot rescue it |
| 13 | The stability probe itself must be validated: an order-preserving probe tests nothing about an order-dependent partition | float32 round trip creates a median 82 exact neighbour ties and reassigns zero voxels in 62% of systems; noise of the same or 100x smaller amplitude reassigns hundreds. Noise/f32 floor ratio median 8 700. Single-seed verdicts flip in 35/319 (1e-4), 17/319 (1e-3), 2/319 (1e-2) against the 5-seed maximum | `results/stability/probe_calibration.csv`, `results/stability/stability_floor_noise_seeds.csv` | F4 (new panel) | **CONFIRMED** | Amplitude is load-bearing for about half the materials (median 0.76 dec over two decades); stated, not hidden |
| 12 | Symmetry folding helps on bulk | Never regenerated under the corrected metric or either protocol; the in-house codec is not in the master table | `results/stage1/sz3_sperr.jsonl` (fixed-basin, void) | — | **PENDING** — will not be quoted | The algorithm track is closed; this claim is dropped from the manuscript rather than rescued |

## Retracted numbers — must not be cited

| Retracted | Why |
|---|---|
| "SZ3 leaves 200x more chemical error than ZFP" | Fixed-basin metric; the full-table figure is 6-12x |
| "SPERR ranks best under fixed basins and worst under re-derived basins" (pilot, claim 3) | 10-material sampling artefact; on 254 materials ZFP is best under both metrics |
| "SPERR is the strongest generic baseline" | Ranking reversed by the metric error |
| Any "compression ratio at equal chemical fidelity" of 130-600x | Inflated 10-20x by the fixed-basin metric |
| "Spatial error allocation is dead (bits/chemistry ratio ~1.0)" | Diagnostic used fixed basins and was blind to the dominant term |
| "Bulk float32 reaches 26x, lossy is pointless there" | Sampling bias: smallest-first ordering selected high-symmetry materials; full corpus gives 4.6x |
| Bias correction "2.08x on slabs" | Fixed-basin metric; gains largely evaporate honestly measured |
| "Bulk crystals have a median Bader stability floor of 6e-9 e" and every Protocol A non-evaluable rate | Float32 probe is order-preserving; understates the floor ~8 700x. Archived, marked PROVISIONAL / archived; A.1 values replace them |
| "BQB's 35:1 converts to about 7.8x against float64" | Wrong denominator twice over: BQB's reference is the Gaussian cube (13.167 B/value), not CHGCAR, and the ~36 B/value CHGCAR figure used included header and augmentation block. **The correct conversion is 21.3:1**, i.e. 3.01 bits per grid value. See `results/external_baselines/BASELINE_REPORT.md` |

## External baselines: closed

| Tool | Runnable here | Fair comparison | Disposition |
|---|---|---|---|
| BQB | yes (prebuilt Win64) | no — text denominator, MD-trajectory task, no L∞ target | related work; optional single-frame supplementary row, not yet run |
| den2bin | no (source-only C++) | no — no error control of any kind | related work only, excluded |

Full reasoning and the measured unit conversions: `results/external_baselines/BASELINE_REPORT.md`.
CHGCAR bytes-per-value was **measured** at 18.200, not taken from the literature.

## Algorithm track: closed

No mechanism survived under the corrected metric. The contribution of this work
is the evaluation framework, not a codec. Reopening the algorithm track requires
a gap in the evidence chain that measurement and validation cannot close.
