# Reference audit — manuscript v0.3

Date: 2026-09-06

Purpose: replace provisional compressor citations with verified bibliographic records before the final manuscript is converted to journal style.

## Core compressor references for the Introduction

### ZFP
Diffenderfer, J., Fox, A. L., Hittinger, J. A. F., Sanders, G. & Lindstrom, P. G. **Error Analysis of ZFP Compression for Floating-Point Data.** *SIAM Journal on Scientific Computing* **41**, A1867–A1898 (2019). DOI: `10.1137/18M1168832`.

Role in manuscript: mathematical/error-analysis reference for ZFP and error-bounded floating-point compression.

### SZ3
Liang, X., Zhao, K., Di, S., Li, S., Underwood, R., Gok, A. M., Tian, J., Deng, J., Calhoun, J. C., Tao, D., Chen, Z. & Cappello, F. **SZ3: A Modular Framework for Composing Prediction-Based Error-Bounded Lossy Compressors.** *IEEE Transactions on Big Data* **9**(2), 485–498 (2023; online publication 23 August 2022). DOI: `10.1109/TBDATA.2022.3201176`.

Role in manuscript: primary method reference for SZ3. This should replace the provisional use of the earlier 2018 generic SZ/error-controlled paper as reference [2] when the sentence specifically names SZ3.

### SPERR
Li, S., Lindstrom, P. & Clyne, J. **Lossy Scientific Data Compression With SPERR.** In *2023 IEEE International Parallel and Distributed Processing Symposium (IPDPS)*, 1007–1017 (IEEE, 2023). DOI: `10.1109/IPDPS54959.2023.00104`.

Role in manuscript: primary method reference for SPERR. This replaces the placeholder reference in manuscript v0.3.

## Optional supporting SZ references

These should not replace the SZ3 method citation, but can be used when discussing the evolution of prediction/interpolation-based SZ methods.

- Liang, X., Di, S., Tao, D., Li, S., Li, S., Guo, H., Chen, Z. & Cappello, F. **Error-Controlled Lossy Compression Optimized for High Compression Ratios of Scientific Datasets.** *2018 IEEE International Conference on Big Data*, 438–447. DOI: `10.1109/BigData.2018.8622520`.
- Zhao, K., Di, S., Dmitriev, M., Tonellot, T.-L. D., Chen, Z. & Cappello, F. **Optimizing Error-Bounded Lossy Compression for Scientific Data by Dynamic Spline Interpolation.** *2021 IEEE 37th International Conference on Data Engineering (ICDE)*, 1643–1654. DOI: `10.1109/ICDE51399.2021.00145`.

## Required correction to v0.3 manuscript reference ordering

The opening sentence names `ZFP, SZ3 and SPERR` and cites `[1–3]`. Therefore the cleanest final ordering is:

1. ZFP error-analysis paper above.
2. SZ3 IEEE TBD paper above.
3. SPERR IPDPS paper above.

The 2018 and 2021 SZ-family papers can be inserted later if specific algorithm-history statements require them, which would renumber downstream references during final citation-manager formatting.

## Audit status

- ZFP core reference: **verified**.
- SZ3 core reference: **verified**.
- SPERR core reference: **verified**.
- Bader/Henkelman reference already used in manuscript: DOI `10.1016/j.commatsci.2005.04.010`; retain.
- Jiao et al. QoI-preserving reference: DOI `10.14778/3574245.3574255`; retain.
- TopoSZ: DOI `10.1109/TVCG.2023.3326920`; retain.

Before journal submission, references should be imported through a citation manager / BibTeX rather than manually renumbered in Markdown.
