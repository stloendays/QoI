#!/usr/bin/env python3
"""Collect the per-slab shard outputs and compute the frozen statistics (PROTOCOL.md section 6)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vacuum_level as vl  # noqa: E402

ARMS = ("A1", "A2", "A3", "A5", "A6")
TAUS = (1e-6, 1e-4, 1e-8)


def many(root: Path, pattern: str) -> pd.DataFrame:
    xs = [pd.read_csv(p) for p in sorted(root.rglob(pattern)) if p.stat().st_size > 2]
    return pd.concat(xs, ignore_index=True) if xs else pd.DataFrame()


def truthy(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip().str.lower() == "true"


def summary_table(rows: pd.DataFrame, slabs: pd.DataFrame, ids: list) -> pd.DataFrame:
    out = []
    loaded = set(slabs.loc[slabs.status == "ok", "material_id"]) if len(slabs) else set()
    vac = set(slabs.loc[(slabs.status == "ok") & truthy(slabs.qualifies), "material_id"]) if len(slabs) else set()
    for tau in TAUS:
        for arm in ARMS:
            r = rows[(rows.arm == arm) & (rows.tau == tau)] if len(rows) else rows
            ev = r[truthy(r.evaluated)] if len(r) else r
            s = vl.summarize(ev.abs_dphi_meV) if len(ev) else vl.summarize([])
            m = vl.summarize(ev.max_abs_dV_window_meV) if len(ev) else vl.summarize([])
            def count(col, val=True):
                return int((truthy(r[col]) if val is True else (r[col] == val)).sum()) if len(r) and col in r else 0
            out.append({"tau": tau, "arm": arm, "n_planned": len(ids), "n_material_loaded": len(loaded),
                        "n_vacuum_qualifying": len(vac),
                        "n_streams_recorded": int((r.status != "no_certified_stream_recorded").sum()) if len(r) else 0,
                        "n_R_reproduced": count("R_reproduced"), "n_R_exact": count("R_exact"),
                        "n_S_reproduced": count("S_reproduced"), "n_S_exact": count("S_exact"),
                        "n_reproduced": count("reproduced"), "n_used_exact": count("exact"),
                        "n_used_via_R": count("route_used", "R"), "n_used_via_S": count("route_used", "S"),
                        "n_not_reproduced": count("status", "not_reproduced"),
                        "n_evaluated": s["n"], "median_abs_dphi_meV": s["median"], "p95_abs_dphi_meV": s["p95"],
                        "max_abs_dphi_meV": s["max"], "n_lt_1meV": s["n_lt_1meV"], "frac_lt_1meV": s["frac_lt_1meV"],
                        "n_lt_10meV": s["n_lt_10meV"], "frac_lt_10meV": s["frac_lt_10meV"],
                        "median_max_abs_dV_window_meV": m["median"], "max_max_abs_dV_window_meV": m["max"],
                        "median_tau_times_vref_meV": float(ev.tau_times_vref_meV.median()) if len(ev) else float("nan")})
    return pd.DataFrame(out)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--shards-root", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    a = p.parse_args()
    out = a.output_dir
    out.mkdir(parents=True, exist_ok=True)
    ids = pd.read_csv(a.manifest).material_id.tolist()
    slabs = many(a.shards_root, "slab_*.csv")
    rows = many(a.shards_root, "dphi_*.csv")
    fails = many(a.shards_root, "failures_*.csv")
    missing = [m for m in ids if not len(slabs) or m not in set(slabs.material_id)]
    if missing:
        extra = pd.DataFrame([{"material_id": m, "arm": "material", "tau": "", "error": "no shard output"} for m in missing])
        fails = pd.concat([fails, extra], ignore_index=True)
    order = {m: i for i, m in enumerate(ids)}
    if len(slabs):
        slabs = slabs.sort_values("material_id", key=lambda s: s.map(order)).reset_index(drop=True)
    if len(rows):
        rows["_o"] = rows.material_id.map(order)
        rows["_a"] = rows.arm.map({k: i for i, k in enumerate(ARMS)})
        rows = rows.sort_values(["_o", "_a", "tau"], ascending=[True, True, False]).drop(columns=["_o", "_a"])
    slabs.to_csv(out / "slabs.csv", index=False)
    rows.to_csv(out / "per_slab_dphi.csv", index=False)
    fails.to_csv(out / "failures.csv", index=False)
    summ = summary_table(rows, slabs, ids)
    summ.to_csv(out / "summary.csv", index=False)
    s = {"status": "COMPLETE", "planned": len(ids), "slab_rows": int(len(slabs)), "stream_rows": int(len(rows)),
         "failure_rows": int(len(fails)), "missing_materials": missing,
         "non_qualifying_vacuum": slabs.loc[(slabs.status == "ok") & ~truthy(slabs.qualifies), "material_id"].tolist() if len(slabs) else [],
         "summary": summ.to_dict(orient="records")}
    (out / "SUMMARY.json").write_text(json.dumps(s, indent=2), encoding="utf-8")
    print(summ[["tau", "arm", "n_reproduced", "n_evaluated"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
