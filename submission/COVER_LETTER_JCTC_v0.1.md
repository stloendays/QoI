# Cover Letter — Journal of Chemical Theory and Computation

**Internal draft v0.2 — 2026-09-06**

> Before submission, replace the bracketed author/affiliation fields and confirm the originality, author-approval, funding, conflict, and related-work statements. Do not submit this internal note.

Dear Professor Gagliardi,

We are pleased to submit the manuscript **“Chemical Fidelity beyond Pointwise Error Bounds: Stability and Bader-Domain Migration in Lossy-Compressed Electron Densities”** for consideration as an Article in the *Journal of Chemical Theory and Computation*.

Real-space electron-density fields are increasingly stored and reused across electronic-structure workflows, but existing error-bounded compression guarantees act on field values rather than on the chemical analyses subsequently derived from those fields. Our manuscript establishes a stability-qualified framework for deciding when a lossy-compressed density-functional-theory electron density remains a valid input to Bader charge analysis.

The study provides three main advances. First, it shows that a common fixed-domain evaluation shortcut suppresses a major downstream error channel: across 4,627 successful base-ladder reconstructions, re-derived Bader errors exceed fixed-basin estimates in 99.7% of cases. Direct decomposition in a representative 12-material mechanism set identifies Bader-domain migration as the dominant contribution in that set, while full-benchmark statistical attenuation independently links codec-associated error differences to voxel reassignment. Second, the work separates requested error tolerance from realized field perturbation. ZFP uses a median 0.158 of its requested pointwise error budget, yet approximately twofold codec-associated Bader-error differences remain after matching realized L-infinity error and applying conservative failure controls. Third, we introduce an explicit numerical-resolvability layer: under a calibrated five-seed perturbation protocol, 41.4% of 319 systems are non-evaluable at a 10^-3 e Bader-charge contract, preventing unstable reference analyses from being misclassified as compression failures.

We believe the manuscript is particularly appropriate for *JCTC* because the contribution is a computational methodology for quantum electronic-structure data rather than a benchmark of storage algorithms alone. The framework connects numerical representation, real-space partitioning, DFT-derived observables, and reproducibility-oriented data methodology. We also discuss recent *JCTC* work on downstream fidelity of machine-learned electron densities and adaptive real-space integration (Gong, Zhao, and Tang, 2026; DOI: 10.1021/acs.jctc.6c01124). Our problem is complementary: we study controlled lossy reconstruction of existing electron densities and show that migration of field-derived integration domains creates a distinct fidelity channel.

The study is accompanied by a structured data and software package containing 6,343 successful compressed reconstructions of 254 development materials, a 319-system stability corpus, archived protocol versions, provenance records, failure registries, and reproducible statistical analyses. Before formal submission, the exact submitted scientific state will be frozen as an immutable archival release with a persistent identifier so that reviewers and readers can map the manuscript to a reproducible data-and-software snapshot.

**[CONFIRM BEFORE SUBMISSION: This manuscript is original, is not under consideration elsewhere, all authors have approved its submission, all related manuscripts/preprints have been appropriately disclosed, and the competing-interest statement is accurate.]**

Thank you for considering our work. We believe it will be of interest to readers working on density-functional theory, electronic-structure data, real-space chemical analysis, numerical reproducibility, and computational methodology.

Sincerely,

**[Corresponding Author Name]**  
[Affiliation]  
[Postal Address]  
[Email]  
On behalf of all authors
