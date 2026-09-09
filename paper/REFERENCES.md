# References for the QoI manuscript

Numbering below is the canonical citation order for the current submission draft.

1. Di, S. *et al.* A survey on error-bounded lossy compression for scientific datasets. **ACM Computing Surveys** (2025). https://doi.org/10.1145/3733104.

2. Lindstrom, P. Fixed-rate compressed floating-point arrays. **IEEE Transactions on Visualization and Computer Graphics** **20**, 2674–2683 (2014). https://doi.org/10.1109/TVCG.2014.2346458.

3. Di, S. & Cappello, F. Fast error-bounded lossy HPC data compression with SZ. In **2016 IEEE International Parallel and Distributed Processing Symposium (IPDPS)**, 730–739 (IEEE, 2016). https://doi.org/10.1109/IPDPS.2016.11.

4. Li, S., Lindstrom, P. & Clyne, J. Lossy scientific data compression with SPERR. In **2023 IEEE International Parallel and Distributed Processing Symposium (IPDPS)**, 1007–1017 (IEEE, 2023). https://doi.org/10.1109/IPDPS54959.2023.00104.

5. Tao, D., Di, S., Guo, H., Chen, Z. & Cappello, F. Z-checker: A framework for assessing lossy compression of scientific data. **The International Journal of High Performance Computing Applications** **33**, 285–303 (2019). https://doi.org/10.1177/1094342017737147.

6. Jiao, P., Di, S., Guo, H., Zhao, K., Tian, J., Tao, D., Liang, X. & Cappello, F. Toward quantity-of-interest preserving lossy compression for scientific data. **Proceedings of the VLDB Endowment** **16**, 697–710 (2022). https://doi.org/10.14778/3574245.3574255.

7. Yan, L., Liang, X., Guo, H. & Wang, B. TopoSZ: Preserving topology in error-bounded lossy compression. **IEEE Transactions on Visualization and Computer Graphics** **30**, 1302–1312 (2024). https://doi.org/10.1109/TVCG.2023.3326920.

8. Henkelman, G., Arnaldsson, A. & Jónsson, H. A fast and robust algorithm for Bader decomposition of charge density. **Computational Materials Science** **36**, 354–360 (2006). https://doi.org/10.1016/j.commatsci.2005.04.010.

9. Tang, W., Sanville, E. & Henkelman, G. A grid-based Bader analysis algorithm without lattice bias. **Journal of Physics: Condensed Matter** **21**, 084204 (2009). https://doi.org/10.1088/0953-8984/21/8/084204.

## Intended citation logic

- [1] establishes the mature error-bounded scientific-compression context.
- [2–4] are the primary codec references for ZFP, SZ and SPERR.
- [5] represents conventional post-compression distortion assessment.
- [6] establishes the explicit move from raw-data error control toward downstream QoI preservation.
- [7] establishes that topological features can require constraints beyond a pointwise error bound.
- [8,9] support the density-dependent, grid-based Bader partition used as the deeply validated topology-sensitive QoI in this work.
