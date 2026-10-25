"""Login node: download every input of both studies, verify size / SHA-256, write MANIFEST.tsv, mark completion.

inputs/arch/<task_id>.json.gz  300 archive-sample objects (size must equal frame_bytes; SHA-256 recorded)
inputs/w1/<material_id>.src    92 P1/P3b sources and the development material mp-2521964 (SHA-256 and size must
                               equal the manifest)
Resumable: verified files are kept.
"""
import csv
import hashlib
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path("/scratch/junbotong/qoi-algo-20261025")
V = ROOT / "analysis/server_runs_20261025b/vanda"


def get(url, tries=6):
    last = None
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=900) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(10 * (k + 1))
    raise RuntimeError(f"download failed: {last}")


def main():
    rows = []
    arch = list(csv.DictReader(open(ROOT / "analysis/scope_expansion_20261022/archive_hartree_objects.csv", encoding="utf-8")))
    mats = []
    for m in ("P1_CONFIRMATORY_MANIFEST.csv", "P3B_CONFIRMATORY_MANIFEST.csv"):
        mats += list(csv.DictReader(open(ROOT / "analysis/fresh_population_20261006" / m, encoding="utf-8")))
    mats += [r for r in csv.DictReader(open(ROOT / "analysis/fresh_population_20261006/P1_ENGINEERING_MANIFEST.csv",
                                            encoding="utf-8")) if r["material_id"] == "mp-2521964"]
    jobs = [("arch", r["task_id"], r["url"], int(r["frame_bytes"]), None, V / "inputs/arch" / f"{r['task_id']}.json.gz") for r in arch]
    jobs += [("w1", r["material_id"], r["url"], int(r["source_bytes"]), r["sha256"], V / "inputs/w1" / f"{r['material_id']}.src") for r in mats]
    for item, key, url, size, sha, path in jobs:
        path.parent.mkdir(parents=True, exist_ok=True)
        status = "OK"
        try:
            if path.exists() and path.stat().st_size == size and (sha is None or hashlib.sha256(path.read_bytes()).hexdigest() == sha):
                blob = path.read_bytes()
            else:
                blob = get(url)
                if len(blob) != size:
                    raise RuntimeError(f"size {len(blob)} != {size}")
                if sha is not None and hashlib.sha256(blob).hexdigest() != sha:
                    raise RuntimeError("sha256 mismatch")
                tmp = path.with_suffix(".part")
                tmp.write_bytes(blob)
                tmp.replace(path)
            digest = hashlib.sha256(blob).hexdigest()
        except Exception as e:  # noqa: BLE001
            status, digest = f"FAILED {type(e).__name__}: {e}"[:200], ""
        rows.append((item, key, size, digest, status))
        print(item, key, status, flush=True)
    with open(V / "inputs/MANIFEST.tsv", "w", encoding="utf-8") as fh:
        fh.write("item\tkey\tbytes\tsha256\tstatus\n")
        for r in rows:
            fh.write("\t".join(map(str, r)) + "\n")
    bad = [r for r in rows if r[4] != "OK"]
    if not bad:
        (V / "PREFETCH_COMPLETE").write_text(f"{len(rows)} inputs OK\n")
    print("PREFETCH", len(rows) - len(bad), "OK,", len(bad), "failed")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
