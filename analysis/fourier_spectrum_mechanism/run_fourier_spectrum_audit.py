#!/usr/bin/env python3
"""Fourier-spectrum mechanism audit for matched-realized-Linf codec errors.

Research extension only. The frozen manuscript and frozen benchmark tables are
read-only. Scientific outputs are written to --output and are intended to be
encrypted by the GitHub Actions handoff workflow before artifact upload.

Core identity checked here:
    V_err(G) = 4*pi*Delta rho(G) / |G|^2
so, with NumPy's unnormalised forward FFT,
    RMS(Delta V_H)^2 = (4*pi)^2 / N^2 *
        sum_{G != 0} |Delta rho(G)|^2 / |G|^4.

The audit therefore separates pointwise amplitude from reciprocal-space error
geometry and tests whether the matched-Linf codec effect is carried by the
low-G / Hartree-weighted part of the reconstruction error spectrum.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import tempfile
from pathlib import Path

import h5py
import hdf5plugin
import numpy as np
import pandas as pd
import zfpy
from pysz import sz, szConfig, szErrorBoundMode

REPO = Path(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(REPO / "analysis"))
from mp_chgcar_loader import load_mp_density, parse_ngrid  # noqa: E402
from hartree_potential_pilot.run_hartree_pilot import reciprocal_g2, hartree_potential  # noqa: E402

CODECS = ("ZFP", "SZ3", "SPERR")
CALIPER_DEX = 0.10
LOW_Q = 0.25
HIGH_Q = 0.75
TARGET_HARTREE_RATIO = 0.078
TARGET_RATIO_REL_TOL = 0.50  # mechanism audit, not a refit to the target
REPRO_RATIO_GATE = (0.85, 1.15)
MIN_TRIPLES = 12


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def compress_reconstruct(codec: str, rho: np.ndarray, tol: float) -> np.ndarray:
    rho = np.ascontiguousarray(rho, dtype=np.float64)
    if codec == "ZFP":
        blob = zfpy.compress_numpy(rho, tolerance=float(tol))
        return np.ascontiguousarray(zfpy.decompress_numpy(blob), dtype=np.float64)

    if codec == "SZ3":
        cfg = szConfig()
        cfg.errorBoundMode = szErrorBoundMode.ABS
        cfg.absErrorBound = float(tol)
        compressed, _ = sz.compress(rho, cfg)
        recon, _ = sz.decompress(compressed, np.float64, rho.shape)
        return np.ascontiguousarray(recon, dtype=np.float64)

    if codec == "SPERR":
        # Frozen benchmark configuration: absolute mode, one HDF5 chunk.
        fd, name = tempfile.mkstemp(suffix=".h5")
        os.close(fd)
        try:
            with h5py.File(name, "w") as f:
                f.create_dataset(
                    "rho",
                    data=rho,
                    chunks=rho.shape,
                    **hdf5plugin.Sperr(absolute=float(tol)),
                )
            with h5py.File(name, "r") as f:
                recon = np.asarray(f["rho"][...], dtype=np.float64)
            return np.ascontiguousarray(recon)
        finally:
            try:
                os.remove(name)
            except FileNotFoundError:
                pass

    raise ValueError(codec)


def rfft_multiplicity(shape: tuple[int, int, int]) -> np.ndarray:
    nz = shape[2]
    nr = nz // 2 + 1
    w1 = np.full(nr, 2.0, dtype=np.float64)
    w1[0] = 1.0
    if nz % 2 == 0:
        w1[-1] = 1.0
    return w1.reshape(1, 1, nr)


def spectrum_metrics(err: np.ndarray, g2: np.ndarray) -> dict[str, float]:
    F = np.fft.rfftn(err)
    E = np.abs(F) ** 2
    w = rfft_multiplicity(err.shape)
    G = np.sqrt(g2)
    gmax = float(G.max())
    if not np.isfinite(gmax) or gmax <= 0:
        raise RuntimeError("invalid reciprocal grid")
    q = G / gmax

    Ew = E * w
    total = float(Ew.sum())
    if not np.isfinite(total) or total <= 0:
        raise RuntimeError("zero/non-finite spectral error energy")

    mask = g2 > 0
    nonzero_total = float(Ew[mask].sum())
    if nonzero_total <= 0:
        raise RuntimeError("zero nonzero-G spectral energy")
    low_mask = mask & (q <= LOW_Q)
    high_mask = mask & (q >= HIGH_Q)
    low = float(Ew[low_mask].sum())
    high = float(Ew[high_mask].sum())
    centroid = float((Ew[mask] * q[mask]).sum() / nonzero_total)
    g0_energy = float(Ew[~mask].sum())

    hw = float((Ew[mask] / (g2[mask] ** 2)).sum())
    hw_low = float((Ew[low_mask] / (g2[low_mask] ** 2)).sum())
    return {
        "error_energy": total,
        "nonzero_G_error_energy": nonzero_total,
        "G0_error_energy": g0_energy,
        "G0_error_fraction_total": g0_energy / total,
        "low_G_error_energy": low,
        "high_G_error_energy": high,
        "low_G_fraction": low / nonzero_total,
        "high_G_fraction": high / nonzero_total,
        "spectral_centroid_qmax": centroid,
        "hartree_weighted_error": hw,
        "hartree_weighted_low_G_fraction": hw_low / hw if hw > 0 else np.nan,
        "spectral_hartree_susceptibility": hw / total,
    }


def greedy_triples(sub: pd.DataFrame) -> list[dict]:
    groups = {
        c: sub[sub["codec"].str.upper() == c].sort_values("realized_Linf").copy()
        for c in CODECS
    }
    if any(g.empty for g in groups.values()):
        return []

    # Build all admissible three-way tuples and require the FULL tuple span
    # max(log10 Linf)-min(log10 Linf) <= CALIPER_DEX. Greedily accept the
    # smallest-span unused tuple, which prevents SZ3 and SPERR from being
    # farther apart than the stated common-support caliper.
    candidates = []
    for iz, rz in groups["ZFP"].iterrows():
        lz = math.log10(float(rz.realized_Linf))
        for isz, rsz in groups["SZ3"].iterrows():
            lsz = math.log10(float(rsz.realized_Linf))
            for isp, rsp in groups["SPERR"].iterrows():
                lsp = math.log10(float(rsp.realized_Linf))
                logs = (lz, lsz, lsp)
                span = max(logs) - min(logs)
                if span <= CALIPER_DEX + 1e-15:
                    center = abs(lz - (lsz + lsp) / 2.0)
                    candidates.append((span, center, int(iz), int(isz), int(isp), rz, rsz, rsp))

    candidates.sort(key=lambda x: x[:5])
    used = {c: set() for c in CODECS}
    triples = []
    for span, _, iz, isz, isp, rz, rsz, rsp in candidates:
        if iz in used["ZFP"] or isz in used["SZ3"] or isp in used["SPERR"]:
            continue
        used["ZFP"].add(iz)
        used["SZ3"].add(isz)
        used["SPERR"].add(isp)
        triples.append({
            "ZFP": rz,
            "SZ3": rsz,
            "SPERR": rsp,
            "max_pairwise_distance_dex": float(span),
        })
    return triples


def pair_summary(df: pd.DataFrame, a: str, b: str) -> dict:
    p = df[(df.codec == a)].merge(
        df[df.codec == b],
        on=["material_id", "triple_id"],
        suffixes=("_A", "_B"),
        validate="one_to_one",
    )
    if p.empty:
        return {"pair": f"{a}/{b}", "n": 0}

    def ratio(col):
        x = p[f"{col}_A"].to_numpy(float)
        y = p[f"{col}_B"].to_numpy(float)
        m = np.isfinite(x) & np.isfinite(y) & (y > 0)
        return x[m] / y[m]

    hartree = ratio("hartree_rel_RMSE")
    weighted = np.sqrt(ratio("hartree_weighted_error"))
    total = np.sqrt(ratio("error_energy"))
    susceptibility = np.sqrt(ratio("spectral_hartree_susceptibility"))
    lowfrac = ratio("low_G_fraction")
    centroid_delta = (
        p["spectral_centroid_qmax_A"].to_numpy(float)
        - p["spectral_centroid_qmax_B"].to_numpy(float)
    )
    return {
        "pair": f"{a}/{b}",
        "n": int(len(p)),
        "median_hartree_RMSE_ratio": float(np.median(hartree)),
        "median_sqrt_hartree_weighted_ratio": float(np.median(weighted)),
        "median_sqrt_total_error_energy_ratio": float(np.median(total)),
        "median_sqrt_spectral_susceptibility_ratio": float(np.median(susceptibility)),
        "median_low_G_fraction_ratio": float(np.median(lowfrac)),
        "median_centroid_delta_qmax": float(np.median(centroid_delta)),
        "max_abs_parseval_relative_error": float(
            np.nanmax(
                np.r_[
                    p["parseval_relative_error_A"].to_numpy(float),
                    p["parseval_relative_error_B"].to_numpy(float),
                ]
            )
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)

    bench_path = REPO / "benchmark" / "master_benchmark_full.csv"
    meta_path = REPO / "materials_metadata.csv"
    cohort_path = REPO / "analysis" / "hartree_potential_pilot" / "full_ladder_rows.csv"

    bench = pd.read_csv(bench_path, low_memory=False)
    meta = pd.read_csv(meta_path).set_index("material_id")
    cohort = pd.read_csv(cohort_path)
    mids = list(dict.fromkeys(cohort.material_id.astype(str).tolist()))
    if len(mids) != 12:
        raise RuntimeError("frozen Hartree cohort drift")

    b = bench[bench.material_id.astype(str).isin(mids)].copy()
    b["codec"] = b["codec"].astype(str).str.upper()
    b = b[
        b.codec.isin(CODECS)
        & np.isfinite(pd.to_numeric(b.realized_Linf, errors="coerce"))
        & (pd.to_numeric(b.realized_Linf, errors="coerce") > 0)
        & np.isfinite(pd.to_numeric(b.nominal_tolerance_absolute, errors="coerce"))
    ].copy()

    selected = []
    triple_counter = 0
    for mid in mids:
        triples = greedy_triples(b[b.material_id.astype(str) == mid])
        for t in triples:
            triple_counter += 1
            for codec in CODECS:
                r = t[codec]
                selected.append({
                    "material_id": mid,
                    "triple_id": triple_counter,
                    "codec": codec,
                    "frozen_realized_Linf": float(r.realized_Linf),
                    "nominal_tolerance_absolute": float(r.nominal_tolerance_absolute),
                    "max_pairwise_distance_dex": float(t["max_pairwise_distance_dex"]),
                    "formula": str(r.formula),
                })
    sel = pd.DataFrame(selected)
    if sel.empty or sel.triple_id.nunique() < MIN_TRIPLES:
        raise RuntimeError("insufficient three-codec matched support")

    sel.to_csv(out / "matched_triples_protocol.csv", index=False)

    rows = []
    for mid, gmat in sel.groupby("material_id", sort=False):
        m = meta.loc[mid]
        rec = load_mp_density(
            args.cache / f"{mid}.json.gz",
            expected_sha256=str(m.sha256),
            expected_ngrid=parse_ngrid(m.ngrid),
            expected_npoints=int(m.npoints),
            expected_natoms=int(m.natoms),
        )
        rho = np.ascontiguousarray(rec["grid"], dtype=np.float64)
        g2 = reciprocal_g2(rho.shape, rec["lattice"])
        v0 = hartree_potential(rho, g2)
        v0_rms = float(np.sqrt(np.mean(v0 * v0)))
        if not np.isfinite(v0_rms) or v0_rms <= 0:
            raise RuntimeError("invalid Hartree reference")

        for _, s in gmat.iterrows():
            codec = str(s.codec)
            recon = compress_reconstruct(codec, rho, float(s.nominal_tolerance_absolute))
            err = recon - rho
            linf = float(np.max(np.abs(err)))
            repro_ratio = linf / float(s.frozen_realized_Linf)
            if not (REPRO_RATIO_GATE[0] <= repro_ratio <= REPRO_RATIO_GATE[1]):
                raise RuntimeError(f"reconstruction reproduction gate failed for {mid}/{codec}")

            sm = spectrum_metrics(err, g2)
            dv = hartree_potential(err, g2)
            hartree_rmse = float(np.sqrt(np.mean(dv * dv)))
            hartree_rel = hartree_rmse / v0_rms
            n = float(err.size)
            predicted_rmse2 = ((4.0 * np.pi) ** 2 / (n * n)) * sm["hartree_weighted_error"]
            direct_rmse2 = hartree_rmse * hartree_rmse
            parseval_rel = abs(predicted_rmse2 - direct_rmse2) / max(direct_rmse2, 1e-300)

            rows.append({
                "material_id": mid,
                "formula": str(s.formula),
                "triple_id": int(s.triple_id),
                "codec": codec,
                "nominal_tolerance_absolute": float(s.nominal_tolerance_absolute),
                "frozen_realized_Linf": float(s.frozen_realized_Linf),
                "reproduced_realized_Linf": linf,
                "reproduction_ratio": repro_ratio,
                "max_pairwise_distance_dex": float(s.max_pairwise_distance_dex),
                "density_rmse": float(np.sqrt(np.mean(err * err))),
                "hartree_RMSE": hartree_rmse,
                "hartree_rel_RMSE": hartree_rel,
                "parseval_relative_error": parseval_rel,
                **sm,
            })

    detail = pd.DataFrame(rows)
    detail.to_csv(out / "fourier_spectrum_detail.csv", index=False)

    summaries = pd.DataFrame([
        pair_summary(detail, "ZFP", "SZ3"),
        pair_summary(detail, "ZFP", "SPERR"),
        pair_summary(detail, "SZ3", "SPERR"),
    ])
    summaries.to_csv(out / "pairwise_mechanism_summary.csv", index=False)

    zs = summaries[summaries.pair == "ZFP/SZ3"].iloc[0]
    parseval_pass = bool(float(summaries.max_abs_parseval_relative_error.max()) < 1e-10)
    identity_pass = bool(
        abs(float(zs.median_hartree_RMSE_ratio) - float(zs.median_sqrt_hartree_weighted_ratio))
        / max(float(zs.median_hartree_RMSE_ratio), 1e-300)
        < 0.02
    )
    target_close = bool(
        abs(float(zs.median_hartree_RMSE_ratio) - TARGET_HARTREE_RATIO)
        / TARGET_HARTREE_RATIO
        <= TARGET_RATIO_REL_TOL
    )
    structure_direction = bool(
        float(zs.median_sqrt_spectral_susceptibility_ratio) < 1.0
        and float(zs.median_low_G_fraction_ratio) < 1.0
        and float(zs.median_centroid_delta_qmax) > 0.0
    )
    magnitude_not_sufficient = bool(
        float(zs.median_sqrt_total_error_energy_ratio)
        > 2.0 * float(zs.median_hartree_RMSE_ratio)
    )

    status = {
        "status": "MECHANISM_SUPPORTED" if (parseval_pass and identity_pass and structure_direction and magnitude_not_sufficient) else "MECHANISM_NOT_ESTABLISHED",
        "scope": "12-material frozen Hartree cohort; three-codec matched realized-Linf triples; frozen manuscript untouched",
        "definitions": {
            "matched_realized_Linf_caliper_dex": CALIPER_DEX,
            "low_G": f"0 < |G|/Gmax <= {LOW_Q}; G=0 reported separately and excluded from mechanism fractions",
            "high_G": f"|G|/Gmax >= {HIGH_Q}",
            "spectral_centroid": "sum |Delta rho(G)|^2 q / sum |Delta rho(G)|^2, q=|G|/Gmax",
            "hartree_weighted_error": "sum_{G!=0} |Delta rho(G)|^2 / |G|^4",
        },
        "checks": {
            "parseval_identity_pass": parseval_pass,
            "hartree_ratio_equals_sqrt_weighted_ratio_pass": identity_pass,
            "zfp_sz3_ratio_consistent_with_approx_0p078": target_close,
            "zfp_error_shifted_away_from_low_G_relative_to_sz3": structure_direction,
            "pointwise_total_spectral_energy_alone_is_insufficient": magnitude_not_sufficient,
        },
        "counts": {
            "materials": int(detail.material_id.nunique()),
            "matched_triples": int(detail.triple_id.nunique()),
            "codec_reconstructions": int(len(detail)),
        },
        "input_sha256": {
            str(bench_path.relative_to(REPO)): sha256(bench_path),
            str(meta_path.relative_to(REPO)): sha256(meta_path),
            str(cohort_path.relative_to(REPO)): sha256(cohort_path),
        },
        "environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "zfpy": getattr(zfpy, "__version__", "unknown"),
            "hdf5plugin": getattr(hdf5plugin, "__version__", "unknown"),
        },
    }
    (out / "SUMMARY.json").write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    public = [
        "status=" + status["status"],
        "parseval_identity_pass=" + str(parseval_pass).lower(),
        "weighted_identity_pass=" + str(identity_pass).lower(),
        "target_0p078_consistency=" + str(target_close).lower(),
        "spectral_structure_direction_pass=" + str(structure_direction).lower(),
        "magnitude_only_insufficient_pass=" + str(magnitude_not_sufficient).lower(),
        "scientific_values=encrypted",
    ]
    (out / "PUBLIC_QA.txt").write_text("\n".join(public) + "\n", encoding="utf-8")

    hashes = []
    for p in sorted(out.iterdir()):
        if p.is_file():
            hashes.append(f"{sha256(p)}  {p.name}")
    (out / "SHA256SUMS.txt").write_text("\n".join(hashes) + "\n", encoding="utf-8")

    print("FOURIER_SPECTRUM_PIPELINE_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
