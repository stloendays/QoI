#!/usr/bin/env python3
"""Random smooth periodic synthetic densities on non-orthogonal lattices.

No material data are used. Fields mimic an all-electron density stored in the
CHGCAR convention (rho * V_cell): a sum of cusp-like exponential "atoms" plus a
weak low-frequency periodic perturbation, evaluated with the periodic minimum
image over 27 cell images in Cartesian distance.
"""
from __future__ import annotations

import numpy as np

LATTICES = ("cubic", "hexagonal", "monoclinic", "triclinic", "sheared")


def make_lattice(kind: str, rng: np.random.Generator, scale: float = 6.0) -> np.ndarray:
    """Rows are lattice vectors (Angstrom)."""
    if kind == "cubic":
        L = np.eye(3)
    elif kind == "hexagonal":
        L = np.array([[1.0, 0.0, 0.0], [-0.5, np.sqrt(3) / 2, 0.0], [0.0, 0.0, 1.3]])
    elif kind == "monoclinic":
        beta = np.deg2rad(rng.uniform(100, 118))
        L = np.array([[1.0, 0, 0], [0, 1.1, 0], [np.cos(beta) * 1.2, 0, np.sin(beta) * 1.2]])
    elif kind == "triclinic":
        a, b, c = rng.uniform(0.9, 1.3, 3)
        al, be, ga = np.deg2rad(rng.uniform(70, 110, 3))
        ax = np.array([a, 0, 0])
        bx = np.array([b * np.cos(ga), b * np.sin(ga), 0])
        cx_ = c * np.cos(be)
        cy = c * (np.cos(al) - np.cos(be) * np.cos(ga)) / np.sin(ga)
        cz = np.sqrt(max(c * c - cx_ * cx_ - cy * cy, 1e-3))
        L = np.array([ax, bx, [cx_, cy, cz]])
    elif kind == "sheared":
        L = np.eye(3) + rng.uniform(-0.35, 0.35, (3, 3)) * (1 - np.eye(3))
    else:
        raise ValueError(kind)
    return scale * L


def random_field(shape, lattice, rng: np.random.Generator, n_atoms: int = 4,
                 noise: float = 0.02, vacuum_slab: bool = False):
    """Return (field_in_CHGCAR_units, frac_positions)."""
    shape = tuple(int(s) for s in shape)
    L = np.asarray(lattice, dtype=np.float64)
    V = abs(np.linalg.det(L))
    frac = rng.uniform(0, 1, (n_atoms, 3))
    if vacuum_slab:
        frac[:, 2] = rng.uniform(0.3, 0.7, n_atoms)
    amps = rng.uniform(5.0, 60.0, n_atoms)
    decay = rng.uniform(1.4, 3.0, n_atoms)          # 1/Angstrom
    g = np.stack(np.meshgrid(*[np.arange(n) / n for n in shape], indexing="ij"), -1)
    imgs = np.array([(a, b, c) for a in (-1, 0, 1) for b in (-1, 0, 1) for c in (-1, 0, 1)])
    rho = np.zeros(shape)
    for x, A, k in zip(frac, amps, decay):
        dv = g - x
        dv = dv - np.round(dv)
        best = np.full(shape, np.inf)
        for im in imgs:
            r = np.linalg.norm((dv + im) @ L, axis=-1)
            best = np.minimum(best, r)
        rho += A * np.exp(-k * best)
    if noise > 0:
        spec = np.zeros(shape, dtype=complex)
        for _ in range(6):
            kk = tuple(int(rng.integers(-2, 3)) for _ in range(3))
            spec[kk] += rng.normal() + 1j * rng.normal()
        pert = np.real(np.fft.ifftn(spec)) * np.prod(shape)
        pert /= max(np.max(np.abs(pert)), 1e-12)
        # multiplicative so that low-density (vacuum) regions stay low
        rho = rho * (1.0 + noise * pert)
    return rho * V, frac
