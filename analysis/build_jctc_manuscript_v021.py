from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
src = ROOT / "submission/JCTC_MANUSCRIPT_v0.2.md"
dst = ROOT / "submission/JCTC_MANUSCRIPT_v0.2.1.md"
text = src.read_text(encoding="utf-8")

text = text.replace(
    "**JCTC Article submission draft v0.2 — 2026-09-06**",
    "**JCTC Article submission draft v0.2.1 — 2026-09-06**",
    1,
)

old = "The development benchmark contains 254 DFT charge-density fields: 186 bulk materials and 68 slab systems. The stability analysis adds 37 AFLOW bulk systems and 28 NOMAD two-dimensional or vacuum-containing systems, producing a 319-system stability corpus."
new = "The development benchmark contains 254 DFT charge-density fields from the Materials Project [17]: 186 bulk materials and 68 slab systems. The stability analysis adds 37 AFLOW bulk systems [18] and 28 NOMAD two-dimensional or vacuum-containing systems [19], producing a 319-system stability corpus."
if old not in text:
    raise RuntimeError("benchmark provenance sentence not found")
text = text.replace(old, new, 1)

old = 'Bader partitions are computed with `baderkit` 0.10.2 using `method="ongrid"`.'
new = 'Bader partitions are computed with `baderkit` 0.10.2 [16] using `method="ongrid"`.'
if old not in text:
    raise RuntimeError("baderkit methods sentence not found")
text = text.replace(old, new, 1)

text = text.replace(
    "*Proc. VLDB Endow.* **2022/2023**, *16*, 697–710.",
    "*Proc. VLDB Endow.* **2022**, *16* (4), 697–710.",
    1,
)
text = text.replace(
    "*IEEE Trans. Vis. Comput. Graph.* **2024**, *30*, 1302–1312.",
    "*IEEE Trans. Vis. Comput. Graph.* **2024**, *30* (1), 1302–1312.",
    1,
)
text = text.replace(
    "*IEEE Trans. Vis. Comput. Graph.* **2026**, *32*, 6593–6609.",
    "*IEEE Trans. Vis. Comput. Graph.* **2026**, *32* (7), 6593–6609.",
    1,
)
text = text.replace(
    "*J. Chem. Inf. Model.* **2018**, *58*, 2092–2107.",
    "*J. Chem. Inf. Model.* **2018**, *58* (10), 2092–2107.",
    1,
)

refs = """
16. Weaver, S. M.; Warren, S. BaderKit: A Python Package for Grid-based Bader Charge Analysis. *J. Open Source Softw.* **2026**, *11* (121), 9943. DOI: 10.21105/joss.09943.
17. Horton, M. K.; Huck, P.; Yang, R. X.; et al. Accelerated Data-Driven Materials Science with the Materials Project. *Nat. Mater.* **2025**, *24*, 1522–1532. DOI: 10.1038/s41563-025-02272-0.
18. Curtarolo, S.; Setyawan, W.; Wang, S.; Xue, J.; Yang, K.; Taylor, R. H.; Nelson, L. J.; Hart, G. L. W.; Sanvito, S.; Buongiorno-Nardelli, M.; Mingo, N.; Levy, O. AFLOWLIB.ORG: A Distributed Materials Properties Repository from High-Throughput *ab Initio* Calculations. *Comput. Mater. Sci.* **2012**, *58*, 227–235. DOI: 10.1016/j.commatsci.2012.02.002.
19. Draxl, C.; Scheffler, M. The NOMAD Laboratory: From Data Sharing to Artificial Intelligence. *J. Phys. Mater.* **2019**, *2*, 036001. DOI: 10.1088/2515-7639/ab13bb.
"""
if "10.21105/joss.09943" not in text:
    text = text.rstrip() + "\n" + refs

required = [
    "JCTC Article submission draft v0.2.1",
    "Materials Project [17]",
    "AFLOW bulk systems [18]",
    "NOMAD two-dimensional or vacuum-containing systems [19]",
    "`baderkit` 0.10.2 [16]",
    "10.21105/joss.09943",
    "10.1038/s41563-025-02272-0",
    "10.1016/j.commatsci.2012.02.002",
    "10.1088/2515-7639/ab13bb",
]
for token in required:
    if token not in text:
        raise RuntimeError(f"missing token: {token}")

dst.write_text(text, encoding="utf-8")
print(f"Built {dst.relative_to(ROOT)}")
