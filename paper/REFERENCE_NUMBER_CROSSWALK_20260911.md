# Reference-number crosswalk for submission — 2026-09-11

The project reference library uses stable IDs 1–21 in `paper/REFERENCES.md` and in the Notion/PDF archive. Those IDs are provenance identifiers and are not changed, because renumbering them would break the literature archive.

The submission manuscript instead numbers references in order of first appearance, as required by numbered Nature/ACS-style workflows. The current polished manuscript first introduces the literature in the following functional order: scientific-compression foundations and codecs; scientific-workflow/chemistry compression context; post-compression assessment; QoI-aware control and pipelines; topology-aware methods; recent QoI uncertainty prediction; QTAIM/Bader numerical foundations.

| Stable library ID | Submission citation no. | Reference shorthand |
|---:|---:|---|
| 1 | 1 | Di et al., error-bounded compression survey |
| 2 | 2 | Lindstrom, ZFP |
| 3 | 3 | Liang et al., SZ3 |
| 4 | 4 | Li et al., SPERR |
| 18 | 5 | Cappello et al., scientific lossy-compression use cases |
| 21 | 6 | Gok et al., PaSTRI |
| 19 | 7 | Lara et al., DFT AO-basis compression |
| 5 | 8 | Tao et al., Z-checker |
| 6 | 9 | Jiao et al., QoI-preserving compression |
| 12 | 10 | Ainsworth et al., derived-quantity error control |
| 13 | 11 | Gong et al., QoI-preserving reduction |
| 14 | 12 | Lee et al., learned compression with derived-quantity preservation |
| 20 | 13 | Banerjee et al., scalable QoI-guaranteed pipeline |
| 7 | 14 | Yan et al., TopoSZ |
| 15 | 15 | Gorski et al., topological guarantees |
| 11 | 16 | Liu et al., TOPIQ preprint |
| 17 | 17 | Bader, QTAIM monograph |
| 8 | 18 | Henkelman et al., Bader decomposition |
| 9 | 19 | Tang et al., lattice-bias-free Bader analysis |
| 16 | 20 | Yu & Trinkle, Bader charge integration |
| 10 | 21 | Hutcheon & Teale, arbitrary-grid topological analysis |

## Submission-order reference sequence

`1, 2, 3, 4, 18, 21, 19, 5, 6, 12, 13, 14, 20, 7, 15, 11, 17, 8, 9, 16, 10`

## Key citation-group translations

| Evidentiary role | Stable library IDs | Submission numbers |
|---|---|---|
| Error-bounded compression + codecs | [1–4] | [1–4] |
| Chemistry/scientific-workflow context | [3,18,19,21] | [3,5–7] |
| Z-checker | [5] | [8] |
| QoI mathematical control | [6,12] | [9,10] |
| QoI-preserving operational pipelines | [13,14,20] | [11–13] |
| Topology-aware compression | [7,15] | [14,15] |
| Recent QoI uncertainty prediction | [11] | [16] |
| QTAIM foundation | [17] | [17] |
| Grid-based Bader algorithms/integration | [8,9,16] | [18–20] |
| Arbitrary-grid numerical topology | [10] | [21] |
| Full Bader numerical background | [8–10,16,17] | [17–21] |

## Audit rule

Stable library IDs should be used in literature-management/provenance files. Submission citation numbers should be used only in reader-facing manuscript and journal-style bibliography renderings. DOI/title metadata, rather than the integer alone, remains the authoritative identity of a reference.

## Update 2026-10-03 (workflow integration)

Two library IDs were added and the submission order was extended by first appearance. Compression Safeguards is
first cited in the Introduction directly after TOPIQ, so it takes submission number 17 and the five Bader/topology
references move from 17–21 to 18–22. Wilks is first cited in Methods (finite-panel admission bound) and takes 23.

| Stable library ID | Submission citation no. | Reference shorthand |
|---:|---:|---|
| 22 | 17 | Tyree et al., Compression Safeguards preprint |
| 17 | 18 | Bader, QTAIM monograph |
| 8 | 19 | Henkelman et al., Bader decomposition |
| 9 | 20 | Tang et al., lattice-bias-free Bader analysis |
| 16 | 21 | Yu & Trinkle, Bader charge integration |
| 10 | 22 | Hutcheon & Teale, arbitrary-grid topological analysis |
| 23 | 23 | Wilks, tolerance limits |

Submission-order reference sequence (current):

`1, 2, 3, 4, 18, 21, 19, 5, 6, 12, 13, 14, 20, 7, 15, 11, 22, 17, 8, 9, 16, 10, 23`

## Update 2026-10-03 (measurement-science framing)

Two library IDs were added. Currie (IUPAC 1995) and the AIAG MSA manual are first cited in the Introduction paragraph
that precedes "Here we establish QSQ…", so they take submission numbers 23 and 24; Wilks, first cited in Methods, moves
from 23 to 25 (main-text Methods citation and SI Note 18 "main-text ref. 25" updated).

| Stable library ID | Submission citation no. | Reference shorthand |
|---:|---:|---|
| 24 | 23 | Currie, IUPAC 1995 detection/quantification nomenclature |
| 25 | 24 | AIAG, Measurement Systems Analysis manual (4th edn) |
| 23 | 25 | Wilks, tolerance limits |

Submission-order reference sequence (current):

`1, 2, 3, 4, 18, 21, 19, 5, 6, 12, 13, 14, 20, 7, 15, 11, 22, 17, 8, 9, 16, 10, 24, 25, 23`


## Update 2026-10-05 — QOAC-H integration (current authoritative submission order)

QOAC-H introduces three prior-art references before the Methods-only Wilks citation: QPET, transform-coding theory, and the electron-density/Hartree tensor-compression precedent. They take submission numbers 25–27. Wilks therefore moves from 25 to 28.

| Stable library ID | Submission citation no. | Reference shorthand |
|---:|---:|---|
| 1 | 1 | Di et al., error-bounded compression survey |
| 2 | 2 | Lindstrom, ZFP |
| 3 | 3 | Liang et al., SZ3 |
| 4 | 4 | Li et al., SPERR |
| 18 | 5 | Cappello et al., scientific lossy-compression use cases |
| 21 | 6 | Gok et al., PaSTRI |
| 19 | 7 | Lara et al., DFT AO-basis compression |
| 5 | 8 | Tao et al., Z-checker |
| 6 | 9 | Jiao et al., QoI-preserving compression |
| 12 | 10 | Ainsworth et al., MGARD derived-quantity control |
| 13 | 11 | Gong et al., QoI-preserving reduction |
| 14 | 12 | Lee et al., learned compression with derived-quantity preservation |
| 20 | 13 | Banerjee et al., scalable QoI-guaranteed pipeline |
| 7 | 14 | Yan et al., TopoSZ |
| 15 | 15 | Gorski et al., topological guarantees |
| 11 | 16 | Liu et al., TOPIQ |
| 22 | 17 | Tyree et al., Compression Safeguards |
| 17 | 18 | Bader, QTAIM monograph |
| 8 | 19 | Henkelman et al., Bader decomposition |
| 9 | 20 | Tang et al., lattice-bias-free Bader analysis |
| 16 | 21 | Yu & Trinkle, Bader integration |
| 10 | 22 | Hutcheon & Teale, arbitrary-grid topological analysis |
| 24 | 23 | Currie, IUPAC quantification nomenclature |
| 25 | 24 | AIAG, Measurement Systems Analysis |
| 26 | 25 | Liu et al., QPET |
| 27 | 26 | Goyal, transform coding |
| 28 | 27 | Chinnamsetty et al., density/Hartree tensor approximation |
| 23 | 28 | Wilks, tolerance limits |

Submission-order stable-library sequence (current):

`1, 2, 3, 4, 18, 21, 19, 5, 6, 12, 13, 14, 20, 7, 15, 11, 22, 17, 8, 9, 16, 10, 24, 25, 26, 27, 28, 23`

This 2026-10-05 mapping supersedes earlier submission-number tables while preserving all stable library IDs.
