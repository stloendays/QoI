#!/usr/bin/env python3
"""Run one shard of the frozen 24-system P3A implementation-transfer panel."""
from __future__ import annotations
import argparse, csv, hashlib, json, sys, tempfile, time
from collections import defaultdict
from pathlib import Path
from typing import Any
import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from development_compatibility_smoke import build_grid, fetch_exact, load_metadata

OLD_SEEDS = (20260905, 1, 2, 3, 4)
SOLVERS = ("baderkit_ongrid", "henkelman_ongrid", "henkelman_neargrid")
TAUS = (1e-4, 1e-3, 1e-2)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--henkelman-binary", type=Path, required=True)
    p.add_argument("--shard-count", type=int, required=True)
    p.add_argument("--shard-index", type=int, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    return p.parse_args()


def shard_for(material: str, n: int) -> int:
    return int.from_bytes(hashlib.sha256(("QSQ-P3A|" + material).encode()).digest()[:8], "big") % n


def load_amplitudes(root: Path) -> dict[str, float]:
    vals: dict[str, list[float]] = defaultdict(list)
    seeds: dict[str, set[int]] = defaultdict(set)
    with (root / "stability/stability_floor_A1_per_seed.csv").open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            vals[r["material_id"]].append(float(r["probe_linf"]))
            seeds[r["material_id"]].add(int(r["seed"]))
    out = {}
    for m, x in vals.items():
        if seeds[m] != set(OLD_SEEDS) or len(x) != 5 or len(set(x)) != 1:
            raise RuntimeError(f"legacy amplitude/seed drift for {m}")
        out[m] = x[0]
    return out


def write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({k for r in rows for k in r}) if rows else ["material_id", "status"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def add_material_failures(rows: list[dict[str, Any]], material: str, stage: str, error: str) -> None:
    for solver in SOLVERS:
        rows.append({"material_id": material, "variant": "baseline", "seed": "", "solver": solver, "status": "FAILED", "stage": stage, "error": error})
        for seed in OLD_SEEDS:
            rows.append({"material_id": material, "variant": "noise", "seed": seed, "solver": solver, "status": "FAILED", "stage": stage, "error": error})


def main() -> int:
    a = parse_args()
    if a.shard_count <= 0 or not 0 <= a.shard_index < a.shard_count:
        raise SystemExit("invalid shard parameters")
    root = a.repo_root.resolve(); outdir = a.output_dir.resolve(); outdir.mkdir(parents=True, exist_ok=True)
    mech = root / "mechanism/independent_bader_20260908"
    sys.path.insert(0, str(mech))
    import run_study as study  # type: ignore
    study.BADER = a.henkelman_binary.resolve()
    if not study.BADER.is_file():
        raise RuntimeError(f"Henkelman binary missing: {study.BADER}")

    metadata = load_metadata(root); amps = load_amplitudes(root)
    with a.panel.open(newline="", encoding="utf-8") as f:
        panel = list(csv.DictReader(f))
    if len(panel) != 24 or len({r["material_id"] for r in panel}) != 24:
        raise RuntimeError("P3A panel must contain 24 unique systems")
    selected = [r for r in panel if shard_for(r["material_id"], a.shard_count) == a.shard_index]
    rows: list[dict[str, Any]] = []; failures: list[dict[str, Any]] = []

    for p in selected:
        m = p["material_id"]; meta = metadata.get(m); eps = amps.get(m)
        if meta is None or eps is None:
            add_material_failures(failures, m, "preflight", "missing metadata/amplitude")
            continue
        try:
            blob = fetch_exact(meta["url"], meta["sha256"], int(meta["source_bytes"]))
            with tempfile.TemporaryDirectory(prefix="qoi_p3a_") as td:
                work = Path(td); grid, loader = build_grid(meta, blob, work)
                field = np.ascontiguousarray(np.asarray(grid.total, dtype=np.float64))
                lattice = np.asarray(grid.structure.lattice.matrix, dtype=np.float64)
                frac = np.asarray(grid.structure.frac_coords, dtype=np.float64)
                symbols = [str(x) for x in grid.structure.species]
                if field.size != int(p["npoints"]) or len(symbols) != int(p["natoms"]):
                    raise RuntimeError("panel/source shape or atom-count mismatch")
                refs: dict[str, np.ndarray] = {}
                baseline_log = work / "logs" / "baseline"; baseline_log.mkdir(parents=True, exist_ok=True)
                for solver in SOLVERS:
                    t0 = time.time()
                    try:
                        q, _, extra = study.solve(solver, field, lattice, frac, symbols, work / solver, baseline_log)
                        refs[solver] = np.asarray(q, dtype=float)
                        rows.append({"material_id": m, "system_type": p["system_type"], "floor_band": p["floor_band"], "variant": "baseline", "seed": "", "solver": solver, "status": "SUCCESS", "response_e": 0.0, "epsilon": eps, "measured_Linf": 0.0, "source_sha256": meta["sha256"], "loader": loader, "elapsed_seconds": time.time()-t0, "charges_json": json.dumps(refs[solver].tolist(), separators=(",", ":")), "vacuum_charge_e": extra.get("vacuum_charge_e", "")})
                    except Exception as exc:
                        failures.append({"material_id": m, "variant": "baseline", "seed": "", "solver": solver, "status": "FAILED", "stage": "baseline_solver", "error": f"{type(exc).__name__}: {exc}"})
                for seed in OLD_SEEDS:
                    rng = np.random.default_rng(seed)
                    noise = rng.uniform(-eps, eps, size=field.shape).astype(np.float64, copy=False)
                    recon = field + noise; linf = float(np.max(np.abs(noise))) if noise.size else 0.0
                    noise_log = work / "logs" / f"noise_{seed}"; noise_log.mkdir(parents=True, exist_ok=True)
                    for solver in SOLVERS:
                        if solver not in refs:
                            failures.append({"material_id": m, "variant": "noise", "seed": seed, "solver": solver, "status": "FAILED", "stage": "missing_baseline", "error": "baseline unavailable"}); continue
                        t0 = time.time()
                        try:
                            q, _, extra = study.solve(solver, recon, lattice, frac, symbols, work / solver, noise_log)
                            q = np.asarray(q, dtype=float); response = float(np.max(np.abs(q - refs[solver])))
                            precision = 2e-6 if solver.startswith("henkelman") else 0.0
                            verdicts = {str(t): ("AMBIGUOUS" if precision and abs(response-t) <= precision else "PASS" if response < t else "FAIL") for t in TAUS}
                            rows.append({"material_id": m, "system_type": p["system_type"], "floor_band": p["floor_band"], "variant": "noise", "seed": seed, "solver": solver, "status": "SUCCESS", "response_e": response, "epsilon": eps, "measured_Linf": linf, "source_sha256": meta["sha256"], "loader": loader, "elapsed_seconds": time.time()-t0, "charges_json": json.dumps(q.tolist(), separators=(",", ":")), "threshold_verdicts_json": json.dumps(verdicts, separators=(",", ":")), "vacuum_charge_e": extra.get("vacuum_charge_e", "")})
                        except Exception as exc:
                            failures.append({"material_id": m, "variant": "noise", "seed": seed, "solver": solver, "status": "FAILED", "stage": "perturbed_solver", "error": f"{type(exc).__name__}: {exc}"})
        except Exception as exc:
            add_material_failures(failures, m, "source_or_grid", f"{type(exc).__name__}: {exc}")

    rows.sort(key=lambda r: (r["material_id"], r["solver"], str(r.get("seed", ""))))
    failures.sort(key=lambda r: (r["material_id"], r["solver"], str(r.get("seed", ""))))
    write_rows(outdir / f"outcomes_shard_{a.shard_index:02d}.csv", rows)
    write_rows(outdir / f"failures_shard_{a.shard_index:02d}.csv", failures)
    planned = len(selected) * 18
    accounted = len(rows) + len(failures)
    if accounted != planned:
        raise RuntimeError(f"P3A accounting mismatch: {accounted} != {planned}")
    manifest = {"shard_index": a.shard_index, "shard_count": a.shard_count, "materials": len(selected), "planned_solver_evaluations": planned, "successful_rows": len(rows), "failed_rows": len(failures), "accounted_solver_evaluations": accounted, "panel_sha256": hashlib.sha256(a.panel.read_bytes()).hexdigest(), "henkelman_binary_sha256": hashlib.sha256(study.BADER.read_bytes()).hexdigest()}
    (outdir / f"manifest_shard_{a.shard_index:02d}.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0 if not failures else 2

if __name__ == "__main__":
    raise SystemExit(main())
