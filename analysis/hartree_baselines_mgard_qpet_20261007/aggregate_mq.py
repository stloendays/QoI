#!/usr/bin/env python3
"""Aggregate the M/Q strongest-baseline arms against the recorded law arms A1/A2/A3/A6 (see PROTOCOL.md).

Descriptive record, no pass/fail gate. Ratio medians follow `analysis/general_qoac_law/aggregate_law.py`: a ratio is
defined only where both arms certified (undefined ratios are dropped); the bootstrap is `aggregate_law.boot` (fixed
seed 20261006, 10,000 resamples over materials, a fresh generator per statistic, percentile 95% interval).
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "general_qoac_law"))
sys.path.insert(0, str(HERE))
from aggregate_law import boot  # noqa: E402
import codecs_mq as C  # noqa: E402

TAUS = (1e-6, 1e-4, 1e-8)   # report order: primary first
LAW = "analysis/general_qoac_law/results"
FRESH = "analysis/fresh_population_20261006"
COHORTS = {"P1_CONFIRMATORY": f"{FRESH}/P1_CONFIRMATORY_MANIFEST.csv",
           "P3B_CONFIRMATORY": f"{FRESH}/P3B_CONFIRMATORY_MANIFEST.csv"}
RATIOS = (("A1", "M2"), ("A1", "Mbest"), ("A1", "Q"), ("A3", "M2"), ("A3", "Q"))
PRIMARY_ARMS = ("A1", "A2", "A3", "A6", "M2", "Mbest", "Q")
M_COLS = [f"M_s={s}" for s in C.MGARD_S]
Q_COLS = [f"Q_{h}_b{b}" for h in C.QPET_HOSTS for b in C.QPET_BLOCKS]
ARM_CONFIGS = {"M2": ["M_s=-2"], "Mbest": M_COLS, "Q": Q_COLS}


def many(root: Path, pat: str) -> pd.DataFrame:
    xs = [pd.read_csv(p) for p in sorted(Path(root).rglob(pat)) if p.stat().st_size > 2]
    return pd.concat(xs, ignore_index=True) if xs else pd.DataFrame()


def truthy(s: pd.Series) -> pd.Series:
    return s.astype(str).str.lower() == "true"


def wide_table(rows: pd.DataFrame, law: pd.DataFrame, ids: list[str], m2_feasible: bool = True) -> pd.DataFrame:
    """One row per (material, tau): certified CR of every config and arm (NaN = not certified or not run)."""
    idx = pd.MultiIndex.from_product([ids, sorted(set(TAUS))], names=["material_id", "tau"])
    out = pd.DataFrame(index=idx)
    if len(rows):
        c = rows[truthy(rows.certified)]
        cr = c.groupby(["material_id", "tau", "config"]).cr.max().unstack("config")
        out = out.join(cr, how="left")
    for col in M_COLS + Q_COLS:
        if col not in out:
            out[col] = np.nan
    lw = law.set_index(["material_id", "tau"])[["A1", "A2", "A3", "A6"]]
    out = out.join(lw, how="left")
    out["M2"] = out["M_s=-2"] if m2_feasible else np.nan
    mb = M_COLS if m2_feasible else [c for c in M_COLS if c != "M_s=-2"]
    out["Mbest"] = out[mb].max(axis=1, skipna=True)
    for h in C.QPET_HOSTS:
        out[f"Q_{h}"] = out[[f"Q_{h}_b{b}" for b in C.QPET_BLOCKS]].max(axis=1, skipna=True)
    out["Q"] = out[Q_COLS].max(axis=1, skipna=True)
    return out


def ran_table(rows: pd.DataFrame, ids: list[str]) -> pd.DataFrame:
    """Whether each arm's search ran (a result row exists) for every config of the arm at (material, tau)."""
    idx = pd.MultiIndex.from_product([ids, sorted(set(TAUS))], names=["material_id", "tau"])
    out = pd.DataFrame(index=idx)
    have = set()
    if len(rows):
        have = set(zip(rows.material_id, rows.tau, rows.config))
    for arm, cols in ARM_CONFIGS.items():
        out[arm] = [all((m, t, c) in have for c in cols) for m, t in idx]
    return out


def ratio_stats(tab: pd.DataFrame, ran: pd.DataFrame, num: str, den: str) -> dict:
    t = tab
    both = t[num].notna() & t[den].notna()
    r = (t[num] / t[den])[both]
    never = int((t[num].notna() & t[den].isna() & ran[den]).sum()) if den in ran else 0
    not_run = int((t[num].notna() & t[den].isna() & ~ran[den]).sum()) if den in ran else int((t[den].isna()).sum())
    wins = int((r > 1).sum())
    return {"n_both_certified": int(r.size), "wins": wins, "baseline_never_certified": never,
            "wins_incl_never_certified": wins + never, "baseline_not_run": not_run,
            "numerator_not_certified": int(t[num].isna().sum()),
            "median": float(r.median()) if r.size else None, "ci95": boot(r) if r.size else None,
            "min": float(r.min()) if r.size else None, "max": float(r.max()) if r.size else None}


def arm_medians(tab: pd.DataFrame) -> dict:
    cols = list(PRIMARY_ARMS) + M_COLS + [f"Q_{h}" for h in C.QPET_HOSTS] + Q_COLS
    return {c: {"n_certified": int(tab[c].notna().sum()), "median_cr": float(tab[c].median()) if tab[c].notna().any() else None}
            for c in cols}


def fail_time(rows: pd.DataFrame, evals: pd.DataFrame, fails: pd.DataFrame, ids: list[str]) -> dict:
    out = {}
    for arm, cols in ARM_CONFIGS.items():
        d = {}
        ev = evals[evals.material_id.isin(ids) & evals.config.isin(cols)] if len(evals) else evals
        fl = fails[fails.material_id.isin(ids) & fails.config.isin(cols)] if len(fails) else fails
        d["evaluations"] = int(len(ev))
        d["failed_evaluations"] = int(len(fl))
        d["materials_with_failed_evaluations"] = int(fl.material_id.nunique()) if len(fl) else 0
        d["failure_examples"] = sorted(set(fl.error.astype(str).str[:160]))[:5] if len(fl) else []
        rr = rows[rows.material_id.isin(ids) & rows.config.isin(cols)] if len(rows) else rows
        per = {}
        for tau in TAUS:
            s = rr[rr.tau == tau].groupby("material_id").search_seconds.sum() if len(rr) else pd.Series(dtype=float)
            per[f"tau_{tau:g}"] = {"median_seconds_per_material": float(s.median()) if len(s) else None,
                                   "total_hours": float(s.sum() / 3600) if len(s) else 0.0}
        d["search_wall_time"] = per
        d["codec_plus_certificate_hours"] = float(ev.seconds.sum() / 3600) if len(ev) else 0.0
        d["searches"] = int(len(rr))
        d["searches_codec_never_executed"] = int((rr.lo_decades_skipped == -1).sum()) if len(rr) else 0
        d["searches_lower_bound_raised"] = int((rr.lo_decades_skipped > 0).sum()) if len(rr) else 0
        out[arm] = d
    if len(fails):
        mf = fails[fails.material_id.isin(ids) & (fails.arm.astype(str) == "material")]
        out["material_level_failures"] = sorted(mf.material_id.unique().tolist())
    else:
        out["material_level_failures"] = []
    return out


def cohort(name: str, repo: Path, rows, evals, fails, m2_feasible: bool, outdir: Path) -> dict:
    ids = pd.read_csv(repo / COHORTS[name]).material_id.tolist()
    law = pd.read_csv(repo / LAW / f"run_{name}" / "part_a_material.csv")
    law = law[law.material_id.isin(ids)]
    r = rows[rows.material_id.isin(ids)] if len(rows) else rows
    tab = wide_table(r, law, ids, m2_feasible)
    ran = ran_table(r, ids)
    od = outdir / f"run_{name}"; od.mkdir(parents=True, exist_ok=True)
    tab.reset_index().to_csv(od / "material.csv", index=False)
    if len(r):
        r.to_csv(od / "rows.csv", index=False)
    if len(evals):
        evals[evals.material_id.isin(ids)].to_csv(od / "evals.csv.gz", index=False, compression="gzip")
    if len(fails):
        fails[fails.material_id.isin(ids)].to_csv(od / "failures.csv", index=False)
    s = {"materials": len(ids), "materials_with_rows": int(r.material_id.nunique()) if len(r) else 0}
    for tau in TAUS:
        tt = tab.xs(tau, level="tau"); rt = ran.xs(tau, level="tau")
        s[f"tau_{tau:g}"] = {"median_cr": arm_medians(tt),
                             "ratios": {f"{a}_over_{b}": (ratio_stats(tt, rt, a, b) if (b != "M2" or m2_feasible)
                                                          else {"M2_infeasible": True}) for a, b in RATIOS}}
    s["failures_and_wall_time"] = fail_time(r, evals, fails, ids)
    (od / "SUMMARY.json").write_text(json.dumps(s, indent=2), encoding="utf-8")
    return s


def m2_feasibility(shards: Path) -> tuple[bool, str]:
    ps = list(shards.rglob("probe.json"))
    if not ps:
        return True, "probe.json not found; M2 treated as attempted"
    p = json.loads(ps[0].read_text(encoding="utf-8"))
    f = p.get("mgard_tiny", {}).get("-2", {})
    return bool(f.get("feasible", False)), json.dumps(f)[:600]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--shards-root", type=Path, required=True)
    ap.add_argument("--phase", required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    a = ap.parse_args()
    rows = many(a.shards_root, "rows_*.csv"); evals = many(a.shards_root, "evals_*.csv"); fails = many(a.shards_root, "failures_*.csv")
    infos = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(a.shards_root.rglob("info_*.json"))]
    out = a.output_dir / ("probe" if a.phase == "probe" else ".")
    out.mkdir(parents=True, exist_ok=True)
    tc = out / "toolchain"; tc.mkdir(exist_ok=True)
    for p in a.shards_root.rglob("*"):
        if p.is_file() and p.parent.name.startswith("hbmq-probe"):
            shutil.copy(p, tc / p.name)
    feasible, why = m2_feasibility(a.shards_root)
    summary = {"phase": a.phase, "m2_feasible": feasible, "m2_probe": why, "material_info": infos}
    if a.phase == "probe":
        for name, d in (("rows", rows), ("evals", evals), ("failures", fails)):
            if len(d):
                d.to_csv(out / f"shakedown_{name}.csv", index=False)
        (out / "SUMMARY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(json.dumps({"rows": len(rows), "evals": len(evals), "failures": len(fails), "m2_feasible": feasible}))
        return 0
    for name in COHORTS:
        summary[name] = cohort(name, a.repo_root, rows, evals, fails, feasible, out)
    (out / "SUMMARY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k]["materials_with_rows"] for k in COHORTS}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
