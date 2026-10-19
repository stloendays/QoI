#!/usr/bin/env python3
"""Aggregate the frozen Hartree-contract archive-law checkpoints."""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
WP_F_DIR = REPO / "analysis" / "extensions_20260930" / "WP-F"
if str(WP_F_DIR) not in sys.path:
    sys.path.insert(0, str(WP_F_DIR))

# Reuse the frozen WP-F stratified expansion estimator by import.
import analyze_wpf as wpf_analysis  # type: ignore  # noqa: E402

from run_archive_law import (  # noqa: E402
    TAUS,
    load_tasks,
    stored_bytes,
    tau_key,
)


FRAME_TB = 8.4976
BOOT_SEED = 20261012
BOOT_REPS = 2000
REPORT_ORDER = (1e-6, 1e-4, 1e-8)


def stratified_total(df: pd.DataFrame, strata: pd.DataFrame, column: str) -> float:
    """Call the WP-F expansion estimator with the archive-law data frame."""
    if len(df) == 0:
        return float("nan")
    return float(wpf_analysis.expand(df, strata, column))


def ratio(numerator: float, denominator: float) -> float:
    if not (np.isfinite(numerator) and np.isfinite(denominator)) or denominator == 0.0:
        return float("nan")
    return float(numerator / denominator)


def _success_subset(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["status"] == "SUCCESS"]


def point_metrics(df: pd.DataFrame, strata: pd.DataFrame, tau: float) -> dict[str, float]:
    """Compute all ratios from one (possibly bootstrap-resampled) data frame."""
    key = tau_key(tau)
    json_total = stratified_total(df, strata, "json_bytes")
    l_total = stratified_total(df, strata, f"stored_L_{key}")
    p_total = stratified_total(df, strata, f"stored_P_{key}")
    successful = _success_subset(df)
    raw_total = stratified_total(successful, strata, "raw64_bytes")
    lossless_total = stratified_total(successful, strata, "lossless_bytes")
    l_success_total = stratified_total(successful, strata, f"stored_L_{key}")
    p_success_total = stratified_total(successful, strata, f"stored_P_{key}")

    flags = df[f"eligible_{key}"].fillna(False).astype(float)
    success_flag = (df["status"] == "SUCCESS").astype(float)
    eligible_success = flags * success_flag
    eligible_count_frame = stratified_total(df.assign(_x=flags), strata, "_x")
    eligible_bytes_frame = stratified_total(
        df.assign(_x=flags * df["json_bytes"]), strata, "_x"
    )
    success_count_frame = stratified_total(df.assign(_x=success_flag), strata, "_x")
    success_bytes_frame = stratified_total(
        df.assign(_x=success_flag * df["json_bytes"]), strata, "_x"
    )
    eligible_count_success = stratified_total(
        df.assign(_x=eligible_success), strata, "_x"
    )
    eligible_bytes_success = stratified_total(
        df.assign(_x=eligible_success * df["json_bytes"]), strata, "_x"
    )
    population_count = float(strata["N_frame"].sum())

    failures = (df["status"] != "SUCCESS").astype(float)
    failure_count = stratified_total(df.assign(_x=failures), strata, "_x")
    failure_bytes = stratified_total(
        df.assign(_x=failures * df["json_bytes"]), strata, "_x"
    )

    both = (
        df[f"writer_L_certified_{key}"].fillna(False).astype(bool)
        & df[f"writer_P_certified_{key}"].fillna(False).astype(bool)
    )
    if bool(both.any()):
        stream_ratio = (
            df.loc[both, f"writer_L_stream_bytes_{key}"
                   ].astype(float)
            / df.loc[both, f"writer_P_stream_bytes_{key}"].astype(float)
        )
        median_stream_ratio = float(np.median(stream_ratio.to_numpy()))
        n_both = float(len(stream_ratio))
    else:
        median_stream_ratio = float("nan")
        n_both = 0.0

    return {
        "json_total": json_total,
        "stored_L_total": l_total,
        "stored_P_total": p_total,
        "raw64_success_total": raw_total,
        "lossless_success_total": lossless_total,
        "R_L_vs_json": ratio(json_total, l_total),
        "R_P_vs_json": ratio(json_total, p_total),
        "R_L_over_R_P": ratio(ratio(json_total, l_total), ratio(json_total, p_total)),
        "R_L_vs_float64": ratio(raw_total, l_success_total),
        "R_P_vs_float64": ratio(raw_total, p_success_total),
        "R_L_vs_lossless": ratio(lossless_total, l_success_total),
        "R_P_vs_lossless": ratio(lossless_total, p_success_total),
        "eligible_fraction_count": ratio(eligible_count_frame, population_count),
        "eligible_fraction_bytes": ratio(eligible_bytes_frame, json_total),
        "eligible_fraction_count_evaluable": ratio(eligible_count_success, success_count_frame),
        "eligible_fraction_bytes_evaluable": ratio(eligible_bytes_success, success_bytes_frame),
        "failure_fraction_count": ratio(failure_count, population_count),
        "failure_fraction_bytes": ratio(failure_bytes, json_total),
        "median_certified_stream_ratio_L_over_P": median_stream_ratio,
        "n_both_certified": n_both,
    }


def _resample_within_strata(
    df: pd.DataFrame, strata: pd.DataFrame, rng: np.random.Generator
) -> pd.DataFrame:
    parts = []
    for stratum in strata.index:
        group = df[df["stratum"] == stratum]
        if len(group) == 0:
            raise ValueError(f"no sample rows for stratum {stratum}")
        indices = rng.integers(0, len(group), size=len(group))
        parts.append(group.iloc[indices])
    return pd.concat(parts, ignore_index=True)


def _fast_bootstrap_metrics(
    frame: pd.DataFrame,
    strata: pd.DataFrame,
    tau: float,
    samples: list[tuple[float, np.ndarray]],
) -> dict[str, float]:
    """Evaluate one paired resample using precomputed NumPy row selections."""
    key = tau_key(tau)
    status = frame["status"].to_numpy(dtype=object)
    success = status == "SUCCESS"
    eligible = frame[f"eligible_{key}"].fillna(False).to_numpy(dtype=bool)
    json_values = frame["json_bytes"].to_numpy(dtype=float)
    stored_l = frame[f"stored_L_{key}"].to_numpy(dtype=float)
    stored_p = frame[f"stored_P_{key}"].to_numpy(dtype=float)
    raw = pd.to_numeric(frame["raw64_bytes"], errors="coerce").to_numpy(dtype=float)
    lossless = pd.to_numeric(frame["lossless_bytes"], errors="coerce").to_numpy(dtype=float)
    population_count = float(strata["N_frame"].sum())

    def total(values: np.ndarray, mask: np.ndarray | None = None) -> float:
        result = 0.0
        for weight, selected in samples:
            chosen = selected
            if mask is not None:
                chosen = selected[mask[selected]]
            result += weight * float(np.nansum(values[chosen]))
        return result

    json_total = total(json_values)
    l_total = total(stored_l)
    p_total = total(stored_p)
    raw_total = total(raw, success)
    lossless_total = total(lossless, success)
    l_success_total = total(stored_l, success)
    p_success_total = total(stored_p, success)
    eligible_float = eligible.astype(float)
    success_float = success.astype(float)
    eligible_success = eligible & success
    eligible_count_frame = total(eligible_float)
    eligible_bytes_frame = total(eligible_float * json_values)
    success_count_frame = total(success_float)
    success_bytes_frame = total(success_float * json_values)
    eligible_count_success = total(eligible_success.astype(float))
    eligible_bytes_success = total(eligible_success.astype(float) * json_values)
    failure_float = (~success).astype(float)
    failure_count = total(failure_float)
    failure_bytes = total(failure_float * json_values)
    return {
        "R_L_vs_json": ratio(json_total, l_total),
        "R_P_vs_json": ratio(json_total, p_total),
        "R_L_over_R_P": ratio(ratio(json_total, l_total), ratio(json_total, p_total)),
        "R_L_vs_float64": ratio(raw_total, l_success_total),
        "R_P_vs_float64": ratio(raw_total, p_success_total),
        "R_L_vs_lossless": ratio(lossless_total, l_success_total),
        "R_P_vs_lossless": ratio(lossless_total, p_success_total),
        "eligible_fraction_count": ratio(eligible_count_frame, population_count),
        "eligible_fraction_bytes": ratio(eligible_bytes_frame, json_total),
        "eligible_fraction_count_evaluable": ratio(eligible_count_success, success_count_frame),
        "eligible_fraction_bytes_evaluable": ratio(eligible_bytes_success, success_bytes_frame),
        "failure_fraction_count": ratio(failure_count, population_count),
        "failure_fraction_bytes": ratio(failure_bytes, json_total),
    }


def paired_bootstrap(
    df: pd.DataFrame,
    strata: pd.DataFrame,
    tau: float,
    *,
    n_boot: int = BOOT_REPS,
    seed: int = BOOT_SEED,
    return_samples: bool = False,
) -> dict[str, Any]:
    """Stratified paired bootstrap; all ratios use each common resample."""
    if n_boot < 1:
        raise ValueError("n_boot must be positive")
    rng = np.random.default_rng(seed)
    frame = df.reset_index(drop=True)
    groups = {
        stratum: np.flatnonzero(frame["stratum"].to_numpy(dtype=object) == stratum)
        for stratum in strata.index
    }
    weights = {
        stratum: float(strata.loc[stratum, "N_frame"] / strata.loc[stratum, "n_sample"])
        for stratum in strata.index
    }
    names = (
        "R_L_vs_json",
        "R_P_vs_json",
        "R_L_over_R_P",
        "R_L_vs_float64",
        "R_P_vs_float64",
        "R_L_vs_lossless",
        "R_P_vs_lossless",
        "eligible_fraction_count",
        "eligible_fraction_bytes",
        "eligible_fraction_count_evaluable",
        "eligible_fraction_bytes_evaluable",
        "failure_fraction_count",
        "failure_fraction_bytes",
    )
    values = {name: np.empty(n_boot, dtype=float) for name in names}
    for index in range(n_boot):
        selections = [
            (
                weights[stratum],
                groups[stratum][rng.integers(0, len(groups[stratum]), size=len(groups[stratum]))],
            )
            for stratum in strata.index
        ]
        metrics = _fast_bootstrap_metrics(frame, strata, tau, selections)
        for name in names:
            values[name][index] = metrics[name]
    if return_samples:
        return values
    return {name: percentile_interval(array) for name, array in values.items()}


def percentile_interval(values: np.ndarray) -> tuple[float, float]:
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    if len(finite) == 0:
        return float("nan"), float("nan")
    return float(np.quantile(finite, 0.025)), float(np.quantile(finite, 0.975))


def _checkpoint_failure(task: dict[str, str], category: str, error: str) -> dict[str, Any]:
    return {
        "task_id": task["task_id"],
        "stratum": task["stratum"],
        "stage": "checkpoint",
        "category": category,
        "error": error,
    }


def _writer_fields(
    obj: dict[str, Any], writer: str, key: str, row: dict[str, Any] | None
) -> None:
    if row is None:
        obj[f"writer_{writer}_certified_{key}"] = np.nan
        obj[f"writer_{writer}_stream_bytes_{key}"] = np.nan
        obj[f"writer_{writer}_cr_{key}"] = np.nan
        obj[f"writer_{writer}_codec_{key}"] = ""
        return
    obj[f"writer_{writer}_certified_{key}"] = bool(row.get("certified", False))
    obj[f"writer_{writer}_stream_bytes_{key}"] = int(row["stream_bytes"])
    obj[f"writer_{writer}_cr_{key}"] = float(row.get("cr", np.nan))
    obj[f"writer_{writer}_codec_{key}"] = row.get("codec", "")


def merge_checkpoints(
    sample_csv: Path, checkpoint_dir: Path
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Merge all 300 tasks; absent or incomplete checkpoints become failures."""
    tasks = load_tasks(sample_csv)
    sample = pd.DataFrame(tasks)
    sample["bytes"] = sample["bytes"].astype(int)
    strata_path = sample_csv.parent / "strata.csv"
    strata = pd.read_csv(strata_path).set_index("stratum")
    counts = sample["stratum"].value_counts().to_dict()
    for stratum, row in strata.iterrows():
        if int(counts.get(stratum, 0)) != int(row["n_sample"]):
            raise ValueError(f"sample count mismatch in {stratum}")

    objects: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for task in tasks:
        task_id = task["task_id"]
        checkpoint_path = checkpoint_dir / f"{task_id}.json"
        checkpoint: dict[str, Any] | None = None
        if checkpoint_path.exists():
            try:
                loaded = json.loads(checkpoint_path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    checkpoint = loaded
                else:
                    failures.append(_checkpoint_failure(task, "invalid_checkpoint", "checkpoint is not an object"))
            except Exception as exc:  # malformed checkpoints remain failures.
                failures.append(_checkpoint_failure(task, "invalid_checkpoint", f"{type(exc).__name__}: {exc}"))
        else:
            failures.append(_checkpoint_failure(task, "missing_checkpoint", "no checkpoint was written"))

        complete = bool(checkpoint and checkpoint.get("complete") is True)
        status = "SUCCESS" if complete and checkpoint.get("status") == "SUCCESS" else "FAILED"
        if checkpoint is not None and not complete:
            failures.append(_checkpoint_failure(task, "incomplete_checkpoint", "checkpoint is not complete"))
        if checkpoint is not None:
            rows = checkpoint.get("failures") or []
            for failure in rows:
                item = dict(failure)
                item.setdefault("task_id", task_id)
                item.setdefault("stratum", task["stratum"])
                item.setdefault("category", "other")
                item.setdefault("stage", "unknown")
                item.setdefault("error", "")
                failures.append(item)
        if status == "FAILED" and checkpoint is not None and not (checkpoint.get("failures") or []):
            failures.append(_checkpoint_failure(task, "other", "checkpoint status is FAILED"))

        obj: dict[str, Any] = {
            "task_id": task_id,
            "stratum": task["stratum"],
            "rank_in_stratum": int(task["rank_in_stratum"]),
            "key": task["key"],
            "url": task["url"],
            "frame_bytes": int(task["bytes"]),
            "status": status,
            "checkpoint_complete": complete,
            "json_bytes": int((checkpoint or {}).get("json_bytes", task["bytes"])),
            "raw64_bytes": (checkpoint or {}).get("raw64_bytes", np.nan),
            "lossless_bytes": (checkpoint or {}).get("lossless_bytes", np.nan),
            "epsilon": (checkpoint or {}).get("epsilon", np.nan),
            "floor_hartree": (checkpoint or {}).get("floor_hartree", np.nan),
            "wall_seconds": (checkpoint or {}).get("wall_seconds", np.nan),
            "peak_rss_bytes": (checkpoint or {}).get("peak_rss_bytes", np.nan),
        }
        if status != "SUCCESS":
            obj["json_bytes"] = int(task["bytes"])

        checkpoint_eligible = (checkpoint or {}).get("eligible") or {}
        checkpoint_writers = (checkpoint or {}).get("writers") or {}
        checkpoint_storage = (checkpoint or {}).get("storage") or {}
        for tau in TAUS:
            key = tau_key(tau)
            eligible: bool | None
            if status == "SUCCESS" and key in checkpoint_eligible:
                eligible = bool(checkpoint_eligible[key])
            else:
                eligible = None
            obj[f"eligible_{key}"] = eligible if eligible is not None else np.nan
            writers = checkpoint_writers.get(key) or {}
            _writer_fields(obj, "L", key, writers.get("L"))
            _writer_fields(obj, "P", key, writers.get("P"))

            if key in checkpoint_storage:
                storage = checkpoint_storage[key]
                stored_l = int(storage["L"])
                stored_p = int(storage["P"])
            elif status == "SUCCESS" and np.isfinite(obj["lossless_bytes"]):
                stored_l = stored_bytes(
                    status=status,
                    eligible=eligible,
                    certified_bytes=(int(obj[f"writer_L_stream_bytes_{key}"])
                                     if bool(obj[f"writer_L_certified_{key}"]) else None),
                    lossless_bytes=int(obj["lossless_bytes"]),
                    frame_bytes=int(task["bytes"]),
                )[0]
                stored_p = stored_bytes(
                    status=status,
                    eligible=eligible,
                    certified_bytes=(int(obj[f"writer_P_stream_bytes_{key}"])
                                     if bool(obj[f"writer_P_certified_{key}"]) else None),
                    lossless_bytes=int(obj["lossless_bytes"]),
                    frame_bytes=int(task["bytes"]),
                )[0]
            else:
                stored_l = stored_p = int(task["bytes"])
            obj[f"stored_L_{key}"] = stored_l
            obj[f"stored_P_{key}"] = stored_p
        objects.append(obj)

    return pd.DataFrame(objects), strata, pd.DataFrame(failures)


def _estimate_row(
    tau: float, quantity: str, estimate: float, ci: tuple[float, float], *, note: str = ""
) -> dict[str, Any]:
    return {
        "tau_H": float(tau),
        "quantity": quantity,
        "estimate": float(estimate) if np.isfinite(estimate) else np.nan,
        "ci_low": float(ci[0]) if np.isfinite(ci[0]) else np.nan,
        "ci_high": float(ci[1]) if np.isfinite(ci[1]) else np.nan,
        "bootstrap_reps": BOOT_REPS,
        "bootstrap_seed": BOOT_SEED,
        "note": note,
    }


def build_estimates(df: pd.DataFrame, strata: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for tau in TAUS:
        metrics = point_metrics(df, strata, tau)
        boot = paired_bootstrap(df, strata, tau)
        def add(quantity: str, metric: str, note: str = "") -> None:
            rows.append(_estimate_row(tau, quantity, metrics[metric], boot[metric], note=note))

        add("R_L_vs_json", "R_L_vs_json")
        add("R_P_vs_json", "R_P_vs_json")
        add("R_L_over_R_P", "R_L_over_R_P", "paired ratio from the same bootstrap resample")
        saving = FRAME_TB * (1.0 - 1.0 / metrics["R_L_vs_json"])
        saving_ci = (
            FRAME_TB * (1.0 - 1.0 / boot["R_L_vs_json"][0]),  # saving increases with R
            FRAME_TB * (1.0 - 1.0 / boot["R_L_vs_json"][1]),
        ) if np.all(np.isfinite(boot["R_L_vs_json"])) else (np.nan, np.nan)
        rows.append(_estimate_row(tau, "saving_TB_L", saving, saving_ci, note="8.4976 TB frame"))
        for quantity, metric in (
            ("R_L_vs_float64", "R_L_vs_float64"),
            ("R_P_vs_float64", "R_P_vs_float64"),
            ("R_L_vs_lossless", "R_L_vs_lossless"),
            ("R_P_vs_lossless", "R_P_vs_lossless"),
            ("eligible_fraction_count", "eligible_fraction_count"),
            ("eligible_fraction_bytes", "eligible_fraction_bytes"),
            ("eligible_fraction_count_evaluable", "eligible_fraction_count_evaluable"),
            ("eligible_fraction_bytes_evaluable", "eligible_fraction_bytes_evaluable"),
            ("failure_fraction_count", "failure_fraction_count"),
            ("failure_fraction_bytes", "failure_fraction_bytes"),
        ):
            add(quantity, metric)
        rows.append(
            _estimate_row(
                tau,
                "median_certified_stream_ratio_L_over_P",
                metrics["median_certified_stream_ratio_L_over_P"],
                (np.nan, np.nan),
                note="unweighted per-object median where both writers certified",
            )
        )
        rows.append(
            _estimate_row(
                tau,
                "n_both_certified",
                metrics["n_both_certified"],
                (np.nan, np.nan),
            )
        )
    return pd.DataFrame(rows)


def build_strata_results(df: pd.DataFrame, strata: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for stratum in strata.index:
        group = df[df["stratum"] == stratum]
        row: dict[str, Any] = {
            "stratum": stratum,
            "N_frame": int(strata.loc[stratum, "N_frame"]),
            "n_sample": int(strata.loc[stratum, "n_sample"]),
            "n_success": int((group["status"] == "SUCCESS").sum()),
            "n_failed": int((group["status"] != "SUCCESS").sum()),
            "json_bytes_sample": int(group["json_bytes"].sum()),
            "wall_seconds_median": float(group["wall_seconds"].median()),
            "wall_seconds_total": float(group["wall_seconds"].sum()),
            "peak_rss_GB_max": float(group["peak_rss_bytes"].max() / 1e9),
        }
        for tau in TAUS:
            key = tau_key(tau)
            row[f"eligible_count_{key}"] = int(
                group[f"eligible_{key}"].fillna(False).astype(bool).sum()
            )
            row[f"eligible_bytes_fraction_{key}"] = ratio(
                float(group.loc[group[f"eligible_{key}"].fillna(False).astype(bool), "json_bytes"].sum()),
                float(group["json_bytes"].sum()),
            )
            row[f"R_L_vs_json_{key}"] = ratio(
                float(group["json_bytes"].sum()), float(group[f"stored_L_{key}"].sum())
            )
            row[f"R_P_vs_json_{key}"] = ratio(
                float(group["json_bytes"].sum()), float(group[f"stored_P_{key}"].sum())
            )
        rows.append(row)
    return pd.DataFrame(rows)


def _display(value: Any, digits: int = 4) -> str:
    if value is None or (isinstance(value, float) and not math.isfinite(value)):
        return "NA"
    if isinstance(value, (np.floating, float)):
        if value != 0.0 and abs(float(value)) < 1e-3:
            return f"{float(value):.3g}"
        return f"{float(value):.{digits}f}"
    return str(value)


def markdown_table(df: pd.DataFrame, columns: list[str]) -> list[str]:
    header = "| " + " | ".join(columns) + " |"
    rule = "| " + " | ".join("---" for _ in columns) + " |"
    lines = [header, rule]
    for _, row in df[columns].iterrows():
        lines.append("| " + " | ".join(_display(row[col]) for col in columns) + " |")
    return lines


def _estimate_lookup(estimates: pd.DataFrame, tau: float, quantity: str) -> pd.Series:
    rows = estimates[(estimates["tau_H"] == tau) & (estimates["quantity"] == quantity)]
    if len(rows) != 1:
        raise ValueError(f"expected one estimate for {quantity} at {tau}, found {len(rows)}")
    return rows.iloc[0]


def build_results_draft(
    estimates: pd.DataFrame,
    strata_results: pd.DataFrame,
    failures: pd.DataFrame,
    objects: pd.DataFrame,
) -> str:
    lines = ["# Closed-form Hartree law on the Materials Project archive", ""]
    for tau in REPORT_ORDER:
        rl = _estimate_lookup(estimates, tau, "R_L_vs_json")
        rp = _estimate_lookup(estimates, tau, "R_P_vs_json")
        rr = _estimate_lookup(estimates, tau, "R_L_over_R_P")
        saving = _estimate_lookup(estimates, tau, "saving_TB_L")
        lines.append(
            f"τ_H = {tau:g}: R_L = {_display(rl['estimate'], 3)} "
            f"[{_display(rl['ci_low'], 3)}, {_display(rl['ci_high'], 3)}]; "
            f"R_P = {_display(rp['estimate'], 3)} "
            f"[{_display(rp['ci_low'], 3)}, {_display(rp['ci_high'], 3)}]; "
            f"R_L/R_P = {_display(rr['estimate'], 3)} "
            f"[{_display(rr['ci_low'], 3)}, {_display(rr['ci_high'], 3)}]; "
            f"law saving = {_display(saving['estimate'], 3)} TB."
        )
    lines.extend(
        [
            "",
            f"Frame: 415,289 objects and {FRAME_TB:.4f} TB of current MP JSON bytes; "
            f"the sample has {len(objects)} objects.",
            "",
            "## All tolerance estimates",
            "",
        ]
    )
    display_quantities = [
        "R_L_vs_json",
        "R_P_vs_json",
        "R_L_over_R_P",
        "saving_TB_L",
        "R_L_vs_float64",
        "R_L_vs_lossless",
        "eligible_fraction_count",
        "eligible_fraction_bytes",
        "median_certified_stream_ratio_L_over_P",
    ]
    wide = []
    for tau in REPORT_ORDER:
        row: dict[str, Any] = {"tau_H": tau}
        for quantity in display_quantities:
            row[quantity] = _estimate_lookup(estimates, tau, quantity)["estimate"]
        wide.append(row)
    lines.extend(
        markdown_table(
            pd.DataFrame(wide),
            ["tau_H"] + display_quantities,
        )
    )
    lines.extend(
        [
            "",
            "The float64 and lossless comparisons use successful/evaluable objects "
            "because §5 defines failed objects only by their current MP JSON storage; "
            "the fixed design weights and all sample rows are retained.",
            "",
            "## Eligibility and failures",
            "",
        ]
    )
    eligibility_rows = []
    for tau in REPORT_ORDER:
        eligibility_rows.append(
            {
                "tau_H": tau,
                "eligible_count_all": _estimate_lookup(estimates, tau, "eligible_fraction_count")["estimate"],
                "eligible_bytes_all": _estimate_lookup(estimates, tau, "eligible_fraction_bytes")["estimate"],
                "eligible_count_evaluable": _estimate_lookup(estimates, tau, "eligible_fraction_count_evaluable")["estimate"],
                "eligible_bytes_evaluable": _estimate_lookup(estimates, tau, "eligible_fraction_bytes_evaluable")["estimate"],
                "median_L_over_P": _estimate_lookup(estimates, tau, "median_certified_stream_ratio_L_over_P")["estimate"],
                "n_both": _estimate_lookup(estimates, tau, "n_both_certified")["estimate"],
            }
        )
    lines.extend(markdown_table(pd.DataFrame(eligibility_rows), list(eligibility_rows[0])))
    lines.extend(["", f"Failure records: {len(failures)}.", ""])
    if len(failures):
        category = (
            failures.groupby("category", dropna=False).size().reset_index(name="records")
            .sort_values("category")
        )
        lines.extend(markdown_table(category, ["category", "records"]))
    else:
        lines.append("No failure records.")
    lines.extend(["", "## Per-stratum results", ""])
    columns = [
        "stratum",
        "N_frame",
        "n_sample",
        "n_success",
        "n_failed",
        "R_L_vs_json_1e-06",
        "R_P_vs_json_1e-06",
        "eligible_count_1e-06",
    ]
    lines.extend(markdown_table(strata_results, columns))
    lines.extend(["", "## Wall time and memory per stratum", ""])
    lines.extend(
        markdown_table(
            strata_results,
            ["stratum", "wall_seconds_median", "wall_seconds_total", "peak_rss_GB_max"],
        )
    )
    lines.extend(
        [
            "",
            "Bootstrap: 2,000 within-stratum resamples, "
            "`numpy.random.default_rng(20261012)`, percentile 95%; R_L, R_P and "
            "R_L/R_P use the same resample.",
            "",
            "No object is dropped or reweighted after its outcome is known, and no "
            "pass/fail gate is applied by this aggregation script.",
        ]
    )
    return "\n".join(lines) + "\n"


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value) if np.isfinite(value) else None
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def write_outputs(
    *,
    objects: pd.DataFrame,
    strata: pd.DataFrame,
    failures: pd.DataFrame,
    out_dir: Path,
) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    estimates = build_estimates(objects, strata)
    strata_results = build_strata_results(objects, strata)
    objects.to_csv(out_dir / "objects.csv", index=False)
    estimates.to_csv(out_dir / "estimates.csv", index=False)
    strata_results.to_csv(out_dir / "strata_results.csv", index=False)
    if len(failures):
        failure_columns = ["task_id", "stratum", "stage", "category", "error"]
        for col in failure_columns:
            if col not in failures:
                failures[col] = ""
        failures[failure_columns].to_csv(out_dir / "failures.csv", index=False)
    else:
        pd.DataFrame(columns=["task_id", "stratum", "stage", "category", "error"]).to_csv(
            out_dir / "failures.csv", index=False
        )
    draft = build_results_draft(estimates, strata_results, failures, objects)
    (out_dir / "RESULTS_DRAFT.md").write_text(draft, encoding="utf-8")

    primary = {
        "R_L": _estimate_lookup(estimates, 1e-6, "R_L_vs_json").to_dict(),
        "R_P": _estimate_lookup(estimates, 1e-6, "R_P_vs_json").to_dict(),
        "R_L_over_R_P": _estimate_lookup(estimates, 1e-6, "R_L_over_R_P").to_dict(),
        "saving_TB": _estimate_lookup(estimates, 1e-6, "saving_TB_L").to_dict(),
    }
    summary = {
        "protocol": "analysis/archive_hartree_law_20261012/PROTOCOL.md",
        "frame_tb": FRAME_TB,
        "sample_objects": int(len(objects)),
        "status_counts": objects["status"].value_counts().to_dict(),
        "failure_records": int(len(failures)),
        "bootstrap": {"reps": BOOT_REPS, "seed": BOOT_SEED, "interval": "percentile_95"},
        "primary_tau_H": 1e-6,
        "primary": primary,
        "outputs": [
            "objects.csv",
            "estimates.csv",
            "strata_results.csv",
            "failures.csv",
            "SUMMARY.json",
            "RESULTS_DRAFT.md",
        ],
    }
    (out_dir / "SUMMARY.json").write_text(
        json.dumps(_json_safe(summary), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoints", type=Path, required=True)
    parser.add_argument("--sample-csv", type=Path, default=WP_F_DIR / "sample.csv")
    parser.add_argument("--out", type=Path, default=HERE / "results")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    objects, strata, failures = merge_checkpoints(args.sample_csv.resolve(), args.checkpoints.resolve())
    write_outputs(objects=objects, strata=strata, failures=failures, out_dir=args.out.resolve())
    print((args.out.resolve() / "RESULTS_DRAFT.md").read_text(encoding="utf-8").splitlines()[2])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
