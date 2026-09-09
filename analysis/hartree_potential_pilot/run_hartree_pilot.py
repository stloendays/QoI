"""Hartree-potential QoI pilot (ZFP, 12 small bulk materials).

Independent extension of the frozen benchmark.  Reads the frozen master table
(never writes it), regenerates the ZFP reconstructions from the public source
densities with the benchmark's own loader, and compares the periodic electronic
Hartree potential of each reconstruction with that of the original field.

Hartree potential (gauge-fixed, G=0 -> 0):
    V(G) = 4*pi*rho(G)/|G|^2  for G != 0.
Primary metric: potential_rel_RMSE = RMS(V_recon - V_orig) / RMS(V_orig).
Bader errors are NOT recomputed; they are taken from the frozen master table for
the same (material, codec, tolerance) row, which is legitimate only when the
regenerated reconstruction reproduces the frozen realized_Linf within 5 %.

Usage:
  python analysis/hartree_potential_pilot/run_hartree_pilot.py \
      --cache <dir with <material_id>.json.gz> [--npz-dir <frozen npz grids>]
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import zfpy

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "analysis"))
from mp_chgcar_loader import load_mp_density, parse_ngrid  # noqa: E402

OUT = REPO / "analysis" / "hartree_potential_pilot"
GATE = (0.95, 1.05)
N_MATERIALS = 12
MIN_ROWS = 5


def reciprocal_g2(shape, lattice):
    """|G|^2 on the rfftn grid for a periodic cell with row-vector lattice."""
    nx, ny, nz = shape
    B = 2.0 * np.pi * np.linalg.inv(lattice).T  # rows b_i, a_i . b_j = 2 pi delta_ij
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


def loglog_fit(x, y):
    x = np.log10(np.asarray(x, float)); y = np.log10(np.asarray(y, float))
    m = np.isfinite(x) & np.isfinite(y)
    if m.sum() < 3:
        return np.nan, np.nan
    p = np.polyfit(x[m], y[m], 1)
    yhat = np.polyval(p, x[m]); ss = ((y[m] - y[m].mean()) ** 2).sum()
    r2 = 1 - ((y[m] - yhat) ** 2).sum() / ss if ss > 0 else np.nan
    return float(p[0]), float(r2)


def corr_log(a, b, method):
    a = np.asarray(a, float); b = np.asarray(b, float)
    m = np.isfinite(a) & np.isfinite(b) & (a > 0) & (b > 0)
    if m.sum() < 3:
        return np.nan
    return float(pd.Series(np.log10(a[m])).corr(pd.Series(np.log10(b[m])), method=method))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True)
    ap.add_argument("--npz-dir", default=None)
    args = ap.parse_args()
    cache = Path(args.cache)

    bench = pd.read_csv(REPO / "benchmark" / "master_benchmark_full.csv", low_memory=False)
    meta = pd.read_csv(REPO / "materials_metadata.csv").set_index("material_id")
    z = bench[(bench.codec == "ZFP") & (bench.system_type == "bulk")].copy()
    z = z[np.isfinite(z.nominal_tolerance_absolute) & np.isfinite(z.Bader_error_resolved_e)]
    counts = z.groupby("material_id").size()
    order = z.groupby("material_id").npoints.first().sort_values().index
    mids = [m for m in order if counts[m] >= MIN_ROWS][:N_MATERIALS]

    provenance = {"materials": {}, "environment": {
        "python": platform.python_version(), "numpy": np.__version__,
        "zfpy": getattr(zfpy, "__version__", "1.0.1 (pip)"), "pandas": pd.__version__},
        "loader": "analysis/mp_chgcar_loader.py (verbatim RhoCodec scripts/fetch_mp_corpus.py::parse_chgcar_json)",
        "frozen_table": "benchmark/master_benchmark_full.csv (read only)",
        "gate": {"reproduced_over_frozen_realized_Linf": list(GATE)}}
    rows = []
    for mid in mids:
        mrow = meta.loc[mid]
        rec = load_mp_density(cache / f"{mid}.json.gz", expected_sha256=str(mrow.sha256),
                              expected_ngrid=parse_ngrid(mrow.ngrid), expected_npoints=int(mrow.npoints),
                              expected_natoms=int(mrow.natoms))
        rho = np.ascontiguousarray(rec["grid"], dtype=np.float64)
        prov = {"sha256_verified": True, "ngrid": list(rho.shape), "npoints": int(rho.size),
                "natoms": len(rec["symbols"]), "envelope": rec["envelope"],
                "mean_electrons_per_cell": float(rho.mean())}
        if args.npz_dir:
            p = Path(args.npz_dir) / f"{mid}.npz"
            if p.exists():
                with np.load(p, allow_pickle=False) as zz:
                    prov["bit_identical_to_frozen_npz_grid"] = bool(np.array_equal(zz["grid"], rho))
                    prov["lattice_allclose_frozen_npz"] = bool(np.allclose(zz["lattice"], rec["lattice"]))
        ptp_frozen = float(z[z.material_id == mid].value_ptp.iloc[0])
        prov["value_ptp_matches_frozen"] = bool(abs(np.ptp(rho) - ptp_frozen) <= 1e-9 * max(1.0, ptp_frozen))
        provenance["materials"][mid] = prov

        g2 = reciprocal_g2(rho.shape, rec["lattice"])
        v0 = hartree_potential(rho, g2)
        v0_rms = float(np.sqrt(np.mean(v0 ** 2)))
        v0_ptp = float(np.ptp(v0))

        sub = z[z.material_id == mid].sort_values("realized_Linf").reset_index(drop=True)
        pilot_idx = sorted({0, len(sub) // 2, len(sub) - 1})
        roles = {pilot_idx[0]: "tight", pilot_idx[len(pilot_idx) // 2]: "middle", pilot_idx[-1]: "loose"}
        for i, r in sub.iterrows():
            tol = float(r.nominal_tolerance_absolute)
            blob = zfpy.compress_numpy(rho, tolerance=tol)
            recon = zfpy.decompress_numpy(blob)
            err = recon - rho
            linf = float(np.abs(err).max())
            dv = hartree_potential(err, g2)
            ratio = linf / float(r.realized_Linf)
            rows.append({
                "material_id": mid, "formula": r.formula, "npoints": int(r.npoints), "natoms": int(r.natoms),
                "stability_floor_A1_e": float(r.stability_floor_A1_e),
                "ladder": r.ladder, "pilot_role": roles.get(i, ""), "is_pilot_row": i in roles,
                "nominal_tolerance_relative": float(r.nominal_tolerance_relative),
                "nominal_tolerance_absolute": tol,
                "frozen_realized_Linf": float(r.realized_Linf), "reproduced_realized_Linf": linf,
                "Linf_reproduction_ratio": ratio,
                "reproduction_gate_pass": GATE[0] <= ratio <= GATE[1],
                "realized_Linf": linf, "realized_Linf_over_ptp": linf / float(np.ptp(rho)),
                "rmse_density": float(np.sqrt(np.mean(err ** 2))),
                "frozen_compressed_bytes": int(r.compressed_bytes), "reproduced_compressed_bytes": len(blob),
                "compression_ratio_frozen": float(r.compression_ratio),
                "compression_ratio_reproduced": rho.nbytes / len(blob),
                "Bader_error_resolved_e": float(r.Bader_error_resolved_e),
                "Bader_error_fixed_e": float(r.Bader_error_fixed_e),
                "frac_voxels_reassigned": float(r.frac_voxels_reassigned),
                "electron_count_abs_dev": float(abs(recon.mean() - rho.mean())),
                "V_orig_rms": v0_rms, "V_orig_ptp": v0_ptp,
                "potential_rel_RMSE": float(np.sqrt(np.mean(dv ** 2))) / v0_rms,
                "potential_rel_Linf": float(np.abs(dv).max()) / v0_rms,
                "potential_rel_Linf_over_Vptp": float(np.abs(dv).max()) / v0_ptp,
            })
            print(f"{mid:11s} rel {r.nominal_tolerance_relative:<8g} Linf ratio {ratio:.4f} "
                  f"Vrel {rows[-1]['potential_rel_RMSE']:.3e} Bader {r.Bader_error_resolved_e:.3e}", flush=True)

    full = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    full.to_csv(OUT / "full_ladder_rows.csv", index=False)
    pilot = full[full.is_pilot_row].copy()
    pilot.to_csv(OUT / "pilot_rows.csv", index=False)
    (OUT / "provenance.json").write_text(json.dumps(provenance, indent=2))

    def block(df, label):
        v = df[df.reproduction_gate_pass]
        return {
            "population": label, "n_rows": len(df), "n_gate_pass": int(df.reproduction_gate_pass.sum()),
            "gate_pass_fraction": float(df.reproduction_gate_pass.mean()),
            "median_Linf_reproduction_ratio": float(df.Linf_reproduction_ratio.median()),
            "min_Linf_reproduction_ratio": float(df.Linf_reproduction_ratio.min()),
            "max_Linf_reproduction_ratio": float(df.Linf_reproduction_ratio.max()),
            "median_potential_rel_RMSE": float(v.potential_rel_RMSE.median()),
            "p95_potential_rel_RMSE": float(v.potential_rel_RMSE.quantile(.95)),
            "median_potential_rel_Linf": float(v.potential_rel_Linf.median()),
            "median_Bader_error_resolved_e": float(v.Bader_error_resolved_e.median()),
            "pearson_log_Verr_vs_log_Linf": corr_log(v.potential_rel_RMSE, v.realized_Linf, "pearson"),
            "spearman_log_Verr_vs_log_Linf": corr_log(v.potential_rel_RMSE, v.realized_Linf, "spearman"),
            "pearson_log_Bader_vs_log_Linf": corr_log(v.Bader_error_resolved_e, v.realized_Linf, "pearson"),
            "spearman_log_Bader_vs_log_Linf": corr_log(v.Bader_error_resolved_e, v.realized_Linf, "spearman"),
            "pearson_log_Verr_vs_log_Bader": corr_log(v.potential_rel_RMSE, v.Bader_error_resolved_e, "pearson"),
            "spearman_log_Verr_vs_log_Bader": corr_log(v.potential_rel_RMSE, v.Bader_error_resolved_e, "spearman"),
            "pooled_loglog_slope_Verr_vs_Linf": loglog_fit(v.realized_Linf, v.potential_rel_RMSE)[0],
            "pooled_loglog_R2_Verr_vs_Linf": loglog_fit(v.realized_Linf, v.potential_rel_RMSE)[1],
            "pooled_loglog_slope_Bader_vs_Linf": loglog_fit(v.realized_Linf, v.Bader_error_resolved_e)[0],
            "pooled_loglog_R2_Bader_vs_Linf": loglog_fit(v.realized_Linf, v.Bader_error_resolved_e)[1],
        }
    summary = pd.DataFrame([block(pilot, "pilot_3_rows_per_material"), block(full, "full_frozen_ZFP_ladder")])
    summary.to_csv(OUT / "summary.csv", index=False)

    mono = []
    for mid, g in full[full.reproduction_gate_pass].groupby("material_id"):
        g = g.sort_values("realized_Linf")
        x = g.realized_Linf.to_numpy(); v = g.potential_rel_RMSE.to_numpy(); b = g.Bader_error_resolved_e.to_numpy()
        dv = np.diff(v); db = np.diff(b); dx = np.diff(np.log10(x))
        with np.errstate(divide="ignore", invalid="ignore"):
            el_v = np.diff(np.log10(v)) / dx
            el_b = np.diff(np.log10(np.maximum(b, 1e-12))) / dx
        sv, r2v = loglog_fit(x, v); sb, r2b = loglog_fit(x, np.maximum(b, 1e-12))
        mono.append({
            "material_id": mid, "formula": g.formula.iloc[0], "n_gate_pass_rows": len(g),
            "stability_floor_A1_e": float(g.stability_floor_A1_e.iloc[0]),
            "Linf_span_decades": float(np.log10(x.max() / x.min())),
            "potential_monotone_nondecreasing": bool(np.all(dv >= 0)),
            "potential_n_decreases": int((dv < 0).sum()),
            "potential_loglog_slope": sv, "potential_loglog_R2": r2v,
            "potential_local_elasticity_min": float(np.nanmin(el_v)) if len(el_v) else np.nan,
            "potential_local_elasticity_max": float(np.nanmax(el_v)) if len(el_v) else np.nan,
            "potential_dynamic_range": float(v.max() / v.min()),
            "bader_monotone_nondecreasing": bool(np.all(db >= 0)),
            "bader_n_decreases": int((db < 0).sum()),
            "bader_loglog_slope": sb, "bader_loglog_R2": r2b,
            "bader_local_elasticity_min": float(np.nanmin(el_b)) if len(el_b) else np.nan,
            "bader_local_elasticity_max": float(np.nanmax(el_b)) if len(el_b) else np.nan,
            "bader_max_consecutive_jump_ratio": float(np.max(b[1:] / np.maximum(b[:-1], 1e-12))) if len(b) > 1 else np.nan,
            "bader_dynamic_range": float(b.max() / max(b.min(), 1e-12)),
            "bader_min_e": float(b.min()), "bader_max_e": float(b.max()),
        })
    mono = pd.DataFrame(mono)
    mono.to_csv(OUT / "monotonicity.csv", index=False)
    print(summary.T.to_string()); print(mono.to_string())


if __name__ == "__main__":
    main()
