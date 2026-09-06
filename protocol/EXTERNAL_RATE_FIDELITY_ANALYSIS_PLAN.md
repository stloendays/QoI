# External rate–fidelity analysis plan — frozen before corpus-scale execution

**Frozen: 2026-09-07, after implementation smoke/pilot inspection on two explicitly
identified sentinel systems and before any corpus-scale external rate–fidelity
run.**

This document fixes the analysis population, endpoints, denominator semantics and
reporting rules for the external end-to-end compression benchmark. It does not
change Protocol A.1, any codec setting, any tolerance ladder, the 0.05 e early
stop rule, or the already-frozen 65-system external manifest.

## 1. Why a confirmatory subset is needed

The strict external manifest contains 65 systems (37 AFLOW bulk + 28 NOMAD 2D).
Before the corpus-scale rate–fidelity run, two records were deliberately used as
implementation sentinels while validating the new end-to-end harness:

- `aflow-Ni1_ICSD_181716` — exercises AFLOW pre-VASP5 species/provenance parsing.
- `nomad2d-0XHkHlmw3DQ_` — exercises the NOMAD 2D parser, Bader and all three codec paths.

Their rate–fidelity outputs were inspected while checking implementation
correctness. They therefore remain external to development of the scientific
protocol and codec parameters, but they are no longer honestly describable as
*unseen rate–fidelity confirmation data*.

The correction is made **before** the corpus-scale run and without reference to
whether either sentinel produced favorable or unfavorable codec results:

- all **65** systems will still be run and released for completeness;
- the two sentinels are labelled `implementation_sentinel` and their aggregate
  rate–fidelity statistics are descriptive;
- the remaining **63 systems (36 AFLOW bulk + 27 NOMAD 2D)** are the primary
  confirmatory rate–fidelity cohort.

The frozen machine-readable split is
`validation/external_rate_fidelity_split.json`. No additional material may be
moved between sets after this freeze.

This split affects only the new rate–fidelity validation. The already-completed
Protocol A.1 stability validation on all 65 systems is a separate analysis and
is unchanged.

## 2. Scientific question

Primary question:

> Do codec rate–fidelity behavior and chemistry-aware certification patterns
> measured on the development corpora transfer to a frozen independent
> rate–fidelity cohort without changing the protocol, codec settings or
> tolerance ladders?

This is a validation of the **evaluation workflow and observed codec behavior**,
not a claim that the three codecs or Bader charge exhaust scientific data
compression generally.

## 3. Frozen inputs

The formal run must consume, without tuning:

- `external_test_MANIFEST.json` — 65 frozen source records with URL, byte count
  and SHA-256;
- `stability/stability_floor_A1.csv` — Protocol A.1 floors;
- `protocol/PROTOCOL_A1.md` — eligibility semantics;
- `benchmark/master_benchmark_full.csv` — source of the already-used development
  tolerance values and staged ladder policy;
- `validation/external_rate_fidelity_split.json` — 65/2/63 reporting split.

A preflight job must pass before external codec computation begins.

## 4. Populations and frozen denominator checks

### 4.1 Descriptive full corpus

- n = 65
- bulk = 37
- vacuum2d = 28
- A.1 eligible counts: 18 / 44 / 59 at tau = 1e-4 / 1e-3 / 1e-2 e.

### 4.2 Primary confirmatory rate–fidelity cohort

- n = 63
- bulk = 36
- vacuum2d = 27
- expected A.1 eligible counts: **16 / 42 / 57** at tau =
  1e-4 / 1e-3 / 1e-2 e.

These expected eligibility counts are fixed from the already-frozen A.1 floors;
they are not outcomes of the compression run. Any mismatch is a pipeline/input
integrity error and must stop the confirmatory analysis.

## 5. Frozen codec sampling policy

For each material and each of ZFP, SZ3 and SPERR:

1. **Base ladder**: use the nine development tolerance values from 1e-5 to 1e-1.
   Evaluate from tighter to looser settings. Retain the first successful row with
   `Bader_error_resolved_e >= 0.05 e`, then stop that material-codec base ladder.
2. **Tight ladder**: the four development values 1e-7, 3e-7, 1e-6, 3e-6 are run
   only when `stability_floor_A1_e < 1e-3 e`, matching the development selection.
3. A row-level codec/Bader failure does not establish the 0.05 e early-stop
   condition. It is recorded and the next frozen tolerance is attempted.
4. No tolerance may be added, removed or selected in response to external
   rate–fidelity outcomes.

## 6. QoI and certification

For scientific threshold tau in {1e-4, 1e-3, 1e-2} e:

- **eligible** iff `stability_floor_A1_e < tau`;
- if not eligible: `NON_EVALUABLE_BADER_UNSTABLE`, neither pass nor fail;
- if eligible, a codec row is **CERTIFIED** iff
  `Bader_error_resolved_e < tau`;
- fixed-basin Bader error is diagnostic only and never substitutes for the
  resolved-basin contract.

All Bader basins used for the resolved metric are recomputed from the
reconstructed field.

## 7. Failure accounting

Two failure granularities are frozen.

### Material-level failure

A provenance, source-integrity, parsing, original-grid or original-Bader failure
prevents that material from entering the rate–fidelity analysis. It is a hard
`PIPELINE_FAILURE`, is reported explicitly, and invalidates a claim of complete
confirmatory-corpus execution until resolved or transparently reported.

### Row-level failure

A failure of one `(material, codec, tolerance)` after the material has entered
the benchmark is written to `formal_external_e2e_row_failures.csv`. The failed
row:

- is not a certified pass;
- is not silently removed from audit records;
- does not erase other successful rows from that material;
- does not by itself make the entire material a pipeline failure.

This matches the released development `failure_registry.csv` semantics.

## 8. Primary material-level rate metric

For material i, codec c and threshold tau:

```text
CCR_i,c(tau) = max compression_ratio
               over retained settings certified at tau.
```

CCR (Certified Compression Ratio) is a formal name for the existing development
"best certified ratio" quantity. It is not a new endpoint selected after looking
at external data.

An eligible material with no certified setting has no CCR for that codec.

## 9. Frozen summary statistics

All headline statistics use **materials as the independent units**, never codec
rows.

For each tau, external stratum and codec report:

- total materials;
- A.1 admitted / non-evaluable counts;
- number and fraction of admitted materials with at least one certified setting;
- median CCR among certified materials;
- deterministic paired-material bootstrap 95% CI for the median;
- p10, q1, q3 and p90 of CCR;
- number of materials affected by at least one row-level failure.

The 63-system confirmatory table is primary. The analogous all-65 table is
reported as descriptive.

## 10. Frozen pairwise codec comparison

For each tau and stratum, compare codecs on every A.1-admitted material:

- both have CCR: larger CCR wins;
- only one has CCR: the codec with CCR wins;
- neither has CCR: tie;
- no admitted material is silently removed because a codec lacks a certified
  setting.

Report win/tie/loss fractions, bootstrap CI for the first codec's win fraction,
and median `log2(CCR_a / CCR_b)` only among materials where both CCRs exist.

Pair order is fixed to:

1. SPERR vs SZ3
2. SPERR vs ZFP
3. SZ3 vs ZFP

## 11. Development-derived expectations tested externally

These are directional generalization checks fixed from the released development
results, not requirements for declaring the pipeline successful.

At tau = 1e-4 e:

- expected rate ordering: **ZFP > SZ3 > SPERR**.

At tau = 1e-3 e:

- ZFP and SZ3 are expected to be close;
- both are expected to outperform SPERR on rate among admitted materials.

At tau = 1e-2 e:

- expected rate ordering: **SZ3 > ZFP > SPERR**.

Additional pre-existing mechanism expectations:

- ZFP should typically realize substantially less than its requested L-infinity
  budget, while SZ3 and SPERR should sit near the requested bound;
- fixed-basin Bader error should understate resolved-basin error in cases with
  meaningful domain migration.

A failure of any directional expectation is a scientific result and must be
reported; it must not trigger parameter retuning.

## 12. What counts as workflow validation

The external workflow itself passes its engineering/protocol validation if:

1. frozen preflight invariants pass;
2. every confirmatory source is accounted for;
3. material-level failures are explicitly reported;
4. every successful codec row respects its requested L-infinity bound;
5. eligibility, certification, row-failure and aggregation semantics are applied
   exactly as frozen here;
6. aggregate outputs are reproducibly generated from the row table.

Whether development codec rankings reproduce is a **scientific outcome**, not a
software pass criterion.

## 13. Claim boundary after completion

If the confirmatory run completes under this plan, defensible wording is:

> The complete chemistry-aware rate–fidelity workflow was evaluated end-to-end
> on a pre-specified 63-system confirmatory cohort drawn from the frozen external
> corpus, with two previously inspected systems retained separately as
> implementation sentinels.

Do not describe all 65 systems as untouched rate–fidelity confirmation data, and
do not call the framework a universal standard on the basis of this Bader-charge
case study alone.
