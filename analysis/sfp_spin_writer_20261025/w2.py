#!/usr/bin/env python3
"""QOAC writer W2: structure-factor prediction (SFP) of the total density, and a compact magnetization sub-stream
(W2M) certified on per-atom moments, both on the W1 writer (analysis/waterfill_writer_20261025/w1.py).

SFP. A crystal's density is, to first order, a superposition of atom-centred densities, whose Fourier coefficients
are sum_t f_t(|G|) S_t(G) with the structure factor S_t(G) = sum_{a in t} exp(-2 pi i h.x_a) of species t (h the
Miller index of G, x_a fractional coordinates). In each radial shell s of the W1 topology the encoder fits
f_t(q) = a_{s,t} + b_{s,t} (q - qbar_s) by operator-weighted least squares (weights m_k w_k, the Hartree metric of
the writer), quantizes the 2T parameters with one step per shell (chosen so that the quantization adds at most
SFP_QERR of the residual's operator-weighted energy), and keeps the shell's prediction only if the quantized
prediction leaves less than SFP_GATE of the shell's energy. The W1 writer then codes the residual c - p. Every shell,
written or not, is decoded as p + residual, so the prediction also lowers the distortion of shells the water-filling
rule leaves out. The decoder recomputes p from the stored structure (species, float32 fractional coordinates) and the
integer parameters with the same function as the encoder. The symmetry plan of W1 applies unchanged: p obeys the same
star relations as c, so the residual does too.

W2 stream: b"QW2", version, flags (bit 0: SFP block present), varint length of the SFP block, SFP block, then a W1
stream (of the residual when bit 0 is set, of the field otherwise). The writer reports the smaller of the two.
SFP block: varint natoms, u8 species count, species Z (u8 each), species index per atom (u8), fractional coordinates
(3 x f32 per atom, in [0, 1)), u32 mask of predicted shells, then per predicted shell (ascending) a zigzag varint
exponent e (step 2^(e/4)) and 2T zigzag varint parameter codes (a_t, b_t per species, species order).

W2M. The magnetization density is written by the W1 water-filling writer (Hartree-law steps Delta = alpha q^2,
symmetry validated against the magnetization itself) with alpha searched against the per-atom moment contract on the
partition of the decoded total density. Basin integration is a linear operator whose symbol is the Fourier transform of
the basin indicators; for regions with sharp boundaries its shell-averaged energy falls as q^-4 (Porod's law), the
decay of the Hartree weight, which is why the Hartree law's allocation is used. In a complete object the magnetization
shares the grid and lattice of the density stream, so the sub-stream omits them and stores the 32 shell fields as a
u32 mask plus the non-empty fields: b"QM2", version, mode, flags, DC (f64), alpha (f64), symmetry generators, u32 mask,
varint fields of the non-empty shells, segments.
"""
from __future__ import annotations

import copy
import math
import struct
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "waterfill_writer_20261025"))
import w1  # noqa: E402

v02 = w1.v02
MAGIC = b"QW2"
MAGIC_M = b"QM2"
VERSION = 1
SHELLS = w1.SHELLS
SFP_DEG = 2             # quadratic form factor within a shell (development: 1, 2, 3, 4, 6 tried; 2 best over both tolerances)
SFP_GATE = 0.5          # keep a shell's prediction if it leaves < 50% of the shell's operator-weighted energy
SFP_QERR = 0.02         # parameter quantization adds <= 2% of the residual energy of the shell
SFP_MIN_PER_PARAM = 4   # fit a shell only with at least 4 orbits per parameter
MARGIN_M = 0.995        # moment search predicate: max error < MARGIN_M * tau_mu
Z = {s: i + 1 for i, s in enumerate(
    "H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr Y Zr Nb Mo "
    "Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf Ta W Re Os Ir Pt Au Hg Tl "
    "Pb Bi Po At Rn Fr Ra Ac Th Pa U Np Pu Am Cm Bk Cf Es Fm".split())}


# ------------------------------------------------------------------------------------------------ varints
def _zz(n):
    return (n << 1) ^ (n >> 63) if n < 0 else n << 1


def _unzz(u):
    return (u >> 1) ^ -(u & 1)


def _varint(n):
    return w1._varint(int(n))


def _read_varint(blob, p):
    return w1._read_varint(blob, p)


# ------------------------------------------------------------------------------------------- structure factors
def miller(topo):
    """Signed Miller indices of the representative orbits."""
    N = np.asarray(topo.shape, dtype=np.int64)
    idx = np.array(np.unravel_index(topo.rep_flat, topo.shape), dtype=np.int64).T
    return np.where(idx > N // 2, idx - N, idx)


def structure_table(symbols, frac):
    """Species (sorted by Z), species index per atom, float32 fractional coordinates in [0, 1)."""
    zs = sorted({Z[s] for s in symbols})
    sp = np.array([zs.index(Z[s]) for s in symbols], dtype=np.int64)
    f = np.mod(np.asarray(frac, dtype=np.float64), 1.0).astype(np.float32)
    f = np.where(f >= np.float32(1.0), np.float32(0.0), f)
    return zs, sp, f


def structure_factors(topo, sp, f32, nsp):
    h = miller(topo).astype(np.float64)
    f = f32.astype(np.float64)
    S = np.zeros((h.shape[0], nsp), dtype=np.complex128)
    for t in range(nsp):
        sel = f[sp == t]
        for a in range(0, sel.shape[0], 4):
            S[:, t] += np.exp(-2j * np.pi * (h @ sel[a:a + 4].T)).sum(axis=1)
    return S


def shell_degree(n_orbits, nsp):
    """Degree of the form factor in a shell of n_orbits orbits: the largest d <= SFP_DEG with at least
    SFP_MIN_PER_PARAM orbits per parameter, -1 if not even d = 0 qualifies (a rule the decoder repeats)."""
    for d in range(SFP_DEG, -1, -1):
        if n_orbits >= SFP_MIN_PER_PARAM * nsp * (d + 1):
            return d
    return -1


def _shell_design(q, S, m):
    qs = q[m]
    q0 = float(qs.mean())
    deg = shell_degree(int(m.sum()), S.shape[1])
    cols = []
    for t in range(S.shape[1]):
        for d in range(deg + 1):
            cols.append(S[m, t] * (qs - q0) ** d)
    return np.array(cols).T


def prediction(topo, S, used, exps, codes):
    """Prediction on the representative orbits from the integer parameters; shared by encoder and decoder."""
    q = topo.q
    shell = topo.shell_ids.astype(np.int64)
    pred = np.zeros(q.size, dtype=np.complex128)
    for s, e, c in zip(used, exps, codes):
        m = shell == s
        A = _shell_design(q, S, m)
        pred[m] = A @ (np.asarray(c, dtype=np.float64) * 2.0 ** (e / 4.0))
    return np.where(topo.self_conjugate, pred.real + 0j, pred)


def sfp_fit(F, symbols, frac):
    """Fit, quantize and gate the per-shell form factors. Returns the prediction info (or None if no shell is kept)."""
    topo = F.topo
    zs, sp, f32 = structure_table(symbols, frac)
    S = structure_factors(topo, sp, f32, len(zs))
    q = topo.q
    c = F.cr + 1j * F.ci
    used, exps, codes = [], [], []
    for s in range(SHELLS):
        m = F.shell == s
        if shell_degree(int(m.sum()), len(zs)) < 0:
            continue
        A = _shell_design(q, S, m)
        npar = A.shape[1]
        w = F.mw[m]
        sw = np.sqrt(w)
        Ar = np.vstack([A.real * sw[:, None], A.imag * sw[:, None]])
        br = np.concatenate([c[m].real * sw, c[m].imag * sw])
        coef, *_ = np.linalg.lstsq(Ar, br, rcond=None)
        e0 = float(np.sum(w * np.abs(c[m]) ** 2))
        e1 = float(np.sum(w * np.abs(c[m] - A @ coef) ** 2))
        colw = np.sum(Ar * Ar, axis=0)
        if e0 <= 0 or e1 >= SFP_GATE * e0 or not np.all(np.isfinite(coef)):
            continue
        delta = math.sqrt(max(SFP_QERR * max(e1, 1e-6 * e0) * 12.0 / (npar * float(colw.mean())), 1e-300))
        e = int(math.floor(4.0 * math.log2(delta)))
        code = np.rint(coef / 2.0 ** (e / 4.0)).astype(np.int64)
        p = A @ (code * 2.0 ** (e / 4.0))
        e1q = float(np.sum(w * np.abs(c[m] - p) ** 2))
        if e1q >= SFP_GATE * e0:
            continue
        used.append(s)
        exps.append(e)
        codes.append(code)
    if not used:
        return None
    pred = prediction(topo, S, used, exps, codes)
    return {"zs": zs, "sp": sp, "f32": f32, "used": used, "exps": exps, "codes": codes, "pred": pred, "S": S}


def restrict(F, info, shells):
    """The prediction restricted to the given shells (None if none of them is predicted)."""
    keep = [i for i, s in enumerate(info["used"]) if s in set(shells)]
    if not keep:
        return None
    out = dict(info, used=[info["used"][i] for i in keep], exps=[info["exps"][i] for i in keep],
               codes=[info["codes"][i] for i in keep])
    out["pred"] = prediction(F.topo, info["S"], out["used"], out["exps"], out["codes"])
    return out


def sfp_block(info):
    out = bytearray(_varint(info["sp"].size))
    out.append(len(info["zs"]))
    out += bytes(info["zs"])
    out += info["sp"].astype(np.uint8).tobytes()
    out += info["f32"].astype("<f4").tobytes()
    mask = 0
    for s in info["used"]:
        mask |= 1 << s
    out += struct.pack("<I", mask)
    for e, c in zip(info["exps"], info["codes"]):
        out += _varint(_zz(int(e)))
        for v in c:
            out += _varint(_zz(int(v)))
    return bytes(out)


def shell_counts(topo):
    return np.bincount(topo.shell_ids.astype(np.int64), minlength=SHELLS)


def parse_sfp_block(blob, counts):
    """Inverse of sfp_block; counts are the orbit counts of the 32 shells (they fix each shell's degree)."""
    p = 0
    nat, p = _read_varint(blob, p)
    nsp = blob[p]
    p += 1
    zs = list(blob[p:p + nsp])
    p += nsp
    sp = np.frombuffer(blob[p:p + nat], dtype=np.uint8).astype(np.int64)
    p += nat
    f32 = np.frombuffer(blob[p:p + 12 * nat], dtype="<f4").reshape(nat, 3).copy()
    p += 12 * nat
    mask = struct.unpack("<I", blob[p:p + 4])[0]
    p += 4
    used = [s for s in range(SHELLS) if mask >> s & 1]
    exps, codes = [], []
    for s in used:
        npar = nsp * (shell_degree(int(counts[s]), nsp) + 1)
        u, p = _read_varint(blob, p)
        exps.append(_unzz(u))
        c = []
        for _ in range(npar):
            u, p = _read_varint(blob, p)
            c.append(_unzz(u))
        codes.append(np.asarray(c, dtype=np.int64))
    if p != len(blob):
        raise ValueError("SFP block length")
    return {"zs": zs, "sp": sp, "f32": f32, "used": used, "exps": exps, "codes": codes}


def residual_field(F, pred):
    """The W1 field of the residual c - p (same topology, plan, operator weights and reference energies)."""
    G = copy.copy(F)
    G.cr = F.cr - pred.real
    G.ci = np.where(F.selfc, 0.0, F.ci - pred.imag)
    G.e_sig = F.mw * (G.cr * G.cr + G.ci * G.ci)
    return G


def real_space(topo, coeff):
    """Real field whose representative-orbit coefficients are coeff (DC zero)."""
    full = np.zeros(topo.shape, dtype=np.complex128)
    flat = full.ravel()
    flat[topo.rep_flat] = coeff
    ns = ~topo.self_conjugate
    flat[topo.partner_flat[ns]] = np.conj(coeff[ns])
    return np.ascontiguousarray(np.fft.ifftn(full, norm="ortho").real)


# ----------------------------------------------------------------------------------------------- W2 container
def wrap(w1_blob, sfp=None):
    blk = sfp_block(sfp) if sfp is not None else b""
    return MAGIC + bytes([VERSION, 1 if sfp is not None else 0]) + _varint(len(blk)) + blk + w1_blob


def decode(blob):
    if blob[:3] != MAGIC or blob[3] != VERSION:
        raise ValueError("not a W2 stream")
    flags = blob[4]
    n, p = _read_varint(blob, 5)
    blk, inner = blob[p:p + n], blob[p + n:]
    rec = w1.decode(inner)
    if flags & 1:
        shape = struct.unpack("<3I", inner[6:18])
        lat = np.frombuffer(inner[18:90], dtype="<f8").reshape(3, 3).copy()
        topo = v02.build_topology(tuple(shape), lat, shell_count=SHELLS)
        info = parse_sfp_block(blk, shell_counts(topo))
        S = structure_factors(topo, info["sp"], info["f32"], len(info["zs"]))
        rec = rec + real_space(topo, prediction(topo, S, info["used"], info["exps"], info["codes"]))
    return rec


def _scalar(F, tau, ptp, certify, pack):
    """As w1.search_scalar (spectral bisection of alpha, then decode and certify, alpha *= 0.99 at most 40 times),
    with the stream built by pack(alpha) and decoded by decode()."""
    def ok(a):
        return w1.spectral_ok(F, w1.steps_of(F, "wf", a), w1.keep_mask(F, "wf", a), tau)
    a = w1.bisect_scale(ok, 1e-14 * ptp, 1e3 * ptp)
    if a is None:
        return None
    for _ in range(40):
        blob = pack(a)
        rec = decode(blob)
        eh, es = certify(rec)
        if eh < tau and es < tau:
            return {"param": f"alpha_rel={a / ptp:.9g}", "alpha": a, "bytes": len(blob), "rec": rec, "hartree_hist": eh,
                    "hartree_safe": es, "shells_written": int(np.count_nonzero(w1.wf_shells(F, a))), "blob": blob}
        a *= 0.99
    return None


def search_wf(F, info, tau, ptp, certify):
    """Water-filling writer on the field (info None) or on the SFP residual; W2 stream bytes."""
    if info is None:
        return _scalar(F, tau, ptp, certify, lambda a: wrap(w1.encode(F, "wf", alpha=a)))
    G = residual_field(F, info["pred"])
    return _scalar(G, tau, ptp, certify, lambda a: wrap(w1.encode(G, "wf", alpha=a), info))


def search_w2(F, info, tau, ptp, certify):
    """The W2 writer: the smallest certified stream among no prediction, the prediction on every gated shell, and the
    prediction on the gated shells that the water-filling rule writes. Returns the result with its 'variant'."""
    cands = []
    r = search_wf(F, None, tau, ptp, certify)
    if r is not None:
        cands.append(dict(r, variant="none", sfp_shells=0))
    if info is not None:
        r = search_wf(F, info, tau, ptp, certify)
        if r is not None:
            cands.append(dict(r, variant="all", sfp_shells=len(info["used"])))
            G = residual_field(F, info["pred"])
            written = np.flatnonzero(w1.wf_shells(G, r["alpha"])).tolist()
            sub = restrict(F, info, written)
            if sub is not None and len(sub["used"]) < len(info["used"]):
                r2 = search_wf(F, sub, tau, ptp, certify)
                if r2 is not None:
                    cands.append(dict(r2, variant="written", sfp_shells=len(sub["used"])))
    if not cands:
        return None
    best = dict(min(cands, key=lambda c: c["bytes"]))
    best["variant_bytes"] = {c["variant"]: int(c["bytes"]) for c in cands}
    none = [c for c in cands if c["variant"] == "none"]
    best["none_bytes"] = int(none[0]["bytes"]) - len(wrap(b"")) if none else None     # the bare W1 stream
    return best


def search_rdo(F, info, tau, ptp, certify):
    """Operational allocation on the SFP residual: arm A3's Lagrangian selection with polish at margin 0.995, shrinking
    by 0.995 until the decoded W2 stream is certified (at most 20), as w1.search_rdo."""
    G = residual_field(F, info["pred"])
    an = w1.rdo_analysis(G, ptp)
    mg = w1.MARGIN
    for _ in range(20):
        ch = w1.v3.select(an, tau, margin=mg, polish=True)
        shells = np.array([int(c.j[i]) for c, i in zip(an.curves, ch)], dtype=np.int64)
        blob = wrap(w1.encode(G, "rdo", ptp=ptp, shells=shells), info)
        rec = decode(blob)
        eh, es = certify(rec)
        if eh < tau and es < tau:
            return {"param": f"margin={mg:.6f}", "bytes": len(blob), "rec": rec, "hartree_hist": eh,
                    "hartree_safe": es, "shells_written": int(np.count_nonzero(shells >= 0))}
        mg *= 0.995
    return None


# ----------------------------------------------------------------------------------- magnetization sub-stream
def _w1_layout(blob):
    """Offsets of a W1 'wf' stream: fields start, the 32 field values, segments start."""
    if blob[:3] != w1.MAGIC or blob[4] != w1.MODES["wf"]:
        raise ValueError("W2M wraps W1 'wf' streams only")
    flags = blob[5]
    p = 6 + 12 + 72 + 8 + 8
    if flags & 1:
        ng = blob[p]
        p += 1
        for _ in range(ng):
            p += 9
            for _ in range(3):
                _, p = _read_varint(blob, p)
    sym_end = p
    fields = []
    for _ in range(SHELLS):
        f, p = _read_varint(blob, p)
        fields.append(f)
    return sym_end, fields, p


def compact_m(blob):
    sym_end, fields, seg = _w1_layout(blob)
    mask = 0
    body = bytearray()
    for s, f in enumerate(fields):
        if f:
            mask |= 1 << s
            body += _varint(f)
    return MAGIC_M + blob[3:6] + blob[90:sym_end] + struct.pack("<I", mask) + bytes(body) + blob[seg:]


def expand_m(cblob, shape, lat):
    if cblob[:3] != MAGIC_M:
        raise ValueError("not a W2M stream")
    flags = cblob[5]
    p = 6 + 8 + 8
    if flags & 1:
        ng = cblob[p]
        p += 1
        for _ in range(ng):
            p += 9
            for _ in range(3):
                _, p = _read_varint(cblob, p)
    head = w1.MAGIC + cblob[3:6] + struct.pack("<3I", *shape) + np.asarray(lat, dtype="<f8").tobytes() + cblob[6:p]
    mask = struct.unpack("<I", cblob[p:p + 4])[0]
    p += 4
    fields = bytearray()
    for s in range(SHELLS):
        if mask >> s & 1:
            f, p = _read_varint(cblob, p)
            fields += _varint(f)
        else:
            fields += _varint(0)
    return head + bytes(fields) + cblob[p:]


def decode_m(cblob, shape, lat):
    return w1.decode(expand_m(cblob, shape, lat))


def moments(m, atom, natoms):
    """Per-atom moments on a 1-based atom label grid (as scope_expansion_20261022/run_spin_s1.sums)."""
    s = np.bincount(atom.ravel(), weights=m.ravel(), minlength=natoms + 2)
    return s[1:natoms + 1] / m.size


def search_m(Fm, shape, lat, atom, natoms, mu_ref, tau_mu, ptp_m, final_check=None):
    """Largest alpha (log bisection, 50 steps) whose decoded magnetization keeps every moment on the partition within
    MARGIN_M * tau_mu; then the final check (the Henkelman binary on the decoded pair), alpha *= 0.99 until it holds
    (at most 40). Returns bytes, alpha, decoded field and the final error, or None."""
    memo = {}

    def run(a):
        if a not in memo:
            cb = compact_m(w1.encode(Fm, "wf", alpha=a))
            rec = decode_m(cb, shape, lat)
            memo[a] = (cb, rec, float(np.max(np.abs(moments(rec, atom, natoms) - mu_ref))) if natoms else 0.0)
        return memo[a]

    a = w1.bisect_scale(lambda x: run(x)[2] < MARGIN_M * tau_mu, 1e-12 * ptp_m, 1e6 * ptp_m, iters=50)
    if a is None:
        return None
    for _ in range(40):
        cb, rec, e = run(a)
        ef = final_check(rec) if final_check is not None else e
        if ef < tau_mu:
            return {"bytes": len(cb), "alpha_rel": a / ptp_m, "rec": rec, "err_partition": e, "err_final": ef,
                    "shells_written": bin(struct.unpack("<I", _mask_of(cb))[0]).count("1"), "blob": cb}
        a *= 0.99
    return None


def _mask_of(cb):
    flags = cb[5]
    p = 6 + 8 + 8
    if flags & 1:
        ng = cb[p]
        p += 1
        for _ in range(ng):
            p += 9
            for _ in range(3):
                _, p = _read_varint(cb, p)
    return cb[p:p + 4]


def porod_exponent(atom, natoms, lat, max_atoms=16):
    """Slope of log(shell-mean of sum_a |FT(1_a)|^2) against log q over shells 2..24 of the W1 topology (descriptive:
    the basin-integration symbol's decay; Porod's law predicts -4). At most max_atoms basins, evenly spaced."""
    topo = v02.build_topology(atom.shape, lat, shell_count=SHELLS)
    sel = np.unique(np.linspace(1, natoms, min(natoms, max_atoms)).round().astype(int)) if natoms else []
    acc = np.zeros(topo.rep_flat.size)
    for a in sel:
        X = np.fft.fftn((atom == a).astype(np.float64), norm="ortho").ravel()[topo.rep_flat]
        acc += np.abs(X) ** 2
    sh = topo.shell_ids.astype(np.int64)
    mean_e = np.bincount(sh, acc, minlength=SHELLS) / np.maximum(np.bincount(sh, minlength=SHELLS), 1)
    mean_q = np.bincount(sh, topo.q, minlength=SHELLS) / np.maximum(np.bincount(sh, minlength=SHELLS), 1)
    k = np.arange(2, 25)
    ok = (mean_e[k] > 0) & (mean_q[k] > 0)
    if ok.sum() < 5:
        return None
    return float(np.polyfit(np.log(mean_q[k][ok]), np.log(mean_e[k][ok]), 1)[0])
