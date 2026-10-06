#!/usr/bin/env python3
"""QOAC-HB v2 runner: pluggable base codecs x post-processors {none, uniform, HAP(mu), CTP-uniform, CTP-HAP(mu)}.

Generalizes analysis/qoac_hb_joint/run_joint.py (frozen; not modified). Every base codec gets the identical
set of post-processors. Bytes per stored stream:
    none            payload
    uniform         payload + QOAC-B1 side channel
    hap:<mu>        payload + QOAC-B1 side channel + 8 (kappa)
    ctp-uniform     payload + 1 flag byte [+ QOAC-B1 side channel if projected]
    ctp-hap:<mu>    payload + 1 flag byte [+ QOAC-B1 side channel + 8 if projected]
Candidate selection per (base, post): options passing the Hartree certificate (and closure when a projection is
stored) are ordered by CR and verified with actual Henkelman Bader, up to MAX_ATTEMPTS options. For CTP each
row offers an unprojected option (U) and a projected option (P); the encoder's Bader check on the unprojected
stream decides which one is stored, so an option is certified only if it is the one CTP would store.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys
import tempfile
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import numpy as np

HERE = Path(__file__).resolve().parent
A = HERE.parent
sys.path.insert(0, str(HERE))
import projection_v2 as pv  # noqa: E402

qb = pv.qb
qoac = pv.qoac
b1 = pv._load("run_engineering", A / "operator_aware_bader_fixed_partition" / "run_engineering.py")
t1 = pv._load("truncation_codec", A / "qoac_h_strong_baselines" / "truncation_codec.py")
assert t1.qoac is qoac
v3 = pv._load("codec_qoac_v03", HERE / "codec_qoac_v03.py")
assert v3.v02 is qoac

TAU_H = 1e-6
TAU_B = 1e-3
CLOSURE = 1e-9
MAX_ATTEMPTS = 5
ALPHA_REL = np.logspace(-7.0, 1.0, 25)
Q_CUTS = (0.05, 0.075, 0.10, 0.15, 0.20, 0.30, 0.50, 0.75, 1.00)
DEFAULT_MUS = (1e-6, 1e-4, 1e-2, 1.0)
R3_TAU = 1e-6
R3_MARGINS = tuple(0.995 * 0.995 ** k for k in range(6))   # least -> most conservative
R3_D_FLOOR_REL = 1e-3 * 1e-12 / 32


# ---------------------------------------------------------------------------------------------------------
# Base codecs (register new ones by name with `register`)
# ---------------------------------------------------------------------------------------------------------

@dataclass
class Context:
    material_id: str
    chg: np.ndarray
    lattice: np.ndarray
    prep: Any
    ptp: float
    work: Path
    core: Any
    wp_rows: list[dict]
    cache: dict = field(default_factory=dict)   # per-material codec state (e.g. the R3 analysis)


@dataclass
class BaseCodec:
    name: str
    candidates: Callable[[Context], list[tuple[str, tuple]]]   # -> [(param label, spec)]
    decode: Callable[[Context, tuple], tuple[np.ndarray, int]]  # spec -> (reconstruction, payload bytes)


REGISTRY: "OrderedDict[str, BaseCodec]" = OrderedDict()


def register(codec: BaseCodec) -> BaseCodec:
    if codec.name in REGISTRY:
        raise ValueError(f"base codec {codec.name!r} already registered")
    REGISTRY[codec.name] = codec
    return codec


def _j_cands(ctx):
    return [(f"alpha_rel={ar:.6g}", (float(ar),)) for ar in ALPHA_REL]


def _j_decode(ctx, spec):
    blob, _ = qoac.encode_prepared(ctx.prep, alpha=spec[0] * ctx.ptp, beta=2.0, zlib_level=6)
    rec, _, _ = qoac.decode_blob(blob)
    return np.asarray(rec, dtype=np.float64), len(blob)


def _t1_cands(ctx):
    return [(f"q_cut={qc};alpha_rel={ar:.6g}", (qc, float(ar))) for qc in Q_CUTS for ar in ALPHA_REL]


def _t1_decode(ctx, spec):
    blob = t1.encode(ctx.prep, alpha=spec[1] * ctx.ptp, q_cut=spec[0])
    return np.asarray(t1.decode(blob), dtype=np.float64), len(blob)


def _gp_cands(ctx):
    rows = [r for r in ctx.wp_rows if r["material_id"] == ctx.material_id and r["status"] == "OK"]
    return [(f"{r['codec']};tol_rel={r['nominal_tolerance_relative']}",
             (r["codec"].lower(), float(r["nominal_tolerance_absolute"]))) for r in rows]


def _gp_decode(ctx, spec):
    rec, nb, _ = ctx.core.codec_roundtrip(spec[0], ctx.chg, spec[1], ctx.work)
    return np.asarray(rec, dtype=np.float64), int(nb)


def _r3_analysis(ctx):
    """QOAC v0.3 analysis of this material, computed once and kept on the per-material context."""
    if "R3" not in ctx.cache:
        try:
            rh, _ = qoac.reference_hartree_rms(ctx.chg, ctx.lattice)
            ctx.cache["R3"] = v3.analyze(ctx.chg, ctx.lattice, operator="hartree_potential", prior="operator",
                                         reference_historical_rms=rh, d_floor_rel=R3_D_FLOOR_REL)
        except Exception as exc:  # stored so every R3 candidate reports it without recomputing
            ctx.cache["R3"] = exc
    an = ctx.cache["R3"]
    if isinstance(an, Exception):
        raise RuntimeError(f"R3 analysis failed: {type(an).__name__}: {an}") from an
    return an


def _r3_cands(ctx):
    return [(f"tau={R3_TAU:g};k={k};margin={mg:.9g}", (k, mg)) for k, mg in enumerate(R3_MARGINS)]


def _r3_decode(ctx, spec):
    an = _r3_analysis(ctx)
    key = ("R3", spec)
    if key not in ctx.cache:
        ctx.cache[key] = v3.select(an, R3_TAU, margin=spec[1], polish=True)
    blob = v3.encode(an, ctx.cache[key])
    return np.asarray(v3.decode(blob), dtype=np.float64), len(blob)


register(BaseCodec("J", _j_cands, _j_decode))     # frozen QOAC-H v0.2 ladder
register(BaseCodec("T1", _t1_cands, _t1_decode))  # frozen spectral-truncation ladder
register(BaseCodec("GP", _gp_cands, _gp_decode))  # frozen WP-G ZFP/SZ3/SPERR rows
register(BaseCodec("R3", _r3_cands, _r3_decode))  # QOAC v0.3 RDO streams, tau = 1e-6, six margins


# ---------------------------------------------------------------------------------------------------------
# Post-processors
# ---------------------------------------------------------------------------------------------------------

def post_names(mus):
    hap = [f"hap:{mu:g}" for mu in mus]
    return ["none", "uniform", *hap, "ctp-uniform", *[f"ctp-{h}" for h in hap]]


def projection_of(post: str) -> str | None:
    """Projection key used by a post-processor ('uniform', 'hap:<mu>' or None)."""
    if post == "none":
        return None
    return post[4:] if post.startswith("ctp-") else post


def parse_args(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--frozen-root", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--shard-count", type=int, default=1)
    p.add_argument("--shard-index", type=int, default=0)
    p.add_argument("--material-id", action="append", default=None, help="restrict to these materials")
    p.add_argument("--bader", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--base", nargs="+", default=None, help="registered base codecs (default: all)")
    p.add_argument("--mu", nargs="+", type=float, default=list(DEFAULT_MUS), help="HAP weights mu")
    return p.parse_args(argv)


def shard_for(mid, n):
    return int.from_bytes(hashlib.sha256(("QOAC-HB-V2|" + mid).encode()).digest()[:8], "big") % n


def write_csv(path, rows):
    fields = []
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


class _LRU(OrderedDict):
    def __init__(self, size):
        super().__init__(); self.size = size

    def get_or(self, key, fn):
        if key in self:
            self.move_to_end(key); return self[key]
        v = fn(); self[key] = v
        while len(self) > self.size:
            self.popitem(last=False)
        return v


# ---------------------------------------------------------------------------------------------------------
# One material
# ---------------------------------------------------------------------------------------------------------

def process(meta, a, core, dev, wp_all, bases, mus):
    mid = meta["material_id"]
    out = {"material_id": mid, "system_type": meta["system_type"], "rows": [], "bader": [], "selected": [], "failures": []}
    chg_blob = b1.fetch(meta["url"])
    if hashlib.sha256(chg_blob).hexdigest() != meta["sha256"]:
        raise RuntimeError("CHGCAR checksum mismatch")
    a0 = b1.fetch(b1.BUCKET + f"aeccar0s/{meta['task_id']}.json.gz")
    a2 = b1.fetch(b1.BUCKET + f"aeccar2s/{meta['task_id']}.json.gz")
    with tempfile.TemporaryDirectory(prefix="qoachb2_") as td:
        work = Path(td)
        grid, _ = dev.build_grid(meta, chg_blob, work)
        chg = np.ascontiguousarray(np.asarray(grid.total, dtype=np.float64))
        ae = np.asarray(dev.decode_mp_chgcar(a0).data["total"], float) + np.asarray(dev.decode_mp_chgcar(a2).data["total"], float)
        if ae.shape != chg.shape or not np.all(np.isfinite(ae)):
            raise RuntimeError("invalid AECCAR")
        st = grid.structure
        lat = np.asarray(st.lattice.matrix, float)
        S = b1.Solver(a.bader, lat, np.asarray(st.frac_coords, float), [s.specie.symbol for s in st], chg.shape, work)
        qref, lflat = S(chg, ae)
        labels = qb.label_grid_from_fortran_flat(lflat, chg.shape)
        side = qb.side_channel_from_field(chg, labels)
        side_uniform = len(side.to_bytes())
        rh, rs = qoac.reference_hartree_rms(chg, lat)
        raw = chg.nbytes

        # projections: key -> (callable, side-channel bytes)
        t0 = time.time()
        s_h, s_rho = pv.reference_scales(chg, lat)
        kappas = [pv.kappa_from_mu(mu, s_h, s_rho) for mu in mus]
        haps = pv.HartreeAwareProjector.build_many(labels, lat, kappas)
        t_pre = time.time() - t0
        projections = {"uniform": (lambda f: qb.project_to_region_sums(f, labels, side.sums), side_uniform)}
        for mu, hp in zip(mus, haps):
            projections[f"hap:{mu:g}"] = (lambda f, hp=hp: hp.project(f, side.sums), side_uniform + hp.side_extra_bytes)
        posts = post_names(mus)
        out.update(npoints=int(chg.size), raw_bytes=int(raw), side_channel_bytes=side_uniform, natoms=len(qref),
                   n_regions=int(np.count_nonzero(qb.region_counts(labels))), hap_precompute_seconds=t_pre,
                   **{f"kappa[{mu:g}]": k for mu, k in zip(mus, kappas)},
                   **{f"gram_cond[{mu:g}]": hp.condition for mu, hp in zip(mus, haps)})

        ctx = Context(mid, chg, lat, qoac.prepare_field(chg, lat, shell_count=32), float(np.ptp(chg)), work, core, wp_all)
        t_proj = 0.0
        n_proj = 0
        # per (base, param): unprojected metrics + per-projection metrics
        metrics: dict[tuple[str, str], dict] = {}
        specs: dict[tuple[str, str], tuple] = {}
        for bname in bases:
            codec = REGISTRY[bname]
            for param, spec in codec.candidates(ctx):
                try:
                    rec, nb = codec.decode(ctx, spec)
                    e0 = rec - chg
                    h0 = qoac.hartree_error_metrics(e0, lat, rh, rs)
                    m = {"payload": int(nb), "U": {"hh": h0[0], "hs": h0[1],
                         "closure": qb.closure_metrics(chg, rec, labels)["max_rel_region_sum_error_scaled"],
                         "linf": float(np.max(np.abs(e0))), "rmse": float(np.sqrt(np.mean(e0 * e0)))}}
                    for key, (fn, _) in projections.items():
                        tp = time.time(); y = fn(rec); t_proj += time.time() - tp; n_proj += 1
                        e = y - chg
                        eh, es = qoac.hartree_error_metrics(e, lat, rh, rs)
                        m[key] = {"hh": eh, "hs": es,
                                  "closure": qb.closure_metrics(chg, y, labels)["max_rel_region_sum_error_scaled"],
                                  "linf": float(np.max(np.abs(e))), "rmse": float(np.sqrt(np.mean(e * e)))}
                    metrics[(bname, param)] = m
                    specs[(bname, param)] = spec
                except Exception as exc:
                    out["failures"].append({"material_id": mid, "base": bname, "param": param,
                                            "error": f"{type(exc).__name__}: {exc}"[:400]})
        out.update(projection_seconds_total=t_proj, projections_applied=n_proj)

        def hpass(mm, closure):
            return mm["hh"] < TAU_H and mm["hs"] < TAU_H and (not closure or mm["closure"] <= CLOSURE)

        # option tables
        options: dict[tuple[str, str], list[dict]] = {}
        for (bname, param), m in metrics.items():
            nb = m["payload"]
            for post in posts:
                pk = projection_of(post)
                ctp = post.startswith("ctp-")
                flag = pv.CTP_FLAG_BYTES if ctp else 0
                kinds = (["U"] if pk is None else (["U", pk] if ctp else [pk]))
                for kind in kinds:
                    mm = m[kind]
                    extra = flag + (0 if kind == "U" else projections[kind][1])
                    tot = nb + extra
                    row = {"material_id": mid, "base": bname, "post": post, "param": param, "stored": kind,
                           "payload_bytes": nb, "extra_bytes": extra, "total_bytes": tot, "compression_ratio": raw / tot,
                           "hartree_hist_pre": m["U"]["hh"], "hartree_safe_pre": m["U"]["hs"],
                           "hartree_hist": mm["hh"], "hartree_safe": mm["hs"], "closure_scaled": mm["closure"],
                           "density_Linf": mm["linf"], "density_RMSE": mm["rmse"], "extra_fraction": extra / tot,
                           "hartree_pass": hpass(mm, kind != "U")}
                    out["rows"].append(row)
                    if row["hartree_pass"]:
                        options.setdefault((bname, post), []).append(row)

        # Bader verification
        fields = _LRU(4)
        bcache: dict[tuple[str, str, str], tuple[float, float]] = {}

        def field_of(bname, param, kind):
            def make():
                rec, nb = REGISTRY[bname].decode(ctx, specs[(bname, param)])
                if nb != metrics[(bname, param)]["payload"]:
                    raise RuntimeError("non-deterministic payload size")
                return rec
            rec = fields.get_or((bname, param), make)
            return rec if kind == "U" else projections[kind][0](rec)

        def bader(bname, param, kind):
            key = (bname, param, kind)
            if key not in bcache:
                q, lab = S(field_of(bname, param, kind), ae)
                bcache[key] = (float(np.max(np.abs(q - qref))), float(np.mean(lab != lflat)))
            return bcache[key]

        def ok(r):
            return r[0] <= TAU_B and r[1] == 0.0

        for bname in bases:
            for post in posts:
                opts = sorted(options.get((bname, post), []), key=lambda r: -r["compression_ratio"])
                sel = {"material_id": mid, "base": bname, "post": post, "n_hartree_pass": len(opts), "certified": False,
                       "attempts": 0}
                for k, r in enumerate(opts[:MAX_ATTEMPTS]):
                    try:
                        ctp = post.startswith("ctp-")
                        bu = bader(bname, r["param"], "U")
                        decision = ("unprojected" if ok(bu) else "projected") if ctp else ""
                        if r["stored"] == "U":
                            bs = bu
                            cert = ok(bu)
                        elif ctp and decision == "unprojected":
                            bs = (float("nan"), float("nan"))
                            cert = False  # CTP would store the unprojected stream for this row
                        else:
                            bs = bader(bname, r["param"], r["stored"])
                            cert = ok(bs)
                        rowb = {"material_id": mid, "base": bname, "post": post, "param": r["param"], "stored": r["stored"],
                                "attempt": k + 1, "compression_ratio": r["compression_ratio"], "ctp_decision": decision,
                                "bader_error_e": bs[0], "reassigned_frac": bs[1],
                                "unprojected_bader_error_e": bu[0], "unprojected_reassigned_frac": bu[1], "certified": cert}
                    except Exception as exc:
                        out["failures"].append({"material_id": mid, "base": bname, "param": r["param"], "post": post,
                                                "error": f"bader: {type(exc).__name__}: {exc}"[:400]})
                        continue
                    out["bader"].append(rowb)
                    sel["attempts"] = k + 1
                    if cert:
                        sel.update(certified=True, param=r["param"], stored=r["stored"], ctp_decision=decision,
                                   compression_ratio=r["compression_ratio"], total_bytes=r["total_bytes"],
                                   hartree_hist=r["hartree_hist"], hartree_safe=r["hartree_safe"],
                                   bader_error_e=bs[0], density_Linf=r["density_Linf"], extra_fraction=r["extra_fraction"])
                        break
                out["selected"].append(sel)
        out["bader_solves"] = len(bcache) + 1
    return out


def main(argv=None):
    a = parse_args(argv)
    out = a.output_dir.resolve(); out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(a.frozen_root.resolve() / "validation"))
    sys.path.insert(0, str(a.repo_root.resolve() / "validation" / "qsq_prospective"))
    import external_end_to_end as core
    import development_compatibility_smoke as dev
    bases = a.base or list(REGISTRY)
    unknown = [b for b in bases if b not in REGISTRY]
    if unknown:
        raise SystemExit(f"unknown base codec(s): {unknown}; registered: {list(REGISTRY)}")
    mus = [float(m) for m in a.mu]
    with open(a.repo_root / "analysis/extensions_20260930/WP-G/rows.csv", encoding="utf-8") as f:
        wp_all = list(csv.DictReader(f))
    with open(a.manifest, encoding="utf-8") as f:
        manifest = list(csv.DictReader(f))
    if a.material_id:
        manifest = [m for m in manifest if m["material_id"] in set(a.material_id)]
    planned = [m for m in manifest if shard_for(m["material_id"], a.shard_count) == a.shard_index]
    rows, bader, selected, fails, mats = [], [], [], [], []
    for meta in planned:
        t0 = time.time()
        try:
            r = process(meta, a, core, dev, wp_all, bases, mus)
            rows += r.pop("rows"); bader += r.pop("bader"); selected += r.pop("selected"); fails += r.pop("failures")
            mats.append(r | {"status": "SUCCESS", "seconds": time.time() - t0})
        except Exception as exc:
            mats.append({"material_id": meta["material_id"], "status": "FAILED", "error": f"{type(exc).__name__}: {exc}"[:400]})
        print(f"QOACHB2_DONE {meta['material_id']} {mats[-1]['status']} seconds={time.time() - t0:.1f}", flush=True)
    i = a.shard_index
    for name, data in (("rows", rows), ("bader", bader), ("selected", selected), ("failures", fails), ("materials", mats)):
        write_csv(out / f"{name}_shard_{i:02d}.csv", data if data else [{"material_id": ""}])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
