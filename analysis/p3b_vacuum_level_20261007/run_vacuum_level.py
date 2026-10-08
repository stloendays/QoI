#!/usr/bin/env python3
"""Vacuum-level error of the certified P3b Part A streams, one slab per call (PROTOCOL.md).

For each slab: load the exact NOMAD CHGCAR (SHA-256 and byte count from the manifest), fix the surface normal and
the vacuum window from the reference density, regenerate every certified A1/A2/A3/A5/A6 stream of the P3b law run
with the frozen Part A code (`analysis/qoac_v03_rdo/run_engineering.py`), check that it reproduces the recorded
bytes and Hartree relative errors, and evaluate Delta Phi on the decoded field.

Two regeneration routes (PROTOCOL.md section 3):
- R: from the recorded parameter string (A1/A2/A6 parameters are printed to 9 significant digits);
- S: the frozen `run_engineering.material` rerun unchanged (its deterministic searches recover the full-precision
  parameters); its `certify` is wrapped only to keep the planar average of each decoded error along the normal axis.
The stream used is an exact reproduction if one exists (R before S), else a within-tolerance one (R before S); a
stream that neither route reproduces is excluded and counted.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import sys
import tempfile
import time
import traceback
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "qoac_v03_rdo"))
import vacuum_level as vl  # noqa: E402
import run_engineering as eng  # noqa: E402  (frozen Part A code: v3, t1, v02, certify, TAUS, MARGIN, material)

ARMS = ("A1", "A2", "A3", "A5", "A6")
BYTES_ABS_TOL = 16          # reproduce: |bytes - recorded| <= 16 bytes
ERR_REL_TOL = 1e-6          # reproduce: |e - recorded| <= 1e-6 * recorded, for both Hartree metrics; and e < tau
EXACT_ERR_REL = 1e-12       # "exact": identical bytes and both Hartree errors within 1e-12 relative
DOWNLOAD_ATTEMPTS = 3


def certified_streams(rows_csv: Path, material_id: str) -> dict:
    """{(arm, tau): recorded row} — the certified row with the largest CR (first in file order on ties)."""
    best: dict = {}
    with open(rows_csv, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["material_id"] != material_id or r["arm"] not in ARMS:
                continue
            if r["certified"].strip().lower() != "true":
                continue
            key = (r["arm"], float(r["tau"]))
            if key not in best or float(r["cr"]) > float(best[key]["cr"]):
                best[key] = r
    return best


def parse_param(param: str) -> dict:
    out = {}
    for part in param.split(";"):
        k, v = part.split("=", 1)
        out[k] = v
    return out


def margin_value(text: str) -> float:
    """The exact float margin of eng.material's retry sequence (0.995, 0.995*0.995, ...) printed as `text`."""
    mg = eng.MARGIN
    for _ in range(20):
        if f"{mg:.4f}" == text:
            return mg
        mg *= 0.995
    raise ValueError(f"margin {text!r} is not in the frozen retry sequence")


def check(nbytes: int, eh: float, es: float, rec_row: dict, tau: float) -> tuple[bool, bool]:
    """(reproduced, exact) against the recorded row."""
    rb, re_h, re_s = int(rec_row["bytes"]), float(rec_row["hartree_hist"]), float(rec_row["hartree_safe"])
    db = abs(int(nbytes) - rb)
    reproduced = (db <= BYTES_ABS_TOL and abs(eh - re_h) <= ERR_REL_TOL * re_h and abs(es - re_s) <= ERR_REL_TOL * re_s
                  and eh < tau and es < tau)
    exact = db == 0 and abs(eh - re_h) <= EXACT_ERR_REL * re_h and abs(es - re_s) <= EXACT_ERR_REL * re_s
    return bool(reproduced), bool(exact)


def fetch(dev, meta: dict, cache: Path) -> bytes:
    """The exact source bytes; the same cache file name as run_engineering.material, so route S reuses them."""
    cp = cache / f"{meta['material_id']}.src"
    if cp.exists() and hashlib.sha256(cp.read_bytes()).hexdigest() == meta["sha256"]:
        return cp.read_bytes()
    err = None
    for attempt in range(DOWNLOAD_ATTEMPTS):
        try:
            blob = dev.fetch_exact(meta["url"], meta["sha256"], int(meta["source_bytes"]))
            cp.write_bytes(blob)
            return blob
        except Exception as exc:  # a SHA-256 or byte-count mismatch fails on every attempt
            err = exc
            time.sleep(30 * (attempt + 1))
    raise RuntimeError(f"download failed after {DOWNLOAD_ATTEMPTS} attempts: {err}")


def route_r(x, lat, ptp, rh, rs, streams, axis, work, core):
    """Regenerate every recorded certified stream from its printed parameter. {(arm, tau): result dict}."""
    v02, v3, t1 = eng.v02, eng.v3, eng.t1
    need = {arm for arm, _ in streams}
    d_floor = 1e-3 * min(eng.TAUS) ** 2 / 32
    anO = v3.analyze(x, lat, prior="operator", reference_historical_rms=rh, d_floor_rel=d_floor)
    anB = (v3.analyze(x, lat, prior="flat", reference_historical_rms=rh, d_floor_rel=d_floor, select_operator="density")
           if "A5" in need else None)
    prep = anO.prep
    out = {}
    for (arm, tau), rec_row in streams.items():
        p = parse_param(rec_row["param"])
        try:
            if arm == "A1":
                b, _ = v02.encode_prepared(prep, alpha=float(p["alpha_rel"]) * ptp, beta=2.0, zlib_level=6)
                nbytes = len(b)
                rec, _, _ = v02.decode_blob(b)
            elif arm == "A2":
                b = t1.encode(prep, alpha=float(p["alpha_rel"]) * ptp, q_cut=float(p["q_cut"]))
                nbytes = len(b)
                rec = t1.decode(b)
            elif arm in ("A3", "A5"):
                an, pol = (anO, True) if arm == "A3" else (anB, False)
                ch = v3.select(an, tau, margin=margin_value(p["margin"]), polish=pol)
                b = v3.encode(an, ch)
                nbytes = len(b)
                rec = v3.decode(b)
            else:
                rec, nbytes, _ = core.codec_roundtrip(p["codec"], x, float(p["abs_tol_rel"]) * ptp, work)
                rec = np.asarray(rec, dtype=np.float64)
            eh, es, _, _ = eng.certify(rec, x, lat, rh, rs)
            d = rec - x
            out[(arm, tau)] = {"bytes": int(nbytes), "eh": eh, "es": es, "profile": vl.planar_average(d, axis),
                               "delta_electrons": float(np.mean(d))}
        except Exception as exc:
            out[(arm, tau)] = {"error": f"{type(exc).__name__}: {exc}"[:300]}
    return out


def route_s(meta, repo, frozen, cache, axis):
    """Rerun the frozen run_engineering.material unchanged; {(arm, tau, param): result dict}, failures, seconds."""
    captured = []
    orig = eng.certify

    def wrapped(rec, x, lat, rh, rs):
        res = orig(rec, x, lat, rh, rs)
        d = np.asarray(rec, dtype=np.float64) - x
        captured.append((tuple(res), vl.planar_average(d, axis), float(np.mean(d))))
        return res

    eng.certify = wrapped
    try:
        _, rows, fails, secs = eng.material((meta, str(repo), str(frozen), str(cache)))
    finally:
        eng.certify = orig
    out, j = {}, 0
    for r in rows:                      # surviving rows are an ordered subsequence of the certify calls
        key = (r["hartree_hist"], r["hartree_safe"], r["density_Linf"], r["density_RMSE"])
        while j < len(captured) and captured[j][0] != key:
            j += 1
        if j == len(captured):
            raise RuntimeError("route S: a returned row has no matching certify call")
        out[(r["arm"], float(r["tau"]), r["param"])] = {"bytes": int(r["bytes"]), "eh": r["hartree_hist"],
                                                        "es": r["hartree_safe"], "profile": captured[j][1],
                                                        "delta_electrons": captured[j][2]}
        j += 1
    return out, fails, secs


def material(meta: dict, repo: Path, frozen: Path, cache: Path, rows_csv: Path):
    sys.path.insert(0, str(frozen / "validation"))
    sys.path.insert(0, str(repo / "validation" / "qsq_prospective"))
    import development_compatibility_smoke as dev
    import external_end_to_end as core
    v02 = eng.v02
    mid = meta["material_id"]
    t0 = time.time()
    slab = {"material_id": mid, "formula": meta["formula"], "manifest_sha256": meta["sha256"]}
    rows, fails = [], []
    try:
        blob = fetch(dev, meta, cache)
        slab["source_sha256_verified"] = bool(hashlib.sha256(blob).hexdigest() == meta["sha256"]
                                              and len(blob) == int(meta["source_bytes"]))
        if not slab["source_sha256_verified"]:
            raise RuntimeError("source bytes do not match the manifest SHA-256 / byte count")
        streams = certified_streams(rows_csv, mid)
        slab["n_recorded_streams"] = len(streams)
        with tempfile.TemporaryDirectory(prefix="p3bvac_") as td:
            work = Path(td)
            grid, loader = dev.build_grid(meta, blob, work)
            x = np.ascontiguousarray(np.asarray(grid.total, dtype=np.float64))
            lat = np.asarray(grid.structure.lattice.matrix, float)
            ptp = float(np.ptp(x))
            rh, rs = v02.reference_hartree_rms(x, lat)
            vol = vl.cell_volume(lat)
            vh = vl.hartree_potential_ev(x, lat)
            own_rms = float(np.sqrt(np.mean(vh * vh)))
            del vh
            win = vl.vacuum_window(x, lat)
            axis = win["normal_axis"]
            slab.update({"loader": loader, "shape": "x".join(str(n) for n in x.shape), "npoints": x.size,
                         "cell_volume_A3": vol, "n_electrons_mean_field": float(np.mean(x)),
                         "vref_rms_eV_hist": vl.K_E / vol * rh, "vref_rms_eV_safe": vl.K_E / vol * rs,
                         "vref_rms_eV_own3d": own_rms, "vref_own3d_rel_diff": own_rms / (vl.K_E / vol * rh) - 1.0})
            slab.update({k: v for k, v in win.items() if k != "window_index"})
            ts = time.time()
            try:
                R = route_r(x, lat, ptp, rh, rs, streams, axis, work, core)
            except Exception:
                R = {}
                fails.append({"material_id": mid, "arm": "route_R", "tau": "", "error": traceback.format_exc()[-800:]})
            slab["route_r_seconds"] = time.time() - ts
            del x, grid
        try:
            S, s_fails, s_secs = route_s(meta, repo, frozen, cache, axis)
            slab["route_s_seconds"] = s_secs
            slab["route_s_failures"] = len(s_fails)
            for f in s_fails:
                fails.append({"material_id": mid, "arm": f"route_S:{f.get('arm', '')}", "tau": f.get("tau", ""),
                              "error": str(f.get("error", ""))[-800:]})
        except Exception:
            S = {}
            fails.append({"material_id": mid, "arm": "route_S", "tau": "", "error": traceback.format_exc()[-800:]})
        for arm in ARMS:
            for tau in sorted(eng.TAUS, reverse=True):
                row = {"material_id": mid, "formula": meta["formula"], "arm": arm, "tau": tau}
                rec_row = streams.get((arm, tau))
                if rec_row is None:
                    row.update({"status": "no_certified_stream_recorded", "reproduced": False, "evaluated": False})
                    rows.append(row)
                    continue
                row.update({"param": rec_row["param"], "codec": parse_param(rec_row["param"]).get("codec", ""),
                            "recorded_bytes": int(rec_row["bytes"]), "recorded_hartree_hist": float(rec_row["hartree_hist"]),
                            "recorded_hartree_safe": float(rec_row["hartree_safe"])})
                cands = []          # (priority, route, dphi, dmax, delta_electrons, exact)
                for pr, (name, res) in enumerate((("R", R.get((arm, tau))), ("S", S.get((arm, tau, rec_row["param"]))))):
                    if res is None:
                        row[f"{name}_status"] = "missing"
                        continue
                    if "error" in res:
                        row[f"{name}_status"] = "error"
                        row[f"{name}_error"] = res["error"]
                        continue
                    ok, exact = check(res["bytes"], res["eh"], res["es"], rec_row, tau)
                    row.update({f"{name}_status": "reproduced" if ok else "not_reproduced", f"{name}_bytes": res["bytes"],
                                f"{name}_hartree_hist": res["eh"], f"{name}_hartree_safe": res["es"],
                                f"{name}_exact": exact, f"{name}_reproduced": ok})
                    if ok:
                        dphi, dmax = vl.vacuum_shift_from_profile(res["profile"], lat, win)
                        row[f"{name}_dphi_meV"] = dphi
                        cands.append(((0 if exact else 2) + pr, name, dphi, dmax, res["delta_electrons"], exact))
                if not cands:
                    row.update({"status": "not_reproduced", "reproduced": False, "evaluated": False})
                else:
                    _, name, dphi, dmax, dn, exact = min(cands)    # exact before tolerance; R before S
                    row.update({"route_used": name, "reproduced": True, "exact": exact, "dphi_meV": dphi,
                                "abs_dphi_meV": abs(dphi), "max_abs_dV_window_meV": dmax, "delta_electrons": dn,
                                "evaluated": bool(win["qualifies"]),
                                "status": "ok" if win["qualifies"] else "no_qualifying_vacuum"})
                row["tau_times_vref_meV"] = 1e3 * tau * slab["vref_rms_eV_hist"]
                rows.append(row)
    except Exception:
        fails.append({"material_id": mid, "arm": "material", "tau": "", "error": traceback.format_exc()[-800:]})
        slab["status"] = "material_failure"
    else:
        slab["status"] = "ok"
    slab["seconds"] = time.time() - t0
    return slab, rows, fails


def write_csv(path: Path, data: list) -> None:
    if not data:
        return
    fields = list(dict.fromkeys(k for r in data for k in r))
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(data)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--frozen-root", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--rows", type=Path, required=True, help="recorded part_a_rows.csv of the P3b law run")
    p.add_argument("--cache-dir", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--only", default="")
    a = p.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=True)
    a.cache_dir.mkdir(parents=True, exist_ok=True)
    man = list(csv.DictReader(open(a.manifest, encoding="utf-8")))
    if a.only:
        man = [m for m in man if m["material_id"] in a.only.split(",")]
    for meta in man:
        slab, rows, fails = material(meta, a.repo_root.resolve(), a.frozen_root.resolve(), a.cache_dir.resolve(),
                                     a.rows.resolve())
        mid = meta["material_id"]
        write_csv(a.output_dir / f"slab_{mid}.csv", [slab])
        write_csv(a.output_dir / f"dphi_{mid}.csv", rows)
        write_csv(a.output_dir / f"failures_{mid}.csv", fails)
        n_r = sum(1 for r in rows if r.get("route_used") == "R")
        n_s = sum(1 for r in rows if r.get("route_used") == "S")
        print(f"VAC_DONE {mid} status={slab['status']} vacuum={slab.get('qualifies')} axis={slab.get('normal_axis')} "
              f"run_A={slab.get('run_A', float('nan')):.2f} streams={len(rows)} via_R={n_r} via_S={n_s} "
              f"failures={len(fails)} seconds={slab['seconds']:.0f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
