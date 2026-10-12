#!/usr/bin/env python3
"""Aggregate FFCz checkpoints against the recorded law and BP comparison arms."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
REPO_DEFAULT = HERE.parents[1]
sys.path.insert(0, str(REPO_DEFAULT / "analysis" / "general_qoac_law"))
sys.path.insert(0, str(HERE))
import aggregate_law  # noqa: E402
import run_ffcz as R  # noqa: E402


# aggregate_law.boot is reused unchanged; its module-level seed is set to the
# FFCz protocol seed before every statistic is evaluated.
aggregate_law.SEED = 20261012
boot = aggregate_law.boot

TAUS = (1e-6, 1e-4, 1e-8)
ALL_TAUS = (1e-4, 1e-6, 1e-8)
COHORTS = R.COHORTS
LAW = R.LAW
BP = R.BP
REFERENCE_HASHES = {key: R.INPUT_SHA256[key] for key in R.INPUT_SHA256 if key.startswith(LAW) or key.startswith(BP)}


def many(root: Path, pattern: str) -> pd.DataFrame:
    frames = [pd.read_csv(path) for path in sorted(Path(root).rglob(pattern)) if path.stat().st_size > 2]
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def truthy(values: pd.Series) -> pd.Series:
    return values.astype(str).str.lower() == "true"


def check_reference_inputs(repo: Path) -> dict[str, str]:
    bad: list[str] = []
    actual: dict[str, str] = {}
    for relative, expected in REFERENCE_HASHES.items():
        path = Path(repo) / relative
        if not path.is_file():
            bad.append(f"{relative}: missing")
            continue
        digest = R.lf_sha256(path)
        actual[relative] = digest
        if digest != expected:
            bad.append(f"{relative}: {digest} != {expected}")
    if bad:
        raise RuntimeError("reference input SHA-256 mismatch: " + " | ".join(bad))
    return actual


def _index(ids: list[str]) -> pd.MultiIndex:
    return pd.MultiIndex.from_product([ids, ALL_TAUS], names=["material_id", "tau"])


def _column_from(source: pd.DataFrame, index: pd.MultiIndex, column: str) -> pd.Series:
    if source.empty or column not in source:
        return pd.Series(np.nan, index=index, dtype=float)
    keyed = source.drop_duplicates(["material_id", "tau"]).set_index(["material_id", "tau"])[column]
    return keyed.reindex(index)


def f_table(rows: pd.DataFrame, ids: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return F's best certified CR/config and whether all 18 searches ran."""
    index = _index(ids)
    out = pd.DataFrame(index=index)
    ran = pd.DataFrame(index=index)
    if rows.empty:
        out["F"] = np.nan
        out["F_config"] = pd.Series(index=index, dtype=object)
        ran["F"] = False
        return out, ran
    rows = rows[rows.material_id.isin(ids)].copy()
    rows["tau"] = pd.to_numeric(rows["tau"], errors="coerce")
    certified = rows[truthy(rows["certified"])].copy()
    if certified.empty:
        out["F"] = np.nan
        out["F_config"] = pd.Series(index=index, dtype=object)
    else:
        certified["cr"] = pd.to_numeric(certified["cr"], errors="coerce")
        best = (
            certified.dropna(subset=["cr"])
            .sort_values(["material_id", "tau", "cr", "config"], ascending=[True, True, False, True])
            .drop_duplicates(["material_id", "tau"])
            .set_index(["material_id", "tau"])
        )
        out["F"] = best["cr"].reindex(index)
        out["F_config"] = best["config"].reindex(index).astype(object)
    all_configs = set(R.CONFIG_BY_ID)
    ran_by_key = rows.groupby(["material_id", "tau"])["config"].agg(lambda values: set(values) >= all_configs)
    ran["F"] = ran_by_key.reindex(index, fill_value=False).astype(bool)
    return out, ran


def wide_table(rows: pd.DataFrame, law: pd.DataFrame, bp: pd.DataFrame, ids: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    index = _index(ids)
    out = pd.DataFrame(index=index)
    ran = pd.DataFrame(index=index)
    law = law[law.material_id.isin(ids)].copy()
    bp = bp[bp.material_id.isin(ids)].copy()
    law_index = set(zip(law.material_id, pd.to_numeric(law.tau))) if not law.empty else set()
    bp_index = set(zip(bp.material_id, pd.to_numeric(bp.tau))) if not bp.empty else set()
    for column in ("A1", "A2", "A3", "A6"):
        out[column] = _column_from(law, index, column)
        ran[column] = [key in law_index for key in index]
    for column in ("M2", "Mbest", "Q"):
        out[column] = _column_from(bp, index, column)
        ran[column] = [key in bp_index for key in index]
    f, f_ran = f_table(rows, ids)
    out = out.join(f)
    ran = ran.join(f_ran)
    return out, ran


def ratio_stats(table: pd.DataFrame, ran: pd.DataFrame, numerator: str, denominator: str) -> dict[str, Any]:
    both = table[numerator].notna() & table[denominator].notna()
    ratios = (table[numerator] / table[denominator])[both]
    denominator_ran = ran[denominator].astype(bool) if denominator in ran else pd.Series(False, index=table.index)
    never = int((table[numerator].notna() & table[denominator].isna() & denominator_ran).sum())
    not_run = int((table[numerator].notna() & table[denominator].isna() & ~denominator_ran).sum())
    return {
        "n_both_certified": int(ratios.size),
        "wins": int((ratios > 1).sum()),
        "baseline_never_certified": never,
        "wins_incl_never_certified": int((ratios > 1).sum()) + never,
        "baseline_not_run": not_run,
        "numerator_not_certified": int(table[numerator].isna().sum()),
        "median": float(ratios.median()) if ratios.size else None,
        "ci95": boot(ratios.to_numpy()) if ratios.size else None,
        "min": float(ratios.min()) if ratios.size else None,
        "max": float(ratios.max()) if ratios.size else None,
    }


def arm_medians(table: pd.DataFrame) -> dict[str, Any]:
    arms = ("A1", "A2", "A3", "A6", "M2", "Mbest", "Q", "F")
    return {
        arm: {
            "n_certified": int(table[arm].notna().sum()),
            "median_cr": float(table[arm].median()) if table[arm].notna().any() else None,
        }
        for arm in arms
    }


def fail_time(rows: pd.DataFrame, evals: pd.DataFrame, failures: pd.DataFrame, ids: list[str]) -> dict[str, Any]:
    rows = rows[rows.material_id.isin(ids)] if not rows.empty else rows
    evals = evals[evals.material_id.isin(ids)] if not evals.empty else evals
    failures = failures[failures.material_id.isin(ids)] if not failures.empty else failures
    out: dict[str, Any] = {}
    row_configs = set(R.CONFIG_BY_ID)
    ev = evals[evals.config.isin(row_configs)] if not evals.empty and "config" in evals else evals
    fl = failures[failures.config.isin(row_configs)] if not failures.empty and "config" in failures else failures
    out["evaluations"] = int(len(ev))
    out["failed_evaluations"] = int(len(fl))
    out["materials_with_failed_evaluations"] = int(fl.material_id.nunique()) if not fl.empty else 0
    out["failure_examples"] = sorted(set(fl.error.astype(str).str[:160]))[:5] if not fl.empty and "error" in fl else []
    per_tau: dict[str, Any] = {}
    for tau in TAUS:
        if rows.empty:
            seconds = pd.Series(dtype=float)
        else:
            subset = rows[pd.to_numeric(rows.tau, errors="coerce") == tau].copy()
            subset["search_seconds"] = pd.to_numeric(subset["search_seconds"], errors="coerce").fillna(0.0)
            seconds = subset.groupby("material_id").search_seconds.sum()
        per_tau[f"tau_{tau:g}"] = {
            "median_seconds_per_material": float(seconds.median()) if not seconds.empty else None,
            "total_hours": float(seconds.sum() / 3600.0) if not seconds.empty else 0.0,
        }
    out["search_wall_time"] = per_tau
    if not ev.empty and "seconds" in ev:
        out["codec_plus_certificate_hours"] = float(pd.to_numeric(ev.seconds, errors="coerce").fillna(0.0).sum() / 3600.0)
    else:
        out["codec_plus_certificate_hours"] = 0.0
    out["searches"] = int(len(rows))
    out["searches_codec_never_executed"] = int((pd.to_numeric(rows.lo_decades_skipped, errors="coerce") == -1).sum()) if not rows.empty else 0
    out["searches_lower_bound_raised"] = int((pd.to_numeric(rows.lo_decades_skipped, errors="coerce") > 0).sum()) if not rows.empty else 0
    material_level = failures[failures.get("arm", pd.Series(index=failures.index, dtype=object)).astype(str) == "material"] if not failures.empty else failures
    out["material_level_failures"] = sorted(material_level.material_id.unique().tolist()) if not material_level.empty else []
    return out


def cohort_summary(name: str, repo: Path, rows: pd.DataFrame, evals: pd.DataFrame, failures: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    ids = [row["material_id"] for row in R._read_manifest(repo, COHORTS[name])]
    law = pd.read_csv(repo / LAW / f"run_{name}" / "part_a_material.csv")
    bp = pd.read_csv(repo / BP / f"run_{name}" / "material.csv")
    table, ran = wide_table(rows, law, bp, ids)
    material = table.reset_index()
    material.insert(0, "cohort", name)
    for arm in ("A1", "A2", "A3", "A6", "M2", "Mbest", "Q", "F"):
        material[f"{arm}_search_ran"] = ran[arm].to_numpy()
    summaries: dict[str, Any] = {"materials": len(ids), "materials_with_rows": int(rows.material_id.nunique()) if not rows.empty else 0}
    for tau in TAUS:
        tt = table.xs(tau, level="tau")
        rr = ran.xs(tau, level="tau")
        summaries[f"tau_{tau:g}"] = {
            "median_cr": arm_medians(tt),
            "ratios": {
                "A1_over_F": ratio_stats(tt, rr, "A1", "F"),
                "A3_over_F": ratio_stats(tt, rr, "A3", "F"),
                "F_over_A6": ratio_stats(tt, rr, "F", "A6"),
                "F_over_Q": ratio_stats(tt, rr, "F", "Q"),
            },
        }
    summaries["failures_and_wall_time"] = fail_time(rows, evals, failures, ids)
    return material, summaries


def _summary_csv(summaries: dict[str, Any]) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for cohort, summary in summaries["cohorts"].items():
        for tau in TAUS:
            block = summary[f"tau_{tau:g}"]
            for arm, values in block["median_cr"].items():
                records.append({"cohort": cohort, "tau": tau, "kind": "arm", "arm": arm,
                                 "n_certified": values["n_certified"], "median_cr": values["median_cr"]})
            for ratio, values in block["ratios"].items():
                row = {"cohort": cohort, "tau": tau, "kind": "ratio", "ratio": ratio}
                row.update(values)
                records.append(row)
    return pd.DataFrame(records)


def _fmt(value: Any) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "NA"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _draft(summaries: dict[str, Any]) -> str:
    lines = ["# FFCz Hartree-baseline results", ""]
    for cohort, summary in summaries["cohorts"].items():
        lines += [f"## {cohort}", ""]
        for tau in TAUS:
            block = summary[f"tau_{tau:g}"]
            lines += [f"### τ = {tau:g}", "", "| Arm | n certified | median CR |", "|---|---:|---:|"]
            for arm, values in block["median_cr"].items():
                lines.append(f"| {arm} | {values['n_certified']} | {_fmt(values['median_cr'])} |")
            lines += ["", "| Ratio | n | median | 95% CI | wins | baseline never certified |", "|---|---:|---:|---|---:|---:|"]
            for ratio, values in block["ratios"].items():
                ci = values["ci95"]
                ci_text = "NA" if ci is None else f"[{_fmt(ci[0])}, {_fmt(ci[1])}]"
                lines.append(f"| {ratio} | {values['n_both_certified']} | {_fmt(values['median'])} | {ci_text} | "
                             f"{values['wins']} | {values['baseline_never_certified']} |")
            lines.append("")
        lines += ["Failure and wall-time accounting: " + json.dumps(summary["failures_and_wall_time"], sort_keys=True), ""]
    return "\n".join(lines)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_DEFAULT)
    parser.add_argument("--raw-root", type=Path, default=HERE / "results_raw")
    parser.add_argument("--output-dir", type=Path, default=HERE / "results")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    repo = args.repo_root.resolve()
    hashes = check_reference_inputs(repo)
    rows = many(args.raw_root, "rows_*.csv")
    evals = many(args.raw_root, "evals_*.csv")
    failures = many(args.raw_root, "failures_*.csv")
    materials: list[pd.DataFrame] = []
    summaries: dict[str, Any] = {"protocol": "analysis/hartree_baseline_ffcz_20261012/PROTOCOL.md", "seed": 20261012,
                                 "bootstrap": "aggregate_law.boot with aggregate_law.SEED=20261012", "input_sha256": hashes,
                                 "cohorts": {}}
    for cohort in COHORTS:
        material, summary = cohort_summary(cohort, repo, rows, evals, failures)
        materials.append(material)
        summaries["cohorts"][cohort] = summary
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    pd.concat(materials, ignore_index=True).to_csv(out / "material.csv", index=False)
    _summary_csv(summaries).to_csv(out / "summary.csv", index=False)
    (out / "SUMMARY.json").write_text(json.dumps(summaries, indent=2, allow_nan=False), encoding="utf-8")
    (out / "RESULTS_DRAFT.md").write_text(_draft(summaries), encoding="utf-8")
    print(json.dumps({"cohorts": {key: value["materials"] for key, value in summaries["cohorts"].items()},
                      "rows": len(rows), "evals": len(evals), "failures": len(failures)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
