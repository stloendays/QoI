# Main manuscript ↔ Supplementary Information cross-reference plan

Updated 2026-09-11. This map specifies where each Supplementary object should be cited in the polished manuscript. It is a build plan rather than a second narrative: the main text keeps the central claims, while the SI carries detailed denominators, sensitivity analyses and robustness evidence.

**Current insertion state (submission audit 2026-09-11):** Tables S1–S7 exist as submission-facing drafts; Supplementary Figs. S1, S2 and S7 are formally locked. The polished manuscript now cites only built/locked SI objects (S1–S4, S6–S7; Figs. S1, S2, S7). References to Tables S8–S14 and Figs. S3–S6/S8 remain deferred until those objects are built and locked.

## Cross-reference principles

1. The first mention of an SI object should occur immediately after the main-text claim it substantiates.
2. Do not cite more than two supplementary objects in a single sentence unless they answer distinct questions.
3. Main Figures 1–7 retain all headline results; supplementary figures expand or validate them rather than introduce new central conclusions.
4. Detailed failure accounting belongs in the SI even when the main text reports the existence of failures.
5. The same Supplementary object may be cited from Results and Methods when it supports both interpretation and reproducibility.

## Recommended insertions

| Main manuscript location | Main-text statement | Add SI reference | Purpose |
|---|---|---|---|
| Results — operator hierarchy, electron count | 3,205 globally charge-conserving rows; 1,383 still exceed Bader 1e-3 e | **Supplementary Table S8; Supplementary Fig. S3** | full codec/tolerance breakdown and distribution |
| Results — operator hierarchy, Hartree | 6,270 gate-passing rows; pooled slope 1.02; high material R² | **Supplementary Table S9; Supplementary Fig. S3** | full strata, gate accounting, monotonicity and matched-Hartree dispersion |
| Results — first definition of Protocol A.1 | five fixed-seed perturbations and material-specific stability floor | **Supplementary Table S2; Supplementary Fig. S2** | protocol definition, seed and amplitude validation |
| Results — eligibility fractions | 79.9%, 41.4%, 9.7% non-evaluable in 319-system stability universe | **Supplementary Table S3; Supplementary Fig. S1** | complete threshold/stratum breakdown |
| Results — Figure 3 binary-to-three-state result | 97.2% / 95.5% failure reclassification and 46.3% invalid naive passes | **Supplementary Table S4; Supplementary Fig. S7** | codec-specific decomposition |
| Results — qualification-probe correction | float32 probe order-preserving; A.1 needed | **Supplementary Fig. S2; Supplementary Table S7** | calibration, seed spread, amplitude dependence |
| Results — strictest certified regime | error/floor ≈ 1.09–1.33 at 1e-4 e | **Supplementary Table S6; Supplementary Fig. S4** | full threshold comparison and tight-ladder trajectories |
| Results — Bader basin migration | fixed-domain scoring suppresses domain migration | **Supplementary Table S10; Supplementary Fig. S5** | extended representative-case matrix |
| Results / Discussion — implementation robustness | Bader mechanism not specific to one solver implementation | **Supplementary Table S11; Supplementary Fig. S5** | BaderKit/Henkelman/near-grid comparison |
| Results — realized distortion matching | primary 0.10-dex matching and residual codec effects | **Supplementary Table S12; Supplementary Fig. S6** | match quality, common support and 0.05–0.30 dex sensitivity |
| Results — development rate–fidelity | codec ranking changes with scientific contract | **Supplementary Table S13** | full admitted denominators, CIs, quantiles and pairwise wins |
| Results — external confirmation | 63-system frozen primary cohort; 1,689 rows; 3 row failures | **Supplementary Table S13; Supplementary Fig. S8** | full per-system/pairwise distributions |
| Methods — Benchmark design | 254 development systems, 6,343 rows | **Supplementary Table S1** | denominator/provenance registry |
| Methods — Protocol A.1 | exact seeds, floor definition and archived A | **Supplementary Table S2** | protocol reproducibility |
| Methods — External confirmation | primary 63 vs descriptive 65 universes | **Supplementary Table S1** | prevent denominator ambiguity |
| Methods / Data availability | solver failures and non-evaluable semantics | **Supplementary Table S14** | explicit failure taxonomy and negative-result register |

## Suggested sentence-level edits for the polished manuscript

These are recommended compact additions; they should be inserted only after the supplementary objects are built and locked.

### Operator controls

After the electron-count paragraph:

> The codec- and tolerance-resolved electron-count control is reported in Supplementary Table S8 and Supplementary Fig. S3.

After the Hartree paragraph:

> Full stratum-specific scaling, reproduction-gate accounting and material-level smoothness diagnostics are provided in Supplementary Table S9 and Supplementary Fig. S3.

### Stability qualification

After Protocol A.1 is first defined:

> The archived Protocol A comparison, five-seed calibration and amplitude sensitivity are detailed in Supplementary Tables S2 and S7 and Supplementary Fig. S2.

After overall eligibility fractions:

> Eligibility by development and external stratum is reported in Supplementary Table S3 and Supplementary Fig. S1.

### Central reclassification result

After the Figure 3 paragraph:

> The codec-resolved reclassification shows the same strict-threshold pattern for ZFP, SZ3 and SPERR (Supplementary Table S4 and Supplementary Fig. S7).

### Tight regime

After the floor-scale paragraph:

> Threshold- and codec-resolved error-to-floor summaries and tight-ladder trajectories are shown in Supplementary Table S6 and Supplementary Fig. S4.

### Bader mechanism

After the fixed-versus-re-derived paragraph:

> Extended per-atom decompositions and an independent Bader-implementation comparison are provided in Supplementary Tables S10–S11 and Supplementary Fig. S5.

### Realized-distortion matching

After the 0.10-dex matched effect estimates:

> Match-quality diagnostics, common-support counts and sensitivity to 0.05–0.30-dex calipers are provided in Supplementary Table S12 and Supplementary Fig. S6.

### Rate–fidelity

After the development rate–fidelity paragraph:

> Full eligibility denominators, certified fractions, bootstrap intervals and pairwise win fractions are reported in Supplementary Table S13.

### External confirmation

After the external 63-system paragraph:

> Supplementary Table S1 distinguishes the 63-system primary confirmatory cohort from the 65-system external descriptive/stability set; detailed external distributions and failure accounting are provided in Supplementary Table S13 and Supplementary Fig. S8.

## Cross-reference audit checklist

Before final Word/PDF assembly:

- [ ] Tables S1–S14 exist with final captions.
- [ ] Figures S1–S8 exist as R-generated PNG/PDF/SVG.
- [ ] No main-text reference points to an unbuilt SI object.
- [ ] No SI object is orphaned (never cited in main text or SI prose).
- [ ] 319-system stability and 63-system external-confirmatory denominators are never conflated.
- [ ] `Protocol A` is always labelled archived/provisional.
- [ ] `non-evaluable` is never used as a synonym for failure.
- [ ] Table S13 values are regenerated from final machine-readable sources at build time.
- [ ] Supplementary captions state whether analyses are primary, sensitivity, diagnostic or negative-result evidence.
- [ ] Final citation and figure/table numbering are checked after journal-specific formatting.
