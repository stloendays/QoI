<!-- QSQ_RESEARCH_AUDIT_INTEGRATED -->
# Claim–evidence matrix

> **Research interpretation superseded in part (2026-09-11).** The common-ladder and reused-seed audits require a stronger research programme, not just submission assembly. Full-record 97.2%/95.5% are historical ladder-dependent fractions, not causal misattribution estimates. Common-base values are 83.2%/56.5%; numerical agreement remains defined even when the reference fails QSQ. The authoritative next-step plan is `paper/RESEARCH_UPGRADE_PLAN.md`; executed evidence is `analysis/research_upgrade/REPORT.md`. Older quantitative claims below retain their original data scope.


Status vocabulary is restricted to **CONFIRMED**, **PROVISIONAL**, **FALSIFIED**,
**PENDING**. Words like "promising", "encouraging" or "seems to work" are not
permitted. Every claim names the data file that supports it; a claim with no
data file cannot leave PENDING.

Last updated: 2026-09-11 (Claim 14 added after the frozen binary-to-three-state certifiability audit; Claim 1 remains restated after within-material matching on realized L∞).

**Reader-facing terminology.** The operative qualification framework is **QoI Stability Qualification (QSQ)**. The superseded order-preserving test is the **archived float32 probe**. Historical repository identifiers such as `Protocol A`, `Protocol A.1`, and `_A1` are retained only in paths and provenance records.

**Correction of record (2026-09-04).** An earlier statement that bulk crystals
show "0% above 1e-3" came from a 10-material pilot and is **false on the full
254-material corpus**, where 4.3% of bulk sits above 1e-3 and one bulk material
reaches 2.14e-02. The bulk/slab contrast survives as a *relative* difference of
roughly 2-3x in non-evaluable rate, not as a dichotomy. Claims 5 and 6 are
worded accordingly.

**Correction of record (2026-09-05; submission audit refreshed 2026-09-11).** The archived float32 stability probe is order-preserving and blind to the on-grid basin-assignment failure channel. It remains frozen as provenance. **QSQ** uses five pre-registered non-order-preserving noise seeds and defines the floor as the maximum response over seeds. In the current formal paired comparison of all 254 development materials, the operative QSQ floor is a median of approximately **1.6×10^4** times the archived float32-probe floor. The older ~8,700× intermediate summary is superseded for submission wording. Every probe-dependent current claim below is stated under QSQ; archived values are retained only when they document the correction of record. Codec rows of the master table are probe-independent and unaffected.

**Correction of record (2026-09-07).** Equal nominal tolerance is not equal
pointwise distortion across codecs. At the same requested tolerance ZFP realizes
a median L∞ only 0.170x that of SZ3 and 0.170x that of SPERR, while SZ3/SPERR is
1.00x. The earlier 6–12x ZFP/SZ3 resolved-Bader gap at matched nominal tolerance
therefore mixes realized-distortion magnitude with error-field structure. Claim 1
is restated using within-material matching on `realized_Linf`; the matched-nominal
numbers remain descriptive but are no longer used as causal evidence.

**Benchmark-validity audit (2026-09-11).** Binary Bader pass/fail labels were re-audited at the material–codec level under frozen QSQ eligibility semantics. The audit does not change any reconstruction row, threshold, or stability output; it changes how an outcome may be scientifically labelled. Claim 14 records the resulting reclassification and is the primary Figure 3 evidence.

| # | Claim | Evidence | Dataset | Figure | Status | Remaining risk |
|---|---|---|---|---|---|---|
| 1 | Scalar pointwise L∞ magnitude does not determine chemical fidelity | Equal nominal tolerance is confounded: ZFP/SZ3 realized-L∞ ratio **0.170x**, ZFP/SPERR **0.170x**, SZ3/SPERR **1.00x**. After within-material matching on `log10(realized_linf)` (primary 0.10-dex caliper), re-derived Bader error remains **0.557x** for ZFP/SZ3 (95% material-bootstrap CI 0.525–0.598), **0.601x** for ZFP/SPERR (0.534–0.662), and **1.033x** for SZ3/SPERR (0.976–1.072). The ZFP residual remains ~0.56–0.60x from 0.05–0.30 dex. At τ=0.01 e among jointly QSQ-eligible pairs, ZFP certification exceeds SZ3 by **+14.9 pp** and SPERR by **+17.0 pp** at the primary caliper | `analysis/matched_realized_linf_v1/equal_nominal_diagnostics.csv`, `analysis/matched_realized_linf_v1/matched_effects_summary.csv`, `analysis/matched_realized_linf_v1/matched_pairs_primary_0p10dex.csv` | F6 | **CONFIRMED** (restated) | Matching controls the scalar L∞ magnitude, not every norm or spatial statistic of the error field. The residual therefore supports an error-*structure* contribution beyond L∞, but should not be attributed to one specific geometric statistic without further decomposition |
| 2 | Fixed-basin evaluation is systematically biased | Same operating points scored both ways: fixed-basin deviation is 9-11x smaller across all codecs and both strata | `results/verify/primary_claim.jsonl`, `results/adaptive/boundary.jsonl` | F5 | **CONFIRMED** | Magnitude may shift with corpus; direction is not in doubt |
| 3 | Codec ranking reverses between the two metrics | On the full table the *best* codec at matched tolerance is ZFP under **both** metrics (fixed: 170/171 at 1e-3; resolved: 164/171); the winner changes in only 4% (1e-3) and 2% (1e-2) of materials. What does change is the order of the two worse codecs: the full 3-codec order differs between metrics in 44% (1e-3) and 16% (1e-2) of materials | `results/honest_benchmark/rate_chemical_master.csv` | F5 | **FALSIFIED** (as stated) | The 10-material pilot's "SPERR best under fixed basins, worst under re-derived" was a sampling artefact. The surviving, weaker statement — the fixed-basin metric mis-orders the non-winning codecs in a large minority of materials — is folded into claim 2 |
| 4 | Domain migration dominates tight-tolerance error | At 1e-4 the domain term is 0.00911 e against an integrand term of 0.00041 e, i.e. 100% of the total; at 1e-3 it is 65% | `results/adaptive/boundary.jsonl` (6 materials) | F5 | **PROVISIONAL** | 6 materials in this original diagnostic; representative-case matrix is the stronger current mechanism evidence |
| 5 | Bader charge is *typically* stable for bulk crystals, but not universally | **QSQ**, development bulk n=186: non-evaluable 77.4% at 1e-4, 44.6% at 1e-3, 9.7% at 1e-2 [archived float32 probe: 16.7% / 4.3% / 0.5%]. "Typically stable" holds only at the 1e-2 e contract | `stability/eligibility_summary_A1.csv` [archived: `results/stability/stability_floor.csv`] | F4 | **CONFIRMED** (restated) | The archived wording "median floor 6e-9" is withdrawn: it was a property of the probe. Under QSQ the development-bulk median floor is 6.729e-04 e |
| 6 | Bader instability is markedly more common for slabs than for bulk | Under QSQ the development contrast is weak (rank effect 0.564; non-evaluable 94% vs 77% at 1e-4, 41% vs 45% at 1e-3) and **reverses externally** (0.382; ext vacuum 71% / 21% / 0% vs ext bulk 73% / 41% / 16%). [archived float32 probe: dev 0.672 / ext 0.419] | `stability/eligibility_summary_A1.csv` | F7 | **FALSIFIED** as a generalisation (unchanged) | Same verdict under both probes |
| 6b | Bader instability is common and not predictable from cheap proxies | **QSQ**: 71-94% of every stratum non-evaluable at 1e-4, 21-45% at 1e-3, 0-16% at 1e-2; correlation of log floor with log points/atom +0.08, atom count +0.17 [archived float32 probe: 25-27% at 1e-4; +0.20 / +0.12] | `stability/eligibility_summary_A1.csv`, `stability/stability_floor_A1_per_seed.csv` (319 systems x 5 seeds) | F4, F7 | **CONFIRMED** (strengthened) | None on the measurement; the floor is defined at the float32 L-inf amplitude (S7 gives amplitude sensitivity) |
| 7 | Reference sensitivity and fixed-pipeline numerical agreement are distinct assessment targets | Frozen QSQ screen fractions remain measured; they do not establish that fixed-reference Bader comparisons are undefined. An exact reconstruction can reproduce a sensitive reference. | `paper/ROBUST_FIDELITY_FOUNDATIONS.md`; `stability/eligibility_by_threshold_A1.csv` | F3/F4 with revised scope | **CONFIRMED** for the stated distinction | Finite-seed acceptance is not a universal stability certificate |
| 8 | Lossy compression remains worthwhile over exact alternatives | Lossless: bulk f64+zstd 2.1x, f64+xz 3.0x, f32+zstd 4.6x; slab 1.1x / 1.2x / 2.2x. Lossy, **QSQ, τ = 1e-2 e, best certified ratio, median [95% CI]** from the current frozen summary: bulk SZ3 51.8x [47.7, 60.3], ZFP 30.0x [27.1, 31.9], SPERR 11.5x [10.1, 13.2]; slab SZ3 67.8x [59.6, 70.6], ZFP 40.5x [35.8, 44.9], SPERR 8.1x [7.7, 8.6]; certified fractions 95.2%/98.8%/95.8% for bulk SZ3/ZFP/SPERR and 77.0%/96.7%/77.0% for slab SZ3/ZFP/SPERR; 18 bulk and 7 slab materials non-evaluable and reported as such | `results/baseline/lossless.jsonl`, `benchmark/summary_a1.csv` | F7 | **CONFIRMED** | With tight rungs merged: at τ=1e-3 e bulk SZ3 12.9x [12.0,14.3] and ZFP 13.5x [12.8,14.5] tie; at 1e-4 e ZFP 7.6x > SZ3 6.3x > SPERR 4.2x. These are among admitted materials only |
| 9 | Boundary-aware allocation improves compression | 12 slabs, median 0.99x against uniform allocation, 17% helped, 25% hurt | `results/negative/boundary_allocation/` | S7 | **FALSIFIED** | None. Mechanism recorded: reassignment appears at boundaries but is caused by error along non-local ascent paths |
| 10 | Promolecule prior improves compression | 12 materials, median 0.47x, wins on 0% | `results/stage0/g0c_promolecule.jsonl` | S8 | **FALSIFIED** | None |
| 11 | Symmetry folding helps on slabs | 68 slabs, median 1.04x against the best generic codec, 51% win rate; 54% of systems are effectively P1 | `results/slabs/slab.jsonl` | S8 | **FALSIFIED** | Measured under the fixed-basin metric, but the result is a null and the corrected metric cannot rescue it |
| 12 | Symmetry folding helps on bulk | Never regenerated under the corrected metric or either stability probe; the in-house codec is not in the master table | `results/stage1/sz3_sperr.jsonl` (fixed-basin, void) | — | **PENDING** — will not be quoted | The algorithm track is closed; this claim is dropped from the manuscript rather than rescued |
| 13 | The stability probe itself must be validated: an order-preserving probe tests nothing about an order-dependent partition | In the 18-material pre-freeze calibration, the archived float32 round trip creates a median 82 exact neighbour ties and reassigns zero voxels in 9/18 systems, whereas same-amplitude primary-seed QSQ noise creates no exact ties and reassigns zero voxels in only 2/18. In the formal 254-material paired development comparison, the five-seed QSQ/archived-floor median shift is ~1.6×10^4. Primary-seed verdicts differ from the five-seed maximum in 35/319 (1e-4), 17/319 (1e-3), 2/319 (1e-2) | `stability/probe_calibration.csv`, `stability/stability_floor_A1_per_seed.csv` | F4 | **CONFIRMED** | Amplitude is load-bearing for about half the materials (median 0.76 dec over two decades); stated, not hidden |
| 14 | Full-record reclassification is strongly ladder-design-dependent | Full-record 97.2%/95.5%/56.5% reproduce, but common-base fractions are 83.2%/56.5%/51.3%; 214 added 1e-3 e passes all belong to the eligible group. Causal misattribution interpretation withdrawn. | `analysis/research_upgrade/ladder_summary.csv`; `analysis/research_upgrade/ladder_transitions.csv` | F3 historical full record | **CONFIRMED** for the audited design dependence | Complete a uniform tight ladder; report rejection prevalence and validate held-out usefulness |

## Retracted numbers — must not be cited

| Retracted | Why |
|---|---|
| "SZ3 leaves 200x more chemical error than ZFP" | Fixed-basin metric; the full-table figure is much smaller |
| "The 6–12x matched-nominal ZFP/SZ3 resolved-Bader gap directly measures codec error geometry" | Equal nominal tolerance gives strongly unequal realized L∞; ZFP realizes ~0.17x the perturbation of SZ3/SPERR. The matched-realized residual is ~1.7–1.8x in the inverse SZ3/ZFP direction and is the appropriate evidence for structure beyond scalar L∞ |
| "SPERR ranks best under fixed basins and worst under re-derived basins" (pilot, claim 3) | 10-material sampling artefact; on 254 materials ZFP is best under both metrics |
| "SPERR is the strongest generic baseline" | Ranking reversed by the metric error |
| Any "compression ratio at equal chemical fidelity" of 130-600x | Inflated 10-20x by the fixed-basin metric |
| "Spatial error allocation is dead (bits/chemistry ratio ~1.0)" | Diagnostic used fixed basins and was blind to the dominant term |
| "Bulk float32 reaches 26x, lossy is pointless there" | Sampling bias: smallest-first ordering selected high-symmetry materials; full corpus gives 4.6x |
| Bias correction "2.08x on slabs" | Fixed-basin metric; gains largely evaporate honestly measured |
| "Bulk crystals have a median Bader stability floor of 6e-9 e" and every archived-float32-probe non-evaluable rate | The float32 probe is order-preserving and understates the floor substantially. The older ~8,700x intermediate summary is superseded for submission wording by the formal five-seed QSQ paired-development median shift of ~1.6×10^4. Archived values remain provenance only; QSQ values replace them for current claims |
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
