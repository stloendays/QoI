# Hartree spectral mechanism audit

Status: **FREQUENCY_STRUCTURE_DOMINANT**

## Population

- Exact frozen ZFP/SZ3 matched pairs: **457**
- Materials: **214**
- Regenerated selected reconstructions: **914**

## Reproduction and operator audit

- Frozen matched-pair center: **0.0776221**
- Reproduced historical Hartree center: **0.0776221**
- Nyquist-safe Hartree center: **0.0776219**
- sqrt(Hartree-weighted spectral ratio): **0.0776219**
- maximum safe Parseval relative error: **1.296e-15**

## Spectral decomposition

- sqrt(total safe spectral-energy ratio), ZFP/SZ3: **0.375963**
- sqrt(spectral Hartree-susceptibility ratio), ZFP/SZ3: **0.202683**
- material-median absolute-log share from spectral susceptibility: **62.0%**
- materials with lower ZFP spectral Hartree susceptibility: **99.5%**
- materials with higher ZFP spectral centroid: **98.1%**
- materials with lower ZFP low-G energy fraction: **99.1%**

The safe Hartree ratio is exactly constrained by the Poisson-weighted spectrum. The separate total-energy and spectral-susceptibility factors indicate whether the codec effect is primarily an L2 error-magnitude effect, a frequency-allocation effect, or a combination of both.

The frozen manuscript is not modified by this audit.
