# Supplementary Table S17 — Fourier-spectrum mechanism diagnostics

**Supplementary Table S17 | Operator-resolved Fourier diagnostics for realized-$L_\infty$-matched ZFP/SZ3 reconstructions.**

The mechanism population contains 457 matched pairs from 214 materials (914 reconstructions). Material-level centers are computed after within-material aggregation on the log scale unless otherwise stated. The exact multiplicative Hartree decomposition is evaluated pairwise; separately aggregated centers are descriptive and are not expected to multiply exactly.

| Diagnostic | Value | Interpretation |
|---|---:|---|
| Historical Hartree error ratio, ZFP/SZ3 | 0.0776221 | Reproduces the matched-pair Hartree effect used as the mechanism target |
| Nyquist-safe Hartree error ratio, ZFP/SZ3 | 0.0776219 | Shows that the codec effect is unchanged after restoring exact Hermitian parity |
| Total spectral-error-energy factor, $\sqrt{E_{\mathrm{ZFP}}/E_{\mathrm{SZ3}}}$ | 0.376 | Contribution from overall spectral error magnitude |
| Spectral Hartree-susceptibility factor, $\sqrt{S_{H,\mathrm{ZFP}}/S_{H,\mathrm{SZ3}}}$ | 0.203 | Contribution from frequency allocation under Hartree weighting |
| Material-median spectral-structure share of absolute log effect | 62.0% | Frequency allocation is the larger component of the matched-distortion Hartree effect |
| Low-$G$ error-energy fraction ratio, ZFP/SZ3 | 0.416 | ZFP places less reconstruction-error energy in long-wavelength modes |
| High-$G$ error-energy fraction ratio, ZFP/SZ3 | 0.626 | ZFP also differs at high $G$, but these modes are weakly weighted by the Hartree operator |
| Materials with lower ZFP spectral Hartree susceptibility | 99.5% | Direction of the susceptibility effect is nearly universal in the mechanism cohort |
| Materials with higher ZFP spectral centroid | 98.1% | ZFP error is shifted toward higher reciprocal-space frequencies |
| Materials with lower ZFP low-$G$ error-energy fraction | 99.1% | Long-wavelength suppression is consistent across materials |
| Maximum real-space/Fourier-space Parseval relative discrepancy | $1.30\times10^{-15}$ | Confirms numerical identity of the Nyquist-safe operator and spectral expression |

For the Nyquist-safe reciprocal-space set $\mathcal{G}_s$,

$$
E=\sum_{G\in\mathcal{G}_s}|\Delta\rho(G)|^2,
\qquad
W_H=\sum_{G\in\mathcal{G}_s}\frac{|\Delta\rho(G)|^2}{|G|^4},
\qquad
S_H=\frac{W_H}{E}.
$$

For every matched pair,

$$
R_H=
\sqrt{\frac{E_{\mathrm{ZFP}}}{E_{\mathrm{SZ3}}}}
\sqrt{\frac{S_{H,\mathrm{ZFP}}}{S_{H,\mathrm{SZ3}}}}.
$$

**Machine-readable evidence:** Fourier-spectrum mechanism audit in the repository reader-facing provenance index, including the matched-pair mechanism table, reconstruction spectral metrics, radial-spectrum summary, mechanism-ratio summary and audit summary.
