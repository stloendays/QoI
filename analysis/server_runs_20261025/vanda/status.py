#!/usr/bin/env python3
"""Read-only status of the linearized-XC study on Vanda (JSON). --probe: probe verdict only."""
import argparse
import csv
import json
from pathlib import Path

ROOT = Path("/scratch/junbotong/qoi-xcl-20261025")
V = ROOT / "analysis/server_runs_20261025/vanda"


def ck(kind):
    out = {}
    for p in (V / "checkpoints" / kind).glob("*.json"):
        try:
            out[p.stem] = json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            out[p.stem] = {"status": "UNREADABLE"}
    return out


def tasks(name):
    p = V / name
    return [l.split("\t")[0].strip() for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def count(kind, task_file):
    t = tasks(task_file)
    c = ck(kind)
    s = sum(c.get(x, {}).get("status") == "SUCCESS" for x in t)
    f = sum(x in c and c[x].get("status") != "SUCCESS" for x in t)
    return {"total": len(t), "success": s, "failed": f, "pending": len(t) - s - f}


def probe():
    """Both probe materials SUCCESS, with X and F certified at both tolerances (PROTOCOL §7)."""
    checks = {}
    x = ck("xcl")
    for m in tasks("probe_tasks_xcl.txt"):
        c = x.get(m)
        if c is None:
            checks[f"xcl_{m}"] = None
            continue
        rows = c.get("xc_contract", [])
        checks[f"xcl_{m}"] = c.get("status") == "SUCCESS" and len(rows) == 4 and all(r.get("certified") for r in rows)
    pend = any(v is None for v in checks.values())
    verdict = "PENDING" if pend else ("PASS" if all(checks.values()) else "FAIL")
    return {"verdict": verdict, "checks": checks}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    a = ap.parse_args()
    if a.probe:
        print(json.dumps(probe(), indent=1))
        return
    man = V / "inputs/MANIFEST.tsv"
    rows = list(csv.DictReader(man.open(encoding="utf-8"), delimiter="\t")) if man.exists() else []
    print(json.dumps({"install": (V / "INSTALL_COMPLETE").exists(),
                      "prefetch": {"complete": (V / "PREFETCH_COMPLETE").exists(), "rows": len(rows),
                                   "ok": sum(r["status"] == "OK" for r in rows),
                                   "failed": sum(r["status"] != "OK" for r in rows)},
                      "xcl": count("xcl", "tasks_xcl.tsv"),
                      "probe": probe() if (V / "probe/verdict.json").exists() else {"verdict": "NOT_RUN"}}))


if __name__ == "__main__":
    main()
