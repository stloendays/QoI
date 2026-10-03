"""Stage 2: SI gallery -- reference densities of five development materials (render-venv).

    D:/Tools/render-venv/Scripts/python.exe build_gallery.py [--preview]   -> renders/gallery_*.png

One rule for every material: the isolevel encloses the densest 15 % of the non-vacuum voxels
(rho > 1e-3 e/A^3), so the surfaces are comparable across chemistries whose absolute densities differ. Bulk cells share one
oblique camera direction; the slab is viewed along its in-plane lattice vector a, so the line of sight
lies in the surface plane (a side view defined by the cell). Each cell is framed to fill its render.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scene as S  # noqa: E402

DATA = Path(r"D:\Research\QoI-ext-cache\figure3d")
OUT = HERE / "renders"
SIZE_BULK, SIZE_SLAB = (1400, 1400), (900, 2400)
if "--preview" in sys.argv:
    OUT = OUT / "preview"
    SIZE_BULK, SIZE_SLAB = (500, 500), (300, 800)
OUT.mkdir(parents=True, exist_ok=True)

ENCLOSED = 0.15
CAM = (-0.55, -1.0, -0.42)
MATERIALS = ("mp-676693", "mp-560341", "mp-1009084", "mp-1007755", "nomad-9jQMkfdCbgX_")


def build(mid):
    from ovito.pipeline import Pipeline, StaticSource
    d = np.load(DATA / f"gallery_{mid}.npz")
    L, frac, species = d["lattice"], d["frac"], [str(s) for s in d["species"]]
    skip = tuple(s for s in set(species) if s in ("K", "Eu", "Hf", "Au", "Co", "Sn"))
    pairs = S.short_pairs(L, frac, species, cutoff=2.0 if "Si" in species else 1.5, skip=skip + ("Co",))
    cart = (frac % 1.0) @ L
    # cell edges scale with the cell, so every framed-to-fill render shows the same line weight
    atoms = S.base_data(L, cart, species, bonds=pairs, cell_width=0.0035 * float(np.linalg.norm(L, axis=1).max()))
    g = S.base_data(L, cart, species, show_cell=False)
    g.particles.vis.enabled = False
    S.add_grid(g, L, "rho", d["rho"])
    a = Pipeline(source=StaticSource(data=atoms))
    r = d["rho"]
    iso_level = float(np.quantile(r[r > 1e-3], 1 - ENCLOSED))
    iso = S.iso_pipeline(g, "rho", iso_level, S.RHO_SURF, transparency=0.35)
    if str(d["system_type"]) == "slab":
        cam = tuple(np.asarray(L[0]) / np.linalg.norm(L[0]))
        S.render([a, iso], OUT / f"gallery_{mid}.png", cam, L, size=SIZE_SLAB, fov_pad=1.04)
    else:
        S.render([a, iso], OUT / f"gallery_{mid}.png", CAM, L, size=SIZE_BULK)
    print(mid, str(d["formula"]), str(d["ngrid"]), "bonds", len(pairs), "iso %.3f e/A^3" % iso_level)
    return dict(material_id=mid, formula=str(d["formula"]), ngrid=str(d["ngrid"]), natoms=len(species),
                system_type=str(d["system_type"]), iso_e_per_A3=iso_level)


if __name__ == "__main__":
    import json
    meta = [build(m) for m in MATERIALS]
    json.dump(meta, open(HERE / "renders" / "gallery_params.json", "w"), indent=1)
