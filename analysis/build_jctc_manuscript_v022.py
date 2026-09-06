from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "submission/JCTC_MANUSCRIPT_v0.2.1.md"
out = ROOT / "submission/JCTC_MANUSCRIPT_v0.2.2.md"
text = src.read_text(encoding="utf-8")

text = text.replace(
    "**JCTC Article submission draft v0.2.1 — 2026-09-06**",
    "**JCTC Article submission draft v0.2.2 — 2026-09-06**",
    1,
)

old_p1 = (
    "Real-space electron-density fields are central intermediates in electronic-structure workflows. "
    "They support charge partitioning, bonding analysis, visualization, archival reuse, and increasingly data-driven post-processing. "
    "In high-throughput density-functional-theory (DFT) calculations, these volumetric fields can become a substantial storage and I/O burden even after the underlying electronic-structure calculation is complete. "
    "Error-bounded lossy compression offers a direct remedy by replacing exact storage with a controlled numerical approximation. "
    "General-purpose compressors such as ZFP, SZ3, and SPERR expose explicit pointwise error controls [1–3], making the reconstruction error easy to specify and verify."
)
new_p1 = (
    "Real-space electron-density fields are central intermediates in electronic-structure workflows. "
    "They support charge partitioning, bonding analysis, visualization, archival reuse, and increasingly data-driven post-processing. "
    "In high-throughput density-functional-theory (DFT) calculations, these volumetric fields can become a substantial storage and I/O burden even after the underlying electronic-structure calculation is complete. "
    "Chemistry-specific work has shown that volumetric trajectories, including electron-density grids, can be compressed efficiently without changing their values when a lossless representation is used [14]. "
    "Lossy compression addresses a different regime: it exchanges exact reconstruction for a controlled numerical perturbation and therefore requires a scientific criterion for deciding which perturbations remain acceptable. "
    "General-purpose compressors such as ZFP, SZ3, and SPERR expose explicit pointwise error controls [1–3], making the field-level reconstruction error easy to specify and verify."
)
if old_p1 not in text:
    raise SystemExit("Introduction paragraph 1 pattern not found")
text = text.replace(old_p1, new_p1, 1)

old_neighbor = (
    "This field-derived-domain structure also connects the problem to recent work on electron-density fidelity. "
    "Gong, Zhao, and Tang showed that machine-learned electron densities can exhibit downstream errors associated with real-space integration and grid discretization and developed adaptive integration to improve property evaluation [15]. "
    "Lossy compression creates a complementary setting: the starting density is already available, the perturbation is controlled by a codec, and the downstream partition can move as a consequence of reconstruction. "
    "The resulting question is not simply whether the density is close pointwise, but whether the reconstructed density remains a valid input to the chemical analysis."
)
new_neighbor = (
    "This field-derived-domain structure connects the problem to a growing JCTC literature on the downstream use of approximate electron densities. "
    "Gong, Zhao, and Tang showed that machine-learned electron densities can exhibit property errors associated with real-space integration and grid discretization and developed adaptive integration to improve downstream evaluation [15]. "
    "Nguyen and co-workers subsequently evaluated learned charge-conditioned electron densities through downstream Bader partitioning and electrostatic-potential analysis across a broad external benchmark [20]. "
    "Together, these studies establish that electron-density quality is most informative when it is assessed through the analyses that consume the field. "
    "Lossy compression creates a complementary controlled-perturbation setting: the reference density is already available, the reconstruction error can be measured directly, and the Bader partition can itself migrate after decompression. "
    "The resulting question is not simply whether the density is close pointwise, but what field-level guarantee is sufficient for a quantitative chemical-fidelity contract."
)
if old_neighbor not in text:
    raise SystemExit("Neighboring-work paragraph pattern not found")
text = text.replace(old_neighbor, new_neighbor, 1)

ref20 = (
    "20. Nguyen, T. M.; Tawfik, S. A.; Tran, T.; Venkatesh, S. ChargeFlow: Flow-Matching Refinement of Charge-Conditioned Electron Densities. "
    "*J. Chem. Theory Comput.* **2026**, *22* (16), 8481–8492. DOI: 10.1021/acs.jctc.6c00585.\n"
)
if "10.1021/acs.jctc.6c00585" not in text:
    text = text.rstrip() + "\n" + ref20

out.write_text(text, encoding="utf-8")
print(f"Built {out.relative_to(ROOT)}")
