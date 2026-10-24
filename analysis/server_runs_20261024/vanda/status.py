#!/usr/bin/env python3
"""Read-only status of the two studies on Vanda (JSON). --probe: probe verdict only."""
import argparse
import csv
import json
from pathlib import Path

ROOT = Path("/scratch/junbotong/qoi-srv-20261024")
V = ROOT / "analysis/server_runs_20261024/vanda"


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
    out = {"total": len(t), "success": s, "failed": f, "pending": len(t) - s - f}
    if kind == "arch":                                  # pending per production script (strata of tasks_arch.tsv)
        strata = {l.split("	")[0]: l.split("	")[1] for l in (V / task_file).read_text().splitlines() if l.strip()}
        out["pending_small"] = sum(x not in c and not strata[x].startswith("D10") for x in t)
        out["pending_large"] = sum(x not in c and strata[x].startswith("D10") for x in t)
    return out


def probe():
    checks, pend = {}, False
    lx = V / "probe/libxc.json"
    try:
        d = json.loads(lx.read_text())
        checks["libxc"] = d["lda_exc_maxrel"] < 1e-8 and d["lda_vxc_maxrel"] < 1e-8 and d["pbe_exc_maxrel"] < 1e-3
    except Exception:  # noqa: BLE001
        checks["libxc"] = None
    try:
        checks["writers"] = bool(json.loads((V / "probe/writers.json").read_text())["ok"])
    except Exception:  # noqa: BLE001
        checks["writers"] = None
    a = ck("arch")
    for t in tasks("probe_tasks_arch.txt"):
        c = a.get(t)
        checks[f"arch_{t}"] = None if c is None else (c.get("status") == "SUCCESS" and all(
            c["results"][f"{w}_1e-06"]["certified"] for w in ("T", "O")))
    x = ck("xc")
    for m in tasks("probe_tasks_xc.txt"):
        c = x.get(m)
        if c is None:
            checks[f"xc_{m}"] = None
            continue
        rows = [r for r in c.get("transfer", []) if r.get("status") == "OK"]
        checks[f"xc_{m}"] = c.get("status") == "SUCCESS" and len(rows) >= 9 and all(
            r["hartree_certified"] and abs(r["bytes"] - r["bytes_recorded"]) <= max(3, 1e-3 * r["bytes_recorded"]) for r in rows)
    if any(v is None for v in checks.values()):
        pend = True
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
                      "arch": count("arch", "tasks_arch.tsv"), "xc": count("xc", "tasks_xc.tsv"),
                      "probe": probe() if (V / "probe/verdict.json").exists() else {"verdict": "NOT_RUN"}}))


if __name__ == "__main__":
    main()
