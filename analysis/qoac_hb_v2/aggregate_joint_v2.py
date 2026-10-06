#!/usr/bin/env python3
"""Aggregate the shard outputs of run_joint_v2.py (descriptive only; no pass/fail gates).

Everything is reported separately for every Bader tolerance tau_B found in the shard outputs. The pseudo
post-processor `hartree_only` (best Hartree-certified unprojected row, no Bader requirement, no side channel) is
the reference for the joint overhead; every other post-processor is a joint (Hartree + Bader) post-processor.

Writes to --output-dir:
    joint_v2_material.csv   one row per (material, base, post, tau_B): certified CR, Bader attempts, Bader error,
                            reassignment, Hartree errors before/after the stored post-processing, the ratio of the
                            certified CR to the best certified CR among the other base codecs with the same
                            post-processor, the joint overhead CR_hartree_only / CR_joint, and for rows that
                            store a HAP projection the HAP / uniform Hartree-error ratios of the same row
    joint_v2_best_post.csv  one row per (material, base, tau_B): best joint CR over the joint post-processors,
                            the post-processor achieving it, and its ratio to the best other base codec
    SUMMARY.json            per tau_B (key `by_tau`), see `summarize`
    rows.csv.gz, bader_attempts.csv, selected.csv, failures.csv, materials.csv   concatenated shard outputs

Ratio convention (as in analysis/qoac_hb_joint/aggregate_joint.py): a CR ratio is defined on materials where
the numerator base certifies; if no other base certifies that material the ratio is +inf in the CSV and enters
the median as SOLE_CERTIFIER_RATIO.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

HARTREE_ONLY = "hartree_only"
FOCUS_BASE = "R3"
KEY = ["material_id", "base", "post", "tau_bader"]
SOLE_CERTIFIER_RATIO = 1e9
SHARD_FILES = ("rows", "bader", "selected", "failures", "materials")
TEXT = {c: str for c in ("material_id", "base", "post", "param", "stored", "status", "ctp_decision")}


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


def median_or_none(x) -> float | None:
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    return float(np.median(x)) if x.size else None


def tau_label(t) -> str:
    return f"{float(t):g}"


def ratio_vs_best_other(df: pd.DataFrame, by: list[str], value: str) -> tuple[np.ndarray, np.ndarray]:
    """(best other base value, value / best other) for each row of df; df has one row per (by..., base)."""
    piv = df.pivot_table(index=by, columns="base", values=value, aggfunc="first")
    best_other = np.full(len(df), np.nan)
    for i, (idx, b) in enumerate(zip(df[by].itertuples(index=False, name=None), df["base"])):
        idx = idx if len(by) > 1 else idx[0]
        if idx in piv.index:
            others = piv.loc[idx].drop(labels=b, errors="ignore")
            if others.notna().any():
                best_other[i] = float(others.max())
    v = df[value].to_numpy(float)
    ratio = np.where(~np.isnan(v) & ~np.isnan(best_other), v / np.where(np.isnan(best_other), 1.0, best_other),
                     np.where(~np.isnan(v), np.inf, np.nan))
    return best_other, ratio


def ratio_stats(r) -> dict:
    r = np.asarray(r, dtype=float)
    r = r[~np.isnan(r)]
    return {"n": int(r.size), "n_sole_certifier": int(np.isinf(r).sum()),
            "median": median_or_none(np.where(np.isfinite(r), r, SOLE_CERTIFIER_RATIO))}


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

    if len(sel) and "tau_bader" not in sel:
        raise RuntimeError("selected_shard_*.csv has no tau_bader column (pre-tau_B runner output)")
    for df in (sel, bad):
        if "tau_bader" in df:
            df["tau_bader"] = df["tau_bader"].map(tau_label)
    bases = ordered_unique(sel.get("base", []))
    posts = ordered_unique(sel.get("post", []))
    joint_posts = [q for q in posts if q != HARTREE_ONLY]
    taus = sorted(ordered_unique(sel.get("tau_bader", [])), key=float, reverse=True)

    # one row per (material, base, post, tau_B) over the whole manifest
    grid = pd.DataFrame([(m, b, q, t) for m in man["material_id"] for b in bases for q in posts for t in taus],
                        columns=KEY)
    grid = grid.merge(man[["material_id", "system_type"]], on="material_id", how="left")
    grid.insert(2, "material_status", [status.get(m, "MISSING") for m in grid["material_id"]])

    sel_cols = ["certified", "attempts", "n_hartree_pass", "param", "stored", "ctp_decision", "compression_ratio",
                "total_bytes", "extra_fraction", "bader_error_e", "hartree_hist", "hartree_safe", "density_Linf"]
    s = sel.reindex(columns=KEY + sel_cols).copy()
    if s.duplicated(KEY).any():
        raise RuntimeError("duplicate (material, base, post, tau_B) rows in selected_shard_*.csv")
    s["certified"] = as_bool(s["certified"])
    s["compression_ratio"] = pd.to_numeric(s["compression_ratio"], errors="coerce")
    s.loc[~s["certified"], "compression_ratio"] = np.nan
    M = grid.merge(s, on=KEY, how="left")
    M["certified"] = M["certified"].eq(True)

    # certified Bader attempt: reassignment and the unprojected control
    bcols = ["reassigned_frac", "unprojected_bader_error_e", "unprojected_reassigned_frac", "attempt"]
    b = bad.reindex(columns=KEY + ["certified"] + bcols).copy()
    b = b[as_bool(b["certified"])].drop(columns="certified").rename(columns={"attempt": "certified_attempt"})
    if b.duplicated(KEY).any():
        raise RuntimeError("more than one certified Bader attempt for a (material, base, post, tau_B)")
    M = M.merge(b, on=KEY, how="left")

    # pre-projection Hartree errors, closure and density errors of the certified (param, stored) row;
    # hartree_only rows are the `none` rows of the runner
    rcols = ["hartree_hist_pre", "hartree_safe_pre", "closure_scaled", "density_RMSE", "payload_bytes", "extra_bytes"]
    r = rows.reindex(columns=["material_id", "base", "post", "param", "stored"] + rcols).rename(columns={"post": "rows_post"})
    M["rows_post"] = M["post"].where(M["post"] != HARTREE_ONLY, "none")
    n = len(M)
    M = M.merge(r, on=["material_id", "base", "rows_post", "param", "stored"], how="left")
    if len(M) != n:
        raise RuntimeError("duplicate (material, base, post, param, stored) rows in rows_shard_*.csv")
    M = M.drop(columns="rows_post")
    for c in rcols:
        M.loc[~M["certified"], c] = np.nan

    # HAP vs uniform Hartree error of the same decoded row (only rows that store a HAP projection)
    uni = rows[rows["stored"] == "uniform"].drop_duplicates(["material_id", "base", "param"])
    uni = uni.reindex(columns=["material_id", "base", "param", "hartree_hist", "hartree_safe"]).rename(
        columns={"hartree_hist": "uniform_hartree_hist", "hartree_safe": "uniform_hartree_safe"})
    M = M.merge(uni, on=["material_id", "base", "param"], how="left")
    is_hap = M["certified"] & M["stored"].fillna("").str.startswith("hap:")
    for k in ("hist", "safe"):
        num = pd.to_numeric(M[f"hartree_{k}"], errors="coerce")
        den = pd.to_numeric(M[f"uniform_hartree_{k}"], errors="coerce")
        M[f"hap_over_uniform_hartree_{k}"] = np.where(is_hap & (den > 0), num / den, np.nan)
        M.loc[~is_hap, f"uniform_hartree_{k}"] = np.nan

    # CR relative to the best other base codec with the same post-processor (and tau_B)
    M["best_other_cr"], M["cr_ratio_vs_best_other"] = ratio_vs_best_other(
        M, ["material_id", "post", "tau_bader"], "compression_ratio")

    # joint overhead: CR_hartree_only / CR_joint of the same (material, base, tau_B)
    ho = M[M["post"] == HARTREE_ONLY].set_index(["material_id", "base", "tau_bader"])["compression_ratio"]
    M["hartree_only_cr"] = [ho.get(k, np.nan) for k in zip(M["material_id"], M["base"], M["tau_bader"])]
    M["joint_overhead"] = np.where(M["post"] != HARTREE_ONLY, M["hartree_only_cr"] / M["compression_ratio"], np.nan)

    order = ["material_id", "system_type", "material_status", "tau_bader", "base", "post", "certified",
             "compression_ratio", "attempts", "certified_attempt", "n_hartree_pass", "param", "stored", "ctp_decision",
             "bader_error_e", "reassigned_frac", "unprojected_bader_error_e", "unprojected_reassigned_frac",
             "hartree_hist_pre", "hartree_safe_pre", "hartree_hist", "hartree_safe", "uniform_hartree_hist",
             "uniform_hartree_safe", "hap_over_uniform_hartree_hist", "hap_over_uniform_hartree_safe",
             "closure_scaled", "density_Linf", "density_RMSE", "payload_bytes", "extra_bytes", "total_bytes",
             "extra_fraction", "best_other_cr", "cr_ratio_vs_best_other", "hartree_only_cr", "joint_overhead"]
    M = M[order]
    M.to_csv(out / "joint_v2_material.csv", index=False)

    # best joint post-processor per (material, base, tau_B)
    J = M[M["post"].isin(joint_posts)]
    best = []
    for (m, bname, t), g in J.groupby(["material_id", "base", "tau_bader"], sort=False):
        c = g["compression_ratio"]
        i = c.idxmax() if c.notna().any() else None
        best.append({"material_id": m, "base": bname, "tau_bader": t,
                     "best_joint_post": g.at[i, "post"] if i is not None else "",
                     "best_joint_cr": float(c[i]) if i is not None else np.nan,
                     "hartree_only_cr": float(g["hartree_only_cr"].iloc[0])})
    B = pd.DataFrame(best, columns=["material_id", "base", "tau_bader", "best_joint_post", "best_joint_cr",
                                    "hartree_only_cr"])
    B["joint_overhead"] = B["hartree_only_cr"] / B["best_joint_cr"]
    B["best_other_cr"], B["cr_ratio_vs_best_other"] = ratio_vs_best_other(B, ["material_id", "tau_bader"],
                                                                           "best_joint_cr")
    B.to_csv(out / "joint_v2_best_post.csv", index=False)

    by_tau = {t: summarize(M[M["tau_bader"] == t], B[B["tau_bader"] == t], bad, t, bases, posts, joint_posts)
              for t in taus}
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
        "tau_bader": taus,
        "definitions": {
            "cr_ratio_vs_best_other": ("certified CR / max certified CR of the other base codecs with the same "
                                       "post-processor and tau_B, over materials where the base certifies; sole "
                                       f"certifier = inf, entered in the median as {SOLE_CERTIFIER_RATIO:g}"),
            "joint_overhead": ("CR_hartree_only / CR_joint for the same (material, base, tau_B), over materials "
                               "where both certify; hartree_only = best Hartree-certified unprojected row with no "
                               "Bader requirement and no side channel"),
            "focus_vs_others_same_post": (f"best {FOCUS_BASE} joint CR / best joint CR of the other bases with the "
                                          "same post-processor (= cr_ratio_vs_best_other of the focus base)"),
            "focus_vs_others_best_post": (f"{FOCUS_BASE} CR at its best joint post-processor / max over the other "
                                          "bases of their CR at their own best joint post-processor"),
            "ctp_projected_fraction": ("fraction of CTP decisions that projected: among certified selected streams "
                                       "(`selected`) and among all Bader attempts (`attempts`)"),
            "hap_over_uniform_hartree": ("Hartree relative RMSE of the stored HAP projection / that of the uniform "
                                         "projection of the same decoded row, over certified selected rows that "
                                         "store a HAP projection"),
        },
        "by_tau": by_tau,
    }
    (out / "SUMMARY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("by_tau", "definitions")}, indent=2))
    return 0


def summarize(M: pd.DataFrame, B: pd.DataFrame, bad: pd.DataFrame, tau: str, bases, posts, joint_posts) -> dict:
    """Descriptive statistics for one tau_B."""
    by = {}
    for bname in bases:
        by[bname] = {}
        for q in posts:
            g = M[(M["base"] == bname) & (M["post"] == q)]
            e = {"n_certified": int(g["certified"].sum()),
                 "median_cr": median_or_none(g.loc[g["certified"], "compression_ratio"]),
                 "cr_ratio_vs_best_other": ratio_stats(g["cr_ratio_vs_best_other"])}
            if q != HARTREE_ONLY:
                ov = g["joint_overhead"].to_numpy(float)
                e["joint_overhead"] = {"n": int(np.sum(~np.isnan(ov))), "median": median_or_none(ov)}
            if q.startswith("ctp-"):
                c = g.loc[g["certified"], "ctp_decision"]
                at = bad[(bad["base"] == bname) & (bad["post"] == q) & (bad["tau_bader"] == tau)] if len(bad) else bad
                ad = at.get("ctp_decision", pd.Series(dtype=str))
                e["ctp_projected_fraction"] = {
                    "selected": {"n": int(len(c)), "fraction": float((c == "projected").mean()) if len(c) else None},
                    "attempts": {"n": int(len(ad)), "fraction": float((ad == "projected").mean()) if len(ad) else None},
                }
            if "hap:" in q:
                e["hap_over_uniform_hartree"] = {
                    k: {"n": int(g[f"hap_over_uniform_hartree_{k}"].notna().sum()),
                        "median": median_or_none(g[f"hap_over_uniform_hartree_{k}"]),
                        "max": (float(g[f"hap_over_uniform_hartree_{k}"].max())
                                if g[f"hap_over_uniform_hartree_{k}"].notna().any() else None)}
                    for k in ("hist", "safe")}
            by[bname][q] = e

    best = {}
    for bname in bases:
        g = B[B["base"] == bname]
        best[bname] = {"n_certified": int(g["best_joint_cr"].notna().sum()),
                       "median_cr": median_or_none(g["best_joint_cr"]),
                       "joint_overhead": {"n": int(g["joint_overhead"].notna().sum()),
                                          "median": median_or_none(g["joint_overhead"])},
                       "post_counts": {k: int(v) for k, v in g.loc[g["best_joint_cr"].notna(), "best_joint_post"]
                                       .value_counts().items()},
                       "cr_ratio_vs_best_other": ratio_stats(g["cr_ratio_vs_best_other"])}

    focus = None
    if FOCUS_BASE in bases:
        f = M[M["base"] == FOCUS_BASE]
        focus = {"base": FOCUS_BASE,
                 "same_post": {q: ratio_stats(f.loc[f["post"] == q, "cr_ratio_vs_best_other"]) for q in joint_posts},
                 "best_post": ratio_stats(B.loc[B["base"] == FOCUS_BASE, "cr_ratio_vs_best_other"])}
    return {"by_base_post": by, "best_joint_post_by_base": best, "focus_vs_others": focus}


if __name__ == "__main__":
    raise SystemExit(main())
