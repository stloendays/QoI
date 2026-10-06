#!/usr/bin/env python3
"""QOAC v0.3: operator-metric rate-distortion-optimal shell allocation with direct certificate targeting.

Representation: the frozen QOAC-H v0.2 Hermitian-orbit topology (conservative Nyquist metric, G=0 exact,
32 radial shells, one zlib block per shell). The quantization step of orbit k in shell s is

    Delta_k = mult_s * u_k,

where u_k is a fixed prior shape (operator law w_k^{-1/2}, or flat) and mult_s is chosen per shell from a
discrete ladder, or the shell is dropped entirely (no block stored).

Because every shell is an independent zlib block, the stream size is exactly separable by shell, and the
operator distortion is exactly separable by orbit (Parseval). The encoder therefore computes each shell's
exact operational (bytes, distortion) curve and selects the multipliers by Lagrangian optimization, so that
the certificate is met with minimum bytes. The distortion uses the conservative Nyquist |G|^2, an upper bound
for the historical metric; the Nyquist-safe metric is constrained separately.
"""
from __future__ import annotations

import json
import math
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "operator_aware_codec_hartree_v02"))
import codec_qoac_h_v02 as v02  # noqa: E402

MAGIC = b"QOACV03\n"
LADDER_STEP = 2.0 ** 0.25          # multiplier ladder ratio
LADDER_LO, LADDER_HI = -160, 48    # mult/ptp = LADDER_STEP**j, j in [LO, HI]


def operator_weight(topo: v02.HermitianTopology, operator: str) -> np.ndarray:
    """Squared operator weight per canonical orbit (conservative |G|^2), up to a constant."""
    g2 = topo.g2_safe_rep / topo.g2_safe_max
    if operator == "hartree_potential":
        return g2 ** -2.0
    if operator == "hartree_field":
        return g2 ** -1.0
    if operator == "density":
        return np.ones_like(g2)
    raise ValueError(f"unknown operator {operator}")


def prior_shape(topo: v02.HermitianTopology, operator: str, prior: str) -> np.ndarray:
    if prior == "flat":
        return np.ones(topo.q.shape)
    if prior == "operator":
        return operator_weight(topo, operator) ** -0.5   # equals 1 at q = 1
    raise ValueError(f"unknown prior {prior}")


def nyquist_orbits(topo: v02.HermitianTopology) -> np.ndarray:
    nx, ny, nz = topo.shape
    yz = ny * nz
    i = topo.rep_flat // yz
    j = (topo.rep_flat % yz) // nz
    k = topo.rep_flat % nz
    m = np.zeros(i.size, dtype=bool)
    for idx, n in ((i, nx), (j, ny), (k, nz)):
        if n % 2 == 0:
            m |= idx == n // 2
    return m


@dataclass
class ShellCurve:
    shell: int
    j: np.ndarray        # ladder index (-1 encodes "dropped")
    bytes: np.ndarray    # exact compressed block bytes (0 if dropped)
    d_cons: np.ndarray   # operator distortion with conservative weights (all orbits)
    d_safe: np.ndarray   # operator distortion over non-Nyquist orbits
    d_sel: np.ndarray    # distortion in the selection metric (equals d_cons unless an operator-blind control)


@dataclass
class Analysis:
    prep: v02.PreparedSpectrum
    operator: str
    prior: str
    ptp: float
    u: np.ndarray
    w: np.ndarray
    mult: np.ndarray
    safe: np.ndarray
    ref_cons_spec: float     # spectral reference energy matching the historical real-space metric
    ref_safe_spec: float
    curves: list


def _block(qr: np.ndarray, qi: np.ndarray, zlib_level: int) -> tuple[bytes, str, int]:
    max_abs = max(int(np.max(np.abs(qr))), int(np.max(np.abs(qi))))
    dt = v02._smallest_signed_dtype(max_abs)
    inter = np.empty(2 * qr.size, dtype=dt)
    inter[0::2] = qr
    inter[1::2] = qi
    raw = inter.tobytes()
    return zlib.compress(raw, zlib_level), dt.str, len(raw)


def analyze(field: np.ndarray, lattice: np.ndarray, operator: str = "hartree_potential", prior: str = "operator",
            reference_historical_rms: float | None = None, d_floor_rel: float = 1e-20,
            zlib_level: int = 6, select_operator: str | None = None) -> Analysis:
    """Compute every shell's exact (bytes, distortion) curve on the multiplier ladder."""
    prep = v02.prepare_field(field, lattice, shell_count=32)
    topo = prep.topology
    ptp = float(np.ptp(field))
    w = operator_weight(topo, operator)
    wsel = operator_weight(topo, select_operator) if select_operator else w
    u = prior_shape(topo, operator, prior)
    safe = ~nyquist_orbits(topo)
    m = np.where(topo.self_conjugate, 1.0, 2.0)
    c = prep.spectrum.ravel()[topo.rep_flat]
    cr = c.real.copy()
    ci = np.where(topo.self_conjugate, 0.0, c.imag)
    e_orb = m * w * (cr * cr + ci * ci)
    ref_safe = float(np.sum(e_orb[safe]))
    if reference_historical_rms is not None and operator == "hartree_potential":
        # mean(V^2) = (1/N) sum_G (4 pi)^2 |rho_ortho(G)|^2 / g2^2 ; w = (g2/g2max)^-2
        n = field.size
        ref_cons = n * reference_historical_rms ** 2 / (4 * math.pi) ** 2 / topo.g2_safe_max ** -2
    else:
        ref_cons = float(np.sum(e_orb))
    mult = ptp * LADDER_STEP ** np.arange(LADDER_LO, LADDER_HI + 1, dtype=np.float64)
    d_floor = d_floor_rel * ref_cons
    curves = []
    for s in range(topo.shell_count):
        idx = np.flatnonzero(topo.shell_ids == s)
        if idx.size == 0:
            curves.append(ShellCurve(s, np.array([-1]), np.zeros(1), np.zeros(1), np.zeros(1), np.zeros(1)))
            continue
        crs, cis, us, ws, ms, ss = cr[idx], ci[idx], u[idx], w[idx], m[idx], safe[idx]
        wls = wsel[idx]
        selfc = topo.self_conjugate[idx]
        e_full = ms * ws * (crs * crs + cis * cis)
        js, bs, dc, dsf = [-1], [0.0], [float(e_full.sum())], [float(e_full[ss].sum())]
        dsl = [float(np.sum(ms * wls * (crs * crs + cis * cis)))]
        for j in range(mult.size - 1, -1, -1):          # coarse -> fine
            st = mult[j] * us
            qr = np.rint(crs / st)
            qi = np.rint(cis / st)
            qi[selfc] = 0.0
            if not (np.any(qr) or np.any(qi)):
                continue                                 # all-zero block is dominated by "dropped"
            er = crs - qr * st
            ei = cis - qi * st
            sq = er * er + ei * ei
            e = ms * ws * sq
            comp, _, _ = _block(qr.astype(np.int64), qi.astype(np.int64), zlib_level)
            js.append(j); bs.append(float(len(comp))); dc.append(float(e.sum())); dsf.append(float(e[ss].sum()))
            dsl.append(float(np.sum(ms * wls * sq)))
            if dc[-1] < d_floor:
                break
        curves.append(ShellCurve(s, np.array(js), np.array(bs), np.array(dc), np.array(dsf), np.array(dsl)))
    return Analysis(prep, operator, prior, ptp, u, w, mult, safe, ref_cons, ref_safe, curves)


def _choose(an: Analysis, lam: float) -> list[int]:
    return [int(np.argmin(c.d_sel + lam * c.bytes)) for c in an.curves]


def _totals(an: Analysis, choice: list[int]) -> tuple[float, float, float]:
    b = sum(c.bytes[i] for c, i in zip(an.curves, choice))
    d1 = sum(c.d_cons[i] for c, i in zip(an.curves, choice))
    d2 = sum(c.d_safe[i] for c, i in zip(an.curves, choice))
    return b, d1, d2


def select(an: Analysis, tau: float, margin: float = 0.995, polish: bool = True) -> list[int]:
    """Minimum-bytes Lagrangian selection meeting both relative-RMSE certificates (with a safety margin)."""
    t1 = (margin * tau) ** 2 * an.ref_cons_spec
    t2 = (margin * tau) ** 2 * an.ref_safe_spec

    def ok(ch):
        _, d1, d2 = _totals(an, ch)
        return d1 <= t1 and d2 <= t2

    lo, hi = -60.0, 60.0                 # log10 lambda in units of selection distortion per byte, relative
    scale = float(sum(c.d_sel[0] for c in an.curves)) or 1.0
    best = None
    if not ok(_choose(an, scale * 10 ** lo)):
        raise RuntimeError("certificate unreachable on the multiplier ladder")
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        ch = _choose(an, scale * 10 ** mid)
        if ok(ch):
            lo, best = mid, ch
        else:
            hi = mid
    best = best or _choose(an, scale * 10 ** lo)
    # greedy polish: move shells to cheaper curve points while the certificate still holds
    improved = polish
    while improved:
        improved = False
        _, d1, d2 = _totals(an, best)
        cand = []
        for s, (c, i) in enumerate(zip(an.curves, best)):
            for k in range(c.bytes.size):
                if c.bytes[k] < c.bytes[i]:
                    dd1 = c.d_cons[k] - c.d_cons[i]
                    dd2 = c.d_safe[k] - c.d_safe[i]
                    if d1 + dd1 <= t1 and d2 + dd2 <= t2:
                        cand.append((c.bytes[i] - c.bytes[k], s, k))
        if cand:
            gain, s, k = max(cand)
            best = list(best)
            best[s] = k
            improved = True
    return best


def encode(an: Analysis, choice: list[int], zlib_level: int = 6) -> bytes:
    topo = an.prep.topology
    c = an.prep.spectrum.ravel()[topo.rep_flat]
    blocks, records = [], []
    for s, (cv, i) in enumerate(zip(an.curves, choice)):
        j = int(cv.j[i])
        idx = np.flatnonzero(topo.shell_ids == s)
        if j < 0 or idx.size == 0:
            records.append({"shell": s, "j": -1})
            continue
        st = an.mult[j] * an.u[idx]
        qr = np.rint(c.real[idx] / st).astype(np.int64)
        qi = np.rint(c.imag[idx] / st).astype(np.int64)
        qi[topo.self_conjugate[idx]] = 0
        comp, dt, raw = _block(qr, qi, zlib_level)
        blocks.append(comp)
        records.append({"shell": s, "j": j, "dtype": dt, "raw_bytes": raw, "compressed_bytes": len(comp)})
    header = {"version": 3, "shape": list(topo.shape), "lattice": topo.lattice.tolist(), "ptp": an.ptp,
              "operator": an.operator, "prior": an.prior, "ladder": [LADDER_STEP, LADDER_LO, LADDER_HI],
              "shells": records}
    hb = json.dumps(header, separators=(",", ":"), sort_keys=True).encode()
    dc = np.asarray([an.prep.spectrum.ravel()[0]], dtype="<c16").tobytes()
    return MAGIC + struct.pack("<Q", len(hb)) + hb + dc + b"".join(blocks)


def decode(blob: bytes) -> np.ndarray:
    if not blob.startswith(MAGIC):
        raise ValueError("not a QOAC v0.3 stream")
    p = len(MAGIC)
    nh = struct.unpack("<Q", blob[p:p + 8])[0]
    p += 8
    h = json.loads(blob[p:p + nh])
    p += nh
    shape = tuple(h["shape"])
    topo = v02.build_topology(shape, np.asarray(h["lattice"]), shell_count=32)
    u = prior_shape(topo, h["operator"], h["prior"])
    step, lo, hi = h["ladder"]
    mult = h["ptp"] * step ** np.arange(lo, hi + 1, dtype=np.float64)
    f = np.zeros(shape, dtype=np.complex128)
    flat = f.ravel()
    flat[0] = np.frombuffer(blob[p:p + 16], dtype="<c16")[0]
    p += 16
    for rec in h["shells"]:
        if rec["j"] < 0:
            continue
        raw = zlib.decompress(blob[p:p + rec["compressed_bytes"]])
        p += rec["compressed_bytes"]
        vals = np.frombuffer(raw, dtype=np.dtype(rec["dtype"])).astype(np.float64)
        idx = np.flatnonzero(topo.shell_ids == rec["shell"])
        st = mult[rec["j"]] * u[idx]
        coeff = vals[0::2] * st + 1j * vals[1::2] * st
        selfc = topo.self_conjugate[idx]
        coeff[selfc] = coeff[selfc].real
        flat[topo.rep_flat[idx]] = coeff
        ns = ~selfc
        flat[topo.partner_flat[idx][ns]] = np.conj(coeff[ns])
    if p != len(blob):
        raise ValueError("trailing bytes")
    out = np.fft.ifftn(f, norm="ortho")
    if float(np.max(np.abs(out.imag))) > 1e-11 * max(1.0, float(np.max(np.abs(out.real)))):
        raise RuntimeError("real-field invariant violated")
    return np.ascontiguousarray(out.real)
