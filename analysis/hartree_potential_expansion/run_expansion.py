"""Full Hartree-potential QoI expansion over the frozen development corpus.

Executes the frozen protocol in README.md / LOCAL_RUN_INSTRUCTIONS.md.  It reuses
the *original* codec wrappers that produced `benchmark/master_benchmark_full.csv`
(RhoCodec `scripts/honest_benchmark.py`: `encode_zfp`, `encode_sz3`, `encode_sperr`,
which call zfpy fixed-accuracy, `rhocodec.sz3.compress` = pysz ABS INTERP_LORENZO,
and hdf5plugin Sperr absolute single-chunk) and the exact `.npz` grids the frozen
benchmark consumed (`data/mp/grids`, `data/slabs/grids`).  The bulk `.npz` grids
were verified bit-identical to `analysis/mp_chgcar_loader.py` output on the pilot.

Every frozen master-table row of every material is regenerated: same
`nominal_tolerance_absolute`, same codec, same wrapper.  The row inherits the frozen
Bader columns only through the exact key
`(material_id, codec, nominal_tolerance_relative, nominal_tolerance_absolute, ladder)`.
Gate (frozen): 0.95 <= reproduced/frozen realized_Linf <= 1.05 AND reproduced
compressed bytes == frozen compressed bytes.  Failures are recorded, never dropped.

Hartree potential: V(G) = 4*pi*rho(G)/|G|^2 for G != 0, V(G=0) = 0, same code as
the pilot.  potential_rel_RMSE = RMS(V_recon - V_orig) / RMS(V_orig).

Usage (from the QoI repo root, with the CatalystForge interpreter):
  python analysis/hartree_potential_expansion/run_expansion.py --rhocodec D:/Research/RhoCodec --workers 8
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import platform
import sys
import time
import traceback
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "analysis" / "hartree_potential_expansion"
GATE = (0.95, 1.05)
KEY = ["material_id", "codec", "nominal_tolerance_relative", "nominal_tolerance_absolute", "ladder"]
CODEC_FN = {"ZFP": "encode_zfp", "SZ3": "encode_sz3", "SPERR": "encode_sperr"}
CORPUS_DIR = {"bulk": "data/mp/grids", "slab": "data/slabs/grids"}

_hb = None  # honest_benchmark module, imported lazily per worker


def _import_wrappers(rhocodec: str):
    global _hb
    if _hb is None:
        logging.disable(logging.CRITICAL)
        warnings.filterwarnings("ignore")
        sys.path.insert(0, str(Path(rhocodec) / "scripts"))
        sys.path.insert(0, str(Path(rhocodec) / "src"))
        import honest_benchmark as hb  # noqa: WPS433
        _hb = hb
    return _hb


def reciprocal_g2(shape, lattice):
    nx, ny, nz = shape
    B = 2.0 * np.pi * np.linalg.inv(lattice).T
    n1 = np.fft.fftfreq(nx) * nx
    n2 = np.fft.fftfreq(ny) * ny
    n3 = np.fft.rfftfreq(nz) * nz
    N1, N2, N3 = np.meshgrid(n1, n2, n3, indexing="ij")
    G = (N1[..., None] * B[0] + N2[..., None] * B[1] + N3[..., None] * B[2])
    return np.einsum("...k,...k->...", G, G)


def hartree_potential(field, g2):
    F = np.fft.rfftn(field)
    V = np.zeros_like(F)
    mask = g2 > 0
    V[mask] = 4.0 * np.pi * F[mask] / g2[mask]
    return np.fft.irfftn(V, s=field.shape)


def run_material(args):
    mid, system_type, npz_path, frozen_rows, rhocodec = args
    hb = _import_wrappers(rhocodec)
    t0 = time.time()
    out_rows, failures = [], []
    try:
        blob = Path(npz_path).read_bytes()
        npz_sha = hashlib.sha256(blob).hexdigest()
        with np.load(npz_path, allow_pickle=False) as z:
            lattice = np.asarray(z["lattice"], dtype=np.float64)
            grid = np.ascontiguousarray(z["grid"], dtype=np.float64)
    except Exception as exc:  # infrastructure failure
        failures.append({"material_id": mid, "system_type": system_type, "codec": "", "stage": "load",
                         "failure_class": "infrastructure", "detail": f"{type(exc).__name__}: {exc}"[:300]})
        return mid, out_rows, failures, {"seconds": time.time() - t0}
    ptp = float(np.ptp(grid))
    g2 = reciprocal_g2(grid.shape, lattice)
    v0 = hartree_potential(grid, g2)
    v0_rms = float(np.sqrt(np.mean(v0 ** 2)))
    del v0
    for r in frozen_rows:
        codec = r["codec"]
        fn = getattr(hb, CODEC_FN[codec], None)
        base = {"material_id": mid, "formula": r["formula"], "system_type": system_type, "corpus": r["corpus"],
                "codec": codec, "codec_config_frozen": r["codec_config"], "ladder": r["ladder"],
                "nominal_tolerance_relative": r["nominal_tolerance_relative"],
                "nominal_tolerance_absolute": r["nominal_tolerance_absolute"],
                "npoints": int(grid.size), "npoints_frozen": r["npoints"], "natoms": r["natoms"],
                "value_ptp": ptp, "value_ptp_frozen": r["value_ptp"],
                "stability_floor_A1_e": r["stability_floor_A1_e"], "npz_sha256": npz_sha,
                "frozen_realized_Linf": r["realized_Linf"], "frozen_compressed_bytes": int(r["compressed_bytes"]),
                "compression_ratio_frozen": r["compression_ratio"],
                "Bader_error_resolved_e": r["Bader_error_resolved_e"], "Bader_error_fixed_e": r["Bader_error_fixed_e"],
                "frac_voxels_reassigned": r["frac_voxels_reassigned"], "n_voxels_reassigned": r["n_voxels_reassigned"],
                "electron_count_abs_dev_frozen": r["electron_count_abs_dev"], "rmse_density_frozen": r["rmse"]}
        if fn is None:
            failures.append({**{k: base[k] for k in ("material_id", "system_type", "codec")}, "stage": "wrapper",
                             "failure_class": "infrastructure", "detail": f"wrapper {CODEC_FN[codec]} unavailable"})
            continue
        eb = float(r["nominal_tolerance_absolute"])
        try:
            t1 = time.time()
            nbytes, recon, cfg = fn(grid, eb)
            t_enc = time.time() - t1
            recon = np.asarray(recon, dtype=np.float64).reshape(grid.shape)
        except Exception as exc:
            failures.append({**{k: base[k] for k in ("material_id", "system_type", "codec")},
                             "nominal_tolerance_relative": r["nominal_tolerance_relative"], "stage": "codec",
                             "failure_class": "numerical", "detail": f"{type(exc).__name__}: {exc}"[:300]})
            continue
        err = recon - grid
        finite = bool(np.all(np.isfinite(recon)))
        linf = float(np.abs(err).max()) if finite else float("nan")
        ratio = linf / float(r["realized_Linf"]) if finite else float("nan")
        bytes_equal = int(nbytes) == int(r["compressed_bytes"])
        gate_linf = bool(finite and GATE[0] <= ratio <= GATE[1])
        gate = bool(gate_linf and bytes_equal)
        if finite:
            dv = hartree_potential(err, g2)
            v_rmse = float(np.sqrt(np.mean(dv ** 2))) / v0_rms
            v_linf = float(np.abs(dv).max()) / v0_rms
            del dv
        else:
            v_rmse = v_linf = float("nan")
            failures.append({**{k: base[k] for k in ("material_id", "system_type", "codec")},
                             "nominal_tolerance_relative": r["nominal_tolerance_relative"], "stage": "codec",
                             "failure_class": "numerical", "detail": "non-finite reconstruction"})
        if not gate:
            failures.append({**{k: base[k] for k in ("material_id", "system_type", "codec")},
                             "nominal_tolerance_relative": r["nominal_tolerance_relative"], "stage": "gate",
                             "failure_class": "reproduction_mismatch",
                             "detail": f"Linf ratio {ratio:.6g}; bytes {nbytes} vs frozen {int(r['compressed_bytes'])}"})
        out_rows.append({**base, "codec_config_reproduced": cfg,
                         "reproduced_realized_Linf": linf, "Linf_reproduction_ratio": ratio,
                         "reproduced_compressed_bytes": int(nbytes), "compressed_bytes_equal": bytes_equal,
                         "gate_linf_pass": gate_linf, "reproduction_gate_pass": gate,
                         "realized_Linf": linf, "realized_Linf_over_ptp": linf / ptp if finite else float("nan"),
                         "rmse_density": float(np.sqrt(np.mean(err ** 2))) if finite else float("nan"),
                         "electron_count_abs_dev": float(abs(recon.mean() - grid.mean())) if finite else float("nan"),
                         "compression_ratio_reproduced": grid.nbytes / int(nbytes),
                         "compression_ratio": grid.nbytes / int(nbytes),
                         "V_orig_rms": v0_rms, "potential_rel_RMSE": v_rmse, "potential_rel_Linf": v_linf,
                         "encode_seconds": round(t_enc, 3)})
    return mid, out_rows, failures, {"seconds": time.time() - t0, "npoints": int(grid.size)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rhocodec", default="D:/Research/RhoCodec")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=None, help="debug: first N materials")
    ap.add_argument("--materials", default=None, help="debug: comma-separated material ids")
    args = ap.parse_args()
    rc = Path(args.rhocodec)

    bench = pd.read_csv(REPO / "benchmark" / "master_benchmark_full.csv", low_memory=False)
    assert not bench.duplicated(KEY).any(), "frozen key not unique"
    bench_sha = hashlib.sha256((REPO / "benchmark" / "master_benchmark_full.csv").read_bytes()).hexdigest()
    mats = bench[["material_id", "system_type", "npoints"]].drop_duplicates("material_id").sort_values("npoints")
    if args.materials:
        mats = mats[mats.material_id.isin(args.materials.split(","))]
    if args.limit:
        mats = mats.head(args.limit)

    tasks, missing = [], []
    for _, m in mats.iterrows():
        p = rc / CORPUS_DIR[m.system_type] / f"{m.material_id}.npz"
        if not p.exists():
            missing.append({"material_id": m.material_id, "system_type": m.system_type, "codec": "", "stage": "load",
                            "failure_class": "infrastructure", "detail": f"missing {p}"})
            continue
        fr = bench[bench.material_id == m.material_id].to_dict("records")
        tasks.append((m.material_id, m.system_type, str(p), fr, str(rc)))
    print(f"{len(tasks)} materials, {sum(len(t[3]) for t in tasks)} frozen rows, {len(missing)} missing", flush=True)

    rows, failures, timing = [], list(missing), {}
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(run_material, t): t[0] for t in tasks}
        done = 0
        for f in as_completed(futs):
            mid = futs[f]
            try:
                mid, r, fl, tm = f.result()
            except Exception:
                failures.append({"material_id": mid, "stage": "worker", "failure_class": "infrastructure",
                                 "detail": traceback.format_exc()[-300:]})
                r, fl, tm = [], [], {}
            rows += r; failures += fl; timing[mid] = tm; done += 1
            ng = sum(x["reproduction_gate_pass"] for x in r)
            print(f"[{done}/{len(tasks)}] {mid:22s} rows {len(r):3d} gate {ng:3d} fail {len(fl):2d} {tm.get('seconds', 0):7.1f}s", flush=True)
            if done % 10 == 0:
                pd.DataFrame(rows).to_csv(OUT / "rows.partial.csv", index=False)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "rows.csv", index=False)
    pd.DataFrame(failures).to_csv(OUT / "failures.csv", index=False)
    if (OUT / "rows.partial.csv").exists():
        (OUT / "rows.partial.csv").unlink()

    hb = _import_wrappers(str(rc))
    import zfpy, h5py, hdf5plugin, pysz  # noqa
    def ver(mod):
        try:
            from importlib.metadata import version
            return version(mod)
        except Exception:
            return "unknown"
    prov = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__,
                        "zfpy": ver("zfpy"), "pysz": ver("pysz"), "h5py": h5py.__version__,
                        "hdf5plugin": hdf5plugin.version, "platform": platform.platform(),
                        "interpreter": sys.executable},
        "codec_wrappers": {"module": str(Path(hb.__file__)), "ZFP": "honest_benchmark.encode_zfp (zfpy fixed-accuracy)",
                           "SZ3": "honest_benchmark.encode_sz3 -> rhocodec.sz3.compress (pysz ABS INTERP_LORENZO)",
                           "SPERR": "honest_benchmark.encode_sperr (hdf5plugin Sperr absolute, single chunk)"},
        "density_source": {"bulk": str(rc / CORPUS_DIR["bulk"]), "slab": str(rc / CORPUS_DIR["slab"]),
                           "note": "exact .npz grids consumed by the frozen benchmark; per-row npz_sha256 in rows.csv; "
                                   "source-file SHA-256 per material in materials_metadata.csv / RhoCodec provenance.jsonl",
                           "loader_for_public_files": "analysis/mp_chgcar_loader.py (bit-identical to npz on pilot)"},
        "frozen_benchmark": {"path": "benchmark/master_benchmark_full.csv", "sha256": bench_sha,
                             "row_key": KEY},
        "gate": {"realized_Linf_ratio": list(GATE), "compressed_bytes_equal": True},
        "counts": {"materials_attempted": len(tasks), "materials_missing_npz": len(missing),
                   "frozen_rows_targeted": int(sum(len(t[3]) for t in tasks)), "rows_regenerated": len(df),
                   "rows_gate_pass": int(df.reproduction_gate_pass.sum()) if len(df) else 0,
                   "failure_records": len(failures),
                   "gate_pass_by_codec": df.groupby("codec").reproduction_gate_pass.mean().to_dict() if len(df) else {},
                   "gate_pass_by_system_type": df.groupby("system_type").reproduction_gate_pass.mean().to_dict() if len(df) else {}},
        "timing_seconds_by_material": {k: v.get("seconds") for k, v in timing.items()},
    }
    (OUT / "provenance.json").write_text(json.dumps(prov, indent=2))
    print(json.dumps(prov["counts"], indent=2))


if __name__ == "__main__":
    main()
