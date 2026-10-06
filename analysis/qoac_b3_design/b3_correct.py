#!/usr/bin/env python3
"""QOAC-B3 prototype: partition-faithful correction of a compressed partition
field, side-information coding, and the lossless label-map alternative.

See DESIGN_STUDY.md sections 2-4 for the derivation of the constraints
checked here.
"""
from __future__ import annotations

import lzma
import struct
from dataclasses import dataclass, field

import numpy as np

from ongrid import (Partition, Stencil, cell_volume, is_max_raw, make_stencil,
                    ongrid_partition, successor, vacuum_mask, weighted_candidates)


# --------------------------------------------------------------------------
# Reference context
# --------------------------------------------------------------------------

@dataclass
class Reference:
    f: np.ndarray            # flat reference field
    shape: tuple
    lattice: np.ndarray
    vacval: float | None
    st: Stencil
    part: Partition
    lab: np.ndarray          # flat volnum labels (vacuum = nb+1)
    is_fmax: np.ndarray      # flat bool: f-maxima (basin maxima)
    volume: float


def make_reference(field, lattice, vacval=1e-3) -> Reference:
    f = np.ascontiguousarray(field, dtype=np.float64)
    st = make_stencil(lattice, f.shape)
    part = ongrid_partition(f, lattice, vacval, st)
    is_fmax = np.zeros(f.size, dtype=bool)
    is_fmax[part.maxima] = True
    return Reference(f.ravel().copy(), f.shape, np.asarray(lattice, float), vacval, st,
                     part, part.volnum.ravel().copy(), is_fmax, cell_volume(lattice))


# --------------------------------------------------------------------------
# Constraint checker
# --------------------------------------------------------------------------

@dataclass
class Check:
    ok: bool
    vac: np.ndarray          # flat bool: vacuum-mask mismatch
    nonmax: np.ndarray       # flat bool: successor constraint violated (non-max voxel)
    maxima: np.ndarray       # flat bool: f-maximum no longer a (raw and weighted) maximum
    wrong_succ: np.ndarray   # flat int: decoded successor (for culprit selection)
    counts: dict = field(default_factory=dict)


def check_constraints(g, ref: Reference, tier: str = "B", margin: float = 0.0,
                      vac_margin: float = 0.0, exact: np.ndarray | None = None) -> Check:
    """Evaluate the sufficient conditions of DESIGN_STUDY.md section 2.

    tier "S": successor-exact      s_g(p) == s_f(p) for all non-vacuum p
    tier "B": basin-faithful       lab(s_g(p)) == lab(p), s_g(p) != p for non-max p;
                                    f-maxima remain weighted- and raw-maxima
    margin > 0 (robust mode, tier B only): every decision must win by at least
    `margin` in the weighted comparison (and maxima must exceed every neighbour by
    `margin`) unless the whole 27-point stencil is bit-identical to the reference
    (``exact`` flat bool mask), in which case the decision is identical by
    construction. vac_margin is the analogous margin on |g|/V - vacval.
    """
    g = np.ascontiguousarray(g, dtype=np.float64).ravel()
    N = g.size
    st = ref.st
    if exact is None:
        exact = g == ref.f
    vac_f = ref.lab == ref.part.nbasins + 1
    vac_g = vacuum_mask(g, ref.volume, ref.vacval).ravel()
    vac_bad = vac_g != vac_f
    if ref.vacval is not None and vac_margin > 0:
        close = np.abs(np.abs(g / ref.volume) - ref.vacval) < vac_margin
        vac_bad |= close & ~exact
    sg = successor(g.reshape(ref.shape), st)
    idx = np.arange(N)
    live = ~vac_f
    if tier == "S":
        nonmax = live & (sg != ref.part.succ)
        maxima = live & ref.is_fmax & ~is_max_raw(g.reshape(ref.shape), st)
        nonmax &= ~ref.is_fmax
    elif tier == "B":
        nonmax = live & ~ref.is_fmax & ((sg == idx) | (ref.lab[sg] != ref.lab))
        maxima = live & ref.is_fmax & ((sg != idx) | ~is_max_raw(g.reshape(ref.shape), st))
        if margin > 0:
            stencil_exact = exact & np.all(exact[st.nbr], axis=0)
            T = weighted_candidates(g.reshape(ref.shape), st)
            same = ref.lab[st.nbr] == ref.lab[None, :]
            best_in = np.where(same, T, -np.inf).max(axis=0)
            best_out = np.where(~same, T, -np.inf).max(axis=0)
            gap = best_in - np.maximum(g, best_out)
            nonmax |= live & ~ref.is_fmax & (gap < margin) & ~stencil_exact
            mgap = g - g[st.nbr].max(axis=0)
            maxima |= live & ref.is_fmax & (mgap < margin) & ~stencil_exact
    else:
        raise ValueError(tier)
    ok = not (vac_bad.any() or nonmax.any() or maxima.any())
    return Check(ok, vac_bad, nonmax, maxima, sg,
                 {"vac": int(vac_bad.sum()), "nonmax": int(nonmax.sum()), "maxima": int(maxima.sum())})


# --------------------------------------------------------------------------
# Base codec: uniform scalar quantization (stand-in for SZ/ZFP-class codecs)
# --------------------------------------------------------------------------

def quantize(f: np.ndarray, eps: float) -> tuple[np.ndarray, np.ndarray]:
    q = np.round(np.asarray(f, dtype=np.float64) / (2.0 * eps)).astype(np.int64)
    return q, q.astype(np.float64) * (2.0 * eps)


def rel_quantize(f: np.ndarray, delta: float, floor: float):
    """Pointwise-relative quantization in the log domain.

    g0 = sign(f) exp(2 delta round(log|f| / (2 delta))) for |f| >= floor, else 0.
    Returns (indices, g0, eps_vec) with |f - g0| <= eps_vec, where eps_vec is a
    function of g0 only (decoder-reproducible): (e^delta - 1)|g0|, or floor."""
    x = np.asarray(f, dtype=np.float64)
    big = np.abs(x) >= floor
    q = np.zeros(x.shape, dtype=np.int64)
    q[big] = np.round(np.log(np.abs(x[big])) / (2 * delta)).astype(np.int64)
    g0 = np.zeros_like(x)
    g0[big] = np.sign(x[big]) * np.exp(q[big] * 2 * delta)
    eps_vec = np.where(big, np.expm1(delta) * np.abs(g0) * (1 + 1e-12), floor)
    sgn = np.where(big, np.sign(x), 0).astype(np.int64)
    return q * 4 + (sgn + 1), g0, eps_vec   # sign folded into the index stream


def lorenzo_bytes(q: np.ndarray) -> int:
    """Payload size of quantization indices after 3-D Lorenzo prediction,
    zigzag mapping and xz/LZMA. A crude but real byte count."""
    a = np.asarray(q, dtype=np.int64)
    p = np.zeros_like(a)
    p[1:, :, :] += a[:-1, :, :]
    p[:, 1:, :] += a[:, :-1, :]
    p[:, :, 1:] += a[:, :, :-1]
    p[1:, 1:, :] -= a[:-1, :-1, :]
    p[1:, :, 1:] -= a[:-1, :, :-1]
    p[:, 1:, 1:] -= a[:, :-1, :-1]
    p[1:, 1:, 1:] += a[:-1, :-1, :-1]
    r = (a - p).ravel()
    z = np.where(r >= 0, 2 * r, -2 * r - 1).astype(np.uint64)
    if z.max(initial=0) < 2 ** 16:
        raw = z.astype("<u2").tobytes()
    else:
        raw = z.astype("<u4").tobytes()
    return len(lzma.compress(raw, preset=9 | lzma.PRESET_EXTREME))


# --------------------------------------------------------------------------
# Correction with a refinement ladder
# --------------------------------------------------------------------------

BITS_PER_LEVEL = 4
MAX_REFINE = 3          # levels 1..3 are refinements; level 4 = exact float64
EXACT = MAX_REFINE + 1


def level_value(f: np.ndarray, g0: np.ndarray, eps, level: np.ndarray):
    """Decoder-reproducible value at refinement level k (k=0: base).

    ``eps`` is the base error bound, scalar or per voxel; a per-voxel bound
    must itself be computable by the decoder (e.g. from g0, as in
    ``rel_quantize``)."""
    out = g0.copy()
    eps = np.broadcast_to(np.asarray(eps, dtype=np.float64), g0.shape)
    for k in range(1, MAX_REFINE + 1):
        m = level == k
        if m.any():
            step = 2.0 * eps[m] / float(2 ** (BITS_PER_LEVEL * k))
            r = np.round((f[m] - g0[m]) / step)
            out[m] = g0[m] + r * step
    m = level >= EXACT
    out[m] = f[m]
    return out


@dataclass
class CorrectionResult:
    g: np.ndarray
    level: np.ndarray
    iterations: int
    history: list
    side_bits: int
    side_bytes: int
    n_edits: int
    edits_by_level: dict


def correct(ref: Reference, eps: float, tier: str = "B", margin: float = 0.0,
            vac_margin: float = 0.0, g0: np.ndarray | None = None,
            max_iter: int = 10_000, level0: np.ndarray | None = None) -> CorrectionResult:
    """Iteratively escalate the precision of culprit voxels until the check
    passes. Termination: every iteration strictly increases sum(level), and
    level is capped at EXACT; when every voxel is exact the check passes
    because g == f bit for bit (regular reference assumed)."""
    f = ref.f
    if g0 is None:
        _, g0 = quantize(f, eps)
    g0 = np.ascontiguousarray(g0, dtype=np.float64).ravel()
    if np.ndim(eps):
        eps = np.ascontiguousarray(eps, dtype=np.float64).ravel()
    level = np.zeros(f.size, dtype=np.int64) if level0 is None else np.asarray(level0).ravel().copy()
    g = level_value(f, g0, eps, level)
    history = []
    it = 0
    st = ref.st
    while it < max_iter:
        exact = level >= EXACT
        chk = check_constraints(g, ref, tier, margin, vac_margin, exact | (g == f))
        history.append(chk.counts)
        if chk.ok:
            break
        it += 1
        cul = np.zeros(f.size, dtype=bool)
        cul[chk.vac] = True
        bad = np.flatnonzero(chk.nonmax)
        cul[bad] = True
        cul[ref.part.succ[bad]] = True
        cul[chk.wrong_succ[bad]] = True
        if margin > 0 and bad.size:
            # the strongest out-of-basin competitor
            T = weighted_candidates(g.reshape(ref.shape), st)[:, bad]
            out = ref.lab[st.nbr[:, bad]] != ref.lab[bad][None, :]
            k = np.argmax(np.where(out, T, -np.inf), axis=0)
            has = out.any(axis=0)
            cul[st.nbr[k[has], bad[has]]] = True
        mx = np.flatnonzero(chk.maxima)
        if mx.size:
            cul[mx] = True
            nb = st.nbr[:, mx]
            thr = g[mx] - max(margin, 0.0)
            hit = g[nb] >= thr[None, :]
            cul[nb[hit]] = True
        # if every culprit of a violation is already exact, escalate its stencil
        stuck = cul & (level >= EXACT)
        if stuck.any():
            viol = np.flatnonzero(chk.nonmax | chk.maxima)
            allx = np.all(level[st.nbr[:, viol]] >= EXACT, axis=0) & (level[viol] >= EXACT)
            for p in viol[~allx]:
                cul[st.nbr[:, p]] = True
        cul &= level < EXACT
        if not cul.any():
            raise RuntimeError("correction stalled: reference irregular or margin infeasible")
        level[cul] += 1
        g = level_value(f, g0, eps, level)
    else:
        raise RuntimeError("max_iter reached")
    bits, nbytes = side_info_size(level, g.size)
    edits = {int(k): int((level == k).sum()) for k in range(1, EXACT + 1) if (level == k).any()}
    return CorrectionResult(g.reshape(ref.shape), level.reshape(ref.shape), it, history,
                            bits, nbytes, int((level > 0).sum()), edits)


# --------------------------------------------------------------------------
# Side-information coding (actual bit stream)
# --------------------------------------------------------------------------

class BitWriter:
    def __init__(self):
        self.bits = []

    def put(self, value: int, n: int):
        for i in range(n - 1, -1, -1):
            self.bits.append((value >> i) & 1)

    def gamma(self, x: int):  # Elias gamma, x >= 1
        n = x.bit_length()
        self.put(0, n - 1)
        self.put(x, n)

    def tobytes(self) -> bytes:
        b = self.bits + [0] * (-len(self.bits) % 8)
        return bytes(int("".join(map(str, b[i:i + 8])), 2) for i in range(0, len(b), 8))


SIDE_HEADER = struct.Struct("<8sIdI")  # magic, n_edits, eps, bits/level


def side_info_size(level: np.ndarray, n: int) -> tuple[int, int]:
    """Serialize (position gaps: Elias-gamma; level: truncated unary;
    refinement residual: BITS_PER_LEVEL*k + 1 bits; exact: 64 bits)."""
    lv = np.asarray(level).ravel()
    pos = np.flatnonzero(lv > 0)
    w = BitWriter()
    prev = -1
    for p in pos:
        w.gamma(int(p - prev))
        prev = p
        k = int(lv[p])
        w.put((1 << (k - 1)) - 1 << 1 if k < EXACT else (1 << (EXACT - 1)) - 1, k if k < EXACT else EXACT - 1)
        w.put(0, BITS_PER_LEVEL * k + 1 if k < EXACT else 64)
    payload = len(w.bits)
    return payload + 8 * SIDE_HEADER.size, (payload + 7) // 8 + SIDE_HEADER.size


# --------------------------------------------------------------------------
# Alternative L: lossless label map
# --------------------------------------------------------------------------

def label_map_cost(volnum: np.ndarray) -> dict:
    """Two honest numbers for storing the label map losslessly:
    * lzma_bytes: an actual xz stream of the labels (uint16, C order);
    * ctx_bytes: ideal code length of an adaptive (KT) context model that
      predicts each label from its three causal face neighbours. A real
      arithmetic coder is within a few bytes of this estimate."""
    lab = np.asarray(volnum, dtype=np.int64)
    lzb = len(lzma.compress(lab.astype("<u2").tobytes(), preset=9 | lzma.PRESET_EXTREME))
    n1, n2, n3 = lab.shape
    nlab = int(lab.max()) + 1
    NONE = -1
    A = np.full(lab.shape, NONE); A[:, :, 1:] = lab[:, :, :-1]
    B = np.full(lab.shape, NONE); B[:, 1:, :] = lab[:, :-1, :]
    C = np.full(lab.shape, NONE); C[1:, :, :] = lab[:-1, :, :]
    x = lab.ravel(); a = A.ravel(); b = B.ravel(); c = C.ravel()
    sym = np.where(x == a, 0, np.where(x == b, 1, np.where(x == c, 2, 3)))
    ctx = ((a == b).astype(int) * 1 + (a == c).astype(int) * 2 + (b == c).astype(int) * 4
           + (a == NONE).astype(int) * 8 + (b == NONE).astype(int) * 16 + (c == NONE).astype(int) * 32)
    counts = {}
    bits = 0.0
    for s, k in zip(sym.tolist(), ctx.tolist()):
        cnt = counts.setdefault(k, [0.5, 0.5, 0.5, 0.5])
        bits -= np.log2(cnt[s] / sum(cnt))
        cnt[s] += 1
    n_other = int((sym == 3).sum())
    bits += n_other * np.log2(max(nlab, 2))
    return {"lzma_bytes": int(lzb), "ctx_bytes": int(np.ceil(bits / 8)) + 16,
            "boundary_voxels": int((sym != 0).sum())}


# --------------------------------------------------------------------------
# One-shot variant: per-voxel error allowance from reference margins
# --------------------------------------------------------------------------

def oneshot_allowance(ref: Reference, safety: float = 0.5, guard_ulps: float = 64.0) -> np.ndarray:
    """Per-voxel absolute error allowance eps_p such that ANY field g with
    |g_p - f_p| <= eps_p satisfies the tier-B conditions with the reference
    successor a = s_f(p) as the in-basin witness (DESIGN_STUDY.md 2.5).

    Linear sufficient condition for each comparison c = (p, a, b):
        |w_a - w_b| eps_p + w_a eps_a + w_b eps_b < m_c = T_f(p,a) - T_f(p,b)
    (stay-put competitor: w_a (eps_a + eps_p) < w_a (f_a - f_p)); maxima:
        eps_M + eps_q < f_M - f_q;  vacuum: eps_p < V | |f_p|/V - vacval |.
    Each participating voxel receives safety * m_c / C_c (C_c = sum of the
    coefficients), so every inequality holds with slack (1 - safety) m_c.
    Margins below a floating-point guard get allowance 0 (stored exactly):
    then every value entering that comparison is bit-identical to the
    reference and the decision is identical, including tie-breaking.
    """
    f = ref.f
    st = ref.st
    N = f.size
    w = st.w
    guard = guard_ulps * np.spacing(np.max(np.abs(f))) * (1.0 + w.max())
    allow = np.full(N, np.inf)
    vac_f = ref.lab == ref.part.nbasins + 1
    live = ~vac_f
    idx = np.arange(N)

    def give(vox, m, C):
        a = np.where(m > guard, safety * m / C, 0.0)
        np.minimum.at(allow, vox, a)

    # non-maximum voxels: reference winner a vs stay-put and out-of-basin b
    P = np.flatnonzero(live & ~ref.is_fmax)
    if P.size:
        a = ref.part.succ[P]
        T = weighted_candidates(f.reshape(ref.shape), st)[:, P]   # (26, |P|)
        ka = np.argmax(st.nbr[:, P] == a[None, :], axis=0)
        wa = w[ka]
        Ta = T[ka, np.arange(P.size)]
        m0 = wa * (f[a] - f[P])                     # vs stay-put
        give(P, m0, 2 * wa); give(a, m0, 2 * wa)
        lab_n = ref.lab[st.nbr[:, P]]
        for k in range(26):
            out = lab_n[k] != ref.lab[P]
            if not out.any():
                continue
            pp, aa, bb = P[out], a[out], st.nbr[k, P[out]]
            m = Ta[out] - T[k, out]
            C = np.abs(wa[out] - w[k]) + wa[out] + w[k]
            give(pp, m, C); give(aa, m, C); give(bb, m, C)
    # maxima
    M = np.flatnonzero(live & ref.is_fmax)
    for k in range(26):
        q = st.nbr[k, M]
        m = f[M] - f[q]
        give(M, m, 2.0); give(q, m, 2.0)
    # vacuum threshold
    if ref.vacval is not None:
        m = ref.volume * np.abs(np.abs(f / ref.volume) - ref.vacval)
        give(idx, m, 1.0)
    return allow


def oneshot_levels(allow: np.ndarray, eps) -> np.ndarray:
    """Smallest ladder level whose error bound eps / 2^(4k) is <= allowance."""
    eps = np.broadcast_to(np.asarray(eps, dtype=np.float64), allow.shape)
    with np.errstate(divide="ignore"):
        ratio = np.where(allow > 0, eps / allow, np.inf)
    lev = np.zeros(allow.shape, dtype=np.int64)
    need = ratio > 1.0
    k = np.ceil(np.log2(ratio[need]) / BITS_PER_LEVEL)
    lev[need] = np.where(np.isfinite(k) & (k <= MAX_REFINE), k, EXACT).astype(np.int64)
    return lev
