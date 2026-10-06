#!/usr/bin/env python3
"""Pure-numpy emulation of the Henkelman Bader 1.05 on-grid partition.

Two implementations are provided:

* ``ongrid_literal``: a scalar, line-by-line transcription of the control flow
  of ``bader_calc`` + ``max_ongrid`` + ``step_ongrid`` + ``refine_edge``
  (with ``refine_edge_itrs = 0``) + the vacuum rule, from
  ``mechanism/independent_bader_20260908/reference_source/bader_mod.f90``.
  It is slow and is used only as the reference in unit tests.
* ``ongrid_partition``: a vectorized implementation (successor map + pointer
  jumping) that is exact whenever the field is *regular* in the sense of
  ``regularity_report`` (DESIGN_STUDY.md section 2.3).

Index conventions follow the Fortran arrays: a field ``f`` has shape
``(n1, n2, n3)`` and is indexed ``f[i1, i2, i3]`` with the Fortran scan order
(n1 outermost, n3 innermost) equal to numpy C order. Fortran indices are
1-based; flat indices here are 0-based C-order positions. Returned volume
numbers (``volnum``) are 1-based exactly like Fortran; the vacuum volume is
``nbasins + 1``.

The field values are CHGCAR-convention values (rho * V_cell). The vacuum test
is ``abs(f / V_cell) <= vacval`` exactly as in ``bader_calc``.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

# Neighbour offsets in the exact Fortran loop order (d1 outer, d3 inner),
# centre excluded. The centre has lat_i_dist = 0 and can never win a strict
# ">" comparison, so dropping it does not change the outcome.
OFFSETS = [
    (d1, d2, d3)
    for d1 in (-1, 0, 1)
    for d2 in (-1, 0, 1)
    for d3 in (-1, 0, 1)
    if (d1, d2, d3) != (0, 0, 0)
]


# --------------------------------------------------------------------------
# Lattice quantities (transcription of read_charge_chgcar / matrix_volume)
# --------------------------------------------------------------------------

def lat_i_dist(lattice: np.ndarray, npts: tuple[int, int, int]) -> dict:
    """1 / |dcar| for each of the 26 offsets.

    ``lattice`` rows are the (scaled) lattice vectors as read from the POSCAR
    header, so ``dir2car = lattice.T`` and ``lat2car[:, i] = a_i / n_i``.
    The arithmetic is done in the same operation order as the Fortran source
    (sequential sums); compiler reassociation in the real binary can still
    change the last bit, which is why DESIGN_STUDY.md defines a robust margin.
    """
    L = np.asarray(lattice, dtype=np.float64)
    dir2car = L.T
    lat2car = np.empty((3, 3))
    for i in range(3):
        lat2car[:, i] = dir2car[:, i] / float(npts[i])
    out = {}
    for d in OFFSETS:
        dcar = [0.0, 0.0, 0.0]
        for j in range(3):
            s = 0.0
            for i in range(3):
                s = s + lat2car[j, i] * float(d[i])
            dcar[j] = s
        ss = 0.0
        for j in range(3):
            ss = ss + dcar[j] * dcar[j]
        out[d] = 1.0 / math.sqrt(ss)
    return out


def cell_volume(lattice: np.ndarray) -> float:
    """matrix_volume: triple product a1 . (a2 x a3), as in matrix_mod.f90."""
    L = np.asarray(lattice, dtype=np.float64)
    return float(abs(np.dot(L[0], np.cross(L[1], L[2]))))


# --------------------------------------------------------------------------
# Vectorized implementation
# --------------------------------------------------------------------------

def _neighbor_index(shape, d):
    """Flat index of p + d (periodic) for every p, C order."""
    i1, i2, i3 = np.indices(shape)
    return np.ravel_multi_index(
        ((i1 + d[0]) % shape[0], (i2 + d[1]) % shape[1], (i3 + d[2]) % shape[2]),
        shape,
    ).ravel()


@dataclass
class Stencil:
    shape: tuple
    w: np.ndarray          # (26,) weights in loop order
    nbr: np.ndarray        # (26, N) flat neighbour indices in loop order


def make_stencil(lattice, shape) -> Stencil:
    shape = tuple(int(s) for s in shape)
    wd = lat_i_dist(lattice, shape)
    w = np.array([wd[d] for d in OFFSETS], dtype=np.float64)
    nbr = np.stack([_neighbor_index(shape, d) for d in OFFSETS])
    return Stencil(shape, w, nbr)


def weighted_candidates(field: np.ndarray, st: Stencil) -> np.ndarray:
    """T[k, p] = f_p + (f_{p+d_k} - f_p) * w_k, evaluated in the Fortran
    operation order (subtract, multiply, add; no fused multiply-add)."""
    f = np.ascontiguousarray(field, dtype=np.float64).ravel()
    fn = f[st.nbr]
    return f[None, :] + (fn - f[None, :]) * st.w[:, None]


def successor(field: np.ndarray, st: Stencil) -> np.ndarray:
    """step_ongrid for every voxel: flat index of the chosen neighbour, or the
    voxel itself if no candidate strictly exceeds the centre value.

    Strict ">" update in loop order means: among equal maximal candidates the
    first in loop order wins."""
    f = np.ascontiguousarray(field, dtype=np.float64).ravel()
    T = weighted_candidates(field, st)
    best = f.copy()
    arg = np.arange(f.size)
    for k in range(T.shape[0]):
        upd = T[k] > best
        best = np.where(upd, T[k], best)
        arg = np.where(upd, st.nbr[k], arg)
    return arg


def vacuum_mask(field: np.ndarray, volume: float, vacval: float | None) -> np.ndarray:
    f = np.asarray(field, dtype=np.float64)
    if vacval is None:
        return np.zeros(f.shape, dtype=bool)
    return np.abs(f / volume) <= vacval


def terminal(succ: np.ndarray) -> np.ndarray:
    """Pointer jumping to the fixed point of the successor map. Valid because
    on-grid ascent strictly increases the field, so the map is acyclic."""
    t = succ.copy()
    while True:
        t2 = t[t]
        if np.array_equal(t2, t):
            return t
        t = t2


@dataclass
class Partition:
    volnum: np.ndarray       # (n1,n2,n3) int, 1..nb basins, nb+1 vacuum
    nbasins: int
    maxima: np.ndarray       # (nb,) flat index of the maximum of basin b (1-based b -> [b-1])
    succ: np.ndarray         # flat successor map
    vacuum: np.ndarray       # flat bool


def ongrid_partition(field, lattice, vacval: float | None = 1e-3, st: Stencil | None = None) -> Partition:
    """Vectorized Henkelman on-grid partition (exact for regular fields)."""
    f = np.ascontiguousarray(field, dtype=np.float64)
    shape = f.shape
    st = st or make_stencil(lattice, shape)
    vol = cell_volume(lattice)
    vac = vacuum_mask(f, vol, vacval).ravel()
    succ = successor(f, st)
    term = terminal(succ)
    N = f.size
    # basin numbering = order of discovery in the scan = smallest non-vacuum
    # scan index whose ascent reaches that maximum
    starts = np.flatnonzero(~vac)
    tmax = term[starts]
    first = np.full(N, N, dtype=np.int64)
    np.minimum.at(first, tmax, starts)
    max_ids = np.flatnonzero(first < N)
    order = np.argsort(first[max_ids], kind="stable")
    maxima = max_ids[order]
    rank = np.zeros(N, dtype=np.int64)
    rank[maxima] = np.arange(1, maxima.size + 1)
    vol_flat = rank[term]
    nb = int(maxima.size)
    vol_flat[vac] = nb + 1
    return Partition(vol_flat.reshape(shape), nb, maxima, succ, vac)


# --------------------------------------------------------------------------
# Regularity (conditions under which ongrid_partition == literal Fortran)
# --------------------------------------------------------------------------

def is_max_raw(field: np.ndarray, st: Stencil) -> np.ndarray:
    """charge_mod is_max: no 26-neighbour strictly greater (raw values)."""
    f = np.ascontiguousarray(field, dtype=np.float64).ravel()
    return ~np.any(f[st.nbr] > f[None, :], axis=0)


def regularity_report(field, lattice, vacval=1e-3, st: Stencil | None = None) -> dict:
    """R1: every weighted-stationary non-vacuum voxel is a raw is_max
          (otherwise refine_edge can produce negative volume numbers);
       R2: no non-vacuum voxel steps into a vacuum voxel
          (otherwise first pass and refine_edge disagree on vacuum crossing)."""
    f = np.ascontiguousarray(field, dtype=np.float64)
    st = st or make_stencil(lattice, f.shape)
    vac = vacuum_mask(f, cell_volume(lattice), vacval).ravel()
    succ = successor(f, st)
    idx = np.arange(f.size)
    stationary = succ == idx
    r1_bad = np.flatnonzero(stationary & ~is_max_raw(f, st) & ~vac)
    r2_bad = np.flatnonzero(~vac & ~stationary & vac[succ])
    return {"R1_violations": int(r1_bad.size), "R2_violations": int(r2_bad.size),
            "regular": bool(r1_bad.size == 0 and r2_bad.size == 0)}


# --------------------------------------------------------------------------
# Literal transcription of the Fortran control flow (reference)
# --------------------------------------------------------------------------

def ongrid_literal(field, lattice, vacval: float | None = 1e-3) -> tuple[np.ndarray, int]:
    """Scalar transcription of bader_calc (ongrid, refine_edge_itrs=0).

    Returns (volnum, nbasins) with Fortran semantics, including the vacuum
    label nbasins+1 and the refine_edge pass. Indices are 0-based internally
    but the pbc/neighbour logic is identical."""
    f = np.asarray(field, dtype=np.float64)
    n = f.shape
    wd = lat_i_dist(lattice, n)
    vol = cell_volume(lattice)
    rho = f.tolist()

    def rv(p):
        return rho[p[0] % n[0]][p[1] % n[1]][p[2] % n[2]]

    def wrap(p):
        return (p[0] % n[0], p[1] % n[1], p[2] % n[2])

    volnum = [[[0] * n[2] for _ in range(n[1])] for _ in range(n[0])]

    def V(p):
        return volnum[p[0]][p[1]][p[2]]

    def setV(p, v):
        volnum[p[0]][p[1]][p[2]] = v

    def step(p):  # step_ongrid
        pm = p
        rho_ctr = rv(p)
        rho_max = rho_ctr
        for d1 in (-1, 0, 1):
            for d2 in (-1, 0, 1):
                for d3 in (-1, 0, 1):
                    pt = (p[0] + d1, p[1] + d2, p[2] + d3)
                    rho_tmp = rv(pt)
                    w = 0.0 if (d1, d2, d3) == (0, 0, 0) else wd[(d1, d2, d3)]
                    rho_tmp = rho_ctr + (rho_tmp - rho_ctr) * w
                    if rho_tmp > rho_max:
                        rho_max = rho_tmp
                        pm = pt
        return wrap(pm)

    def max_ongrid(p):
        path = [p]
        while True:
            q = step(p)
            if q == path[-1]:
                break
            p = q
            path.append(p)
            if V(p) > 0:
                break
        return p, path

    def is_max(p):
        r = rv(p)
        for d1 in (-1, 0, 1):
            for d2 in (-1, 0, 1):
                for d3 in (-1, 0, 1):
                    if rv((p[0] + d1, p[1] + d2, p[2] + d3)) > r:
                        return False
        return True

    if vacval is not None:
        for a in range(n[0]):
            for b in range(n[1]):
                for c in range(n[2]):
                    if abs(rho[a][b][c] / vol) <= vacval:
                        volnum[a][b][c] = -1
    bnum = 0
    for a in range(n[0]):
        for b in range(n[1]):
            for c in range(n[2]):
                p = (a, b, c)
                if V(p) == 0:
                    pend, path = max_ongrid(p)
                    pv = V(pend)
                    if pv == 0:
                        bnum += 1
                        pv = bnum
                    for q in path:
                        if V(q) != -1:
                            setV(q, pv)
    if vacval is not None:
        for a in range(n[0]):
            for b in range(n[1]):
                for c in range(n[2]):
                    if volnum[a][b][c] == -1:
                        volnum[a][b][c] = bnum + 1

    # refine_edge, ref_itrs == 1 branch: mark edge points
    def is_vol_edge(p):
        v = abs(V(p))
        for d1 in (-1, 0, 1):
            for d2 in (-1, 0, 1):
                for d3 in (-1, 0, 1):
                    if abs(V(wrap((p[0] + d1, p[1] + d2, p[2] + d3)))) != v:
                        return True
        return False

    for a in range(n[0]):
        for b in range(n[1]):
            for c in range(n[2]):
                p = (a, b, c)
                if V(p) == bnum + 1:
                    continue
                if is_vol_edge(p) and not is_max(p):
                    setV(p, -V(p))
    for a in range(n[0]):
        for b in range(n[1]):
            for c in range(n[2]):
                p = (a, b, c)
                if V(p) < 0:
                    pend, _ = max_ongrid(p)
                    setV(p, V(pend))  # may be out of range for irregular fields
    return np.array(volnum, dtype=np.int64), bnum


# --------------------------------------------------------------------------
# Atom assignment (assign_chg2atom): nearest ion to each basin maximum
# --------------------------------------------------------------------------

def atom_map(part: Partition, lattice, frac_positions) -> np.ndarray:
    """Per-voxel atom index (1-based, nions+1 for vacuum), AtIndex semantics.
    Minimum image is evaluated over the 27 neighbouring images."""
    L = np.asarray(lattice, dtype=np.float64)
    shape = part.volnum.shape
    frac = np.asarray(frac_positions, dtype=np.float64)
    mx = np.array(np.unravel_index(part.maxima, shape)).T / np.array(shape)
    imgs = np.array([(a, b, c) for a in (-1, 0, 1) for b in (-1, 0, 1) for c in (-1, 0, 1)])
    nn = np.empty(part.nbasins, dtype=np.int64)
    for i, m in enumerate(mx):
        dv = (m[None, :] - frac)
        dv = dv - np.round(dv)
        d = ((dv[:, None, :] + imgs[None, :, :]) @ L)
        nn[i] = int(np.argmin(np.min(np.sum(d * d, axis=2), axis=1))) + 1
    lut = np.concatenate([[0], nn, [frac.shape[0] + 1]])
    return lut[part.volnum]
