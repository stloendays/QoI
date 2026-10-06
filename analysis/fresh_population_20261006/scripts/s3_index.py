"""Index the anonymous materialsproject-parsed S3 prefixes (metadata only).

Writes s3_index_<prefix>.csv.gz with columns key,task_id,size,last_modified,etag.
"""
from __future__ import annotations

import csv
import gzip
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

BUCKET = "https://materialsproject-parsed.s3.amazonaws.com/"
NS = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
TASK_RE = re.compile(r"^[a-z0-9]+/(mp-\d+)\.json\.gz$")


def list_prefix(prefix: str):
    token = None
    while True:
        params = {"list-type": "2", "prefix": prefix, "max-keys": "1000"}
        if token:
            params["continuation-token"] = token
        url = BUCKET + "?" + urllib.parse.urlencode(params)
        for attempt in range(6):
            try:
                with urllib.request.urlopen(url, timeout=120) as r:
                    root = ET.fromstring(r.read())
                break
            except Exception as exc:  # noqa: BLE001
                if attempt == 5:
                    raise
                print(f"retry {attempt}: {exc}", file=sys.stderr)
                time.sleep(5 * (attempt + 1))
        for c in root.findall("s3:Contents", NS):
            yield (
                c.find("s3:Key", NS).text,
                int(c.find("s3:Size", NS).text),
                c.find("s3:LastModified", NS).text,
                c.find("s3:ETag", NS).text.strip('"'),
            )
        if root.find("s3:IsTruncated", NS).text != "true":
            return
        token = root.find("s3:NextContinuationToken", NS).text


def main() -> int:
    out_dir = Path(sys.argv[1])
    log = {}
    for prefix in ("chgcars/", "aeccar0s/", "aeccar2s/"):
        started = datetime.now(timezone.utc).isoformat()
        name = prefix.rstrip("/")
        path = out_dir / f"s3_index_{name}.csv.gz"
        n = n_task = 0
        with gzip.open(path, "wt", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["key", "task_id", "size", "last_modified", "etag"])
            for key, size, lm, etag in list_prefix(prefix):
                m = TASK_RE.match(key)
                tid = m.group(1) if m else ""
                n += 1
                n_task += bool(tid)
                w.writerow([key, tid, size, lm, etag])
        log[name] = {
            "listing_started_utc": started,
            "listing_finished_utc": datetime.now(timezone.utc).isoformat(),
            "n_keys": n,
            "n_task_keys": n_task,
        }
        print(name, n, n_task, flush=True)
    (out_dir / "s3_index_log.json").write_text(json.dumps(log, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
