#!/usr/bin/env python3
"""QOAC-HB v2 projections: Hartree-aware projection (HAP) and certify-then-project (CTP).

Hartree-aware projection
------------------------
Given a decoded field x, integer labels (regions 0..L tiling the periodic grid), target region sums t,
the lattice and a dimensionless weight mu > 0, HAP returns y = x + c with

    c = argmin J(c),   J(c) = ||V_H[c]||^2 / s_H + mu ||c||^2 / s_rho,   subject to  A c = d,

where A is the (L+1) x N region-indicator matrix (A c)_i = sum_{r in region i} c(r), d = t - A x,
s_H = ||V_H[rho_ref]||^2 and s_rho = ||rho_ref||^2 (real-space grid sums). V_H = H c is the periodic
Hartree operator of the project's historical convention (`hartree_potential_from_field(..., safe=False)`:
G = 0 removed, rfft half-grid, x/y Nyquist index taken at -n/2). On the full spectrum H is a real, symmetric
Fourier multiplier m(G) (see `hartree_multiplier_rfft`), so

    M = H^T H / s_H + mu I / s_rho   is diagonal in Fourier space:  M(G) = m(G)^2 / s_H + mu / s_rho,

with M(0) = mu / s_rho because m(0) = 0. Stationarity of the Lagrangian c^T M c - 2 lambda^T (A c - d) gives

    c = M^{-1} A^T lambda,      (A M^{-1} A^T) lambda = d,

i.e. B_j = M^{-1} 1_j, Gram G_ij = sum_{r in region i} B_j(r). Only the ratio of the two weights matters,
so we work with M' = s_H M = H^T H + kappa I, kappa = mu s_H / s_rho (the single scalar the decoder needs;
it is serialized as 8 bytes next to the region sums).

G = 0 handled explicitly. The regions tile the cell, so summing all constraints gives N c_0 = sum_i d_i,
where c_0 is the mean of c. Because M is diagonal in Fourier space the G = 0 mode decouples from the rest,
so c_0 = sum(d) / N independently of M(0), and the remaining zero-mean part c_perp solves the same problem
on the zero-mean subspace with d_perp = d - c_0 n (n = region counts):

    c_perp = P M'^{-1} P A^T lambda,   G_perp lambda = d_perp,   G_perp = A P M'^{-1} P A^T.

G_perp is singular along the all-ones vector (P A^T 1 = P 1 = 0) and d_perp is orthogonal to it, so we
solve (G_perp + gamma 1 1^T) lambda = d_perp, which returns the solution with 1^T lambda = 0. This removes
the s_rho / mu rank-one term that the literal Gram A M^{-1} A^T carries, so the system stays well posed as
mu -> 0 (pure Hartree-norm minimization, M'(G != 0) >= m_min^2 > 0). Full derivation: DERIVATION.md.

Per (material, mu), `HartreeAwareProjector` computes one forward/inverse FFT pair per region to build
G_perp and factors it once. Applying it to a decoded candidate needs one bincount, one small solve and one
FFT pair (c = M'^{-1} P A^T lambda; the B_j are never stored). A final uniform residual pass
(`qoac_b_core.project_to_region_sums`) restores floating-point closure.

Certify-then-project
--------------------
`certify_then_project` runs the Bader check on the unprojected stream; if it meets the Bader contract the
stream is stored with a one-byte flag and no side channel, otherwise the chosen projection is applied and
its side channel stored after the flag byte.
"""
from __future__ import annotations

import importlib.util
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

import numpy as np

_A = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    """Import a frozen module by file path (sibling analysis dirs share script names such as run_engineering)."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


qb = _load("qoac_b_core", _A / "operator_aware_bader_fixed_partition" / "qoac_b_core.py")
qoac = _load("codec_qoac_h_v02", _A / "operator_aware_codec_hartree_v02" / "codec_qoac_h_v02.py")

KAPPA = struct.Struct("<d")
CTP_FLAG_BYTES = 1


# ---------------------------------------------------------------------------------------------------------
# Hartree operator as a Fourier multiplier
# ---------------------------------------------------------------------------------------------------------

def hartree_multiplier_rfft(shape: tuple[int, int, int], lattice: np.ndarray) -> np.ndarray:
    """Real multiplier m on the rfftn half grid with irfftn(m * rfftn(x)) == hartree_potential_from_field(x).

    The historical operator applies 4 pi / |G|^2 on the half grid with fftfreq Nyquist signs. On the kz = 0
    and kz = Nyquist planes irfftn keeps only the Hermitian part of the product, so the effective multiplier
    there is (m(G) + m(-G)) / 2; elsewhere it is m(G). Returning the symmetrized multiplier makes H an exact
    real-symmetric Fourier multiplier (needed for H^T H = F^-1 m^2 F).
    """
    nx, ny, nz = (int(v) for v in shape)
    g2 = qoac.reciprocal_g2_historical((nx, ny, nz), lattice)
    m = np.zeros_like(g2)
    pos = g2 > 0.0
    m[pos] = 4.0 * np.pi / g2[pos]
    ix = (-np.arange(nx)) % nx
    iy = (-np.arange(ny)) % ny
    planes = [0] + ([nz // 2] if nz % 2 == 0 and nz > 1 else [])
    for p in planes:
        sl = m[:, :, p]
        m[:, :, p] = 0.5 * (sl + sl[np.ix_(ix, iy)])
    return m


def apply_hartree(field: np.ndarray, multiplier: np.ndarray) -> np.ndarray:
    x = np.asarray(field, dtype=np.float64)
    return np.fft.irfftn(np.fft.rfftn(x) * multiplier, s=x.shape, axes=(0, 1, 2))


def reference_scales(rho_ref: np.ndarray, lattice: np.ndarray) -> tuple[float, float]:
    """(s_H, s_rho): squared real-space norms of the historical Hartree potential and of the density."""
    r = np.asarray(rho_ref, dtype=np.float64)
    vh = qoac.hartree_potential_from_field(r, lattice, safe=False)
    s_h = float(np.sum(vh * vh)); s_rho = float(np.sum(r * r))
    if not (np.isfinite(s_h) and s_h > 0.0 and np.isfinite(s_rho) and s_rho > 0.0):
        raise ValueError("invalid reference scales")
    return s_h, s_rho


def kappa_from_mu(mu: float, s_h: float, s_rho: float) -> float:
    if not (mu > 0.0 and np.isfinite(mu)):
        raise ValueError("mu must be positive and finite")
    return float(mu) * float(s_h) / float(s_rho)


def objective(c: np.ndarray, lattice: np.ndarray, mu: float, s_h: float, s_rho: float) -> tuple[float, float, float]:
    """(J, Hartree term, density term) of the HAP objective, using the canonical Hartree function."""
    c = np.asarray(c, dtype=np.float64)
    vh = qoac.hartree_potential_from_field(c, lattice, safe=False)
    th = float(np.sum(vh * vh)) / s_h
    tr = float(mu) * float(np.sum(c * c)) / s_rho
    return th + tr, th, tr


# ---------------------------------------------------------------------------------------------------------
# HAP
# ---------------------------------------------------------------------------------------------------------

@dataclass
class HartreeAwareProjector:
    """Precomputed HAP for one (labels, lattice, kappa). Reusable for any decoded field on that partition."""

    labels: np.ndarray
    shape: tuple[int, int, int]
    kappa: float
    inv_multiplier: np.ndarray      # 1 / (m^2 + kappa) on the rfft half grid, 0 at G = 0 (applies P M'^-1 P)
    counts: np.ndarray
    active: np.ndarray              # indices of populated regions
    gram: np.ndarray                # G_perp restricted to active regions
    chol: np.ndarray                # Cholesky factor of the Jacobi-scaled (G_perp + gamma 1 1^T)
    jacobi: np.ndarray
    gamma: float
    condition: float                # 2-norm condition number of the scaled regularized Gram

    @property
    def side_extra_bytes(self) -> int:
        return KAPPA.size

    @staticmethod
    def build_many(labels: np.ndarray, lattice: np.ndarray, kappas: Iterable[float]) -> list["HartreeAwareProjector"]:
        """Build projectors for several kappas, sharing the per-region forward FFTs."""
        lab = np.ascontiguousarray(np.asarray(labels, dtype=np.int64))
        if lab.ndim != 3 or np.any(lab < 0):
            raise ValueError("labels must be a non-negative 3-D integer grid")
        shape = tuple(int(v) for v in lab.shape)
        kappas = [float(k) for k in kappas]
        if any(not (k >= 0.0 and np.isfinite(k)) for k in kappas):
            raise ValueError("kappa must be finite and >= 0")
        m2 = hartree_multiplier_rfft(shape, lattice) ** 2
        invs = []
        for k in kappas:
            den = m2 + k
            inv = np.zeros_like(den)
            nz = den > 0.0
            inv[nz] = 1.0 / den[nz]
            inv[0, 0, 0] = 0.0
            invs.append(inv)
        counts = qb.region_counts(lab)
        active = np.flatnonzero(counts > 0)
        flat = lab.ravel(); nl = counts.size
        grams = [np.empty((active.size, active.size)) for _ in kappas]
        for col, j in enumerate(active):
            fj = np.fft.rfftn((lab == j).astype(np.float64))
            for g, inv in zip(grams, invs):
                bj = np.fft.irfftn(fj * inv, s=shape, axes=(0, 1, 2))
                g[:, col] = np.bincount(flat, weights=bj.ravel(), minlength=nl)[active]
        out = []
        for k, inv, g in zip(kappas, invs, grams):
            g = 0.5 * (g + g.T)
            gamma = float(np.mean(np.diag(g))) if g.size else 1.0
            reg = g + gamma * np.ones_like(g)
            jac = 1.0 / np.sqrt(np.diag(reg))
            scaled = reg * jac[:, None] * jac[None, :]
            chol = np.linalg.cholesky(scaled)
            cond = float(np.linalg.cond(scaled))
            out.append(HartreeAwareProjector(lab, shape, k, inv, counts, active, g, chol, jac, gamma, cond))
        return out

    @classmethod
    def build(cls, labels: np.ndarray, lattice: np.ndarray, kappa: float) -> "HartreeAwareProjector":
        return cls.build_many(labels, lattice, [kappa])[0]

    def _solve(self, rhs: np.ndarray) -> np.ndarray:
        z = np.linalg.solve(self.chol, rhs * self.jacobi)
        return np.linalg.solve(self.chol.T, z) * self.jacobi

    def correction(self, field: np.ndarray, target_sums: np.ndarray) -> np.ndarray:
        """The HAP correction c (before the final floating-point closure pass)."""
        x, lab, max_label = qb._validate(field, self.labels)
        target = np.asarray(target_sums, dtype=np.float64)
        if target.shape != self.counts.shape or x.shape != self.shape:
            raise ValueError("field/target do not match the precomputed partition")
        d = (target - qb.region_sums(x, lab))[self.active]
        n = self.counts[self.active].astype(np.float64)
        c0 = float(np.sum(d)) / float(np.sum(n))
        d_perp = d - c0 * n
        lam = np.zeros(self.counts.size)
        lam[self.active] = self._solve(d_perp)
        c = np.fft.irfftn(np.fft.rfftn(lam[lab]) * self.inv_multiplier, s=self.shape, axes=(0, 1, 2))
        return c + c0

    def project(self, field: np.ndarray, target_sums: np.ndarray) -> np.ndarray:
        y = np.asarray(field, dtype=np.float64) + self.correction(field, target_sums)
        return qb.project_to_region_sums(y, self.labels, target_sums)


def hap_side_channel_bytes(side: qb.BasinSideChannel, kappa: float) -> bytes:
    """Serialized HAP side channel: the QOAC-B1 region sums followed by kappa (float64)."""
    return side.to_bytes() + KAPPA.pack(float(kappa))


def parse_hap_side_channel(blob: bytes) -> tuple[qb.BasinSideChannel, float]:
    if len(blob) < KAPPA.size:
        raise ValueError("truncated HAP side channel")
    (kappa,) = KAPPA.unpack(blob[-KAPPA.size:])
    return qb.BasinSideChannel.from_bytes(blob[:-KAPPA.size]), float(kappa)


def project_uniform(field: np.ndarray, labels: np.ndarray, target_sums: np.ndarray) -> np.ndarray:
    return qb.project_to_region_sums(field, labels, target_sums)


# ---------------------------------------------------------------------------------------------------------
# CTP
# ---------------------------------------------------------------------------------------------------------

def certify_then_project(
    field: np.ndarray,
    bader_ok: Callable[[np.ndarray], bool],
    projector: Callable[[np.ndarray], np.ndarray],
    side_channel_bytes: int,
) -> tuple[np.ndarray, int, str]:
    """Return (stored field, extra bytes beyond the codec payload, decision).

    decision = "unprojected": the unprojected stream meets the Bader contract; only the flag byte is stored.
    decision = "projected": it does not; the projection is applied and flag + side channel are stored.
    """
    x = np.asarray(field, dtype=np.float64)
    if bader_ok(x):
        return x, CTP_FLAG_BYTES, "unprojected"
    return projector(x), CTP_FLAG_BYTES + int(side_channel_bytes), "projected"
