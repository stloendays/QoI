# Verification addendum to `QOAC_PROGRAM_PRIOR_ART_AUDIT_20261006.md` (2026-10-06)

The cloud audit could not open any source (egress-blocked). The three highest-risk items it flagged were
re-checked from an unrestricted network by opening the abstract pages directly.

| item | verified facts | consequence |
|---|---|---|
| FFCz, arXiv:2601.01596 (C. Ren, R. Underwood, S. Di, E. Kutay, Z. Lukić, A. Yener, F. Cappello, H. Guo; submitted 2026-01-04) | Post-processing correction of SZ3/ZFP/SPERR output; frequency-domain errors written as linear combinations of spatial errors; iterative projection onto spatial and frequency-domain error-bound constraints; data: cosmology, X-ray diffraction, combustion, EEG. No downstream physical operator defines a weighting in the abstract. | Closest spectral prior art. It bounds spectra after decompression; it does not design the quantizer in a physical-operator metric. The QOAC-H distinction (operator symbol defines the quantization law, decoded field recertified under the downstream operator) stands. FFCz must be cited and discussed. |
| BlockMGARD, arXiv:2609.00205 (Y. Li, Q. Gong, Q. Liu, J. Lee, N. Podhorszki, S. Klasky, X. Liang, J. Chen; submitted 2026-08-31) | Region-of-interest error control on GPUs on top of a multilevel MGARD-type decomposition. The abstract does not describe operator-norm (negative-Sobolev) allocation or Poisson-type operators. | Not a close match for C1/C2 on the abstract; full text still to be read before submission. |
| Compression Safeguards, EGUsphere preprint, DOI 10.5194/egusphere-2026-4266 (J. Tyree, R. Underwood, C. Bouvier, D. Köhler, T. Reichelt, P. Dueben, S. Faghih-Naini, H. Järvinen, M. Klöwer) | Wraps a compressor with pointwise and QoI-based safeguards, including regionally varying error bounds on derived quantities; corrections stored as binary differences, optionally distributed separately. The abstract does not state exact preservation of sums over a user-supplied partition. | Supports the audit verdict that C3 (post-decode constraint correction) is methodologically incremental: credit Lee et al. 2022 and Compression Safeguards. |

The DOI of Compression Safeguards (10.5194/egusphere-2026-4266) is now verified. Every other UNVERIFIED tag in the
main audit stands until the full text has been read.
