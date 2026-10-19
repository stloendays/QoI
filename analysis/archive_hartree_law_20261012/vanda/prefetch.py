#!/usr/bin/env python3
"""Prefetch the frozen 300-object WP-F sample on the Vanda login node."""
from __future__ import annotations

import csv
import hashlib
import os
import time
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
REPO = STUDY.parents[1]
SAMPLE = REPO / "analysis" / "extensions_20260930" / "WP-F" / "sample.csv"
INPUTS = HERE / "inputs"
MANIFEST = INPUTS / "MANIFEST.tsv"
USER_AGENT = "QoI-archive-law-20261012/1.0 (research; anonymous public bucket)"


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def read_sample() -> list[dict[str, str]]:
    with SAMPLE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 300:
        raise RuntimeError(f"expected 300 sample rows, found {len(rows)}")
    return rows


def read_existing_manifest() -> dict[str, dict[str, str]]:
    if not MANIFEST.exists():
        return {}
    with MANIFEST.open(newline="", encoding="utf-8") as handle:
        return {row["task_id"]: row for row in csv.DictReader(handle, delimiter="\t")}


def write_manifest(rows: dict[str, dict[str, str]]) -> None:
    fields = [
        "task_id", "stratum", "key", "url", "path", "expected_bytes",
        "actual_bytes", "sha256", "size_matches_sample", "status",
    ]
    temp = MANIFEST.with_suffix(".tmp")
    with temp.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        for task_id in sorted(rows):
            writer.writerow(rows[task_id])
    os.replace(temp, MANIFEST)


def download(row: dict[str, str], destination: Path) -> bytes:
    error: Exception | None = None
    for attempt in range(1, 4):
        try:
            request = urllib.request.Request(row["url"], headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=900) as response:
                blob = response.read()
            if len(blob) != int(row["bytes"]):
                raise RuntimeError(f"size {len(blob)} != sample {row['bytes']}")
            part = destination.with_suffix(destination.suffix + ".part")
            part.write_bytes(blob)
            os.replace(part, destination)
            return blob
        except Exception as exc:
            error = exc
            part = destination.with_suffix(destination.suffix + ".part")
            if part.exists():
                part.unlink()
            if attempt < 3:
                time.sleep(10 * attempt)
    raise RuntimeError(f"download failed after 3 attempts: {error}")


def main() -> int:
    INPUTS.mkdir(parents=True, exist_ok=True)
    rows = read_sample()
    manifest = read_existing_manifest()
    failures = 0
    for row in rows:
        task_id = row["task_id"]
        destination = INPUTS / f"{task_id}.json.gz"
        base = {
            "task_id": task_id, "stratum": row["stratum"], "key": row["key"],
            "url": row["url"], "path": destination.name, "expected_bytes": row["bytes"],
        }
        prior = manifest.get(task_id, {})
        blob: bytes | None = None
        if destination.is_file() and prior.get("status") == "OK":
            candidate = destination.read_bytes()
            if len(candidate) == int(row["bytes"]) and sha256(candidate) == prior.get("sha256", "").lower():
                blob = candidate
        if blob is None and destination.is_file() and not prior:
            candidate = destination.read_bytes()
            if len(candidate) == int(row["bytes"]):
                blob = candidate
        if blob is None:
            try:
                blob = download(row, destination)
            except Exception as exc:
                failures += 1
                manifest[task_id] = base | {
                    "actual_bytes": "", "sha256": "", "size_matches_sample": "0", "status": "FAILED",
                }
                write_manifest(manifest)
                print(f"{task_id} FAILED {type(exc).__name__}: {exc}", flush=True)
                continue
        manifest[task_id] = base | {
            "actual_bytes": str(len(blob)), "sha256": sha256(blob),
            "size_matches_sample": str(len(blob) == int(row["bytes"])), "status": "OK",
        }
        write_manifest(manifest)
        print(f"{task_id} OK bytes={len(blob)}", flush=True)
    print(f"MANIFEST {MANIFEST} rows={len(manifest)} failures={failures}", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
