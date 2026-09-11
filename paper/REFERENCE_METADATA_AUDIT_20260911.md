# Reference metadata audit — 2026-09-11

## Scope

This audit checks the 21 canonical references used by `paper/MANUSCRIPT_TOP_JOURNAL_POLISHED_20260911.md` for author attribution, title, publication venue, year, volume/issue where applicable, pages/article number, DOI, and source type. Verification prioritized publisher pages, PubMed, institutional publication records, DBLP for computer-science conference metadata, and arXiv for preprints.

## Outcome

**Overall status: PASS.** No incorrect DOI, wrong-paper citation, or material title/author mismatch was found. Two canonical entries required metadata completion rather than substantive correction:

1. **Ref. 1 (Di et al., ACM Computing Surveys)** — completed with volume **57**, issue **11**, Article **287**, pages **1–38**.
2. **Ref. 13 (Gong et al.)** — completed with **Communications in Computer and Information Science, vol. 1512**, pages **22–39**.

The canonical source `paper/REFERENCES.md` has been updated accordingly.

## Verified records

| Ref. | Short name | Metadata status | Primary verification basis |
|---:|---|---|---|
| 1 | Di et al. survey | VERIFIED / COMPLETED | ACM Computing Surveys publisher record; institutional manuscript metadata |
| 2 | ZFP | VERIFIED | PubMed / IEEE bibliographic record |
| 3 | SZ3 | VERIFIED | IEEE Xplore; University of Kentucky record; arXiv author list |
| 4 | SPERR | VERIFIED | IPDPS/UCAR metadata; SPERR project citation |
| 5 | Z-checker | VERIFIED | SAGE publisher record |
| 6 | QoI-preserving compression | VERIFIED | PVLDB / University of Kentucky record |
| 7 | TopoSZ | VERIFIED | PubMed / IEEE record |
| 8 | Henkelman Bader algorithm | VERIFIED | Elsevier record |
| 9 | Tang lattice-bias Bader algorithm | VERIFIED | PubMed / IOP metadata |
| 10 | Hutcheon & Teale | VERIFIED | ACS / PMC record |
| 11 | TOPIQ | VERIFIED PREPRINT | arXiv 2608.26912 |
| 12 | Ainsworth et al. | VERIFIED | SIAM publisher record |
| 13 | Gong et al. | VERIFIED / COMPLETED | Princeton/ORNL institutional records; Springer DOI |
| 14 | Lee et al. | VERIFIED | Applied Sciences / ORNL record |
| 15 | Gorski et al. | VERIFIED | PubMed / IEEE metadata |
| 16 | Yu & Trinkle | VERIFIED | PubMed / JCP metadata |
| 17 | Bader book | VERIFIED | Oxford Academic |
| 18 | Cappello et al. use cases | VERIFIED | SAGE / OSTI metadata |
| 19 | Lara et al. | VERIFIED | ACS JCTC publisher record |
| 20 | Banerjee et al. | VERIFIED | ORNL / DBLP / IEEE conference metadata |
| 21 | PaSTRI | VERIFIED | University of Kentucky / DBLP metadata |

## Pagination note for Ref. 20

The e-Science 2023 table of contents places the paper after preceding conference material and displays a proceedings start location of 22, but ORNL and DBLP bibliographic records both report the paper as **1–10**. The canonical reference therefore retains **1–10**, matching the stable bibliographic records rather than inferring physical proceedings pagination from the table of contents.

## Style renderings produced

- `paper/REFERENCES_NATURE_STYLE_20260911.md`
- `paper/REFERENCES_ACS_STYLE_20260911.md`

The Nature rendering follows the current Nature guidance that references are sequential, article titles are included, journal titles are abbreviated, and papers with more than five authors are rendered as first author + *et al.*. The ACS rendering follows the current ACS reference-element order and semicolon-separated author convention; final author truncation should be checked against the exact target ACS journal.

## Citation-order note

The polished manuscript intentionally keeps working citations in bracketed numerical form while the target journal is undecided. Do not renumber references merely to match thematic grouping: both Nature and ACS-family journals generally expect numbering by order of first appearance. Final citation-callout typography (superscript versus bracketed) should be changed only after the target journal is fixed.

## Remaining submission-time check

Once a target journal is selected:

1. re-run reference order against the final manuscript after any paragraph/figure movement;
2. apply the exact journal abbreviation and author-truncation rules;
3. resolve the final bibliographic status of the 2026 TOPIQ preprint if a peer-reviewed version appears before submission;
4. use the final DOI-bearing repository release for the manuscript's own Data/Code Availability statement.