#!/usr/bin/env python3
"""Aggregate self-contained label-byte shards and compute the frozen metrics."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
MANIFEST_REL = Path("analysis/fresh_population_20261006/P2_CONFIRMATORY_MANIFEST.csv")
BEST_REL = Path("analysis/qoac_hb_v2/results/P2_CONFIRMATORY_MANIFEST/joint_v2_best_post.csv")
MATERIALS_REL = Path("analysis/qoac_hb_v2/results/P2_CONFIRMATORY_MANIFEST/materials.csv")

EXPECTED_MANIFEST_SHA256 = "361202189512883931c90a9fe62d7cb48fd4f7294a55ae019d781c7c89aafab5"
EXPECTED_BEST_SHA256 = "d740c09a906a85f351f06c9adf8845e3261d64cc834171f5cf9b053caf1a307f"
EXPECTED_MATERIALS_SHA256 = "e302831dc8c133dc674c21581bc5c759dc994c4baf481cdaa5eb7307628da73b"

BASES = ("R3", "J", "T1", "GF", "GP")
DEFAULT_TAUS = ("0.001", "0.0001", "1e-05")
BOOTSTRAP_SEED = 20261012
BOOTSTRAP_REPS = 10_000
SOLE_CERTIFIER_RATIO = 1e9

LABEL_COLUMNS = [
    "material_id",
    "task_id",
    "shape",
    "npoints",
    "natoms",
    "label_bytes_primary",
    "label_bytes_ctx",
    "n_labels",
    "roundtrip_ok",
    "charge_check_ok",
    "max_charge_diff_e",
    "status",
    "seconds",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_reference_hashes(repo_root: Path = REPO_ROOT) -> dict[str, str]:
    """Check the two committed HB-v2 byte sources named by the protocol."""
    paths = {
        "joint_v2_best_post.csv": (repo_root / BEST_REL, EXPECTED_BEST_SHA256),
        "materials.csv": (repo_root / MATERIALS_REL, EXPECTED_MATERIALS_SHA256),
    }
    actual: dict[str, str] = {}
    for name, (path, expected) in paths.items():
        if not path.is_file():
            raise RuntimeError(f"reference file is missing: {path}")
        got = sha256_file(path)
        actual[name] = got
        if got != expected:
            raise RuntimeError(f"{name} SHA-256 mismatch: {got} != {expected}")
    return actual


def tau_label(value: Any) -> str:
    return f"{float(value):g}"


def _ordered_unique(values: Iterable[Any]) -> list[str]:
    return list(dict.fromkeys(str(v) for v in values if pd.notna(v) and str(v) != ""))


def _as_bool(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def read_shards(shards_root: Path, stem: str) -> pd.DataFrame:
    """Read all artifact CSVs named ``<stem>_shard_*.csv``."""
    parts: list[pd.DataFrame] = []
    for path in sorted(shards_root.rglob(f"{stem}_shard_*.csv")):
        frame = pd.read_csv(path)
        if "material_id" in frame.columns:
            frame = frame[frame["material_id"].notna() & (frame["material_id"].astype(str) != "")]
        if len(frame):
            parts.append(frame)
    if parts:
        return pd.concat(parts, ignore_index=True)
    return pd.DataFrame(columns=LABEL_COLUMNS if stem == "materials" else ["material_id"])


def round_stream_bytes(raw_bytes: int | float, compression_ratio: float) -> int | None:
    """Apply protocol section 3's integer stream-byte conversion."""
    if not np.isfinite(float(compression_ratio)) or float(compression_ratio) <= 0:
        return None
    value = float(raw_bytes) / float(compression_ratio)
    if not np.isfinite(value) or value < 0:
        return None
    return int(round(value))


def _normalise_best(best: pd.DataFrame) -> pd.DataFrame:
    required = {"material_id", "base", "tau_bader", "best_joint_cr", "hartree_only_cr"}
    missing = sorted(required - set(best.columns))
    if missing:
        raise RuntimeError(f"joint_v2_best_post.csv lacks columns: {missing}")
    out = best.copy()
    out["material_id"] = out["material_id"].astype(str)
    out["base"] = out["base"].astype(str)
    out["tau_B"] = out["tau_bader"].map(tau_label)
    for column in ("best_joint_cr", "hartree_only_cr"):
        out[column] = pd.to_numeric(out[column], errors="coerce")
    if out.duplicated(["material_id", "base", "tau_B"]).any():
        raise RuntimeError("joint_v2_best_post.csv has duplicate material/base/tau rows")
    return out


def _normalise_materials(materials: pd.DataFrame) -> pd.DataFrame:
    out = materials.copy()
    if "material_id" not in out.columns:
        raise RuntimeError("material shard rows lack material_id")
    out["material_id"] = out["material_id"].astype(str)
    for column in ("raw_bytes", "npoints", "natoms"):
        if column in out.columns:
            out[column] = pd.to_numeric(out[column], errors="coerce")
    return out


def _label_usable(row: pd.Series) -> bool:
    return bool(
        str(row.get("status", "")) == "SUCCESS"
        and _as_bool(row.get("roundtrip_ok", False))
        and _as_bool(row.get("charge_check_ok", False))
        and pd.notna(row.get("label_bytes_primary"))
    )


def _material_ids_from(materials: pd.DataFrame, material_ids: Iterable[str] | None) -> list[str]:
    if material_ids is not None:
        return [str(x) for x in material_ids]
    return _ordered_unique(materials.get("material_id", []))


def build_per_material_table(
    best: pd.DataFrame,
    materials: pd.DataFrame,
    material_ids: Iterable[str] | None = None,
    bases: Iterable[str] | None = None,
    taus: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Build one row per material, tau_B and base.

    ``materials`` is the reference ``materials.csv`` joined to the label
    shard rows.  Label bytes remain visible for failed checks, but all
    self-contained metrics are unaccounted (NaN) unless both checks passed.
    """
    b = _normalise_best(best)
    m = _normalise_materials(materials)
    ids = _material_ids_from(m, material_ids)
    if len(ids) != len(set(ids)):
        raise RuntimeError("material_ids contain duplicates")
    selected_bases = list(bases) if bases is not None else _ordered_unique(b["base"])
    selected_taus = list(taus) if taus is not None else sorted(_ordered_unique(b["tau_B"]), key=float, reverse=True)
    if not selected_bases:
        selected_bases = list(BASES)
    if not selected_taus:
        selected_taus = list(DEFAULT_TAUS)

    material_map = {}
    for _, row in m.iterrows():
        mid = str(row["material_id"])
        if mid in material_map:
            raise RuntimeError(f"duplicate material shard row: {mid}")
        material_map[mid] = row
    best_map = {
        (str(row["material_id"]), str(row["base"]), str(row["tau_B"])): row
        for _, row in b.iterrows()
    }

    rows: list[dict[str, Any]] = []
    for mid in ids:
        material = material_map.get(mid, pd.Series(dtype=object))
        raw = pd.to_numeric(material.get("raw_bytes"), errors="coerce")
        label_bytes = pd.to_numeric(material.get("label_bytes_primary"), errors="coerce")
        context_bytes = pd.to_numeric(material.get("label_bytes_ctx"), errors="coerce")
        n_labels = pd.to_numeric(material.get("n_labels"), errors="coerce")
        label_ok = _label_usable(material) if len(material) else False
        for tau in selected_taus:
            tau = tau_label(tau)
            by_base: dict[str, dict[str, Any]] = {}
            for base in selected_bases:
                ref = best_map.get((mid, str(base), tau))
                cr = None if ref is None else ref.get("best_joint_cr")
                cr = float(cr) if cr is not None and pd.notna(cr) else None
                stream = round_stream_bytes(raw, cr) if pd.notna(raw) and cr is not None else None
                cr_sc = (
                    float(raw) / (int(stream) + int(label_bytes))
                    if label_ok and pd.notna(raw) and stream is not None and pd.notna(label_bytes)
                    else None
                )
                by_base[str(base)] = {
                    "S": stream,
                    "CR_sc": cr_sc,
                    "best_joint_cr": cr,
                    "hartree_only_cr": (
                        float(ref["hartree_only_cr"])
                        if ref is not None and pd.notna(ref.get("hartree_only_cr"))
                        else None
                    ),
                }
            r3 = by_base.get("R3", {})
            gf = by_base.get("GF", {})
            r3_cr = r3.get("CR_sc")
            gf_cr = gf.get("CR_sc")
            other = [
                float(value["CR_sc"])
                for name, value in by_base.items()
                if name != "R3" and value.get("CR_sc") is not None and np.isfinite(value["CR_sc"])
            ]
            if r3_cr is None:
                utility = None
                r3_highest = False
            elif other:
                best_other = max(other)
                utility = float(r3_cr) / best_other
                r3_highest = bool(float(r3_cr) >= best_other)
            else:
                utility = float("inf")
                r3_highest = True
            s_h = round_stream_bytes(raw, r3.get("hartree_only_cr")) if pd.notna(raw) and r3.get("hartree_only_cr") is not None else None
            overhead = (
                (int(r3["S"]) + int(label_bytes)) / int(s_h)
                if label_ok and r3.get("S") is not None and pd.notna(label_bytes) and s_h not in (None, 0)
                else None
            )
            partition_share = (
                float(label_bytes) / (int(r3["S"]) + float(label_bytes))
                if label_ok and r3.get("S") is not None and pd.notna(label_bytes)
                else None
            )
            versus_gf = (
                float(r3_cr) / float(gf_cr)
                if r3_cr is not None and gf_cr is not None and float(gf_cr) != 0.0
                else None
            )
            for base in selected_bases:
                value = by_base[str(base)]
                rows.append(
                    {
                        "material_id": mid,
                        "tau_B": tau,
                        "base": str(base),
                        "material_status": str(material.get("status", "MISSING")),
                        "roundtrip_ok": _as_bool(material.get("roundtrip_ok", False)),
                        "charge_check_ok": _as_bool(material.get("charge_check_ok", False)),
                        "label_usable": label_ok,
                        "raw_bytes": int(raw) if pd.notna(raw) else None,
                        "S": value.get("S"),
                        "L": int(label_bytes) if pd.notna(label_bytes) else None,
                        "label_bytes_ctx": int(context_bytes) if pd.notna(context_bytes) else None,
                        "n_labels": int(n_labels) if pd.notna(n_labels) else None,
                        "best_joint_cr": value.get("best_joint_cr"),
                        "CR_sc": value.get("CR_sc"),
                        "S_H": s_h,
                        "O_sc": overhead,
                        "partition_share": partition_share,
                        "U_sc": utility,
                        "r3_highest": r3_highest,
                        "CR_sc_R3": r3_cr,
                        "CR_sc_GF": gf_cr,
                        "versus_best_pointwise": versus_gf,
                    }
                )
    return pd.DataFrame(rows)


def _finite_or_infinite(values: Iterable[Any]) -> np.ndarray:
    out = pd.to_numeric(pd.Series(list(values)), errors="coerce").to_numpy(dtype=float)
    return out[~np.isnan(out)]


def bootstrap_median(
    values: Iterable[Any],
    rng: np.random.Generator,
    reps: int = BOOTSTRAP_REPS,
    inf_replacement: float | None = None,
) -> dict[str, Any]:
    """Return n, median, percentile 95% CI, min and max for a median."""
    raw = _finite_or_infinite(values)
    if raw.size == 0:
        return {"n": 0, "median": None, "ci95": [None, None], "min": None, "max": None}
    transformed = raw.copy()
    n_inf = int(np.isinf(transformed).sum())
    if n_inf and inf_replacement is not None:
        transformed[np.isinf(transformed)] = float(inf_replacement)
    draws = rng.integers(0, transformed.size, size=(int(reps), transformed.size))
    medians = np.median(transformed[draws], axis=1)
    return {
        "n": int(raw.size),
        "median": float(np.median(transformed)),
        "ci95": [float(np.quantile(medians, 0.025)), float(np.quantile(medians, 0.975))],
        "min": float(np.min(raw)),
        "max": float(np.max(raw)),
        "n_infinite": n_inf,
    }


def _unique_material_tau(frame: pd.DataFrame, tau: str) -> pd.DataFrame:
    """Keep one row per material/tau/base for the repeated per-tau fields."""
    return frame[frame["tau_B"] == tau].drop_duplicates(["material_id", "tau_B", "base"])


def summarise(
    per_material: pd.DataFrame,
    material_rows: pd.DataFrame,
    taus: Iterable[str],
    seed: int = BOOTSTRAP_SEED,
    reps: int = BOOTSTRAP_REPS,
) -> tuple[dict[str, Any], pd.DataFrame]:
    """Compute all section 4 statistics and the tabular summary."""
    rng = np.random.default_rng(seed)
    summary_rows: list[dict[str, Any]] = []
    by_tau: dict[str, Any] = {}

    usable = material_rows.copy()
    if "label_usable" not in usable.columns:
        usable["label_usable"] = usable.apply(_label_usable, axis=1)
    label_ok = usable[usable["label_usable"] == True]  # noqa: E712
    label_primary = _finite_or_infinite(label_ok.get("label_bytes_primary", []))
    label_context = _finite_or_infinite(label_ok.get("label_bytes_ctx", []))
    label_primary_stats = bootstrap_median(label_primary, rng, reps)
    label_context_stats = bootstrap_median(label_context, rng, reps)
    for metric, stats in (("L_primary", label_primary_stats), ("L_context", label_context_stats)):
        summary_rows.append(
            {
                "tau_B": "all",
                "scope": "label",
                "base": "",
                "metric": metric,
                "n": stats["n"],
                "median": stats["median"],
                "ci_low": stats["ci95"][0],
                "ci_high": stats["ci95"][1],
                "minimum": stats["min"],
                "maximum": stats["max"],
                "wins": None,
                "n_sole_certifier": stats.get("n_infinite", 0),
            }
        )

    base_order = _ordered_unique(per_material.get("base", []))
    for tau in taus:
        tau = tau_label(tau)
        block: dict[str, Any] = {"by_base": {}}
        for base in base_order:
            g = per_material[(per_material["tau_B"] == tau) & (per_material["base"] == base)]
            stats = bootstrap_median(g["CR_sc"], rng, reps)
            block["by_base"][base] = {"CR_sc": stats}
            summary_rows.append(
                {
                    "tau_B": tau,
                    "scope": "base",
                    "base": base,
                    "metric": "CR_sc",
                    "n": stats["n"],
                    "median": stats["median"],
                    "ci_low": stats["ci95"][0],
                    "ci_high": stats["ci95"][1],
                    "minimum": stats["min"],
                    "maximum": stats["max"],
                    "wins": None,
                    "n_sole_certifier": stats.get("n_infinite", 0),
                }
            )

        unique = _unique_material_tau(per_material, tau)
        r3 = unique[unique["base"] == "R3"]
        r3_stats: dict[str, Any] = {}
        for column, metric in (
            ("O_sc", "O_sc"),
            ("partition_share", "partition_share"),
            ("U_sc", "U_sc"),
            ("versus_best_pointwise", "R3_over_GF"),
        ):
            inf_cap = SOLE_CERTIFIER_RATIO if column == "U_sc" else None
            stats = bootstrap_median(r3[column], rng, reps, inf_replacement=inf_cap)
            if column == "U_sc":
                highest = int(r3["r3_highest"].astype(bool).sum()) if len(r3) else 0
                block_metric = {**stats, "r3_highest": highest}
            else:
                block_metric = stats
            r3_stats[metric] = block_metric
            summary_rows.append(
                {
                    "tau_B": tau,
                    "scope": "R3",
                    "base": "R3",
                    "metric": metric,
                    "n": stats["n"],
                    "median": stats["median"],
                    "ci_low": stats["ci95"][0],
                    "ci_high": stats["ci95"][1],
                    "minimum": stats["min"],
                    "maximum": stats["max"],
                    "wins": block_metric.get("r3_highest"),
                    "n_sole_certifier": stats.get("n_infinite", 0),
                }
            )
        block["R3"] = r3_stats
        by_tau[tau] = block

    checks = {
        "materials_expected": int(len(material_rows)),
        "materials_reported": int(len(material_rows["material_id"].dropna().unique())) if len(material_rows) else 0,
        "roundtrip_ok": int(material_rows.get("roundtrip_ok", pd.Series(dtype=bool)).map(_as_bool).sum()),
        "charge_check_ok": int(material_rows.get("charge_check_ok", pd.Series(dtype=bool)).map(_as_bool).sum()),
        "both_checks_ok": int(label_ok["material_id"].nunique()) if len(label_ok) else 0,
        "unaccounted": int(len(material_rows) - label_ok["material_id"].nunique()),
    }
    summary = {
        "status": "COMPLETE",
        "materials": int(len(material_rows)),
        "bootstrap": {
            "seed": int(seed),
            "resamples": int(reps),
            "statistic": "median",
            "ci": "percentile 2.5% and 97.5%",
            "unit": "material",
        },
        "checks": checks,
        "label_bytes": {"primary": label_primary_stats, "context": label_context_stats},
        "by_tau": by_tau,
        "definitions": {
            "CR_sc": "raw_bytes / (S + L)",
            "O_sc": "(S_R3 + L) / S_H",
            "partition_share": "L / (S_R3 + L)",
            "U_sc": "CR_sc(R3) / max(CR_sc(other bases)); sole certifier uses 1e9 for median",
            "R3_over_GF": "CR_sc(R3) / CR_sc(GF)",
        },
    }
    return summary, pd.DataFrame(summary_rows)


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        value = float(value)
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _cell(value: Any) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ""
    if isinstance(value, (float, np.floating)):
        if np.isinf(value):
            return "inf" if value > 0 else "-inf"
        return f"{float(value):.12g}"
    return str(value)


def write_results(
    output_dir: Path,
    per_material: pd.DataFrame,
    summary: dict[str, Any],
    summary_table: pd.DataFrame,
    failures: pd.DataFrame,
    materials: pd.DataFrame,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    per_material.to_csv(output_dir / "per_material.csv", index=False)
    summary_table.to_csv(output_dir / "summary.csv", index=False)
    (output_dir / "SUMMARY.json").write_text(
        json.dumps(_json_safe(summary), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    failures.to_csv(output_dir / "failures.csv", index=False)
    materials.to_csv(output_dir / "materials.csv", index=False)

    lines = ["# RESULTS_DRAFT", "", "## summary", ""]
    columns = [
        "tau_B",
        "scope",
        "base",
        "metric",
        "n",
        "median",
        "ci_low",
        "ci_high",
        "minimum",
        "maximum",
        "wins",
        "n_sole_certifier",
    ]
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("|" + "|".join("---" for _ in columns) + "|")
    for _, row in summary_table.iterrows():
        lines.append("| " + " | ".join(_cell(row.get(c)) for c in columns) + " |")
    lines.extend(["", "## checks", ""])
    lines.append("| name | value |")
    lines.append("|---|---:|")
    for name, value in summary["checks"].items():
        lines.append(f"| {name} | {_cell(value)} |")
    (output_dir / "RESULTS_DRAFT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--shards-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = REPO_ROOT
    hashes = check_reference_hashes(repo_root)
    manifest = pd.read_csv(args.manifest, dtype={"material_id": str})
    if "material_id" not in manifest.columns:
        raise RuntimeError("manifest lacks material_id")
    manifest_ids = manifest["material_id"].astype(str).tolist()
    if len(manifest_ids) != len(set(manifest_ids)):
        raise RuntimeError("manifest has duplicate material_id values")
    reference_materials = pd.read_csv(repo_root / MATERIALS_REL, dtype={"material_id": str})
    # The reference HB-v2 material table has its own status column.  Preserve
    # it under a distinct name so the self-contained shard status controls the
    # check/accounting decision below.
    if "status" in reference_materials.columns:
        reference_materials = reference_materials.rename(columns={"status": "reference_status"})
    labels = read_shards(args.shards_root, "materials")
    failures = read_shards(args.shards_root, "failures")
    if len(labels) and labels["material_id"].astype(str).duplicated().any():
        duplicate = labels.loc[labels["material_id"].astype(str).duplicated(), "material_id"].tolist()
        raise RuntimeError(f"material reported by more than one shard: {duplicate}")
    labels["material_id"] = labels.get("material_id", pd.Series(dtype=str)).astype(str)
    reference_materials["material_id"] = reference_materials["material_id"].astype(str)
    if set(labels["material_id"]) - set(manifest_ids):
        raise RuntimeError("shard outputs contain materials outside the manifest")
    merged = reference_materials.merge(labels, on="material_id", how="left", suffixes=("", "_label"))
    bases = [base for base in BASES if base in set(pd.read_csv(repo_root / BEST_REL)["base"].astype(str))]
    best = pd.read_csv(repo_root / BEST_REL)
    taus = sorted(_ordered_unique(best["tau_bader"].map(tau_label)), key=float, reverse=True)
    if not bases:
        bases = list(BASES)
    if not taus:
        taus = list(DEFAULT_TAUS)
    per_material = build_per_material_table(
        best,
        merged,
        material_ids=manifest_ids,
        bases=bases,
        taus=taus,
    )
    observed = set(labels["material_id"])
    missing = [mid for mid in manifest_ids if mid not in observed]
    summary, summary_table = summarise(per_material, merged, taus)
    summary["manifest"] = str(args.manifest).replace("\\", "/")
    summary["manifest_sha256"] = sha256_file(args.manifest)
    summary["reference_sha256"] = hashes
    summary["materials_expected"] = int(len(manifest_ids))
    summary["materials_missing"] = missing
    summary["status"] = "COMPLETE" if not missing else "INCOMPLETE"
    write_results(args.output_dir.resolve(), per_material, summary, summary_table, failures, merged)
    print(json.dumps(_json_safe({k: summary[k] for k in ("status", "materials_expected", "materials_missing", "checks")}), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
