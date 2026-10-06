# QOAC-B3: compressing the partition field without moving any Bader basin

Date: 2026-10-06
Branch: `research/qoac-b3-design-20261006` (from `research/qoac-program-base-20261006`)
Status: a design study with a synthetic prototype. No material data were downloaded or used. The real-material protocol in section 7 is only a proposal and has not been run.

## 0. Summary

QOAC-B1 and QOAC-B2 keep the partition-defining field `AECCAR0 + AECCAR2` exact. Henkelman on-grid Bader then gives a fixed label map, and B2 projects the compressed CHGCAR so that its per-basin sums match. B2's 38-material confirmatory result is `SUMMARY.json`: median CR ratio 1.86, zero reassignment, zero Bader error. B3 asks whether the partition field itself can be compressed while guaranteeing that Henkelman's on-grid algorithm, run on the decoded field, gives the reference partition voxel for voxel.

Findings:

1. **Exact semantics.** I transcribed the on-grid path of `bader_mod.f90`: `bader_calc`, `max_ongrid`, `step_ongrid`, `refine_edge` and the vacuum rule. For fields satisfying two regularity conditions (R1, R2), the Fortran output equals a pure function of the field: the terminal maximum of a deterministic weighted steepest-ascent successor map, with basins numbered in scan order. Outside those conditions the binary's own two passes disagree with each other, and the prototype shows a concrete case.
2. **Sufficient conditions** (section 2). Zero reassignment is guaranteed by three local constraint families:
   - (V) the vacuum mask is identical;
   - (M) every reference maximum stays a raw 26-neighbour maximum;
   - (B) every non-maximum voxel's decoded steepest-ascent successor is a different voxel in the same reference basin.

   (B) is a disjunction. Fixing the reference successor as witness turns it into a set of three-voxel linear inequalities `(w_k - w_a) g_p + w_a g_a - w_k g_b > 0`. Under a pointwise error bound these become linear inequalities in the per-voxel error allowances.
3. **Algorithms** (section 3).
   - **A2** is an iterative, MSz-style correction. It escalates culprit voxels along a refinement ladder: three 4-bit levels, then exact float64.
   - **A1** is a one-shot, codec-agnostic per-voxel allowance computed from reference margins.

   Both provably terminate with zero reassignment and keep the base error bound. The alternative contract **L** stores the label map losslessly instead.
4. **Prototype result** (section 5). The field set is 20 random smooth fields on 5 lattice families (4 of them non-orthogonal), with 4–7 maxima, 32×30×34 grids and 6 base-quantizer settings. Over all 120 field×setting cases:
   - all three corrected arms give **zero reassignment**, also through the literal Fortran transcription (80/80 cross-checks);
   - A1 needs **zero** extra iterations;
   - `Linf ≤ bound` holds.
5. **Cost.** The dominant design choice is the **base error metric**.
   - With an absolute bound, low-density regions become plateaus. Side information is then 0.3–10× the base payload, worse than storing labels.
   - With a pointwise-relative (log-domain) bound, A2 side information is 0.6–31% of the base payload. At δ ≤ 1e-2 it is smaller than the label map: median 106–736 B against 1004 B.
   - Storing labels **without any AECCAR** costs about 1 kB on these grids, roughly 10× less than any partition-faithful field. A partition-faithful field is worth its cost only when the user needs the field itself.
6. **Prior art** (section 1). I could not open any source: the session's egress proxy refused arxiv.org, doi.org, dblp.org and crossref. Every citation below is therefore **UNVERIFIED**, corroborated only by search-engine summaries. On those summaries, only the MSz family guarantees exact, vertex-for-vertex preservation of a steepest-ascent segmentation. It does so on a piecewise-linear triangulated grid with a raw largest-neighbour rule. None covers the distance-weighted 26-neighbour rule with Henkelman's tie-break and vacuum semantics.

## 1. Prior art

**How this was verified.** A search sub-agent and I tried to open every source. The proxy rejected CONNECT to arxiv.org, export.arxiv.org, doi.org, dblp.org, api.crossref.org, hal.archives-ouvertes.fr and others; I reproduced the 403 with `curl` myself. Only a web-search tool worked. **All entries are therefore UNVERIFIED.** "Search-corroborated" means search summaries agreed on the bibliographic data shown. Everything must be checked against the sources before this document is cited.

| # | Citation | ID | Status | Object preserved / discretization / guarantee |
|---|---|---|---|---|
| P1 | Y. Li, X. Liang, B. Wang, Y. Qiu, L. Yan, H. Guo, "MSz: An Efficient Parallel Algorithm for Correcting Morse-Smale Segmentations in Error-Bounded Lossy Compressors", IEEE TVCG 31(1):130–140, 2025 (VIS 2024) | DOI 10.1109/TVCG.2024.3456337; arXiv:2406.09423 | UNVERIFIED (search-corroborated) | PL Morse–Smale segmentation, i.e. ascending/descending manifold labels from steepest neighbour chains on a triangulated grid. Edits are computed at compression time, applied iteratively after decompression, kept within the error bound and stored as side information. Reported as exact per vertex. Neighbourhood (likely Freudenthal-type) **not verified**. The rule is raw largest neighbour, **not** distance-weighted. |
| P2 | Y. Li, M. Xia, X. Liang, B. Wang, R. Underwood, S. Di, H. Sharma, D. Beniwal, F. Cappello, H. Guo, "pMSz: A Distributed Parallel Algorithm for Correcting Extrema and Morse-Smale Segmentations in Lossy Compression" | arXiv:2601.01787 (2026) | UNVERIFIED | Same object as P1. Enforces that each vertex keeps its steepest ascending/descending neighbour ("local ordering"), which is the analogue of tier S below. Exact on its own discretization. |
| P3 | Y. Li, M. Xia, X. Liang, B. Wang, H. Guo, "Preserving Discrete Morse-Smale Complexes in Error-Bounded Lossy Compression" | arXiv:2409.17346 | UNVERIFIED | Discrete-gradient (Forman) MS complex. Uses edits. |
| P4 | Y. Li, M. Xia, X. Liang, B. Wang, H. Guo, "EXaCTz: Guaranteed Extremum Graph and Contour Tree Preservation for Distributed- and GPU-Parallel Lossy Compression" | arXiv:2604.01397 (2026) | UNVERIFIED | Extremum graph and contour tree, guaranteed. Edits with convergence bounded by a "vulnerability graph". |
| P5 | L. Yan, X. Liang, H. Guo, B. Wang, "TopoSZ: Preserving Topology in Error-Bounded Lossy Compression", IEEE TVCG 30(1), 2024 (VIS 2023) | DOI 10.1109/TVCG.2023.3326920; arXiv:2304.11768 | UNVERIFIED | Contour tree and extrema of a PL field up to a persistence threshold, via constrained quantization inside SZ1.4. Not exact for any segmentation. |
| P6 | M. Soler, M. Plainchault, B. Conche, J. Tierny, "Topologically Controlled Lossy Compression", IEEE PacificVis 2018, 46–55 | arXiv:1802.02731; HAL hal-01703832; DOI not confirmed | UNVERIFIED | Bounded bottleneck distance of persistence diagrams. Not exact segmentation preservation. |
| P7 | N. Gorski, X. Liang, H. Guo, L. Yan, B. Wang, "A General Framework for Augmenting Lossy Compressors with Topological Guarantees", IEEE TVCG 31(6):3693–3705, 2025 | DOI 10.1109/TVCG.2025.3567054; arXiv:2502.14022 | UNVERIFIED | Contour tree (join/split trees), guaranteed. Codec-agnostic, with variable-precision edits. |
| P8 | X. Liang, H. Guo, S. Di, F. Cappello, M. Raj, C. Liu, K. Ono, Z. Chen, T. Peterka, "Toward Feature-Preserving 2D and 3D Vector Field Compression", IEEE PacificVis 2020 | DOI 10.1109/PacificVis48177.2020.6431 | UNVERIFIED | Vertex-wise error bounds derived so that critical points survive. Methodologically this is A1's ancestor. |
| P9 | X. Liang et al., "Toward Feature-Preserving Vector Field Compression" (cpSZ), IEEE TVCG | DOI 10.1109/TVCG.2022.3214821 | UNVERIFIED (volume/year unconfirmed) | Exact critical-point preservation for PL vector fields. |
| P10 | M. Xia, S. Di, F. Cappello, P. Jiao, K. Zhao, J. Liu, X. Wu, X. Liang, H. Guo, "Preserving Topological Feature with Sign-of-Determinant Predicates in Lossy Compression: A Case Study of Vector Field Critical Points", IEEE ICDE 2024 | IEEE Xplore 10597764; DOI not seen | UNVERIFIED | Perturbation bounds that keep predicate signs fixed. This is the same logic as section 2.4. |
| P11 | M. Xia et al., "TspSZ: An Efficient Parallel Error-Bounded Lossy Compressor for Topological Skeleton Preservation", ICDE 2025 (inferred) | not found | UNVERIFIED (weak) | 2D vector-field critical points plus separatrices. |
| — | "Toward Error-bounded Critical Point Preservation" (scalar) | — | not found | No paper under this title. Scalar extrema are covered by P1, P2, P4 and P5. |
| B1 | G. Henkelman, A. Arnaldsson, H. Jónsson, "A fast and robust algorithm for Bader decomposition of charge density", Comput. Mater. Sci. 36(3):354–360, 2006 | DOI 10.1016/j.commatsci.2005.04.010 (as supplied; string not seen in search) | UNVERIFIED | The on-grid method. **What I rely on is the source code in this repository, which I read directly** (section 2). |
| B2 | W. Tang, E. Sanville, G. Henkelman, "A grid-based Bader analysis algorithm without lattice bias", J. Phys.: Condens. Matter 21, 084204, 2009 | DOI believed 10.1088/0953-8984/21/8/084204 (unconfirmed) | UNVERIFIED | Near-grid method (not used by the contract). |
| B3 | M. Yu, D. R. Trinkle, "Accurate and efficient algorithm for Bader charge integration", J. Chem. Phys. 134, 064111, 2011 | DOI 10.1063/1.3553716; arXiv:1010.4916 | UNVERIFIED | Weight method (not used by the contract). |

**Which works guarantee exact preservation of a steepest-ascent segmentation on a discrete grid?** On the (unverified) summaries, only P1 and P2. Their segmentation is defined on a piecewise-linear triangulation, uses a raw largest-neighbour rule and has no vacuum masking. P2's "keep the steepest neighbour" constraint corresponds to tier S here, and P1's iterative edit strategy corresponds to A2. Three things are not in the prior art as summarized:

- the derivation for Henkelman's rule: 26 neighbours, differences divided by the neighbour distance, strict-`>` loop-order tie-break, absolute vacuum threshold, and the `refine_edge` regularity conditions;
- the basin-level relaxation (tier B), which only requires successors to stay inside the basin;
- the pointwise-relative base metric, the dominant cost lever here.

These are offered as this study's contribution, pending verification that P1–P4 do not already contain them.

## 2. Exact on-grid semantics and sufficient conditions

Source: `mechanism/independent_bader_20260908/reference_source/bader_mod.f90`, `charge_mod.f90`, `chgcar_mod.f90`, `options_mod.f90` (Bader 1.05). The contract runs `bader CHGCAR -ref REFCAR -b ongrid -vac 0.001`. The partition is computed on `REFCAR = AECCAR0 + AECCAR2` (`chgtemp`), and charges are integrated from CHGCAR (`chgval`).

### 2.1 Notation

- Grid Λ = Z_{n1}×Z_{n2}×Z_{n3}. All indexing is periodic (`rho_val`, `pbc`).
- Offsets d_k, k = 1..26, in the Fortran loop order: d1 outermost, d3 innermost, each from −1 to 1, centre removed. The centre has `lat_i_dist = 0` and can never win a strict `>`, so dropping it is exact.
- Weights w_k = 1/|Σ_i d_{k,i} a_i / n_i|, where a_i are the scaled lattice vectors (`read_charge_chgcar`). Note w_k = w_{−k}. In skewed cells a diagonal neighbour can be closer than a face neighbour. w_k > 1 Å⁻¹ is typical, so the coefficient (1 − w_k) below is usually negative.
- f is the REFCAR field in CHGCAR units (ρ·V), V = |a1·(a2×a3)| (`matrix_volume`), and v = `vacval` = 0.001.
- Candidate value (`step_ongrid`), evaluated in floating point as subtract, multiply, add:
  `T_k(f;p) = f_p + (f_{p+d_k} − f_p)·w_k = (1 − w_k) f_p + w_k f_{p+d_k}`.
- Successor s_f(p): the first k in loop order attaining the maximum of T_k, provided T_k > f_p strictly (update rule `IF (rho_tmp > rho_max)`). Otherwise s_f(p) = p. Since w_k > 0, T_k > f_p ⇔ f_{p+d_k} > f_p. Ascent therefore strictly increases f, and the successor graph is acyclic.
- Vacuum set Z(f) = {p : |f_p / V| ≤ v}, evaluated on the reference field.

### 2.2 What the binary computes

`bader_calc` with `-b ongrid` runs in four steps:

1. It sets `volnum = −1` on Z(f).
2. It scans p in C order (n1 outer, n3 inner). From each unassigned non-vacuum voxel it follows `max_ongrid`. The path stops either at a voxel that does not move or at the first voxel with `volnum > 0`; vacuum voxels (−1) are traversed. If the end voxel is unassigned it opens a new basin (`bnum+1`). All path voxels except vacuum voxels take the end voxel's label.
3. It relabels vacuum to `bnum+1`.
4. It always calls `refine_edge` once, with `refine_edge_itrs = 0`: `bader_calc` overwrites the option, and ongrid also defaults to 0 in `options_mod`. This step marks every non-vacuum voxel that has a 26-neighbour with a different |label| and is not a raw `is_max`. It then re-ascends from each marked voxel. Paths now stop at the first positive label, and the vacuum label `bnum+1` counts as positive.

Atoms are attached by `assign_chg2atom`: each basin is assigned to the ion nearest to its maximum's grid position. `AtIndex` writes `nions+1` for vacuum.

**Lemma 1 (pure-function form).** Let τ_f(p) be the fixed point of s_f. Call f *regular* if

- **R1**: every non-vacuum voxel with s_f(p) = p is a raw `is_max`, meaning no 26-neighbour is strictly larger;
- **R2**: no non-vacuum voxel has s_f(p) ∈ Z(f).

If f is regular, then
`volnum(p) = nb+1` for p ∈ Z(f), and otherwise `volnum(p) = rank of τ_f(p)`. Basins are ranked by the smallest scan index of any non-vacuum voxel whose ascent ends there.

*Proof sketch.* In step 2, an early stop at a positive label happens only at a voxel that already carries the label of its own terminal maximum. Ascent is deterministic, so that voxel's trajectory is a suffix of the current one, and every label is the label of τ_f. In step 4, a re-ascent from an edge voxel again reaches either a positive voxel carrying τ_f's label or a maximum. Maxima are never marked, because by R1 every stationary voxel is an `is_max`. R2 rules out a path entering vacuum. Without R2, such a path would cross vacuum in step 2 but stop on the vacuum label in step 4. So refinement reassigns nothing. A new basin is opened exactly when a scan start first reaches a not-yet-labelled maximum. □

**When regularity fails.**

- R1 fails only through floating-point absorption: f_q > f_p but `(f_q − f_p)·w_k` is below half an ulp of f_p. The voxel then opens its own basin in step 2. If it lies on an edge, step 4 gives it a negative label ("ERROR: should be no new maxima"), and `volchg` is later indexed with that negative label.
- R2 needs a non-vacuum voxel with ρ < −v next to vacuum. That can only happen with negative all-electron densities.

`test_regularity_flags_vacuum_crossing` builds such a field. The literal transcription finds 9 basins and the naive terminal-map shortcut finds 10. **Regularity of the reference must be a gate (section 7)**, and B3 must also guarantee it for the decoded field.

### 2.3 Sufficient conditions for an identical partition

Let f be regular, with labels ℓ(p) and basin maxima M_b. Let g be the decoded field.

**Theorem 1.** `volnum(g) = volnum(f)` voxel for voxel, with the same basin numbering, the same maxima and hence the same atom map, if:

- **(V) vacuum**: for every p, `|g_p| ≤ vV ⇔ |f_p| ≤ vV`.
- **(M) maxima**: for every non-vacuum reference maximum M and every neighbour q, `g_q ≤ g_M`. This is the raw condition, which implies weighted stationarity and `is_max`.
- **(B) basin-faithful successor**: for every non-vacuum, non-maximum p, `s_g(p) ≠ p` and `ℓ(s_g(p)) = ℓ(p)`.

*Proof.*

- **Chains stay in the basin.** By (B), the g-ascent chain from a non-vacuum p never leaves ℓ(p). It never enters vacuum, because vacuum has its own label. g strictly increases along the chain, so it terminates.
- **The terminal voxel is M.** The chain ends at a g-stationary voxel of basin ℓ(p). By (B), no non-maximum voxel is g-stationary. By (M), M_{ℓ(p)} is g-stationary. So τ_g = τ_f.
- **Vacuum and numbering.** The vacuum sets agree by (V). The basins are the same voxel sets, so the scan-order ranks are the same.
- **g is regular.** Its stationary non-vacuum voxels are exactly the reference maxima, which are raw maxima by (M), so R1 holds. Successors stay out of vacuum, so R2 holds. Lemma 1 therefore applies to g. □

**Tier S (successor-exact).** A stronger condition replaces (B) by `s_g(p) = s_f(p)` for all non-vacuum p. Let a = p + d_{k*} be the reference successor. Tier S is equivalent to three families of inequalities:

```
(S1)  (w_k − w_{k*}) g_p + w_{k*} g_a − w_k g_{p+d_k}  >  0     for k < k*  (earlier in loop order)
(S2)  (w_k − w_{k*}) g_p + w_{k*} g_a − w_k g_{p+d_k}  ≥  0     for k > k*
(S3)  g_a − g_p > 0
```

(In floating point these are the comparisons of the rounded T values; see 2.4.) All are linear in three voxel values. Tier S is the analogue of pMSz's local-ordering constraint.

**Tier B, linearised.** (B) is a disjunction over the in-basin neighbours, so its feasible set is non-convex. Fixing the witness a = s_f(p) gives a linear sufficient system. Let O(p) be the set of out-of-basin neighbour offsets, vacuum included. The system is (S1)/(S2) restricted to k ∈ O(p), plus (S3). Constraints against in-basin competitors are dropped. This is the system A1 certifies. A2 checks (B) itself, which is the weakest condition, and accepts any in-basin successor.

**Vacuum and maxima** are also local and linear:

- (V): `|g_p| ≤ vV` if |f_p| ≤ vV, else `|g_p| > vV`.
- (M): `g_M − g_q ≥ 0` for each of the 26 neighbours q.

**Periodic boundaries** need nothing extra, because every stencil wraps (`rho_val`/`pbc`). For n_i ≤ 2 the offsets ±1 alias to the same voxel with the same weight, and the conditions still hold as stated. The prototype assumes n_i ≥ 3.

### 2.4 Robust (error-bound) form

Suppose |g_p − f_p| ≤ ε_p. Then for any comparison c = (p, a, b):

```
|Δ[T_a − T_b]| ≤ |w_a − w_b| ε_p + w_a ε_a + w_b ε_b         (≤ 2 ε w_max for uniform ε)
|Δ[T_a − g_p]| ≤ w_a (ε_a + ε_p)
|Δ[g_M − g_q]| ≤ ε_M + ε_q
|Δ[|g_p| − vV]| ≤ ε_p
```

Let m_c ≥ 0 be the reference margin of each comparison: the left-hand side evaluated on f. **Corollary.** If every comparison satisfies `coefficient · ε < m_c`, then **any** g inside the box satisfies tier B (witness form) and therefore Theorem 1. This is the one-shot certificate, the same logic as vertex-wise bounds in P8–P10.

**Floating point and exact ties.**

- The binary evaluates T in rounded arithmetic, possibly with a different compiler's reassociation or FMA. Its result can differ from an exact-arithmetic or numpy evaluation by a few ulps of max|f|·(1 + w_max). The prototype therefore assigns zero allowance (exact storage) to any comparison whose margin is below a guard γ = 64·ulp(max|f|)·(1 + w_max). It also offers a robust check with a margin parameter.
- Tie-breaking: a comparison with m_c = 0 is an exact tie that loop order decides. It can only be certified by **bit identity**: if every value entering the comparison equals the reference bit for bit, then the same binary makes the same decision. Exact storage achieves this regardless of how the binary rounds.

## 3. Algorithms

All variants share one decoder:

```
decode base codec → g0;  apply side-info edits → g;  [run Henkelman on g → labels];  B2 projection of CHGCAR with labels
```

### 3.1 Refinement ladder (edit format)

Each edited voxel p carries a level k:

- k ∈ {1, 2, 3}: `g_p = g0_p + r·step_k`, with `step_k = 2 ε_p / 2^{4k}` and r = round((f_p − g0_p)/step_k), coded in 4k + 1 bits. The error is at most ε_p·2^{−4k}.
- k = 4: `g_p = f_p` exactly, coded as 64 raw bits.

Edits only ever tighten the error, so **the base bound |g − f| ≤ ε_p is preserved**. The prototype measured max Linf/bound = 0.999999.

For a pointwise-relative base, ε_p = (e^δ − 1)|g0_p|. That is a function of g0 alone, so the decoder can recompute it.

Side-information stream:

- header (24 B);
- for each edited voxel in increasing flat index:
  - Elias-γ code of the gap to the previous index;
  - truncated-unary level;
  - residual or raw float.

`side_info_size` computes the exact bit length. A Golomb–Rice gap code would save about log2(N/K) bits per edit; γ is used for simplicity.

### 3.2 A2: iterative correction (MSz-style)

```
level ← 0;  g ← g0
repeat
    run the checker on g (tier B by default; tier S or a robust margin optional)
    if no violation: stop
    culprits ← for each violated non-maximum p: {p, s_f(p), s_g(p)} (+ strongest out-of-basin competitor in robust mode)
               for each violated maximum M: {M} ∪ {q ∈ N(M) : g_q ≥ g_M − margin}
               for each vacuum mismatch: {p}
               if all culprits of a violation are already exact: its whole 27-point stencil
    level[culprits] += 1 (capped at exact);  g ← ladder(f, g0, level)
```

**Termination and correctness.** Every iteration strictly increases Σ level, and Σ level is bounded by 4N, so the loop terminates. If it ever reaches g = f, the check passes trivially, because f is regular and decisions on bit-identical inputs are identical. When the loop stops, the checker certifies Theorem 1. The encoder needs the decoder in the loop. In the prototype A2 converged in at most 10 iterations.

### 3.3 A1: one-shot allowance (codec-agnostic)

From the reference alone, compute for every comparison of section 2.4 an allowance `safety·m_c / C_c`, with C_c the sum of the comparison's coefficients and safety = 0.5. Give that allowance to every participating voxel and take the minimum over all comparisons, with zero below the guard γ. Each voxel then gets the smallest ladder level whose bound fits within its allowance.

By the corollary, **any** base codec output plus these edits satisfies Theorem 1. No decoder runs in the encoder loop, and the edit set is known before compression. The cost is conservatism: in the prototype A1 used about 10× more edits than A2-B under relative bounds, about the same as tier S. A1 needed **0** corrective iterations in all 120 cases.

A1's allowance map is also a valid **pointwise error-bound map**, which a pointwise-bounded codec could consume directly, as cpSZ does (P8/P9). That route would then need side information only for the bound map, not for the edits.

### 3.4 The base metric matters most

Steepest-ascent decisions depend on gradient *directions*. The reference margin of a comparison scales like |∇f|·h·(angle gap). With an absolute bound ε, a comparison is fragile where |∇f| h ≲ ε w_max h. In all-electron densities that is the whole low-density interstitial region and the vacuum shell, where an absolute quantizer produces plateaus and spurious maxima. Measured atom-level reassignment *before* correction was a median of 33% at abs 1e-3 and 72% at abs 1e-2.

Densities decay roughly exponentially away from nuclei, so |f|/|∇f| ≈ 1/κ is nearly constant. A pointwise-relative bound ε_p = δ|f_p| makes fragility independent of the density's magnitude. The prototype implements this as quantization of log|f| (`rel_quantize`). Reassignment before correction drops to a median of 0.1% (δ = 1e-3) and 0.7% (δ = 1e-2), and side information shrinks 20–150×. **Recommendation: B3's base codec for AECCAR should be pointwise-relative**, for example SZ3 in PW_REL mode or log-transform plus an absolute codec.

## 4. Side-information cost

### 4.1 Analytic model

Let K be the number of edited voxels and N the total. With an ideal gap code and a ladder level distribution π_k:

```
bits ≈ K · [ log2(N/K) + 1.44 + Σ_k π_k (k + 4k + 1) + π_exact (3 + 64) ]
```

If the margins are locally uniformly distributed near zero, each ladder step resolves 15/16 of the remaining fragile comparisons, so π_k ≈ (15/16)·16^{−(k−1)}. The value bits are then about 6–8 per edit, plus a 16^{−3} tail of exact storage. Measured: 9–28 bits per edit including γ-coded positions.

**Expected K.**

- **Tier B** (A2-B, A1). Only voxels whose stencil crosses a basin boundary have out-of-basin competitors. Let N_∂ be their number; for compact basins N_∂ ≈ α N^{2/3} N_b^{1/3}, with α of order 10 for a 26-neighbourhood. At a zero-flux surface the ascent direction is tangential, so the in-basin and out-of-basin best candidates are nearly tied and the margin density at zero is high. To first order `K_B ≈ N_∂ · c · 2 ε w_max / ⟨|∇f|⟩_∂ + K_max + K_vac`:
  - K_max ≤ 27 N_b: maxima are cusp-like, so f_M − f_q ≈ f_M κ h, and these are rarely fragile;
  - K_vac ≈ (vacuum surface)/h² × (thickness ≈ ε/(V |∇ρ| h)).
- **Relative bound**: replace ε/|∇f| by δ/κ. Then `K_B ≈ c N_∂ · 2 δ w_max/κ`, linear in δ and independent of magnitude. Measured median K went from 30 to 352 to 1522 for δ = 1e-3, 1e-2, 5e-2. That is ≈ 10× per decade at small δ, saturating as K approaches N_∂ ≈ 3.5k. This is consistent with the model.
- **Tier S** constrains every non-vacuum voxel: `K_S ≈ c' N · 2 δ w_max/κ`, about N/N_∂ times K_B. Measured: about 10× K_B under relative bounds.

**Extrapolation to a real grid (an estimate, not a measurement).** Take N ≈ 8·10⁶ voxels (a 200³ grid) and N_b ≈ 50 basins. Then N_∂ ≈ 10⁵–10⁶. With δ = 1e-2 and the measured synthetic ratio K_B/N_∂ ≈ 0.1, K ≈ 10⁴–10⁵ edits at about 16 bits, i.e. 20–200 kB. For comparison:

- labels (L) at the measured ≈ 2.3 bits per scan-transition voxel: ≈ 30–300 kB;
- the relative-bound AECCAR base payload: likely several MB.

Real AECCAR0 has very sharp core cusps and shallow interstitial minima, so both K and N_∂ must be measured. That is the purpose of the protocol in section 7.

### 4.2 Alternative L: lossless label map

Store the reference label map losslessly. In the prototype each voxel is predicted from its three causal face neighbours using an adaptive context model (ideal code length; a real arithmetic coder is within a few bytes), with xz as a real-byte upper bound. Measured: median 1004 B (context model) per 32×30×34 field, ≈ 2.3 bits per scan-transition voxel. That is 5–27% of the base AECCAR payload, depending on the bound. The cost scales as N_∂·H_∂ and does not depend on ε.

### 4.3 The two contracts, compared honestly

| | A (partition-faithful AECCAR: A1/A2) | L (lossless labels) |
|---|---|---|
| Stored | Error-bounded AECCAR + edits | Label map (+ optional, independently compressed AECCAR) |
| User can recompute with the unmodified Henkelman binary | **Yes**: `bader CHGCAR -ref decoded_REFCAR -b ongrid -vac 0.001` reproduces the reference partition (given regularity and the guard or bit-identity) | **No**: the binary on any lossy AECCAR gives a different partition, so the user must integrate with the stored labels (B2's projection does this already) |
| Field available for other analyses (e.g. a different QoI, visualization) | Yes, with a pointwise bound | Only if an AECCAR is stored too, with no partition guarantee |
| Different Bader settings (`-vac` value, neargrid, weight, edge refinement) | **Not guaranteed**: the certificate is specific to ongrid with v = 0.001 (re-certify per setting; neargrid's gradient-correction accumulation is not covered) | Not possible at all |
| Dependence on arithmetic of the binary | Needs margin ≥ γ, or bit-identical stencils | None |
| Cost on synthetic fields | Base payload (5–19 kB) + side (0.1–36 kB) | ≈ 1 kB labels only, or + base if the field is wanted |
| Cheaper when | Relative bound δ ≲ 1e-2 *and* the field is needed anyway (side < labels) | Only Bader charges are needed |

A third option is worth stating. If the field itself is not needed, one could encode *any* field whose on-grid partition equals the labels, for example a synthetic field generated from the labels. That costs the same as L and gives the "rerun the binary" property. It is a trick, though, and has no value for other analyses. I do not recommend it as a scientific contract.

## 5. Prototype and test results

Files in `analysis/qoac_b3_design/`:

- `ongrid.py`:
  - weights and volume transcribed from `read_charge_chgcar` and `matrix_volume`;
  - vectorized successor (strict `>` in loop order), pointer-jumping partition, scan-order numbering and vacuum rule;
  - regularity report (R1, R2);
  - `ongrid_literal`, a line-by-line scalar transcription of `bader_calc` / `max_ongrid` / `step_ongrid` / `refine_edge` / `is_max` / `is_vol_edge`;
  - the AtIndex atom map.
- `b3_correct.py`: the checker (tiers S/B, robust margin, exact-stencil exemption); absolute and log-domain quantizers; Lorenzo+xz payload bytes; the ladder; A2; A1; side-info serialization; label-map coder.
- `synthetic.py`: random periodic fields made of 4–7 cusp-like exponential "atoms" plus a multiplicative low-k perturbation, in CHGCAR units, on cubic, hexagonal, monoclinic, triclinic and randomly sheared cells, optionally with a vacuum slab. No material data.
- `test_qoac_b3.py`: 15 tests, all passing (`python3 -m pytest -q test_qoac_b3.py`, ~12 s, numpy 2.4.6). They check:
  - the weights against inverse distances, and their inversion symmetry;
  - **fast vs literal on 20 random smooth fields and 30 coarsely quantized ones** (plateaus and exact ties) across all five lattice families, plus a run without vacuum;
  - explicit loop-order tie-breaking and periodic wrap;
  - that R2 violations are flagged and the shortcut departs from the literal semantics;
  - **zero reassignment after correction**: A2 tiers B and S under absolute bounds 1e-4, 1e-3 and 1e-2 on 4 non-orthogonal families × 3 seeds, and A2-B under relative bounds on 4 families × 3 seeds × 3 δ. Each is checked on volnum, maxima and atom map, and on a subset with the literal transcription;
  - A1 with no iteration (abs and rel);
  - A1 certifying 20 random perturbations anywhere inside its allowance box;
  - robust-margin mode;
  - checker soundness: a passing check implies an identical partition over 40 random perturbations of varying size.
- `run_synthetic_study.py` writes `results/synthetic_study.{json,md}`: 20 fields (5 lattice families × 4 seeds, 32×30×34 voxels, 4–7 basins, 7 of 20 with vacuum voxels) × 6 base settings.

| base | bound | atom reass. before (median) | zero reass. after (A2-B, A2-S, A1) | A2-B edits | A2-B side B | A2-B side / base | A2-S side B | A1 side B | A1 extra iters | L B | L / base |
|---|---|---|---|---|---|---|---|---|---|---|---|
| abs | 1e-4·max | 0.039 | 20/20 | 2733 | 3870 | 0.28 | 14679 | 14151 | 0 | 1004 | 0.07 |
| abs | 1e-3·max | 0.327 | 20/20 | 15211 | 16554 | 2.07 | 33797 | 29946 | 0 | 1004 | 0.13 |
| abs | 1e-2·max | 0.717 | 20/20 | 26575 | 35722 | 10.07 | 67500 | 53199 | 0 | 1004 | 0.27 |
| rel | δ=1e-3 | 0.001 | 20/20 | 30 | 106 | 0.006 | 806 | 848 | 0 | 1004 | 0.05 |
| rel | δ=1e-2 | 0.007 | 20/20 | 352 | 736 | 0.072 | 5208 | 4788 | 0 | 1004 | 0.10 |
| rel | δ=5e-2 | 0.030 | 20/20 | 1522 | 2460 | 0.31 | 16396 | 12644 | 0 | 1004 | 0.13 |

Other measurements:

- The literal transcription agreed on 80/80 corrected fields (A2-B and A1 at bound 1e-2).
- All reference fields were regular.
- Max Linf/bound was 0.999999.
- A2 needed at most 10 iterations (abs) and at most 6 (rel).

**Caveats.**

- The grids are small (3.3·10⁴ voxels), so boundary voxels are about 10% of the volume and labels are relatively cheap.
- Uniform quantization with Lorenzo+xz stands in for SZ3/ZFP/SPERR.
- The synthetic densities lack real core cusps, PAW augmentation artefacts and the dynamic range of AECCAR0.
- All equality claims are against my transcription, not the compiled binary. Section 7's Gate 0 closes that gap.

## 6. Interpretation boundary

What the prototype establishes:

- under the transcribed semantics and on regular fields, local inequality constraints certify an identical Henkelman on-grid partition;
- an MSz-style iterative correction, or a one-shot allowance, enforces those constraints with bounded, accountable side information and without exceeding the base error bound;
- a pointwise-relative base metric is the key to making the side information small.

What it does not establish:

- that the compiled Bader 1.05 binary agrees with the transcription bit for bit;
- the cost on real AECCAR fields;
- any guarantee for other Bader modes or vacuum thresholds;
- that a partition-faithful field beats a lossless label map in bytes. On these synthetic fields it does **not**, when only charges are needed.

## 7. Proposed prospective engineering protocol (not executed)

**Populations.**

- **Engineering (development):** the 12 QOAC-B1 engineering materials, already exposed to B1 and B2 development.
- **Confirmation:** the 38 B1/B2 holdout materials have now been executed under B2 (CHGCAR side only). Their AECCAR compression has never been evaluated. Using them for B3 confirmation is allowed only if declared as **non-naive** in the freeze document.
- **Preferred:** freeze a **fresh** population before any B3 run. Draw 40 materials from the same Materials Project loader with successful AECCAR/CHGCAR retrieval and a finite Henkelman run. Exclude the 50 WP-G materials. Select by minimum SHA-256 of `"QOAC-B3-CONFIRM|" + material_id` within 10 npoints strata. Run the 38 non-naive materials as a secondary replication.

**Arms**, all followed by B2's CHGCAR projection at κ = 4 using the labels each arm yields:

| Arm | AECCAR stored as | Labels at decode |
|---|---|---|
| G0 | exact (lossless xz of float64): the B2 reference bundle | binary on exact REFCAR |
| G1 | WP-G codec ladder (SZ3/ZFP/SPERR, absolute), no correction | binary on decoded REFCAR (expected to reassign) |
| A2-abs | G1 base + A2 tier-B edits | binary on decoded REFCAR |
| A2-rel | pointwise-relative base (SZ3 PW_REL or log + absolute), δ ∈ {1e-3, 3e-3, 1e-2, 3e-2} + A2 tier-B edits | binary on decoded REFCAR |
| A1-rel | same base + one-shot allowance edits | binary on decoded REFCAR |
| L | no AECCAR; context-coded label map | stored labels |
| L+ | label map + the A2-rel base without edits | stored labels |

Robust mode is mandatory in all A arms: margin γ = 64·ulp(max|f|)·(1 + w_max) on every emulated decision, and exact storage below the guard.

**Gates (engineering, 12 materials).**

- **Gate 0, emulator fidelity.** On exact REFCAR, for 12/12 materials:
  - (a) R1 and R2 hold;
  - (b) the emulator's volume map equals the binary's (`-p all_bader` / bader index) and its atom map equals `AtIndex`, voxel for voxel;
  - (c) the same holds for a second build of the reference source (gfortran `-O0`, no FMA).

  Failing Gate 0 stops B3, because the targets would be wrong.
- **Gate A, scientific closure.** For every A arm row selected, 12/12 materials, the binary run on the decoded REFCAR must give:
  - zero reassignment on both the bader-volume and atom maps;
  - after B2 projection, Bader error ≤ 2e-6 e;
  - Linf(AECCAR) ≤ base bound.
- **Gate B, rate.** Bundle bytes = AECCAR payload + edits + CHGCAR B2 bytes. R = bytes(G0) / bytes(arm). GO for the best A arm requires at least 9/12 with R > 1 and median R > 1.5.
- **Gate C, side-information practicality.** For the selected A-rel arm, edits/AECCAR payload must be < 10% for at least 10/12 materials.
- **Gate D, contract decision (reported, not pass/fail).** Report median bytes(A-best)/bytes(L+) and bytes(L)/bytes(G0). If L+ is cheaper than A-best by more than 10%, the recommended contract is L. A is then retained only as the "rerun-the-binary" option and its premium is reported.

**Confirmation.** Allowed only if Gates 0, A and B pass. On the fresh 40 materials, with frozen δ, arm and safety factor:

- 40/40 pass Gate 0;
- 40/40 have zero reassignment and Bader error ≤ 2e-6 e;
- at least 32/40 have R > 1, with median R > 1.3;
- the bootstrap 95% lower bound on median R is > 1.1;
- edits < 10% of the AECCAR payload for at least 36/40.

The 38 non-naive materials are reported with the same metrics as a secondary result.

**Reported for every row:** AECCAR Linf and pointwise relative error; reassignment before correction; K; edits by level; A2 iterations; side bytes; label bytes; N_∂; R1/R2 status; encode and decode wall time; the number of emulated decisions within 10γ of a tie.

**Engineering runner (prepared 2026-10-06, not executed).** `run_real_engineering.py` and `.github/workflows/qoac_b3_real_engineering.yml` implement Gate 0 and the A2/A1/L arms on the fresh P2 engineering manifest (`analysis/fresh_population_20261006/P2_ENGINEERING_MANIFEST.csv`, 12 materials). It differs from the protocol above as follows:
- Gate 0 compares the binary's BvIndex/AtIndex, basin count and maxima with the fast emulator, and with `ongrid_literal` only when npoints ≤ 400 000. Gate 0(c), the second `-O0` build, is not run.
- The A arms use the prototype log-domain base quantizer with δ ∈ {1e-3, 1e-2, 5e-2} and robust margin γ. They do not apply B2's CHGCAR projection, and they do not include the G1 codec ladder.
- The binary is rerun on (exact CHGCAR, decoded REFCAR), and reassignment and Bader error are measured against the binary's own reference run.
- Arm L round-trips the label maps through xz and checks the per-atom sums of the exact CHGCAR against `ACF.dat`.
- Only the Gate 0 agreement statistics are aggregated. Gates A to D are not evaluated.
- Execution is triggered by `workflow_dispatch` or by pushing `analysis/qoac_b3_design/RUN_REAL`.
- Results go to `results/real_engineering/`.
