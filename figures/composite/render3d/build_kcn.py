"""Stage 2: OVITO renders of KCN (mp-676693) for Figs. 1, 5 and 7.

    D:/Tools/render-venv/Scripts/python.exe build_kcn.py [name ...]   -> renders/kcn_*.png

Every render uses the same orthographic camera, so the panels of one figure can be
read against each other voxel for voxel.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scene as S  # noqa: E402

DATA = Path(r"D:\Research\QoI-ext-cache\figure3d")
OUT = HERE / "renders"
OUT.mkdir(exist_ok=True)

d = np.load(DATA / "mp-676693_fields.npz")
prov = json.loads((DATA / "mp-676693_provenance.json").read_text(encoding="utf-8"))
L, frac, species = d["lattice"], d["frac"], list(d["species"])
# The MP file's C/N atoms form a periodic chain C-N-N-C-C-N-N-C (1.36-1.47 A); drawn as the file gives it.
pairs = S.short_pairs(L, frac, species)
assert len(pairs) == 7, pairs
cart = (frac % 1.0) @ L
CAM = (-0.55, -1.0, -0.42)          # oblique view down the long diagonal; same for every KCN render
RHO_ISO = 0.60                      # e / A^3, reference density
# One delta-rho isolevel for the matched ZFP/SZ3 pair (Fig. 7): 0.5 x the smaller realized L-inf of the pair
L_SZ3 = prov["rows"]["sz3_1e-4"]["realized_Linf_rho_e_per_A3"]
L_ZFP = prov["rows"]["zfp_1e-3"]["realized_Linf_rho_e_per_A3"]
DRHO_ISO = 0.5 * min(L_SZ3, L_ZFP)


def atoms_only(show_cell=True):
    return S.base_data(L, cart, species, bonds=pairs, show_cell=show_cell)


def grid_data(name, arr):
    dc = S.base_data(L, cart, species, show_cell=False)
    dc.particles.vis.enabled = False
    S.add_grid(dc, L, name, arr)
    return dc


def rho():
    from ovito.pipeline import Pipeline, StaticSource
    a = Pipeline(source=StaticSource(data=atoms_only()))
    iso = S.iso_pipeline(grid_data("rho", d["rho"]), "rho", RHO_ISO, S.RHO_SURF, transparency=0.35)
    S.render([a, iso], OUT / "kcn_rho.png", CAM, L)


def drho(tag, stem):
    from ovito.pipeline import Pipeline, StaticSource
    a = Pipeline(source=StaticSource(data=atoms_only()))
    arr = d["drho_" + tag]
    pos = S.iso_pipeline(grid_data("dp", arr), "dp", DRHO_ISO, S.POS, cap=True)
    neg = S.iso_pipeline(grid_data("dn", -arr), "dn", DRHO_ISO, S.NEG, cap=True)
    S.render([a, pos, neg], OUT / stem, CAM, L)


def basins():
    """Reference isosurface coloured by the Bader basin (owning atom's element) of each vertex."""
    from ovito.pipeline import Pipeline, StaticSource
    from ovito.modifiers import CreateIsosurfaceModifier
    a = Pipeline(source=StaticSource(data=atoms_only()))
    dc = grid_data("rho", d["rho"])
    g = dc.grids["rho"]
    g_ = dc.grids_["rho"]
    g_.create_property("basin", data=d["labels_ref"].astype(np.float64).ravel(order="F"))
    p = Pipeline(source=StaticSource(data=dc))
    m = CreateIsosurfaceModifier(operate_on="voxels:rho", property="rho", isolevel=RHO_ISO, transfer_values=True)
    p.modifiers.append(m)
    cols = np.array([S.ELEMENT[s][0] for s in species] + [(0.8, 0.8, 0.8)])

    def colour(frame, data):
        mesh = data.surfaces_["isosurface_"]
        lab = np.rint(np.asarray(mesh.vertices["basin"])).astype(int).clip(0, len(species))
        mesh.vertices_.create_property("Color", data=cols[lab])
    p.modifiers.append(colour)
    m.vis.show_cap = True
    m.vis.cap_color = (0.86, 0.87, 0.90)   # section planes are neutral: basin colour lives on the surface only
    m.vis.smooth_shading = True
    S.render([a, p], OUT / "kcn_basins.png", CAM, L)


def reassigned(tag, stem, big):
    """Atoms + faint reference isosurface + the voxels whose Bader owner changed (RED)."""
    from ovito.pipeline import Pipeline, StaticSource
    a = Pipeline(source=StaticSource(data=atoms_only()))
    iso = S.iso_pipeline(grid_data("rho", d["rho"]), "rho", RHO_ISO, S.RHO_SURF, transparency=0.75)
    moved = np.argwhere(d["labels_" + tag] != d["labels_ref"])
    shape = np.array(d["rho"].shape)
    pts = ((moved + 0.5) / shape) @ L if len(moved) else np.zeros((0, 3))
    from ovito.data import DataCollection
    dc = DataCollection()
    pp = dc.create_particles(count=len(pts))
    pp.create_property("Position", data=pts)
    pp.create_property("Color", data=np.tile(S.RED, (len(pts), 1)))
    pp.create_property("Radius", data=np.full(len(pts), big))
    v = Pipeline(source=StaticSource(data=dc))
    S.render([a, iso, v], OUT / stem, CAM, L)
    print(tag, "reassigned voxels", len(pts))


# ---- Hartree-potential error, with the paper's own Nyquist-safe Poisson operator -------------------------
sys.path.insert(0, str(HERE.parents[2] / "analysis" / "hartree_spectral_mechanism"))
import run_shard as H  # noqa: E402

HARTREE_EV_A = 14.399645   # e^2 / (4 pi eps0) in eV A. safe_hartree returns 4 pi rho(G)/G^2 (1/A for rho in
                           # e/A^3), so the potential energy is V (eV) = 14.40 x safe_hartree(rho).
_G2 = H.reciprocal_g2(d["rho"].shape, L)
_NYQ = H.nyquist_mask(d["rho"].shape)
DVH = {t: HARTREE_EV_A * H.safe_hartree(d["drho_" + t].astype(np.float64), _G2, _NYQ)
       for t in ("zfp_1e-3", "sz3_1e-4")}
_rms = {t: float(np.sqrt(np.mean(v * v))) for t, v in DVH.items()}
# frozen pair 266: Nyquist-safe Hartree error ratio ZFP/SZ3 = 0.153234 (matched_pair_mechanism.csv)
assert abs(_rms["zfp_1e-3"] / _rms["sz3_1e-4"] - 0.153234) < 5e-4, _rms
# One shared isolevel, 50 % of the SZ3 max. Both codecs put ~99 % of the Hartree-weighted error at low G, so
# the contrast is magnitude, not shape (a per-codec level would invent a shape difference). ZFP's max |dV_H|
# lies below this level and the panel states it.
_ISO = 0.5 * float(np.abs(DVH["sz3_1e-4"]).max())
VH_ISO = {t: _ISO for t in DVH}
VH_MAX = {t: float(np.abs(v).max()) for t, v in DVH.items()}


def dvh(tag, stem):
    from ovito.pipeline import Pipeline, StaticSource
    a = Pipeline(source=StaticSource(data=atoms_only()))
    arr = DVH[tag]
    pos = S.iso_pipeline(grid_data("vp", arr), "vp", VH_ISO[tag], S.POS, cap=True)
    neg = S.iso_pipeline(grid_data("vn", -arr), "vn", VH_ISO[tag], S.NEG, cap=True)
    S.render([a, pos, neg], OUT / stem, CAM, L)


JOBS = {
    "dvh_zfp": lambda: dvh("zfp_1e-3", "kcn_dvh_zfp_1e-3.png"),
    "dvh_sz3": lambda: dvh("sz3_1e-4", "kcn_dvh_sz3_1e-4.png"),
    "rho": rho,
    "basins": basins,
    "drho_zfp": lambda: drho("zfp_1e-3", "kcn_drho_zfp_1e-3.png"),
    "drho_sz3": lambda: drho("sz3_1e-4", "kcn_drho_sz3_1e-4.png"),
    "moved_1e-7": lambda: reassigned("zfp_1e-7", "kcn_moved_zfp_1e-7.png", 0.30),
    "moved_3e-7": lambda: reassigned("zfp_3e-7", "kcn_moved_zfp_3e-7.png", 0.30),
    "moved_1e-3": lambda: reassigned("zfp_1e-3", "kcn_moved_zfp_1e-3.png", 0.06),
    "moved_1e-2": lambda: reassigned("zfp_1e-2", "kcn_moved_zfp_1e-2.png", 0.045),
}

SIZE = (1500, 1500)
if "--preview" in sys.argv:
    sys.argv.remove("--preview")
    SIZE = (600, 600)
    OUT = HERE / "renders" / "preview"
    OUT.mkdir(exist_ok=True)
_render = S.render
S.render = lambda pipes, png, cam, lat, **kw: _render(pipes, OUT / Path(png).name, cam, lat, size=SIZE, **kw)

if __name__ == "__main__":
    print("delta-rho isolevel %.3g e/A^3 (L_inf ZFP %.3g, SZ3 %.3g)" % (DRHO_ISO, L_ZFP, L_SZ3))
    print("Hartree isolevels %s meV; rms dV_H ZFP %.4g meV, SZ3 %.4g meV, ratio %.4f"
          % ({k: round(1e3 * v, 4) for k, v in VH_ISO.items()}, 1e3 * _rms["zfp_1e-3"], 1e3 * _rms["sz3_1e-4"], _rms["zfp_1e-3"] / _rms["sz3_1e-4"]))
    json.dump(dict(rho_iso_e_per_A3=RHO_ISO, drho_iso_e_per_A3=DRHO_ISO, hartree_iso_eV=_ISO, hartree_max_eV=VH_MAX,
                   hartree_rms_eV=_rms, camera_dir=CAM),
              open(HERE / "renders" / "kcn_render_params.json", "w"), indent=1)
    for name in (sys.argv[1:] or JOBS):
        JOBS[name]()
