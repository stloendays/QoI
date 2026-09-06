# JCTC Submission Readiness Status v0.1

**Date:** 2026-09-06  
**Branch:** `submission/jctc-v0.1`  
**Target:** *Journal of Chemical Theory and Computation* — Article

## Overall status

**Scientific narrative: ready.**  
**Journal-targeted manuscript text: ready for formatting/figure embedding.**  
**Supporting Information text: substantially populated and internally consistent.**  
**Administrative/release/graphics package: not yet submission-complete.**

The currently unavailable full per-atom decomposition file is **not a mandatory blocker** for the present JCTC claim set. The direct decomposition claim is explicitly restricted to the representative 12-material mechanism set, and the population-scale mechanism story is independently supported by full-benchmark reassignment attenuation.

---

## Automated integrity gates

### Main manuscript

`submission/JCTC_MANUSCRIPT_LINT_v0.1.md`

**37/37 checks passed; 0 failed.**

The gate currently verifies:

- frozen headline numbers;
- 209-word abstract and no abstract citations;
- JCTC chemistry/electronic-structure framing;
- representative-set mechanism scope;
- `NON_EVALUABLE_BADER_UNSTABLE` semantics;
- protocol-defined stability-floor terminology;
- association rather than causal-codec language;
- unique and contiguous references 1–15;
- all simple numerical citations resolve;
- no duplicate DOI entries;
- pMSz formal IPDPS 2026 record;
- MARGR as reference 15;
- TOPIQ/FZ-VIS accepted/arXiv records.

### Supporting Information

`submission/JCTC_SI_LINT_v0.1.md`

**34/34 checks passed; 0 failed.**

The gate verifies:

- fixed-basin denominator robustness;
- Protocol A.1 headline eligibility values;
- probe seed/amplitude sensitivity;
- realized-bound utilization;
- conservative complete-case exclusion;
- matched-realized-L∞ residuals;
- reassignment attenuation and p-values;
- global electron-count negative control;
- representative direct mechanism values;
- strict slab n=4 caveat;
- noncausal and nonintrinsic terminology;
- per-atom extension remains conditional.

---

## Submission package already prepared

### Scientific text

- `JCTC_MANUSCRIPT_v0.1.md`
- `SUPPORTING_INFORMATION_TEXT_JCTC_v0.1.md`
- `COVER_LETTER_JCTC_v0.1.md`

### Journal/reproducibility preparation

- `DATA_SOFTWARE_AVAILABILITY_JCTC_v0.1.md`
- `REFERENCE_AUDIT_JCTC_v0.1.md`
- `JCTC_REQUIREMENTS_SNAPSHOT_20260906.md`
- `JCTC_SUBMISSION_CHECKLIST_v0.1.md`
- `JCTC_SUBMISSION_METADATA_v0.1.md`
- `SUBMISSION_MANIFEST_TEMPLATE_v0.1.md`

### Graphics planning

- `TOC_GRAPHIC_BRIEF_JCTC_v0.1.md`
- `JCTC_FIGURE_ASSEMBLY_PLAN_v0.1.md`
- current numeric drafts for Figures 2, 4, 5, and 6 in `figures_v03/` as SVG/PDF/PNG.

---

## Scientific items that are frozen

Do not reopen these without a material scientific contradiction:

1. Protocol A.1 definition and eligibility semantics.
2. 6,343-row successful master benchmark and 77-entry failure registry relationship.
3. fixed-basin versus re-derived primary endpoint.
4. separation of nominal-bound utilization from matched realized-L∞ residual.
5. complete-case material exclusion rule for failure sensitivity.
6. reassignment attenuation as mechanism-consistent observational evidence, not causal mediation.
7. global electron-count deviation negative control.
8. non-evaluable fraction headline values.
9. contract-dependent compression/certification frontier.
10. representative-set scope of direct domain/integrand decomposition.

---

## Items that can still improve without changing the scientific story

### 1. Main figures

- create original Figure 1 schematic;
- polish existing numeric Figures 2, 4, 5, and 6 to JCTC-ready visual quality;
- assemble current Figure 3 from representative direct decomposition + reassignment attenuation;
- optionally upgrade Figure 3 if the per-atom table arrives and passes the preregistered material-level audit.

### 2. Supporting Information production

- convert populated SI text into a formatted review-ready document;
- insert supplementary figures/tables and self-contained captions;
- map each SI figure/table to committed source data.

### 3. ACS Fast Format manuscript

- convert manuscript text into final Word or LaTeX/PDF review-ready form;
- embed figures near first discussion;
- add final author/affiliation block;
- ensure manuscript metadata matches ACS Publishing Center entries.

### 4. Reproducible release

- freeze exact submission commit;
- create release/tag;
- deposit the exact scientific snapshot in Zenodo or equivalent;
- obtain persistent DOI;
- replace future-release wording in Data and Software Availability with the active DOI;
- record file hashes in the submission manifest.

---

## True blockers before clicking Submit

### Requires user/coauthor information

- [ ] final author list and order
- [ ] affiliations
- [ ] corresponding author
- [ ] ORCIDs
- [ ] funding/grant numbers
- [ ] CRediT roles if used/requested
- [ ] competing-interest confirmation
- [ ] originality/concurrent-submission confirmation
- [ ] preprint/related-manuscript disclosure

### Requires final production work

- [ ] original TOC graphic
- [ ] final six main figures / Figure 3 decision
- [ ] review-ready formatted main manuscript
- [ ] review-ready SI
- [ ] immutable archive DOI
- [ ] final submission-day reference check for TOPIQ/FZ-VIS and any other 2026 accepted records
- [ ] final manifest/hashes

---

## Per-atom decision rule

If the full per-atom file remains unavailable when every other blocker is closed, **do not delay submission solely for that file**. Submit using the current representative-set direct decomposition and full-benchmark attenuation evidence.

If it arrives before submission:

1. run the preregistered case/material-level analysis;
2. material bootstrap and leave-one-material-out sensitivity;
3. do not count atoms as independent replicates;
4. upgrade Figure 3/direct-mechanism wording only if the result is consistent;
5. rerun manuscript and SI lints.

---

## Current recommendation

Proceed from **scientific development** to **publication production**. The highest-value next work is visual/formatting/release preparation rather than new full-scale benchmark calculations.
