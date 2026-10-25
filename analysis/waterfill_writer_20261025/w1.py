#!/usr/bin/env python3
"""QOAC-H writer W1: binary container, per-shell adaptive arithmetic coding, symmetry-predictive coding, and four
Hartree allocations on the v0.2 Hermitian-orbit topology (32 radial shells, conservative Nyquist metric, G = 0 exact).

Allocations (Delta_k is the quantization step of orbit k, q_k = |G_k| / |G|_max):
  law    Delta_k = alpha q_k^2 in every shell (the closed-form operator law, arm A1's allocation)
  wf     the law with reverse water-filling: shell s is written iff E_s > KAPPA alpha^2 H_s, where
         E_s = sum_k m_k w_k |c_k|^2 is its operator-weighted energy and H_s = sum_k m_k w_k q_k^4 p_k / 12 the
         operator-weighted high-rate noise of the law's steps (w_k = q_k^-4, so H_s = sum_k m_k p_k / 12; m_k orbit
         multiplicity, p_k real parts). One scalar alpha; no per-shell search.
  trunc  Delta_k = alpha for q_k <= q_c, nothing above (arm A2's allocation)
  rdo    Delta_k = mult_s q_k^2 with mult_s on the v0.3 ladder or the shell dropped, chosen by the v0.3 Lagrangian
         selection on the exact per-shell (bytes, distortion) curves of this writer (arm A3's allocation)

Coefficients are quantized by rounding (floor(|x| / Delta + 1/2) with the sign of x). With symmetry, the
representative of each star is quantized directly and every other member of the same shell is coded as the quantized
residual from its prediction a * c_rep (or a * conj(c_rep)) at the member's own step.

Stream: b"QW1", version, mode, flags (bit 0 symmetry), shape (3 x u32), lattice (9 x f64), DC (f64), mode parameters,
symmetry generators (u8 count; 9 x i8 and 3 varints each), 32 shell fields (varint: 0 = no segment, else
2 * length + coder + 1; coder 0 = QAC, 1 = zlib), then the segments.
"""
from __future__ import annotations

import math
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "operator_aware_codec_hartree_v02"))
sys.path.insert(0, str(HERE.parent / "qoac_v03_rdo"))
import codec_qoac_h_v02 as v02  # noqa: E402
import codec_qoac_v03 as v3  # noqa: E402
import qac  # noqa: E402
import symmetry as sym  # noqa: E402

MAGIC = b"QW1"
VERSION = 1
MODES = {"law": 0, "wf": 1, "trunc": 2, "rdo": 3}
KAPPA = 1.0
MARGIN = 0.995
SHELLS = 32
TAU_FLOOR = 1e-8          # smallest tolerance of the study: sets the RDO curves' distortion floor (as v0.3)


# --------------------------------------------------------------------------------------------- spectrum and plan
@dataclass
class Field:
    topo: v02.HermitianTopology
    cr: np.ndarray
    ci: np.ndarray
    selfc: np.ndarray
    mw: np.ndarray
    safe: np.ndarray
    shell: np.ndarray
    e_sig: np.ndarray
    ref_cons: float
    ref_safe: float
    dc: float
    plan: sym.Plan
    group: list
    sym_status: dict


def prepare(x, lat, rh, structure=None, use_symmetry=True):
    """Spectrum, operator weights and the law protocol's reference energies (historical RMS, Nyquist-safe sum)."""
    prep = v02.prepare_field(x, lat, shell_count=SHELLS)
    topo = prep.topology
    c = prep.spectrum.ravel()[topo.rep_flat]
    selfc = topo.self_conjugate
    cr = c.real.copy()
    ci = np.where(selfc, 0.0, c.imag)
    m = np.where(selfc, 1.0, 2.0)
    w = v3.operator_weight(topo, "hartree_potential")
    mw = m * w
    safe = ~v3.nyquist_orbits(topo)
    e_sig = mw * (cr * cr + ci * ci)
    ref_cons = x.size * rh ** 2 / (4 * math.pi) ** 2 / topo.g2_safe_max ** -2     # as codec_qoac_v03.analyze
    ref_safe = float(np.sum(e_sig[safe]))
    dc = complex(prep.spectrum.ravel()[0])
    if dc.imag != 0.0:
        raise RuntimeError("DC coefficient is not real")
    N = np.asarray(x.shape, dtype=np.int64)
    if use_symmetry and structure is not None:
        group, status = sym.grid_group(structure, x)
    else:
        group, status = sym.closure([], N), {"status": "off", "spacegroup": "", "ops": 1}
    plan = sym.Plan(topo, group)
    status["classes"] = plan.classes
    status["orbits"] = int(topo.rep_flat.size)
    return Field(topo, cr, ci, selfc, mw, safe, topo.shell_ids.astype(np.int64), e_sig, ref_cons, ref_safe,
                 dc.real, plan, group, status)


def _round(x, st):
    return np.sign(x) * np.floor(np.abs(x) / st + 0.5)


def predicted(plan, idx):
    """For orbits idx (ascending; one shell or part of one): which are coded as residuals from their representative
    (a member whose representative is also in idx), and the representative's position in idx."""
    mem = plan.member[idx]
    pos = np.searchsorted(idx, plan.root[idx])
    pc = np.clip(pos, 0, max(idx.size - 1, 0))
    eff = mem & (pos < idx.size) & (idx[pc] == plan.root[idx])
    return eff, pc


def reconstruct(plan, selfc, qr, qi, steps, idx):
    """Decoded coefficients of the orbits idx from their symbols; shared by encoder and decoder."""
    st = steps[idx]
    chat = qr * st + 1j * (qi * st)
    eff, pos = predicted(plan, idx)
    if np.any(eff):
        mi = np.flatnonzero(eff)
        g = idx[mi]
        src = chat[pos[mi]]
        pred = plan.a[g] * np.where(plan.cj[g], np.conj(src), src)
        pred = np.where(selfc[g], pred.real + 0j, pred)
        chat[mi] = pred + qr[mi] * st[mi] + 1j * (qi[mi] * st[mi])
    return chat


def quantize(F, steps, idx):
    """Symbols (qr, qi) and decoded coefficients of the orbits idx (ascending; one shell or part of one)."""
    plan = F.plan
    cr, ci, sc = F.cr[idx], F.ci[idx], F.selfc[idx]
    st = steps[idx]
    qr = _round(cr, st)
    qi = np.where(sc, 0.0, _round(ci, st))
    eff, pos = predicted(plan, idx)
    if np.any(eff):
        mi = np.flatnonzero(eff)
        g = idx[mi]
        rep = ~eff
        chat_r = np.where(rep, qr * st + 1j * (qi * st), 0)
        src = chat_r[pos[mi]]
        pred = plan.a[g] * np.where(plan.cj[g], np.conj(src), src)
        pred = np.where(sc[mi], pred.real + 0j, pred)
        qr[mi] = _round(cr[mi] - pred.real, st[mi])
        qi[mi] = np.where(sc[mi], 0.0, _round(ci[mi] - pred.imag, st[mi]))
    chat = reconstruct(plan, F.selfc, qr, qi, steps, idx)
    return qr, qi, chat


# ------------------------------------------------------------------------------------------------ allocations
def keep_mask(F, mode, alpha=None, q_cut=None, shells=None):
    """Orbits written by an allocation."""
    if mode == "law":
        return np.ones(F.shell.size, dtype=bool)
    if mode == "wf":
        return wf_shells(F, alpha)[F.shell]
    if mode == "trunc":
        return F.topo.q <= q_cut
    if mode == "rdo":
        return shells[F.shell] >= 0
    raise ValueError(mode)


def wf_shells(F, alpha):
    parts = np.where(F.selfc, 1.0, 2.0)
    m = np.where(F.selfc, 1.0, 2.0)
    E = np.bincount(F.shell, weights=F.e_sig, minlength=SHELLS)
    H = np.bincount(F.shell, weights=m * parts / 12.0, minlength=SHELLS)
    return E > KAPPA * alpha * alpha * H


def steps_of(F, mode, alpha=None, ptp=None, shells=None):
    q2 = F.topo.q ** 2
    if mode in ("law", "wf"):
        return alpha * q2
    if mode == "trunc":
        return np.full(q2.shape, float(alpha))
    if mode == "rdo":
        mult = ptp * v3.LADDER_STEP ** np.arange(v3.LADDER_LO, v3.LADDER_HI + 1, dtype=np.float64)
        j = shells[F.shell]
        return np.where(j >= 0, mult[np.clip(j, 0, None)], 1.0) * q2
    raise ValueError(mode)


def distortion(F, steps, keep):
    """Relative Hartree distortion (squared) in the conservative and Nyquist-safe metrics of the decoded spectrum."""
    e = F.e_sig.copy()
    for s in range(SHELLS):
        idx = shell_order(F, s, keep)
        if idx.size:
            _, _, chat = quantize(F, steps, idx)
            e[idx] = F.mw[idx] * ((F.cr[idx] - chat.real) ** 2 + (F.ci[idx] - chat.imag) ** 2)
    return float(e.sum()) / F.ref_cons, float(e[F.safe].sum()) / F.ref_safe


def spectral_ok(F, steps, keep, tau):
    a, b = distortion(F, steps, keep)
    t = (MARGIN * tau) ** 2
    return a <= t and b <= t


# ----------------------------------------------------------------------------------------------- container
def _varint(n):
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def _read_varint(blob, p):
    n = shift = 0
    while True:
        b = blob[p]
        p += 1
        n |= (b & 0x7F) << shift
        shift += 7
        if not b & 0x80:
            return n, p


def _zseg(r, i):
    mx = max(int(np.max(np.abs(r))), int(np.max(np.abs(i))))
    dt = v02._smallest_signed_dtype(mx)
    inter = np.empty(2 * r.size, dtype=dt)
    inter[0::2] = r
    inter[1::2] = i
    return bytes([np.dtype(dt).itemsize]) + zlib.compress(inter.tobytes(), 6)


def segment(r, i, selfc, kind):
    """The smaller of the QAC and zlib codings of one shell: (payload, coder)."""
    r = np.asarray(r, dtype=np.int64)
    i = np.asarray(i, dtype=np.int64)
    a = qac.encode(r, i, selfc, kind)
    b = _zseg(r, i)
    return (a, 0) if len(a) <= len(b) else (b, 1)


def shell_order(F, s, keep):
    """Orbits of shell s that are written, in coding order (ascending orbit position)."""
    b = F.plan.bounds
    if s + 1 >= b.size:
        return np.zeros(0, dtype=np.int64)
    sl = F.plan.order[b[s]:b[s + 1]]
    return sl[keep[sl]]


def _params(mode, alpha=None, q_cut=None, ptp=None, shells=None):
    if mode in ("law", "wf"):
        return struct.pack("<d", alpha)
    if mode == "trunc":
        return struct.pack("<dd", alpha, q_cut)
    return struct.pack("<d", ptp) + np.asarray(shells, dtype="<i2").tobytes()


def _sym_bytes(F):
    if F.plan.nops <= 1:
        return b""
    gens = sym.generators(F.group, np.asarray(F.topo.shape))
    out = bytearray([len(gens)])
    for M, T in gens:
        out += np.asarray(M, dtype=np.int8).tobytes()
        for t in T:
            out += _varint(int(t))
    return bytes(out)


def encode(F, mode, alpha=None, q_cut=None, ptp=None, shells=None):
    steps = steps_of(F, mode, alpha, ptp, shells)
    keep = keep_mask(F, mode, alpha, q_cut, shells)
    flags = 1 if F.plan.nops > 1 else 0
    head = (MAGIC + bytes([VERSION, MODES[mode], flags]) + struct.pack("<3I", *F.topo.shape)
            + np.asarray(F.topo.lattice, dtype="<f8").tobytes() + struct.pack("<d", F.dc)
            + _params(mode, alpha, q_cut, ptp, shells) + _sym_bytes(F))
    fields, segs = [], []
    for s in range(SHELLS):
        idx = shell_order(F, s, keep)
        if idx.size == 0:
            fields.append(_varint(0))
            continue
        qr, qi, _ = quantize(F, steps, idx)
        pay, coder = segment(qr, qi, F.selfc[idx], predicted(F.plan, idx)[0].astype(np.int64))
        fields.append(_varint(2 * len(pay) + coder + 1))
        segs.append(pay)
    return head + b"".join(fields) + b"".join(segs)


def decode(blob):
    """Decode a W1 stream to the real-space field."""
    if blob[:3] != MAGIC or blob[3] != VERSION:
        raise ValueError("not a W1 stream")
    mode = {v: k for k, v in MODES.items()}[blob[4]]
    flags = blob[5]
    p = 6
    shape = struct.unpack("<3I", blob[p:p + 12])
    p += 12
    lat = np.frombuffer(blob[p:p + 72], dtype="<f8").reshape(3, 3).copy()
    p += 72
    dc = struct.unpack("<d", blob[p:p + 8])[0]
    p += 8
    alpha = q_cut = ptp = shells = None
    if mode in ("law", "wf"):
        alpha = struct.unpack("<d", blob[p:p + 8])[0]
        p += 8
    elif mode == "trunc":
        alpha, q_cut = struct.unpack("<dd", blob[p:p + 16])
        p += 16
    else:
        ptp = struct.unpack("<d", blob[p:p + 8])[0]
        shells = np.frombuffer(blob[p + 8:p + 8 + 2 * SHELLS], dtype="<i2").astype(np.int64)
        p += 8 + 2 * SHELLS
    topo = v02.build_topology(tuple(shape), lat, shell_count=SHELLS)
    N = np.asarray(shape, dtype=np.int64)
    gens = []
    if flags & 1:
        ng = blob[p]
        p += 1
        for _ in range(ng):
            M = np.frombuffer(blob[p:p + 9], dtype=np.int8).astype(np.int64).reshape(3, 3)
            p += 9
            T = []
            for _ in range(3):
                t, p = _read_varint(blob, p)
                T.append(t)
            gens.append((M, np.asarray(T, dtype=np.int64)))
    plan = sym.Plan(topo, sym.closure(gens, N))
    fields = []
    for _ in range(SHELLS):
        f, p = _read_varint(blob, p)
        fields.append(f)
    shell = topo.shell_ids.astype(np.int64)
    F = _Shell(topo, plan, shell)
    if mode == "wf":
        keep = np.isin(shell, [s for s in range(SHELLS) if fields[s]])
    else:
        keep = keep_mask(F, mode, alpha, q_cut, shells)
    steps = steps_of(F, mode, alpha, ptp, shells)
    coeff = np.zeros(topo.rep_flat.size, dtype=np.complex128)
    for s in range(SHELLS):
        idx = shell_order(F, s, keep)
        if fields[s] == 0:
            if idx.size:
                raise ValueError("missing segment")
            continue
        n = (fields[s] - 1) >> 1
        coder = (fields[s] - 1) & 1
        pay = blob[p:p + n]
        p += n
        sc = topo.self_conjugate[idx]
        if coder == 0:
            qr, qi = qac.decode(pay, sc, predicted(plan, idx)[0].astype(np.int64))
        else:
            dt = {1: np.int8, 2: np.int16, 4: np.int32, 8: np.int64}[pay[0]]
            vals = np.frombuffer(zlib.decompress(pay[1:]), dtype=np.dtype(dt).newbyteorder("<")).astype(np.int64)
            qr, qi = vals[0::2], vals[1::2]
        coeff[idx] = reconstruct(plan, topo.self_conjugate, qr.astype(np.float64), qi.astype(np.float64), steps, idx)
    if p != len(blob):
        raise ValueError("trailing bytes")
    full = np.zeros(shape, dtype=np.complex128)
    flat = full.ravel()
    flat[0] = dc
    flat[topo.rep_flat] = coeff
    ns = ~topo.self_conjugate
    flat[topo.partner_flat[ns]] = np.conj(coeff[ns])
    out = np.fft.ifftn(full, norm="ortho")
    if float(np.max(np.abs(out.imag))) > 1e-11 * max(1.0, float(np.max(np.abs(out.real)))):
        raise RuntimeError("real-field invariant violated")
    return np.ascontiguousarray(out.real)


@dataclass
class _Shell:
    topo: v02.HermitianTopology
    plan: sym.Plan
    shell: np.ndarray


# -------------------------------------------------------------------------------------------------- searches
def bisect_scale(ok, lo, hi, iters=60):
    """Largest scale in [lo, hi] (log space) for which ok holds (as the law protocol's bisect_scale)."""
    if not ok(lo):
        return None
    if ok(hi):
        return hi
    best = lo
    a, b = math.log(lo), math.log(hi)
    for _ in range(iters):
        mid = 0.5 * (a + b)
        if ok(math.exp(mid)):
            a = mid
            best = math.exp(mid)
        else:
            b = mid
        if b - a < 1e-9:
            break
    return best


def search_scalar(F, mode, tau, ptp, certify):
    """law / wf: spectral bisection of alpha, then decode and certify (alpha *= 0.99 until certified, at most 40)."""
    def ok(a):
        return spectral_ok(F, steps_of(F, mode, a), keep_mask(F, mode, a), tau)
    a = bisect_scale(ok, 1e-14 * ptp, 1e3 * ptp)
    if a is None:
        return None
    for _ in range(40):
        blob = encode(F, mode, alpha=a)
        rec = decode(blob)
        eh, es = certify(rec)
        if eh < tau and es < tau:
            return {"param": f"alpha_rel={a / ptp:.9g}", "bytes": len(blob), "rec": rec, "hartree_hist": eh,
                    "hartree_safe": es, "shells_written": int(np.count_nonzero(wf_shells(F, a))) if mode == "wf" else SHELLS}
        a *= 0.99
    return None


def search_trunc(F, tau, ptp, certify):
    """As arm A2: every cutoff k/32, spectral bisection of a uniform step, the three smallest candidates decoded and
    certified (alpha *= 0.99, at most 40); the smallest certified stream."""
    q = F.topo.q
    cand = []
    for k in range(1, SHELLS + 1):
        qc = k / SHELLS
        keep = q <= qc
        a = bisect_scale(lambda s: spectral_ok(F, np.full(q.shape, s), keep, tau), 1e-14 * ptp, 1e3 * ptp)
        if a:
            cand.append((len(encode(F, "trunc", alpha=a, q_cut=qc)), qc, a))
    best = None
    for _, qc, a in sorted(cand)[:3]:
        for _ in range(40):
            blob = encode(F, "trunc", alpha=a, q_cut=qc)
            rec = decode(blob)
            eh, es = certify(rec)
            if eh < tau and es < tau:
                if best is None or len(blob) < best["bytes"]:
                    best = {"param": f"q_cut={qc:.6g};alpha_rel={a / ptp:.9g}", "bytes": len(blob), "rec": rec,
                            "hartree_hist": eh, "hartree_safe": es}
                break
            a *= 0.99
    return best


def rdo_analysis(F, ptp):
    """Exact (bytes, distortion) curve of every shell on the v0.3 multiplier ladder, with this writer's segments."""
    q2 = F.topo.q ** 2
    mult = ptp * v3.LADDER_STEP ** np.arange(v3.LADDER_LO, v3.LADDER_HI + 1, dtype=np.float64)
    d_floor = 1e-3 * TAU_FLOOR ** 2 / 32 * F.ref_cons
    allk = np.ones(F.shell.size, dtype=bool)
    curves = []
    for s in range(SHELLS):
        idx = shell_order(F, s, allk)
        if idx.size == 0:
            curves.append(v3.ShellCurve(s, np.array([-1]), np.zeros(1), np.zeros(1), np.zeros(1), np.zeros(1)))
            continue
        e_full = F.e_sig[idx]
        ss = F.safe[idx]
        js, bs, dc, dsf = [-1], [0.0], [float(e_full.sum())], [float(e_full[ss].sum())]
        kind = predicted(F.plan, idx)[0].astype(np.int64)
        for j in range(mult.size - 1, -1, -1):      # coarse -> fine
            steps = np.zeros(F.shell.size)
            steps[idx] = mult[j] * q2[idx]
            qr, qi, chat = quantize(F, steps, idx)
            if not (np.any(qr) or np.any(qi)):
                continue
            d = F.mw[idx] * ((F.cr[idx] - chat.real) ** 2 + (F.ci[idx] - chat.imag) ** 2)
            pay, _ = segment(qr, qi, F.selfc[idx], kind)
            n = len(pay)
            js.append(j)
            bs.append(float(n + len(_varint(2 * n + 2)) - 1))     # segment + its length field beyond the 1-byte empty field
            dc.append(float(d.sum()))
            dsf.append(float(d[ss].sum()))
            if dc[-1] < d_floor:
                break
        curves.append(v3.ShellCurve(s, np.array(js), np.array(bs), np.array(dc), np.array(dsf), np.array(dc)))
    return v3.Analysis(None, "hartree_potential", "operator", ptp, q2, None, mult, F.safe, F.ref_cons, F.ref_safe,
                       curves)


def search_rdo(F, an, tau, ptp, certify):
    """As arm A3: Lagrangian selection with polish at margin 0.995, shrinking by 0.995 until certified (at most 20)."""
    mg = MARGIN
    for _ in range(20):
        ch = v3.select(an, tau, margin=mg, polish=True)
        shells = np.array([int(c.j[i]) for c, i in zip(an.curves, ch)], dtype=np.int64)
        blob = encode(F, "rdo", ptp=ptp, shells=shells)
        rec = decode(blob)
        eh, es = certify(rec)
        if eh < tau and es < tau:
            return {"param": f"margin={mg:.4f}", "bytes": len(blob), "rec": rec, "hartree_hist": eh,
                    "hartree_safe": es, "shells_written": int(np.count_nonzero(shells >= 0))}
        mg *= 0.995
    return None
