# Manuscript v0.4 change log — 2026-09-08

Canonical integrated draft: `paper/MANUSCRIPT_CHATGPT_v0.4.md`

## Why v0.4 was necessary

The previous v0.3.1 manuscript predated two major closure experiments:

1. the final **63/63 pre-frozen external confirmatory audit**;
2. the **independent Henkelman Bader robustness supplement** with spatial controls.

The new version incorporates both without modifying any frozen scientific result.

## Major changes

### 1. Abstract upgraded from internal evidence to external confirmation

The abstract now reports:
- 254-material / 6,343-row development benchmark;
- matched-realized-L∞ residual rather than same-nominal codec gaps;
- Protocol A.1 resolvability counts;
- final 63/63 external completeness and directional replication;
- independent Bader implementation robustness.

### 2. External validation is now a full Results section

New headline facts:
- 63/63 confirmatory systems complete;
- 1,689 retained rows;
- zero material-level failures;
- zero bound violations;
- exact pre-frozen A.1 eligibility counts 16/42/57;
- all three pre-specified direction predictions reproduce.

The final external CCR values replace the earlier 62-system sensitivity values.

### 3. Tight-threshold language softened

At 1e-4 e, the external ZFP–SZ3 separation is narrower than development. The manuscript now says the **direction reproduces** rather than describing ZFP as strongly separated from SZ3. At 1e-2 e, the SZ3 rate advantage is strong and material-level pairing supports it.

### 4. Last Cl recovery documented transparently

The manuscript records the exact CHGCAR hash and the fact that only the broken AFLOW metadata transport path was changed. Scientific code, Bader settings, codec ladder, Protocol A.1 and certification semantics remained frozen.

### 5. Independent implementation check added

The manuscript now reports that Henkelman on-grid reproduces the BaderKit perturbation response with median response ratio 1.00 (IQR 0.92–1.005), while explicitly acknowledging materials whose unperturbed basin sets differ between implementations.

This changes the robustness statement from:

> “the development data and internal mechanism analyses support the interpretation”

into:

> “the central qualitative perturbation response survives an independent Bader implementation.”

### 6. Spatial-control interpretation made more precise

The new manuscript uses global permutation, density-stratified permutation and periodic translation to distinguish error-value magnitude from spatial organization. It avoids claiming a uniquely identified boundary-local mechanism.

Preferred wording:

> “Error organization beyond scalar magnitude matters; destroying spatial autocorrelation changes the downstream response, whereas periodic translation is approximately null.”

### 7. Discussion reorganized around evidence hierarchy

The Discussion now emphasizes four orthogonal checks:
- re-derived downstream analysis;
- matched realized distortion;
- frozen external data;
- independent implementation.

This is stronger than presenting a sequence of codec comparisons because it makes the paper a validation methodology rather than a leaderboard.

### 8. Limitations integrated into Discussion

There is no standalone `Limitations` section in v0.4. Scope restrictions are placed directly where their corresponding claims are discussed:
- 12-material mechanism panel ≠ prevalence estimate;
- Protocol A.1 floor is operational and solver-dependent in magnitude;
- three codecs are not exhaustive;
- Bader is a demanding exemplar, not all QoIs.

### 9. Explicit Conclusions section added

The final paper now closes on the reusable workflow:

> measure realized distortion → establish numerical resolvability → re-run the downstream analysis → certify scientific fidelity → validate across independent data and implementation.

## Supporting manuscript-control files

- `paper/CLAIM_EVIDENCE_MATRIX_v0.4.md`
- `paper/HEADLINE_NUMBER_REGISTRY_v0.4.md`
- `validation/final_external_confirmatory63_20260908/`
- `mechanism/independent_bader_20260908/`

## Remaining editorial work before submission

The scientific story is materially closed, but v0.4 should still undergo:
- reference-by-reference verification against the final text;
- JCTC formatting and word-count cleanup;
- figure renumbering/caption alignment after the final figure map is chosen;
- cross-document lint against SI and Data/Code Availability;
- final author/affiliation/acknowledgment metadata.

These are editorial/submission tasks, not unresolved scientific gates.
