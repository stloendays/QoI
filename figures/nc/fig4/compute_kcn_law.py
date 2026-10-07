"""Data for NC Fig. 4: how the closed-form Hartree law allocates error and bytes on one density (KCN, mp-676693).

KCN is the development material already shown in Figs. 1a and 3e. Descriptive only: no confirmatory claim rests on it.

For the Hartree potential (squared weight w = |G|^-4, conservative Nyquist metric) it builds, with the project's own
codecs and certificates,
  - rate-distortion curves (compressed bytes against decoded Hartree relative error, both historical and Nyquist-safe
    operators, the larger reported) for
      law       QOAC-H v0.2 stream, Delta_G = alpha q^2              (A1 codec)
      uniform   the same stream with Delta_G = alpha                 (Part B operator-blind arm)
      trunc     T1 truncation, uniform inside q <= q_c, nothing above (A2 codec; lower envelope over q_c = k/32)
      zfp, sz3, sperr  pointwise codecs by absolute tolerance       (A6 members; SPERR if its plugin loads)
  - the certified point of every arm at tau = 1e-4, 1e-6 and 1e-8 (highest-ratio decoded stream below tau, the same
    bisection as the Part A runner), and at tau = 1e-6:
      bytes per radial shell (law, uniform, trunc),
      decoded error spectrum per radial bin: error energy and Hartree-weighted error energy (all arms),
      the step-size map Delta_G on the reciprocal plane spanned by b1 and b2 through G = 0 (law, uniform, trunc).

    D:/Research/QoI-final4-local/venv/Scripts/python.exe compute_kcn_law.py   -> data/kcn_law.npz, data/kcn_law.json
"""
from __future__ import annotations

import csv
import hashlib
import json
import logging
import math
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FROZEN_VALIDATION = Path(r"D:\Research\QoI-final4-local\frozen_repo\validation")
CACHE = Path(r"D:\Research\QoI-ext-cache\densities")
sys.path.insert(0, str(FROZEN_VALIDATION))
sys.path.insert(0, str(REPO / "validation" / "qsq_prospective"))
sys.path.insert(0, str(REPO / "analysis" / "operator_aware_codec_hartree_v02"))
sys.path.insert(0, str(REPO / "analysis" / "qoac_h_strong_baselines"))
import development_compatibility_smoke as dev  # noqa: E402
import external_end_to_end as core  # noqa: E402
import codec_qoac_h_v02 as v02  # noqa: E402
import truncation_codec as t1  # noqa: E402

logging.disable(logging.WARNING)
KCN = "mp-676693"
TAUS = (1e-4, 1e-6, 1e-8)
MARGIN = 0.995
NBIN = 48


def load():
    meta = next(r for r in csv.DictReader(open(REPO / "materials_metadata.csv", encoding="utf-8"))
                if r["material_id"] == KCN)
    blob = (CACHE / f"{meta['sha256']}.bin").read_bytes()
    assert hashlib.sha256(blob).hexdigest() == meta["sha256"]
    td = tempfile.mkdtemp(prefix="nc4_")
    grid, _ = dev.build_grid(meta, blob, Path(td))
    x = np.ascontiguousarray(np.asarray(grid.total, dtype=np.float64))
    return x, np.asarray(grid.structure.lattice.matrix, float), Path(td)


class Spec:
    """Exact orbit-space Hartree distortion (all orbits and Nyquist-safe orbits) for steps and a keep mask."""

    def __init__(self, prep):
        t = prep.topology
        c = prep.spectrum.ravel()[t.rep_flat]
        self.cr, self.ci = c.real.copy(), np.where(t.self_conjugate, 0.0, c.imag)
        self.selfc = t.self_conjugate
        g2 = t.g2_safe_rep / t.g2_safe_max
        self.mw = np.where(t.self_conjugate, 1.0, 2.0) * g2 ** -2.0
        nx, ny, nz = t.shape
        yz = ny * nz
        i, j, k = t.rep_flat // yz, (t.rep_flat % yz) // nz, t.rep_flat % nz
        nyq = np.zeros(i.size, bool)
        for idx, n in ((i, nx), (j, ny), (k, nz)):
            if n % 2 == 0:
                nyq |= idx == n // 2
        self.safe = ~nyq
        p = self.mw * (self.cr ** 2 + self.ci ** 2)
        self.ref_all, self.ref_safe = float(p.sum()), float(p[self.safe].sum())

    def err(self, steps, keep=None):
        qr, qi = np.rint(self.cr / steps), np.rint(self.ci / steps)
        qi[self.selfc] = 0
        er, ei = self.cr - qr * steps, self.ci - qi * steps
        e = self.mw * (er * er + ei * ei)
        if keep is not None:
            e = np.where(keep, e, self.mw * (self.cr ** 2 + self.ci ** 2))
        return math.sqrt(max(float(e.sum()) / self.ref_all, float(e[self.safe].sum()) / self.ref_safe))


def bisect(ok, lo, hi, iters=60):
    if not ok(lo):
        return None
    if ok(hi):
        return hi
    a, b, best = math.log(lo), math.log(hi), lo
    for _ in range(iters):
        m = 0.5 * (a + b)
        if ok(math.exp(m)):
            a, best = m, math.exp(m)
        else:
            b = m
        if b - a < 1e-9:
            break
    return best


def main():
    t0 = time.time()
    x, lat, work = load()
    raw = x.nbytes
    ptp = float(np.ptp(x))
    rh, rs = v02.reference_hartree_rms(x, lat)
    prep = v02.prepare_field(x, lat)
    topo = prep.topology
    S = Spec(prep)
    q = topo.q

    def hartree(rec):
        eh, es = v02.hartree_error_metrics(rec - x, lat, rh, rs)
        return max(eh, es)

    # ---- encoders ---------------------------------------------------------------------------------------------
    def enc_law(a):
        b, _ = v02.encode_prepared(prep, alpha=a, beta=2.0)
        return b, v02.decode_blob(b)[0]

    def enc_uni(a):
        b, _ = v02.encode_prepared(prep, alpha=a, beta=0.0)
        return b, v02.decode_blob(b)[0]

    def enc_tr(a, qc):
        b = t1.encode(prep, alpha=a, q_cut=qc)
        return b, t1.decode(b)

    out = {"material_id": KCN, "formula": "KCN", "shape": list(x.shape), "raw_bytes": raw, "ptp": ptp, "rd": {},
           "cert": {}}
    # ---- rate-distortion curves ---------------------------------------------------------------------------------
    for arm, fn, beta in (("law", enc_law, 2.0), ("uniform", enc_uni, 0.0)):
        pts = []
        for ar in np.logspace(-9.5, -0.5, 46):
            b, rec = fn(float(ar * ptp))
            pts.append((len(b), hartree(rec)))
        out["rd"][arm] = pts
        print(arm, "rd done", round(time.time() - t0), flush=True)
    env = []
    for kq in range(1, 33):
        qc = kq / 32
        keep = q <= qc
        for ar in np.logspace(-9.0, -1.0, 17):
            a = float(ar * ptp)
            e = S.err(np.full(q.shape, a), keep)
            if e > 3e-2:
                continue
            b = t1.encode(prep, alpha=a, q_cut=qc)
            env.append((len(b), e, qc))
    out["rd"]["trunc_all"] = env
    print("trunc rd done", round(time.time() - t0), flush=True)
    codecs = ["zfp", "sz3", "sperr"]
    for c in list(codecs):
        pts = []
        try:
            for tr in np.logspace(-9.0, -1.0, 33):
                rec, nb, _ = core.codec_roundtrip(c, x, float(tr * ptp), work)
                pts.append((int(nb), hartree(np.asarray(rec, float))))
        except Exception as exc:  # SPERR plugin may be missing in this environment
            print("skip", c, exc, flush=True)
            codecs.remove(c)
            continue
        out["rd"][c] = pts
        print(c, "rd done", round(time.time() - t0), flush=True)

    # ---- certified points (same bisection and decode back-off as the Part A runner) -----------------------------
    keep_streams = {}
    for tau in TAUS:
        cert = {}
        a = bisect(lambda s: S.err(s * q ** 2) <= MARGIN * tau, 1e-14 * ptp, 1e3 * ptp)
        for _ in range(40):
            b, rec = enc_law(a)
            if hartree(rec) < tau:
                break
            a *= 0.99
        cert["law"] = dict(bytes=len(b), cr=raw / len(b), hartree=hartree(rec), alpha_rel=a / ptp)
        keep_streams[("law", tau)] = (b, rec, np.full(q.shape, a) * q ** 2, None)
        a = bisect(lambda s: S.err(np.full(q.shape, s)) <= MARGIN * tau, 1e-14 * ptp, 1e3 * ptp)
        for _ in range(40):
            b, rec = enc_uni(a)
            if hartree(rec) < tau:
                break
            a *= 0.99
        cert["uniform"] = dict(bytes=len(b), cr=raw / len(b), hartree=hartree(rec), alpha_rel=a / ptp)
        keep_streams[("uniform", tau)] = (b, rec, np.full(q.shape, a), None)
        best = None
        for kq in range(1, 33):
            qc = kq / 32
            keep = q <= qc
            a = bisect(lambda s: S.err(np.full(q.shape, s), keep) <= MARGIN * tau, 1e-14 * ptp, 1e3 * ptp)
            if a is None:
                continue
            nb = len(t1.encode(prep, alpha=a, q_cut=qc))
            if best is None or nb < best[0]:
                best = (nb, qc, a)
        _, qc, a = best
        for _ in range(40):
            b, rec = enc_tr(a, qc)
            if hartree(rec) < tau:
                break
            a *= 0.99
        cert["trunc"] = dict(bytes=len(b), cr=raw / len(b), hartree=hartree(rec), alpha_rel=a / ptp, q_cut=qc)
        keep_streams[("trunc", tau)] = (b, rec, np.where(q <= qc, a, np.inf), qc)
        for c in codecs:
            seen = {}

            def okc(t):
                rec, nb, _ = core.codec_roundtrip(c, x, float(t), work)
                rec = np.asarray(rec, float)
                good = hartree(rec) < tau
                if good:
                    seen[t] = (int(nb), rec)
                return good

            bisect(okc, 1e-14 * ptp, 1.0 * ptp)
            if seen:
                nb, rec = min(seen.values(), key=lambda v: v[0])
                cert[c] = dict(bytes=nb, cr=raw / nb, hartree=hartree(rec))
                keep_streams[(c, tau)] = (None, rec, None, None)
        out["cert"]["%g" % tau] = cert
        print("tau", tau, {k: round(v["cr"], 2) for k, v in cert.items()}, round(time.time() - t0), flush=True)

    # ---- tau = 1e-6 diagnostics ------------------------------------------------------------------------------------
    tau = 1e-6
    arrays = {}
    edges = np.linspace(0.0, 1.0, NBIN + 1)
    bins = np.clip(np.digitize(q, edges) - 1, 0, NBIN - 1)
    mult = np.where(topo.self_conjugate, 1.0, 2.0)
    g2 = topo.g2_safe_rep / topo.g2_safe_max
    c0 = prep.spectrum.ravel()[topo.rep_flat]
    arrays["bin_edges"] = edges
    arrays["ref_power"] = np.bincount(bins, mult * np.abs(c0) ** 2, NBIN)
    arrays["modes"] = np.bincount(bins, mult, NBIN)
    for (arm, t), (b, rec, steps, qc) in keep_streams.items():
        if t != tau:
            continue
        d = np.fft.fftn(rec - x, norm="ortho").ravel()[topo.rep_flat]
        e = mult * np.abs(d) ** 2
        arrays[f"err_{arm}"] = np.bincount(bins, e, NBIN)
        arrays[f"werr_{arm}"] = np.bincount(bins, e * g2 ** -2.0, NBIN)
        if b is not None and arm in ("law", "uniform", "trunc"):
            hd = json.loads(b[len(v02.MAGIC) + 8: len(v02.MAGIC) + 8 + int.from_bytes(b[len(v02.MAGIC):len(v02.MAGIC) + 8], "little")])
            arrays[f"shell_bytes_{arm}"] = np.array([r.get("compressed_bytes", 0) for r in hd["shells"]], float)
    # step-size maps on the (b1, b2) plane through G = 0 (k3 = 0), in Cartesian reciprocal coordinates
    nx, ny, _ = x.shape
    fi = np.rint(np.fft.fftfreq(nx) * nx).astype(int)
    fj = np.rint(np.fft.fftfreq(ny) * ny).astype(int)
    bvec = 2.0 * np.pi * np.linalg.inv(lat).T
    I, J = np.meshgrid(np.fft.fftshift(fi), np.fft.fftshift(fj), indexing="ij")
    G = I[..., None] * bvec[0] + J[..., None] * bvec[1]
    g2full = v02.conservative_g2(x.shape, lat)[:, :, 0]
    g2p = np.fft.fftshift(g2full)
    qp = np.sqrt(g2p / topo.g2_safe_max)
    for arm in ("law", "uniform", "trunc"):
        c = out["cert"]["%g" % tau][arm]
        a = c["alpha_rel"] * ptp
        if arm == "law":
            st = a * qp ** 2
        elif arm == "uniform":
            st = np.full(qp.shape, a)
        else:
            st = np.where(qp <= c["q_cut"], a, np.nan)
        st[(I == 0) & (J == 0)] = np.nan          # G = 0 is stored exactly
        arrays[f"map_{arm}"] = st / ptp
    arrays["map_gx"], arrays["map_gy"] = G[..., 0], G[..., 1]
    arrays["map_b"] = bvec
    arrays["gmax"] = np.array(math.sqrt(topo.g2_safe_max))
    np.savez_compressed(HERE / "data" / "kcn_law.npz", **arrays)
    out["seconds"] = time.time() - t0
    (HERE / "data" / "kcn_law.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("done", round(time.time() - t0))


if __name__ == "__main__":
    (HERE / "data").mkdir(exist_ok=True)
    main()
