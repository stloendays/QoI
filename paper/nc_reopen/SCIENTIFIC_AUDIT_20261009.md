# Scientific claim-boundary audit — 2026-10-09

**Status:** manuscript and SI corrected; numerical evidence unchanged; further physical and systems benchmarks required before submission. This record is a reviewer-facing engineering audit, **not** an additional confirmatory dataset.

**Authority:** start from `paper/nc-revision3-20261008` at `f0f78b0`. The predecessor protocol and result manifests are immutable on this review branch. The current narrative source is `paper/MANUSCRIPT.md` and `paper/SUPPLEMENTARY_INFORMATION.md`, not the existing PDF/DOCX proof dated 2026-10-08.

## Canonical scientific claim

For electronic densities, numerical qualification of the intended QoI, the spectral symbol of the downstream linear operator, and independent decode-verified certification jointly determine when compressed data can safely support a declared downstream analysis. The operator-aware allocation advantage is prospectively tested; multiple-QoI composition is shown **on bulk crystals with a fixed, exact Bader partition**.

## Claim → decisive evidence → scope

| Claim | Evidence and test population | Correct interpretation |
|---|---|---|
| QSQ separates unstable from stable measurement contracts | 254 development densities, 59 fresh perturbations each; at `1e-3 e`, 135/8,437 qualified exceedances vs 5,326/6,549 rejected | Prospective numerical-risk stratification, not a universal bound on a codec's compression error |
| QSQ finite-panel joint risk bound | Conditional-i.i.d. proof in SI 1.5 and `test_scientific_claims.py`; $5^5/6^6\approx6.698\%$ | Conditional-i.i.d. joint admission-and-one-future-exceedance bound, **not** a result of finite exchangeability alone (sharp limit 1/6) and not conditional risk among admitted cases |
| Fourier operator symbol guides Hartree certification | 60 P1 bulk and 32 P3b slabs, `analysis/general_qoac_law/results/RESULTS.md` | Strong gains against the *implemented* pointwise, truncation, QPET block-average and MGARD configurations |
| QPET comparison | `analysis/hartree_baselines_mgard_qpet_20261007/RESULTS.md`, 92 materials | QPET artifact does not encode Hartree QoI directly; HPEZ uses float32, A1 used original float64; HPEZ crashed for some search points. Primary QPET result is a specific configured comparator, not a theorem about every possible QoI-preserving compressor |
| MGARD tuning | SI 5.1 | Best tested smoothness from `{inf,0,-1,-2}`: A1/M-best at `1e-6` is 16.6× bulk and 19.6× slab, versus 18.2× / 21.0× using physically matched `s=-2` |
| Fixed-reference vacuum shift | 27/32 slabs, `analysis/p3b_vacuum_level_20261007/RESULTS.md` | Median 0.00401 meV, maximum 0.0452 meV at `1e-6`; a Hartree vacuum-window proxy with unchanged Fermi level, not a self-consistent work-function difference; density-defined vacuum threshold does not guarantee a flat electrostatic plateau |
| Bulk joint Hartree–Bader | 48 P2 fresh bulk crystals, `analysis/qoac_hb_v2/results/P2_CONFIRMATORY_MANIFEST/RESULTS.md` | 48/48 joint passes under exact AECCAR0+AECCAR2 reference. Median compressed-stream incremental overhead 1.000 excludes exact reference partition bytes. Fixed partition also prevents using zero voxel reassignment as evidence of robustness to perturbing that partition |
| Partition self-containment | 12 P2 engineering materials, `analysis/qoac_b3_design/results/real_engineering/RESULTS.md` | Lossless atom-label maps median 12.9 kB; compare alternate partition encodings, not the total self-contained archive CR of 48 confirmed materials |
| Archive capacity | Stratified 300 objects (293 completed, 7 conservative failures), WP-F | 4.37× vs gzipped JSON, including ~2.00× from lossless-binary reformatting and 2.66× versus lossless binary from QSQ-gated ZFP/SZ3/SPERR; no Fourier operator encoder in archive experiment |
| Gain forecasting | 92 fresh materials, five operators | Pooled Spearman 0.977, material-level correlations 0.79–0.89 for three gaining operators; Gaussian smoothing systematically overpredicted (bulk 17.6 vs 12.1, slabs 22.0 vs 15.3) |
| Slab joint certification | `research/hb-selfslab-20261007` evidence and `paper/nc_reopen/DECISIONS.md` | The pre-registered self-computed slab joint gate failed (26/32 rather than 31/32). Do not claim the bulk 48/48 result generalizes to slabs. This cohort remains separate per author decision |
| Operational law near-optimality | P1/P3b law protocol | Bulk median A3/A1 1.105 passes near-optimality gate, slabs 1.222 do **not** pass the original 1.15 gate; A3 is the slab recommendation |

## Corrections made without changing frozen experiments

1. Replaced finite-exchangeability misuse by an exact conditional-i.i.d. theorem and a sharp finite-exchangeable counterexample; retained empirical 0.901% rate.
2. Defined joint-CR overhead as incremental *compressed charge-stream* overhead under a reusable exact partition; self-contained representations remain a separate experimental question.
3. Relabelled work-function statements as fixed-reference vacuum Hartree shifts in the main text, Methods, legends and SI. Frozen measurement code and result files were not edited.
4. Reported the strongest tested MGARD parameter and QPET local-QoI/precision/runtime failure caveats without removing observed compression gains.
5. Separated archive format conversion from certified ZFP/SZ3/SPERR savings and from Fourier law results.
6. Made slab near-optimality failure, Gaussian predictor bias and bulk-only joint scope explicit.
7. Added CI regression tests: `paper/nc_reopen/test_scientific_claims.py`, with `.github/workflows/audit_nc_scientific_claims.yml`; standard source audit runs alongside word counting.

## Remaining experiments and decisions (not invented as completed)

### A. Full self-contained joint compression (priority: high)

On the existing P2 48-material population, encode and count `CHGCAR operator stream + side channel + exact partition label map + decoder metadata`. Use both (a) original CHGCAR bytes and (b) a lossless float64 baseline as denominators; separately report per-material and medians of end-to-end bytes. Verify Bader charges with the stored labels, rather than assuming recomputation on lossy AECCAR. If the scientific requirement includes *topological stability under a perturbed partition*, that is a **different contract**, requiring a new experiment with perturbed AECCAR and basin comparison.

### B. Work-function physics (priority: high if used in headline)

Test slab-vacuum plateau quality explicitly, changing vacuum thickness/window width and dipole correction. Where full electronic-structure inputs are available, recompute a genuine DFT work function consistently with `E_F`, the full local potential and the vacuum reference. Report the 27/32 screen separately from any stricter physically converged subset. Until then the current numbers are valid for fixed-reference electrostatic vacuum shifts only.

### C. Baseline parity and systems cost (priority: high)

A clean, hardware-matched comparison should use the same input precision, precomputation allowance, number of codec evaluations, output metric, serialized bytes, encode time, decode time, certificate time, peak RSS, and thread count for A1/A3/A5/A6, QPET and strongest tuned MGARD. Record the upstream HPEZ crash rate; do not discard crashes silently. Compare an explicitly Hartree-aware QoI implementation when one is available before claiming general superiority to QoI-preserving frameworks.

### D. Slab and archive integration (priority: medium)

The slab joint test's failed registered gate must remain visible in provenance; do not retrofit it into a passing joint headline. If the operator-aware Fourier encoder is proposed for archive savings, sample it on the **same WP-F frame and metric**; the current 4.37× headline pertains to the QSQ-gated generic-codec writer.

### E. Predictor calibration and efficiency (priority: medium)

Report within-operator ranking alongside pooled rank correlation, and quantify systematic Gaussian overprediction. Measure runtime and memory on the same host for the analytic law and per-shell optimizer before stating a deployment-optimal strategy solely from CR.

### F. Submission blockers (priority: release)

- Supply author list, order, affiliations, correspondence, ORCID and funding from confirmed metadata (never infer).
- Verify prior-art reference metadata and the full text of the Compression Safeguards preprint.
- Replace the Zenodo archival DOI placeholder with a minted archive or a permitted actual release identifier.
- Rebuild and visually inspect DOCX/PDF **after** this branch's manuscript change. The prebuilt `NC_manuscript_20261008` files are stale against the audited Markdown.
- Resolve, or explicitly sign off, residual supplementary cross-reference ordering warnings.

## Validation convention

`python paper/nc_reopen/test_scientific_claims.py` tests the probability argument, source/claim scope and word budget. `python paper/nc_reopen/audit_manuscript.py` checks citations, cross-references, file paths, commit ancestry and math delimiters. Neither substitutes for VASP runs, Bader recomputation, baseline runtime benchmarking, literature verification or figure/Word/PDF rendering.
