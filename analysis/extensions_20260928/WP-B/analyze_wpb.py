#!/usr/bin/env python3
"""WP-B pre-declared analyses 1-5, acceptance rule, summary.csv, RESULTS.md, provenance.json.

Every number in RESULTS.md is read from the machine-readable outputs of run_wpb.py
(cp_reference.csv, cp_rows.csv, cp_probes.csv, failures.csv) and written to summary.csv
before it is rendered. Material-cluster bootstrap: 2,000 resamples, seed 20260928.
"""
from __future__ import annotations

import hashlib
import importlib.metadata as md
import json
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

SCRIPT_DIR = Path(__file__).resolve().parent
# optional first argument: directory holding run_wpb.py outputs (smoke runs); default is this directory
HERE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else SCRIPT_DIR
REPO_ROOT = SCRIPT_DIR.parents[2]
FROZEN_REPO = Path(r"D:\Research\QoI-final4-local\frozen_repo")
BOOT_N = 2000
BOOT_SEED = 20260928
TAU_CP = (0, 1, 2)
TAU_BADER = 1e-3
CODEC_ORDER = ["ZFP", "SZ3", "SPERR"]

SUMMARY_ROWS: list[dict[str, Any]] = []


def add(analysis: str, metric: str, value: Any, *, group: str = "", ci_low: Any = "", ci_high: Any = "",
        numerator: Any = "", denominator: Any = "", note: str = "") -> None:
    SUMMARY_ROWS.append({
        "analysis": analysis, "metric": metric, "group": group, "value": value, "ci95_low": ci_low,
        "ci95_high": ci_high, "numerator": numerator, "denominator": denominator, "note": note,
    })


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head(path: Path) -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=path, capture_output=True, text=True, check=True).stdout.strip()
    except Exception as exc:  # noqa: BLE001
        return f"unavailable: {exc}"


# ----------------------------------------------------------------------------
# material-cluster bootstrap
# ----------------------------------------------------------------------------
class ClusterBootstrap:
    """Resample materials with replacement; statistics are functions of the resampled material list."""

    def __init__(self, materials: list[str], n: int = BOOT_N, seed: int = BOOT_SEED):
        self.materials = np.asarray(sorted(materials))
        self.rng = np.random.Generator(np.random.PCG64(seed))
        self.n = n
        self.samples = [self.rng.integers(0, len(self.materials), size=len(self.materials)) for _ in range(n)]

    def ci(self, stat_fn, alpha: float = 0.05) -> tuple[float, float, np.ndarray]:
        vals = np.array([stat_fn(self.materials[idx]) for idx in self.samples], dtype=float)
        if np.isnan(vals).any():
            return float("nan"), float("nan"), vals
        # percentile interval (linear interpolation between order statistics); +inf resamples sit at the
        # top of the order and an interpolation that touches one yields +inf rather than inf - inf = nan
        return _percentile_inf(vals, 100 * alpha / 2), _percentile_inf(vals, 100 * (1 - alpha / 2)), vals


def _percentile_inf(vals: np.ndarray, q: float) -> float:
    s = np.sort(vals)
    pos = q / 100 * (s.size - 1)
    i, j = int(np.floor(pos)), int(np.ceil(pos))
    if i == j:
        return float(s[i])
    if np.isinf(s[j]):
        return float("inf")
    return float(s[i] + (s[j] - s[i]) * (pos - i))


def rate_from_counts(num: np.ndarray, den: np.ndarray, idx: np.ndarray) -> float:
    d = float(den[idx].sum())
    return float(num[idx].sum() / d) if d > 0 else float("nan")


def cohen_kappa(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=int)
    b = np.asarray(b, dtype=int)
    n = a.size
    if n == 0:
        return float("nan")
    po = float(np.mean(a == b))
    pe = float(np.mean(a) * np.mean(b) + (1 - np.mean(a)) * (1 - np.mean(b)))
    return float("nan") if pe == 1.0 else (po - pe) / (1 - pe)


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    if len(x) < 3 or np.all(x == x[0]) or np.all(y == y[0]):
        return float("nan")
    return float(stats.spearmanr(x, y).statistic)


def fmt(x: Any, nd: int = 4) -> str:
    if isinstance(x, str):
        return x
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "n/a"
    if isinstance(x, float) and np.isinf(x):
        return "inf"
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    return f"{x:.{nd}g}"


def pct(x: float) -> str:
    return "n/a" if not np.isfinite(x) else f"{100 * x:.2f}%"


# ----------------------------------------------------------------------------
def main() -> int:
    t_start = time.time()
    ref = pd.read_csv(HERE / "cp_reference.csv")
    rows = pd.read_csv(HERE / "cp_rows.csv")
    probes = pd.read_csv(HERE / "cp_probes.csv")
    failures = pd.read_csv(HERE / "failures.csv")
    population = json.loads((HERE / "population.json").read_text(encoding="utf-8"))
    agg_counts = json.loads((HERE / "aggregate_counts.json").read_text(encoding="utf-8"))
    run_status = pd.read_csv(HERE / "material_run_status.csv")
    floors = pd.read_csv(REPO_ROOT / "stability" / "stability_floor_A1.csv").set_index("material_id")
    bench = pd.read_csv(REPO_ROOT / "benchmark" / "master_benchmark_full.csv")
    meta = pd.read_csv(REPO_ROOT / "materials_metadata.csv").set_index("material_id")

    materials = sorted(ref["material_id"].tolist())
    n_materials = len(materials)
    assert n_materials == population["materials"]
    ref_ok = ref[ref["status"] == "SUCCESS"].set_index("material_id")

    # ---------------- population and accounting ----------------
    planned_rows = population["reconstruction_rows_planned"]
    planned_probes = population["qsq_seed_probes_planned"] + population["fresh_probes_planned"]
    n_fail_rows = int((failures["kind"] == "reconstruction").sum())
    n_fail_probes = int((failures["kind"] == "probe").sum())
    n_gate_fail = int((failures["stage"] == "reproduction_gate").sum())
    n_rows_success = int((rows["status"] == "SUCCESS").sum())
    n_rows_gate_fail_listed = int((rows["status"] == "GATE_FAIL").sum())
    n_probes_success = int((probes["status"] == "SUCCESS").sum())
    add("population", "population", population["population"])
    add("population", "materials", n_materials)
    add("population", "reconstruction_rows_planned", planned_rows)
    add("population", "reconstruction_rows_scored", n_rows_success, denominator=planned_rows)
    add("population", "reconstruction_rows_gate_fail", n_rows_gate_fail_listed, denominator=planned_rows)
    add("population", "reconstruction_rows_other_failure", n_fail_rows - n_gate_fail, denominator=planned_rows)
    add("population", "probes_planned", planned_probes)
    add("population", "probes_scored", n_probes_success, denominator=planned_probes)
    add("population", "probes_failed", n_fail_probes, denominator=planned_probes)
    add("population", "materials_reference_failed", int((ref["status"] != "SUCCESS").sum()), denominator=n_materials)
    accounted_rows = n_rows_success + n_fail_rows
    accounted_probes = n_probes_success + n_fail_probes
    add("population", "rows_accounted", accounted_rows, denominator=planned_rows,
        note="scored + failed (gate failures are listed in cp_rows.csv and failures.csv)")
    add("population", "probes_accounted", accounted_probes, denominator=planned_probes)
    if accounted_rows != planned_rows or accounted_probes != planned_probes:
        raise RuntimeError(f"accounting mismatch rows {accounted_rows}/{planned_rows} probes {accounted_probes}/{planned_probes}")

    # reproduction checks on the frozen stack
    ok_rows = rows[rows["status"] == "SUCCESS"].copy()
    add("reproduction", "realized_over_stored_min", float(rows["realized_over_stored"].min()))
    add("reproduction", "realized_over_stored_max", float(rows["realized_over_stored"].max()))
    add("reproduction", "rows_bader_rederived_within_1e-6_e_of_stored", int((ok_rows["bader_error_abs_diff_vs_stored_e"] <= 1e-6).sum()), denominator=len(ok_rows))
    add("reproduction", "rows_bader_rederived_abs_diff_max_e", float(ok_rows["bader_error_abs_diff_vs_stored_e"].max()))
    add("reproduction", "rows_bader_rederived_same_side_of_1e-3_e", int(((ok_rows["bader_error_resolved_e"] >= 1e-3) == (ok_rows["stored_Bader_error_resolved_e"] >= 1e-3)).sum()), denominator=len(ok_rows))
    fresh_ok = probes[(probes["family"] == "fresh_iid") & (probes["status"] == "SUCCESS")]
    seed_ok = probes[(probes["family"] == "qsq_seed") & (probes["status"] == "SUCCESS")]
    add("reproduction", "fresh_probes_bader_within_1e-6_e_of_frozen_P2", int((fresh_ok["bader_response_abs_diff_vs_frozen_e"] <= 1e-6).sum()), denominator=len(fresh_ok))
    add("reproduction", "fresh_probes_bader_abs_diff_max_e", float(fresh_ok["bader_response_abs_diff_vs_frozen_e"].max()))
    add("reproduction", "qsq_seed_probes_bader_within_1e-6_e_of_frozen", int((seed_ok["bader_response_abs_diff_vs_frozen_e"] <= 1e-6).sum()), denominator=len(seed_ok))
    add("reproduction", "qsq_seed_probes_bader_abs_diff_max_e", float(seed_ok["bader_response_abs_diff_vs_frozen_e"].max()))
    add("reproduction", "materials_n_max_equals_baderkit_maxima", int((ref_ok["n_max"] == ref_ok["baderkit_n_maxima"]).sum()), denominator=len(ref_ok))

    # ---------------- reference QoI description ----------------
    add("reference", "n_max_median", float(ref_ok["n_max"].median()))
    add("reference", "n_max_min", int(ref_ok["n_max"].min()))
    add("reference", "n_max_max", int(ref_ok["n_max"].max()))
    add("reference", "n_min_median", float(ref_ok["n_min"].median()))
    add("reference", "materials_with_n_max_equal_natoms", int((ref_ok["n_max"] == ref_ok["natoms"]).sum()), denominator=len(ref_ok))
    add("reference", "materials_with_maxima_in_vacuum_basin", int((ref_ok["n_max_in_vacuum_basin"] > 0).sum()), denominator=len(ref_ok))
    add("reference", "materials_with_atom_lacking_maximum", int((ref_ok["n_atoms_with_zero_maxima"] > 0).sum()), denominator=len(ref_ok))

    # ---------------- analysis 1: QSQ-cp floor and eligibility ----------------
    seed_tab = seed_ok.pivot_table(index="material_id", columns="seed_label", values="delta_n_max", aggfunc="first")
    jd_tab = seed_ok.pivot_table(index="material_id", columns="seed_label", values="jaccard_distance", aggfunc="first")
    per_mat = pd.DataFrame(index=materials)
    per_mat["system_type"] = meta.loc[materials, "system_type"].values
    per_mat["n_seed_scored"] = seed_ok.groupby("material_id").size().reindex(materials).fillna(0).astype(int)
    per_mat["f_cp"] = seed_tab.max(axis=1).reindex(materials)
    per_mat["f_cp_setchange_any"] = (jd_tab > 0).any(axis=1).reindex(materials)
    per_mat["jaccard_max_over_seeds"] = jd_tab.max(axis=1).reindex(materials)
    complete = per_mat["n_seed_scored"] == 5
    per_mat["floor_defined"] = complete
    # eligibility: materials with any failed seed are non-evaluable and count as screen-rejected
    per_mat["cp_eligible_tau0"] = complete & (per_mat["f_cp"] == 0) & (~per_mat["f_cp_setchange_any"].fillna(True).astype(bool))
    per_mat["cp_eligible_tau0_count_only"] = complete & (per_mat["f_cp"] == 0)
    per_mat["cp_eligible_tau1"] = complete & (per_mat["f_cp"] <= 1)
    per_mat["cp_eligible_tau2"] = complete & (per_mat["f_cp"] <= 2)
    per_mat["stability_floor_A1_e"] = floors.loc[materials, "stability_floor_A1_e"].values
    per_mat["log10_f_bader"] = np.log10(per_mat["stability_floor_A1_e"])
    per_mat["bader_eligible_1e-3"] = per_mat["stability_floor_A1_e"] < TAU_BADER
    bench_elig = bench.drop_duplicates("material_id").set_index("material_id")["eligible_A1_at_0.001"]
    if not (bench_elig.reindex(materials).astype(bool).values == per_mat["bader_eligible_1e-3"].values).all():
        raise RuntimeError("Bader eligibility at 1e-3 e disagrees with the frozen benchmark column")

    add("A1", "materials_floor_defined", int(complete.sum()), denominator=n_materials)
    add("A1", "f_cp_median", float(per_mat.loc[complete, "f_cp"].median()))
    add("A1", "f_cp_zero_count", int((per_mat.loc[complete, "f_cp"] == 0).sum()), denominator=n_materials)
    for q in (0.5, 0.75, 0.9, 0.95):
        add("A1", f"f_cp_quantile_{q}", float(per_mat.loc[complete, "f_cp"].quantile(q)))
    add("A1", "f_cp_max", float(per_mat.loc[complete, "f_cp"].max()))
    for tau in TAU_CP:
        col = f"cp_eligible_tau{tau}"
        n_el = int(per_mat[col].sum())
        add("A1", f"cp_eligible_tau{tau}_materials", n_el, denominator=n_materials, group=f"tau_cp={tau}",
            note="tau_cp=0 requires an identical maximum-voxel set on all five seeds" if tau == 0 else "f_cp <= tau_cp")
        for st in ("bulk", "slab"):
            sub = per_mat[per_mat["system_type"] == st]
            add("A1", f"cp_eligible_tau{tau}_materials", int(sub[col].sum()), group=f"tau_cp={tau};{st}", denominator=len(sub))
    add("A1", "cp_eligible_tau0_count_only_materials", int(per_mat["cp_eligible_tau0_count_only"].sum()), denominator=n_materials,
        note="secondary: |delta n_max| = 0 on all five seeds without requiring set identity")

    # ---------------- analysis 2: prospective test (P2 form) ----------------
    fresh = fresh_ok.copy()
    fresh_fail = failures[(failures["kind"] == "probe") & (failures["family"] == "fresh_iid")]
    fresh["exceed"] = (fresh["delta_n_max"] >= 1).astype(int)
    fresh["exceed_set"] = (fresh["jaccard_distance"] > 0).astype(int)
    fresh["eligible"] = fresh["material_id"].map(per_mat["cp_eligible_tau0"]).astype(bool)
    boot = ClusterBootstrap(materials)

    def group_arrays(df: pd.DataFrame, col: str, mask_col: str, want: bool) -> tuple[np.ndarray, np.ndarray]:
        sub = df[df[mask_col] == want]
        num = sub.groupby("material_id")[col].sum().reindex(materials).fillna(0).values.astype(float)
        den = sub.groupby("material_id")[col].size().reindex(materials).fillna(0).values.astype(float)
        return num, den

    def prospective(df: pd.DataFrame, col: str, label: str, note: str) -> dict[str, float]:
        num_e, den_e = group_arrays(df, col, "eligible", True)
        num_r, den_r = group_arrays(df, col, "eligible", False)
        idx_all = np.arange(n_materials)
        pos = {m: i for i, m in enumerate(materials)}

        def to_idx(ms: np.ndarray) -> np.ndarray:
            return np.fromiter((pos[m] for m in ms), dtype=int, count=len(ms))

        rate_e = rate_from_counts(num_e, den_e, idx_all)
        rate_r = rate_from_counts(num_r, den_r, idx_all)
        rr = rate_r / rate_e if rate_e > 0 else (float("inf") if rate_r > 0 else float("nan"))
        lo_e, hi_e, _ = boot.ci(lambda ms: rate_from_counts(num_e, den_e, to_idx(ms)))
        lo_r, hi_r, _ = boot.ci(lambda ms: rate_from_counts(num_r, den_r, to_idx(ms)))

        def rr_fn(ms: np.ndarray) -> float:
            i = to_idx(ms)
            a = rate_from_counts(num_e, den_e, i)
            b = rate_from_counts(num_r, den_r, i)
            if not np.isfinite(a) or not np.isfinite(b):
                return float("nan")
            if a > 0:
                return b / a
            return float("inf") if b > 0 else float("nan")

        lo_rr, hi_rr, rr_vals = boot.ci(rr_fn)
        n_inf = int(np.isinf(rr_vals).sum())
        n_nan = int(np.isnan(rr_vals).sum())
        add("A2", f"{label}_exceedance_rate_eligible", rate_e, ci_low=lo_e, ci_high=hi_e,
            numerator=int(num_e.sum()), denominator=int(den_e.sum()), note=note)
        add("A2", f"{label}_exceedance_rate_rejected", rate_r, ci_low=lo_r, ci_high=hi_r,
            numerator=int(num_r.sum()), denominator=int(den_r.sum()), note=note)
        add("A2", f"{label}_risk_ratio_rejected_over_eligible", rr, ci_low=lo_rr, ci_high=hi_rr,
            note=f"{note}; bootstrap resamples with infinite RR: {n_inf}, undefined: {n_nan}")
        add("A2", f"{label}_materials_eligible", int((den_e > 0).sum()), denominator=n_materials)
        add("A2", f"{label}_materials_rejected", int((den_r > 0).sum()), denominator=n_materials)
        add("A2", f"{label}_materials_eligible_with_any_exceedance", int(((num_e > 0) & (den_e > 0)).sum()), denominator=int((den_e > 0).sum()))
        add("A2", f"{label}_materials_rejected_with_any_exceedance", int(((num_r > 0) & (den_r > 0)).sum()), denominator=int((den_r > 0).sum()))
        return {"rate_e": rate_e, "rate_r": rate_r, "rr": rr, "lo": lo_rr, "hi": hi_rr, "n_inf": n_inf, "n_nan": n_nan,
                "lo_e": lo_e, "hi_e": hi_e, "lo_r": lo_r, "hi_r": hi_r,
                "num_e": int(num_e.sum()), "den_e": int(den_e.sum()), "num_r": int(num_r.sum()), "den_r": int(den_r.sum()),
                "m_e": int((den_e > 0).sum()), "m_r": int((den_r > 0).sum())}

    primary = prospective(fresh, "exceed", "primary", "primary endpoint: |delta n_max| >= 1 on fresh trials; eligibility at tau_cp=0")
    secondary = prospective(fresh, "exceed_set", "setchange", "secondary endpoint: maximum-voxel set changed (Jaccard > 0)")
    add("A2", "fresh_trials_failed", len(fresh_fail), denominator=population["fresh_probes_planned"])
    # failure-as-exceedance sensitivity (only differs when failures exist)
    if len(fresh_fail):
        ff = fresh_fail.assign(delta_n_max=1, jaccard_distance=1.0, exceed=1, exceed_set=1)
        ff["eligible"] = ff["material_id"].map(per_mat["cp_eligible_tau0"]).astype(bool)
        prospective(pd.concat([fresh, ff[fresh.columns.intersection(ff.columns)]], ignore_index=True), "exceed", "primary_failures_as_exceedance",
                    "sensitivity: failed fresh trials counted as exceedances")

    # acceptance
    accepted = bool(np.isfinite(primary["rr"]) and primary["rr"] > 5 and primary["lo"] > 1) or bool(np.isinf(primary["rr"]) and primary["lo"] > 1)
    add("acceptance", "risk_ratio", primary["rr"], ci_low=primary["lo"], ci_high=primary["hi"])
    add("acceptance", "rule", "RR > 5 and 95% CI lower bound > 1")
    add("acceptance", "verdict", "QSQ_GENERALIZES_TO_CP_QOI" if accepted else "QSQ_DOES_NOT_GENERALIZE_TO_CP_QOI_ON_THESE_DATA")

    # ---------------- analysis 3: cross-QoI transfer ----------------
    a = per_mat["bader_eligible_1e-3"].astype(int).values
    b = per_mat["cp_eligible_tau0"].astype(int).values
    kappa = cohen_kappa(a, b)
    pos = {m: i for i, m in enumerate(materials)}

    def idx_of(ms: np.ndarray) -> np.ndarray:
        return np.fromiter((pos[m] for m in ms), dtype=int, count=len(ms))

    lo_k, hi_k, _ = boot.ci(lambda ms: cohen_kappa(a[idx_of(ms)], b[idx_of(ms)]))
    add("A3", "kappa_bader1e-3_vs_cp_tau0", kappa, ci_low=lo_k, ci_high=hi_k, denominator=n_materials)
    add("A3", "both_eligible", int(((a == 1) & (b == 1)).sum()), denominator=n_materials)
    add("A3", "bader_only_eligible", int(((a == 1) & (b == 0)).sum()), denominator=n_materials)
    add("A3", "cp_only_eligible", int(((a == 0) & (b == 1)).sum()), denominator=n_materials)
    add("A3", "neither_eligible", int(((a == 0) & (b == 0)).sum()), denominator=n_materials)
    add("A3", "agreement_fraction", float(np.mean(a == b)), denominator=n_materials)
    for tau in (1, 2):
        b2 = per_mat[f"cp_eligible_tau{tau}"].astype(int).values
        k2 = cohen_kappa(a, b2)
        lo2, hi2, _ = boot.ci(lambda ms, b2=b2: cohen_kappa(a[idx_of(ms)], b2[idx_of(ms)]))
        add("A3", f"kappa_bader1e-3_vs_cp_tau{tau}", k2, ci_low=lo2, ci_high=hi2, denominator=n_materials, note="secondary")
    x = per_mat["log10_f_bader"].values.astype(float)
    y = per_mat["f_cp"].values.astype(float)
    mask = complete.values & np.isfinite(x) & np.isfinite(y)
    rho = spearman(x[mask], y[mask])
    lo_r, hi_r, _ = boot.ci(lambda ms: spearman(x[idx_of(ms)][mask[idx_of(ms)]], y[idx_of(ms)][mask[idx_of(ms)]]))
    add("A3", "spearman_log10_f_bader_vs_f_cp", rho, ci_low=lo_r, ci_high=hi_r, denominator=int(mask.sum()))
    y2 = per_mat["jaccard_max_over_seeds"].values.astype(float)
    rho2 = spearman(x[mask], y2[mask])
    lo_r2, hi_r2, _ = boot.ci(lambda ms: spearman(x[idx_of(ms)][mask[idx_of(ms)]], y2[idx_of(ms)][mask[idx_of(ms)]]))
    add("A3", "spearman_log10_f_bader_vs_max_jaccard_over_seeds", rho2, ci_low=lo_r2, ci_high=hi_r2, denominator=int(mask.sum()), note="secondary")

    # ---------------- analysis 4: codec scoring ----------------
    ok_rows["cp_eligible_tau0"] = ok_rows["material_id"].map(per_mat["cp_eligible_tau0"]).astype(bool)
    ok_rows["cp_eligible_tau1"] = ok_rows["material_id"].map(per_mat["cp_eligible_tau1"]).astype(bool)
    ok_rows["cp_eligible_tau2"] = ok_rows["material_id"].map(per_mat["cp_eligible_tau2"]).astype(bool)
    ok_rows["dq0"] = (ok_rows["delta_n_max"] == 0)
    ok_rows["set_identical"] = (ok_rows["jaccard_distance"] == 0)
    add("A4", "gate_passing_rows", len(ok_rows), denominator=planned_rows)
    add("A4", "gate_passing_rows_delta0", int(ok_rows["dq0"].sum()), denominator=len(ok_rows), note="all gate-passing rows, pooled")
    add("A4", "gate_passing_rows_set_identical", int(ok_rows["set_identical"].sum()), denominator=len(ok_rows), note="all gate-passing rows, pooled")
    a4_table: list[dict[str, Any]] = []
    for codec in CODEC_ORDER:
        for tol, sub in ok_rows[ok_rows["codec"] == codec].groupby("nominal_tolerance_relative"):
            for elig_label, sub2 in (("cp_eligible_tau0", sub[sub["cp_eligible_tau0"]]), ("cp_rejected_tau0", sub[~sub["cp_eligible_tau0"]]), ("all", sub)):
                n = len(sub2)
                k = int(sub2["dq0"].sum())
                add("A4", "fraction_delta0", k / n if n else float("nan"), group=f"{codec};tol={tol:g};{elig_label}", numerator=k, denominator=n)
                a4_table.append({"codec": codec, "tol": tol, "split": elig_label, "n": n, "k": k, "frac": k / n if n else float("nan")})
    for codec in CODEC_ORDER:
        sub = ok_rows[ok_rows["codec"] == codec]
        for elig_label, sub2 in (("cp_eligible_tau0", sub[sub["cp_eligible_tau0"]]), ("cp_rejected_tau0", sub[~sub["cp_eligible_tau0"]])):
            n = len(sub2)
            k = int(sub2["dq0"].sum())
            add("A4", "fraction_delta0_pooled_over_tolerances", k / n if n else float("nan"), group=f"{codec};{elig_label}", numerator=k, denominator=n)
    # certified at tau_cp: rows of cp-eligible materials with delta <= tau (tau=0: identical set)
    cert_table: list[dict[str, Any]] = []
    for tau in TAU_CP:
        col = f"cp_eligible_tau{tau}"
        for codec in CODEC_ORDER:
            sub = ok_rows[(ok_rows["codec"] == codec) & ok_rows[col]]
            n = len(sub)
            if tau == 0:
                k = int(sub["set_identical"].sum())
            else:
                k = int((sub["delta_n_max"] <= tau).sum())
            add("A4", f"certified_at_tau{tau}_rate", k / n if n else float("nan"), group=f"{codec};eligible_rows", numerator=k, denominator=n,
                note="denominator = gate-passing rows of cp-eligible materials at this tau_cp")
            n_mat = int(sub["material_id"].nunique())
            cert_table.append({"tau": tau, "codec": codec, "k": k, "n": n, "n_mat": n_mat, "rate": k / n if n else float("nan")})
            # material-level: eligible material certified if any rung of the codec meets tau (best-rung)
            if n:
                mat_ok = sub.groupby("material_id").apply(lambda d: bool(d["set_identical"].any()) if tau == 0 else bool((d["delta_n_max"] <= tau).any()), include_groups=False)
                add("A4", f"certified_at_tau{tau}_materials_any_rung", int(mat_ok.sum()), group=f"{codec};eligible_materials", denominator=int(mat_ok.size))
        # ignoring eligibility (for the denominator contrast)
        sub_all = ok_rows[ok_rows["codec"].isin(CODEC_ORDER)]
        k_all = int(sub_all["set_identical"].sum()) if tau == 0 else int((sub_all["delta_n_max"] <= tau).sum())
        add("A4", f"delta_le_tau{tau}_rate_ignoring_eligibility", k_all / len(sub_all), group="all codecs", numerator=k_all, denominator=len(sub_all))

    # ---------------- analysis 5: operator contrast ----------------
    xb = ok_rows["bader_error_resolved_e"].values.astype(float)
    yc = ok_rows["delta_n_max"].values.astype(float)
    rho5 = spearman(yc, xb)
    row_mat = ok_rows["material_id"].values
    mat_rows: dict[str, np.ndarray] = {m: np.flatnonzero(row_mat == m) for m in materials}

    def rows_idx(ms: np.ndarray) -> np.ndarray:
        parts = [mat_rows[m] for m in ms if m in mat_rows]
        return np.concatenate(parts) if parts else np.empty(0, dtype=int)

    lo5, hi5, _ = boot.ci(lambda ms: spearman(yc[rows_idx(ms)], xb[rows_idx(ms)]))
    add("A5", "spearman_delta_n_max_vs_bader_error", rho5, ci_low=lo5, ci_high=hi5, denominator=len(ok_rows))
    yj = ok_rows["jaccard_distance"].values.astype(float)
    rho5j = spearman(yj, xb)
    lo5j, hi5j, _ = boot.ci(lambda ms: spearman(yj[rows_idx(ms)], xb[rows_idx(ms)]))
    add("A5", "spearman_jaccard_vs_bader_error", rho5j, ci_low=lo5j, ci_high=hi5j, denominator=len(ok_rows), note="secondary")
    cp0_badbad = int(((yc == 0) & (xb >= TAU_BADER)).sum())
    cp1_badgood = int(((yc >= 1) & (xb < TAU_BADER)).sum())
    both_bad = int(((yc >= 1) & (xb >= TAU_BADER)).sum())
    both_good = int(((yc == 0) & (xb < TAU_BADER)).sum())
    n5 = len(ok_rows)
    lo_a, hi_a, _ = boot.ci(lambda ms: float(np.mean((yc[rows_idx(ms)] == 0) & (xb[rows_idx(ms)] >= TAU_BADER))))
    lo_b, hi_b, _ = boot.ci(lambda ms: float(np.mean((yc[rows_idx(ms)] >= 1) & (xb[rows_idx(ms)] < TAU_BADER))))
    add("A5", "fraction_delta0_and_bader_ge_1e-3", cp0_badbad / n5, ci_low=lo_a, ci_high=hi_a, numerator=cp0_badbad, denominator=n5)
    add("A5", "fraction_delta_ge1_and_bader_lt_1e-3", cp1_badgood / n5, ci_low=lo_b, ci_high=hi_b, numerator=cp1_badgood, denominator=n5)
    add("A5", "fraction_delta_ge1_and_bader_ge_1e-3", both_bad / n5, numerator=both_bad, denominator=n5)
    add("A5", "fraction_delta0_and_bader_lt_1e-3", both_good / n5, numerator=both_good, denominator=n5)
    # conditional forms
    n_cp0 = int((yc == 0).sum())
    n_cp1 = int((yc >= 1).sum())
    add("A5", "P(bader_ge_1e-3 | delta0)", cp0_badbad / n_cp0 if n_cp0 else float("nan"), numerator=cp0_badbad, denominator=n_cp0)
    add("A5", "P(bader_lt_1e-3 | delta_ge1)", cp1_badgood / n_cp1 if n_cp1 else float("nan"), numerator=cp1_badgood, denominator=n_cp1)
    setch_badgood = int(((yj > 0) & (xb < TAU_BADER)).sum())
    set0_badbad = int(((yj == 0) & (xb >= TAU_BADER)).sum())
    add("A5", "fraction_set_identical_and_bader_ge_1e-3", set0_badbad / n5, numerator=set0_badbad, denominator=n5, note="secondary (set identity instead of count)")
    add("A5", "fraction_set_changed_and_bader_lt_1e-3", setch_badgood / n5, numerator=setch_badgood, denominator=n5, note="secondary (set identity instead of count)")
    # same contrast on the perturbation probes (same rows in the probe table)
    pr = probes[probes["status"] == "SUCCESS"]
    ypc = pr["delta_n_max"].values.astype(float)
    xpb = pr["bader_response_max_e"].values.astype(float)
    add("A5", "probes_fraction_delta0_and_bader_ge_1e-3", float(np.mean((ypc == 0) & (xpb >= TAU_BADER))), numerator=int(((ypc == 0) & (xpb >= TAU_BADER)).sum()), denominator=len(pr), note="perturbation probes (all 64 per material)")
    add("A5", "probes_fraction_delta_ge1_and_bader_lt_1e-3", float(np.mean((ypc >= 1) & (xpb < TAU_BADER))), numerator=int(((ypc >= 1) & (xpb < TAU_BADER)).sum()), denominator=len(pr), note="perturbation probes (all 64 per material)")
    add("A5", "probes_spearman_delta_n_max_vs_bader_response", spearman(ypc, xpb), denominator=len(pr), note="perturbation probes")

    # ---------------- wall time ----------------
    wall_material = float(run_status["wall_seconds"].sum())
    log_lines = (HERE / "run_log.txt").read_text(encoding="utf-8").splitlines() if (HERE / "run_log.txt").exists() else []
    invocation_walls = [float(l.split(":")[-1]) for l in log_lines if "execution wall seconds this invocation" in l]
    add("wall_time", "sum_material_wall_seconds", wall_material)
    add("wall_time", "sum_invocation_wall_seconds", float(sum(invocation_walls)))
    add("wall_time", "invocations", len(invocation_walls))

    # ---------------- outputs ----------------
    per_mat_out = per_mat.reset_index().rename(columns={"index": "material_id"})
    per_mat_out.to_csv(HERE / "cp_material_floors.csv", index=False)
    summary = pd.DataFrame(SUMMARY_ROWS)
    summary.to_csv(HERE / "summary.csv", index=False)

    # RESULTS.md
    S = {(r["analysis"], r["metric"], r["group"]): r for r in SUMMARY_ROWS}

    def g(analysis: str, metric: str, group: str = "") -> dict[str, Any]:
        return S[(analysis, metric, group)]

    L: list[str] = []
    L.append("# WP-B — Density critical points as a second topology-sensitive QoI: results")
    L.append("")
    L.append("All numbers below are read from `summary.csv`, which is computed by `analyze_wpb.py` from")
    L.append("`cp_reference.csv`, `cp_rows.csv`, `cp_probes.csv` and `failures.csv` (written by `run_wpb.py`).")
    L.append("Material-cluster bootstrap: 2,000 resamples, seed 20260928, percentile 95% intervals.")
    L.append("")
    L.append("## Population actually run (declared before any statistic was computed)")
    L.append("")
    L.append(f"- Population: **{population['population']}** (declared {population['declared_at']} in `population.json`).")
    L.append(f"- Materials: {n_materials} development materials (all rows of `materials_metadata.csv` with corpus `dev_*`).")
    L.append(f"- Reconstructions: all {planned_rows} rows of `benchmark/master_benchmark_full.csv` regenerated at the stored `nominal_tolerance_absolute` "
             f"(base and tight ladders, ZFP/SZ3/SPERR). Reproduction gate: realized L∞ within 0.95–1.05 of the stored `realized_Linf`.")
    L.append(f"- Perturbations: five QSQ seeds {population['qsq_seeds']} plus 59 fresh iid labels 10000–10058 per material "
             f"= {planned_probes} probes (amplitude = the material's `probe_linf`; Generator(PCG64(seed)), uniform on [−ε, +ε)).")
    L.append("")
    L.append("## Accounting")
    L.append("")
    L.append("| Item | Count | Denominator |")
    L.append("|---|---:|---:|")
    for metric in ("reconstruction_rows_scored", "reconstruction_rows_gate_fail", "reconstruction_rows_other_failure", "probes_scored", "probes_failed", "materials_reference_failed"):
        r = g("population", metric)
        L.append(f"| {metric} | {r['value']} | {r['denominator']} |")
    L.append("")
    L.append(f"Failures are listed row by row in `failures.csv` ({len(failures)} entries; {n_gate_fail} reproduction-gate, "
             f"{n_fail_rows - n_gate_fail} other reconstruction, {n_fail_probes} probe). No failure is dropped from a denominator or counted as a pass.")
    L.append("")
    L.append("## Reproduction of the frozen stack on this machine")
    L.append("")
    r1 = g("reproduction", "rows_bader_rederived_within_1e-6_e_of_stored")
    r2 = g("reproduction", "fresh_probes_bader_within_1e-6_e_of_frozen_P2")
    r3 = g("reproduction", "qsq_seed_probes_bader_within_1e-6_e_of_frozen")
    r4 = g("reproduction", "materials_n_max_equals_baderkit_maxima")
    L.append(f"- Realized L∞ / stored realized L∞ over all {planned_rows} rows: min {fmt(g('reproduction','realized_over_stored_min')['value'], 10)}, "
             f"max {fmt(g('reproduction','realized_over_stored_max')['value'], 10)}.")
    L.append(f"- Re-derived resolved Bader error within 1e-6 e of the stored value: {r1['value']}/{r1['denominator']} gate-passing rows "
             f"(largest absolute difference {fmt(g('reproduction','rows_bader_rederived_abs_diff_max_e')['value'])} e); "
             f"same side of the 1e-3 e threshold as the stored value: {g('reproduction','rows_bader_rederived_same_side_of_1e-3_e')['value']}/{r1['denominator']}.")
    L.append(f"- Fresh-probe Bader response within 1e-6 e of the frozen P2 value: {r2['value']}/{r2['denominator']} "
             f"(largest absolute difference {fmt(g('reproduction','fresh_probes_bader_abs_diff_max_e')['value'])} e).")
    L.append(f"- Five-seed Bader response within 1e-6 e of the frozen per-seed value: {r3['value']}/{r3['denominator']} "
             f"(largest absolute difference {fmt(g('reproduction','qsq_seed_probes_bader_abs_diff_max_e')['value'])} e).")
    L.append(f"- Reference n_max equal to BaderKit's own on-grid maxima count: {r4['value']}/{r4['denominator']} materials.")
    L.append("")
    L.append("## Reference QoI")
    L.append("")
    L.append(f"- n_max median {fmt(g('reference','n_max_median')['value'])} (range {g('reference','n_max_min')['value']}–{g('reference','n_max_max')['value']}); "
             f"n_min median {fmt(g('reference','n_min_median')['value'])}.")
    L.append(f"- Materials with n_max = natoms: {g('reference','materials_with_n_max_equal_natoms')['value']}/{n_materials}; "
             f"with at least one maximum in the vacuum basin: {g('reference','materials_with_maxima_in_vacuum_basin')['value']}/{n_materials}; "
             f"with at least one atom whose basin holds no maximum: {g('reference','materials_with_atom_lacking_maximum')['value']}/{n_materials}.")
    L.append("")
    L.append("## Analysis 1 — QSQ-cp floor and eligibility")
    L.append("")
    L.append(f"f^cp_m = max over the five seeds of |Δn_max|. Floor defined (all five seeds scored) for {g('A1','materials_floor_defined')['value']}/{n_materials} materials.")
    L.append(f"Median f^cp = {fmt(g('A1','f_cp_median')['value'])}; f^cp = 0 for {g('A1','f_cp_zero_count')['value']}/{n_materials}; "
             f"90th percentile {fmt(g('A1','f_cp_quantile_0.9')['value'])}; max {fmt(g('A1','f_cp_max')['value'])}.")
    L.append("")
    L.append("| τ_cp | Eligible materials | Bulk | Slab |")
    L.append("|---|---:|---:|---:|")
    for tau in TAU_CP:
        r = g("A1", f"cp_eligible_tau{tau}_materials", f"tau_cp={tau}")
        rb = g("A1", f"cp_eligible_tau{tau}_materials", f"tau_cp={tau};bulk")
        rs = g("A1", f"cp_eligible_tau{tau}_materials", f"tau_cp={tau};slab")
        L.append(f"| {tau} | {r['value']}/{r['denominator']} ({pct(r['value']/r['denominator'])}) | {rb['value']}/{rb['denominator']} | {rs['value']}/{rs['denominator']} |")
    rc = g("A1", "cp_eligible_tau0_count_only_materials")
    L.append("")
    L.append(f"τ_cp = 0 requires an identical maximum-voxel set on all five seeds (protocol). Count-only variant (|Δn_max| = 0 on all five seeds): {rc['value']}/{rc['denominator']}.")
    L.append("")
    L.append("## Analysis 2 — Prospective test (P2 form), τ_cp = 0")
    L.append("")
    L.append("| Endpoint | Group | Exceeding trials / trials | Rate [95% CI] | Materials |")
    L.append("|---|---|---:|---:|---:|")
    for label, d in (("abs(Δn_max) ≥ 1 (primary)", primary), ("maximum set changed (secondary)", secondary)):
        L.append(f"| {label} | cp-eligible | {d['num_e']}/{d['den_e']} | {pct(d['rate_e'])} [{pct(d['lo_e'])}, {pct(d['hi_e'])}] | {d['m_e']} |")
        L.append(f"| {label} | screen-rejected | {d['num_r']}/{d['den_r']} | {pct(d['rate_r'])} [{pct(d['lo_r'])}, {pct(d['hi_r'])}] | {d['m_r']} |")
    L.append("")
    L.append(f"**Risk ratio (rejected / eligible), primary endpoint: {fmt(primary['rr'])} [95% CI {fmt(primary['lo'])}, {fmt(primary['hi'])}]** "
             f"(bootstrap resamples with infinite ratio: {primary['n_inf']}, undefined: {primary['n_nan']}).")
    L.append(f"Risk ratio, secondary endpoint: {fmt(secondary['rr'])} [{fmt(secondary['lo'])}, {fmt(secondary['hi'])}].")
    L.append(f"Fresh trials failed: {len(fresh_fail)}/{population['fresh_probes_planned']}.")
    L.append("")
    L.append("### Acceptance")
    L.append("")
    L.append(f"Rule: QSQ generalizes to the cp QoI if the prospective risk ratio exceeds 5 with a 95% CI lower bound above 1.")
    L.append(f"**Verdict: {g('acceptance','verdict')['value']}** (RR = {fmt(primary['rr'])}, CI lower bound = {fmt(primary['lo'])}).")
    L.append("")
    L.append("## Analysis 3 — Cross-QoI transfer")
    L.append("")
    k = g("A3", "kappa_bader1e-3_vs_cp_tau0")
    L.append(f"- Cohen's κ between Bader eligibility at 1e-3 e and cp eligibility at τ_cp = 0: **{fmt(k['value'])}** [95% CI {fmt(k['ci95_low'])}, {fmt(k['ci95_high'])}], n = {n_materials}.")
    L.append(f"  Contingency: both eligible {g('A3','both_eligible')['value']}, Bader-only {g('A3','bader_only_eligible')['value']}, cp-only {g('A3','cp_only_eligible')['value']}, "
             f"neither {g('A3','neither_eligible')['value']}; raw agreement {pct(g('A3','agreement_fraction')['value'])}.")
    for tau in (1, 2):
        k2 = g("A3", f"kappa_bader1e-3_vs_cp_tau{tau}")
        L.append(f"- κ at τ_cp = {tau} (secondary): {fmt(k2['value'])} [{fmt(k2['ci95_low'])}, {fmt(k2['ci95_high'])}].")
    rr3 = g("A3", "spearman_log10_f_bader_vs_f_cp")
    L.append(f"- Spearman ρ between log10 f_m (Bader) and f^cp_m: **{fmt(rr3['value'])}** [95% CI {fmt(rr3['ci95_low'])}, {fmt(rr3['ci95_high'])}], n = {rr3['denominator']}.")
    rr3b = g("A3", "spearman_log10_f_bader_vs_max_jaccard_over_seeds")
    L.append(f"- Spearman ρ between log10 f_m and the five-seed maximum Jaccard distance (secondary): {fmt(rr3b['value'])} [{fmt(rr3b['ci95_low'])}, {fmt(rr3b['ci95_high'])}].")
    L.append("")
    L.append("## Analysis 4 — Codec scoring (gate-passing reconstructions)")
    L.append("")
    r = g("A4", "gate_passing_rows_delta0")
    rs = g("A4", "gate_passing_rows_set_identical")
    L.append(f"Gate-passing rows: {g('A4','gate_passing_rows')['value']}/{planned_rows}. Pooled fraction with |Δn_max| = 0: {r['value']}/{r['denominator']} ({pct(r['value']/r['denominator'])}); "
             f"with identical maximum set: {rs['value']}/{rs['denominator']} ({pct(rs['value']/rs['denominator'])}).")
    L.append("")
    L.append("Fraction of rows with |Δn_max| = 0 by codec and nominal relative tolerance, split by cp-eligibility at τ_cp = 0 (k/n):")
    L.append("")
    tols = sorted(ok_rows["nominal_tolerance_relative"].unique())
    L.append("| Codec | Split | " + " | ".join(f"{t:g}" for t in tols) + " |")
    L.append("|---|---|" + "---:|" * len(tols))
    a4 = pd.DataFrame(a4_table)
    for codec in CODEC_ORDER:
        for split in ("cp_eligible_tau0", "cp_rejected_tau0"):
            cells = []
            for t in tols:
                m = a4[(a4["codec"] == codec) & (a4["split"] == split) & (a4["tol"] == t)]
                cells.append("–" if m.empty or m.iloc[0]["n"] == 0 else f"{int(m.iloc[0]['k'])}/{int(m.iloc[0]['n'])}")
            L.append(f"| {codec} | {split} | " + " | ".join(cells) + " |")
    L.append("")
    L.append("Certified-at-τ_cp rates (denominator = gate-passing rows of cp-eligible materials at that τ_cp; τ_cp = 0 requires an identical maximum set):")
    L.append("")
    L.append("| τ_cp | Codec | Certified rows / eligible rows | Rate | Eligible materials with ≥1 certified rung |")
    L.append("|---|---|---:|---:|---:|")
    for row in cert_table:
        key = ("A4", f"certified_at_tau{row['tau']}_materials_any_rung", f"{row['codec']};eligible_materials")
        mat = S.get(key)
        mat_txt = f"{mat['value']}/{mat['denominator']}" if mat else "–"
        L.append(f"| {row['tau']} | {row['codec']} | {row['k']}/{row['n']} | {pct(row['rate'])} | {mat_txt} |")
    for tau in TAU_CP:
        ri = g("A4", f"delta_le_tau{tau}_rate_ignoring_eligibility", "all codecs")
        L.append(f"- Ignoring eligibility, rows meeting τ_cp = {tau}: {ri['numerator']}/{ri['denominator']} ({pct(ri['value'])}).")
    L.append("")
    L.append("## Analysis 5 — Operator contrast (same gate-passing rows)")
    L.append("")
    r5 = g("A5", "spearman_delta_n_max_vs_bader_error")
    L.append(f"- Spearman ρ between |Δn_max| and re-derived resolved Bader error: **{fmt(r5['value'])}** [95% CI {fmt(r5['ci95_low'])}, {fmt(r5['ci95_high'])}], n = {r5['denominator']} rows.")
    r5j = g("A5", "spearman_jaccard_vs_bader_error")
    L.append(f"- Spearman ρ between Jaccard distance and Bader error (secondary): {fmt(r5j['value'])} [{fmt(r5j['ci95_low'])}, {fmt(r5j['ci95_high'])}].")
    fa = g("A5", "fraction_delta0_and_bader_ge_1e-3")
    fb = g("A5", "fraction_delta_ge1_and_bader_lt_1e-3")
    L.append(f"- Rows with |Δn_max| = 0 but Bader error ≥ 1e-3 e: **{fa['numerator']}/{fa['denominator']} ({pct(fa['value'])})** [95% CI {pct(fa['ci95_low'])}, {pct(fa['ci95_high'])}].")
    L.append(f"- Rows with |Δn_max| ≥ 1 but Bader error < 1e-3 e: **{fb['numerator']}/{fb['denominator']} ({pct(fb['value'])})** [95% CI {pct(fb['ci95_low'])}, {pct(fb['ci95_high'])}].")
    fc = g("A5", "fraction_delta_ge1_and_bader_ge_1e-3")
    fd = g("A5", "fraction_delta0_and_bader_lt_1e-3")
    L.append(f"- Both fail: {fc['numerator']}/{fc['denominator']} ({pct(fc['value'])}); both pass: {fd['numerator']}/{fd['denominator']} ({pct(fd['value'])}).")
    pa = g("A5", "P(bader_ge_1e-3 | delta0)")
    pb = g("A5", "P(bader_lt_1e-3 | delta_ge1)")
    L.append(f"- Conditional: P(Bader ≥ 1e-3 e | |Δn_max| = 0) = {pa['numerator']}/{pa['denominator']} ({pct(pa['value'])}); "
             f"P(Bader < 1e-3 e | |Δn_max| ≥ 1) = {pb['numerator']}/{pb['denominator']} ({pct(pb['value'])}).")
    sa = g("A5", "fraction_set_identical_and_bader_ge_1e-3")
    sb = g("A5", "fraction_set_changed_and_bader_lt_1e-3")
    L.append(f"- Set-identity variant: identical set but Bader ≥ 1e-3 e {sa['numerator']}/{sa['denominator']} ({pct(sa['value'])}); "
             f"set changed but Bader < 1e-3 e {sb['numerator']}/{sb['denominator']} ({pct(sb['value'])}).")
    qa = g("A5", "probes_fraction_delta0_and_bader_ge_1e-3")
    qb = g("A5", "probes_fraction_delta_ge1_and_bader_lt_1e-3")
    qs = g("A5", "probes_spearman_delta_n_max_vs_bader_response")
    L.append(f"- Same contrast on the perturbation probes: |Δn_max| = 0 but Bader ≥ 1e-3 e {qa['numerator']}/{qa['denominator']} ({pct(qa['value'])}); "
             f"|Δn_max| ≥ 1 but Bader < 1e-3 e {qb['numerator']}/{qb['denominator']} ({pct(qb['value'])}); Spearman ρ {fmt(qs['value'])}.")
    L.append("")
    L.append("## Wall time")
    L.append("")
    L.append(f"- Sum of per-material worker wall time: {wall_material:.0f} s ({wall_material/3600:.2f} h).")
    L.append(f"- Sum of runner invocation wall time ({len(invocation_walls)} invocation(s), 4 worker processes): {sum(invocation_walls):.0f} s ({sum(invocation_walls)/3600:.2f} h).")
    L.append("")
    L.append("## Files")
    L.append("")
    L.append("`cp_reference.csv` (per material), `cp_rows.csv` (per reconstruction, gate failures listed with status GATE_FAIL), "
             "`cp_probes.csv` (per perturbation), `cp_material_floors.csv` (per-material floors and eligibility), `summary.csv`, "
             "`failures.csv`, `population.json`, `provenance.json`, `run_log.txt`, `DEVIATIONS.md`.")
    (HERE / "RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    # provenance
    inputs_read = [
        REPO_ROOT / "materials_metadata.csv",
        REPO_ROOT / "benchmark" / "master_benchmark_full.csv",
        REPO_ROOT / "stability" / "stability_floor_A1.csv",
        REPO_ROOT / "stability" / "stability_floor_A1_per_seed.csv",
        REPO_ROOT / "validation" / "qsq_prospective" / "fresh_seed_jobs.csv",
        REPO_ROOT / "validation" / "qsq_prospective" / "p2_fresh_probes" / "outcomes.csv",
        REPO_ROOT / "validation" / "qsq_prospective" / "development_compatibility_smoke.py",
        REPO_ROOT / "analysis" / "extensions_20260928" / "PROTOCOL.md",
        FROZEN_REPO / "validation" / "external_end_to_end.py",
        FROZEN_REPO / "validation" / "requirements-external-e2e.txt",
    ]
    outputs = ["cp_reference.csv", "cp_rows.csv", "cp_probes.csv", "cp_material_floors.csv", "summary.csv", "failures.csv",
               "population.json", "aggregate_counts.json", "material_run_status.csv", "run_wpb.py", "analyze_wpb.py"]
    pip_freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True).stdout.splitlines()
    pins = {}
    for name in ("numpy", "baderkit", "pysz", "zfpy", "hdf5plugin", "h5py", "pymatgen", "scipy", "pandas", "numba", "llvmlite"):
        try:
            pins[name] = md.version(name)
        except md.PackageNotFoundError:
            pins[name] = "NOT_INSTALLED"
    source_shas = {mid: meta.loc[mid, "sha256"] for mid in materials}
    prov = {
        "package": "WP-B",
        "protocol": "analysis/extensions_20260928/PROTOCOL.md (WP-B)",
        "branch": "ext/WP-B-20260928",
        "repo_head_commit_at_analysis": git_head(REPO_ROOT),
        "protocol_commit": "b74ede8",
        "frozen_scientific_commit": "893f931b3045b0b628329db81999c2f439d4e830",
        "frozen_scientific_checkout": str(FROZEN_REPO),
        "frozen_checkout_head": git_head(FROZEN_REPO),
        "python": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "scientific_pins": pins,
        "pip_freeze": pip_freeze,
        "bader_settings": {"method": "ongrid", "vacuum_tol": 1e-3, "persistence_tol": 0.5, "nna_cutoff": False},
        "critical_point_definition": "strict 26-neighbour periodic local maxima/minima on the raw grid; ties are not extrema; no smoothing",
        "reproduction_gate": [0.95, 1.05],
        "bootstrap": {"resamples": BOOT_N, "seed": BOOT_SEED, "cluster": "material", "interval": "percentile 95%"},
        "population": population,
        "aggregate_counts": agg_counts,
        "input_files_sha256": {str(p.relative_to(p.parents[len(p.parts) - len(REPO_ROOT.parts) - 1]) if str(p).startswith(str(REPO_ROOT)) else str(p)): sha256_file(p) for p in inputs_read},
        "source_density_sha256_by_material": source_shas,
        "density_cache_dir": r"D:\Research\QoI-ext-cache\densities",
        "checkpoint_dir": r"D:\Research\QoI-ext-cache\WP-B\checkpoints",
        "output_files_sha256": {name: sha256_file(HERE / name) for name in outputs if (HERE / name).exists()},
        "wall_time_seconds": {"sum_material_worker": wall_material, "sum_invocations": float(sum(invocation_walls)), "analysis": time.time() - t_start},
        "workers": 4,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    (HERE / "provenance.json").write_text(json.dumps(prov, indent=2), encoding="utf-8")
    print(f"verdict: {g('acceptance','verdict')['value']}; RR={fmt(primary['rr'])} [{fmt(primary['lo'])}, {fmt(primary['hi'])}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
