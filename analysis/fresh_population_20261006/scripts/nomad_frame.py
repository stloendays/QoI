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
import urllib.request
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


def main() -> int:
    out = Path(sys.argv[1])
    started = datetime.now(timezone.utc).isoformat()
    formulas = {}
    for e in paginate("/entries/query", {"required": {"include": [
            "entry_id", "results.material.chemical_formula_reduced"]}}):
        formulas[e["entry_id"]] = (e.get("results", {}).get("material", {})
                                   .get("chemical_formula_reduced", ""))
    n_entries = n_chg = 0
    rows = []
    for e in paginate("/entries/rawdir/query", {}):
        n_entries += 1
        main_dir = e["mainfile"].rsplit("/", 1)[0] if "/" in e["mainfile"] else ""
        cands = []
        for f in e.get("files", []):
            d, _, base = f["path"].rpartition("/")
            if d == main_dir and CHG_RE.match(base):
                cands.append((base, f["path"], f["size"]))
        if not cands:
            continue
        n_chg += 1
        base, path, size = sorted(cands)[0]
        fm = formulas.get(e["entry_id"], "")
        rows.append([e["entry_id"], e["upload_id"], e["mainfile"], path, size, fm, reduce(fm)])
    with gzip.open(out / "nomad_frame_surface_vasp.csv.gz", "wt", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["entry_id", "upload_id", "mainfile", "chgcar_path", "chgcar_bytes",
                    "formula_nomad", "reduced_formula"])
        w.writerows(rows)
    log = {"api": API, "query": QUERY, "owner": "public",
           "listing_started_utc": started,
           "listing_finished_utc": datetime.now(timezone.utc).isoformat(),
           "n_entries": n_entries, "n_entries_with_formula": len(formulas),
           "n_entries_with_chgcar_in_mainfile_dir": n_chg}
    (out / "nomad_frame_log.json").write_text(json.dumps(log, indent=2))
    print(json.dumps(log, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
