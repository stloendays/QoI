# P3B NOMAD exact-input review — engineering note

The first exact-input review attempt (GitHub Actions run `34614319030`) is retained as a failed engineering/provenance audit. It did **not** run DFT, Bader grid-convergence calculations, or inspect any P3B scientific outcome.

## What failed

Two review-layer assumptions were too strict:

1. the script attempted `INCAR`, `KPOINTS`, and `OUTCAR` only at the entry raw root; some NOMAD entries expose the analysed CHGCAR at the entry path while the auxiliary VASP inputs are associated with another path in the same published upload or are represented only in the normalized archive;
2. the script required an explicit XC token such as `GGA`, `METAGGA`, `LHFCALC`, or `LDAU` in INCAR even when NOMAD's normalized archive and/or OUTCAR identify the exchange-correlation functional unambiguously. This incorrectly marked ordinary PBE calculations that rely on VASP defaults/PAW metadata as incomplete.

The run reached three systems before the path failure: `nomad-FPTBoTAPMQA8` and `nomad-FVlJ8rpkyGT5` were marked FAIL only by the explicit-INCAR-XC rule; `nomad-ZvTQv6REajO4` passed; the fourth system, `nomad-0xMhYZKiiVKL`, stopped on a raw-root `INCAR` 404.

## Allowed recovery changes

A recovery review may change only the **provenance extraction logic**:

- use NOMAD entry/upload metadata to locate raw auxiliary-file paths when available;
- accept exact normalized archive evidence for XC, pseudopotential identity, spin, k-point sampling, cutoff, smearing, and grid controls when the raw auxiliary file is not directly exposed;
- distinguish `RAW_EXACT`, `ARCHIVE_EXACT`, and `INCOMPLETE` evidence rather than forcing one raw-file layout;
- continue recording the frozen CHGCAR structure/grid/source identity as the density reference.

## Scientific quantities that remain frozen

The recovery review must not change the 24-system panel, the 12 slab candidates, original QSQ floors, perturbation seeds or amplitudes, Bader definitions, thresholds, P1/P2/P3A results, or the future P3B grid-refinement outcomes. No electronic-structure calculation is authorized by this note.
