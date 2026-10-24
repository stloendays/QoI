"""The linearized-XC allocation law (PROTOCOL.md §4): reciprocal-space steps set by the XC energy's own first-order
sensitivity, stored in the QOAC v0.3 shell container.

To first order the XC-energy error of a decoded density is the inner product of the error with the XC potential,
dE = sum_r v_xc(r) d rho(r) dv = sum_G conj(V(G)) E(G) dv (orthonormal FFT). With independent quantization errors its
variance is sum_G |V(G)|^2 Delta_G^2 / 12, and the high-rate allocation that minimizes the stored bits at a given
variance is Delta_G proportional to |V(G)|^-1, the same rule the Hartree law applies to the Hartree symbol. The v0.3
container stores one step multiplier per radial shell (32 shells, ladder ratio 2^1/4), so the law uses the
shell-averaged weight W_s = mean over the shell's orbits of |V(G)|^2 and Delta_s = alpha (W_s / W_max)^-1/2.

v_xc is the exact derivative of the discrete PBE energy of `nonlinear_xc_20261024/xc.py` (the contract's own E_xc):
f = rho eps_pbe(rho, sigma), sigma = |grad rho|^2 by FFT with the unpaired Nyquist modes dropped, and
dE/drho = dv [f_rho - sum_c D_c(2 f_sigma D_c rho)] with D_c the spectral derivative, f_rho and f_sigma by complex
step. Points with rho <= RHO_MIN carry no energy and no sensitivity, as in xc.py.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "nonlinear_xc_20261024"))
sys.path.insert(0, str(HERE.parent / "qoac_v03_rdo"))
import xc  # noqa: E402
import codec_qoac_v03 as v03  # noqa: E402

v02 = v03.v02
H = 1e-30                       # complex-step size, relative
DROP = v03.LADDER_HI + 1        # a shell whose step is above the ladder is not stored


def _derivative_ops(shape, lattice):
    """Components of the spectral gradient (bohr^-1) on the FFT grid, unpaired Nyquist modes zeroed (as xc.grad_sq)."""
    recip = 2.0 * math.pi * np.linalg.inv(np.asarray(lattice, float)).T * xc.BOHR
    k = [np.fft.fftfreq(n) * n for n in shape]
    for i, n in enumerate(shape):
        if n % 2 == 0:
            k[i][n // 2] = 0.0
    K = np.meshgrid(*k, indexing="ij")
    return [K[0] * recip[0, c] + K[1] * recip[1, c] + K[2] * recip[2, c] for c in range(3)]


def _f(rho, sigma):
    return rho * xc.eps_pbe(rho, sigma)


def pbe_potential(total: np.ndarray, lattice: np.ndarray) -> np.ndarray:
    """v_xc^PBE (hartree) of a CHGCAR-unit field: the derivative of xc.py's discrete E_pbe with respect to rho, / dv."""
    rho, _ = xc.density_au(total, lattice)
    gs = _derivative_ops(rho.shape, lattice)
    rk = np.fft.fftn(rho)
    grads = [np.fft.ifftn(1j * g * rk).real for g in gs]
    sigma = sum(d * d for d in grads)
    ok = rho > xc.RHO_MIN
    r, s = rho[ok], sigma[ok]
    f_rho = np.zeros_like(rho)
    f_sig = np.zeros_like(rho)
    hr = H * r
    f_rho[ok] = np.imag(_f(r + 1j * hr, s)) / hr
    hs = H * np.maximum(s, 1e-300)
    f_sig[ok] = np.imag(_f(r, s + 1j * hs)) / hs
    v = f_rho.copy()
    for g, d in zip(gs, grads):
        v -= np.fft.ifftn(1j * g * np.fft.fftn(2.0 * f_sig * d)).real
    return v


def shell_weights(prep, v: np.ndarray) -> np.ndarray:
    """W_s: mean |V(G)|^2 over each shell's orbits (multiplicity-weighted), V the orthonormal FFT of v_xc."""
    topo = prep.topology
    V = np.fft.fftn(v, norm="ortho").ravel()[topo.rep_flat]
    m = np.where(topo.self_conjugate, 1.0, 2.0)
    w = m * (V.real ** 2 + V.imag ** 2)
    num = np.bincount(topo.shell_ids, weights=w, minlength=topo.shell_count)
    den = np.bincount(topo.shell_ids, weights=m, minlength=topo.shell_count)
    return np.where(den > 0, num / np.maximum(den, 1e-300), 0.0)


def shape_of(W: np.ndarray, writer: str) -> np.ndarray:
    """u_s >= 1 with Delta_s = alpha u_s: X (W_s / W_max)^-1/2, F flat. A shell without sensitivity gets the coarsest step."""
    if writer == "F":
        return np.ones_like(W)
    wmax = float(W.max())
    return np.where(W > 0, (np.maximum(W, 1e-300) / wmax) ** -0.5, np.inf)


def ladder_index(mult_rel: np.ndarray) -> np.ndarray:
    """Nearest ladder exponent of mult / ptp, clipped below to the finest rung; DROP (= HI + 1) above the ladder."""
    j = np.rint(np.log(mult_rel) / math.log(v03.LADDER_STEP))
    j = np.where(np.isfinite(j), j, DROP)
    return np.clip(j, v03.LADDER_LO, DROP).astype(int)


def alpha_floor(prep, u: np.ndarray, ptp: float) -> float:
    """Smallest alpha whose snapped steps keep every quantized coefficient within 0.95 of the int64 range."""
    topo = prep.topology
    c = prep.spectrum.ravel()[topo.rep_flat]
    cmax = np.zeros(topo.shell_count)
    np.maximum.at(cmax, topo.shell_ids, np.maximum(np.abs(c.real), np.abs(c.imag)))
    lim = 0.95 * float(np.iinfo(np.int64).max)
    need = np.where(np.isfinite(u), cmax / (u * lim), 0.0)
    return float(need.max()) * v03.LADDER_STEP ** 0.5 * (1.0 + 1e-6)     # snapping lowers a step by <= 2^1/8


def encode(prep, ptp: float, u: np.ndarray, alpha: float, zlib_level: int = 6) -> bytes:
    """A QOAC v0.3 stream (prior "flat") with shell s quantized at the ladder rung nearest alpha u_s.
    v0.3 records each shell's rung as an index into ptp * LADDER_STEP ** arange(LO, HI + 1); -1 drops the shell."""
    rung = ladder_index(alpha * u / ptp)
    mult = ptp * v03.LADDER_STEP ** np.arange(v03.LADDER_LO, v03.LADDER_HI + 1, dtype=np.float64)
    curves = [SimpleNamespace(j=np.array([r - v03.LADDER_LO if r != DROP else -1])) for r in rung]
    an = SimpleNamespace(prep=prep, ptp=ptp, operator="density", prior="flat", u=np.ones(prep.topology.q.shape),
                         mult=mult, curves=curves)
    return v03.encode(an, [0] * len(curves), zlib_level=zlib_level)


def decode(blob: bytes) -> np.ndarray:
    return np.asarray(v03.decode(blob), dtype=np.float64)
