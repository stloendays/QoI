#!/usr/bin/env python3
"""Re-list the NOMAD surface/VASP entries that the 2026-10-06 frame dropped for "rawdir size unavailable" (metadata only).

The 2026-10-06 frame (`analysis/fresh_population_20261006/nomad_frame_surface_vasp.csv.gz`, built by
`scripts/nomad_frame.py`) kept 820 of the 1,014 entries with a CHGCAR in the mainfile directory and dropped 194 whose
CHGCAR size could not be read from `GET /entries/<id>/rawdir`. The dropped entries were not recorded by id. This script
repeats the frame query with the same filter and file rule, identifies the dropped entries as the entries with a
CHGCAR in the mainfile directory that are not in the frame and whose `entry_create_time` is before the frame listing
start (2026-10-06T14:37:34Z), and queries their rawdir again. An entry is resolved when the listing now returns the
CHGCAR's size.

Outputs (--out-dir): relisted_entries.csv (one row per identified entry, with `resolved` and `chgcar_bytes`), and
relist_log.json (counts).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FRESH = REPO / "analysis" / "fresh_population_20261006"
sys.path.insert(0, str(FRESH / "scripts"))
import nomad_frame as nf  # noqa: E402  (same API, query, CHGCAR rule, retry policy and formula reduction)

FRAME_LISTING_START = "2026-10-06T14:37:34"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=HERE)
    a = ap.parse_args(argv)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    frame = pd.read_csv(FRESH / "nomad_frame_surface_vasp.csv.gz")
    in_frame = set(frame.entry_id)
    n_entries = 0
    cand = []
    for e in nf.paginate("/entries/query", {"required": {"include": [
            "entry_id", "upload_id", "mainfile", "files", "entry_create_time",
            "results.material.chemical_formula_reduced"]}}):
        n_entries += 1
        mainfile = e.get("mainfile", "")
        main_dir = mainfile.rsplit("/", 1)[0] if "/" in mainfile else ""
        names = []
        for path in e.get("files", []):
            d, _, base = path.rpartition("/")
            if d == main_dir and nf.CHG_RE.match(base):
                names.append((base, path))
        if not names:
            continue
        fm = e.get("results", {}).get("material", {}).get("chemical_formula_reduced", "")
        base, path = sorted(names)[0]
        cand.append({"entry_id": e["entry_id"], "upload_id": e["upload_id"], "mainfile": mainfile,
                     "chgcar_path": path, "formula_nomad": fm, "reduced_formula": nf.reduce(fm),
                     "entry_create_time": str(e.get("entry_create_time", ""))})
    old = [c for c in cand if c["entry_id"] not in in_frame and c["entry_create_time"][:19] < FRAME_LISTING_START]
    new_since = [c for c in cand if c["entry_id"] not in in_frame and c["entry_create_time"][:19] >= FRAME_LISTING_START]

    def size_of(row):
        res = nf.get(f"/entries/{urllib.parse.quote(row['entry_id'])}/rawdir")
        if not res:
            return None
        for f in res["data"]["files"]:
            if f["path"] == row["chgcar_path"]:
                return f.get("size")
        return None

    with ThreadPoolExecutor(3) as ex:
        sizes = list(ex.map(size_of, old))
    rows = []
    for c, s in zip(old, sizes):
        rows.append(c | {"chgcar_bytes": "" if s is None else int(s), "resolved": int(s is not None)})
    a.out_dir.mkdir(parents=True, exist_ok=True)
    cols = ["entry_id", "upload_id", "mainfile", "chgcar_path", "chgcar_bytes", "formula_nomad", "reduced_formula",
            "entry_create_time", "resolved"]
    with open(a.out_dir / "relisted_entries.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: r["entry_id"]))
    log = {"api": nf.API, "query": nf.QUERY, "owner": "public", "listing_started_utc": started,
           "listing_finished_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "n_entries_now": n_entries, "n_entries_with_chgcar_in_mainfile_dir_now": len(cand),
           "n_in_frame": sum(1 for c in cand if c["entry_id"] in in_frame),
           "frame_rows_not_listed_now": len(in_frame - {c["entry_id"] for c in cand}),
           "n_not_in_frame_created_before_frame_listing": len(old),
           "n_not_in_frame_created_after_frame_listing": len(new_since),
           "n_relisted_resolved": sum(r["resolved"] for r in rows),
           "n_relisted_unresolved": sum(1 - r["resolved"] for r in rows),
           "frame_listing_start_utc": FRAME_LISTING_START + "Z",
           "frame_log_n_rawdir_size_unavailable_dropped": 194}
    (a.out_dir / "relist_log.json").write_text(json.dumps(log, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(log, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
