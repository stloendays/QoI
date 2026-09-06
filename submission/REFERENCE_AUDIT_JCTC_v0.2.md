# JCTC Reference Audit v0.2

**Checked:** 2026-09-06  
**Applies to:** `JCTC_MANUSCRIPT_v0.2.1.md`

## Current bibliography status

The working manuscript now contains **19 numbered references**. Reference numbering is contiguous, every numerical citation resolves, and the automated v0.2.1 lint reports no duplicate DOI entries.

## Compression and QoI methodology

1. ZFP — Diffenderfer et al., *SIAM J. Sci. Comput.* 2019. DOI: `10.1137/18M1168832`.
2. SZ3 — Liang et al., *IEEE Trans. Big Data* 2023. DOI: `10.1109/TBDATA.2022.3201176`.
3. SPERR — Li, Lindstrom, Clyne, IPDPS 2023. DOI: `10.1109/IPDPS54959.2023.00104`.
4. QoI-preserving compression — Jiao et al., *Proc. VLDB Endow.* **2022**, 16(4), 697–710. DOI: `10.14778/3574245.3574255`.
5–9. Topology-, Morse–Smale-, extrema-, and local-order-preserving compression records are retained with publisher DOI information where available.
10–11. TOPIQ and FZ-VIS remain 2026 accepted works with arXiv records; final proceedings/TVCG metadata should be rechecked immediately before submission.

## Chemical-analysis and electron-density methodology

12. Bader, *Atoms in Molecules: A Quantum Theory* (1990).
13. Henkelman, Arnaldsson, Jónsson, grid-based Bader decomposition, *Comput. Mater. Sci.* 2006. DOI: `10.1016/j.commatsci.2005.04.010`.
14. Brehm and Thomas, volumetric-data lossless compression, *J. Chem. Inf. Model.* 2018, 58(10), 2092–2107. DOI: `10.1021/acs.jcim.8b00501`.
15. Gong, Zhao, Tang, adaptive real-space integration for electron-density fidelity, *J. Chem. Theory Comput.* 2026. DOI: `10.1021/acs.jctc.6c01124`.
16. Weaver and Warren, **BaderKit**, *J. Open Source Softw.* 2026, 11(121), 9943. DOI: `10.21105/joss.09943`.

BaderKit is now cited directly in the benchmark-design section because the reported calculations use `baderkit` 0.10.2.

## Data-source provenance references

17. Materials Project — Horton et al., *Nat. Mater.* 2025, 24, 1522–1532. DOI: `10.1038/s41563-025-02272-0`.
18. AFLOWLIB — Curtarolo et al., *Comput. Mater. Sci.* 2012, 58, 227–235. DOI: `10.1016/j.commatsci.2012.02.002`.
19. NOMAD — Draxl and Scheffler, *J. Phys. Mater.* 2019, 2, 036001. DOI: `10.1088/2515-7639/ab13bb`.

These three references are now cited at first mention in Section 2.2 so that the data-provenance narrative is bibliographically closed rather than relying only on URLs and manifest metadata.

## Submission-day dynamic checks

- [ ] Recheck TOPIQ for final SC 2026 proceedings DOI/pages.
- [ ] Recheck FZ-VIS for final IEEE TVCG bibliographic record/DOI.
- [ ] Recheck the 2026 JCTC Gong–Zhao–Tang paper for volume/issue/pages or article number if assigned.
- [ ] Recheck the 2026 IEEE TBD local-order paper for volume/issue/pages if assigned.
- [ ] Recheck the 2026 IPDPS pMSz proceedings page range.
- [ ] Run the manuscript reference lint after any change in numbering.
- [ ] Resolve every DOI once more from the final submitted bibliography.

## Editorial rule

Do not increase reference count simply to make the paper appear broader. Add references only when they support one of four roles: compressor definition, QoI/topology methodology, Bader/electron-density methodology, or benchmark-data provenance. The main text should remain selective; detailed adjacent work can remain in Supporting Information when it does not change the central scientific argument.
