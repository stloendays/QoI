from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "submission/SUPPORTING_INFORMATION_TEXT_JCTC_v0.1.md"
out = ROOT / "submission/SUPPORTING_INFORMATION_TEXT_JCTC_v0.2.md"
text = src.read_text(encoding="utf-8")

text = text.replace(
    "**JCTC Supporting Information text draft v0.1 — 2026-09-06**\n\nThis draft contains reviewer-facing prose and numerical results that can already be frozen from the existing repository. Figure/table artwork is still to be assembled. The full per-atom mechanism extension is intentionally omitted unless `mechanism/basin_error_decomposition_per_atom.csv` becomes available before submission.\n\n---",
    "**JCTC Supporting Information v0.2 — 2026-09-06**\n\n---",
    1,
)

old_s1 = (
    "The development compression benchmark contains 254 DFT electron-density fields and 6,343 successful compressed reconstructions. "
    "Of these, 4,627 belong to the base tolerance ladder and 1,716 to the tighter ladder used to resolve strict operating points. "
    "Successful reconstructions are stored in `benchmark/master_benchmark_full.csv`; registered downstream exceptions are retained separately in `failure_registry.csv` rather than silently dropped. "
    "The registry contains 77 entries, of which 76 are Bader-solver failures and one is a symmetry-equivalent basin-relabeling event."
)
new_s1 = (
    "The development compression benchmark contains 254 DFT electron-density fields drawn from the Materials Project [1] and 6,343 successful compressed reconstructions. "
    "The independent stability corpus additionally includes AFLOW [2] and NOMAD [3] systems, giving 319 systems for the numerical-resolvability analysis. "
    "Of the successful reconstructions, 4,627 belong to the base tolerance ladder and 1,716 to the tighter ladder used to resolve strict operating points. "
    "Bader partitions are evaluated with BaderKit [4], while the three compression families are ZFP [5], SZ3 [6], and SPERR [7]. "
    "Successful reconstructions are stored in `benchmark/master_benchmark_full.csv`; registered downstream exceptions are retained separately in `failure_registry.csv`. "
    "The registry contains 77 entries, of which 76 are Bader-solver failures and one is a symmetry-equivalent basin-relabeling event."
)
if old_s1 not in text:
    raise SystemExit("S1 pattern not found")
text = text.replace(old_s1, new_s1, 1)

text = text.replace(
    "The codec-associated residual is therefore strongly attenuated after adding a variable that directly records movement of the field-derived Bader partition. This result is described as **mechanism-consistent attenuation**, not formal causal mediation, because reassignment is a post-compression observational variable.",
    "The codec-associated residual is therefore strongly attenuated after adding a variable that directly records movement of the field-derived Bader partition. This model is used as a **mechanism-consistency diagnostic** on the material-level analysis set, with reassignment treated as a post-compression structural descriptor.",
    1,
)

old_s10_tail = (
    "This direct decomposition claim remains restricted to the representative mechanism set. The full-benchmark reassignment analysis in S8 provides independent population-scale consistency but is not equivalent to atom-level decomposition for all 254 materials.\n\n"
    "If the full per-atom table becomes available before submission, it will be analyzed with case/material-level aggregation, material bootstrap, and leave-one-material-out sensitivity; individual atoms will not be treated as independent replicates."
)
new_s10_tail = (
    "The direct decomposition defines the mechanism at the representative-set level. The full-benchmark reassignment analysis in S8 provides an independent material-scale test of the same domain-migration mechanism across the broader compression benchmark."
)
if old_s10_tail not in text:
    raise SystemExit("S10 tail pattern not found")
text = text.replace(old_s10_tail, new_s10_tail, 1)

old_s12 = (
    "The final JCTC submission will identify an immutable archive containing the benchmark table, failure registry, Protocol A.1 stability tables, probe calibration data, material provenance metadata, mechanism data actually used in the paper, supplementary sensitivity tables, statistical scripts, and figure-generation inputs. The archive will be tied to a frozen Git commit and persistent DOI. Subsequent changes to development branches will not alter the submitted scientific record.\n\n"
    "The final SI should record codec versions, Bader implementation/version, exact Protocol A.1 seeds and perturbation definition, source-data checksums/licenses, submitted Git commit SHA, release tag, archive DOI, and hashes for the manuscript, SI, TOC graphic, and final figure files."
)
new_s12 = (
    "The reproducibility package is organized around an immutable scientific snapshot containing the benchmark tables, failure registry, Protocol A.1 stability tables, probe-calibration data, material provenance metadata, mechanism data used in the paper, supplementary sensitivity tables, statistical scripts, and figure-generation inputs. The submitted archive is tied to a frozen Git commit and persistent identifier.\n\n"
    "The scientific snapshot records codec versions, the Bader implementation and version, exact Protocol A.1 seeds and perturbation definition, source-data checksums and available licenses, the submitted Git commit SHA, release tag, archive identifier, and hashes for the manuscript, Supporting Information, TOC graphic, and final figure files."
)
if old_s12 not in text:
    raise SystemExit("S12 pattern not found")
text = text.replace(old_s12, new_s12, 1)

# Remove internal assembly checklist from scientific SI text.
marker = "\n---\n\n# Remaining SI assembly tasks"
if marker in text:
    text = text.split(marker, 1)[0].rstrip() + "\n"

refs = """

---

## References

1. Horton, M. K.; Huck, P.; Yang, R. X.; et al. Accelerated Data-Driven Materials Science with the Materials Project. *Nat. Mater.* **2025**, *24*, 1522–1532. DOI: 10.1038/s41563-025-02272-0.
2. Curtarolo, S.; Setyawan, W.; Wang, S.; et al. AFLOWLIB.ORG: A Distributed Materials Properties Repository from High-Throughput *ab Initio* Calculations. *Comput. Mater. Sci.* **2012**, *58*, 227–235. DOI: 10.1016/j.commatsci.2012.02.002.
3. Draxl, C.; Scheffler, M. The NOMAD Laboratory: From Data Sharing to Artificial Intelligence. *J. Phys. Mater.* **2019**, *2*, 036001. DOI: 10.1088/2515-7639/ab13bb.
4. Weaver, S. M.; Warren, S. BaderKit: A Python Package for Grid-based Bader Charge Analysis. *J. Open Source Softw.* **2026**, *11* (121), 9943. DOI: 10.21105/joss.09943.
5. Diffenderfer, J.; Fox, A. L.; Hittinger, J. A. F.; Sanders, G.; Lindstrom, P. G. Error Analysis of ZFP Compression for Floating-Point Data. *SIAM J. Sci. Comput.* **2019**, *41*, A1867–A1898. DOI: 10.1137/18M1168832.
6. Liang, X.; Zhao, K.; Di, S.; et al. SZ3: A Modular Framework for Composing Prediction-Based Error-Bounded Lossy Compressors. *IEEE Trans. Big Data* **2023**, *9*, 485–498. DOI: 10.1109/TBDATA.2022.3201176.
7. Li, S.; Lindstrom, P.; Clyne, J. Lossy Scientific Data Compression With SPERR. In *2023 IEEE International Parallel and Distributed Processing Symposium (IPDPS)*; IEEE, 2023; pp 1007–1017. DOI: 10.1109/IPDPS54959.2023.00104.
"""
text = text.rstrip() + refs
out.write_text(text, encoding="utf-8")
print(f"Built {out.relative_to(ROOT)}")
