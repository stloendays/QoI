# References for the QoI manuscript

Numbering below is the canonical citation order for the current submission draft and the 2026-09-11 certifiability reframe.

1. Di, S. *et al.* A survey on error-bounded lossy compression for scientific datasets. **ACM Computing Surveys** (2025). https://doi.org/10.1145/3733104.

2. Lindstrom, P. Fixed-rate compressed floating-point arrays. **IEEE Transactions on Visualization and Computer Graphics** **20**, 2674–2683 (2014). https://doi.org/10.1109/TVCG.2014.2346458.

3. Di, S. & Cappello, F. Fast error-bounded lossy HPC data compression with SZ. In **2016 IEEE International Parallel and Distributed Processing Symposium (IPDPS)**, 730–739 (IEEE, 2016). https://doi.org/10.1109/IPDPS.2016.11.

4. Li, S., Lindstrom, P. & Clyne, J. Lossy scientific data compression with SPERR. In **2023 IEEE International Parallel and Distributed Processing Symposium (IPDPS)**, 1007–1017 (IEEE, 2023). https://doi.org/10.1109/IPDPS54959.2023.00104.

5. Tao, D., Di, S., Guo, H., Chen, Z. & Cappello, F. Z-checker: A framework for assessing lossy compression of scientific data. **The International Journal of High Performance Computing Applications** **33**, 285–303 (2019). https://doi.org/10.1177/1094342017737147.

6. Jiao, P., Di, S., Guo, H., Zhao, K., Tian, J., Tao, D., Liang, X. & Cappello, F. Toward quantity-of-interest preserving lossy compression for scientific data. **Proceedings of the VLDB Endowment** **16**, 697–710 (2022). https://doi.org/10.14778/3574245.3574255.

7. Yan, L., Liang, X., Guo, H. & Wang, B. TopoSZ: Preserving topology in error-bounded lossy compression. **IEEE Transactions on Visualization and Computer Graphics** **30**, 1302–1312 (2024). https://doi.org/10.1109/TVCG.2023.3326920.

8. Henkelman, G., Arnaldsson, A. & Jónsson, H. A fast and robust algorithm for Bader decomposition of charge density. **Computational Materials Science** **36**, 354–360 (2006). https://doi.org/10.1016/j.commatsci.2005.04.010.

9. Tang, W., Sanville, E. & Henkelman, G. A grid-based Bader analysis algorithm without lattice bias. **Journal of Physics: Condensed Matter** **21**, 084204 (2009). https://doi.org/10.1088/0953-8984/21/8/084204.

10. Hutcheon, M. J. & Teale, A. M. Topological Analysis of Functions on Arbitrary Grids: Applications to Quantum Chemistry. **Journal of Chemical Theory and Computation** **18**, 6077–6091 (2022). https://doi.org/10.1021/acs.jctc.2c00649.

11. Liu, Y., Jiang, B., Yang, T., Di, S., Underwood, R. & Jin, S. TOPIQ: Statistical Error Propagation for Quantity-of-Interest Prediction under Lossy Compression. **arXiv** 2608.26912 (2026). https://arxiv.org/abs/2608.26912.

## Intended citation logic

- [1] establishes the mature error-bounded scientific-compression context.
- [2–4] are the primary codec references for ZFP, SZ and SPERR.
- [5] represents conventional post-compression distortion assessment.
- [6] establishes that explicit downstream QoI preservation is already prior art; the manuscript must not claim novelty for the generic statement that raw-data error does not determine QoI fidelity.
- [7] establishes that topological features can require constraints beyond a pointwise error bound.
- [8–10] support the density-dependent, grid-based and numerically sensitive nature of Bader/topological analysis. In particular, [10] makes it inappropriate to present finite Bader grid sensitivity itself as the paper's novelty.
- [11] shows that current scientific-compression research is already moving toward QoI-level bias and uncertainty propagation. The present manuscript should therefore distinguish itself through **pre-certification numerical eligibility, benchmark validity, and the separation of non-evaluable QoI targets from genuine compression failures**.

## Positioning rule frozen 2026-09-11

The manuscript's literature claim should be conservative:

> Prior work establishes both QoI-aware compression and numerical/topological sensitivity in downstream analysis. Our contribution is the stability-qualified certification logic that asks whether a requested downstream tolerance is itself numerically identifiable before it is used to score a compressor, and then evaluates the consequences of that qualification on a frozen electronic-density benchmark.

Do not use an absolute “first ever” statement unless a later systematic review supports it.