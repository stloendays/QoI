# JCTC Reference Audit v0.3

**Checked:** 2026-09-06  
**Manuscript:** `JCTC_MANUSCRIPT_v0.2.3.md`

## Current bibliography status

The manuscript currently contains **20 numbered references**. Numbering is contiguous, all numerical citations resolve, and DOI strings are unique where present. Initial ACS Fast Format permits references in any consistent style provided the records are complete and include article titles; journal production will apply the final JCTC house style after acceptance.

## Chemistry/electron-density context

### Brehm and Thomas — volumetric lossless compression

Brehm, M.; Thomas, M. An Efficient Lossless Compression Algorithm for Trajectories of Atom Positions and Volumetric Data. *J. Chem. Inf. Model.* **2018**, *58* (10), 2092–2107. DOI: **10.1021/acs.jcim.8b00501**.

Role in the manuscript: establishes that volumetric chemistry data, including electron-density grids, are already a recognized compression target. The present study addresses the distinct lossy regime in which a scientific-fidelity contract is required.

### MARGR — downstream fidelity of approximate electron densities

Gong, J.; Zhao, Z.; Tang, B. Z. Bridging Machine Learning and Electron Density Theory with Adaptive Real-Space Integration. *J. Chem. Theory Comput.* **2026**, ASAP Article. DOI: **10.1021/acs.jctc.6c01124**. Published online 29 August 2026.

As of 2026-09-06, ACS lists this as an ASAP article without final issue pagination. Keep the DOI and ASAP status until final volume/issue/page metadata appear.

### ChargeFlow — downstream Bader use of learned electron densities

Nguyen, T. M.; Tawfik, S. A.; Tran, T.; Venkatesh, S. ChargeFlow: Flow-Matching Refinement of Charge-Conditioned Electron Densities. *J. Chem. Theory Comput.* **2026**, *22* (16), 8481–8492. DOI: **10.1021/acs.jctc.6c00585**.

Role in the manuscript: provides current JCTC evidence that approximate electron densities are evaluated through downstream chemical analyses, including successful Bader partitioning on a broad external benchmark. The present paper builds a quantitative chemical-fidelity contract for controlled lossy reconstruction, including realized-error matching, re-derived domain migration, and numerical resolvability.

## Bader analysis implementation and provenance

### BaderKit

Weaver, S. M.; Warren, S. BaderKit: A Python Package for Grid-based Bader Charge Analysis. *J. Open Source Softw.* **2026**, *11* (121), 9943. DOI: **10.21105/joss.09943**.

The manuscript cites this directly because the benchmark uses `baderkit` 0.10.2.

### Materials Project

Horton, M. K.; Huck, P.; Yang, R. X.; et al. Accelerated Data-Driven Materials Science with the Materials Project. *Nat. Mater.* **2025**, *24*, 1522–1532. DOI: **10.1038/s41563-025-02272-0**.

### AFLOW

Curtarolo, S.; Setyawan, W.; Wang, S.; et al. AFLOWLIB.ORG: A Distributed Materials Properties Repository from High-Throughput *ab Initio* Calculations. *Comput. Mater. Sci.* **2012**, *58*, 227–235. DOI: **10.1016/j.commatsci.2012.02.002**.

### NOMAD

Draxl, C.; Scheffler, M. The NOMAD Laboratory: From Data Sharing to Artificial Intelligence. *J. Phys. Mater.* **2019**, *2*, 036001. DOI: **10.1088/2515-7639/ab13bb**.

These provenance citations now appear at first use in the benchmark-design section, while source URLs, hashes, and licensing metadata remain in the repository metadata files.

## Compression and topology/QoI literature

The core compression references remain ZFP, SZ3, SPERR, QoI-preserving compression, TopoSZ, the general topology-guarantee framework, DMSC preservation, pMSz, and the 2026 local-order-preserving compressor. These support three distinct layers of prior work: pointwise error-bounded compression, QoI-aware evaluation, and preservation of discrete/topological structure.

The PVLDB record for the QoI-preserving paper is normalized to **2022, 16(4), 697–710**, DOI **10.14778/3574245.3574255**.

## 2026 accepted records to recheck on submission day

### TOPIQ

Liu, Y.; Jiang, B.; Yang, T.; Di, S.; Underwood, R.; Jin, S. TOPIQ: Statistical Error Propagation for Quantity-of-Interest Prediction under Lossy Compression. Accepted for *SC 2026*; arXiv:2608.26912. DOI for current arXiv record: **10.48550/arXiv.2608.26912**.

### FZ-VIS

Liu, G.; Li, Y.; Ren, C.; Underwood, R.; Liang, X.; Wang, B.; Di, S.; Cappello, F.; Guo, H. FZ-VIS: A Visual Analytics Framework for Quantities-of-Interest-Aware Scientific Lossy Compression. Accepted at *IEEE VIS 2026 / IEEE Trans. Vis. Comput. Graph.*; arXiv:2608.08386. DOI for current arXiv record: **10.48550/arXiv.2608.08386**.

Before formal submission, recheck whether either work has acquired final proceedings/TVCG volume, pagination, or publisher DOI and replace the accepted/arXiv form when appropriate.

## Submission-day reference gate

- [ ] verify MARGR final issue metadata if it has moved beyond ASAP;
- [ ] verify TOPIQ final SC 2026 proceedings DOI/pagination;
- [ ] verify FZ-VIS final TVCG bibliographic metadata;
- [ ] verify titles and DOI strings against publisher records;
- [ ] ensure every reference used in the Supporting Information is self-contained there;
- [ ] rerun manuscript, SI, and cross-document reference lints after any renumbering.
