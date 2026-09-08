# Electron-count QoI negative-control study

## Purpose
Test whether preservation of the global linear observable, total electron count, is sufficient to imply preservation of the topology-dependent Bader charge QoI. It is deliberately treated as a negative control, not as a second headline property.

## Dataset
- Reconstruction rows analysed: **6343**
- Materials/codecs/tolerances: frozen `benchmark/master_benchmark_full.csv`
- QoI: `electron_count_abs_dev` already recorded for every successful reconstruction.

## Global electron-count fidelity
- median |Delta N|: **9.37539e-05 e**
- 95th percentile: **0.0642956 e**
- 99th percentile: **0.274914 e**
- maximum: **3.97545 e**

## Key decoupling test
Using a deliberately loose definition of globally preserved electron count, **|Delta N| < 1e-4 e**, there are **3205** reconstruction rows with a finite re-solved Bader result. Among them, **1383** have Bader error >= 1e-3 e, i.e. **0.431513** of globally charge-conserving rows still fail the 1e-3 e local charge criterion.

## Interpretation rule
This control is manuscript-worthy only if electron count is substantially more stable than re-solved Bader charge and there is a non-negligible population satisfying global conservation while violating the local Bader criterion. In that case the supported statement is:

> Global electron-number conservation is not a sufficient certificate of downstream chemical fidelity.

It does **not** support a claim that electron count itself is a difficult QoI.

See `summary_by_codec.csv`, `summary_by_tolerance.csv`, `electron_bader_decoupling.csv`, and `correlations.csv` for the full audit trail.
