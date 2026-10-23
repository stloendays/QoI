"""Spin-unpolarized exchange-correlation energy of a stored periodic density (LDA: Slater + PW92; GGA: PBE).

The QoI of this study (PROTOCOL.md §3): E_xc[rho] of the stored total density, rho in CHGCAR units (rho * V_cell),
on its own grid, gradients by FFT on the periodic cell, energy in eV per atom. Points with rho <= RHO_MIN contribute
zero (negative decoded values included); this is the density threshold of the QoI, not a tuning parameter.
Formulas: Perdew & Wang, PRB 45, 13244 (1992), original PW92 parameters (libxc LDA_C_PW); Perdew, Burke & Ernzerhof,
PRL 77, 3865 (1996) (libxc GGA_X_PBE, GGA_C_PBE). `check_against_libxc` compares with PySCF/libxc where available.
"""
from __future__ import annotations

import math

import numpy as np

BOHR = 0.529177210903          # Angstrom
HARTREE_EV = 27.211386245988
RHO_MIN = 1e-12                # bohr^-3

# PW92 unpolarized correlation (original parameters)
_A, _A1, _B1, _B2, _B3, _B4 = 0.031091, 0.21370, 7.5957, 3.5876, 1.6382, 0.49294
# PBE
_KAPPA, _MU = 0.804, 0.2195149727645171
_BETA = 0.06672455060314922
_GAMMA = (1.0 - math.log(2.0)) / math.pi ** 2
_CX = -0.75 * (3.0 / math.pi) ** (1.0 / 3.0)


def density_au(total: np.ndarray, lattice: np.ndarray) -> tuple[np.ndarray, float]:
    """CHGCAR-unit field -> density in bohr^-3, and the voxel volume in bohr^3."""
    vol_a3 = abs(float(np.linalg.det(lattice)))
    rho = np.asarray(total, dtype=np.float64) / vol_a3 * BOHR ** 3
    return rho, vol_a3 / BOHR ** 3 / rho.size


def grad_sq(rho: np.ndarray, lattice: np.ndarray) -> np.ndarray:
    """|grad rho|^2 in bohr^-8 by FFT on the periodic cell (lattice rows in Angstrom)."""
    shape = rho.shape
    recip = 2.0 * math.pi * np.linalg.inv(np.asarray(lattice, float)).T * BOHR    # rows b_i in bohr^-1
    k = [np.fft.fftfreq(n) * n for n in shape]
    for i, n in enumerate(shape):                       # drop the unpaired Nyquist mode of even axes
        if n % 2 == 0:
            k[i][n // 2] = 0.0
    K = np.meshgrid(*k, indexing="ij")
    rk = np.fft.fftn(rho)
    g2 = np.zeros(shape)
    for c in range(3):
        gc = K[0] * recip[0, c] + K[1] * recip[1, c] + K[2] * recip[2, c]
        d = np.fft.ifftn(1j * gc * rk).real
        g2 += d * d
    return g2


def _pw92(rs):
    q = 2.0 * _A * (_B1 * np.sqrt(rs) + _B2 * rs + _B3 * rs ** 1.5 + _B4 * rs ** 2)
    return -2.0 * _A * (1.0 + _A1 * rs) * np.log1p(1.0 / q)


def eps_lda(rho):
    """Energy per particle (hartree), Slater exchange + PW92 correlation; rho > 0."""
    rs = (3.0 / (4.0 * math.pi * rho)) ** (1.0 / 3.0)
    return _CX * rho ** (1.0 / 3.0) + _pw92(rs)


def eps_pbe(rho, sigma):
    """Energy per particle (hartree), PBE exchange + correlation; rho > 0, sigma = |grad rho|^2."""
    kf = (3.0 * math.pi ** 2 * rho) ** (1.0 / 3.0)
    s2 = sigma / (4.0 * kf * kf * rho * rho)
    fx = 1.0 + _KAPPA - _KAPPA / (1.0 + _MU * s2 / _KAPPA)
    ex = _CX * rho ** (1.0 / 3.0) * fx
    rs = (3.0 / (4.0 * math.pi * rho)) ** (1.0 / 3.0)
    ec = _pw92(rs)
    ks = np.sqrt(4.0 * kf / math.pi)
    t2 = sigma / (4.0 * ks * ks * rho * rho)
    with np.errstate(over="ignore"):
        A = (_BETA / _GAMMA) / np.expm1(-ec / _GAMMA)
    at2 = A * t2
    H = _GAMMA * np.log1p((_BETA / _GAMMA) * t2 * (1.0 + at2) / (1.0 + at2 + at2 * at2))
    return ex + ec + H


def exc_energies(total: np.ndarray, lattice: np.ndarray, natoms: int) -> dict:
    """E_xc^LDA and E_xc^PBE in eV per atom, and V_xc^LDA on the grid (hartree), of a CHGCAR-unit field."""
    rho, dv = density_au(total, lattice)
    g2 = grad_sq(rho, lattice)
    ok = rho > RHO_MIN
    r = rho[ok]
    e_lda = float(np.sum(r * eps_lda(r)) * dv)
    e_pbe = float(np.sum(r * eps_pbe(r, g2[ok])) * dv)
    return {"E_lda_eV_per_atom": e_lda * HARTREE_EV / natoms, "E_pbe_eV_per_atom": e_pbe * HARTREE_EV / natoms,
            "vxc_lda": _vxc_lda(rho)}


def _vxc_lda(rho):
    """d(rho eps_lda)/d rho, zero below RHO_MIN (hartree)."""
    v = np.zeros_like(rho)
    ok = rho > RHO_MIN
    r = rho[ok]
    rs = (3.0 / (4.0 * math.pi * r)) ** (1.0 / 3.0)
    vx = (4.0 / 3.0) * _CX * r ** (1.0 / 3.0)
    q0 = -2.0 * _A * (1.0 + _A1 * rs)
    q1 = 2.0 * _A * (_B1 * np.sqrt(rs) + _B2 * rs + _B3 * rs ** 1.5 + _B4 * rs ** 2)
    dq1 = _A * (_B1 / np.sqrt(rs) + 2.0 * _B2 + 3.0 * _B3 * np.sqrt(rs) + 4.0 * _B4 * rs)
    ec = q0 * np.log1p(1.0 / q1)
    dec = -2.0 * _A * _A1 * np.log1p(1.0 / q1) - q0 * dq1 / (q1 * q1 + q1)
    v[ok] = vx + ec - rs / 3.0 * dec
    return v


def xc_errors(ref: dict, dec_total: np.ndarray, lattice: np.ndarray, natoms: int) -> dict:
    """Errors of a decoded field against the reference energies: |dE| in meV per atom, V_xc^LDA relative RMS."""
    d = exc_energies(dec_total, lattice, natoms)
    vr = ref["vxc_lda"]
    return {"dE_lda_meV_per_atom": abs(d["E_lda_eV_per_atom"] - ref["E_lda_eV_per_atom"]) * 1e3,
            "dE_pbe_meV_per_atom": abs(d["E_pbe_eV_per_atom"] - ref["E_pbe_eV_per_atom"]) * 1e3,
            "vxc_lda_rel_rms": float(np.sqrt(np.mean((d["vxc_lda"] - vr) ** 2)) / np.sqrt(np.mean(vr ** 2)))}


def check_against_libxc(total: np.ndarray, lattice: np.ndarray, n: int = 20000, seed: int = 0) -> dict:
    """Energy density and LDA potential at n grid points against PySCF/libxc (LDA_X + LDA_C_PW, GGA_X/C_PBE)."""
    from pyscf.dft import libxc
    rho, _ = density_au(total, lattice)
    g2 = grad_sq(rho, lattice)
    rng = np.random.default_rng(seed)
    idx = rng.choice(np.flatnonzero(rho > 1e-6), size=min(n, int((rho > 1e-6).sum())), replace=False)
    r, s = rho.ravel()[idx], g2.ravel()[idx]
    e_l = libxc.eval_xc("LDA,PW", r, spin=0, deriv=1)
    g = np.zeros((4, r.size))
    g[0] = r
    g[1] = np.sqrt(s)                                   # libxc only uses |grad rho|^2 = sum of squares
    e_p = libxc.eval_xc("PBE,PBE", g, spin=0, deriv=1)
    rel = lambda a, b: float(np.max(np.abs(a - b) / np.maximum(np.abs(b), 1e-300)))  # noqa: E731
    return {"points": int(r.size), "lda_exc_maxrel": rel(eps_lda(r), e_l[0]),
            "pbe_exc_maxrel": rel(eps_pbe(r, s), e_p[0]), "lda_vxc_maxrel": rel(_vxc_lda(r), e_l[1][0])}
