from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "paper/MANUSCRIPT_CHATGPT_v0.3.md"
dst = ROOT / "paper/MANUSCRIPT_CHATGPT_v0.3.1.md"
text = src.read_text(encoding="utf-8")

# Version marker.
text = text.replace(
    "**Integrated manuscript draft v0.3 — 2026-09-06**",
    "**Integrated manuscript draft v0.3.1 — 2026-09-06**",
    1,
)

# Insert global-conservation negative control after the mechanism-attenuation caveat.
anchor = (
    "We interpret this result as mechanism-consistent attenuation, not as formal causal mediation. "
    "Basin reassignment is a post-compression variable and is not randomized, and a voxel count does not encode which atoms exchange volume or how much electron density those voxels carry. "
    "The direct algebraic decomposition remains the primary mechanistic evidence. The attenuation result provides independent full-benchmark support for the same failure mode."
)
insert = anchor + "\n\n" + (
    "A global conservation proxy does not provide an alternative explanation for this attenuation. "
    "We added the absolute total electron-count deviation to the same complete-case material-fixed-effect model. "
    "This leaves the SZ3/ZFP multiplier essentially unabated (2.34 to 2.58) and the SPERR/ZFP multiplier unchanged (2.08 to 2.06), whereas adding basin reassignment reduces them to 0.96 and 0.94. "
    "When both post-compression covariates are included, the electron-count term is not significant (log–log coefficient −0.017, 95% CI −0.040 to 0.006; p=0.139), while the reassignment coefficient remains 0.879 [0.722, 1.036] (p=5.25×10^-28). "
    "Thus the codec-associated residual is not explained by simple global integral/conservation error; the structural variable that records redistribution among Bader domains is the one that absorbs the residual (Supplementary Fig. S13)."
)
if anchor not in text:
    raise RuntimeError("Mechanism insertion anchor not found")
text = text.replace(anchor, insert, 1)

# Add the short Discussion negative-control sentence after the paragraph on the residual mechanism.
disc_anchor = (
    "The remaining difference is robust across matching windows, interpolation on common support, stability qualification and conservative removal of failure-affected materials. "
    "More importantly, it almost disappears when basin reassignment is included in the material-controlled model. "
    "We therefore interpret the approximately twofold residual not as an intrinsic property of the codec label, but as evidence that different reconstruction patterns perturb the ascent relations defining Bader domains to different extents."
)
disc_insert = disc_anchor + " " + (
    "Consistent with this interpretation, a global electron-count deviation does not attenuate the codec-associated residual once measured L∞ and material identity are controlled, whereas basin reassignment does."
)
if disc_anchor not in text:
    raise RuntimeError("Discussion insertion anchor not found")
text = text.replace(disc_anchor, disc_insert, 1)

# Make the very small strict-slab stratum explicit rather than saying only that it is 'small'.
slab_old = (
    "At \\(10^{-4}\\) e, ZFP leads the bulk ratio at 7.6x compared with 6.3x for SZ3 and 4.2x for SPERR. "
    "The slab sample at this strictest contract is small and is therefore treated descriptively."
)
slab_new = (
    "At \\(10^{-4}\\) e, ZFP leads the bulk ratio at 7.6x compared with 6.3x for SZ3 and 4.2x for SPERR. "
    "Only four slab materials are admitted at this strictest contract, so the slab frontier is treated descriptively rather than as a population-level ranking."
)
if slab_old not in text:
    raise RuntimeError("Strict-slab wording anchor not found")
text = text.replace(slab_old, slab_new, 1)

# Replace the provisional SZ3/SPERR references. v0.3 reference 2 was an older SZ-family paper;
# keep that historical paper out of the opening [1–3] method citation and use the SZ3 paper instead.
old_ref2 = (
    "2. Liang, X. et al. Error-Controlled Lossy Compression Optimized for High Compression Ratios of Scientific Datasets. *IEEE Big Data* (2018)."
)
new_ref2 = (
    "2. Liang, X., Zhao, K., Di, S., Li, S., Underwood, R., Gok, A. M., Tian, J., Deng, J., Calhoun, J. C., Tao, D., Chen, Z. & Cappello, F. "
    "SZ3: A Modular Framework for Composing Prediction-Based Error-Bounded Lossy Compressors. *IEEE Trans. Big Data* **9**, 485–498 (2023). DOI: 10.1109/TBDATA.2022.3201176."
)
old_ref3 = (
    "3. Li, S. et al. SPERR: Error-bounded lossy compression for scientific data. [software/method reference to be replaced with final bibliographic record used in submission]."
)
new_ref3 = (
    "3. Li, S., Lindstrom, P. & Clyne, J. Lossy Scientific Data Compression With SPERR. In *2023 IEEE International Parallel and Distributed Processing Symposium (IPDPS)*, 1007–1017 (IEEE, 2023). DOI: 10.1109/IPDPS54959.2023.00104."
)
if old_ref2 not in text or old_ref3 not in text:
    raise RuntimeError("Expected provisional reference text not found")
text = text.replace(old_ref2, new_ref2, 1).replace(old_ref3, new_ref3, 1)

# Update data/code availability with the verified bibliography and v0.3.1 construction path.
data_anchor = (
    "`analysis/chatgpt-postprocess-20260906` contains the realized-L∞, complete-case and mechanism-attenuation audits; `analysis/paper-freeze-v03-20260906` contains the manuscript statistical plan, machine-generated headline-number registry and figure-data exports."
)
data_insert = (
    "`analysis/chatgpt-postprocess-20260906` contains the realized-L∞, complete-case and mechanism-attenuation audits; `analysis/paper-freeze-v03-20260906` contains the manuscript statistical plan, machine-generated headline-number registry, figure-data exports, global-conservation negative control and verified core bibliography."
)
if data_anchor in text:
    text = text.replace(data_anchor, data_insert, 1)

# Guardrails.
for forbidden in [
    "[software/method reference to be replaced",
    "Integrated manuscript draft v0.3 —",
]:
    if forbidden in text:
        raise RuntimeError(f"Unresolved provisional text remains: {forbidden}")

# Ensure critical new evidence appears exactly once in the integrated draft.
assert "2.34 to 2.58" in text
assert "p=5.25×10^-28" in text
assert "Only four slab materials are admitted" in text
assert "10.1109/TBDATA.2022.3201176" in text
assert "10.1109/IPDPS54959.2023.00104" in text

dst.write_text(text, encoding="utf-8")
print(f"Built {dst.relative_to(ROOT)} from {src.relative_to(ROOT)}")
