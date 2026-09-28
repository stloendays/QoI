#!/usr/bin/env python3
"""WP-D pre-declared modelling (a)-(d), figure, RESULTS.md and provenance.json.

All analysis rules here were fixed before descriptors.csv was inspected (see DEVIATIONS.md).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import KFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SEED = 20260928
N_BOOT = 2000
N_OUTER = 10
N_INNER = 5
TAUS = [1e-4, 1e-3, 1e-2]
TAU_TAG = {1e-4: "1e-4", 1e-3: "1e-3", 1e-2: "1e-2"}
ALPHAS = np.logspace(-3, 3, 25)
CS = np.logspace(-3, 3, 13)
GAP_LOG_OFFSET = 1e-3  # added before log10 of normalized boundary gaps (exact ties give 0)
MEDIAN_FLOOR_REL = 1e-12  # rho_median clipped to this fraction of rho_max before eps/median

# Raw descriptor columns (groups 1-6) used for univariate Spearman.
RAW_DESCRIPTORS = {
    1: ["natoms", "npoints", "mean_grid_spacing_A", "max_axis_grid_spacing_A", "cell_aspect_ratio",
        "vacuum_fraction", "is_slab", "is_vacuum2d"],
    2: ["eps_m", "eps_over_rho_max", "eps_over_rho_median"],
    3: ["boundary_fraction", "boundary_gap_p05_over_eps", "boundary_gap_p50_over_eps",
        "boundary_gap_p95_over_eps", "boundary_gap_lt1_fraction"],
    4: ["near_tie_fraction_lt_eps", "near_tie_fraction_lt_0p1eps"],
    5: ["min_basin_voxels", "min_basin_charge_e", "n_basins_lt_100_voxels"],
    6: ["n_axis_order_flips_noise_seed20260905"],
}
# Model features (groups 1-5): name -> (source column, transform)
LOG10 = "log10"
LOG10_P1 = "log10(x+1)"
LOG10_GAP = f"log10(x+{GAP_LOG_OFFSET})"
IDENT = "identity"
FEATURES = {
    "log10_natoms": ("natoms", LOG10),
    "log10_npoints": ("npoints", LOG10),
    "mean_grid_spacing_A": ("mean_grid_spacing_A", IDENT),
    "max_axis_grid_spacing_A": ("max_axis_grid_spacing_A", IDENT),
    "log10_cell_aspect_ratio": ("cell_aspect_ratio", LOG10),
    "vacuum_fraction": ("vacuum_fraction", IDENT),
    "is_slab": ("is_slab", IDENT),
    "is_vacuum2d": ("is_vacuum2d", IDENT),
    "log10_eps_m": ("eps_m", LOG10),
    "log10_eps_over_rho_max": ("eps_over_rho_max", LOG10),
    "log10_eps_over_rho_median": ("eps_over_rho_median", LOG10),
    "boundary_fraction": ("boundary_fraction", IDENT),
    "log10_boundary_gap_p05_over_eps": ("boundary_gap_p05_over_eps", LOG10_GAP),
    "log10_boundary_gap_p50_over_eps": ("boundary_gap_p50_over_eps", LOG10_GAP),
    "log10_boundary_gap_p95_over_eps": ("boundary_gap_p95_over_eps", LOG10_GAP),
    "boundary_gap_lt1_fraction": ("boundary_gap_lt1_fraction", IDENT),
    "near_tie_fraction_lt_eps": ("near_tie_fraction_lt_eps", IDENT),
    "near_tie_fraction_lt_0p1eps": ("near_tie_fraction_lt_0p1eps", IDENT),
    "log10_min_basin_voxels_p1": ("min_basin_voxels", LOG10_P1),
    "min_basin_charge_e": ("min_basin_charge_e", IDENT),
    "n_basins_lt_100_voxels": ("n_basins_lt_100_voxels", IDENT),
}
FEATURE_GROUP6 = {"log10_axis_order_flips_p1": ("n_axis_order_flips_noise_seed20260905", LOG10_P1)}
FEATURE_TO_RAW = {k: v[0] for k, v in {**FEATURES, **FEATURE_GROUP6}.items()}


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fold_of(material_id: str) -> int:
    h = hashlib.sha256(f"{SEED}|{material_id}".encode("utf-8")).hexdigest()
    return int(h, 16) % N_OUTER


def stratum(row) -> str:
    return ("dev" if row["corpus"].startswith("dev") else "ext") + "_" + row["system_type"]


def build_features(df: pd.DataFrame, include_group6: bool = False) -> tuple[pd.DataFrame, dict]:
    spec = dict(FEATURES)
    if include_group6:
        spec.update(FEATURE_GROUP6)
    X = pd.DataFrame(index=df.index)
    notes = {}
    d = df.copy()
    # eps/median with clipped median (recorded)
    med_floor = MEDIAN_FLOOR_REL * d["rho_max"]
    clipped = d["rho_median"] <= med_floor
    d["eps_over_rho_median"] = d["eps_m"] / np.maximum(d["rho_median"], med_floor)
    notes["n_median_clipped"] = int(clipped.sum())
    # NaN gaps (systems without any basin boundary): percentiles -> column max, lt1 fraction -> 0
    nan_gap = d["boundary_gap_p50_over_eps"].isna()
    notes["n_no_boundary_imputed"] = int(nan_gap.sum())
    for c in ["boundary_gap_p05_over_eps", "boundary_gap_p50_over_eps", "boundary_gap_p95_over_eps"]:
        d.loc[nan_gap, c] = d[c].max()
    d.loc[nan_gap, "boundary_gap_lt1_fraction"] = 0.0
    for name, (col, tr) in spec.items():
        x = d[col].astype(float)
        if tr == LOG10:
            X[name] = np.log10(x)
        elif tr == LOG10_P1:
            X[name] = np.log10(x + 1.0)
        elif tr == LOG10_GAP:
            X[name] = np.log10(x + GAP_LOG_OFFSET)
        else:
            X[name] = x
    if not np.isfinite(X.values).all():
        bad = X.columns[~np.isfinite(X.values).all(axis=0)].tolist()
        raise RuntimeError(f"non-finite features: {bad}")
    return X, notes


def r2_rmse(y: np.ndarray, yhat: np.ndarray) -> tuple[float, float]:
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return r2, float(np.sqrt(ss_res / len(y)))


def boot_ci(stat_fn, n: int, rng: np.random.Generator, n_boot: int = N_BOOT) -> tuple[float, float]:
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        v = stat_fn(idx)
        if v is not None and np.isfinite(v):
            vals.append(v)
    if len(vals) < 100:
        return float("nan"), float("nan")
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def inner_cv_alpha(X: np.ndarray, y: np.ndarray, alphas=ALPHAS) -> float:
    kf = KFold(N_INNER, shuffle=True, random_state=SEED)
    best, best_mse = None, np.inf
    for a in alphas:
        mse = 0.0
        for tr, te in kf.split(X):
            m = make_pipeline(StandardScaler(), Ridge(alpha=a)).fit(X[tr], y[tr])
            mse += float(np.mean((m.predict(X[te]) - y[te]) ** 2))
        if mse < best_mse:
            best, best_mse = a, mse
    return float(best)


def inner_cv_C(X: np.ndarray, y: np.ndarray, cs=CS) -> float:
    kf = KFold(N_INNER, shuffle=True, random_state=SEED)
    best, best_ll = None, np.inf
    for c in cs:
        ll = 0.0
        ok = True
        for tr, te in kf.split(X):
            if len(np.unique(y[tr])) < 2:
                ok = False
                break
            m = make_pipeline(StandardScaler(), LogisticRegression(C=c, max_iter=5000)).fit(X[tr], y[tr])
            p = np.clip(m.predict_proba(X[te])[:, 1], 1e-12, 1 - 1e-12)
            ll += -float(np.sum(y[te] * np.log(p) + (1 - y[te]) * np.log(1 - p)))
        if ok and ll < best_ll:
            best, best_ll = c, ll
    if best is None:  # no inner split contained both classes (only possible on tiny subsets)
        best = 1.0
    return float(best)


def ridge_fit(X: np.ndarray, y: np.ndarray):
    a = inner_cv_alpha(X, y)
    return make_pipeline(StandardScaler(), Ridge(alpha=a)).fit(X, y), a


def logit_fit(X: np.ndarray, y: np.ndarray):
    c = inner_cv_C(X, y)
    return make_pipeline(StandardScaler(), LogisticRegression(C=c, max_iter=5000)).fit(X, y), c


def outer_cv_ridge(X: np.ndarray, y: np.ndarray, folds: np.ndarray) -> tuple[np.ndarray, list[float]]:
    oof = np.full(len(y), np.nan)
    alphas = []
    for k in range(N_OUTER):
        te = folds == k
        tr = ~te
        if te.sum() == 0:
            continue
        m, a = ridge_fit(X[tr], y[tr])
        oof[te] = m.predict(X[te])
        alphas.append(a)
    return oof, alphas


def outer_cv_logit(X: np.ndarray, y: np.ndarray, folds: np.ndarray) -> tuple[np.ndarray, list[float]]:
    oof = np.full(len(y), np.nan)
    cs = []
    for k in range(N_OUTER):
        te = folds == k
        tr = ~te
        if te.sum() == 0:
            continue
        m, c = logit_fit(X[tr], y[tr])
        oof[te] = m.predict_proba(X[te])[:, 1]
        cs.append(c)
    return oof, cs


def operating_points(y: np.ndarray, p: np.ndarray) -> list[dict]:
    """Highest-recall threshold with (i) FPR <= 5% and (ii) FDR <= 5%."""
    out = []
    thr_candidates = np.unique(np.concatenate([p, [np.inf]]))
    for rule in ("false_eligible_rate_FPR_le_5pct", "false_eligible_rate_FDR_le_5pct"):
        best = None
        for t in thr_candidates:
            pred = p >= t
            tp = int(np.sum(pred & (y == 1)))
            fp = int(np.sum(pred & (y == 0)))
            fn = int(np.sum(~pred & (y == 1)))
            tn = int(np.sum(~pred & (y == 0)))
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
            fdr = fp / (tp + fp) if (tp + fp) > 0 else 0.0
            rate = fpr if rule.startswith("false_eligible_rate_FPR") else fdr
            if rate <= 0.05:
                rec = tp / (tp + fn) if (tp + fn) > 0 else float("nan")
                prec = tp / (tp + fp) if (tp + fp) > 0 else float("nan")
                cand = {"rule": rule, "threshold": float(t), "tp": tp, "fp": fp, "fn": fn, "tn": tn,
                        "precision": prec, "recall": rec, "false_positive_rate": fpr,
                        "false_discovery_rate": fdr, "n_predicted_eligible": tp + fp}
                if best is None or (rec > best["recall"]) or (rec == best["recall"] and prec > best["precision"]):
                    best = cand
        out.append(best)
    return out


def main() -> int:
    t_start = time.time()
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--wp-dir", type=Path, required=True)
    ap.add_argument("--frozen-root", type=Path, required=True)
    ap.add_argument("--compute-wall-seconds", type=float, default=float("nan"))
    ap.add_argument("--compute-started", type=str, default="")
    ap.add_argument("--compute-finished", type=str, default="")
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    wp = args.wp_dir.resolve()
    frozen = args.frozen_root.resolve()

    df = pd.read_csv(wp / "descriptors.csv")
    fails = pd.read_csv(wp / "failures.csv")
    n_target = 319
    df["is_slab"] = (df["system_type"] == "slab").astype(float)
    df["is_vacuum2d"] = (df["system_type"] == "vacuum2d").astype(float)
    df["is_dev"] = df["corpus"].str.startswith("dev")
    df["stratum"] = df.apply(stratum, axis=1)
    df["fold"] = df["material_id"].map(fold_of)
    df["y"] = np.log10(df["stability_floor_A1_e"].astype(float))
    for tau in TAUS:
        df[f"eligible_{TAU_TAG[tau]}"] = (df["stability_floor_A1_e"] < tau).astype(int)
    y = df["y"].to_numpy()
    n = len(df)
    rng = np.random.default_rng(SEED)

    # ---------------- (a) univariate Spearman ----------------
    uni_rows = []
    for g, cols in RAW_DESCRIPTORS.items():
        for c in cols:
            x = df[c].astype(float).to_numpy()
            mask = np.isfinite(x)
            xm, ym = x[mask], y[mask]
            nn = int(mask.sum())
            if nn < 5 or np.nanstd(xm) == 0:
                uni_rows.append({"descriptor": c, "group": g, "n": nn, "spearman_rho": np.nan,
                                 "ci_low": np.nan, "ci_high": np.nan, "p_value": np.nan})
                continue
            rho, pval = spearmanr(xm, ym)
            lo, hi = boot_ci(lambda idx: spearmanr(xm[idx], ym[idx])[0] if np.std(xm[idx]) > 0 else None,
                             nn, np.random.default_rng(SEED))
            uni_rows.append({"descriptor": c, "group": g, "n": nn, "spearman_rho": float(rho),
                             "ci_low": lo, "ci_high": hi, "p_value": float(pval)})
    uni = pd.DataFrame(uni_rows)
    uni["abs_rho"] = uni["spearman_rho"].abs()
    uni = uni.sort_values("abs_rho", ascending=False).reset_index(drop=True)
    uni["rank"] = np.arange(1, len(uni) + 1)
    uni["in_model_groups_1_5"] = uni["group"].between(1, 5)
    uni.to_csv(wp / "univariate.csv", index=False)

    # ---------------- (b) ridge with nested CV ----------------
    X_df, notes = build_features(df)
    X6_df, _ = build_features(df, include_group6=True)
    feat = list(X_df.columns)
    feat6 = list(X6_df.columns)
    X = X_df.to_numpy(float)
    X6 = X6_df.to_numpy(float)
    folds = df["fold"].to_numpy()

    oof, alphas = outer_cv_ridge(X, y, folds)
    oof6, alphas6 = outer_cv_ridge(X6, y, folds)
    df["ridge_oof_pred"] = oof
    df["ridge_g6_oof_pred"] = oof6

    cv_rows = []

    def add_cv_row(model, subset_name, mask, pred):
        yy, pp = y[mask], pred[mask]
        m = int(mask.sum())
        r2, rmse = r2_rmse(yy, pp)
        rr = np.random.default_rng(SEED)
        r2_lo, r2_hi = boot_ci(lambda idx: r2_rmse(yy[idx], pp[idx])[0], m, rr)
        rr = np.random.default_rng(SEED)
        rm_lo, rm_hi = boot_ci(lambda idx: r2_rmse(yy[idx], pp[idx])[1], m, rr)
        cv_rows.append({"model": model, "subset": subset_name, "n": m, "R2": r2, "R2_ci_low": r2_lo,
                        "R2_ci_high": r2_hi, "RMSE_decades": rmse, "RMSE_ci_low": rm_lo,
                        "RMSE_ci_high": rm_hi})

    strata_masks = {
        "all": np.ones(n, bool),
        "dev": df["is_dev"].to_numpy(),
        "ext": ~df["is_dev"].to_numpy(),
        "bulk": (df["system_type"] == "bulk").to_numpy(),
        "slab": (df["system_type"] == "slab").to_numpy(),
        "vacuum2d": (df["system_type"] == "vacuum2d").to_numpy(),
        "slab_or_vacuum2d": (df["system_type"] != "bulk").to_numpy(),
    }
    for s in sorted(df["stratum"].unique()):
        strata_masks[s] = (df["stratum"] == s).to_numpy()
    for name, mask in strata_masks.items():
        add_cv_row("ridge_groups1-5_cv10", name, mask, oof)
    for name, mask in strata_masks.items():
        add_cv_row("ridge_groups1-6_diagnostic_cv10", name, mask, oof6)

    # ---------------- (c) logistic classification, CV ----------------
    clf_rows = []
    op_rows = []
    roc_data = {}
    for tau in TAUS:
        tag = TAU_TAG[tau]
        yt = df[f"eligible_{tag}"].to_numpy()
        p, cs = outer_cv_logit(X, yt, folds)
        df[f"logit_oof_prob_{tag}"] = p
        auc = float(roc_auc_score(yt, p))
        lo, hi = boot_ci(lambda idx: roc_auc_score(yt[idx], p[idx]) if len(np.unique(yt[idx])) == 2 else None,
                         n, np.random.default_rng(SEED))
        clf_rows.append({"model": "logistic_groups1-5_cv10", "tau_e": tau, "subset": "all", "n": n,
                         "n_eligible": int(yt.sum()), "AUC": auc, "AUC_ci_low": lo, "AUC_ci_high": hi,
                         "inner_C_values": ";".join(f"{c:g}" for c in cs)})
        for name in ("dev", "ext", "bulk", "slab_or_vacuum2d"):
            mask = strata_masks[name]
            if len(np.unique(yt[mask])) == 2:
                a = float(roc_auc_score(yt[mask], p[mask]))
                ym_, pm_ = yt[mask], p[mask]
                lo2, hi2 = boot_ci(lambda idx: roc_auc_score(ym_[idx], pm_[idx]) if len(np.unique(ym_[idx])) == 2 else None,
                                   int(mask.sum()), np.random.default_rng(SEED))
            else:
                a, lo2, hi2 = np.nan, np.nan, np.nan
            clf_rows.append({"model": "logistic_groups1-5_cv10", "tau_e": tau, "subset": name,
                             "n": int(mask.sum()), "n_eligible": int(yt[mask].sum()), "AUC": a,
                             "AUC_ci_low": lo2, "AUC_ci_high": hi2, "inner_C_values": ""})
        for op in operating_points(yt, p):
            if op is None:
                op_rows.append({"tau_e": tau, "rule": "none_feasible"})
            else:
                op_rows.append({"tau_e": tau, **op})
        roc_data[tag] = roc_curve(yt, p)

    # ---------------- coefficients (full-population fit and dev-only fit) ----------------
    model_all, alpha_all = ridge_fit(X, y)
    coef_all = model_all.named_steps["ridge"].coef_
    dev = df["is_dev"].to_numpy()
    model_dev, alpha_dev = ridge_fit(X[dev], y[dev])
    coef_dev = model_dev.named_steps["ridge"].coef_
    model_all6, alpha_all6 = ridge_fit(X6, y)
    coef_all6 = model_all6.named_steps["ridge"].coef_
    coef = pd.DataFrame({
        "feature": feat,
        "raw_descriptor": [FEATURE_TO_RAW[f] for f in feat],
        "transform": [FEATURES[f][1] for f in feat],
        "coef_standardized_all319": coef_all,
        "coef_standardized_dev254": coef_dev,
    })
    coef["abs_coef_all319"] = coef["coef_standardized_all319"].abs()
    coef = coef.sort_values("abs_coef_all319", ascending=False).reset_index(drop=True)
    coef["rank_all319"] = np.arange(1, len(coef) + 1)
    coef["rank_dev254"] = coef["coef_standardized_dev254"].abs().rank(ascending=False).astype(int)
    coef6 = pd.DataFrame({"feature": feat6, "raw_descriptor": [FEATURE_TO_RAW[f] for f in feat6],
                          "coef_standardized_all319_groups1-6": coef_all6})
    coef = coef.merge(coef6[["feature", "coef_standardized_all319_groups1-6"]], on="feature", how="outer")
    coef.to_csv(wp / "coefficients.csv", index=False)

    # ---------------- (d) external hold-out ----------------
    ext = ~dev
    pred_ext = model_dev.predict(X[ext])
    df.loc[ext, "ridge_dev_fit_pred"] = pred_ext
    ye = y[ext]
    r2_ext, rmse_ext = r2_rmse(ye, pred_ext)
    r2_lo, r2_hi = boot_ci(lambda idx: r2_rmse(ye[idx], pred_ext[idx])[0], int(ext.sum()), np.random.default_rng(SEED))
    rm_lo, rm_hi = boot_ci(lambda idx: r2_rmse(ye[idx], pred_ext[idx])[1], int(ext.sum()), np.random.default_rng(SEED))
    hold_rows = [{"model": "ridge_groups1-5_fit_dev254", "tau_e": "", "metric": "R2", "value": r2_ext,
                  "ci_low": r2_lo, "ci_high": r2_hi, "n_external": int(ext.sum()), "n_eligible_external": "",
                  "alpha_or_C": alpha_dev},
                 {"model": "ridge_groups1-5_fit_dev254", "tau_e": "", "metric": "RMSE_decades", "value": rmse_ext,
                  "ci_low": rm_lo, "ci_high": rm_hi, "n_external": int(ext.sum()), "n_eligible_external": "",
                  "alpha_or_C": alpha_dev}]
    for sname in ("ext_bulk", "ext_vacuum2d"):
        m = (df["stratum"] == sname).to_numpy()[ext]
        r2s, rms = r2_rmse(ye[m], pred_ext[m])
        hold_rows.append({"model": "ridge_groups1-5_fit_dev254", "tau_e": "", "metric": f"R2_{sname}", "value": r2s,
                          "ci_low": np.nan, "ci_high": np.nan, "n_external": int(m.sum()), "n_eligible_external": "",
                          "alpha_or_C": alpha_dev})
        hold_rows.append({"model": "ridge_groups1-5_fit_dev254", "tau_e": "", "metric": f"RMSE_decades_{sname}",
                          "value": rms, "ci_low": np.nan, "ci_high": np.nan, "n_external": int(m.sum()),
                          "n_eligible_external": "", "alpha_or_C": alpha_dev})
    ext_auc = {}
    for tau in TAUS:
        tag = TAU_TAG[tau]
        yt = df[f"eligible_{tag}"].to_numpy()
        clf, c = logit_fit(X[dev], yt[dev])
        pe = clf.predict_proba(X[ext])[:, 1]
        df.loc[ext, f"logit_dev_fit_prob_{tag}"] = pe
        yte = yt[ext]
        auc = float(roc_auc_score(yte, pe))
        lo, hi = boot_ci(lambda idx: roc_auc_score(yte[idx], pe[idx]) if len(np.unique(yte[idx])) == 2 else None,
                         int(ext.sum()), np.random.default_rng(SEED))
        ext_auc[tag] = (auc, lo, hi, int(yte.sum()))
        hold_rows.append({"model": "logistic_groups1-5_fit_dev254", "tau_e": tau, "metric": "AUC", "value": auc,
                          "ci_low": lo, "ci_high": hi, "n_external": int(ext.sum()),
                          "n_eligible_external": int(yte.sum()), "alpha_or_C": c})
    hold = pd.DataFrame(hold_rows)
    hold.to_csv(wp / "external_holdout.csv", index=False)

    cv = pd.DataFrame(cv_rows)
    clf_df = pd.DataFrame(clf_rows)
    ops = pd.DataFrame(op_rows)
    cv_out = pd.concat([cv, clf_df], ignore_index=True, sort=False)
    cv_out["outer_alpha_values"] = ""
    cv_out.loc[(cv_out["model"] == "ridge_groups1-5_cv10") & (cv_out["subset"] == "all"), "outer_alpha_values"] = ";".join(f"{a:g}" for a in alphas)
    cv_out.loc[(cv_out["model"] == "ridge_groups1-6_diagnostic_cv10") & (cv_out["subset"] == "all"), "outer_alpha_values"] = ";".join(f"{a:g}" for a in alphas6)
    cv_out.to_csv(wp / "cv_metrics.csv", index=False)
    ops.to_csv(wp / "operating_points.csv", index=False)
    df.to_csv(wp / "predictions.csv", index=False)

    # ---------------- acceptance ----------------
    top3_uni = uni[uni["in_model_groups_1_5"]].head(3)["descriptor"].tolist()
    top3_ridge = coef.dropna(subset=["rank_all319"]).sort_values("rank_all319").head(3)["raw_descriptor"].tolist()
    same_top3 = set(top3_uni) == set(top3_ridge)
    r2_ok = bool(r2_ext >= 0.5)
    accepted = bool(r2_ok and same_top3)
    verdict = ("explanatory" if accepted else "measured, not yet predictable")

    # ---------------- figure ----------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(13, 10.5))
    ax = axes[0, 0]
    u = uni.dropna(subset=["spearman_rho"]).sort_values("spearman_rho")
    colors = ["#1f77b4" if g <= 5 else "#7f7f7f" for g in u["group"]]
    ax.barh(u["descriptor"], u["spearman_rho"], color=colors,
            xerr=[u["spearman_rho"] - u["ci_low"], u["ci_high"] - u["spearman_rho"]], capsize=2, ecolor="black")
    ax.axvline(0, color="k", lw=0.8)
    ax.set_xlabel("Spearman ρ with log10 f_m (95% bootstrap CI)")
    ax.set_title("(a) Univariate association (grey = group 6 diagnostic)")
    ax.tick_params(axis="y", labelsize=8)

    ax = axes[0, 1]
    palette = {"dev_bulk": "#1f77b4", "dev_slab": "#ff7f0e", "ext_bulk": "#2ca02c", "ext_vacuum2d": "#d62728"}
    for s, col in palette.items():
        m = (df["stratum"] == s).to_numpy()
        ax.scatter(y[m], oof[m], s=18, color=col, label=f"{s} (n={m.sum()})", alpha=0.8)
    lim = [min(y.min(), np.nanmin(oof)) - 0.3, max(y.max(), np.nanmax(oof)) + 0.3]
    ax.plot(lim, lim, "k--", lw=0.8)
    for tau in TAUS:
        ax.axvline(np.log10(tau), color="grey", lw=0.6, ls=":")
    r2_all = cv[(cv["model"] == "ridge_groups1-5_cv10") & (cv["subset"] == "all")].iloc[0]
    ax.set_xlabel("observed log10 f_m (e)")
    ax.set_ylabel("10-fold CV prediction")
    ax.set_title(f"(b) Ridge, groups 1-5: CV R² = {r2_all['R2']:.2f}, RMSE = {r2_all['RMSE_decades']:.2f} dec")
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    for s, col in {"ext_bulk": "#2ca02c", "ext_vacuum2d": "#d62728"}.items():
        m = (df["stratum"] == s).to_numpy()
        ax.scatter(y[m], df.loc[m, "ridge_dev_fit_pred"], s=22, color=col, label=f"{s} (n={m.sum()})")
    ax.plot(lim, lim, "k--", lw=0.8)
    for tau in TAUS:
        ax.axvline(np.log10(tau), color="grey", lw=0.6, ls=":")
    ax.set_xlabel("observed log10 f_m (e), external 65")
    ax.set_ylabel("prediction from development-only fit")
    ax.set_title(f"(d) External hold-out: R² = {r2_ext:.2f}, RMSE = {rmse_ext:.2f} dec")
    ax.legend(fontsize=8)

    ax = axes[1, 1]
    for tau in TAUS:
        tag = TAU_TAG[tau]
        fpr, tpr, _ = roc_data[tag]
        a = clf_df[(clf_df["tau_e"] == tau) & (clf_df["subset"] == "all")].iloc[0]["AUC"]
        ax.plot(fpr, tpr, label=f"τ = {tag} e: CV AUC = {a:.2f}; ext AUC = {ext_auc[tag][0]:.2f}")
    ax.plot([0, 1], [0, 1], "k--", lw=0.8)
    ax.axvline(0.05, color="grey", lw=0.6, ls=":")
    ax.set_xlabel("false-eligible rate (FPR)")
    ax.set_ylabel("recall of eligible systems")
    ax.set_title("(c) Eligibility classification, 10-fold CV")
    ax.legend(fontsize=8)
    fig.suptitle(f"WP-D: QSQ floor from reference-density descriptors — verdict: {verdict}", fontsize=12)
    fig.tight_layout()
    fig.savefig(wp / "fig_predictor.png", dpi=200)
    fig.savefig(wp / "fig_predictor.svg")
    plt.close(fig)

    # ---------------- RESULTS.md ----------------
    def f3(v):
        return "nan" if v is None or (isinstance(v, float) and not np.isfinite(v)) else f"{v:.3f}"

    L = []
    L.append("# WP-D — Predicting non-evaluability from reference-density descriptors\n")
    L.append("Question: can the QSQ stability floor f_m be anticipated from cheap properties of the reference density and grid?\n")
    L.append("## Population\n")
    L.append(f"- Systems with complete descriptors: **{n} / {n_target}** "
             f"(dev {int(dev.sum())}: bulk {int(((df['stratum']=='dev_bulk')).sum())}, slab {int((df['stratum']=='dev_slab').sum())}; "
             f"ext {int(ext.sum())}: bulk {int((df['stratum']=='ext_bulk').sum())}, vacuum2d {int((df['stratum']=='ext_vacuum2d').sum())}).")
    L.append(f"- Failures recorded in `failures.csv`: **{len(fails)}**" + (" (none)." if len(fails) == 0 else "."))
    for tau in TAUS:
        tag = TAU_TAG[tau]
        L.append(f"- Eligible (f_m < {tag} e): {int(df[f'eligible_{tag}'].sum())} / {n} "
                 f"(dev {int(df.loc[dev, f'eligible_{tag}'].sum())} / {int(dev.sum())}, ext {int(df.loc[ext, f'eligible_{tag}'].sum())} / {int(ext.sum())}).")
    L.append(f"- Target range: log10 f_m from {y.min():.2f} to {y.max():.2f} (f_m in e).")
    L.append(f"- Feature preprocessing notes: systems without any basin boundary (gap percentiles imputed with column maximum, lt1 fraction = 0): {notes['n_no_boundary_imputed']}; "
             f"systems with rho_median clipped for eps/median: {notes['n_median_clipped']}.\n")

    L.append("## (a) Univariate Spearman ρ with log10 f_m (material bootstrap, 2,000 resamples, seed 20260928)\n")
    L.append("| rank | descriptor | group | n | ρ | 95% CI |")
    L.append("|---:|---|---:|---:|---:|---|")
    for _, r in uni.iterrows():
        L.append(f"| {r['rank']} | `{r['descriptor']}` | {r['group']} | {r['n']} | {f3(r['spearman_rho'])} | [{f3(r['ci_low'])}, {f3(r['ci_high'])}] |")
    L.append("")
    L.append(f"Top three (groups 1–5) by |ρ|: {', '.join('`'+t+'`' for t in top3_uni)}.\n")

    L.append("## (b) Ridge regression of log10 f_m on standardized descriptors (groups 1–5), α by inner 5-fold CV, 10-fold outer CV over systems\n")
    L.append("| model | subset | n | R² | 95% CI | RMSE (decades) | 95% CI |")
    L.append("|---|---|---:|---:|---|---:|---|")
    for _, r in cv.iterrows():
        L.append(f"| {r['model']} | {r['subset']} | {r['n']} | {f3(r['R2'])} | [{f3(r['R2_ci_low'])}, {f3(r['R2_ci_high'])}] | {f3(r['RMSE_decades'])} | [{f3(r['RMSE_ci_low'])}, {f3(r['RMSE_ci_high'])}] |")
    L.append("")
    L.append(f"Outer-fold α values (groups 1–5): {', '.join(f'{a:g}' for a in alphas)}. Full-population fit α = {alpha_all:g}; development-only fit α = {alpha_dev:g}.\n")
    L.append("Standardized ridge coefficients (full-population fit, 319 systems), ranked by |coef|:\n")
    L.append("| rank | feature | raw descriptor | coef (all 319) | coef (dev 254) | rank (dev 254) |")
    L.append("|---:|---|---|---:|---:|---:|")
    for _, r in coef.dropna(subset=["rank_all319"]).sort_values("rank_all319").iterrows():
        L.append(f"| {int(r['rank_all319'])} | `{r['feature']}` | `{r['raw_descriptor']}` | {r['coef_standardized_all319']:+.3f} | {r['coef_standardized_dev254']:+.3f} | {int(r['rank_dev254'])} |")
    L.append("")
    L.append(f"Top three ridge descriptors by |standardized coefficient| (all 319): {', '.join('`'+t+'`' for t in top3_ridge)}.\n")

    L.append("## (c) Logistic classification of eligibility (groups 1–5), C by inner 5-fold CV, 10-fold outer CV\n")
    L.append("| τ (e) | subset | n | n eligible | AUC | 95% CI |")
    L.append("|---|---|---:|---:|---:|---|")
    for _, r in clf_df.iterrows():
        L.append(f"| {r['tau_e']:g} | {r['subset']} | {r['n']} | {r['n_eligible']} | {f3(r['AUC'])} | [{f3(r['AUC_ci_low'])}, {f3(r['AUC_ci_high'])}] |")
    L.append("")
    L.append("Operating points on out-of-fold probabilities (highest recall subject to the false-eligible constraint; FPR = false eligible / truly non-eligible, FDR = false eligible / predicted eligible):\n")
    L.append("| τ (e) | rule | threshold | TP | FP | FN | TN | precision | recall | FPR | FDR |")
    L.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for _, r in ops.iterrows():
        if r.get("rule") == "none_feasible":
            L.append(f"| {r['tau_e']:g} | none feasible | | | | | | | | | |")
        else:
            L.append(f"| {r['tau_e']:g} | {r['rule']} | {r['threshold']:.3f} | {int(r['tp'])} | {int(r['fp'])} | {int(r['fn'])} | {int(r['tn'])} | {f3(r['precision'])} | {f3(r['recall'])} | {f3(r['false_positive_rate'])} | {f3(r['false_discovery_rate'])} |")
    L.append("")

    L.append("## (d) Held-out check: fit on the 254 development systems, evaluate on the 65 external systems\n")
    L.append("| model | τ (e) | metric | value | 95% CI | n external | n eligible external |")
    L.append("|---|---|---|---:|---|---:|---:|")
    for _, r in hold.iterrows():
        tau_s = "" if r["tau_e"] == "" or pd.isna(r["tau_e"]) else f"{float(r['tau_e']):g}"
        L.append(f"| {r['model']} | {tau_s} | {r['metric']} | {f3(r['value'])} | [{f3(r['ci_low'])}, {f3(r['ci_high'])}] | {r['n_external']} | {r['n_eligible_external']} |")
    L.append("")

    L.append("## Acceptance (applied literally)\n")
    L.append(f"- Held-out R² on the external 65 = {r2_ext:.3f} (95% CI [{f3(r2_lo)}, {f3(r2_hi)}]); rule requires ≥ 0.5 → **{'met' if r2_ok else 'not met'}**.")
    L.append(f"- Top three in (a): {top3_uni}; top three in ridge coefficients: {top3_ridge}; identical as sets → **{'yes' if same_top3 else 'no'}**.")
    L.append(f"- Verdict: **{verdict}**.\n")
    L.append("## Files\n")
    L.append("`descriptors.csv` (one row per system), `univariate.csv`, `cv_metrics.csv`, `coefficients.csv`, `external_holdout.csv`, "
             "`operating_points.csv`, `predictions.csv` (out-of-fold and hold-out predictions), `fig_predictor.{png,svg}`, `failures.csv`, "
             "`provenance.json`, `DEVIATIONS.md`. Compute: `compute_descriptors.py` → `aggregate.py` → `model.py`.\n")
    (wp / "RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    # ---------------- provenance ----------------
    def git(args_, cwd):
        return subprocess.run(["git", *args_], cwd=cwd, capture_output=True, text=True).stdout.strip()

    pip_freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout.splitlines()
    inputs = {
        "materials_metadata.csv": repo / "materials_metadata.csv",
        "stability/stability_floor_A1.csv": repo / "stability" / "stability_floor_A1.csv",
        "stability/stability_floor_A1_per_seed.csv": repo / "stability" / "stability_floor_A1_per_seed.csv",
        "external_test_MANIFEST.json": repo / "external_test_MANIFEST.json",
        "validation/qsq_prospective/development_compatibility_smoke.py": repo / "validation" / "qsq_prospective" / "development_compatibility_smoke.py",
        "frozen:validation/external_end_to_end.py": frozen / "validation" / "external_end_to_end.py",
        "frozen:validation/requirements-external-e2e.txt": frozen / "validation" / "requirements-external-e2e.txt",
        "analysis/extensions_20260928/PROTOCOL.md": repo / "analysis" / "extensions_20260928" / "PROTOCOL.md",
    }
    modelling_seconds = time.time() - t_start
    prov = {
        "work_package": "WP-D",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "repo_head": git(["rev-parse", "HEAD"], repo),
        "repo_branch": git(["rev-parse", "--abbrev-ref", "HEAD"], repo),
        "frozen_scientific_commit": git(["rev-parse", "HEAD"], frozen),
        "python": sys.version,
        "platform": platform.platform(),
        "pip_freeze": pip_freeze,
        "input_sha256": {k: sha256_path(v) for k, v in inputs.items()},
        "source_density_sha256": dict(zip(df["material_id"], df["source_sha256"])),
        "bader_settings": {"method": "ongrid", "vacuum_tol": 1e-3, "persistence_tol": 0.5, "nna_cutoff": False},
        "seed": SEED, "n_bootstrap": N_BOOT, "outer_folds": N_OUTER, "inner_folds": N_INNER,
        "fold_rule": "int(sha256('20260928|' + material_id), 16) % 10",
        "alpha_grid": [float(a) for a in ALPHAS], "C_grid": [float(c) for c in CS],
        "features_groups1_5": {k: {"raw": v[0], "transform": v[1]} for k, v in FEATURES.items()},
        "feature_group6": {k: {"raw": v[0], "transform": v[1]} for k, v in FEATURE_GROUP6.items()},
        "preprocessing_notes": notes,
        "n_systems": n, "n_failures": int(len(fails)),
        "wall_time": {
            "descriptor_compute_started": args.compute_started,
            "descriptor_compute_finished": args.compute_finished,
            "descriptor_compute_wall_seconds_elapsed": args.compute_wall_seconds,
            "descriptor_compute_sum_of_per_system_wall_seconds": float(df["wall_seconds"].sum()),
            "descriptor_compute_sum_of_bader_seconds": float(df["bader_seconds"].sum()),
            "descriptor_compute_sum_of_download_seconds": float(df["download_seconds"].sum()),
            "modelling_seconds": modelling_seconds,
        },
        "acceptance": {"r2_external": r2_ext, "r2_rule_met": r2_ok, "top3_univariate": top3_uni,
                       "top3_ridge": top3_ridge, "top3_same": same_top3, "verdict": verdict},
    }
    (wp / "provenance.json").write_text(json.dumps(prov, indent=1), encoding="utf-8")
    print(json.dumps(prov["acceptance"], indent=1))
    print(f"CV R2 all = {r2_all['R2']:.3f}, RMSE = {r2_all['RMSE_decades']:.3f}; ext R2 = {r2_ext:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
