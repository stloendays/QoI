#!/usr/bin/env python3
"""Aggregate the shard outputs of run_joint_v2.py (descriptive only; no pass/fail gates).

Writes to --output-dir:
    joint_v2_material.csv   one row per (material, base, post): certified CR, Bader attempts, Bader error,
                            reassignment, Hartree errors before/after the stored post-processing, and the ratio
                            of the certified CR to the best certified CR among the other base codecs with the
                            same post-processor
    SUMMARY.json            per (base, post): number certified, median certified CR, median of that ratio
    rows.csv.gz, bader_attempts.csv, selected.csv, failures.csv, materials.csv   concatenated shard outputs

Ratio convention (as in analysis/qoac_hb_joint/aggregate_joint.py): the ratio is defined on materials where the
base certifies; if no other base certifies that material with the same post-processor the ratio is +inf in the
CSV and enters the median as SOLE_CERTIFIER_RATIO.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

KEY = ["material_id", "base", "post"]
SOLE_CERTIFIER_RATIO = 1e9
SHARD_FILES = ("rows", "bader", "selected", "failures", "materials")
TEXT = {c: str for c in ("material_id", "base", "post", "param", "stored", "status")}


def read_shards(root: Path, name: str) -> pd.DataFrame:
    parts = []
    for p in sorted(root.rglob(f"{name}_shard_*.csv")):
        d = pd.read_csv(p, dtype=TEXT)
        d = d[d["material_id"].notna() & (d["material_id"] != "")]
        if len(d):
            parts.append(d)
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=["material_id"])


def as_bool(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip().str.lower() == "true"


def ordered_unique(values) -> list:
    return list(dict.fromkeys(v for v in values if isinstance(v, str)))


def median_or_none(x: np.ndarray):
    return float(np.median(x)) if x.size else None


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--shards-root", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    a = p.parse_args(argv)
    out = a.output_dir
    out.mkdir(parents=True, exist_ok=True)

    man = pd.read_csv(a.manifest, dtype={"material_id": str})
    d = {name: read_shards(a.shards_root, name) for name in SHARD_FILES}
    mats, sel, bad, rows = d["materials"], d["selected"], d["bader"], d["rows"]

    # population bookkeeping
    seen = mats["material_id"].tolist()
    if len(seen) != len(set(seen)):
        raise RuntimeError(f"material reported by more than one shard: {sorted({m for m in seen if seen.count(m) > 1})}")
    extra = sorted(set(seen) - set(man["material_id"]))
    if extra:
        raise RuntimeError(f"shard outputs contain materials outside the manifest: {extra}")
    status = dict(zip(mats["material_id"], mats["status"])) if "status" in mats else {}
    missing = [m for m in man["material_id"] if m not in status]
    failed = [m for m in man["material_id"] if m in status and status[m] != "SUCCESS"]

    rows.to_csv(out / "rows.csv.gz", index=False, compression={"method": "gzip", "mtime": 0})
    for name, df in (("bader_attempts", bad), ("selected", sel), ("failures", d["failures"]), ("materials", mats)):
        df.to_csv(out / f"{name}.csv", index=False)

    bases = ordered_unique(sel.get("base", []))
    posts = ordered_unique(sel.get("post", []))

    # one row per (material, base, post) over the whole manifest
    grid = pd.DataFrame([(m, b, q) for m in man["material_id"] for b in bases for q in posts], columns=KEY)
    grid = grid.merge(man[["material_id", "system_type"]], on="material_id", how="left")
    grid.insert(2, "material_status", [status.get(m, "MISSING") for m in grid["material_id"]])

    sel_cols = ["certified", "attempts", "n_hartree_pass", "param", "stored", "ctp_decision", "compression_ratio",
                "total_bytes", "extra_fraction", "bader_error_e", "hartree_hist", "hartree_safe", "density_Linf"]
    s = sel.reindex(columns=KEY + sel_cols).copy()
    s["certified"] = as_bool(s["certified"])
    s.loc[~s["certified"], "compression_ratio"] = np.nan
    M = grid.merge(s, on=KEY, how="left")
    M["certified"] = M["certified"].eq(True)

    # certified Bader attempt: reassignment and the unprojected control
    bcols = ["reassigned_frac", "unprojected_bader_error_e", "unprojected_reassigned_frac", "attempt"]
    b = bad.reindex(columns=KEY + ["certified"] + bcols).copy()
    b = b[as_bool(b["certified"])].drop(columns="certified").rename(columns={"attempt": "certified_attempt"})
    if b.duplicated(KEY).any():
        raise RuntimeError("more than one certified Bader attempt for a (material, base, post)")
    M = M.merge(b, on=KEY, how="left")

    # pre-projection Hartree errors, closure and density errors of the certified (param, stored) row
    rcols = ["hartree_hist_pre", "hartree_safe_pre", "closure_scaled", "density_RMSE", "payload_bytes", "extra_bytes"]
    r = rows.reindex(columns=KEY + ["param", "stored"] + rcols)
    n = len(M)
    M = M.merge(r, on=KEY + ["param", "stored"], how="left")
    if len(M) != n:
        raise RuntimeError("duplicate (material, base, post, param, stored) rows in rows_shard_*.csv")
    for c in rcols:
        M.loc[~M["certified"], c] = np.nan

    # CR relative to the best other base codec with the same post-processor
    cr = M.pivot_table(index=["material_id", "post"], columns="base", values="compression_ratio", aggfunc="first")
    cr = cr.reindex(columns=bases)
    best_other = []
    for m, q, bname in zip(M["material_id"], M["post"], M["base"]):
        others = cr.loc[(m, q)].drop(labels=bname) if (m, q) in cr.index else pd.Series(dtype=float)
        best_other.append(float(others.max()) if others.notna().any() else np.nan)
    M["best_other_cr"] = best_other
    M["cr_ratio_vs_best_other"] = np.where(
        M["compression_ratio"].notna() & M["best_other_cr"].notna(), M["compression_ratio"] / M["best_other_cr"],
        np.where(M["compression_ratio"].notna(), np.inf, np.nan))

    order = ["material_id", "system_type", "material_status", "base", "post", "certified", "compression_ratio",
             "attempts", "certified_attempt", "n_hartree_pass", "param", "stored", "ctp_decision", "bader_error_e",
             "reassigned_frac", "unprojected_bader_error_e", "unprojected_reassigned_frac", "hartree_hist_pre",
             "hartree_safe_pre", "hartree_hist", "hartree_safe", "closure_scaled", "density_Linf", "density_RMSE",
             "payload_bytes", "extra_bytes", "total_bytes", "extra_fraction", "best_other_cr", "cr_ratio_vs_best_other"]
    M = M[order]
    M.to_csv(out / "joint_v2_material.csv", index=False)

    by = {}
    for bname in bases:
        by[bname] = {}
        for q in posts:
            g = M[(M["base"] == bname) & (M["post"] == q)]
            c = g.loc[g["certified"], "compression_ratio"].to_numpy(float)
            rr = g["cr_ratio_vs_best_other"].dropna().to_numpy(float)
            by[bname][q] = {
                "n_certified": int(g["certified"].sum()),
                "median_cr": median_or_none(c),
                "cr_ratio_vs_best_other": {
                    "n": int(rr.size),
                    "n_sole_certifier": int(np.isinf(rr).sum()),
                    "median": median_or_none(np.where(np.isfinite(rr), rr, SOLE_CERTIFIER_RATIO)),
                },
            }
    summary = {
        "status": "COMPLETE" if not missing else "INCOMPLETE",
        "manifest": str(a.manifest).replace("\\", "/"),
        "manifest_sha256": hashlib.sha256(a.manifest.read_bytes()).hexdigest(),
        "materials": int(len(man)),
        "materials_success": int(sum(v == "SUCCESS" for v in status.values())),
        "materials_failed": failed,
        "materials_missing": missing,
        "setting_failures": int(len(d["failures"])),
        "bases": bases,
        "posts": posts,
        "cr_ratio_definition": ("certified CR / max certified CR of the other base codecs with the same post-processor, "
                                "over materials where the base certifies; sole certifier = inf, entered in the median "
                                f"as {SOLE_CERTIFIER_RATIO:g}"),
        "by_base_post": by,
    }
    (out / "SUMMARY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "by_base_post"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
