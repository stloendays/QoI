#!/usr/bin/env python3
"""Aggregate study 1: per-material rows, recorded law-protocol arms, the H1–H3 criteria and descriptive ratios."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TAUS = (1e-6, 1e-4, 1e-8)
NEW = ("L1", "W1", "W1S", "T1S", "O1", "O1S")
OLD = ("A1", "A2", "A3", "A6")
RUNS = {"P1": "run_P1_CONFIRMATORY", "P3B": "run_P3B_CONFIRMATORY"}
SEED, NBOOT = 20261025, 10000


def recorded(repo: Path) -> dict:
    """Smallest certified recorded stream per (material, arm, tau) of the law protocol."""
    best = {}
    for run in RUNS.values():
        for r in csv.DictReader(open(repo / "analysis/general_qoac_law/results" / run / "part_a_rows.csv",
                                     encoding="utf-8")):
            if r["certified"] != "True" or r["arm"] not in OLD:
                continue
            k = (r["material_id"], r["arm"], float(r["tau"]))
            if k not in best or int(r["bytes"]) < best[k]:
                best[k] = int(r["bytes"])
    return best


def med_ci(v, rng):
    v = np.asarray(v, float)
    b = np.median(rng.choice(v, size=(NBOOT, v.size), replace=True), axis=1)
    return {"median": float(np.median(v)), "ci95": [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))],
            "n": int(v.size), "min": float(v.min()), "max": float(v.max()), "wins": int(np.sum(v > 1.0))}


def aggregate(ckpt: Path, repo: Path, out: Path) -> dict:
    rec = recorded(repo)
    cks = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(ckpt.glob("*.json"))]
    man = {}
    for c, f in (("P1", "P1_CONFIRMATORY_MANIFEST.csv"), ("P3B", "P3B_CONFIRMATORY_MANIFEST.csv")):
        for r in csv.DictReader(open(repo / "analysis/fresh_population_20261006" / f, encoding="utf-8")):
            man[r["material_id"]] = c
    cks = [c for c in cks if c["material_id"] in man]
    ok = [c for c in cks if c["status"] == "SUCCESS"]
    rows, cr = [], {}
    for c in ok:
        mid = c["material_id"]
        for r in c["rows"]:
            rows.append(r)
            if r["certified"]:
                cr[(mid, r["arm"], float(r["tau"]))] = float(r["cr"])
        raw = float(c["raw_bytes"])
        for arm in OLD:
            for tau in TAUS:
                b = rec.get((mid, arm, tau))
                if b:
                    cr[(mid, arm, tau)] = raw / b
    mats = sorted(c["material_id"] for c in ok)
    sym = {c["material_id"]: c.get("symmetry", {}) for c in ok}
    cohort = {c["material_id"]: c["cohort"] for c in ok}

    def ratio(a, b, tau, sel=None):
        v = [cr[(m, a, tau)] / cr[(m, b, tau)] for m in mats if (m, a, tau) in cr and (m, b, tau) in cr
             and (sel is None or sel(m))]
        return v

    summ = {"materials_checkpointed": len(cks), "materials_success": len(ok), "seed": SEED, "resamples": NBOOT,
            "failed": [c["material_id"] for c in cks if c["status"] != "SUCCESS"], "criteria": {}, "ratios": {},
            "certified": {}, "symmetry": {}}
    for arm in NEW:
        for tau in TAUS:
            summ["certified"][f"{arm}_{tau:g}"] = sum((m, arm, tau) in cr for m in mats)
    pairs = [("O1S", "W1S"), ("W1S", "T1S"), ("W1S", "A3"), ("W1S", "A1"), ("W1S", "A2"), ("W1S", "A6"),
             ("L1", "A1"), ("W1", "L1"), ("W1S", "W1"), ("O1", "W1"), ("O1S", "O1"), ("T1S", "A2"), ("O1S", "A3"),
             ("W1", "A3"), ("A3", "A1"), ("A2", "A1")]
    for tau in TAUS:
        for a, b in pairs:
            for name, sel in (("all", None), ("P1", lambda m: cohort[m] == "P1"), ("P3B", lambda m: cohort[m] == "P3B")):
                v = ratio(a, b, tau, sel)
                if v:
                    summ["ratios"][f"{a}/{b}_{tau:g}_{name}"] = med_ci(v, np.random.default_rng(SEED))
        for k in ("1", "2-8", "9-24", ">24"):
            lo, hi = {"1": (1, 1), "2-8": (2, 8), "9-24": (9, 24), ">24": (25, 10 ** 6)}[k]
            sel = lambda m, lo=lo, hi=hi: lo <= int(sym[m].get("ops", 1)) <= hi  # noqa: E731
            v = ratio("W1S", "W1", tau, sel)
            if v:
                summ["ratios"][f"W1S/W1_{tau:g}_ops{k}"] = med_ci(v, np.random.default_rng(SEED))
    summ["symmetry"] = {"ops_median": float(np.median([int(sym[m].get("ops", 1)) for m in mats])) if mats else None,
                        "with_symmetry": sum(int(sym[m].get("ops", 1)) > 1 for m in mats),
                        "status_counts": {s: sum(sym[m].get("status") == s for m in mats)
                                          for s in sorted({sym[m].get("status") for m in mats})}}
    R = summ["ratios"]
    g = lambda k: R.get(k, {})  # noqa: E731
    h1 = {t: g(f"O1S/W1S_{t:g}_all") for t in (1e-6, 1e-4)}
    summ["criteria"]["H1_closed_form_at_optimum"] = {
        "values": h1, "met": all(v and v["median"] <= 1.05 and v["ci95"][1] <= 1.08 for v in h1.values())}
    h2 = {t: g(f"W1S/T1S_{t:g}_all") for t in (1e-6, 1e-4)}
    summ["criteria"]["H2_waterfill_over_truncation"] = {
        "values": h2, "met": all(v and v["wins"] >= 0.9 * v["n"] for v in h2.values())}
    h3 = g("W1S/A3_1e-06_all")
    summ["criteria"]["H3_writer_over_A3"] = {"values": h3, "met": bool(h3 and h3["median"] > 1.3 and h3["ci95"][0] > 1.2)}
    full = all(summ["certified"][f"{a}_{t:g}"] == len(mats) for a in NEW for t in (1e-6, 1e-4))
    summ["criteria"]["validity"] = {"analyzable": len(mats), "all_W1_arms_certified_1e-6_1e-4": full,
                                    "met": len(mats) >= 90 and full}
    out.mkdir(parents=True, exist_ok=True)
    cols = ["material_id", "cohort", "system_type", "npoints", "raw_bytes", "arm", "tau", "certified", "param", "bytes",
            "cr", "hartree_hist", "hartree_safe", "shells_written", "seconds"]
    with (out / "rows.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    with (out / "materials.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["material_id", "cohort", "npoints", "spacegroup", "ops", "classes", "orbits", "symmetry_status",
                    "wall_seconds"] + [f"cr_{a}_{t:g}" for t in (1e-6, 1e-4) for a in NEW + OLD])
        for c in ok:
            m, s = c["material_id"], c.get("symmetry", {})
            w.writerow([m, c["cohort"], c["npoints"], s.get("spacegroup"), s.get("ops"), s.get("classes"), s.get("orbits"),
                        s.get("status"), round(c["wall_seconds"], 1)]
                       + [cr.get((m, a, t)) for t in (1e-6, 1e-4) for a in NEW + OLD])
    (out / "SUMMARY.json").write_text(json.dumps(summ, indent=1) + "\n", encoding="utf-8")
    return summ


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--checkpoints", type=Path, required=True)
    ap.add_argument("--repo-root", type=Path, default=HERE.parents[1])
    ap.add_argument("--out", type=Path, default=HERE / "results")
    a = ap.parse_args()
    s = aggregate(a.checkpoints, a.repo_root.resolve(), a.out)
    print(json.dumps(s["criteria"], indent=1))
