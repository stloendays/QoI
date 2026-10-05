# QOAC-B1 engineering log

## 2026-10-05 — partial run invalidated before engineering gate

The first 12-material execution was interrupted after several materials because the initial runner imposed an unsupported implementation assumption that the maximum Henkelman AtIndex partition label could not exceed the number of atoms.

That restriction was not part of the scientific hypothesis. Fixed-partition QOAC-B only requires a stable non-negative region labeling, and preserving additional exact-reference partition regions is more conservative than dropping them.

Actions:
- remove the atom-count upper bound on partition labels;
- preserve one target sum for every emitted non-negative partition label;
- record the number of extra partition labels;
- upload failure diagnostics even when a material job exits non-zero.

The partial run is engineering/debug output and is not used for Gate A/B/C. The frozen 12/38 material split, tau values, matched-Linf rule and GO/NO-GO thresholds are unchanged.
