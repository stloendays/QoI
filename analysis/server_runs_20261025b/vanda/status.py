#!/usr/bin/env python3
"""Read-only status of the two studies on Vanda (JSON). --probe: probe verdict only."""
import argparse
import csv
import json
from pathlib import Path

ROOT = Path("/scratch/junbotong/qoi-algo-20261025")
V = ROOT / "analysis/server_runs_20261025b/vanda"
KNOWN = ROOT / "analysis/waterfill_writer_20261025/results/DEV_KNOWN_ANSWER.json"
W1_ARMS = ("L1", "W1", "W1S", "T1S", "O1", "O1S")


def ck(kind, base=None):
    out = {}
    for p in ((base or V / "checkpoints" / kind)).glob("*.json"):
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
        strata = {l.split("\t")[0]: l.split("\t")[1] for l in (V / task_file).read_text().splitlines() if l.strip()}
        out["pending_small"] = sum(x not in c and not strata[x].startswith("D10") for x in t)
        out["pending_large"] = sum(x not in c and strata[x].startswith("D10") for x in t)
    return out


def w1_certified(c, taus=(1e-6, 1e-4)):
    rows = {(r["arm"], float(r["tau"])): r for r in c.get("rows", [])}
    return all(rows.get((a, t), {}).get("certified") for a in W1_ARMS for t in taus)


def probe():
    checks = {}
    for name in ("tests_w1", "tests_arch"):
        p = V / "probe" / f"{name}.ok"
        checks[name] = None if not p.exists() else p.read_text().strip() == "OK"
    dev = ck("dev", V / "probe" / "dev").get("mp-2521964")
    if dev is None:
        checks["known_answer"] = None
    else:
        ka = json.loads(KNOWN.read_text())["bytes"]
        got = {f"{r['arm']}_{float(r['tau']):g}": r.get("bytes") for r in dev.get("rows", [])}
        checks["known_answer"] = dev.get("status") == "SUCCESS" and all(
            got.get(k) is not None and abs(got[k] - v) <= max(3, 0.005 * v) for k, v in ka.items())
    w = ck("w1")
    for m in tasks("probe_tasks_w1.txt"):
        c = w.get(m)
        checks[f"w1_{m}"] = None if c is None else (c.get("status") == "SUCCESS" and w1_certified(c))
    a = ck("arch")
    for t in tasks("probe_tasks_arch.txt"):
        c = a.get(t)
        checks[f"arch_{t}"] = None if c is None else (c.get("status") == "SUCCESS" and all(
            c["results"][f"{x}_1e-06"]["certified"] for x in ("W", "Q")))
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
                      "w1": count("w1", "tasks_w1.tsv"), "arch": count("arch", "tasks_arch.tsv"),
                      "probe": probe() if (V / "probe/verdict.json").exists() else {"verdict": "NOT_RUN"}}))


if __name__ == "__main__":
    main()
