"""Draw the P2, P1 and P3 fresh populations by the frozen SELECTION_RULE.md.

Metadata only: size, SHA-256, grid shape, natoms, reduced formula, lattice and
the finite/positive validity check of the total density. Every downloaded file
is deleted right after its metadata is extracted.

Every attempt is appended to attempts.csv; a rerun replays that log and resumes
where it stopped, so an interrupted run gives the same selection.

Usage: select_population.py <repo_root> <out_dir> <scratch_dir> [pools...]
"""
from __future__ import annotations

import csv
import gc
import gzip
import hashlib
import json
import math
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np

SALT = "QOAC-FRESH-20261006|"
MB = 10**6
NPTS_MIN, NPTS_MAX = 150_000, 6_000_000
S3 = "https://materialsproject-parsed.s3.amazonaws.com/"
NOMAD_RAW = "https://nomad-lab.eu/prod/v1/api/v1/entries/{eid}/raw/{base}"
K = {"P2": 60, "P1": 72, "P3": 72}
ENG_STEP = {"P2": 5, "P1": 6, "P3": 6}
ATTEMPT_FIELDS = [
    "pool", "stratum", "hash_rank", "id", "selection_hash", "listed_bytes", "decision",
    "reason", "material_id", "formula", "ngrid", "npoints", "natoms", "lattice_abc",
    "lattice_angles", "sha256", "source_bytes", "aeccar0_bytes", "aeccar2_bytes",
    "downloaded_bytes", "url",
]


class PermanentDownloadError(Exception):
    pass


def shash(ident: str) -> str:
    return hashlib.sha256((SALT + ident).encode()).hexdigest()


def strata(frame: list[tuple[int, str]], k: int) -> list[list[tuple[int, str]]]:
    frame = sorted(frame)
    n = len(frame)
    return [frame[(i * n) // k:((i + 1) * n) // k] for i in range(k)]


def download(url: str, dest: Path) -> tuple[bytes, str, int]:
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "QoI-fresh-population/1.0"})
            h = hashlib.sha256()
            n = 0
            with urllib.request.urlopen(req, timeout=600) as r, dest.open("wb") as f:
                while True:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    h.update(chunk)
                    f.write(chunk)
                    n += len(chunk)
            blob = dest.read_bytes()
            dest.unlink()
            return blob, h.hexdigest(), n
        except urllib.error.HTTPError as exc:
            dest.unlink(missing_ok=True)
            if 400 <= exc.code < 500 and exc.code != 429:
                raise PermanentDownloadError(f"HTTP {exc.code}") from exc
            err = exc
        except Exception as exc:  # noqa: BLE001
            dest.unlink(missing_ok=True)
            err = exc
        print(f"  retry {attempt} {url}: {err}", flush=True)
        time.sleep(15 * (attempt + 1))
    raise RuntimeError(f"transient download failure persisted, aborting run: {url}")


def load_exclusion(out: Path):
    ids, formulas = set(), set()
    with (out / "exclusion_ids.csv").open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ids.add(r["id"])
    with (out / "exclusion_formulas.csv").open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            formulas.add(r["reduced_formula"])
    return ids, formulas


def load_s3(out: Path, name: str) -> dict[str, int]:
    res = {}
    with gzip.open(out / f"s3_index_{name}.csv.gz", "rt", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["task_id"]:
                res[r["task_id"]] = int(r["size"])
    return res


def build_frames(out: Path):
    chg, ae0, ae2 = (load_s3(out, n) for n in ("chgcars", "aeccar0s", "aeccar2s"))
    p2 = [(s, t) for t, s in chg.items()
          if MB <= s <= 80 * MB and t in ae0 and t in ae2
          and ae0[t] <= 150 * MB and ae2[t] <= 150 * MB]
    p2_ids = {t for _, t in p2}
    p1 = [(s, t) for t, s in chg.items() if MB <= s <= 80 * MB and t not in p2_ids]
    nomad = {}
    nomad_path = out / "nomad_frame_surface_vasp.csv.gz"
    if nomad_path.exists():  # P1/P2 may run before the NOMAD frame is frozen
        with gzip.open(nomad_path, "rt", newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                nomad[r["entry_id"]] = r
    p3 = [(int(r["chgcar_bytes"]), e) for e, r in nomad.items()
          if MB <= int(r["chgcar_bytes"]) <= 80 * MB]
    counts = {
        "s3_chgcar_task_ids": len(chg), "s3_aeccar0_task_ids": len(ae0),
        "s3_aeccar2_task_ids": len(ae2),
        "s3_triple_task_ids": len(set(chg) & set(ae0) & set(ae2)),
        "frame_P2": len(p2), "frame_P1": len(p1),
        "nomad_entries_with_chgcar": len(nomad), "frame_P3": len(p3),
    }
    return {"P2": p2, "P1": p1, "P3": p3}, ae0, ae2, nomad, counts


def grid_meta(grid) -> dict:
    s = grid.structure
    lat = s.lattice
    return {
        "formula": s.composition.reduced_formula,
        "shape": tuple(int(x) for x in grid.shape),
        "natoms": len(s),
        "lattice_abc": "%.6f;%.6f;%.6f" % lat.abc,
        "lattice_angles": "%.4f;%.4f;%.4f" % lat.angles,
    }


def density_ok(arr) -> bool:
    a = np.asarray(arr)
    return bool(np.isfinite(a).all() and float(a.sum(dtype=np.float64)) > 0.0)


def main() -> int:
    repo, out, scratch = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    pools = sys.argv[4:] or ["P2", "P1", "P3"]
    sys.path.insert(0, str(repo / "validation" / "qsq_prospective"))
    from development_compatibility_smoke import build_grid, decode_mp_chgcar  # noqa: E402

    scratch.mkdir(parents=True, exist_ok=True)
    excl_ids, excl_formulas = load_exclusion(out)
    frames, ae0, ae2, nomad, counts = build_frames(out)
    (out / "frame_counts.json").write_text(json.dumps(counts, indent=2))
    print(json.dumps(counts), flush=True)

    excl_uploads = sorted({r["upload_id"] for e, r in nomad.items()
                           if e in excl_ids or "nomad-" + e[:12] in excl_ids})

    log_path = out / "attempts.csv"
    done: dict[tuple[str, str], dict] = {}
    if log_path.exists():
        with log_path.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                done[(r["pool"], r["id"])] = r
    new_log = not log_path.exists()
    logf = log_path.open("a", newline="", encoding="utf-8")
    logw = csv.DictWriter(logf, fieldnames=ATTEMPT_FIELDS)
    if new_log:
        logw.writeheader()

    accepted_formulas: set[str] = set()
    # Replay accepted formulas of pools processed earlier in the fixed order.
    order = ["P2", "P1", "P3"]
    for (pool, _), r in done.items():
        if r["decision"] == "accept":
            accepted_formulas.add(r["formula"])

    for pool in order:
        if pool not in pools:
            continue
        k = K[pool]
        for si, stratum in enumerate(strata(frames[pool], k)):
            label = f"{pool}_s{si + 1:02d}of{k}"
            ranked = sorted(stratum, key=lambda st: shash(st[1]))
            if any(done.get((pool, ident), {}).get("decision") == "accept" for _, ident in ranked):
                continue
            accepted = False
            for rank, (size, ident) in enumerate(ranked):
                if (pool, ident) in done:
                    continue
                rec = {f: "" for f in ATTEMPT_FIELDS}
                rec.update(pool=pool, stratum=label, hash_rank=rank, id=ident,
                           selection_hash=shash(ident), listed_bytes=size)
                decision, reason = "reject", ""
                dl = 0
                try:
                    if pool == "P3":
                        row = nomad[ident]
                        base = row["chgcar_path"].rsplit("/", 1)[-1]
                        url = NOMAD_RAW.format(eid=ident, base=base)
                        rec["material_id"] = "nomad-" + ident[:12]
                        if ident in excl_ids or rec["material_id"] in excl_ids:
                            raise ValueError("excluded_id")
                        if row["upload_id"] in excl_uploads:
                            raise ValueError("excluded_upload")
                    else:
                        url = f"{S3}chgcars/{ident}.json.gz"
                        if ident in excl_ids:
                            raise ValueError("excluded_id")
                    rec["url"] = url
                    try:
                        blob, sha, nbytes = download(url, scratch / "candidate.bin")
                    except PermanentDownloadError as exc:
                        raise ValueError(f"download_failed:{exc}") from exc
                    dl += nbytes
                    rec.update(sha256=sha, source_bytes=nbytes)
                    workdir = scratch / "work"
                    workdir.mkdir(exist_ok=True)
                    try:
                        if pool == "P3":
                            meta = {"source": "NOMAD surfaces/adsorbates", "url": url}
                        else:
                            meta = {"source": "Materials Project"}
                            chg = decode_mp_chgcar(blob)
                            comment = str(getattr(chg.poscar, "comment", "")).strip().lower()
                            if comment.startswith("mp-") and comment[3:].isdigit():
                                rec["material_id"] = comment
                            else:
                                rec["material_id"] = ident
                            del chg
                        grid, _ = build_grid(meta, blob, workdir)
                    except Exception as exc:  # noqa: BLE001
                        raise ValueError(f"parse_failed:{type(exc).__name__}") from exc
                    finally:
                        del blob
                        for p in workdir.iterdir():
                            p.unlink()
                    gm = grid_meta(grid)
                    ok = density_ok(grid.total)
                    del grid
                    gc.collect()
                    shape = gm["shape"]
                    npts = math.prod(shape)
                    rec.update(formula=gm["formula"], ngrid="x".join(map(str, shape)),
                               npoints=npts, natoms=gm["natoms"],
                               lattice_abc=gm["lattice_abc"], lattice_angles=gm["lattice_angles"])
                    if pool != "P3" and rec["material_id"] in excl_ids:
                        raise ValueError("excluded_material_id")
                    if not ok:
                        raise ValueError("density_not_finite_positive")
                    if not NPTS_MIN <= npts <= NPTS_MAX:
                        raise ValueError("npoints_out_of_range")
                    if gm["formula"] in excl_formulas:
                        raise ValueError("excluded_formula")
                    if gm["formula"] in accepted_formulas:
                        raise ValueError("duplicate_formula_in_population")
                    if pool == "P2":
                        for name, idx in (("aeccar0", ae0), ("aeccar2", ae2)):
                            try:
                                ablob, _, an = download(f"{S3}{name}s/{ident}.json.gz",
                                                        scratch / "aeccar.bin")
                            except PermanentDownloadError as exc:
                                raise ValueError(f"{name}_download_failed:{exc}") from exc
                            dl += an
                            rec[f"{name}_bytes"] = an
                            try:
                                ach = decode_mp_chgcar(ablob)
                            except Exception as exc:  # noqa: BLE001
                                raise ValueError(f"{name}_parse_failed:{type(exc).__name__}") from exc
                            finally:
                                del ablob
                            arr = ach.data["total"]
                            ashape = tuple(int(x) for x in np.shape(arr))
                            afinite = bool(np.isfinite(arr).all())
                            del ach, arr
                            gc.collect()
                            if ashape != shape:
                                raise ValueError(f"{name}_shape_mismatch")
                            if not afinite:
                                raise ValueError(f"{name}_not_finite")
                    decision, reason = "accept", "ok"
                except ValueError as exc:
                    reason = str(exc)
                rec.update(decision=decision, reason=reason, downloaded_bytes=dl)
                logw.writerow(rec)
                logf.flush()
                done[(pool, ident)] = rec
                print(f"{label} rank {rank} {ident} {decision} {reason} "
                      f"{rec['formula']} {rec['ngrid']} dl={dl}", flush=True)
                if decision == "accept":
                    accepted_formulas.add(rec["formula"])
                    accepted = True
                    break
            if not accepted:
                print(f"{label} EXHAUSTED without acceptance", flush=True)
    logf.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
