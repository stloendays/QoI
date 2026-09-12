#!/usr/bin/env python3
"""Deterministic decision-support layer for the QSQ benchmark.

This module never creates QSQ eligibility or scientific certification labels with
an LLM. It consumes frozen benchmark measurements and ranks only candidates that
satisfy the declared measurement contract.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

TRUE_VALUES = {"1", "true", "t", "yes", "y"}


@dataclass(frozen=True)
class Candidate:
    material_id: str
    codec: str
    codec_config: str
    compression_ratio: float
    bader_error_e: float
    realized_linf: Optional[float]
    encode_seconds: Optional[float]
    bader_seconds: Optional[float]
    nominal_tolerance_relative: Optional[float]
    nominal_tolerance_absolute: Optional[float]
    scientific_margin: float
    score: float = 0.0

    @property
    def total_seconds(self) -> Optional[float]:
        vals = [v for v in (self.encode_seconds, self.bader_seconds) if v is not None]
        return sum(vals) if vals else None


def _float(value: object) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "na"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _truthy(value: object) -> Optional[bool]:
    if value is None:
        return None
    text = str(value).strip().lower()
    if text == "":
        return None
    if text in TRUE_VALUES:
        return True
    if text in {"0", "false", "f", "no", "n"}:
        return False
    return None


def _threshold_tokens(tau: float) -> set[str]:
    sci = f"{tau:.0e}".replace("e-0", "e-").replace("e+0", "e+")
    plain = format(tau, ".10g")
    return {sci.lower(), plain.lower(), sci.lower().replace("-", "_")}


def _find_threshold_flag(fieldnames: Iterable[str], prefix: str, tau: float) -> Optional[str]:
    tokens = _threshold_tokens(tau)
    names = list(fieldnames)
    for name in names:
        low = name.lower()
        if not low.startswith(prefix.lower()):
            continue
        if any(token in low for token in tokens):
            return name
    return None


def _eligibility(row: dict[str, str], fieldnames: list[str], tau: float) -> tuple[Optional[bool], str]:
    flag = _find_threshold_flag(fieldnames, "eligible", tau)
    if flag:
        parsed = _truthy(row.get(flag))
        if parsed is not None:
            return parsed, flag

    floor = _float(row.get("stability_floor_A1_e"))
    if floor is not None:
        return floor < tau, "stability_floor_A1_e < tau"
    return None, "eligibility unavailable"


def _certified(row: dict[str, str], fieldnames: list[str], tau: float, eligible: bool) -> tuple[bool, str]:
    flag = _find_threshold_flag(fieldnames, "certified_at_", tau)
    if flag and "ignoring_eligibility" not in flag.lower():
        parsed = _truthy(row.get(flag))
        if parsed is not None:
            return bool(parsed and eligible), flag

    error = _float(row.get("Bader_error_resolved_e"))
    if error is None:
        return False, "Bader_error_resolved_e unavailable"
    return bool(eligible and error < tau), "eligible AND Bader_error_resolved_e < tau"


def _minmax(values: list[Optional[float]], reverse: bool = False) -> list[float]:
    present = [v for v in values if v is not None and math.isfinite(v)]
    if not present:
        return [0.5] * len(values)
    lo, hi = min(present), max(present)
    out = []
    for value in values:
        if value is None or not math.isfinite(value):
            score = 0.5
        elif hi == lo:
            score = 1.0
        else:
            score = (value - lo) / (hi - lo)
        out.append(1.0 - score if reverse else score)
    return out


def _score_balanced(candidates: list[Candidate], w_rate: float, w_margin: float, w_cost: float) -> list[Candidate]:
    rate = _minmax([math.log(max(c.compression_ratio, 1e-12)) for c in candidates])
    margin = _minmax([c.scientific_margin for c in candidates])
    cost = _minmax([c.total_seconds for c in candidates], reverse=True)
    denom = w_rate + w_margin + w_cost
    if denom <= 0:
        raise ValueError("At least one balanced-objective weight must be positive")

    scored: list[Candidate] = []
    for i, c in enumerate(candidates):
        score = (w_rate * rate[i] + w_margin * margin[i] + w_cost * cost[i]) / denom
        scored.append(Candidate(**{**c.__dict__, "score": score}))
    return scored


def _dedupe_operating_points(candidates: list[Candidate], objective: str) -> list[Candidate]:
    """Keep the best operating point per codec/config before cross-codec ranking."""
    groups: dict[tuple[str, str], list[Candidate]] = {}
    for c in candidates:
        groups.setdefault((c.codec, c.codec_config), []).append(c)

    selected: list[Candidate] = []
    for rows in groups.values():
        if objective == "max-margin":
            best = min(rows, key=lambda c: (c.bader_error_e, -c.compression_ratio))
        elif objective == "min-runtime":
            best = min(rows, key=lambda c: (c.total_seconds if c.total_seconds is not None else math.inf, -c.compression_ratio))
        else:
            best = max(rows, key=lambda c: (c.compression_ratio, c.scientific_margin))
        selected.append(best)
    return selected


def recommend(
    csv_path: Path,
    material_id: str,
    tau: float,
    objective: str,
    w_rate: float = 0.50,
    w_margin: float = 0.35,
    w_cost: float = 0.15,
) -> dict:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        rows = [row for row in reader if row.get("material_id") == material_id]

    if not rows:
        return {
            "status": "MATERIAL_NOT_FOUND",
            "material_id": material_id,
            "tau_e": tau,
            "recommendation": None,
        }

    eligibility_values = [_eligibility(row, fieldnames, tau) for row in rows]
    known_eligibility = [value for value, _ in eligibility_values if value is not None]
    if not known_eligibility:
        return {
            "status": "ELIGIBILITY_UNAVAILABLE",
            "material_id": material_id,
            "tau_e": tau,
            "recommendation": None,
            "guardrail": "No recommendation may be labeled scientifically certified without QSQ eligibility.",
        }

    eligible = all(known_eligibility)
    eligibility_source = next(source for value, source in eligibility_values if value is not None)
    if not eligible:
        return {
            "status": "NON_EVALUABLE_BADER_UNSTABLE",
            "material_id": material_id,
            "tau_e": tau,
            "eligible": False,
            "eligibility_source": eligibility_source,
            "recommendation": None,
            "guardrail": "QSQ does not support this absolute-Bader tolerance; codec pass/fail is not issued at this precision.",
        }

    candidates: list[Candidate] = []
    certification_sources: set[str] = set()
    for row in rows:
        is_certified, source = _certified(row, fieldnames, tau, eligible=True)
        certification_sources.add(source)
        if not is_certified:
            continue

        ratio = _float(row.get("compression_ratio"))
        error = _float(row.get("Bader_error_resolved_e"))
        if ratio is None or error is None:
            continue
        margin = max(0.0, (tau - error) / tau)
        candidates.append(
            Candidate(
                material_id=material_id,
                codec=(row.get("codec") or "").strip(),
                codec_config=(row.get("codec_config") or "").strip(),
                compression_ratio=ratio,
                bader_error_e=error,
                realized_linf=_float(row.get("realized_Linf")),
                encode_seconds=_float(row.get("encode_seconds")),
                bader_seconds=_float(row.get("bader_seconds")),
                nominal_tolerance_relative=_float(row.get("nominal_tolerance_relative")),
                nominal_tolerance_absolute=_float(row.get("nominal_tolerance_absolute")),
                scientific_margin=margin,
            )
        )

    if not candidates:
        return {
            "status": "NO_CERTIFIED_CANDIDATE",
            "material_id": material_id,
            "tau_e": tau,
            "eligible": True,
            "eligibility_source": eligibility_source,
            "recommendation": None,
            "guardrail": "The QoI is eligible, but no measured codec operating point satisfies the declared contract.",
        }

    candidates = _dedupe_operating_points(candidates, objective)
    if objective == "balanced":
        candidates = _score_balanced(candidates, w_rate=w_rate, w_margin=w_margin, w_cost=w_cost)
        ranked = sorted(candidates, key=lambda c: (c.score, c.compression_ratio), reverse=True)
    elif objective == "max-compression":
        ranked = sorted(candidates, key=lambda c: (c.compression_ratio, c.scientific_margin), reverse=True)
    elif objective == "max-margin":
        ranked = sorted(candidates, key=lambda c: (c.bader_error_e, -c.compression_ratio))
    elif objective == "min-runtime":
        ranked = sorted(candidates, key=lambda c: (c.total_seconds if c.total_seconds is not None else math.inf, -c.compression_ratio))
    else:
        raise ValueError(f"Unsupported objective: {objective}")

    def as_dict(c: Candidate) -> dict:
        return {
            "codec": c.codec,
            "codec_config": c.codec_config,
            "compression_ratio": c.compression_ratio,
            "Bader_error_resolved_e": c.bader_error_e,
            "scientific_margin_fraction": c.scientific_margin,
            "realized_Linf": c.realized_linf,
            "encode_seconds": c.encode_seconds,
            "bader_seconds": c.bader_seconds,
            "total_seconds": c.total_seconds,
            "nominal_tolerance_relative": c.nominal_tolerance_relative,
            "nominal_tolerance_absolute": c.nominal_tolerance_absolute,
            "decision_score": c.score if objective == "balanced" else None,
        }

    return {
        "status": "CERTIFIED_RECOMMENDATION",
        "material_id": material_id,
        "tau_e": tau,
        "eligible": True,
        "eligibility_source": eligibility_source,
        "certification_source": sorted(certification_sources),
        "objective": objective,
        "contract": "absolute re-derived Bader-charge error",
        "recommendation": as_dict(ranked[0]),
        "alternatives": [as_dict(c) for c in ranked[1:]],
        "guardrail": "Ranking is decision support among measured, QSQ-eligible, certified operating points; it is not a new scientific claim or an extrapolation to unmeasured settings.",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("benchmark/master_benchmark_full.csv"))
    parser.add_argument("--material-id", required=True)
    parser.add_argument("--tau", type=float, required=True, help="Absolute Bader tolerance in electrons, e.g. 1e-3")
    parser.add_argument(
        "--objective",
        choices=("max-compression", "max-margin", "min-runtime", "balanced"),
        default="balanced",
    )
    parser.add_argument("--weight-rate", type=float, default=0.50)
    parser.add_argument("--weight-margin", type=float, default=0.35)
    parser.add_argument("--weight-cost", type=float, default=0.15)
    parser.add_argument("--output", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = recommend(
        args.input,
        material_id=args.material_id,
        tau=args.tau,
        objective=args.objective,
        w_rate=args.weight_rate,
        w_margin=args.weight_margin,
        w_cost=args.weight_cost,
    )
    payload = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
