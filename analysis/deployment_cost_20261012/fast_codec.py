#!/usr/bin/env python3
"""Production implementation of the QOAC-H v0.2 (law, A1) and QOAC v0.3 (operational, A3) stream formats.

The streams are unchanged. Only the implementation differs from the reference modules:

* the conservative Nyquist metric evaluates the alias sign choices on the Nyquist planes only (every other mode has
  one alias), with the reference's arithmetic, so |G|^2, q and the shell assignment are bit-identical;
* the orbit table is built once and sorted by shell (stable), replacing 32 boolean scans of the orbit list;
* the decoder writes the half spectrum and inverts with a real-to-complex FFT (irfftn) instead of filling the full
  complex spectrum and taking the real part of ifftn.

Encoded streams are byte-identical to the reference encoder; decoded fields agree with the reference decoder to
floating-point rounding (test_fast_codec.py), and every decoded field is re-certified in run_cost.py.
"""
from __future__ import annotations

import json
import struct
import sys
import zlib
from itertools import product
from pathlib import Path

import numpy as np

ANALYSIS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ANALYSIS / "operator_aware_codec_hartree_v02"))
sys.path.insert(0, str(ANALYSIS / "qoac_v03_rdo"))
import codec_qoac_h_v02 as v02  # noqa: E402
import codec_qoac_v03 as v3  # noqa: E402


def _g2_expr(metric, a, b, c):
    # the reference expression of codec_qoac_h_v02.conservative_g2, term by term in the same order
    return (metric[0, 0] * a * a + metric[1, 1] * b * b + metric[2, 2] * c * c
            + 2.0 * metric[0, 1] * a * b + 2.0 * metric[0, 2] * a * c + 2.0 * metric[1, 2] * b * c)


def conservative_g2(shape, lattice) -> np.ndarray:
    nx, ny, nz = (int(v) for v in shape)
    ns = (nx, ny, nz)
    axes = [v02._freq_axis(n).astype(np.float64) for n in ns]
    metric = v02.reciprocal_metric(lattice)
    nyq = [n // 2 if n % 2 == 0 else None for n in ns]
    # one alias everywhere off the Nyquist planes: evaluate with any sign choice
    best = _g2_expr(metric, axes[0][:, None, None], axes[1][None, :, None], axes[2][None, None, :])
    if any(i is not None for i in nyq):
        opts = [(-1.0, 1.0) if i is not None else (1.0,) for i in nyq]
        # points on at least one Nyquist plane: minimum over all sign choices, reference arithmetic
        planes = []
        for ax, i in enumerate(nyq):
            if i is None:
                continue
            sl = [slice(None)] * 3; sl[ax] = slice(i, i + 1)
            planes.append(tuple(sl))
        for sl in planes:
            sub = None
            for signs in product(*opts):
                vals = []
                for d in range(3):
                    v = axes[d].copy()
                    if nyq[d] is not None:
                        v[nyq[d]] = signs[d] * (ns[d] / 2.0)
                    vals.append(v[sl[d]])
                cur = _g2_expr(metric, vals[0][:, None, None], vals[1][None, :, None], vals[2][None, None, :])
                sub = cur if sub is None else np.minimum(sub, cur)
            best[sl] = sub
    best[np.abs(best) < 1e-24] = 0.0
    if not np.all(np.isfinite(best)) or np.any(best < 0.0):
        raise ValueError("invalid conservative reciprocal metric")
    return best

try:                                    # compiled single-pass orbit table; the numpy path below is the fallback
    import numba as _nb
except ImportError:                     # pragma: no cover
    _nb = None

if _nb is not None:
    @_nb.njit(cache=True)
    def _orbit_kernel(nx, ny, nz, m, ax, ay, az, nqx, nqy, nqz):
        """One pass over the grid in C order: conservative |G|^2 (reference arithmetic, minimum over the Nyquist
        alias signs), the maximum over all nonzero modes, and the canonical active orbits."""
        m00, m11, m22 = m[0, 0], m[1, 1], m[2, 2]
        c01, c02, c12 = 2.0 * m[0, 1], 2.0 * m[0, 2], 2.0 * m[1, 2]
        n = nx * ny * nz
        ri = np.empty(n // 2 + 8, np.int32); rj = np.empty(n // 2 + 8, np.int32); rk = np.empty(n // 2 + 8, np.int32)
        g2 = np.empty(n // 2 + 8, np.float64)   # (N + self-conjugate modes, at most 8) / 2
        cnt = 0
        gmax = -1.0
        xa = np.empty(2); xb = np.empty(2); xc = np.empty(2)
        for i in range(nx):
            pi = (nx - i) % nx
            na = 1; xa[0] = ax[i]
            if i == nqx:
                na = 2; xa[0] = -(nx / 2.0); xa[1] = nx / 2.0
            for j in range(ny):
                pj = (ny - j) % ny
                nb = 1; xb[0] = ay[j]
                if j == nqy:
                    nb = 2; xb[0] = -(ny / 2.0); xb[1] = ny / 2.0
                for k in range(nz):
                    pk = (nz - k) % nz
                    nc = 1; xc[0] = az[k]
                    if k == nqz:
                        nc = 2; xc[0] = -(nz / 2.0); xc[1] = nz / 2.0
                    best = np.inf
                    for u in range(na):
                        a = xa[u]
                        for v in range(nb):
                            b = xb[v]
                            for w in range(nc):
                                c = xc[w]
                                cur = (m00 * a * a + m11 * b * b + m22 * c * c
                                       + c01 * a * b + c02 * a * c + c12 * b * c)
                                if cur < best:
                                    best = cur
                    if abs(best) < 1e-24:
                        best = 0.0
                    if best > 0.0:
                        if best > gmax:
                            gmax = best
                        if i < pi or (i == pi and (j < pj or (j == pj and k <= pk))):
                            ri[cnt] = i; rj[cnt] = j; rk[cnt] = k; g2[cnt] = best
                            cnt += 1
        return ri[:cnt], rj[:cnt], rk[:cnt], g2[:cnt], gmax

    @_nb.njit(cache=True)
    def _counting_order(shell, nshell):
        counts = np.zeros(nshell, np.int64)
        for s in shell:
            counts[s] += 1
        pos = np.zeros(nshell, np.int64)
        for s in range(1, nshell):
            pos[s] = pos[s - 1] + counts[s - 1]
        order = np.empty(shell.size, np.int64)
        for t in range(shell.size):
            s = shell[t]; order[pos[s]] = t; pos[s] += 1
        return order, counts

    @_nb.njit(cache=True)
    def _scatter(half, ri, rj, rk, pi, pj, pk, selfc, cr, ci):
        h = half.shape[2]
        for t in range(ri.size):
            if rk[t] < h:
                half[ri[t], rj[t], rk[t]] = complex(cr[t], ci[t])
            if not selfc[t] and pk[t] < h:
                half[pi[t], pj[t], pk[t]] = complex(cr[t], -ci[t])


class Orbits:
    """The Hermitian-orbit table of codec_qoac_h_v02.build_topology, ordered by shell (stable).

    Orbits are kept as (i, j, k) index triples from np.nonzero (C order, i.e. the reference's flat order), so no
    flat-index division is needed; the stable shell sort is a radix sort on int8 keys."""

    def __init__(self, shape, lattice, shell_count: int = 32):
        nx, ny, nz = self.shape = tuple(int(v) for v in shape)
        tx, ty, tz = ((-np.arange(n)) % n for n in self.shape)
        if _nb is not None:
            ax, ay, az = (v02._freq_axis(n).astype(np.float64) for n in self.shape)
            nq = [n // 2 if n % 2 == 0 else -1 for n in self.shape]
            ri, rj, rk, g2_rep, self.g2_max = _orbit_kernel(nx, ny, nz, v02.reciprocal_metric(lattice), ax, ay, az, *nq)
        else:
            g2 = conservative_g2(self.shape, lattice)
            i = np.arange(nx)[:, None, None]; j = np.arange(ny)[None, :, None]; k = np.arange(nz)[None, None, :]
            pi, pj, pk = tx[:, None, None], ty[None, :, None], tz[None, None, :]
            mask = ((i < pi) | ((i == pi) & (j < pj)) | ((i == pi) & (j == pj) & (k <= pk))) & (g2 > 0.0)
            ri, rj, rk = np.nonzero(mask)
            g2_rep = g2[mask]
            self.g2_max = float(np.max(g2[g2 > 0.0]))
        q = np.sqrt(g2_rep / self.g2_max)
        shell = np.clip(np.floor(q * int(shell_count)).astype(np.int64), 0, int(shell_count) - 1).astype(np.int8)
        if _nb is not None:
            order, self.counts = _counting_order(shell, int(shell_count))
        else:
            order = np.argsort(shell, kind="stable"); self.counts = np.bincount(shell, minlength=int(shell_count))
        self.starts = np.concatenate(([0], np.cumsum(self.counts)))
        self.ri, self.rj, self.rk = ri[order].astype(np.int32), rj[order].astype(np.int32), rk[order].astype(np.int32)
        self.pi, self.pj, self.pk = tx[self.ri].astype(np.int32), ty[self.rj].astype(np.int32), tz[self.rk].astype(np.int32)
        self.selfc = (self.ri == self.pi) & (self.rj == self.pj) & (self.rk == self.pk)
        self.q, self.g2_rep = q[order], g2_rep[order]
        self.order, self.shell_count = order, int(shell_count)

    def to_reference(self, lattice) -> v02.HermitianTopology:
        """The reference topology object (original orbit order), for the reference encoder."""
        nx, ny, nz = self.shape
        inv = np.empty_like(self.order); inv[self.order] = np.arange(self.order.size)
        flat = lambda a, b, c: ((a[inv].astype(np.int64) * ny + b[inv]) * nz + c[inv])
        q = self.q[inv]
        return v02.HermitianTopology(shape=self.shape, lattice=np.asarray(lattice, dtype=np.float64).copy(),
                                     rep_flat=flat(self.ri, self.rj, self.rk), partner_flat=flat(self.pi, self.pj, self.pk),
                                     self_conjugate=self.selfc[inv], q=q,
                                     shell_ids=np.clip(np.floor(q * self.shell_count).astype(np.int64), 0,
                                                       self.shell_count - 1).astype(np.int16),
                                     shell_count=self.shell_count, g2_safe_rep=self.g2_rep[inv], g2_safe_max=self.g2_max)

    def synthesize(self, coeff: np.ndarray, dc: complex) -> np.ndarray:
        """Real field from canonical coefficients (shell order), through the half spectrum and irfftn."""
        nx, ny, nz = self.shape
        h = nz // 2 + 1
        half = np.zeros((nx, ny, h), dtype=np.complex128)
        if _nb is not None:
            _scatter(half, self.ri, self.rj, self.rk, self.pi, self.pj, self.pk, self.selfc,
                     np.ascontiguousarray(coeff.real), np.ascontiguousarray(coeff.imag))
            half[0, 0, 0] = dc
            return np.fft.irfftn(half, s=self.shape, axes=(0, 1, 2), norm="ortho")
        keep = self.rk < h
        half[self.ri[keep], self.rj[keep], self.rk[keep]] = coeff[keep]
        keep = (self.pk < h) & ~self.selfc
        half[self.pi[keep], self.pj[keep], self.pk[keep]] = np.conj(coeff[keep])
        half[0, 0, 0] = dc
        return np.fft.irfftn(half, s=self.shape, axes=(0, 1, 2), norm="ortho")


def _parse(blob: bytes, magic: bytes):
    if not blob.startswith(magic):
        raise ValueError("wrong stream magic")
    p = len(magic)
    nh = struct.unpack("<Q", blob[p:p + 8])[0]; p += 8
    h = json.loads(blob[p:p + nh]); p += nh
    dc = complex(np.frombuffer(blob[p:p + 16], dtype="<c16")[0]); p += 16
    return h, dc, p


def _shell_values(blob, p, recs, orb: Orbits, use):
    """Concatenate the (real, imag) integers of the stored shells; return arrays aligned with the orbit order."""
    qr = np.zeros(orb.q.size); qi = np.zeros(orb.q.size); stored = np.zeros(orb.q.size, dtype=bool)
    for rec in recs:
        if not use(rec):
            continue
        s = int(rec["shell"]); a, b = orb.starts[s], orb.starts[s + 1]
        raw = zlib.decompress(blob[p:p + rec["compressed_bytes"]]); p += rec["compressed_bytes"]
        v = np.frombuffer(raw, dtype=np.dtype(rec["dtype"]))
        if v.size != 2 * (b - a):
            raise ValueError("shell value-count mismatch")
        qr[a:b] = v[0::2]; qi[a:b] = v[1::2]; stored[a:b] = True
    if p != len(blob):
        raise ValueError("unexpected trailing bytes")
    return qr, qi, stored


def decode_law(blob: bytes) -> np.ndarray:
    """QOAC-H v0.2 stream (the law, A1)."""
    h, dc, p = _parse(blob, v02.MAGIC[:0] + b"QOACH02\n")
    orb = Orbits(h["shape"], np.asarray(h["lattice"], dtype=np.float64), int(h["shell_count"]))
    a, b = float(h["alpha"]), float(h["beta"])
    steps = np.full(orb.q.shape, a) if b == 0.0 else a * np.power(orb.q, b)
    qr, qi, _ = _shell_values(blob, p, h["shells"], orb, lambda r: int(r["count"]) > 0)
    coeff = qr * steps + 1j * qi * steps
    coeff[orb.selfc] = coeff[orb.selfc].real + 0j
    return orb.synthesize(coeff, dc)


def decode_operational(blob: bytes) -> np.ndarray:
    """QOAC v0.3 stream (the operational optimum, A3)."""
    h, dc, p = _parse(blob, v3.MAGIC)
    orb = Orbits(h["shape"], np.asarray(h["lattice"], dtype=np.float64), 32)
    g2 = orb.g2_rep / orb.g2_max
    if h["prior"] == "flat":
        u = np.ones(orb.q.shape)
    else:
        u = (g2 ** -2.0 if h["operator"] == "hartree_potential" else g2 ** -1.0 if h["operator"] == "hartree_field"
             else np.ones_like(g2)) ** -0.5
    step, lo, hi = h["ladder"]
    mult = h["ptp"] * step ** np.arange(lo, hi + 1, dtype=np.float64)
    j_of = {int(r["shell"]): int(r["j"]) for r in h["shells"]}
    st = np.zeros(orb.q.shape)
    for s, j in j_of.items():
        if j >= 0:
            st[orb.starts[s]:orb.starts[s + 1]] = mult[j] * u[orb.starts[s]:orb.starts[s + 1]]
    qr, qi, stored = _shell_values(blob, p, h["shells"], orb, lambda r: int(r["j"]) >= 0)
    coeff = np.where(stored, qr * st + 1j * qi * st, 0j)
    coeff[orb.selfc] = coeff[orb.selfc].real
    return orb.synthesize(coeff, dc)


def prepare_field(field: np.ndarray, lattice: np.ndarray) -> v02.PreparedSpectrum:
    """codec_qoac_h_v02.prepare_field with the fast orbit table; the reference encoder then gives identical bytes."""
    x = np.ascontiguousarray(np.asarray(field, dtype=np.float64))
    topo = Orbits(x.shape, lattice, 32).to_reference(lattice)
    return v02.PreparedSpectrum(field=x, topology=topo, spectrum=np.asarray(np.fft.fftn(x, norm="ortho"), np.complex128))


def encode_law(field: np.ndarray, lattice: np.ndarray, alpha: float) -> bytes:
    return v02.encode_prepared(prepare_field(field, lattice), alpha=alpha, beta=2.0, zlib_level=6)[0]
