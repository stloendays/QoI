#!/usr/bin/env python3
"""Aggregate study 3: per-material rows, recorded law-protocol arms and revision 11's W1S rows, criteria G1-G2,
the reproduction check and descriptive ratios."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
TAUS = (1e-6, 1e-4)
NEW = ("W1S", "W2S", "W2", "O2S")
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


def rev11_w1s(repo: Path) -> dict:
    out = {}
    for r in csv.DictReader(open(repo / "analysis/waterfill_writer_20261025/results/rows.csv", encoding="utf-8")):
        if r["arm"] == "W1S" and r["certified"] == "True":
            out[(r["material_id"], float(r["tau"]))] = int(r["bytes"])
    return out


def med_ci(v, rng):
    v = np.asarray(v, float)
    b = np.median(rng.choice(v, size=(NBOOT, v.size), replace=True), axis=1)
    return {"median": float(np.median(v)), "ci95": [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))],
            "n": int(v.size), "min": float(v.min()), "max": float(v.max()), "wins": int(np.sum(v > 1.0))}


def aggregate(ckpt: Path, repo: Path, out: Path) -> dict:
    rec = recorded(repo)
    r11 = rev11_w1s(repo)
    cks = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(ckpt.glob("*.json"))]
    man = {}
    for c, f in (("P1", "P1_CONFIRMATORY_MANIFEST.csv"), ("P3B", "P3B_CONFIRMATORY_MANIFEST.csv")):
        for r in csv.DictReader(open(repo / "analysis/fresh_population_20261006" / f, encoding="utf-8")):
            man[r["material_id"]] = c
    cks = [c for c in cks if c["material_id"] in man]
    ok = [c for c in cks if c["status"] == "SUCCESS"]
    rows, cr, by = [], {}, {}
    for c in ok:
        mid = c["material_id"]
        for r in c["rows"]:
            rows.append(r)
            if r["certified"]:
                cr[(mid, r["arm"], float(r["tau"]))] = float(r["cr"])
                by[(mid, r["arm"], float(r["tau"]))] = r
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
        return [cr[(m, a, tau)] / cr[(m, b, tau)] for m in mats if (m, a, tau) in cr and (m, b, tau) in cr
                and (sel is None or sel(m))]

    summ = {"materials_checkpointed": len(cks), "materials_success": len(ok), "seed": SEED, "resamples": NBOOT,
            "failed": [c["material_id"] for c in cks if c["status"] != "SUCCESS"], "criteria": {}, "ratios": {},
            "certified": {}, "variants": {}, "reproduction": {}, "sfp": {}}
    for arm in NEW:
        for tau in TAUS:
            summ["certified"][f"{arm}_{tau:g}"] = sum((m, arm, tau) in cr for m in mats)
    pairs = [("W2S", "W1S"), ("O2S", "W2S"), ("W2S", "A3"), ("W2S", "A1"), ("W2S", "A2"), ("W2S", "A6"),
             ("W2", "W1S"), ("W2S", "W2"), ("O2S", "A3")]
    for tau in TAUS:
        for a, b in pairs:
            for name, sel in (("all", None), ("P1", lambda m: cohort[m] == "P1"), ("P3B", lambda m: cohort[m] == "P3B")):
                v = ratio(a, b, tau, sel)
                if v:
                    summ["ratios"][f"{a}/{b}_{tau:g}_{name}"] = med_ci(v, np.random.default_rng(SEED))
        for k in ("1", "2-8", "9-24", ">24"):
            lo, hi = {"1": (1, 1), "2-8": (2, 8), "9-24": (9, 24), ">24": (25, 10 ** 6)}[k]
            sel = lambda m, lo=lo, hi=hi: lo <= int(sym[m].get("ops", 1)) <= hi  # noqa: E731
            v = ratio("W2S", "W1S", tau, sel)
            if v:
                summ["ratios"][f"W2S/W1S_{tau:g}_ops{k}"] = med_ci(v, np.random.default_rng(SEED))
        vs = [by[(m, "W2S", tau)].get("variant") for m in mats if (m, "W2S", tau) in by]
        summ["variants"][f"{tau:g}"] = {v: vs.count(v) for v in sorted(set(vs))}
        same = [m for m in mats if (m, "W1S", tau) in by and (m, tau) in r11
                and int(by[(m, "W1S", tau)]["bytes"]) == r11[(m, tau)]]
        summ["reproduction"][f"W1S_equals_rev11_{tau:g}"] = {"equal": len(same), "of": len(mats)}
    ns = [c.get("sfp_shells", 0) for c in ok]
    summ["sfp"] = {"materials_with_prediction": sum(n > 0 for n in ns), "shells_median": float(np.median(ns)) if ns else None,
                   "block_bytes_median": float(np.median([c.get("sfp_block_bytes", 0) for c in ok])) if ok else None}
    R = summ["ratios"]
    g = lambda k: R.get(k, {})  # noqa: E731
    g1 = g("W2S/W1S_1e-06_all")
    summ["criteria"]["G1_prediction_gain"] = {"values": g1,
                                              "met": bool(g1 and g1["median"] >= 1.15 and g1["ci95"][0] >= 1.10)}
    g2 = {t: g(f"O2S/W2S_{t:g}_all") for t in TAUS}
    summ["criteria"]["G2_closed_form_at_optimum_with_prediction"] = {
        "values": g2, "met": all(v and v["median"] <= 1.05 and v["ci95"][1] <= 1.08 for v in g2.values())}
    full = all(summ["certified"][f"{a}_{t:g}"] == len(mats) for a in NEW for t in TAUS)
    rep = all(summ["reproduction"][f"W1S_equals_rev11_{t:g}"]["equal"] >= len(mats) - 2 for t in TAUS)
    summ["criteria"]["validity"] = {"analyzable": len(mats), "all_arms_certified": full, "w1s_reproduces_rev11": rep,
                                    "met": len(mats) >= 90 and full and rep}
    out.mkdir(parents=True, exist_ok=True)
    cols = ["material_id", "cohort", "system_type", "npoints", "raw_bytes", "arm", "tau", "certified", "param", "bytes",
            "cr", "hartree_hist", "hartree_safe", "shells_written", "variant", "sfp_shells_used", "w1s_bytes", "seconds"]
    with (out / "rows.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    with (out / "materials.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["material_id", "cohort", "npoints", "natoms", "nspecies", "spacegroup", "ops", "sfp_shells",
                    "sfp_block_bytes", "wall_seconds"] + [f"cr_{a}_{t:g}" for t in TAUS for a in NEW + OLD])
        for c in ok:
            m, s = c["material_id"], c.get("symmetry", {})
            w.writerow([m, c["cohort"], c["npoints"], c.get("natoms"), c.get("nspecies"), s.get("spacegroup"),
                        s.get("ops"), c.get("sfp_shells"), c.get("sfp_block_bytes"), round(c["wall_seconds"], 1)]
                       + [cr.get((m, a, t)) for t in TAUS for a in NEW + OLD])
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
