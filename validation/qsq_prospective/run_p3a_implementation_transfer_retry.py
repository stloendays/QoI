#!/usr/bin/env python3
"""Engineering-only retry wrapper for the unresolved cells of frozen P3A.

The first-run scientific runner is intentionally left unchanged. This wrapper
only (1) interprets the archived amplitude token at its stored decimal
serialization precision for the source-consistency gate and (2) dispatches the
pre-frozen unresolved material set. Perturbation amplitudes used by the base
runner remain the archived numeric values; seeds, solvers, panel and thresholds
are unchanged.
"""
from __future__ import annotations

import csv
import math
from decimal import Decimal, InvalidOperation
from pathlib import Path

import numpy as np

import run_p3a_implementation_transfer as base

HERE = Path(__file__).resolve().parent
RETRY_FILE = HERE / "p3a_retry_materials.txt"
_ARCHIVED_AMPLITUDE_TOKEN: dict[str, str] = {}


def load_retry_materials() -> set[str]:
    materials = {
        line.strip()
        for line in RETRY_FILE.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    if len(materials) != 20:
        raise RuntimeError(f"P3A retry set must contain exactly 20 materials; got {len(materials)}")
    return materials


RETRY_MATERIALS = load_retry_materials()
_BASE_SHARD_FOR = base.shard_for


def retry_shard_for(material: str, n: int) -> int:
    """Keep base deterministic sharding, but dispatch only frozen unresolved materials."""
    if material not in RETRY_MATERIALS:
        return n
    return _BASE_SHARD_FOR(material, n)


def load_amplitudes_with_archive_tokens(root: Path) -> dict[str, float]:
    """Load the same frozen numeric amplitudes while preserving their literal CSV tokens."""
    tokens: dict[str, list[str]] = {}
    seeds: dict[str, set[int]] = {}
    path = root / "stability/stability_floor_A1_per_seed.csv"
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            material = row["material_id"]
            tokens.setdefault(material, []).append(row["probe_linf"].strip())
            seeds.setdefault(material, set()).add(int(row["seed"]))

    out: dict[str, float] = {}
    for material, values in tokens.items():
        if seeds[material] != set(base.OLD_SEEDS) or len(values) != 5 or len(set(values)) != 1:
            raise RuntimeError(f"legacy amplitude/seed drift for {material}")
        token = values[0]
        try:
            value = float(token)
            Decimal(token)
        except (ValueError, InvalidOperation) as exc:
            raise RuntimeError(f"invalid archived amplitude token for {material}: {token!r}") from exc
        if not math.isfinite(value) or value <= 0:
            raise RuntimeError(f"non-positive/non-finite archived amplitude for {material}: {token!r}")
        _ARCHIVED_AMPLITUDE_TOKEN[material] = token
        out[material] = value
    return out


def archive_decimal_quantum(token: str) -> float:
    """One unit in the last decimal place represented by the archived literal token."""
    dec = Decimal(token)
    quantum = Decimal(1).scaleb(dec.as_tuple().exponent)
    return float(abs(quantum))


def verify_archive_compatible_amplitude(field: np.ndarray, recorded: float, material: str) -> float:
    """Verify source identity at the precision actually retained by the historical CSV.

    The archived numeric value remains the perturbation amplitude used by the base
    runner. This check only asks whether a source-rederived float32 round-trip
    amplitude is compatible with the exact archived decimal token. A one-unit-in-
    the-last-stored-decimal bound permits either rounding or truncation at export;
    a small binary64 allowance prevents the comparison itself from becoming an
    ULP-level serialization test.
    """
    token = _ARCHIVED_AMPLITUDE_TOKEN.get(material)
    if token is None:
        raise RuntimeError(f"archived amplitude token unavailable for {material}")
    derived = float(np.max(np.abs(field.astype(np.float32).astype(np.float64) - field)))
    decimal_tol = archive_decimal_quantum(token)
    binary_tol = 8.0 * max(math.ulp(recorded), math.ulp(derived))
    tol = decimal_tol + binary_tol
    if not math.isclose(derived, recorded, rel_tol=0.0, abs_tol=tol):
        raise RuntimeError(
            f"legacy float32 amplitude incompatible with archived decimal token for {material}: "
            f"derived={derived:.17g} archived_token={token} decimal_quantum={decimal_tol:.3g} tol={tol:.3g}"
        )
    return derived


base.shard_for = retry_shard_for
base.load_amplitudes = load_amplitudes_with_archive_tokens
base.verify_legacy_amplitude = verify_archive_compatible_amplitude


if __name__ == "__main__":
    raise SystemExit(base.main())
