#!/usr/bin/env python3
"""Draw the HB slab AECCAR cohort under PROTOCOL.md section 2 (metadata and declared input QC only).

No compression, codec, Hartree, Bader or other QoI outcome is computed on any candidate. Per candidate row this
reads: the NOMAD rawdir listing of the entry; the CHGCAR (size, SHA-256, grid, atom count, parsed reduced formula,
finiteness and sum of the density: the P3b checks); AECCAR0 and AECCAR2 (size, SHA-256, header grid, and the input-QC
parse: shape and finiteness). Downloaded files are discarded after these values are extracted.

Usage:
  select_cohort.py --repo-root <checkout>                       draw; writes manifest.csv, aeccar_sources.csv,
                                                                 selection/attempts.csv, selection/selection_log.json
  select_cohort.py --repo-root <checkout> --pool-only            print the pool counts (frame metadata only)
  select_cohort.py --repo-root <checkout> --check-entries ID ...  run the per-row checks on named frame entries (used
                                                                 for the pre-run check on already-used entries)
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import posixpath
import re
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

TAG = "QOAC-HB-SLAB-AECCAR-20261007|"
API = "https://nomad-lab.eu/prod/v1/api/v1"
N_TARGET = 32
UPLOAD_CAP = 6
BYTES_MIN, BYTES_MAX = 1e6, 80e6
NPOINTS_MIN, NPOINTS_MAX = 1.5e5, 6.0e6
AECCAR_RE = re.compile(r"^AECCAR([02])(\.(bz2|gz|xz))?$")
HERE = Path(__file__).resolve().parent
COHORT = HERE.parent
MAN_COLS = ["material_id", "task_id", "corpus", "system_type", "source", "formula", "ngrid", "sha256", "url",
            "source_bytes", "npoints", "natoms", "selection_stratum", "selection_hash"]
SRC_COLS = ["material_id", "entry_id", "chgcar_ngrid", "aeccar_available",
            "aeccar0_path", "aeccar0_bytes", "aeccar0_sha256", "aeccar0_ngrid",
            "aeccar2_path", "aeccar2_bytes", "aeccar2_sha256", "aeccar2_ngrid"]


def h(s: str) -> str:
    return hashlib.sha256((TAG + s).encode()).hexdigest()


def fetch(url: str) -> bytes:
    err = None
    for k in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "QoI-HB-slab-AECCAR-cohort/1.0"})
            with urllib.request.urlopen(req, timeout=900) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(5 * (k + 1))
    raise RuntimeError(f"download failed: {err}")


def header_grid(raw: bytes) -> str:
    """Grid line of a VASP volumetric file (after the POSCAR block), as 'nx x ny x nz'."""
    lines = raw[:1 << 20].split(b"\n")
    tok5 = lines[5].split()
    if all(re.fullmatch(rb"\d+", t) for t in tok5):
        counts, hdr = [int(t) for t in tok5], 6
    else:
        counts, hdr = [int(t) for t in lines[6].split()], 7
    if lines[hdr].strip()[:1] in (b"S", b"s"):     # Selective dynamics
        hdr += 1
    i = hdr + 1 + sum(counts)
    while not lines[i].strip():
        i += 1
    return "x".join(str(int(x)) for x in lines[i].split()[:3])


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_pool(frame: pd.DataFrame, ex_ids: set[str], ex_f: set[str]) -> tuple[pd.DataFrame, dict]:
    fr = frame[(frame.chgcar_bytes >= BYTES_MIN) & (frame.chgcar_bytes <= BYTES_MAX)]
    n_window = len(fr)
    fr = fr[~fr.entry_id.isin(ex_ids) & ~("nomad-" + fr.entry_id.str[:12]).isin(ex_ids)]
    n_ids = len(fr)
    fr = fr[~fr.reduced_formula.isin(ex_f)]
    counts = {"frame_rows": int(len(frame)), "window_rows": int(n_window), "after_id_exclusion": int(n_ids),
              "pool_rows": int(len(fr)), "pool_formulas": int(fr.reduced_formula.nunique()),
              "pool_uploads": int(fr.upload_id.nunique())}
    return fr, counts


def check_row(r: dict, ex_f: set[str], dev, slab) -> tuple[dict, dict | None, dict | None]:
    """All per-row checks of PROTOCOL.md section 2 except the upload cap. Returns (attempt record, manifest row, source
    row); the last two are None when the row is rejected (reason in the record)."""
    e = r["entry_id"]
    rec = {"reduced_formula": r["reduced_formula"], "entry_id": e, "upload_id": r["upload_id"],
           "chgcar_bytes_listed": int(r["chgcar_bytes"]), "selection_hash": h(e)}

    def reject(reason):
        return rec | {"decision": "reject", "reason": reason}, None, None

    try:
        # (a) metadata: AECCAR0 and AECCAR2 next to the CHGCAR
        listing = json.loads(fetch(f"{API}/entries/{urllib.parse.quote(e)}/rawdir"))["data"]["files"]
        chg_dir = posixpath.dirname(r["chgcar_path"])
        found: dict[str, list[tuple[str, int]]] = {"0": [], "2": []}
        for x in listing:
            m = AECCAR_RE.match(posixpath.basename(x["path"]))
            if m and posixpath.dirname(x["path"]) == chg_dir:
                found[m.group(1)].append((x["path"], int(x.get("size") or 0)))
        missing = [k for k in "02" if not found[k]]
        if missing:
            return reject("no_aeccar" if len(missing) == 2 else f"no_aeccar{missing[0]}")
        aec = {k: sorted(found[k])[0] for k in "02"}

        # (b) the P3b CHGCAR checks
        url = f"{API}/entries/{e}/raw/{posixpath.basename(r['chgcar_path'])}"
        blob = fetch(url)
        sha, nbytes = hashlib.sha256(blob).hexdigest(), len(blob)
        with tempfile.TemporaryDirectory(prefix="hbslab_sel_", ignore_cleanup_errors=True) as td:
            grid, _ = dev.build_grid({"source": "NOMAD surfaces/adsorbates", "url": url}, blob, Path(td))
            x = np.asarray(grid.total, dtype=np.float64)
            st = grid.structure
            shape, n = x.shape, int(x.size)
            ok = bool(np.all(np.isfinite(x)) and float(x.sum()) > 0)
            form, nat = st.composition.reduced_formula, len(st)
            del grid, x
        del blob
        ngrid = "x".join(map(str, shape))
        rec |= {"chgcar_sha256": sha, "chgcar_ngrid": ngrid, "npoints": n, "natoms": nat, "parsed_formula": form}
        if not ok:
            return reject("invalid_density")
        if not (NPOINTS_MIN <= n <= NPOINTS_MAX):
            return reject("npoints_out_of_range")
        if form in ex_f:
            return reject("excluded_parsed_formula")

        # (c) AECCAR metadata: served bytes, SHA-256, header grid on the CHGCAR grid; (d) input QC: parse, shape, finite
        src = {"material_id": "nomad-" + e[:12], "entry_id": e, "chgcar_ngrid": ngrid, "aeccar_available": "1"}
        reason = ""
        for k in "02":
            path, listed = aec[k]
            name = posixpath.basename(path)
            ab = fetch(f"{API}/entries/{e}/raw/{name}")
            asha, served = hashlib.sha256(ab).hexdigest(), len(ab)
            raw = dev.decompress_nomad(name, ab)
            del ab
            ag = header_grid(raw)
            src |= {f"aeccar{k}_path": path, f"aeccar{k}_bytes": str(served), f"aeccar{k}_sha256": asha,
                    f"aeccar{k}_ngrid": ag}
            rec |= {f"aeccar{k}_name": name, f"aeccar{k}_bytes_listed": listed, f"aeccar{k}_bytes": served,
                    f"aeccar{k}_sha256": asha, f"aeccar{k}_ngrid": ag}
            if ag != ngrid:
                reason = reason or f"aeccar{k}_grid_mismatch"
                continue
            try:
                tot = slab.parse_vasp_total(raw)
            except Exception as exc:  # noqa: BLE001
                rec[f"aeccar{k}_qc"] = f"parse_error:{type(exc).__name__}:{str(exc)[:120]}"
                reason = reason or f"aeccar{k}_qc_parse_error"
                continue
            finally:
                del raw
            shp = "x".join(map(str, tot.shape))
            nonfin = int(np.count_nonzero(~np.isfinite(tot)))
            del tot
            rec |= {f"aeccar{k}_qc_shape": shp, f"aeccar{k}_qc_nonfinite": nonfin}
            if shp != ngrid:
                reason = reason or f"aeccar{k}_qc_shape_mismatch"
            elif nonfin:
                reason = reason or f"aeccar{k}_qc_nonfinite"
        if reason:
            return reject(reason)
    except Exception as exc:  # noqa: BLE001
        return reject(f"error:{type(exc).__name__}:{str(exc)[:200]}")
    man = {"material_id": "nomad-" + e[:12], "task_id": e, "corpus": "fresh_hb_slab_aeccar", "system_type": "slab",
           "source": "NOMAD surfaces/adsorbates", "formula": form, "ngrid": ngrid, "sha256": sha, "url": url,
           "source_bytes": nbytes, "npoints": n, "natoms": nat, "selection_stratum": f"formula:{r['reduced_formula']}",
           "selection_hash": h(e)}
    return rec | {"decision": "accept", "reason": ""}, man, src


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, default=COHORT)
    ap.add_argument("--pool-only", action="store_true")
    ap.add_argument("--check-entries", nargs="+", default=None)
    a = ap.parse_args(argv)
    repo = a.repo_root.resolve()
    out = a.out_dir.resolve()
    F = repo / "analysis" / "fresh_population_20261006"
    frame = pd.read_csv(F / "nomad_frame_surface_vasp.csv.gz")
    ex_ids = set(pd.read_csv(HERE / "exclusion_ids.csv", dtype=str).id)
    ex_f = set(pd.read_csv(HERE / "exclusion_formulas.csv", dtype=str).reduced_formula)
    pool, counts = build_pool(frame, ex_ids, ex_f)
    print(json.dumps(counts), flush=True)
    if a.pool_only:
        return 0

    sys.path.insert(0, str(repo / "validation" / "qsq_prospective"))
    import development_compatibility_smoke as dev
    slab = load_module("run_joint_slab", repo / "analysis" / "qoac_hb_slab_20261007" / "run_joint_slab.py")

    if a.check_entries:
        # code-path check on already-used entries: no formula exclusion, so every step is exercised
        rows = frame[frame.entry_id.isin(a.check_entries)].to_dict("records")
        res = [check_row(r, set(), dev, slab)[0] for r in rows]
        out.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(res).to_csv(out / "check_entries.csv", index=False, lineterminator="\n")
        for x in res:
            print(x["entry_id"], x["decision"], x["reason"], flush=True)
        return 0

    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    formulas = sorted(pool.reduced_formula.unique(), key=h)
    attempts, accepted, sources, per_upload = [], [], [], {}
    for f in formulas:
        if len(accepted) >= N_TARGET:
            break
        rows = sorted(pool[pool.reduced_formula == f].to_dict("records"), key=lambda r: h(r["entry_id"]))
        for r in rows:
            if per_upload.get(r["upload_id"], 0) >= UPLOAD_CAP:
                attempts.append({"reduced_formula": f, "entry_id": r["entry_id"], "upload_id": r["upload_id"],
                                 "chgcar_bytes_listed": int(r["chgcar_bytes"]), "selection_hash": h(r["entry_id"]),
                                 "decision": "reject", "reason": "upload_cap"})
                continue
            rec, man, src = check_row(r, ex_f, dev, slab)
            attempts.append(rec)
            print(f"{f} {r['entry_id']} {rec['decision']} {rec['reason']}", flush=True)
            if man is not None:
                accepted.append(man); sources.append(src)
                per_upload[r["upload_id"]] = per_upload.get(r["upload_id"], 0) + 1
                break

    sel = out / "selection"
    sel.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(attempts).to_csv(sel / "attempts.csv", index=False, lineterminator="\n")
    pd.DataFrame(accepted, columns=MAN_COLS).to_csv(out / "manifest.csv", index=False, lineterminator="\n")
    pd.DataFrame(sources, columns=SRC_COLS).to_csv(out / "aeccar_sources.csv", index=False, lineterminator="\n")
    from importlib.metadata import version
    rej = [x["reason"].split(":")[0] for x in attempts if x["decision"] == "reject"]
    log = {
        "rule": "PROTOCOL.md section 2", "salt": TAG, "started_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **counts,
        "formulas_visited": len({x["reduced_formula"] for x in attempts}), "attempts": len(attempts),
        "reject_reasons": {k: rej.count(k) for k in sorted(set(rej))},
        "N": len(accepted), "accepted_per_upload": per_upload,
        "sha256": {p.name: hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()   # LF, as committed
                   for p in (out / "manifest.csv", out / "aeccar_sources.csv", sel / "attempts.csv",
                             Path(__file__).resolve(), HERE / "exclusion_ids.csv", HERE / "exclusion_formulas.csv")},
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__, "pandas": pd.__version__,
                        "baderkit": version("baderkit"), "pymatgen": version("pymatgen")},
    }
    (sel / "selection_log.json").write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: log[k] for k in ("pool_rows", "pool_formulas", "attempts", "reject_reasons", "N")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
