#!/usr/bin/env python3
"""Draw the wide NOMAD slab cohort under PROTOCOL.md section 2 (metadata and declared input checks only).

No compression, codec, Hartree, Bader or other QoI outcome is computed on any candidate.

Phases (each writes its tables to --out-dir/selection, or to --out-dir for the manifest):
  meta  frame + resolved re-listed rows -> CHGCAR header grid of every row (partial read) -> window -> id exclusion ->
        formula exclusion -> AECCAR0/AECCAR2 in the CHGCAR directory (rawdir listing) with header grids on the CHGCAR
        grid (partial reads).                                    -> selection/candidates.csv, selection/funnel_meta.json
  qc    for every row that reached "AECCAR present": the P3b CHGCAR checks and the AECCAR input QC, on the full files.
                                                                 -> selection/qc.csv (resumable cache qc_cache.jsonl)
  draw  one qualified row per reduced formula in hash order, at most 6 per upload, N = min(32, qualified).
                                                                 -> manifest.csv, aeccar_sources.csv,
                                                                    selection/draw.csv, selection/selection_log.json
Usage: select_wide.py --phase {meta,qc,draw} --repo-root <checkout>
"""
from __future__ import annotations

import argparse
import bz2
import hashlib
import importlib.util
import json
import lzma
import posixpath
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

SALT = "QOAC-HB-SLAB-NOMAD-WIDE-20261007|"
API = "https://nomad-lab.eu/prod/v1/api/v1"
N_TARGET = 32
UPLOAD_CAP = 6
NPOINTS_MIN, NPOINTS_MAX = 150_000, 3_870_720
AECCAR_RE = re.compile(r"^AECCAR([02])(\.(bz2|gz|xz))?$")
NO_E_RE = re.compile(rb"\d[+-]\d{2,3}(?=\s|\Z)")      # Fortran E-format with the E dropped: 0.65466110724+193
STARS_RE = re.compile(rb"\*{2,}")
HERE = Path(__file__).resolve().parent
COHORT = HERE.parent
MAN_COLS = ["material_id", "task_id", "corpus", "system_type", "source", "formula", "ngrid", "sha256", "url",
            "source_bytes", "npoints", "natoms", "selection_stratum", "selection_hash"]
SRC_COLS = ["material_id", "entry_id", "chgcar_ngrid", "aeccar_available",
            "aeccar0_path", "aeccar0_bytes", "aeccar0_sha256", "aeccar0_ngrid",
            "aeccar2_path", "aeccar2_bytes", "aeccar2_sha256", "aeccar2_ngrid"]


def h(s: str) -> str:
    return hashlib.sha256((SALT + s).encode()).hexdigest()


def fetch(url: str, tries: int = 5) -> bytes:
    err = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "QoI-HB-slab-NOMAD-wide/1.0"})
            with urllib.request.urlopen(req, timeout=900) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            err = e
            if e.code in (400, 401, 403, 404):
                break
            time.sleep(5 * (k + 1))
        except Exception as e:  # noqa: BLE001
            err = e
            time.sleep(5 * (k + 1))
    raise RuntimeError(f"download failed: {err}")


def raw_url(entry: str, name: str) -> str:
    return f"{API}/entries/{entry}/raw/{urllib.parse.quote(name)}"


def split_header(raw: bytes):
    """(grid 'nx x ny x nz', npoints, natoms, byte offset of the first data line) of a VASP volumetric file."""
    lines = raw.split(b"\n")
    tok5 = lines[5].split()
    if tok5 and all(re.fullmatch(rb"\d+", t) for t in tok5):
        counts, hdr = [int(t) for t in tok5], 6
    else:
        counts, hdr = [int(t) for t in lines[6].split()], 7
    if lines[hdr].strip()[:1] in (b"S", b"s"):     # Selective dynamics
        hdr += 1
    i = hdr + 1 + sum(counts)
    while not lines[i].strip():
        i += 1
    if i >= len(lines) - 1:
        raise ValueError("truncated before the end of the grid line")
    dims = [int(x) for x in lines[i].split()[:3]]
    if len(dims) != 3:
        raise ValueError("no grid line")
    off = sum(len(x) + 1 for x in lines[:i + 1])
    return "x".join(map(str, dims)), int(np.prod(dims)), sum(counts), off


def head(entry: str, name: str) -> bytes:
    """Leading decompressed bytes of a raw file (partial read; bz2 needs a whole 900 kB block)."""
    low = name.lower()
    for n in ((2_000_000, 8_000_000) if low.endswith(".bz2") else (65_536, 1_048_576, 8_000_000)):
        q = f"?offset=0&length={n}" + ("" if low.endswith(".bz2") else "&decompress=true")
        b = fetch(raw_url(entry, name) + q)
        if b[:2] == b"\x1f\x8b":
            b = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(b)
        elif b[:3] == b"BZh":
            b = bz2.BZ2Decompressor().decompress(b)
        elif b[:6] == b"\xfd7zXZ\x00":
            b = lzma.LZMADecompressor().decompress(b)
        try:
            split_header(b)
            return b
        except (IndexError, ValueError):
            continue
    raise RuntimeError("header not found in the leading bytes")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def excluded_id(entry: str, ids: set[str], prefixes: list[str]) -> bool:
    return entry in ids or any(entry.startswith(p) for p in prefixes)


# ------------------------------------------------------------------------------------------------- phase meta
def phase_meta(repo: Path, out: Path) -> None:
    F = repo / "analysis" / "fresh_population_20261006"
    sel = out / "selection"
    frame = pd.read_csv(F / "nomad_frame_surface_vasp.csv.gz").assign(frame_origin="frame_20261006")
    rel = pd.read_csv(sel / "relisted_entries.csv", dtype={"chgcar_bytes": "Int64"})
    rel_ok = rel[rel.resolved == 1].drop(columns=["entry_create_time", "resolved"]).assign(frame_origin="relisted")
    wide = pd.concat([frame, rel_ok], ignore_index=True)
    assert wide.entry_id.is_unique
    ids = set(pd.read_csv(sel / "exclusion_nomad_ids.csv", dtype=str).id)
    prefixes = sorted({i[len("nomad-"):] for i in ids if i.startswith("nomad-")})
    forms = set(pd.read_csv(sel / "exclusion_slab_formulas.csv", dtype=str).reduced_formula)

    def hdr(r):
        try:
            g, n, nat, _ = split_header(head(r["entry_id"], posixpath.basename(r["chgcar_path"])))
            return {"header_grid": g, "npoints": n, "natoms_header": nat, "header_error": ""}
        except Exception as e:  # noqa: BLE001
            return {"header_grid": "", "npoints": np.nan, "natoms_header": np.nan,
                    "header_error": f"{type(e).__name__}:{str(e)[:160]}"}

    with ThreadPoolExecutor(3) as ex:
        heads = list(ex.map(hdr, wide.to_dict("records")))
    wide = pd.concat([wide, pd.DataFrame(heads)], axis=1)
    wide["in_window"] = wide.npoints.between(NPOINTS_MIN, NPOINTS_MAX)
    wide["id_excluded"] = [excluded_id(e, ids, prefixes) for e in wide.entry_id]
    wide["formula_excluded"] = wide.reduced_formula.isin(forms)
    pool = wide[wide.in_window & ~wide.id_excluded & ~wide.formula_excluded]

    def aec(r):
        rec = {"entry_id": r["entry_id"]}
        try:
            files = json.loads(fetch(f"{API}/entries/{urllib.parse.quote(r['entry_id'])}/rawdir"))["data"]["files"]
            d0 = posixpath.dirname(r["chgcar_path"])
            found = {"0": [], "2": []}
            for x in files:
                m = AECCAR_RE.match(posixpath.basename(x["path"]))
                if m and posixpath.dirname(x["path"]) == d0:
                    found[m.group(1)].append((x["path"], x.get("size")))
            for k in "02":
                if found[k]:
                    p, s = sorted(found[k])[0]
                    rec[f"aeccar{k}_path"], rec[f"aeccar{k}_bytes_listed"] = p, s
                    try:
                        rec[f"aeccar{k}_header_grid"] = split_header(head(r["entry_id"], posixpath.basename(p)))[0]
                    except Exception as e:  # noqa: BLE001
                        rec[f"aeccar{k}_header_error"] = f"{type(e).__name__}:{str(e)[:160]}"
        except Exception as e:  # noqa: BLE001
            rec["rawdir_error"] = f"{type(e).__name__}:{str(e)[:160]}"
        return rec

    with ThreadPoolExecutor(3) as ex:
        aecs = list(ex.map(aec, pool.to_dict("records")))
    A = pd.DataFrame(aecs)
    for c in ("aeccar0_path", "aeccar2_path", "aeccar0_header_grid", "aeccar2_header_grid", "rawdir_error",
              "aeccar0_header_error", "aeccar2_header_error", "aeccar0_bytes_listed", "aeccar2_bytes_listed"):
        if c not in A:
            A[c] = np.nan
    wide = wide.merge(A, on="entry_id", how="left")
    both = wide.aeccar0_path.notna() & wide.aeccar2_path.notna()
    on_grid = (wide.aeccar0_header_grid == wide.header_grid) & (wide.aeccar2_header_grid == wide.header_grid)
    wide["aeccar_both_present"] = both
    wide["aeccar_present_on_grid"] = both & on_grid

    def stage(r):
        if r.header_error:
            return "header_unreadable"
        if not r.in_window:
            return "below_window" if r.npoints < NPOINTS_MIN else "above_window"
        if r.id_excluded:
            return "id_excluded"
        if r.formula_excluded:
            return "formula_excluded"
        if isinstance(r.rawdir_error, str):
            return "rawdir_error"
        if not r.aeccar_both_present:
            return "no_aeccar" if pd.isna(r.aeccar0_path) and pd.isna(r.aeccar2_path) else \
                ("no_aeccar0" if pd.isna(r.aeccar0_path) else "no_aeccar2")
        if not r.aeccar_present_on_grid:
            return "aeccar_header_not_on_chgcar_grid"
        return "aeccar_present"

    wide["meta_stage"] = [stage(r) for r in wide.itertuples()]
    sel.mkdir(parents=True, exist_ok=True)
    wide.to_csv(sel / "candidates.csv", index=False, lineterminator="\n")
    w = wide
    funnel = {
        "frame_20261006_rows": int((w.frame_origin == "frame_20261006").sum()),
        "relisted_resolved_rows_added": int((w.frame_origin == "relisted").sum()),
        "frame_wide_rows": int(len(w)),
        "header_unreadable": int((w.header_error != "").sum()),
        "window_rows": int(w.in_window.sum()),
        "window_below": int((w.npoints < NPOINTS_MIN).sum()), "window_above": int((w.npoints > NPOINTS_MAX).sum()),
        "after_id_exclusion": int((w.in_window & ~w.id_excluded).sum()),
        "after_formula_exclusion": int(len(pool)),
        "after_formula_exclusion_formulas": int(pool.reduced_formula.nunique()),
        "after_formula_exclusion_uploads": int(pool.upload_id.nunique()),
        "aeccar_both_present": int(w.aeccar_both_present.sum()),
        "aeccar_present_on_grid": int(w.aeccar_present_on_grid.sum()),
        "aeccar_present_on_grid_formulas": int(w[w.aeccar_present_on_grid].reduced_formula.nunique()),
        "aeccar_present_on_grid_uploads": int(w[w.aeccar_present_on_grid].upload_id.nunique()),
        "meta_stage_counts": w.meta_stage.value_counts().to_dict(),
        "window": [NPOINTS_MIN, NPOINTS_MAX], "salt": SALT,
        "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    (sel / "funnel_meta.json").write_text(json.dumps(funnel, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(funnel, indent=2))


# --------------------------------------------------------------------------------------------------- phase qc
def qc_row(r: dict, forms: set[str], dev, slab) -> dict:
    e = r["entry_id"]
    rec = {"entry_id": e}
    try:
        name = posixpath.basename(r["chgcar_path"])
        url = raw_url(e, name)
        blob = fetch(url)
        rec |= {"chgcar_url": url, "chgcar_bytes": len(blob), "chgcar_sha256": hashlib.sha256(blob).hexdigest()}
        with tempfile.TemporaryDirectory(prefix="hbwide_qc_", ignore_cleanup_errors=True) as td:
            grid, _ = dev.build_grid({"source": "NOMAD surfaces/adsorbates", "url": url}, blob, Path(td))
            x = np.asarray(grid.total, dtype=np.float64)
            st = grid.structure
            rec |= {"chgcar_ngrid": "x".join(map(str, x.shape)), "npoints": int(x.size), "natoms": len(st),
                    "parsed_formula": st.composition.reduced_formula,
                    "chgcar_finite_positive": int(bool(np.all(np.isfinite(x)) and float(x.sum()) > 0))}
            del grid, x
        del blob
    except Exception as exc:  # noqa: BLE001
        rec["chgcar_error"] = f"{type(exc).__name__}:{str(exc)[:200]}"
        rec["qc_reason"] = "chgcar_parse_error"
        return rec
    reason = ""
    if not rec["chgcar_finite_positive"]:
        reason = "invalid_density"
    elif rec["chgcar_ngrid"] != r["header_grid"]:
        reason = "chgcar_grid_differs_from_header"
    elif not (NPOINTS_MIN <= rec["npoints"] <= NPOINTS_MAX):
        reason = "npoints_out_of_window"
    elif rec["parsed_formula"] in forms:
        reason = "excluded_parsed_formula"
    for k in "02":
        try:
            name = posixpath.basename(r[f"aeccar{k}_path"])
            ab = fetch(raw_url(e, name))
            rec |= {f"aeccar{k}_name": name, f"aeccar{k}_bytes": len(ab), f"aeccar{k}_sha256": hashlib.sha256(ab).hexdigest()}
            raw = dev.decompress_nomad(name, ab)
            del ab
            g, _, _, off = split_header(raw)
            data = memoryview(raw)[off:]
            rec |= {f"aeccar{k}_ngrid": g, f"aeccar{k}_no_E_tokens": len(NO_E_RE.findall(data)),
                    f"aeccar{k}_star_tokens": len(STARS_RE.findall(data))}
            del data
            try:
                tot = slab.parse_vasp_total(raw)
                rec |= {f"aeccar{k}_parsed_shape": "x".join(map(str, tot.shape)),
                        f"aeccar{k}_nonfinite": int(np.count_nonzero(~np.isfinite(tot)))}
                del tot
            except Exception as exc:  # noqa: BLE001
                rec[f"aeccar{k}_parse_error"] = f"{type(exc).__name__}:{str(exc)[:160]}"
            del raw
        except Exception as exc:  # noqa: BLE001
            rec[f"aeccar{k}_error"] = f"{type(exc).__name__}:{str(exc)[:160]}"
        if reason:
            continue
        if f"aeccar{k}_error" in rec:
            reason = f"aeccar{k}_read_error"
        elif rec[f"aeccar{k}_ngrid"] != rec["chgcar_ngrid"]:
            reason = f"aeccar{k}_grid_mismatch"
        elif rec[f"aeccar{k}_no_E_tokens"]:
            reason = f"aeccar{k}_no_E_tokens"
        elif f"aeccar{k}_parse_error" in rec:
            reason = f"aeccar{k}_parse_error"
        elif rec[f"aeccar{k}_parsed_shape"] != rec["chgcar_ngrid"]:
            reason = f"aeccar{k}_shape_mismatch"
        elif rec[f"aeccar{k}_nonfinite"]:
            reason = f"aeccar{k}_nonfinite"
    rec["qc_reason"] = reason
    rec["qc_pass"] = int(reason == "")
    return rec


def phase_qc(repo: Path, out: Path) -> None:
    sel = out / "selection"
    sys.path.insert(0, str(repo / "validation" / "qsq_prospective"))
    import development_compatibility_smoke as dev
    slab = load_module("run_joint_slab", repo / "analysis" / "qoac_hb_slab_20261007" / "run_joint_slab.py")
    forms = set(pd.read_csv(sel / "exclusion_slab_formulas.csv", dtype=str).reduced_formula)
    cand = pd.read_csv(sel / "candidates.csv", dtype=str)
    todo = cand[cand.meta_stage == "aeccar_present"].to_dict("records")
    cache_p = sel / "qc_cache.jsonl"
    done = {}
    if cache_p.exists():
        for line in cache_p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                d = json.loads(line); done[d["entry_id"]] = d
    with open(cache_p, "a", encoding="utf-8") as fh:
        for i, r in enumerate(todo):
            if r["entry_id"] in done:
                continue
            t0 = time.time()
            rec = qc_row(r, forms, dev, slab)
            rec["seconds"] = round(time.time() - t0, 1)
            done[r["entry_id"]] = rec
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            print(f"QC {i + 1}/{len(todo)} {r['entry_id']} {r['reduced_formula']} pass={rec.get('qc_pass', 0)} "
                  f"{rec.get('qc_reason', '')} {rec['seconds']}s", flush=True)
    q = pd.DataFrame([done[r["entry_id"]] for r in todo])
    if "qc_pass" not in q:
        q["qc_pass"] = 0
    q["qc_pass"] = q["qc_pass"].fillna(0).astype(int)
    q.to_csv(sel / "qc.csv", index=False, lineterminator="\n")
    print(json.dumps({"qc_rows": len(q), "qc_pass": int(q.qc_pass.sum()),
                      "qc_reasons": q.qc_reason.fillna("").value_counts().to_dict()}, indent=2))


# ------------------------------------------------------------------------------------------------- phase draw
def phase_draw(repo: Path, out: Path) -> None:
    sel = out / "selection"
    cand = pd.read_csv(sel / "candidates.csv", dtype=str)
    q = pd.read_csv(sel / "qc.csv", dtype=str)
    q["qc_pass"] = q.qc_pass.astype(int)
    c = cand.merge(q, on="entry_id", how="inner", suffixes=("", "_qc"))
    qual = c[c.qc_pass == 1]
    formulas = sorted(qual.reduced_formula.unique(), key=h)
    draw, man, src, per_upload = [], [], [], {}
    for f in formulas:
        if len(man) >= N_TARGET:
            break
        for r in sorted(qual[qual.reduced_formula == f].to_dict("records"), key=lambda r: h(r["entry_id"])):
            rec = {"reduced_formula": f, "entry_id": r["entry_id"], "upload_id": r["upload_id"],
                   "formula_hash": h(f), "selection_hash": h(r["entry_id"])}
            if per_upload.get(r["upload_id"], 0) >= UPLOAD_CAP:
                draw.append(rec | {"decision": "reject", "reason": "upload_cap"}); continue
            e = r["entry_id"]
            mid = "nomad-" + e[:12]
            man.append({"material_id": mid, "task_id": e, "corpus": "fresh_hb_slab_nomad_wide", "system_type": "slab",
                        "source": "NOMAD surfaces/adsorbates", "formula": r["parsed_formula"],
                        "ngrid": r["chgcar_ngrid"], "sha256": r["chgcar_sha256"], "url": r["chgcar_url"],
                        "source_bytes": r["chgcar_bytes_qc"], "npoints": r["npoints_qc"], "natoms": r["natoms"],
                        "selection_stratum": f"formula:{f}", "selection_hash": h(e)})
            src.append({"material_id": mid, "entry_id": e, "chgcar_ngrid": r["chgcar_ngrid"], "aeccar_available": "1",
                        **{f"aeccar{k}_{x}": r[f"aeccar{k}_{y}"] for k in "02"
                           for x, y in (("path", "path"), ("bytes", "bytes"), ("sha256", "sha256"), ("ngrid", "ngrid"))}})
            per_upload[r["upload_id"]] = per_upload.get(r["upload_id"], 0) + 1
            draw.append(rec | {"decision": "accept", "reason": ""})
            break
    pd.DataFrame(draw).to_csv(sel / "draw.csv", index=False, lineterminator="\n")
    pd.DataFrame(man, columns=MAN_COLS).to_csv(out / "manifest.csv", index=False, lineterminator="\n")
    pd.DataFrame(src, columns=SRC_COLS).to_csv(out / "aeccar_sources.csv", index=False, lineterminator="\n")
    assert pd.DataFrame(man).material_id.is_unique if man else True
    funnel = json.loads((sel / "funnel_meta.json").read_text(encoding="utf-8"))
    from importlib.metadata import version
    lf = lambda p: hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()  # noqa: E731
    log = {**{k: v for k, v in funnel.items() if k != "finished_utc"},
           "qc_evaluated": int(len(q)), "qc_passed": int(q.qc_pass.sum()),
           "qc_passed_formulas": int(qual.reduced_formula.nunique()), "qc_passed_uploads": int(qual.upload_id.nunique()),
           "qc_reasons": q.qc_reason.fillna("").replace("", "pass").value_counts().to_dict(),
           "draw_formulas_visited": len({d["reduced_formula"] for d in draw}),
           "draw_rejected_upload_cap": sum(d["reason"] == "upload_cap" for d in draw),
           "N": len(man), "accepted_per_upload": per_upload,
           "finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "sha256": {p.name: lf(p) for p in (out / "manifest.csv", out / "aeccar_sources.csv", sel / "draw.csv",
                                              sel / "qc.csv", sel / "candidates.csv", Path(__file__).resolve(),
                                              sel / "exclusion_nomad_ids.csv", sel / "exclusion_slab_formulas.csv",
                                              sel / "relisted_entries.csv")},
           "environment": {"python": sys.version.split()[0], "numpy": np.__version__, "pandas": pd.__version__,
                           "baderkit": version("baderkit"), "pymatgen": version("pymatgen")}}
    (sel / "selection_log.json").write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: log[k] for k in ("qc_evaluated", "qc_passed", "qc_passed_formulas", "N",
                                          "accepted_per_upload")}, indent=2))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=("meta", "qc", "draw"), required=True)
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, default=COHORT)
    a = ap.parse_args(argv)
    {"meta": phase_meta, "qc": phase_qc, "draw": phase_draw}[a.phase](a.repo_root.resolve(), a.out_dir.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
