#!/usr/bin/env python
"""WP-A: calibrated risk model for QSQ (statistics only on frozen inputs).

Implements the section "WP-A -- Calibrated risk model for QSQ" of
analysis/extensions_20260928/PROTOCOL.md. Reads only the four frozen inputs listed
there and writes only under analysis/extensions_20260928/WP-A/.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.isotonic import IsotonicRegression

T0 = time.time()
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE

SEED = 20260928
N_BOOT = 2000
N_FOLDS = 10
TAUS = [1e-4, 1e-3, 1e-2]
P_STARS = [0.005, 0.01, 0.02, 0.05, 0.10]
P_STAR_GATE_COMPARISON = 0.016  # binary gate's realized eligible-group risk (comparison row only)
GATE_RISK_LOW = 0.01600  # frozen P2 rate, eligible group at 1e-3 e (135/8437)
GATE_RISK_HIGH = 0.81325  # frozen P2 rate, rejected group at 1e-3 e (5326/6549)
LOGLOSS_EPS = 1e-6
N_BINS = 10

INPUTS = {
    "outcomes": ROOT / "validation/qsq_prospective/p2_fresh_probes/outcomes.csv",
    "floor": ROOT / "stability/stability_floor_A1.csv",
    "floor_per_seed": ROOT / "stability/stability_floor_A1_per_seed.csv",
    "metadata": ROOT / "materials_metadata.csv",
}
MODELS = ["gate", "logistic_x", "isotonic_x", "logistic_x_secondary"]
MODEL_LABEL = {
    "gate": "Binary gate (frozen P2 rates)",
    "logistic_x": "Logistic on x",
    "isotonic_x": "Isotonic on x",
    "logistic_x_secondary": "Logistic on x + secondary",
}


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fold_of(material_id: str) -> int:
    key = hashlib.sha256(f"{SEED}|{material_id}".encode("utf-8")).hexdigest()
    return int(key, 16) % N_FOLDS


def tiebreak_key(material_id: str, tau: float) -> str:
    return hashlib.sha256(f"{SEED}|tiebreak|{material_id}|{tau:.0e}".encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- inputs
outcomes = pd.read_csv(INPUTS["outcomes"])
floor = pd.read_csv(INPUTS["floor"])
per_seed = pd.read_csv(INPUTS["floor_per_seed"])
meta = pd.read_csv(INPUTS["metadata"])

# --------------------------------------------------------------------------- anchors
anchors = {}
assert len(outcomes) == 14986, len(outcomes)
mats = sorted(outcomes["material_id"].unique())
assert len(mats) == 254, len(mats)
assert (outcomes.groupby("material_id").size() == 59).all()
assert np.isfinite(outcomes["bader_response_max_e"]).all()
assert set(mats) <= set(floor["material_id"])
fm = floor.set_index("material_id").loc[mats, "stability_floor_A1_e"].astype(float)
assert (fm > 0).all()
outcomes["f_m"] = outcomes["material_id"].map(fm)
elig = outcomes[outcomes["f_m"] < 1e-3]
rej = outcomes[outcomes["f_m"] >= 1e-3]
anchors = {
    "n_rows": int(len(outcomes)),
    "n_materials": int(len(mats)),
    "trials_per_material": 59,
    "n_nonfinite_response": 0,
    "tau_1e-3_eligible_materials": int(elig["material_id"].nunique()),
    "tau_1e-3_eligible_exceedances": int((elig["bader_response_max_e"] >= 1e-3).sum()),
    "tau_1e-3_eligible_trials": int(len(elig)),
    "tau_1e-3_rejected_materials": int(rej["material_id"].nunique()),
    "tau_1e-3_rejected_exceedances": int((rej["bader_response_max_e"] >= 1e-3).sum()),
    "tau_1e-3_rejected_trials": int(len(rej)),
}
assert anchors["tau_1e-3_eligible_materials"] == 143
assert anchors["tau_1e-3_eligible_exceedances"] == 135 and anchors["tau_1e-3_eligible_trials"] == 8437
assert anchors["tau_1e-3_rejected_materials"] == 111
assert anchors["tau_1e-3_rejected_exceedances"] == 5326 and anchors["tau_1e-3_rejected_trials"] == 6549
print("anchors reproduced:", anchors)

# --------------------------------------------------------------------------- predictors
ps_dev = per_seed[per_seed["material_id"].isin(mats)]
assert (ps_dev.groupby("material_id").size() == 5).all()
assert (ps_dev["floor_noise_resolved_e"] > 0).all()
g = ps_dev.groupby("material_id")["floor_noise_resolved_e"]
seed_max = g.max().loc[mats]
assert np.allclose(seed_max.values, fm.values, rtol=1e-9, atol=0), "f_m must equal the five-seed max"
sec = pd.DataFrame({
    "seed_median_e": g.median().loc[mats],
    "seed_mean_e": g.mean().loc[mats],
    "log10_seed_median": np.log10(g.median().loc[mats]),
    "log10_seed_mean": np.log10(g.mean().loc[mats]),
    "seed_log10_span": (np.log10(g.max()) - np.log10(g.min())).loc[mats],
})
systype = meta.set_index("material_id").loc[mats, "system_type"]

# material x tau table (762 rows)
rows = []
for tau in TAUS:
    exc = (outcomes["bader_response_max_e"] >= tau).groupby(outcomes["material_id"]).sum().loc[mats]
    for m in mats:
        rows.append({
            "material_id": m,
            "system_type": systype[m],
            "tau_e": tau,
            "f_m_e": fm[m],
            "x": np.log10(fm[m] / tau),
            "log10_tau": np.log10(tau),
            "log10_seed_median": sec.loc[m, "log10_seed_median"],
            "log10_seed_mean": sec.loc[m, "log10_seed_mean"],
            "seed_log10_span": sec.loc[m, "seed_log10_span"],
            "n_trials": 59,
            "n_exceed": int(exc[m]),
            "p_obs": exc[m] / 59.0,
            "fold": fold_of(m),
            "gate_eligible": int(fm[m] < tau),
            "_tiebreak": tiebreak_key(m, tau),
        })
mt = pd.DataFrame(rows).reset_index(drop=True)
mt["gate_risk"] = np.where(mt["gate_eligible"] == 1, GATE_RISK_LOW, GATE_RISK_HIGH)
fold_sizes = mt[mt["tau_e"] == 1e-3].groupby("fold").size().reindex(range(N_FOLDS), fill_value=0)
print("fold sizes:", fold_sizes.to_dict())
assert fold_sizes.sum() == 254

# trial-level table (44,958 rows) for the logistic fits
trial_rows = []
for tau in TAUS:
    t = outcomes[["material_id", "bader_response_max_e"]].copy()
    t["tau_e"] = tau
    t["y"] = (t["bader_response_max_e"] >= tau).astype(int)
    trial_rows.append(t.drop(columns="bader_response_max_e"))
trials = pd.concat(trial_rows, ignore_index=True)
trials = trials.merge(
    mt[["material_id", "tau_e", "x", "log10_tau", "log10_seed_median", "log10_seed_mean", "seed_log10_span", "fold"]],
    on=["material_id", "tau_e"], how="left", validate="many_to_one",
)
assert len(trials) == 14986 * 3 and trials["x"].notna().all()

FEATURES = {
    "logistic_x": ["x", "log10_tau"],
    "logistic_x_secondary": ["x", "log10_tau", "log10_seed_median", "log10_seed_mean", "seed_log10_span"],
}


def fit_logistic(df_trials: pd.DataFrame, features: list[str]):
    X = sm.add_constant(df_trials[features].to_numpy(float), has_constant="add")
    y = df_trials["y"].to_numpy(float)
    groups = pd.factorize(df_trials["material_id"])[0]
    model = sm.GLM(y, X, family=sm.families.Binomial())
    res = model.fit(cov_type="cluster", cov_kwds={"groups": groups}, maxiter=200, tol=1e-10)
    return res


def predict_logistic(res, df: pd.DataFrame, features: list[str]) -> np.ndarray:
    X = sm.add_constant(df[features].to_numpy(float), has_constant="add")
    return np.asarray(res.predict(X), dtype=float)


def fit_isotonic(df_mt: pd.DataFrame) -> IsotonicRegression:
    iso = IsotonicRegression(increasing=True, out_of_bounds="clip")
    iso.fit(df_mt["x"].to_numpy(float), df_mt["p_obs"].to_numpy(float),
            sample_weight=df_mt["n_trials"].to_numpy(float))
    return iso


def isotonic_cutoff(iso: IsotonicRegression, x_train: np.ndarray, p_star: float) -> float:
    """Largest training x at which the fitted isotonic risk is <= p_star (-inf if none)."""
    xs = np.sort(np.unique(x_train))
    fitted = iso.predict(xs)
    ok = xs[fitted <= p_star]
    return float(ok.max()) if ok.size else float("-inf")


# --------------------------------------------------------------------------- 10-fold CV
for mdl in MODELS:
    mt[f"risk_cv_{mdl}"] = np.nan
mt["risk_cv_gate"] = mt["gate_risk"]
for p_star in P_STARS + [P_STAR_GATE_COMPARISON]:
    mt[f"iso_cutoff_fold_p{p_star:g}"] = np.nan
fold_records = []
for k in range(N_FOLDS):
    tr_mt = mt[mt["fold"] != k]
    te_idx = mt.index[mt["fold"] == k]
    tr_tr = trials[trials["fold"] != k]
    rec = {"fold": k, "n_train_materials": int(tr_mt["material_id"].nunique()),
           "n_test_materials": int(mt.loc[te_idx, "material_id"].nunique())}
    for mdl, feats in FEATURES.items():
        res = fit_logistic(tr_tr, feats)
        mt.loc[te_idx, f"risk_cv_{mdl}"] = predict_logistic(res, mt.loc[te_idx], feats)
        rec[f"{mdl}_converged"] = bool(res.converged)
    iso = fit_isotonic(tr_mt)
    mt.loc[te_idx, "risk_cv_isotonic_x"] = iso.predict(mt.loc[te_idx, "x"].to_numpy(float))
    for p_star in P_STARS + [P_STAR_GATE_COMPARISON]:
        c = isotonic_cutoff(iso, tr_mt["x"].to_numpy(float), p_star)
        mt.loc[te_idx, f"iso_cutoff_fold_p{p_star:g}"] = c
        rec[f"iso_cutoff_p{p_star:g}"] = c
    fold_records.append(rec)
folds_df = pd.DataFrame(fold_records)
assert mt[[f"risk_cv_{m}" for m in MODELS]].notna().all().all()

# full-data fits (for the risk-vs-x curve, coefficients and the reported cutoff)
full_fits = {mdl: fit_logistic(trials, feats) for mdl, feats in FEATURES.items()}
iso_full = fit_isotonic(mt)
mt["risk_full_isotonic_x"] = iso_full.predict(mt["x"].to_numpy(float))
for mdl, feats in FEATURES.items():
    mt[f"risk_full_{mdl}"] = predict_logistic(full_fits[mdl], mt, feats)

coef_rows = []
for mdl, feats in FEATURES.items():
    res = full_fits[mdl]
    names = ["const"] + feats
    for i, nm in enumerate(names):
        coef_rows.append({"model": mdl, "term": nm, "coef": float(res.params[i]),
                          "se_cluster_material": float(res.bse[i]), "z": float(res.tvalues[i]),
                          "p_value": float(res.pvalues[i]), "ci95_low": float(res.conf_int()[i][0]),
                          "ci95_high": float(res.conf_int()[i][1]), "n_trials": int(len(trials)),
                          "n_clusters": 254, "converged": bool(res.converged)})
coef_df = pd.DataFrame(coef_rows)
coef_df.to_csv(OUT / "coefficients.csv", index=False)


# --------------------------------------------------------------------------- metrics
def brier(p, k, n):
    """Trial-level Brier score from material-level counts: mean over trials of (p - y)^2."""
    p = np.asarray(p, float); k = np.asarray(k, float); n = np.asarray(n, float)
    per = k * (1 - p) ** 2 + (n - k) * p ** 2
    return per.sum() / n.sum()


def logloss(p, k, n):
    p = np.clip(np.asarray(p, float), LOGLOSS_EPS, 1 - LOGLOSS_EPS)
    k = np.asarray(k, float); n = np.asarray(n, float)
    per = -(k * np.log(p) + (n - k) * np.log1p(-p))
    return per.sum() / n.sum()


def auc_trials(p, k, n):
    """Trial-level AUC (Mann-Whitney with ties = 0.5), predictions constant within (material, tau)."""
    p = np.asarray(p, float); k = np.asarray(k, float); n = np.asarray(n, float)
    order = np.argsort(p, kind="mergesort")
    p, k, n = p[order], k[order], n[order]
    pos = k; neg = n - k
    P = pos.sum(); N = neg.sum()
    if P == 0 or N == 0:
        return np.nan
    # group by distinct predicted value
    uniq, inv = np.unique(p, return_inverse=True)
    pos_g = np.bincount(inv, weights=pos); neg_g = np.bincount(inv, weights=neg)
    neg_below = np.concatenate([[0.0], np.cumsum(neg_g)[:-1]])
    stat = (pos_g * (neg_below + 0.5 * neg_g)).sum()
    return stat / (P * N)


def equal_count_bins(p, tiebreak, n_bins=N_BINS):
    order = np.lexsort((np.asarray(tiebreak), np.asarray(p, float)))
    ranks = np.empty(len(p), int); ranks[order] = np.arange(len(p))
    return (ranks * n_bins) // len(p)


def reliability(p, k, n, tiebreak, n_bins=N_BINS):
    b = equal_count_bins(p, tiebreak, n_bins)
    out = []
    p = np.asarray(p, float); k = np.asarray(k, float); n = np.asarray(n, float)
    for j in range(n_bins):
        sel = b == j
        w = n[sel].sum()
        out.append({"bin": j, "n_materials": int(sel.sum()), "n_trials": int(w),
                    "pred_min": float(p[sel].min()), "pred_max": float(p[sel].max()),
                    "mean_predicted": float((p[sel] * n[sel]).sum() / w),
                    "n_exceed": int(k[sel].sum()), "observed": float(k[sel].sum() / w)})
    return pd.DataFrame(out)


def ece(p, k, n, tiebreak, n_bins=N_BINS):
    r = reliability(p, k, n, tiebreak, n_bins)
    w = r["n_trials"] / r["n_trials"].sum()
    return float((w * (r["mean_predicted"] - r["observed"]).abs()).sum())


def all_metrics(df: pd.DataFrame, col: str) -> dict:
    p = df[col].to_numpy(float); k = df["n_exceed"].to_numpy(float); n = df["n_trials"].to_numpy(float)
    tb = df["_tiebreak"].to_numpy()
    return {"brier": brier(p, k, n), "log_loss": logloss(p, k, n), "auc": auc_trials(p, k, n),
            "ece_10bin": ece(p, k, n, tb)}


rng = np.random.default_rng(SEED)
boot_idx = [rng.integers(0, 254, size=254) for _ in range(N_BOOT)]
mat_index = {m: i for i, m in enumerate(mats)}
mt["_mi"] = mt["material_id"].map(mat_index)
by_mat = [mt.index[mt["_mi"] == i].to_numpy() for i in range(254)]


def resample(df_idx_by_mat, sample):
    return np.concatenate([df_idx_by_mat[i] for i in sample])


def bootstrap_metrics(df: pd.DataFrame, cols: list[str], subsets: dict):
    """Return long table of metrics with material-cluster bootstrap 95% CIs for each subset."""
    records = []
    sub_masks = {name: mask for name, mask in subsets.items()}
    # point estimates
    point = {}
    for sname, mask in sub_masks.items():
        d = df[mask]
        for c in cols:
            point[(sname, c)] = all_metrics(d, c)
        for c in cols:
            if c != "risk_cv_gate":
                point[(sname, c, "diff")] = {
                    "brier_diff_vs_gate": point[(sname, c)]["brier"] - point[(sname, "risk_cv_gate")]["brier"],
                    "log_loss_diff_vs_gate": point[(sname, c)]["log_loss"] - point[(sname, "risk_cv_gate")]["log_loss"],
                }
    # bootstrap
    boot = {key: {mname: [] for mname in ["brier", "log_loss", "auc", "ece_10bin"]} for key in point if len(key) == 2}
    boot_diff = {key: {"brier_diff_vs_gate": [], "log_loss_diff_vs_gate": []} for key in point if len(key) == 3}
    mi_by_mat_local = {}
    for sname, mask in sub_masks.items():
        d = df[mask]
        mi_by_mat_local[sname] = [d.index[d["_mi"] == i].to_numpy() for i in range(254)]
    for b in range(N_BOOT):
        samp = boot_idx[b]
        for sname, mask in sub_masks.items():
            d = df.loc[resample(mi_by_mat_local[sname], samp)]
            vals = {c: all_metrics(d, c) for c in cols}
            for c in cols:
                for mname, v in vals[c].items():
                    boot[(sname, c)][mname].append(v)
                if c != "risk_cv_gate":
                    boot_diff[(sname, c, "diff")]["brier_diff_vs_gate"].append(vals[c]["brier"] - vals["risk_cv_gate"]["brier"])
                    boot_diff[(sname, c, "diff")]["log_loss_diff_vs_gate"].append(vals[c]["log_loss"] - vals["risk_cv_gate"]["log_loss"])
    for (sname, c), mdict in boot.items():
        for mname, arr in mdict.items():
            arr = np.asarray(arr, float)
            records.append({"subset": sname, "model": c.replace("risk_cv_", ""), "metric": mname,
                            "value": point[(sname, c)][mname], "ci95_low": float(np.nanpercentile(arr, 2.5)),
                            "ci95_high": float(np.nanpercentile(arr, 97.5)), "n_boot": N_BOOT,
                            "n_materials": int(df[sub_masks[sname]]["material_id"].nunique()),
                            "n_material_tau_rows": int(sub_masks[sname].sum()),
                            "n_trials": int(df[sub_masks[sname]]["n_trials"].sum())})
    for (sname, c, _), mdict in boot_diff.items():
        for mname, arr in mdict.items():
            arr = np.asarray(arr, float)
            records.append({"subset": sname, "model": c.replace("risk_cv_", ""), "metric": mname,
                            "value": point[(sname, c, "diff")][mname], "ci95_low": float(np.percentile(arr, 2.5)),
                            "ci95_high": float(np.percentile(arr, 97.5)), "n_boot": N_BOOT,
                            "n_materials": int(df[sub_masks[sname]]["material_id"].nunique()),
                            "n_material_tau_rows": int(sub_masks[sname].sum()),
                            "n_trials": int(df[sub_masks[sname]]["n_trials"].sum())})
    return pd.DataFrame(records)


subsets = {"pooled_all_tau": np.ones(len(mt), bool)}
for tau in TAUS:
    subsets[f"tau_{tau:g}"] = (mt["tau_e"] == tau).to_numpy()
cv_cols = [f"risk_cv_{m}" for m in MODELS]
t_metrics = time.time()
cv_metrics = bootstrap_metrics(mt, cv_cols, subsets)
print("metrics + bootstrap seconds:", round(time.time() - t_metrics, 1))
cv_metrics.to_csv(OUT / "cv_metrics.csv", index=False)

# reliability tables (held-out), pooled and per tau
rel_rows = []
for sname, mask in subsets.items():
    d = mt[mask]
    for mdl in MODELS:
        r = reliability(d[f"risk_cv_{mdl}"].to_numpy(float), d["n_exceed"].to_numpy(float),
                        d["n_trials"].to_numpy(float), d["_tiebreak"].to_numpy())
        r.insert(0, "model", mdl); r.insert(0, "subset", sname)
        rel_rows.append(r)
reliability_df = pd.concat(rel_rows, ignore_index=True)
reliability_df.to_csv(OUT / "reliability.csv", index=False)

# --------------------------------------------------------------------------- contract table
contract_rows = []
gate_rows = []
for tau in TAUS:
    d = mt[mt["tau_e"] == tau]
    adm = d["gate_eligible"] == 1
    k_adm = int(d.loc[adm, "n_exceed"].sum()); n_adm = int(d.loc[adm, "n_trials"].sum())
    # bootstrap coverage and observed rate over materials
    cov_b, rate_b = [], []
    dd = d.set_index("_mi").sort_index()
    for b in range(N_BOOT):
        s = dd.loc[boot_idx[b]]
        a = s["gate_eligible"] == 1
        cov_b.append(a.mean())
        nn = s.loc[a, "n_trials"].sum()
        rate_b.append(s.loc[a, "n_exceed"].sum() / nn if nn > 0 else np.nan)
    gate_rows.append({"rule": "binary_gate", "p_star": np.nan, "tau_e": tau, "x_cutoff": 0.0,
                      "x_cutoff_fold_min": 0.0, "x_cutoff_fold_median": 0.0, "x_cutoff_fold_max": 0.0,
                      "n_admitted": int(adm.sum()), "n_materials": 254, "coverage": float(adm.mean()),
                      "coverage_ci95_low": float(np.percentile(cov_b, 2.5)), "coverage_ci95_high": float(np.percentile(cov_b, 97.5)),
                      "admitted_exceedances": k_adm, "admitted_trials": n_adm,
                      "observed_rate": k_adm / n_adm if n_adm else np.nan,
                      "observed_rate_ci95_low": float(np.nanpercentile(rate_b, 2.5)),
                      "observed_rate_ci95_high": float(np.nanpercentile(rate_b, 97.5))})
for p_star in P_STARS + [P_STAR_GATE_COMPARISON]:
    col = f"iso_cutoff_fold_p{p_star:g}"
    fold_cuts = folds_df[f"iso_cutoff_p{p_star:g}"].to_numpy(float)
    x_full = isotonic_cutoff(iso_full, mt["x"].to_numpy(float), p_star)
    for tau in TAUS:
        d = mt[mt["tau_e"] == tau]
        adm = d["x"] <= d[col]  # held-out admission: cutoff from the training folds only
        k_adm = int(d.loc[adm, "n_exceed"].sum()); n_adm = int(d.loc[adm, "n_trials"].sum())
        cov_b, rate_b = [], []
        dd = d.set_index("_mi").sort_index()
        for b in range(N_BOOT):
            s = dd.loc[boot_idx[b]]
            a = s["x"] <= s[col]
            cov_b.append(a.mean())
            nn = s.loc[a, "n_trials"].sum()
            rate_b.append(s.loc[a, "n_exceed"].sum() / nn if nn > 0 else np.nan)
        contract_rows.append({
            "rule": "isotonic_cv" if p_star in P_STARS else "isotonic_cv_gate_risk_comparison",
            "p_star": p_star, "tau_e": tau, "x_cutoff": x_full,
            "x_cutoff_fold_min": float(np.min(fold_cuts)), "x_cutoff_fold_median": float(np.median(fold_cuts)),
            "x_cutoff_fold_max": float(np.max(fold_cuts)),
            "n_admitted": int(adm.sum()), "n_materials": 254, "coverage": float(adm.mean()),
            "coverage_ci95_low": float(np.percentile(cov_b, 2.5)), "coverage_ci95_high": float(np.percentile(cov_b, 97.5)),
            "admitted_exceedances": k_adm, "admitted_trials": n_adm,
            "observed_rate": k_adm / n_adm if n_adm else np.nan,
            "observed_rate_ci95_low": float(np.nanpercentile(rate_b, 2.5)) if n_adm else np.nan,
            "observed_rate_ci95_high": float(np.nanpercentile(rate_b, 97.5)) if n_adm else np.nan,
        })
contract_df = pd.DataFrame(contract_rows + gate_rows)
contract_df.to_csv(OUT / "contract_table.csv", index=False)
folds_df.to_csv(OUT / "cv_folds.csv", index=False)

# --------------------------------------------------------------------------- material_risk.csv
mr = mt.drop(columns=["_tiebreak", "_mi"]).copy()
mr = mr.sort_values(["tau_e", "material_id"]).reset_index(drop=True)
mr.to_csv(OUT / "material_risk.csv", index=False)

# --------------------------------------------------------------------------- acceptance
pooled = cv_metrics[cv_metrics["subset"] == "pooled_all_tau"]
brier_pt = pooled[pooled["metric"] == "brier"].set_index("model")
best_model = brier_pt.loc[[m for m in MODELS if m != "gate"], "value"].idxmin()
iso_diff = pooled[(pooled["model"] == "isotonic_x") & (pooled["metric"] == "brier_diff_vs_gate")].iloc[0]
best_diff = pooled[(pooled["model"] == best_model) & (pooled["metric"] == "brier_diff_vs_gate")].iloc[0]
c2 = contract_df[(contract_df["rule"] == "isotonic_cv") & (contract_df["p_star"] == 0.02) & (contract_df["tau_e"] == 1e-3)].iloc[0]
cond_i_iso = bool(iso_diff["value"] < 0 and iso_diff["ci95_high"] < 0)
cond_i_best = bool(best_diff["value"] < 0 and best_diff["ci95_high"] < 0)
cond_ii = bool(c2["coverage"] > 0.563)
verdict = {
    "condition_i_isotonic_brier_below_gate_ci_excludes_zero": cond_i_iso,
    "condition_i_best_model": best_model,
    "condition_i_best_model_brier_below_gate_ci_excludes_zero": cond_i_best,
    "condition_ii_coverage_at_p2pct_tau1e-3_exceeds_0.563": cond_ii,
    "coverage_at_p2pct_tau1e-3": float(c2["coverage"]),
    "n_admitted_at_p2pct_tau1e-3": int(c2["n_admitted"]),
    "accepted_isotonic_contract": bool(cond_i_iso and cond_ii),
    "accepted_any_model": bool(cond_i_best and cond_ii),
}
print("verdict:", verdict)

# --------------------------------------------------------------------------- figure
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

COL = {"gate": "#4a4a4a", "logistic_x": "#2a78d6", "isotonic_x": "#eb6834", "logistic_x_secondary": "#1baf7a"}
TAU_COL = {1e-4: "#9ec5f4", 1e-3: "#2a78d6", 1e-2: "#104281"}
fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8))
ax = axes[0]
rel_pooled = reliability_df[reliability_df["subset"] == "pooled_all_tau"]
floor_p = 2e-4
ax.plot([floor_p, 1], [floor_p, 1], color="#bbbbbb", lw=1, ls="--", zorder=1)
for mdl in MODELS:
    r = rel_pooled[rel_pooled["model"] == mdl]
    ax.plot(np.clip(r["mean_predicted"], floor_p, 1), np.clip(r["observed"], floor_p, 1),
            marker="o", ms=5, lw=1.6, color=COL[mdl], label=MODEL_LABEL[mdl], zorder=3)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(floor_p, 1.05); ax.set_ylim(floor_p, 1.05)
ax.set_xlabel("Mean predicted exceedance risk (held-out, 10 equal-count bins)")
ax.set_ylabel("Observed exceedance rate in bin")
ax.set_title("(a) Reliability, pooled over tau (762 material-tau rows)", loc="left", fontsize=10)
ax.legend(frameon=False, fontsize=8, loc="upper left")
ax.text(0.98, 0.03, f"values below {floor_p:g} drawn at {floor_p:g}", transform=ax.transAxes, ha="right", fontsize=7, color="#555555")
ax.grid(True, which="major", color="#eeeeee", lw=0.6)

ax = axes[1]
floor_y = 1e-3
xs = np.linspace(mt["x"].min() - 0.2, mt["x"].max() + 0.2, 800)
for tau in TAUS:
    d = mt[mt["tau_e"] == tau]
    ax.scatter(d["x"], np.clip(d["p_obs"], floor_y, 1), s=12, color=TAU_COL[tau], alpha=0.75,
               edgecolor="white", linewidth=0.3, label=f"materials, tau = {tau:g} e (p_m)", zorder=2)
ax.step(xs, np.clip(iso_full.predict(xs), floor_y, 1), where="post", color=COL["isotonic_x"], lw=2,
        label="isotonic on x (all 254)", zorder=4)
res = full_fits["logistic_x"]
for tau, ls in zip(TAUS, [":", "-", "--"]):
    Xg = sm.add_constant(np.column_stack([xs, np.full_like(xs, np.log10(tau))]), has_constant="add")
    ax.plot(xs, np.clip(res.predict(Xg), floor_y, 1), color=COL["logistic_x"], lw=1.4, ls=ls,
            label=f"logistic on x, tau = {tau:g} e", zorder=3)
ax.step([xs.min(), 0, 0, xs.max()], [GATE_RISK_LOW, GATE_RISK_LOW, GATE_RISK_HIGH, GATE_RISK_HIGH], where="post",
        color=COL["gate"], lw=1.4, label="binary gate (1.600% / 81.325%)", zorder=3)
ax.axvline(0, color="#bbbbbb", lw=0.8, ls="--", zorder=1)
ax.set_yscale("log"); ax.set_ylim(floor_y * 0.8, 1.2)
n_lo = int((mt["x"] < -3).sum()); n_hi = int((mt["x"] > 3).sum())
assert (mt.loc[mt["x"] < -3, "p_obs"] == 0).all() and (mt.loc[mt["x"] > 3, "p_obs"] == 1).all()
ax.set_xlim(-3.2, 3.2)
ax.text(0.02, 0.60, f"{n_lo} rows with x < -3 (all p_m = 0) and\n{n_hi} with x > 3 (all p_m = 1) lie outside the axis",
        transform=ax.transAxes, va="top", fontsize=7, color="#555555")
ax.set_xlabel("x = log10(f_m / tau)")
ax.set_ylabel("Fresh-trial exceedance risk P(response >= tau)")
ax.set_title("(b) Risk versus the QSQ statistic", loc="left", fontsize=10)
ax.legend(frameon=False, fontsize=7, loc="lower right")
ax.text(0.02, 0.97, f"p_m = 0 drawn at {floor_y:g}", transform=ax.transAxes, va="top", fontsize=7, color="#555555")
ax.grid(True, which="major", color="#eeeeee", lw=0.6)
fig.tight_layout()
fig.savefig(OUT / "fig_calibration.png", dpi=200)
fig.savefig(OUT / "fig_calibration.svg")
plt.close(fig)

# --------------------------------------------------------------------------- provenance
def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()

pip_freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True)
if pip_freeze.returncode != 0:
    pip_freeze = subprocess.run(["uv", "pip", "freeze", "--python", sys.executable], capture_output=True, text=True)
import matplotlib as _mpl, scipy as _scipy, sklearn as _sklearn, statsmodels as _sm
provenance = {
    "package": "WP-A",
    "protocol": "analysis/extensions_20260928/PROTOCOL.md",
    "protocol_sha256": sha256_file(ROOT / "analysis/extensions_20260928/PROTOCOL.md"),
    "repo_head_commit": git("rev-parse", "HEAD"),
    "repo_base_branch": "paper-20260927",
    "scientific_source_commit_codecs_bader": "893f931b3045b0b628329db81999c2f439d4e830",
    "inputs_sha256": {k: {"path": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(p), "bytes": p.stat().st_size}
                      for k, p in INPUTS.items()},
    "anchors": anchors,
    "seed": SEED, "n_folds": N_FOLDS, "n_bootstrap": N_BOOT, "taus_e": TAUS, "p_stars": P_STARS,
    "fold_rule": "fold = int(sha256('20260928|' + material_id).hexdigest(), 16) mod 10",
    "fold_sizes_materials": {int(k): int(v) for k, v in fold_sizes.items()},
    "gate_risks": {"x_lt_0": GATE_RISK_LOW, "x_ge_0": GATE_RISK_HIGH},
    "logloss_clip_eps": LOGLOSS_EPS,
    "python": sys.version, "platform": platform.platform(),
    "package_versions": {"numpy": np.__version__, "pandas": pd.__version__, "scipy": _scipy.__version__,
                         "scikit-learn": _sklearn.__version__, "statsmodels": _sm.__version__, "matplotlib": _mpl.__version__},
    "pip_freeze": pip_freeze.stdout.splitlines(),
    "verdict": verdict,
    "wall_time_seconds": round(time.time() - T0, 1),
    "outputs": ["material_risk.csv", "cv_metrics.csv", "reliability.csv", "contract_table.csv", "coefficients.csv",
                "cv_folds.csv", "fig_calibration.png", "fig_calibration.svg", "RESULTS.md", "provenance.json"],
}
with open(OUT / "provenance.json", "w", encoding="utf-8") as fh:
    json.dump(provenance, fh, indent=2)
print("wall time s:", provenance["wall_time_seconds"])
