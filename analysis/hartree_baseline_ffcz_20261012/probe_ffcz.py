#!/usr/bin/env python3
"""FFCz probe: synthetic FFT-bound semantics followed by the shakedown material."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
REPO_DEFAULT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_DEFAULT / "analysis" / "qoac_v03_rdo"))
import codecs_ffcz as C  # noqa: E402
import run_ffcz as R  # noqa: E402


SYNTHETIC_SHAPE = (48, 56, 72)
SYNTHETIC_MODES = ("REL", "PTW")
SYNTHETIC_R = (1e-2, 1e-4)
GATING_MODES = ("REL",)


def smooth_field(shape: tuple[int, int, int] = SYNTHETIC_SHAPE) -> np.ndarray:
    i, j, k = np.meshgrid(*[np.arange(n) for n in shape], indexing="ij")
    field = (
        np.sin(2 * np.pi * i / shape[0])
        + 0.5 * np.cos(2 * np.pi * 2 * j / shape[1]) * np.sin(2 * np.pi * k / shape[2])
        + 0.3 * np.cos(2 * np.pi * 3 * k / shape[2])
    )
    return field + 0.01 * np.random.default_rng(1).normal(size=shape)


def frequency_bound_ratio(original: np.ndarray, reconstructed: np.ndarray, r: float, mode: str) -> float:
    """The exact numpy FFT checks frozen in FFCz protocol §7."""
    original = np.asarray(original, dtype=np.float64)
    reconstructed = np.asarray(reconstructed, dtype=np.float64)
    spectrum = np.fft.fftn(original)
    delta = np.fft.fftn(reconstructed - original)
    mode = str(mode).upper()
    if mode == "REL":
        denominator = float(r) * float(np.max(np.abs(spectrum)))
        return float(np.max(np.abs(delta)) / denominator)
    if mode == "PTW":
        mask = np.abs(spectrum) > 0
        if not np.any(mask):
            return 0.0
        return float(np.max(np.abs(delta)[mask] / (float(r) * np.abs(spectrum)[mask])))
    raise ValueError(f"unknown frequency mode {mode!r}")


def spatial_bound_ratio(original: np.ndarray, reconstructed: np.ndarray, abs_bound: float) -> float:
    return float(np.max(np.abs(np.asarray(reconstructed) - np.asarray(original))) / float(abs_bound))


def _file_sha(path: Path) -> str | None:
    if not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _usage(executable: str | Path, usage_file: Path | None) -> str:
    if usage_file is not None and usage_file.is_file():
        return usage_file.read_text(encoding="utf-8", errors="replace")
    try:
        result = subprocess.run([str(executable)], capture_output=True, text=True, timeout=30, check=False)
        return (result.stdout or "") + (result.stderr or "")
    except Exception as exc:
        return f"usage capture failed: {type(exc).__name__}: {exc}"


def synthetic_probe(executable: str | Path, output_dir: Path) -> dict[str, Any]:
    field = smooth_field()
    ptp = float(np.ptp(field))
    abs_bound = 1e-3 * ptp
    output: dict[str, Any] = {
        "shape": list(field.shape),
        "base_codec": "SZ3",
        "eps_b_rel": 1e-3,
        "eps_b": abs_bound,
        "axis_order": C.FFCZ_AXIS_ORDER,
        "checks": [],
    }
    with tempfile.TemporaryDirectory(prefix="ffcz_synthetic_probe_") as temporary:
        workdir = Path(temporary)
        source_raw = workdir / "rho.raw"
        np.ascontiguousarray(field, dtype="<f8").tofile(source_raw)
        try:
            base = C.prepare_base("sz3", field, abs_bound, workdir / "base", name="base", source_raw=source_raw)
        except Exception as exc:
            error = {"mode": "ALL", "error": f"{type(exc).__name__}: {exc}"}
            output["checks"].extend(error for _ in SYNTHETIC_MODES for _ in SYNTHETIC_R)
            output["success"] = False
            return output
        for mode in SYNTHETIC_MODES:
            for r in SYNTHETIC_R:
                check: dict[str, Any] = {"mode": mode, "r": r}
                try:
                    rec, _base_bytes, edits_bytes, details = C.run_ffcz_roundtrip(
                        executable, source_raw, base, abs_bound, mode, r, workdir, tag=f"{mode}_{r:.0e}"
                    )
                    freq_ratio = frequency_bound_ratio(field, rec, r, mode)
                    spatial_ratio = spatial_bound_ratio(field, rec, abs_bound)
                    check.update({
                        "ok": True,
                        "edits_bytes": int(edits_bytes),
                        "spatial_linf_over_eps_b": spatial_ratio,
                        "frequency_ratio": freq_ratio,
                        "bound_confirmed": bool(freq_ratio <= 1.0 + 1e-6),
                        "spatial_bound_confirmed": bool(spatial_ratio <= 1.0 + 1e-6),
                        "details": details,
                    })
                except Exception as exc:
                    check.update({"ok": False, "error": f"{type(exc).__name__}: {exc}", "bound_confirmed": False})
                output["checks"].append(check)
    output["success"] = bool(output["checks"]) and all(c.get("ok") for c in output["checks"])
    # DEVIATIONS 5: only REL gates the run. FFCz's PTW bound is not the protocol's |ΔF(k)| <= r|F(k)|, so its ratio is
    # reported and PTW points are judged by the decoded Hartree certificate alone.
    output["gating_modes"] = list(GATING_MODES)
    output["all_frequency_bounds_confirmed"] = bool(output["success"] and all(
        c.get("bound_confirmed") for c in output["checks"] if c.get("mode") in GATING_MODES))
    output["ptw_frequency_bounds_confirmed"] = bool(output["success"] and all(
        c.get("bound_confirmed") for c in output["checks"] if c.get("mode") == "PTW"))
    return output


def shakedown_probe(repo: Path, inputs: Path, output_dir: Path, executable: str | Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    shakedown_dir = output_dir / "shakedown"
    for task in R.task_ids(repo, "probe"):
        command = [
            sys.executable,
            str(HERE / "run_ffcz.py"),
            "--repo-root", str(repo),
            "--inputs", str(inputs),
            "--output-dir", str(shakedown_dir),
            "--phase", "probe",
            "--task", task,
            "--ffcz-exe", str(executable),
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            results.append({
                "task": task,
                "returncode": int(result.returncode),
                "stdout": result.stdout[-1200:],
                "stderr": result.stderr[-1200:],
            })
        except Exception as exc:
            results.append({"task": task, "returncode": -1, "error": f"{type(exc).__name__}: {exc}"})
    return results


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_DEFAULT)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--ffcz-exe", required=True)
    parser.add_argument("--build-log", type=Path)
    parser.add_argument("--usage-file", type=Path)
    parser.add_argument("--binary-sha256", type=Path)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    repo = args.repo_root.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    synthetic = synthetic_probe(args.ffcz_exe, output_dir)
    payload: dict[str, Any] = {
        "protocol": "analysis/hartree_baseline_ffcz_20261012/PROTOCOL.md §7",
        "executable": str(Path(args.ffcz_exe).resolve()),
        "binary_sha256": _file_sha(Path(args.ffcz_exe)),
        "recorded_binary_sha256": args.binary_sha256.read_text(encoding="utf-8").strip() if args.binary_sha256 and args.binary_sha256.is_file() else None,
        "usage_text": _usage(args.ffcz_exe, args.usage_file),
        "build_log": str(args.build_log) if args.build_log else None,
        "synthetic": synthetic,
        "shakedown": shakedown_probe(repo, args.inputs.resolve(), output_dir, args.ffcz_exe),
    }
    (output_dir / "probe.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    lines = [
        f"axis_order: {C.FFCZ_AXIS_ORDER}",
        f"binary_sha256: {payload['binary_sha256']}",
        f"synthetic_success: {synthetic.get('success')}",
        f"synthetic_frequency_bounds_confirmed (gating {synthetic.get('gating_modes')}): "
        f"{synthetic.get('all_frequency_bounds_confirmed')}",
        f"synthetic_ptw_frequency_bounds_confirmed (reported): {synthetic.get('ptw_frequency_bounds_confirmed')}",
    ]
    for check in synthetic.get("checks", []):
        lines.append(f"synthetic {check.get('mode')} r={check.get('r')}: {check}")
    for result in payload["shakedown"]:
        lines.append(f"shakedown {result['task']}: rc={result['returncode']}")
    (output_dir / "probe_summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"synthetic": synthetic.get("success"), "shakedown_tasks": len(payload["shakedown"]),
                      "shakedown_failures": sum(r.get("returncode") != 0 for r in payload["shakedown"])}, sort_keys=True))
    return 0 if synthetic.get("all_frequency_bounds_confirmed", False) else 1


if __name__ == "__main__":
    raise SystemExit(main())
