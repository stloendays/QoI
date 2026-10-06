#!/usr/bin/env python3
"""A-priori predictors of the matched-rate operator-error ratio between two step-allocation policies.

A policy is a per-orbit step profile Delta_k = alpha * u_k on the QOAC-H v0.2 Hermitian-orbit topology
(conservative Nyquist |G|^2, one canonical coefficient per orbit, multiplicity m = 1 or 2 on the full grid,
n = 1 or 2 real quantized components). Policies are passed as log u (``policy_log_u``) so that very steep
profiles (Gaussian smoothing) cannot overflow. The operator enters only through its squared spectral weight
w(|G|^2) (see ``operators.py``); distortion is the Nyquist-safe operator error energy

    D = sum_{k in safe} m_k w_k sum_{components} E[(c - Q(c))^2].

(a) High-rate orbit-only predictor (generalizes diagnosis D1). Every component has MSE Delta^2/12 and rate
    h - log2 Delta, so at matched total rate

        D(u) ∝ exp(-2 <log u>_n) * sum_{safe} m n w u^2,      <.>_n: n-weighted mean over all orbits.

    It needs only the orbit set (q, w, m, n, Nyquist mask) and no density.

(b) Finite-rate spectrum-aware predictor. Each real component is a zero-mean Laplacian whose variance is
    the reference spectral power averaged over fine radial |G| bins. Quantization is plain rounding
    (np.rint, exactly as the codec) with ideal entropy coding: per component the output entropy H(Delta/sigma)
    and the MSE sigma^2 M(Delta/sigma) are exact closed forms (``laplace_ecsq_exact``). The total rate is
    sum n H, and alpha is found by root bracketing for a target distortion or rate. The model has a dead zone
    (|c| < Delta/2 -> 0), which (a) ignores.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
from scipy import optimize, special

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "operator_aware_codec_hartree_v02"))
import codec_qoac_h_v02 as qoac  # noqa: E402

LN2 = math.log(2.0)
SQRT2 = math.sqrt(2.0)
VARIANCE_BINS = 256


# ---------------------------------------------------------------------------------------------------------
# orbit set and spectrum model
# ---------------------------------------------------------------------------------------------------------
@dataclass
class SpectrumModel:
    """Orbit groups (orbits with identical |G|^2, n and Nyquist status merged; exact for every predictor)."""
    shape: tuple
    g2: np.ndarray        # conservative |G|^2 (A^-2)
    m: np.ndarray         # full-grid multiplicity per orbit
    n: np.ndarray         # real quantized components per orbit
    safe: np.ndarray      # orbit outside every even-grid Nyquist plane
    count: np.ndarray     # orbits per group
    g2_max: float         # codec normalization: q = sqrt(g2 / g2_max)
    sigma2: np.ndarray | None = None   # model variance per real component (None: orbit-only model)
    energy: np.ndarray | None = None   # sum over the group's orbits of |c|^2 (reference spectrum)

    @property
    def n_points(self) -> int:
        return int(np.prod(self.shape))

    @property
    def q(self) -> np.ndarray:
        return np.sqrt(self.g2 / self.g2_max)

    def reference_energy(self, w: np.ndarray) -> float:
        """Nyquist-safe operator energy of the reference density (orbit space, ortho FFT units)."""
        if self.energy is None:
            raise ValueError("model has no reference spectrum")
        return float(np.sum((self.m * w * self.energy)[self.safe]))


def _orbit_arrays(shape, lattice, topology=None):
    topo = topology if topology is not None else qoac.build_topology(
        tuple(int(v) for v in shape), np.asarray(lattice, dtype=np.float64), shell_count=32)
    nx, ny, nz = topo.shape
    yz = ny * nz
    ri = topo.rep_flat // yz
    rj = (topo.rep_flat % yz) // nz
    rk = topo.rep_flat % nz
    nyq = np.zeros(ri.size, dtype=bool)
    for idx, nn in ((ri, nx), (rj, ny), (rk, nz)):
        if nn % 2 == 0:
            nyq |= idx == nn // 2
    m = np.where(topo.self_conjugate, 1.0, 2.0)
    return topo, m, m.copy(), ~nyq


def _group(shape, g2, m, n, safe, g2_max, energy=None, var_bin=None):
    key = np.rint(g2 / g2_max * 1e12).astype(np.int64)
    cols = [key, n.astype(np.int64), safe.astype(np.int64)]
    if var_bin is not None:
        cols.append(var_bin)
    order = np.lexsort(cols[::-1])
    stacked = np.stack([c[order] for c in cols], axis=1)
    brk = np.r_[True, np.any(np.diff(stacked, axis=0) != 0, axis=1)]
    gid = np.cumsum(brk) - 1
    first = order[brk]
    count = np.bincount(gid).astype(np.float64)
    e = None if energy is None else np.bincount(gid, weights=energy[order])
    g2_mean = np.bincount(gid, weights=g2[order]) / count
    return SpectrumModel(tuple(int(v) for v in shape), g2_mean, m[first], n[first], safe[first], count,
                         float(g2_max), None, e), first, gid, order


def orbit_model(shape, lattice) -> SpectrumModel:
    """Orbit-only model (predictor a)."""
    topo, m, n, safe = _orbit_arrays(shape, lattice)
    model, _, _, _ = _group(shape, topo.g2_safe_rep, m, n, safe, topo.g2_safe_max)
    return model


def spectrum_model(field: np.ndarray, lattice, bins: int = VARIANCE_BINS, topology=None) -> SpectrumModel:
    """Orbit groups plus Laplacian component variances from the reference spectrum (predictor b).

    sigma^2 of a radial bin = sum_k (Re c_k^2 + Im c_k^2) / sum_k n_k over the orbits in the bin, with
    ``bins`` uniform bins in q = |G| / |G|_max. The reference spectrum is an input, not a compression outcome.
    """
    x = np.ascontiguousarray(np.asarray(field, dtype=np.float64))
    topo, m, n, safe = _orbit_arrays(x.shape, lattice, topology)
    c = np.fft.fftn(x, norm="ortho").ravel()[topo.rep_flat]
    e = c.real * c.real + np.where(topo.self_conjugate, 0.0, c.imag * c.imag)
    vbin = np.clip(np.floor(topo.q * bins).astype(np.int64), 0, bins - 1)
    num = np.bincount(vbin, weights=e, minlength=bins)
    den = np.bincount(vbin, weights=n, minlength=bins)
    sig_bin = np.divide(num, den, out=np.zeros(bins), where=den > 0)
    model, first, _, _ = _group(x.shape, topo.g2_safe_rep, m, n, safe, topo.g2_safe_max, energy=e, var_bin=vbin)
    model.sigma2 = sig_bin[vbin[first]]
    return model


# ---------------------------------------------------------------------------------------------------------
# policies (log u per orbit group)
# ---------------------------------------------------------------------------------------------------------
Policy = Callable[[SpectrumModel], np.ndarray]


def power_law(beta: float, g2_ref: float | None = None) -> Policy:
    """u = q^beta, q = sqrt(g2 / g2_ref); g2_ref defaults to the codec's g2_max."""
    b = float(beta)

    def f(model: SpectrumModel) -> np.ndarray:
        ref = model.g2_max if g2_ref is None else float(g2_ref)
        return 0.5 * b * np.log(model.g2 / ref)
    return f


def blind() -> Policy:
    return lambda model: np.zeros(model.g2.shape)


def log_weight(weight, model: SpectrumModel) -> np.ndarray:
    """log w per orbit group; ``weight`` is an operators.DiagonalOperator or a callable w(g2)."""
    if hasattr(weight, "log_weight"):
        return weight.log_weight(model.g2)
    with np.errstate(divide="ignore"):
        return np.log(weight(model.g2))


def operator_optimal(weight) -> Policy:
    """u = w^{-1/2}: the high-rate optimum for operator weight w (operator or callable)."""
    return lambda model: -0.5 * log_weight(weight, model)


# ---------------------------------------------------------------------------------------------------------
# (a) high-rate orbit-only predictor
# ---------------------------------------------------------------------------------------------------------
def highrate_log_distortion(model: SpectrumModel, log_w: np.ndarray, log_u: np.ndarray) -> float:
    """log D at a fixed total rate, up to a policy-independent constant."""
    cn = model.count * model.n
    mean_lu = float(np.sum(cn * log_u) / np.sum(cn))
    s = model.safe
    terms = np.log(model.count[s] * model.m[s] * model.n[s]) + log_w[s] + 2.0 * log_u[s]
    return -2.0 * mean_lu + float(special.logsumexp(terms))


def highrate_log_rmse_ratio(model, log_w, log_u_a, log_u_b) -> float:
    """Natural log of the predicted matched-rate operator-RMSE ratio policy a / policy b."""
    return 0.5 * (highrate_log_distortion(model, log_w, log_u_a) - highrate_log_distortion(model, log_w, log_u_b))


def highrate_rmse_ratio(model, log_w, log_u_a, log_u_b) -> float:
    """Predicted matched-rate operator-RMSE ratio policy a / policy b."""
    return math.exp(highrate_log_rmse_ratio(model, log_w, log_u_a, log_u_b))


def highrate_rate_saving_bits_per_point(model, log_w, log_u_a, log_u_b) -> float:
    """Rate saved by policy a over b at matched distortion, bits per real-space grid point."""
    ncomp = float(np.sum(model.count * model.n))
    return -ncomp * highrate_log_rmse_ratio(model, log_w, log_u_a, log_u_b) / LN2 / model.n_points


def highrate_optimal_beta(model, log_w, betas=None, bounds=(-4.0, 4.0)) -> dict:
    """Power-law optimum: grid argmin (ties -> closest to 1) and the continuous minimizer."""
    betas = np.round(np.arange(0.0, 2.0001, 0.25), 2) if betas is None else np.asarray(betas, float)
    lq = 0.5 * np.log(model.g2 / model.g2_max)
    scores = {float(b): highrate_log_distortion(model, log_w, b * lq) for b in betas}
    best = min(scores.values())
    grid = sorted((b for b, v in scores.items() if v - best <= 1e-12), key=lambda b: (abs(b - 1.0), b))[0]
    res = optimize.minimize_scalar(lambda b: highrate_log_distortion(model, log_w, b * lq), bounds=bounds,
                                   method="bounded", options={"xatol": 1e-6})
    return {"beta_grid": grid, "beta_continuous": float(res.x), "log_distortion": scores}


# ---------------------------------------------------------------------------------------------------------
# (b) Laplacian entropy-coded scalar quantizer (plain rounding)
# ---------------------------------------------------------------------------------------------------------
def _k_series(h):
    """K(h) = int_{-h}^{h} s^2 cosh(s) ds = 2 sum_j h^(2j+3) / ((2j)! (2j+3)), for small h."""
    out = np.zeros_like(h)
    h2 = h * h
    term = h ** 3
    fact = 1.0
    for j in range(16):
        if j:
            fact *= (2 * j - 1) * (2 * j)
            term = term * h2
        out += term / (fact * (2 * j + 3))
    return 2.0 * out


def laplace_ecsq_exact(r) -> tuple[np.ndarray, np.ndarray]:
    """Exact output entropy (bits) and MSE/sigma^2 of rint(X / Delta) for X ~ Laplace(0, var=sigma^2).

    r = Delta / sigma > 0. With Laplace scale b = sigma / sqrt(2), d = Delta / b, h = d / 2:
      P(0) = 1 - e^{-h},  P(+-k) = e^{-h} (1 - e^{-d}) e^{-(k-1)d} / 2  (k >= 1)
      H    = -P0 ln P0 - e^{-h} [ln(e^{-h}(1 - e^{-d})/2)] + e^{-h} d / (e^d - 1)        (nats)
      MSE  = b^2 [ gamma(3, h) + K(h) / (e^{2h} - 1) ],   K(h) = int_{-h}^{h} s^2 cosh s ds.
    """
    r = np.asarray(r, dtype=np.float64)
    d = SQRT2 * r
    h = 0.5 * d
    with np.errstate(over="ignore", under="ignore", divide="ignore", invalid="ignore"):
        p0 = -np.expm1(-h)
        P = np.exp(-h)
        t0 = np.where(p0 > 0.0, -p0 * np.log(p0), 0.0)
        t1 = np.where(P > 0.0, -P * (-h + np.log(-np.expm1(-d)) - LN2), 0.0)
        t2 = np.where(P > 0.0, P * d / np.expm1(d), 0.0)
        H = (t0 + t1 + t2) / LN2
        zero_part = 2.0 * special.gammainc(3.0, h)
        small = h < 0.5
        big = h > 30.0
        K = np.where(small, _k_series(np.where(small, h, 0.0)),
                     2.0 * ((h * h + 2.0) * np.sinh(np.minimum(h, 30.0)) - 2.0 * h * np.cosh(np.minimum(h, 30.0))))
        nz = np.where(big, (h * h - 2.0 * h + 2.0) * np.exp(-h), K / np.expm1(np.minimum(2.0 * h, 60.0)))
    mse = 0.5 * (zero_part + nz)       # b^2 / sigma^2 = 1/2
    return np.maximum(H, 0.0), mse


class _ECSQTable:
    """Interpolation table of H(r) and log M(r) on log10 r (accuracy ~1e-7), with exact asymptotes."""
    LO, HI, NPTS = -8.0, 4.0, 24001

    def __init__(self):
        self.x = np.linspace(self.LO, self.HI, self.NPTS)
        H, M = laplace_ecsq_exact(10.0 ** self.x)
        self.H, self.logM = H, np.log(M)
        self.h_inf = math.log2(SQRT2 * math.e)    # differential entropy of unit-variance Laplace (bits)

    def __call__(self, log_r: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Return H (bits) and log M."""
        lx = log_r / math.log(10.0)
        H = np.interp(lx, self.x, self.H)
        logM = np.interp(lx, self.x, self.logM)
        lo = lx < self.LO
        if np.any(lo):
            H[lo] = self.h_inf - lx[lo] * math.log2(10.0)
            logM[lo] = 2.0 * log_r[lo] - math.log(12.0)
        hi = lx > self.HI
        H[hi] = 0.0
        logM[hi] = 0.0
        return H, logM


_TABLE: _ECSQTable | None = None


def ecsq(log_r: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Tabulated (H bits, log MSE/sigma^2) as a function of log(Delta/sigma)."""
    global _TABLE
    if _TABLE is None:
        _TABLE = _ECSQTable()
    return _TABLE(np.asarray(log_r, dtype=np.float64))


def finite_rate_point(model: SpectrumModel, log_w: np.ndarray, log_u: np.ndarray, log_alpha: float,
                      rate_mask: np.ndarray | None = None) -> dict:
    """Model rate (bits), Nyquist-safe distortion and dead-zone fraction at step alpha * u."""
    if model.sigma2 is None:
        raise ValueError("finite-rate predictor needs spectrum_model()")
    pos = model.sigma2 > 0.0
    log_sig = np.where(pos, 0.5 * np.log(np.where(pos, model.sigma2, 1.0)), -np.inf)
    log_r = np.where(pos, log_alpha + log_u - log_sig, np.inf)
    H, logM = ecsq(np.where(np.isfinite(log_r), log_r, 1e3))
    cn = model.count * model.n
    rm = np.ones(model.g2.shape, bool) if rate_mask is None else rate_mask
    rate = float(np.sum((cn * H)[rm]))
    s = model.safe & pos
    with np.errstate(divide="ignore"):
        terms = np.log(cn[s] * model.m[s] * model.sigma2[s]) + log_w[s] + logM[s]
    log_D = float(special.logsumexp(terms))
    D = math.exp(log_D) if log_D < 700.0 else float("inf")
    p0 = np.where(pos, -np.expm1(-np.exp(np.minimum(log_r, 700.0)) / SQRT2), 1.0)
    dead = float(np.sum(model.count * p0 ** model.n) / np.sum(model.count))
    return {"rate_bits": rate, "distortion": D, "log_distortion": log_D, "dead_zone_fraction": dead}


def _bracket(model, log_u):
    pos = model.sigma2 > 0.0
    ls = 0.5 * np.log(model.sigma2[pos]) - log_u[pos]
    ls = ls[np.isfinite(ls)]
    return float(np.min(ls)) - 30.0, float(np.max(ls)) + 30.0


def alpha_for_distortion(model, log_w, log_u, distortion, rate_mask=None) -> float:
    """log alpha giving the target distortion (nan if above the all-zero distortion)."""
    lo, hi = _bracket(model, log_u)
    f = lambda la: finite_rate_point(model, log_w, log_u, la, rate_mask)["log_distortion"] - math.log(distortion)
    if f(hi) <= 0.0:
        return float("nan")
    while f(lo) > 0.0:
        lo -= 20.0
    return float(optimize.brentq(f, lo, hi, xtol=1e-12, rtol=1e-13, maxiter=200))


def alpha_for_rate(model, log_w, log_u, rate_bits, rate_mask=None) -> float:
    lo, hi = _bracket(model, log_u)
    f = lambda la: finite_rate_point(model, log_w, log_u, la, rate_mask)["rate_bits"] - rate_bits
    if f(hi) > 0.0 or f(lo) < 0.0:
        return float("nan")
    return float(optimize.brentq(f, lo, hi, xtol=1e-12, rtol=1e-13, maxiter=200))


def _log_reference_energy(model, log_w) -> float:
    s = model.safe & (model.energy > 0.0)
    return float(special.logsumexp(np.log(model.m[s] * model.energy[s]) + log_w[s]))


def finite_rate_gain(model, log_w, log_u_a, log_u_b, target_rel_rmse: float, rate_mask=None) -> dict:
    """Policy a vs b at a target Nyquist-safe relative operator RMSE.

    rate_ratio            R_a / R_b at matched distortion (the predicted compression-ratio gain is 1/rate_ratio)
    matched_rate_rmse_ratio  RMSE_a / RMSE_b with a at the rate b needs for the target
    """
    D_t = float(target_rel_rmse) ** 2 * math.exp(_log_reference_energy(model, log_w))
    la_a = alpha_for_distortion(model, log_w, log_u_a, D_t, rate_mask)
    la_b = alpha_for_distortion(model, log_w, log_u_b, D_t, rate_mask)
    out = {"target_rel_rmse": float(target_rel_rmse)}
    if not (math.isfinite(la_a) and math.isfinite(la_b)):
        out.update(reachable=False)
        return out
    pa = finite_rate_point(model, log_w, log_u_a, la_a, rate_mask)
    pb = finite_rate_point(model, log_w, log_u_b, la_b, rate_mask)
    la_m = alpha_for_rate(model, log_w, log_u_a, pb["rate_bits"], rate_mask)
    pm = finite_rate_point(model, log_w, log_u_a, la_m, rate_mask) if math.isfinite(la_m) else None
    out.update(
        reachable=True,
        rate_bits_a=pa["rate_bits"], rate_bits_b=pb["rate_bits"],
        bits_per_point_a=pa["rate_bits"] / model.n_points, bits_per_point_b=pb["rate_bits"] / model.n_points,
        rate_ratio=pa["rate_bits"] / pb["rate_bits"],
        matched_rate_rmse_ratio=(math.sqrt(pm["distortion"] / D_t) if pm else float("nan")),
        dead_zone_a=pa["dead_zone_fraction"], dead_zone_b=pb["dead_zone_fraction"],
    )
    return out
