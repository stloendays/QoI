from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "paper/MANUSCRIPT_CHATGPT_v0.3.1.md"
outdir = ROOT / "submission"
outdir.mkdir(exist_ok=True)
dst = outdir / "JCTC_MANUSCRIPT_v0.1.md"

text = src.read_text(encoding="utf-8")

old_title = "# Pointwise Error Bounds Do Not Define Chemical Fidelity: Stability and Domain Migration in Lossy-Compressed Electron Densities"
new_title = "# Chemical Fidelity beyond Pointwise Error Bounds: Stability and Bader-Domain Migration in Lossy-Compressed Electron Densities"
if old_title not in text:
    raise RuntimeError("Expected v0.3.1 title not found")
text = text.replace(old_title, new_title, 1)

# Replace the internal branch-status preamble with a submission-draft marker.
text = re.sub(
    r"\*\*Integrated manuscript draft v0\.3\.1 — 2026-09-06\*\*\n\nThis branch-only draft.*?committed\.\n\n",
    "**JCTC Article submission draft v0.1 — 2026-09-06**\n\n",
    text,
    count=1,
    flags=re.S,
)

# JCTC-facing abstract: chemistry/data-methodology first, while preserving frozen headline results.
new_abstract = r"""## Abstract

Reliable reuse of compressed electronic-structure data requires a fidelity criterion at the level of the downstream analysis, not only the stored field. We establish such a criterion for Bader charges computed from density-functional-theory electron densities. Across 6,343 successful reconstructions of 254 materials compressed with SZ3, ZFP, and SPERR, re-deriving the Bader partition after decompression yields larger charge errors than integrating over reference basins in 99.7% of 4,627 base-ladder cases. In a representative 12-material mechanism set, direct decomposition gives a median bounded domain-migration contribution of 0.995. Equal requested tolerances are also not equal perturbations: ZFP realizes a median 0.158 of its requested L-infinity bound, whereas SZ3 and SPERR nearly saturate theirs. Nevertheless, after matching realized L-infinity error and restricting to systems whose Bader charges are numerically resolvable to 10^-3 e, conservative complete-case comparisons retain 1.82-fold and 2.00-fold Bader-error ratios for SZ3/ZFP and SPERR/ZFP, respectively. These residuals collapse after accounting for basin reassignment but not global electron-count deviation. A calibrated five-seed stability protocol further finds 41.4% of 319 systems non-evaluable at 10^-3 e and 79.9% at 10^-4 e. The resulting workflow measures realized field error, re-executes field-dependent partitioning, and certifies downstream fidelity only where the chemical observable is numerically resolvable.
"""
text = re.sub(r"## Abstract\n.*?\n## Introduction\n", new_abstract + "\n## Introduction\n", text, count=1, flags=re.S)

# Chemistry-centric opening for JCTC.
old_intro_open = (
    "Scientific simulations and instruments increasingly generate volumetric fields at rates that make storage, transfer and repeated analysis expensive. "
    "Error-bounded lossy compression addresses this pressure by allowing controlled numerical distortion in exchange for substantial reductions in data volume. "
    "Scientific compressors such as ZFP, SZ3 and SPERR expose pointwise-error controls that are attractive because they are explicit, inexpensive to verify and largely independent of the downstream application [1–3]."
)
new_intro_open = (
    "Real-space electron-density fields are central intermediates in electronic-structure workflows: they support charge partitioning, bonding analysis, visualization, archival reuse, and increasingly data-driven post-processing. "
    "For high-throughput density-functional-theory calculations, retaining such volumetric fields can impose substantial storage and I/O costs even when the underlying wavefunction calculation is no longer needed. "
    "Error-bounded lossy compression offers a natural remedy by trading controlled numerical distortion for reduced data volume. General-purpose compressors such as ZFP, SZ3, and SPERR expose explicit pointwise-error controls [1–3], but the chemical meaning of those controls depends on how downstream observables respond to the reconstructed field."
)
if old_intro_open not in text:
    raise RuntimeError("Expected introduction opening not found")
text = text.replace(old_intro_open, new_intro_open, 1)

# Insert the closest JCTC electron-density fidelity work and explicitly distinguish the present problem.
# Existing v0.3.1 reference 14 is Brehm & Thomas (2018), so MARGR is reference 15.
anchor = (
    "Compression can therefore alter a Bader charge through two channels: density values can change inside an otherwise fixed basin, and the basin assignment itself can change. "
    "The second contribution is a domain error. If an evaluation reuses the original basins when scoring a reconstructed density, it suppresses this channel by construction and no longer reproduces the analysis that would be performed on the decompressed field."
)
insert = anchor + "\n\n" + (
    "Recent work on machine-learned electron densities has independently highlighted a downstream-fidelity gap caused by real-space integration and grid discretization, and has addressed that problem through adaptive real-space integration [15]. "
    "The present setting is complementary but distinct: the electron density is a controlled lossy reconstruction of an existing electronic-structure field, and the dominant error channel studied here arises because the integration domains themselves are re-derived from that perturbed field. "
    "This distinction makes the partitioning operation part of the fidelity contract rather than a fixed numerical quadrature step."
)
if anchor not in text:
    raise RuntimeError("Bader introduction anchor not found")
text = text.replace(anchor, insert, 1)

# Tighten the final Introduction paragraph around a computational-chemistry methodology contribution.
old_here = (
    "Here we evaluate scientific compression through three distinct layers: field reconstruction, QoI resolvability and downstream fidelity. "
    "We benchmark SZ3, ZFP and SPERR on 254 DFT electron-density fields spanning bulk and slab systems; re-run Bader partitioning on every reconstruction; measure the actual L∞ error rather than assuming that equal requested tolerance implies equal perturbation; and qualify every material against a calibrated, five-seed stability protocol before certification. "
    "We then use a direct error decomposition and full-benchmark basin-reassignment statistics to identify how reconstruction differences propagate into charge error. The resulting framework does not select a universally best codec. Instead, it distinguishes a mathematical reconstruction guarantee from the conditions required for a defensible scientific fidelity claim."
)
new_here = (
    "Here we develop a stability-qualified evaluation protocol for lossy-compressed electronic-structure fields with three explicit layers: field reconstruction, chemical-observable resolvability, and downstream fidelity. "
    "We benchmark SZ3, ZFP, and SPERR on 254 DFT electron-density fields spanning bulk and slab systems; re-run Bader partitioning on every reconstruction; measure realized L-infinity error rather than treating equal requested tolerance as equal perturbation; and qualify each material against a calibrated five-seed stability protocol before certification. "
    "Direct error decomposition and full-benchmark basin-reassignment statistics then identify how reconstruction differences propagate into charge error. The objective is not a universal codec ranking, but a computational-chemistry contract for deciding when compressed electron densities remain valid inputs to a field-dependent analysis."
)
if old_here not in text:
    raise RuntimeError("Expected final Introduction paragraph not found")
text = text.replace(old_here, new_here, 1)

# Replace the internal development-oriented availability paragraph with a JCTC-policy-facing statement.
old_avail = (
    "## Data and code availability\n\n"
    "The frozen data release, Protocol A.1, archived Protocol A, failure registry, provenance records, benchmark tables and claim–evidence matrix are stored in the `stloendays/QoI` repository. Reviewer-facing statistical post-processing is isolated from the frozen `main` branch. `analysis/chatgpt-postprocess-20260906` contains the realized-L∞, complete-case and mechanism-attenuation audits; `analysis/paper-freeze-v03-20260906` contains the manuscript statistical plan, machine-generated headline-number registry, figure-data exports, global-conservation negative control and verified core bibliography."
)
new_avail = (
    "## Data and Software Availability\n\n"
    "The benchmark data, Protocol A.1 stability measurements, failure registry, provenance metadata, mechanism data used in the manuscript, supplementary sensitivity tables, and statistical analysis scripts are maintained in the project repository at https://github.com/stloendays/QoI. A versioned archival release with a persistent identifier will be frozen before formal submission so that the published record maps to an immutable data-and-software snapshot. Source URLs, checksums, and licensing metadata for the underlying material fields are recorded in `materials_metadata.csv`."
)
if old_avail not in text:
    raise RuntimeError("Expected data/code availability paragraph not found")
text = text.replace(old_avail, new_avail, 1)

# Add the recent JCTC electron-density integration paper as reference 15.
ref15 = (
    "15. Gong, J.; Zhao, Z.; Tang, B. Z. Bridging Machine Learning and Electron Density Theory with Adaptive Real-Space Integration. "
    "*J. Chem. Theory Comput.* (2026). DOI: 10.1021/acs.jctc.6c01124."
)
if "10.1021/acs.jctc.6c01124" not in text:
    text = text.rstrip() + "\n" + ref15 + "\n"

# Submission guardrails.
for token in [
    "branch-only draft",
    "until `mechanism/basin_error_decomposition_per_atom.csv` is committed",
    "first to show that pointwise",
]:
    if token.lower() in text.lower():
        raise RuntimeError(f"Submission text still contains internal/overclaim token: {token}")

required = [
    "JCTC Article submission draft v0.1",
    "6,343",
    "99.7%",
    "0.995",
    "1.82-fold",
    "2.00-fold",
    "41.4%",
    "10.1021/acs.jctc.6c01124",
    "field-dependent analysis",
    "## Data and Software Availability",
    "[15]",
]
for token in required:
    if token not in text:
        raise RuntimeError(f"Required JCTC submission token missing: {token}")

dst.write_text(text, encoding="utf-8")
print(f"Built {dst.relative_to(ROOT)}")
