#!/usr/bin/env python3
"""WS-A0: size of every top-level prefix of the public Materials Project parsed bucket.

Anonymous S3 ListObjectsV2 (keys and sizes only, no object content), the same
listing method as the WP-F frame builder. Writes prefix_sizes.csv and SUMMARY.json:
object count and total bytes per prefix, so the charge-density frame used by the
archive estimates (chgcars/, 8.50 TB) can be placed among the other volumetric
products the bucket serves (e.g. AECCAR, ELFCAR, LOCPOT, if present).
Descriptive only.
"""
from __future__ import annotations

import csv
import json
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

BUCKET = "https://materialsproject-parsed.s3.amazonaws.com/"
NS = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}


def get(q: dict) -> ET.Element:
    url = BUCKET + "?" + urllib.parse.urlencode(q)
    for attempt in range(6):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                return ET.fromstring(r.read())
        except Exception:  # noqa: BLE001
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"listing failed: {url}")


def prefixes() -> list[str]:
    out, token = [], None
    while True:
        q = {"list-type": "2", "delimiter": "/", "max-keys": "1000"}
        if token:
            q["continuation-token"] = token
        root = get(q)
        out += [p.find("s3:Prefix", NS).text for p in root.findall("s3:CommonPrefixes", NS)]
        if root.find("s3:IsTruncated", NS).text != "true":
            return out
        token = root.find("s3:NextContinuationToken", NS).text


def size_of(prefix: str) -> tuple[int, int]:
    n = total = 0
    token = None
    while True:
        q = {"list-type": "2", "prefix": prefix, "max-keys": "1000"}
        if token:
            q["continuation-token"] = token
        root = get(q)
        for c in root.findall("s3:Contents", NS):
            n += 1
            total += int(c.find("s3:Size", NS).text)
        if root.find("s3:IsTruncated", NS).text != "true":
            return n, total
        token = root.find("s3:NextContinuationToken", NS).text


def main() -> int:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "bucket_census")
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    t0 = time.time()
    for p in prefixes():
        n, b = size_of(p)
        rows.append({"prefix": p, "objects": n, "bytes": b, "TB": b / 1e12})
        print(p, n, f"{b / 1e12:.4f} TB", f"{time.time() - t0:.0f}s", flush=True)
    rows.sort(key=lambda r: -r["bytes"])
    with (out / "prefix_sizes.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["prefix", "objects", "bytes", "TB"])
        w.writeheader()
        w.writerows(rows)
    summ = {"listed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "bucket": BUCKET,
            "prefixes": len(rows), "total_TB": sum(r["bytes"] for r in rows) / 1e12, "rows": rows}
    (out / "SUMMARY.json").write_text(json.dumps(summ, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
