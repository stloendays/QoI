# P3B provenance audit for genuine density-grid recomputation

Status: **FROZEN_PRE_AUDIT**

This addendum is frozen after P3A completion and before inspecting any new grid-convergence outcomes. It does not modify the 24-system panel, the original QSQ gate, P1, P2, P3A, perturbation seeds, perturbation amplitudes, or scientific thresholds.

## Purpose

P3B is allowed to claim genuine electronic-structure density-grid convergence only for systems whose original calculation provenance is sufficiently recoverable to reproduce the underlying static calculation. Interpolation, Fourier resampling, or down/up-sampling of an archived CHGCAR is not accepted as a new electronic-structure calculation.

The audit covers all 24 frozen systems in `convergence_panel.csv` and records provenance availability without replacing non-recoverable systems.

## Required provenance fields

A system is eligible for a genuine P3B recomputation only after the following are recovered with source evidence:

1. electronic-structure code and version;
2. exchange-correlation functional, including any Hubbard/meta-GGA settings needed to reproduce the run;
3. PAW/pseudopotential dataset identity for every species;
4. spin treatment/state (`ISPIN`, magnetic initialization or equivalent when relevant);
5. k-point mesh or exact k-point specification;
6. plane-wave cutoff (`ENCUT` or equivalent);
7. smearing/integration settings (`ISMEAR`, `SIGMA` or equivalent);
8. final cell and atomic coordinates corresponding to the archived density;
9. charge-density convention needed to reproduce the analysed field;
10. settings that determine or constrain the real-space/FFT density grid, including explicit `NGX/NGY/NGZ`, `NGXF/NGYF/NGZF`, `PREC`, `ADDGRID` or equivalent when present.

Raw input/output files take precedence over normalized metadata. Archive metadata may be used when raw files are unavailable, but the evidence source must be recorded.

## Source-specific recovery

### NOMAD systems

Use each frozen NOMAD entry id from `materials_metadata.csv` and query the public NOMAD archive. When possible, fetch the entry mainfile and sibling VASP files (`INCAR`, `KPOINTS`, `POSCAR`/`CONTCAR`, `OUTCAR`, `vasprun.xml`). Record SHA-256 for every retrieved raw file. POTCAR content must not be redistributed; only non-secret/non-licensed identity strings or hashes already exposed by the source may be retained.

### Materials Project systems

The frozen S3 CHGCAR object and its source task id are recorded. Detailed task inputs require authenticated Materials Project task access. The audit may use `MP_API_KEY` from the execution environment if present, but must never print or commit the key. If authenticated task provenance is unavailable, the affected bulk system remains `NOT_EVALUABLE_FOR_P3B_RECOMPUTATION` rather than being reconstructed from a generic `MPRelaxSet` guess.

## Audit outputs

The audit must produce:

- `p3b_provenance_inventory.csv`: one row per frozen panel system;
- `p3b_provenance_candidates.json`: compact machine-readable evidence/candidate fields;
- `P3B_PROVENANCE_AUDIT_REPORT.md`: coverage and missing-field report;
- `execution_manifest.json`: panel hash, script hash, environment and accounting;
- raw-file hashes only; no POTCAR redistribution.

Automated extraction may label a system `AUTO_CANDIDATE_COMPLETE`, but **human/scientific review is required before a P3B recomputation work order is frozen**. The final work order may contain fewer than 24 systems.

## Grid-recomputation design after provenance review

For each approved system, freeze at least three density-grid levels before viewing Bader outcomes:

- `native`: reproduce the archived/native density-grid setting;
- `fine`: systematically finer real-space/FFT grid;
- `finer`: a second systematically finer grid.

Hold the physical calculation fixed. If VASP permits changing only the output/fine FFT grid while retaining the self-consistent basis, state this explicitly. If a setting changes the self-consistent solution, classify the comparison separately.

At each level record total energy, integrated electron count, exact grid dimensions, CHGCAR SHA-256, BaderKit on-grid charges, Henkelman on-grid charges, and the five historical QSQ perturbation responses. Report two perturbation-amplitude estimands separately if both are used: (i) fixed absolute amplitude inherited from the native field and (ii) level-specific float32 round-trip amplitude.

## No-retuning and failure rules

- Preserve `convergence_panel.csv` byte-for-byte.
- Do not replace a non-recoverable material with another material.
- Do not infer missing pseudopotential, k-point, spin, XC, or smearing settings from composition or defaults.
- Do not treat interpolated densities as DFT grid convergence.
- Do not use P3B outcomes to alter P1/P2/P3A or the original QSQ gate.
- Record every provenance-recovery failure and every later electronic-structure failure explicitly.
