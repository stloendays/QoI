#!/usr/bin/env python3
"""Generic closed-form allocation codec for General-QOAC: Delta_k = alpha * u_k for any per-orbit policy u.

Same Hermitian-orbit representation and per-shell zlib packing as QOAC-H v0.2 (G = 0 exact, 32 shells).
The policy is stored by name and parameters, so the decoder rebuilds u_k from the lattice. Distortion in a
diagonal-operator metric is computed exactly in orbit space (Parseval) over Nyquist-safe orbits; certificates
are always re-verified on the decoded field with the operator library's own metric.
"""
from __future__ import annotations

import json
import math
import struct
import sys
import zlib
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "operator_aware_codec_hartree_v02"))
import codec_qoac_h_v02 as v02  # noqa: E402

MAGIC = b"QOACP01\n"
QMAX = float(2 ** 52)   # largest quantized magnitude accepted (exact in float64 and int64)


def policy_shape(topo: v02.HermitianTopology, policy: dict) -> np.ndarray:
    """Per-orbit relative step u_k (power laws: u = 1 at the largest |G|; Gaussian: u = 1 at G -> 0)."""
    kind = policy["kind"]
    if kind == "flat":
        return np.ones(topo.q.shape)
    if kind == "power_q":
        return np.power(topo.q, float(policy["p"]))
    if kind == "gaussian":
        s2 = float(policy["sigma_angstrom"]) ** 2
        return np.exp(np.minimum(0.5 * s2 * topo.g2_safe_rep, 700.0))
    raise ValueError(f"unknown policy {policy}")


def nyquist_orbits(topo: v02.HermitianTopology) -> np.ndarray:
    nx, ny, nz = topo.shape
    yz = ny * nz
    i, j, k = topo.rep_flat // yz, (topo.rep_flat % yz) // nz, topo.rep_flat % nz
    m = np.zeros(i.size, dtype=bool)
    for idx, n in ((i, nx), (j, ny), (k, nz)):
        if n % 2 == 0:
            m |= idx == n // 2
    return m


class OrbitSpectrum:
    """Canonical coefficients plus exact orbit-space distortion for a weight w(|G|^2) (absolute, A^-2)."""

    def __init__(self, prep: v02.PreparedSpectrum):
        topo = prep.topology
        self.prep, self.topo = prep, topo
        c = prep.spectrum.ravel()[topo.rep_flat]
        self.cr = c.real.copy()
        self.ci = np.where(topo.self_conjugate, 0.0, c.imag)
        self.selfc = topo.self_conjugate
        self.m = np.where(self.selfc, 1.0, 2.0)
        self.safe = ~nyquist_orbits(topo)

    def weight_cache(self, weight_fn):
        w = weight_fn(self.topo.g2_safe_rep)
        mw = (self.m * w)[self.safe]
        ref = float(np.sum(mw * (self.cr[self.safe] ** 2 + self.ci[self.safe] ** 2)))
        return mw, ref

    def rel_error_safe(self, steps: np.ndarray, mw: np.ndarray, ref: float) -> float:
        s = self.safe
        st = steps[s]
        cr, ci = self.cr[s], self.ci[s]
        sr, si = cr / st, ci / st
        if max(float(np.max(np.abs(sr))), float(np.max(np.abs(si)))) > QMAX:
            return math.inf
        qr = np.rint(sr)
        qi = np.rint(si)
        qi[self.selfc[s]] = 0.0
        er, ei = cr - qr * st, ci - qi * st
        return math.sqrt(float(np.sum(mw * (er * er + ei * ei))) / ref)


def bisect_alpha(spec: OrbitSpectrum, u: np.ndarray, mw: np.ndarray, ref: float, tau: float, ptp: float,
                 margin: float = 0.995, iters: int = 60) -> float | None:
    t = margin * tau
    lo, hi = math.log(1e-16 * ptp), math.log(1e4 * ptp)
    while spec.rel_error_safe(np.exp(lo) * u, mw, ref) == math.inf and lo < hi:
        lo += math.log(10.0)                       # raise the floor until quantization is representable
    if spec.rel_error_safe(np.exp(lo) * u, mw, ref) > t:
        return None
    best = math.exp(lo)
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if spec.rel_error_safe(math.exp(mid) * u, mw, ref) <= t:
            lo, best = mid, math.exp(mid)
        else:
            hi = mid
        if hi - lo < 1e-9:
            break
    return best


def encode(prep: v02.PreparedSpectrum, alpha: float, policy: dict, zlib_level: int = 6) -> bytes:
    topo = prep.topology
    u = policy_shape(topo, policy)
    steps = float(alpha) * u
    c = prep.spectrum.ravel()[topo.rep_flat]
    if max(float(np.max(np.abs(c.real / steps))), float(np.max(np.abs(c.imag / steps)))) > QMAX:
        raise OverflowError("quantized coefficient exceeds 2^52")
    qr = np.rint(c.real / steps).astype(np.int64)
    qi = np.rint(c.imag / steps).astype(np.int64)
    qi[topo.self_conjugate] = 0
    blocks, records = [], []
    for s in range(topo.shell_count):
        idx = topo.shell_ids == s
        n = int(np.count_nonzero(idx))
        if n == 0:
            records.append({"shell": s, "count": 0})
            continue
        rr, ii = qr[idx], qi[idx]
        dt = v02._smallest_signed_dtype(max(int(np.max(np.abs(rr))), int(np.max(np.abs(ii)))))
        inter = np.empty(2 * n, dtype=dt)
        inter[0::2], inter[1::2] = rr, ii
        comp = zlib.compress(inter.tobytes(), zlib_level)
        blocks.append(comp)
        records.append({"shell": s, "count": n, "dtype": dt.str, "compressed_bytes": len(comp)})
    header = {"version": 1, "shape": list(topo.shape), "lattice": topo.lattice.tolist(), "alpha": float(alpha),
              "policy": policy, "shells": records}
    hb = json.dumps(header, separators=(",", ":"), sort_keys=True).encode()
    dc = np.asarray([prep.spectrum.ravel()[0]], dtype="<c16").tobytes()
    return MAGIC + struct.pack("<Q", len(hb)) + hb + dc + b"".join(blocks)


def decode(blob: bytes) -> np.ndarray:
    if not blob.startswith(MAGIC):
        raise ValueError("not a policy-codec stream")
    p = len(MAGIC)
    nh = struct.unpack("<Q", blob[p:p + 8])[0]
    p += 8
    h = json.loads(blob[p:p + nh])
    p += nh
    shape = tuple(h["shape"])
    topo = v02.build_topology(shape, np.asarray(h["lattice"]), shell_count=32)
    steps = h["alpha"] * policy_shape(topo, h["policy"])
    f = np.zeros(shape, dtype=np.complex128)
    flat = f.ravel()
    flat[0] = np.frombuffer(blob[p:p + 16], dtype="<c16")[0]
    p += 16
    for rec in h["shells"]:
        if rec["count"] == 0:
            continue
        raw = zlib.decompress(blob[p:p + rec["compressed_bytes"]])
        p += rec["compressed_bytes"]
        vals = np.frombuffer(raw, dtype=np.dtype(rec["dtype"])).astype(np.float64)
        idx = np.flatnonzero(topo.shell_ids == rec["shell"])
        st = steps[idx]
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
