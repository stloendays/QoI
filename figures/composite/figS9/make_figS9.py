"""Supplementary Figure S9 -- the reference densities the benchmark compresses: five development materials.

183 x 72 mm, one row of OVITO renders (render3d/build_gallery.py, densities regenerated from the
SHA-256-verified sources by render3d/prep_fields.py). One isolevel rule for all five: the surface encloses
the densest 15 % of each material's non-vacuum voxels. Bulk cells share one oblique camera; the slab is seen
along its in-plane lattice vector a. Each cell is framed to fill its slot (not to a common scale).
Under each render: source, grid, atoms and the frozen QSQ stability floor (stability/stability_floor_A1.csv
via benchmark/master_benchmark_full.csv).

    D:/Tools/pur_bridge_env/Scripts/python.exe make_figS9.py   -> FigS9.{svg,pdf,png}
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import figdata as D  # noqa: E402
import layout  # noqa: E402
from style import ELEM_ALL, INK, MID, RENDERS, Page, place_render  # noqa: E402

G = {g["material_id"]: g for g in json.load(open(os.path.join(RENDERS, "gallery_params.json")))}
bench = D.master()
meta = D.csv("materials_metadata.csv").set_index("material_id")
ELEMS = {"mp-676693": "K C N", "mp-560341": "Eu Si N O", "mp-1009084": "Be Sn As", "mp-1007755": "Hf Au",
         "nomad-9jQMkfdCbgX_": "Co"}
ORDER = ("mp-676693", "mp-560341", "mp-1009084", "mp-1007755", "nomad-9jQMkfdCbgX_")
PRETTY = {"KCN": "KCN", "EuSi2(NO)2": r"EuSi$_2$(NO)$_2$", "BeSnAs2": r"BeSnAs$_2$", "HfAu": "HfAu",
          "Co20": r"Co$_{20}$ slab"}


def sci(v):
    m, e = ("%.1e" % v).split("e")
    return r"%s$\times10^{%d}$" % (m, int(e))


pg = Page(183.0, 72.0)
xs, ws = (3.0, 40.0, 77.0, 114.0, 151.0), (35.0, 35.0, 35.0, 35.0, 29.0)
for x, w, mid in zip(xs, ws, ORDER):
    g, m = G[mid], meta.loc[mid]
    floor = float(bench[bench.material_id == mid].stability_floor_A1_e.iloc[0])
    place_render(pg, "gallery_%s.png" % mid, x, 21.0, w, 49.0, anchor="S")
    xc = (x + w / 2) / pg.W
    src = "Materials Project" if m.source == "Materials Project" else "NOMAD surface"
    pg.fig.text(xc, 19.5 / pg.H, PRETTY[g["formula"]], fontsize=6.4, fontweight="bold", ha="center", va="top")
    pg.fig.text(xc, 16.3 / pg.H, "%s, %s" % (mid, src), fontsize=5.2, color=MID, ha="center", va="top")
    pg.fig.text(xc, 13.4 / pg.H, "%s grid, %d atoms" % (g["ngrid"].replace("x", "\u00d7"), g["natoms"]),
                fontsize=5.4, color=INK, ha="center", va="top")
    pg.fig.text(xc, 10.5 / pg.H, r"isosurface %.2f e $\AA^{-3}$" % g["iso_e_per_A3"], fontsize=5.4, color=INK,
                ha="center", va="top")
    pg.fig.text(xc, 7.6 / pg.H, r"QSQ floor $f_m$ = %s e" % sci(floor), fontsize=5.4, color=INK,
                ha="center", va="top")
    el = ELEMS[mid].split()
    cv = pg.canvas(x, 1.0, w, 4.0)
    x0 = w / 2 - 3.6 * (len(el) - 1)
    for k, s in enumerate(el):
        cv.scatter([x0 + 7.2 * k - 1.0], [2.0], s=8, color=ELEM_ALL[s], lw=0)
        cv.text(x0 + 7.2 * k + 0.2, 2.0, s, fontsize=5.2, va="center")
    print(mid, g["formula"], "floor", floor)

layout.audit(pg.fig)
pg.save(HERE, "FigS9")
