#!/usr/bin/env python3
"""Generate a deterministic Markdown report from frozen external aggregates.

The report structure is fixed before corpus-scale execution. It separates
workflow-integrity checks from scientific-transfer outcomes so a failure to
reproduce a development codec ordering cannot be mistaken for a software failure
or trigger post-hoc retuning.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

TAUS = ("0.0001", "0.001", "0.01")
CODECS = ("zfp", "sz3", "sperr")
DISPLAY = {"zfp": "ZFP", "sz3": "SZ3", "sperr": "SPERR"}
EXPECTED_ORDER = {
    "0.0001": "ZFP > SZ3 > SPERR",
    "0.001": "ZFP and SZ3 close; both > SPERR",
    "0.01": "SZ3 > ZFP > SPERR",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or not path.read_text().strip():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def as_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def fmt(x: Any, digits: int = 4) -> str:
    if x in (None, ""):
        return "—"
    try:
        v = float(x)
    except (TypeError, ValueError):
        return str(x)
    if v == 0:
        return "0"
    if abs(v) < 1e-3 or abs(v) >= 1e4:
        return f"{v:.3e}"
    return f"{v:.{digits}g}"


def median(values: list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--confirmatory-dir", required=True)
    p.add_argument("--all65-dir", required=True)
    p.add_argument("--output", required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    cdir = Path(args.confirmatory_dir)
    adir = Path(args.all65_dir)
    out = Path(args.output)

    cmeta = json.loads((cdir / "confirmatory_metadata.json").read_text())
    csum = json.loads((cdir / "summary.json").read_text())
    asum = json.loads((adir / "summary.json").read_text())
    summary_rows = read_csv(cdir / "external_summary_a1.csv")
    pairwise_rows = read_csv(cdir / "pairwise_external.csv")
    rows = read_csv(cdir / "formal_external_e2e_rows.csv")
    row_failures = read_csv(cdir / "formal_external_e2e_row_failures.csv")
    hard_failures = read_csv(cdir / "formal_external_e2e_failures.csv")

    overall = {
        (r["threshold_e"], r["codec"]): r
        for r in summary_rows
        if r["stratum"] == "overall"
    }
    pairs = [r for r in pairwise_rows if r["stratum"] == "overall"]

    # Pre-specified diagnostics from all successful confirmatory rows.
    linf_by_codec: dict[str, list[float]] = defaultdict(list)
    migration_by_codec: dict[str, list[float]] = defaultdict(list)
    resolved_over_fixed_by_codec: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        codec = r["codec"].lower()
        linf_by_codec[codec].append(float(r["realized_Linf_over_nominal"]))
        migration_by_codec[codec].append(float(r["atom_domain_migration_fraction"]))
        fixed = float(r["Bader_error_fixed_e"])
        resolved = float(r["Bader_error_resolved_e"])
        if fixed > 0 and math.isfinite(fixed) and math.isfinite(resolved):
            resolved_over_fixed_by_codec[codec].append(resolved / fixed)

    lines: list[str] = []
    lines += [
        "# External rate–fidelity validation report",
        "",
        "Generated deterministically from the frozen aggregate outputs. The report",
        "format and directional development expectations were specified before the",
        "corpus-scale run. Scientific non-replication is reported as an outcome, not",
        "treated as a reason to retune the benchmark.",
        "",
        "## Analysis populations",
        "",
        f"- Descriptive frozen corpus: **{asum['n_materials_observed']} systems**.",
        f"- Primary confirmatory cohort: **{cmeta['confirmatory_n']} systems**.",
        "- Implementation sentinels excluded only from the confirmatory rate–fidelity summary: "
        + ", ".join(f"`{x}`" for x in cmeta["excluded_implementation_sentinels"]) + ".",
        f"- Confirmatory Protocol A.1 eligible counts (1e-4 / 1e-3 / 1e-2 e): "
        f"**{csum['eligible_A1_counts_completed_materials']['1e-4']} / "
        f"{csum['eligible_A1_counts_completed_materials']['1e-3']} / "
        f"{csum['eligible_A1_counts_completed_materials']['1e-2']}**.",
        "",
        "## 1. Workflow integrity",
        "",
        f"- Confirmatory materials observed: **{csum['n_materials_observed']}**; complete: **{csum['n_materials_complete']}**.",
        f"- Hard material pipeline failures: **{csum['n_material_pipeline_failures']}**.",
        f"- Row-level failures: **{csum['n_row_failures']}** across "
        f"**{len(csum['row_failure_materials'])} materials**.",
        f"- Codec L∞ bound violations: **{csum['n_bound_violations']}**; all successful rows respect the bound: **{csum['all_codec_bounds_respected']}**.",
        f"- Source fields flagged with negative density values: **{csum['n_negative_source_density_materials']}**. This is an input-quality diagnostic, not a codec failure.",
        "",
    ]

    if hard_failures:
        lines += ["### Hard failures", ""]
        for r in hard_failures:
            lines.append(f"- `{r.get('material_id','')}` — {r.get('error_type','')}: {r.get('error','')}")
        lines.append("")
    if row_failures:
        by_cat: dict[str, int] = defaultdict(int)
        for r in row_failures:
            by_cat[r.get("category", "UNKNOWN")] += 1
        lines += ["### Row-level failure registry summary", ""]
        for cat in sorted(by_cat):
            lines.append(f"- `{cat}`: {by_cat[cat]}")
        lines.append("")

    lines += ["## 2. Confirmatory material-level certification and CCR", ""]
    lines.append("| τ (e) | Codec | Admitted | Certified | Certified fraction | Median CCR | 95% CI | p10–p90 |")
    lines.append("|---:|---|---:|---:|---:|---:|---:|---:|")
    for tau in TAUS:
        for codec in CODECS:
            r = overall.get((tau, codec), {})
            ci = f"{fmt(r.get('ratio_median_ci_lo'))}–{fmt(r.get('ratio_median_ci_hi'))}"
            spread = f"{fmt(r.get('ratio_p10'))}–{fmt(r.get('ratio_p90'))}"
            lines.append(
                f"| {tau} | {DISPLAY[codec]} | {r.get('n_admitted','—')} | {r.get('n_certified','—')} | "
                f"{fmt(r.get('frac_certified'))} | {fmt(r.get('ratio_median'))} | {ci} | {spread} |"
            )
        lines.append("")

    lines += ["## 3. Pairwise codec comparison on all admitted materials", ""]
    lines.append("| τ (e) | A vs B | n | A wins | ties | B wins | A-win 95% CI | n both CCR | median log2(A/B) |")
    lines.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|")
    for r in pairs:
        ci = f"{fmt(r.get('a_wins_ci_lo'))}–{fmt(r.get('a_wins_ci_hi'))}"
        lines.append(
            f"| {r['threshold_e']} | {r['codec_a'].upper()} vs {r['codec_b'].upper()} | {r['n']} | "
            f"{fmt(r['frac_a_wins'])} | {fmt(r['frac_ties'])} | {fmt(r['frac_b_wins'])} | {ci} | "
            f"{r.get('n_both_certified','—')} | {fmt(r.get('median_log2_ratio_a_over_b'))} |"
        )
    lines.append("")

    lines += ["## 4. Frozen development-derived directional expectations", ""]
    for tau in TAUS:
        medians = {
            codec: (
                float(overall[(tau, codec)]["ratio_median"])
                if overall.get((tau, codec), {}).get("ratio_median") not in (None, "")
                else None
            )
            for codec in CODECS
        }
        available = [(c, v) for c, v in medians.items() if v is not None]
        empirical_order = " > ".join(
            DISPLAY[c] for c, _ in sorted(available, key=lambda x: x[1], reverse=True)
        ) if available else "not estimable"
        lines += [
            f"### τ = {tau} e",
            "",
            f"- Pre-specified development expectation: **{EXPECTED_ORDER[tau]}**.",
            f"- Confirmatory ordering of marginal median CCR among certified materials: **{empirical_order}**.",
            "- Formal transfer interpretation should use the pairwise all-admitted table above together with certification fractions; marginal medians alone can involve different certified subsets.",
            "",
        ]

    lines += ["## 5. Requested versus realized error budget", ""]
    lines.append("| Codec | median realized L∞ / nominal bound | median domain migration fraction | median resolved/fixed Bader-error ratio* |")
    lines.append("|---|---:|---:|---:|")
    for codec in CODECS:
        lines.append(
            f"| {DISPLAY[codec]} | {fmt(median(linf_by_codec[codec]))} | "
            f"{fmt(median(migration_by_codec[codec]))} | {fmt(median(resolved_over_fixed_by_codec[codec]))} |"
        )
    lines += [
        "",
        "*Resolved/fixed ratio is calculated only for successful rows with nonzero fixed-basin error. It is a mechanism diagnostic, not a certification criterion.",
        "",
        "## 6. Interpretation boundary",
        "",
        "A successful workflow-integrity section establishes that the frozen external",
        "evaluation executed as specified. Reproduction or non-reproduction of codec",
        "rankings is a separate scientific result. No external outcome authorizes",
        "changing Protocol A.1, tolerance ladders, eligibility rules, early stopping,",
        "failure accounting, or the 63-system confirmatory population.",
        "",
    ]

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
