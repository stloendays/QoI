# Literature positioning — pointwise magnitude versus error geometry

Updated: 2026-09-07.

## What is already established

The broad proposition that an error-bounded reconstruction is not guaranteed to preserve a downstream scientific object is not new.

- **TopoSZ** (Yan, Liang, Guo & Wang, IEEE TVCG 2024, DOI `10.1109/TVCG.2023.3326920`) explicitly motivates topology-aware compression from the fact that conventional pointwise error bounds do not preserve extrema and contour-tree relations.
- **JCTC 2022, Topological Analysis of Functions on Arbitrary Grids: Applications to Quantum Chemistry** (DOI `10.1021/acs.jctc.2c00649`) shows directly in a Bader/topological-analysis setting that where grid misassignment occurs matters chemically: misassigned points in low-density regions can yield only ~1e-3 e charge error despite a nonzero misassignment fraction.
- **Lindstrom, Error Distributions of Lossy Floating-Point Compressors (JSM 2017)** and subsequent ZFP error analyses establish that compressor errors have algorithm-dependent distributions, bias/correlation structure and realized magnitudes rather than being interchangeable samples inside the same nominal bound.
- **ClimateBenchPress v1.0 (GMD 2026)** compares modern scientific compressors and explicitly reports codec-dependent global error distributions and spatial error patterns, while emphasizing that whether a spatial pattern is problematic depends on the downstream analysis.

Therefore the manuscript must not claim priority for the generic statement `pointwise bound != downstream-QoI preservation` or for the generic existence of codec-specific spatial error patterns.

## What this project can test more specifically

The more specific, potentially novel chain is:

`codec -> electron-density residual field -> Bader basin migration -> Bader-charge error -> chemical certification decision`.

The development data already establish that nominal tolerance is not a codec-independent realized-distortion scale and that fixed-basin evaluation can understate re-derived Bader error. The representative atom-level decomposition establishes that the worst-affected atom is domain-migration dominated in the pre-specified mechanism set.

The matched-realized-L∞ analysis alone is **not** sufficient to call the remaining codec difference an error-geometry effect. The preregistered dual L∞+RMSE analysis is a retained negative/common-support result, and the stronger norm/histogram-preserving residual spatial-permutation intervention is required before making a causal spatial-organization claim.

## Claim ladder

1. **Safe now:** pointwise error control is not a chemical-fidelity contract.
2. **Safe now:** equal nominal tolerance is not equal realized L∞ across codecs.
3. **Safe now:** after matching realized L∞ alone, codec-dependent Bader differences remain in the matched sample.
4. **Not safe from matching alone:** those residual differences are caused by spatial error geometry.
5. **Potentially supportable after permutation:** holding each residual value multiset fixed while changing only fine spatial assignment changes Bader error; if the preregistered attenuation criterion is met, codec-specific spatial organization contributes to the observed ZFP advantage in the representative mechanism set.
