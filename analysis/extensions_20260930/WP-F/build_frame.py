#!/usr/bin/env python3
"""WP-F sampling frame: every charge-density object in the public MP parsed bucket.

Lists s3://materialsproject-parsed/chgcars/ anonymously (keys and byte sizes only; no object
content is read) and writes frame.csv with one row per `chgcars/<task_id>.json.gz` object.
Objects that are development or external systems of the frozen study are flagged, not dropped.

    python build_frame.py            -> frame.csv, frame_provenance.json
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BUCKET = "https://materialsproject-parsed.s3.amazonaws.com/"
NS = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
KEY_RE = re.compile(r"^chgcars/(mp-\d+)\.json\.gz$")


def list_prefix(prefix: str):
    token, page = None, 0
    while True:
        q = {"list-type": "2", "prefix": prefix, "max-keys": "1000"}
        if token:
            q["continuation-token"] = token
        url = BUCKET + "?" + urllib.parse.urlencode(q)
        for attempt in range(5):
            try:
                with urllib.request.urlopen(url, timeout=120) as r:
                    root = ET.fromstring(r.read())
                break
            except Exception:  # noqa: BLE001
                time.sleep(2 * (attempt + 1))
        else:
            raise RuntimeError("listing failed at page %d" % page)
        for c in root.findall("s3:Contents", NS):
            yield c.find("s3:Key", NS).text, int(c.find("s3:Size", NS).text), c.find("s3:LastModified", NS).text
        page += 1
        if root.find("s3:IsTruncated", NS).text != "true":
            break
        token = root.find("s3:NextContinuationToken", NS).text


def frozen_task_ids() -> set[str]:
    ids = set()
    for path in (REPO / "materials_metadata.csv",):
        with path.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                m = re.search(r"chgcars/(mp-\d+)\.json\.gz", r.get("url", ""))
                if m:
                    ids.add(m.group(1))
    # external systems: any MP chgcar key mentioned in the external manifest
    ext = REPO / "external_test_MANIFEST.json"
    if ext.exists():
        ids |= set(re.findall(r"chgcars/(mp-\d+)\.json\.gz", ext.read_text(encoding="utf-8")))
    return ids


def main() -> int:
    t0 = time.time()
    frozen = frozen_task_ids()
    rows, skipped = [], 0
    for key, size, modified in list_prefix("chgcars/"):
        m = KEY_RE.match(key)
        if not m:
            skipped += 1
            continue
        rows.append(dict(key=key, task_id=m.group(1), bytes=size, last_modified=modified,
                         in_frozen_study=int(m.group(1) in frozen)))
    rows.sort(key=lambda r: r["task_id"])
    out = HERE / "frame.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    prov = dict(bucket=BUCKET, prefix="chgcars/", n_objects=len(rows), n_non_task_keys_skipped=skipped,
                n_flagged_frozen=sum(r["in_frozen_study"] for r in rows), total_bytes=sum(r["bytes"] for r in rows),
                n_frozen_task_ids_known=len(frozen), frame_sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
                listed_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), wall_seconds=time.time() - t0)
    (HERE / "frame_provenance.json").write_text(json.dumps(prov, indent=1), encoding="utf-8")
    print(json.dumps(prov, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
