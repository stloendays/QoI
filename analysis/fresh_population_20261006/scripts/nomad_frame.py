"""Freeze a NOMAD surface/adsorbate VASP frame (metadata only, public API, no credentials).

Query: results.material.structural_type = "surface" AND
       results.method.simulation.program_name = "VASP"  (owner = public)
For every entry, the CHGCAR candidate is a raw file in the mainfile directory
whose basename matches ^CHGCAR(.bz2|.gz|.xz)?$ (first in name order).

Writes nomad_frame_surface_vasp.csv.gz with
entry_id,upload_id,mainfile,chgcar_path,chgcar_bytes,formula_nomad,reduced_formula
"""
from __future__ import annotations

import csv
import gzip
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from pymatgen.core import Composition

API = "https://nomad-lab.eu/prod/v1/api/v1"
QUERY = {
    "results.material.structural_type": "surface",
    "results.method.simulation.program_name": "VASP",
}
CHG_RE = re.compile(r"^CHGCAR(\.(bz2|gz|xz))?$")


def post(path: str, body: dict) -> dict:
    data = json.dumps(body).encode()
    for attempt in range(6):
        try:
            req = urllib.request.Request(API + path, data=data,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.loads(r.read())
        except Exception as exc:  # noqa: BLE001
            if attempt == 5:
                raise
            print(f"retry {attempt}: {exc}", file=sys.stderr)
            time.sleep(10 * (attempt + 1))
    raise RuntimeError


def paginate(path: str, extra: dict):
    after = None
    while True:
        pag = {"page_size": 100, "order_by": "entry_id", "order": "asc"}
        if after:
            pag["page_after_value"] = after
        res = post(path, {"owner": "public", "query": QUERY, "pagination": pag, **extra})
        yield from res["data"]
        after = res["pagination"].get("next_page_after_value")
        if not after:
            return


def reduce(f: str) -> str:
    try:
        return Composition(f).reduced_formula
    except Exception:  # noqa: BLE001
        return ""


def get(path: str) -> dict | None:
    """GET with unlimited backoff on 429/transient errors; None only for 404 or a repeated 500."""
    n500 = 0
    attempt = 0
    while True:
        attempt += 1
        try:
            with urllib.request.urlopen(API + path, timeout=300) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            if exc.code == 500:
                n500 += 1
                if n500 >= 3:
                    return None
            err = exc
        except Exception as exc:  # noqa: BLE001
            err = exc
        if attempt > 40:
            raise RuntimeError(f"giving up on {path}: {err}")
        print(f"retry {attempt} {path}: {err}", file=sys.stderr)
        time.sleep(min(120, 5 * attempt))


def main() -> int:
    # entries/rawdir/query fails server-side for this filter (HTTP 500,
    # "Inconsistency: both public and restricted files found"), so file names
    # come from entries/query and sizes from per-entry GET /entries/<id>/rawdir.
    out = Path(sys.argv[1])
    started = datetime.now(timezone.utc).isoformat()
    n_entries = 0
    cand = []
    for e in paginate("/entries/query", {"required": {"include": [
            "entry_id", "upload_id", "mainfile", "files",
            "results.material.chemical_formula_reduced"]}}):
        n_entries += 1
        mainfile = e.get("mainfile", "")
        main_dir = mainfile.rsplit("/", 1)[0] if "/" in mainfile else ""
        names = []
        for path in e.get("files", []):
            d, _, base = path.rpartition("/")
            if d == main_dir and CHG_RE.match(base):
                names.append((base, path))
        if not names:
            continue
        fm = e.get("results", {}).get("material", {}).get("chemical_formula_reduced", "")
        base, path = sorted(names)[0]
        cand.append([e["entry_id"], e["upload_id"], mainfile, path, fm])

    def size_of(row):
        res = get(f"/entries/{urllib.parse.quote(row[0])}/rawdir")
        if not res:
            return None
        for f in res["data"]["files"]:
            if f["path"] == row[3]:
                return f["size"]
        return None

    with ThreadPoolExecutor(3) as ex:
        sizes = list(ex.map(size_of, cand))
    rows, n_nosize = [], 0
    for row, size in zip(cand, sizes):
        if size is None:
            n_nosize += 1
            continue
        rows.append([row[0], row[1], row[2], row[3], size, row[4], reduce(row[4])])
    with gzip.open(out / "nomad_frame_surface_vasp.csv.gz", "wt", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["entry_id", "upload_id", "mainfile", "chgcar_path", "chgcar_bytes",
                    "formula_nomad", "reduced_formula"])
        w.writerows(rows)
    log = {"api": API, "query": QUERY, "owner": "public",
           "listing_started_utc": started,
           "listing_finished_utc": datetime.now(timezone.utc).isoformat(),
           "n_entries": n_entries,
           "n_entries_with_chgcar_in_mainfile_dir": len(cand),
           "n_rawdir_size_unavailable_dropped": n_nosize,
           "n_frame_rows": len(rows)}
    (out / "nomad_frame_log.json").write_text(json.dumps(log, indent=2))
    print(json.dumps(log, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
