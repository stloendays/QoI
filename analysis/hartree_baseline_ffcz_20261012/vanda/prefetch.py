#!/usr/bin/env python3
"""Login-node prefetch of all staged manifests and source bytes."""
from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import urllib.request
from pathlib import Path


STAGING_ROOT = Path("/scratch/junbotong/qoi-ffcz-20261012")
CODE_DIR = Path(__file__).resolve().parents[1]
REPO_DEFAULT = CODE_DIR.parents[1]
MANIFESTS = (
    "analysis/fresh_population_20261006/P1_CONFIRMATORY_MANIFEST.csv",
    "analysis/fresh_population_20261006/P3B_CONFIRMATORY_MANIFEST.csv",
    "analysis/fresh_population_20261006/P1_ENGINEERING_MANIFEST.csv",
)
MANIFEST_SHA256 = {
    MANIFESTS[0]: "3297d6c17959c7a70bf157f7157283f45ddb046fdc460acaa8a8570ab4de7331",
    MANIFESTS[1]: "e7c447d5f8dc3b263c7b5b4b9d1f8344ad9c8ed41e5b72fa333c37ad14b70f97",
    MANIFESTS[2]: "480bc38667544eb4023276ad9def91eff451b4f1dbccb7cde76fb707b66fd6a9",
}
SHAKEDOWN_ID = "mp-3148759"


def fetch_exact(url: str, expected_sha: str, expected_bytes: int) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "QoI-FFCz-prefetch/1.0"})
    with urllib.request.urlopen(request, timeout=300) as response:
        blob = response.read()
    actual = hashlib.sha256(blob).hexdigest()
    if actual != expected_sha:
        raise RuntimeError(f"source SHA256 mismatch: {actual} != {expected_sha}")
    if len(blob) != expected_bytes:
        raise RuntimeError(f"source byte-count mismatch: {len(blob)} != {expected_bytes}")
    return blob


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_DEFAULT)
    parser.add_argument("--staging-root", type=Path, default=STAGING_ROOT)
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    root = args.staging_root.resolve()
    inputs = root / "inputs"
    materials = inputs / "materials"
    materials.mkdir(parents=True, exist_ok=True)
    manifest_rows: list[dict[str, str]] = []
    all_materials: dict[str, dict[str, str]] = {}
    for relative in MANIFESTS:
        source = repo / relative
        if not source.is_file():
            raise RuntimeError(f"manifest missing: {source}")
        destination = inputs / Path(relative).name
        shutil.copyfile(source, destination)
        digest = hashlib.sha256(destination.read_bytes()).hexdigest()
        if digest != MANIFEST_SHA256[relative]:
            raise RuntimeError(f"manifest SHA256 mismatch for {relative}: {digest} != {MANIFEST_SHA256[relative]}")
        manifest_rows.append({"kind": "manifest", "material_id": "", "manifest": relative,
                              "relative_path": str(destination.relative_to(root)), "sha256": digest,
                              "source_bytes": str(destination.stat().st_size), "url": ""})
        with source.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if relative != MANIFESTS[2] or row["material_id"] == SHAKEDOWN_ID:
                    all_materials.setdefault(row["material_id"], row)

    for material_id, row in all_materials.items():
        destination = materials / f"{material_id}.source"
        if destination.is_file():
            blob = destination.read_bytes()
            if hashlib.sha256(blob).hexdigest() != row["sha256"] or len(blob) != int(row["source_bytes"]):
                destination.unlink()
        if not destination.is_file():
            destination.write_bytes(fetch_exact(row["url"], row["sha256"], int(row["source_bytes"])))
        blob = destination.read_bytes()
        actual = hashlib.sha256(blob).hexdigest()
        if actual != row["sha256"] or len(blob) != int(row["source_bytes"]):
            raise RuntimeError(f"staged source validation failed for {material_id}")
        manifest_rows.append({"kind": "source", "material_id": material_id, "manifest": row["corpus"],
                              "relative_path": str(destination.relative_to(root)), "sha256": actual,
                              "source_bytes": str(len(blob)), "url": row["url"]})

    manifest_rows.sort(key=lambda row: (row["kind"], row["material_id"], row["relative_path"]))
    with (inputs / "MANIFEST.tsv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["kind", "material_id", "manifest", "relative_path", "sha256", "source_bytes", "url"], delimiter="\t")
        writer.writeheader()
        writer.writerows(manifest_rows)
    print(f"prefetched {len(all_materials)} materials and {len(MANIFESTS)} manifests into {inputs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
