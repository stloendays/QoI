"""OVITO scene helpers shared by the QSQ structure renders (render-venv only).

Every render is a transparent PNG composed later by matplotlib. Fields arrive as
numpy arrays from prep_fields.py (frozen stack); nothing here recomputes science.

Conventions
    element colours  muted CPK so a chemist reads them without a legend key
    delta-rho sign   + warm (#D8894E), - cool (#4F86B0), always the same isolevel
                     magnitude for both signs and for every codec in a comparison
    reassigned voxel RED, the one red object in the render
"""
from __future__ import annotations

import numpy as np
from ovito.data import DataCollection, ParticleType, VoxelGrid
from ovito.modifiers import CreateIsosurfaceModifier
from ovito.pipeline import Pipeline, StaticSource
from ovito.vis import TachyonRenderer, Viewport

ELEMENT = {  # colour (0-1 rgb), radius (A) -- display radii, not ionic radii
    "K": ((0.62, 0.50, 0.78), 0.48),
    "C": ((0.42, 0.42, 0.44), 0.30),
    "N": ((0.33, 0.47, 0.80), 0.30),
    "Co": ((0.85, 0.56, 0.62), 0.55),
    "Eu": ((0.45, 0.72, 0.70), 0.62),
    "Si": ((0.93, 0.78, 0.53), 0.50),
    "O": ((0.88, 0.35, 0.33), 0.42),
    "Hf": ((0.55, 0.68, 0.86), 0.60),
    "Au": ((0.84, 0.70, 0.35), 0.60),
    "Be": ((0.70, 0.86, 0.55), 0.45),
    "Sn": ((0.55, 0.60, 0.65), 0.58),
    "As": ((0.72, 0.52, 0.86), 0.52),
}
POS, NEG = (0.847, 0.537, 0.306), (0.310, 0.525, 0.690)
RHO_SURF = (0.70, 0.76, 0.89)
RED = (0.922, 0.412, 0.412)


def cell_matrix(lattice: np.ndarray) -> np.ndarray:
    m = np.zeros((3, 4))
    m[:, :3] = np.asarray(lattice).T  # OVITO: columns are the cell vectors
    return m


def base_data(lattice, cart, species, bonds=None, cell_width=0.035, show_cell=True):
    """Cell + atoms (+ optional explicit bonds as index pairs)."""
    dc = DataCollection()
    cell = dc.create_cell(cell_matrix(lattice), pbc=(True, True, True))
    cell.vis.enabled = show_cell
    cell.vis.line_width = cell_width
    cell.vis.rendering_color = (0.25, 0.25, 0.27)
    parts = dc.create_particles(count=len(cart))
    parts.create_property("Position", data=np.asarray(cart))
    tp = parts.create_property("Particle Type")
    names = sorted(set(species), key=list(species).index)
    for i, s in enumerate(names, start=1):
        col, rad = ELEMENT[s]
        tp.types.append(ParticleType(id=i, name=s, color=col, radius=rad))
    tp[...] = [names.index(s) + 1 for s in species]
    if bonds is not None and len(bonds):
        b = parts.create_bonds(count=len(bonds))
        b.create_property("Topology", data=np.asarray([(i, j) for i, j, _ in bonds], dtype=np.int64))
        b.create_property("Periodic Image", data=np.asarray([img for _, _, img in bonds], dtype=np.int32))
        b.vis.width = 0.22
        b.vis.coloring_mode = b.vis.ColoringMode.Uniform
        b.vis.color = (0.45, 0.45, 0.48)
    return dc


def add_grid(dc, lattice, name, arr):
    g = VoxelGrid(identifier=name, domain=dc.cell, shape=arr.shape)
    g.create_property(name, data=np.asarray(arr, dtype=np.float64).ravel(order="F"))
    g.vis.enabled = False
    dc.objects.append(g)
    return g


def iso_pipeline(dc, name, level, color, transparency=0.0, cap=True):
    """A pipeline that shows only the isosurface of one grid property."""
    p = Pipeline(source=StaticSource(data=dc))
    m = CreateIsosurfaceModifier(operate_on="voxels:" + name, property=name, isolevel=level)
    m.vis.surface_color = color
    m.vis.surface_transparency = transparency
    m.vis.show_cap = cap
    m.vis.cap_color = tuple(0.85 * c for c in color)
    m.vis.cap_transparency = transparency
    m.vis.smooth_shading = True
    m.vis.clip_at_domain_boundaries = True
    p.modifiers.append(m)
    return p


def short_pairs(lattice, frac, species, cutoff=1.5, skip=("K",)):
    """Every minimum-image pair shorter than cutoff (A), as given by the structure file."""
    L = np.asarray(lattice)
    f = np.asarray(frac, float)
    out = []
    for i in range(len(f)):
        for j in range(i + 1, len(f)):
            if species[i] in skip or species[j] in skip:
                continue
            dv = f[j] - f[i]
            if np.linalg.norm((dv - np.round(dv)) @ L) < cutoff:
                # OVITO: bond vector = x_j + image . cell - x_i, so the minimum image is -round(dv)
                out.append((i, j, tuple(-int(x) for x in np.round(dv))))
    return out

def render(pipelines, png, camera_dir, lattice, size=(2400, 2400), fov_pad=1.10, zoom_center=None, fov=None,
           ao=True, aa=4):
    """Orthographic Tachyon render with ambient occlusion, transparent background."""
    for p in pipelines:
        p.add_to_scene()
    L = np.asarray(lattice)
    centre = L.sum(axis=0) / 2 if zoom_center is None else np.asarray(zoom_center)
    d = np.asarray(camera_dir, dtype=float)
    d /= np.linalg.norm(d)
    if fov is None:
        corners = np.array([[i, j, k] for i in (0, 1) for j in (0, 1) for k in (0, 1)], float) @ L - centre
        up = np.array([0, 0, 1.0]) if abs(d[2]) < 0.95 else np.array([0, 1.0, 0])
        x = np.cross(d, up); x /= np.linalg.norm(x)
        y = np.cross(x, d)
        half = max(np.abs(corners @ x).max() * size[1] / size[0], np.abs(corners @ y).max())
        fov = half * fov_pad
    vp = Viewport(type=Viewport.Type.Ortho, camera_dir=tuple(d), camera_pos=tuple(centre - d * 300.0), fov=fov)
    vp.render_image(size=size, filename=str(png), background=(1.0, 1.0, 1.0), alpha=True,
                    renderer=TachyonRenderer(ambient_occlusion=ao, ambient_occlusion_brightness=0.8,
                                             ambient_occlusion_samples=6, shadows=False,
                                             antialiasing_samples=aa))
    for p in pipelines:
        p.remove_from_scene()
    print("rendered", png)
