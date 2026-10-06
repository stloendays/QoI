#!/usr/bin/env python3
"""Retrospective calibration of the a-priori gain predictors on the 12 engineering materials.

RETROSPECTIVE: the observed Hartree and electric-field ratios were known before these predictors were
written. Nothing here is a confirmation. Phase ``compute`` writes one JSON per material (predictions only,
computed from geometry + reference spectrum; no compression is run). Phase ``aggregate`` joins them with
the frozen observations and writes results/.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "analysis" / "operator_aware_codec_hartree_v02"))
sys.path.insert(0, str(REPO / "validation" / "qsq_prospective"))
import gain_predictors as gp  # noqa: E402
import operators as ops  # noqa: E402
import codec_qoac_h_v02 as qoac  # noqa: E402

MANIFEST = REPO / "analysis/operator_aware_codec_hartree/results/PILOT_MANIFEST.csv"
ALPHA_REL = np.logspace(-7.0, 1.0, 25)          # frozen ladder of the pilot / E-field / beta-map runs
BETAS = np.round(np.arange(0.0, 2.0001, 0.25), 2)
CALIPER_DEX = 0.05
MIN_MATCHES = 3
BETAMAP_TARGETS = 11
TAUS = (1e-4, 1e-6, 1e-8)
GAUSS_SIGMA = 0.5
DEFLATE_MAX_RATIO = 1032.0
ZLIB_STREAM_OVERHEAD = 11


# ---------------------------------------------------------------------------------------------------------
# container overhead of the frozen codecs (geometry only; no data)
# ---------------------------------------------------------------------------------------------------------
def _header_len(header):
    return len(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8"))


def fixed_bytes_v02(shape, lattice, shell_counts):
    recs = [{"shell": s, "count": int(c), "dtype": "<i1", "raw_bytes": 2 * int(c), "compressed_bytes": max(int(c) // 4, 1)}
            for s, c in enumerate(shell_counts)]
    header = {"version": 2, "shape": list(shape), "lattice": np.asarray(lattice).tolist(), "alpha": 0.012345678901234567,
              "beta": 1.25, "shell_count": 32, "zlib_level": 6, "dc_bytes": 16,
              "representative_modes": int(sum(shell_counts)), "self_conjugate_nonzero_modes": 7, "shells": recs}
    floor = sum(ZLIB_STREAM_OVERHEAD + 2.0 * c / DEFLATE_MAX_RATIO for c in shell_counts if c)
    return 8 + 8 + _header_len(header) + 16 + floor


def fixed_bytes_v01(shape, lattice, shell_counts, special_count):
    recs = [{"shell": s, "count": int(c), "dtype": "<i1", "raw_bytes": 2 * int(c), "compressed_bytes": max(int(c) // 4, 1)}
            for s, c in enumerate(shell_counts)]
    header = {"version": 1, "shape": list(shape), "lattice": np.asarray(lattice).tolist(), "alpha": 0.012345678901234567,
              "beta": 2.0, "shell_count": 32, "zlib_level": 6, "special_count": int(special_count),
              "special_raw_bytes": 16 * int(special_count), "special_compressed_bytes": 16 * int(special_count), "shells": recs}
    floor = sum(ZLIB_STREAM_OVERHEAD + 2.0 * c / DEFLATE_MAX_RATIO for c in shell_counts if c)
    return 8 + 8 + _header_len(header) + 16 * special_count + ZLIB_STREAM_OVERHEAD + floor


# ---------------------------------------------------------------------------------------------------------
# frozen observation statistics, mirrored on model curves
# ---------------------------------------------------------------------------------------------------------
def greedy_match(cr_a, cr_b):
    edges = []
    for ia, a in enumerate(cr_a):
        for ib, b in enumerate(cr_b):
            d = abs(math.log10(a) - math.log10(b))
            if d <= CALIPER_DEX + 1e-15:
                edges.append((d, ia, ib))
    edges.sort()
    ua, ub, out = set(), set(), []
    for d, ia, ib in edges:
        if ia in ua or ib in ub:
            continue
        ua.add(ia); ub.add(ib); out.append((ia, ib))
    return out


def matched_median(curve_a, curve_b):
    pairs = greedy_match(curve_a["cr"], curve_b["cr"])
    r = [curve_a["err"][i] / curve_b["err"][j] for i, j in pairs if curve_b["err"][j] > 0]
    return (float(np.median(r)) if len(r) >= MIN_MATCHES else float("nan")), len(r), pairs


def _interp(cr, err, target):
    x = np.log10(cr); y = np.log10(err)
    o = np.argsort(x); x, y = x[o], y[o]
    ux = np.unique(x); uy = np.array([y[x == v].min() for v in ux])
    return float(np.interp(target, ux, uy))


def _tie_argmin(scores):
    best = min(scores.values())
    return sorted((b for b, s in scores.items() if abs(s - best) <= 1e-12), key=lambda b: (abs(b - 1.0), b))[0]


def betamap_optimum(curves):
    sup = {b: (np.log10(c["cr"]).min(), np.log10(c["cr"]).max()) for b, c in curves.items()}
    L = max(v[0] for v in sup.values()); U = min(v[1] for v in sup.values())
    if not U > L:
        return float("nan"), {}
    targets = np.linspace(L + 0.05 * (U - L), U - 0.05 * (U - L), BETAMAP_TARGETS)
    vals = {b: np.array([_interp(c["cr"], c["err"], t) for t in targets]) for b, c in curves.items()}
    scores = {b: float(np.median(v - vals[1.0])) for b, v in vals.items()}
    return _tie_argmin(scores), scores


def model_ladder(model, log_w, log_u, ptp, raw_bytes, fixed, ref_energy, rate_mask=None):
    cr, err, dz = [], [], []
    for a in ALPHA_REL:
        p = gp.finite_rate_point(model, log_w, log_u, math.log(a * ptp), rate_mask)
        cr.append(raw_bytes / (fixed + p["rate_bits"] / 8.0))
        err.append(math.sqrt(p["distortion"] / ref_energy))
        dz.append(p["dead_zone_fraction"])
    return {"cr": np.array(cr), "err": np.array(err), "dead": np.array(dz)}


# ---------------------------------------------------------------------------------------------------------
# phase 1: per-material predictions
# ---------------------------------------------------------------------------------------------------------
def load_field(dev, meta, cache: Path):
    path = cache / f"{meta['material_id']}.src"
    blob = path.read_bytes() if path.exists() else b""
    if hashlib.sha256(blob).hexdigest() != meta["sha256"]:
        blob = dev.fetch_exact(meta["url"], meta["sha256"], int(meta["source_bytes"]))
        path.write_bytes(blob)
    with tempfile.TemporaryDirectory(prefix="wsb_") as td:
        grid, _ = dev.build_grid(meta, blob, Path(td))
        field = np.ascontiguousarray(np.asarray(grid.total, dtype=np.float64))
        lattice = np.asarray(grid.structure.lattice.matrix, dtype=np.float64)
    return field, lattice


def compute_material(meta, field, lattice):
    mid = meta["material_id"]
    shape = tuple(int(v) for v in field.shape)
    raw_bytes = float(field.nbytes)
    ptp = float(np.ptp(field))
    t0 = time.perf_counter()
    topo = qoac.build_topology(shape, lattice, shell_count=32)
    shell_counts = np.bincount(topo.shell_ids.astype(np.int64), minlength=32)
    model = gp.spectrum_model(field, lattice, topology=topo)
    del topo
    fixed02 = fixed_bytes_v02(shape, lattice, shell_counts)
    nyq_rfft = int(ops.nyquist_mask_rfft(shape).sum())
    fixed01 = fixed_bytes_v01(shape, lattice, shell_counts, nyq_rfft + 1)
    g2_safe_max = float(np.max(model.g2[model.safe]))
    out = {"material_id": mid, "system_type": meta["system_type"], "shape": list(shape), "n_points": model.n_points,
           "orbits": int(model.count.sum()), "orbit_groups": int(model.g2.size), "ptp": ptp,
           "fixed_bytes_v02": fixed02, "fixed_bytes_v01": fixed01}

    pot, fld = ops.hartree_potential(), ops.hartree_field()
    lw_h, lw_e = gp.log_weight(pot, model), gp.log_weight(fld, model)
    pl = lambda b: gp.power_law(b)(model)

    # (a) high-rate orbit-only
    out["a_hartree_b2_over_b0"] = gp.highrate_rmse_ratio(model, lw_h, pl(2.0), pl(0.0))
    out["a_ef_b1_over_b0"] = gp.highrate_rmse_ratio(model, lw_e, pl(1.0), pl(0.0))
    out["a_ef_b1_over_b2"] = gp.highrate_rmse_ratio(model, lw_e, pl(1.0), pl(2.0))
    opt = gp.highrate_optimal_beta(model, lw_e, BETAS)
    out["a_ef_beta_opt_grid"] = opt["beta_grid"]; out["a_ef_beta_opt_continuous"] = opt["beta_continuous"]

    # (b) finite-rate, mirrored on the frozen alpha ladders and frozen matching statistics
    #     Hartree pilot: QOAC-H v0.1 (rFFT, Nyquist planes stored exactly, q normalized over non-Nyquist modes)
    ref_h = model.reference_energy(np.exp(lw_h)); ref_e = model.reference_energy(np.exp(lw_e))
    hl = {b: model_ladder(model, lw_h, gp.power_law(b, g2_safe_max)(model), ptp, raw_bytes, fixed01, ref_h, model.safe)
          for b in (0.0, 2.0)}
    out["b_hartree_b2_over_b0"], out["b_hartree_pairs"], _ = matched_median(hl[2.0], hl[0.0])
    #     E-field: QOAC-H v0.2 orbit codec, full beta grid
    el = {float(b): model_ladder(model, lw_e, pl(float(b)), ptp, raw_bytes, fixed02, ref_e) for b in BETAS}
    out["b_ef_b1_over_b0"], out["b_ef_pairs_b1_b0"], pairs10 = matched_median(el[1.0], el[0.0])
    out["b_ef_b1_over_b2"], out["b_ef_pairs_b1_b2"], pairs12 = matched_median(el[1.0], el[2.0])
    bopt, scores = betamap_optimum(el)
    out["b_ef_beta_opt_betamap"] = bopt
    out.update({f"b_ef_score_beta_{b:g}": s for b, s in scores.items()})
    # model dead-zone fraction at the ladder points that entered the matched pairs
    for b, idx in ((0.0, [j for _, j in pairs10]), (1.0, [i for i, _ in pairs10]), (2.0, [j for _, j in pairs12])):
        out[f"b_ef_dead_zone_beta{b:g}"] = float(np.median(el[b]["dead"][idx])) if idx else float("nan")
    out["ladder_ef"] = {f"{b:g}": {"cr": el[b]["cr"].tolist(), "err": el[b]["err"].tolist()} for b in (0.0, 1.0, 2.0)}

    #     same quantities at one fixed target (tau = 1e-6), matched rate
    for name, lw, ba, bb in (("hartree_b2_over_b0", lw_h, 2.0, 0.0), ("ef_b1_over_b0", lw_e, 1.0, 0.0),
                             ("ef_b1_over_b2", lw_e, 1.0, 2.0)):
        g = gp.finite_rate_gain(model, lw, pl(ba), pl(bb), 1e-6)
        out[f"b_tau1e-6_{name}"] = g.get("matched_rate_rmse_ratio", float("nan"))
    rates = {}
    for b in BETAS:
        la = gp.alpha_for_distortion(model, lw_e, pl(float(b)), 1e-12 * ref_e)
        rates[float(b)] = gp.finite_rate_point(model, lw_e, pl(float(b)), la)["rate_bits"]
    out["b_tau1e-6_ef_beta_opt"] = _tie_argmin({b: math.log(r) for b, r in rates.items()})

    # prediction table: operator-optimal u = w^{-1/2} vs blind u = 1 (no compression run exists for these)
    table = []
    for op in ops.standard_operators(gaussian_sigmas=(GAUSS_SIGMA,)):
        lw = gp.log_weight(op, model)
        ua, ub = gp.operator_optimal(op)(model), gp.blind()(model)
        a_log = gp.highrate_log_rmse_ratio(model, lw, ua, ub)
        a_ratio = math.exp(a_log)
        a_save = gp.highrate_rate_saving_bits_per_point(model, lw, ua, ub)
        for tau in TAUS:
            g = gp.finite_rate_gain(model, lw, ua, ub, tau)
            table.append({"material_id": mid, "system_type": meta["system_type"], "operator": op.label, "target_rel_rmse": tau,
                          "a_matched_rate_rmse_ratio": a_ratio, "a_log10_matched_rate_rmse_ratio": a_log / math.log(10.0),
                          "a_rate_saving_bits_per_point": a_save,
                          "b_reachable": g["reachable"],
                          "b_bits_per_point_optimal": g.get("bits_per_point_a", float("nan")),
                          "b_bits_per_point_blind": g.get("bits_per_point_b", float("nan")),
                          "b_rate_ratio_optimal_over_blind": g.get("rate_ratio", float("nan")),
                          "b_matched_rate_rmse_ratio": g.get("matched_rate_rmse_ratio", float("nan")),
                          "b_dead_zone_optimal": g.get("dead_zone_a", float("nan")),
                          "b_dead_zone_blind": g.get("dead_zone_b", float("nan"))})
    out["prediction_table"] = table
    out["seconds"] = time.perf_counter() - t0
    return out


def phase_compute(a):
    import development_compatibility_smoke as dev
    a.work_dir.mkdir(parents=True, exist_ok=True)
    a.cache_dir.mkdir(parents=True, exist_ok=True)
    for meta in csv.DictReader(open(MANIFEST, encoding="utf-8")):
        if a.only and meta["material_id"] not in a.only.split(","):
            continue
        dst = a.work_dir / f"pred_{meta['material_id']}.json"
        if dst.exists():
            print("SKIP", meta["material_id"], flush=True); continue
        field, lattice = load_field(dev, meta, a.cache_dir)
        res = compute_material(meta, field, lattice)
        dst.write_text(json.dumps(res, indent=1), encoding="utf-8")
        print(f"DONE {meta['material_id']} {res['seconds']:.1f}s groups={res['orbit_groups']}/{res['orbits']}", flush=True)


# ---------------------------------------------------------------------------------------------------------
# phase 2: join with frozen observations
# ---------------------------------------------------------------------------------------------------------
def _agreement(pred, obs, log=True):
    pred = np.asarray(pred, float); obs = np.asarray(obs, float)
    ok = np.isfinite(pred) & np.isfinite(obs)
    p, o = pred[ok], obs[ok]
    rho, pval = stats.spearmanr(p, o) if ok.sum() >= 3 else (float("nan"), float("nan"))
    res = {"n": int(ok.sum()), "median_pred": float(np.median(p)), "median_obs": float(np.median(o)),
           "spearman_rho": float(rho), "spearman_p": float(pval)}
    if log:
        res["median_abs_log_error"] = float(np.median(np.abs(np.log(p / o))))
        res["median_signed_log_error"] = float(np.median(np.log(p / o)))
    else:
        res["median_abs_error"] = float(np.median(np.abs(p - o)))
        res["exact_matches"] = int(np.sum(np.abs(p - o) < 1e-9))
    return res


def phase_aggregate(a):
    out = a.output_dir; out.mkdir(parents=True, exist_ok=True)
    preds = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(a.work_dir.glob("pred_*.json"))]
    if len(preds) != 12:
        raise RuntimeError(f"expected 12 materials, found {len(preds)}")
    res = REPO / "analysis"
    h = pd.read_csv(res / "operator_aware_codec_hartree/results/mechanism_material.csv").set_index("material_id")
    e = pd.read_csv(res / "general_qoac_electric_field/results/mechanism_material.csv").set_index("material_id")
    bm = pd.read_csv(res / "general_qoac_electric_field_beta_map/results/beta_map_material.csv").set_index("material_id")
    dg = pd.read_csv(res / "general_qoac_electric_field_diagnosis/results/diagnosis_material.csv").set_index("material_id")
    rows_ef = pd.read_csv(res / "general_qoac_electric_field_beta_map/results/beta_map_rows.csv")

    cal, table = [], []
    for p in preds:
        mid = p["material_id"]
        r = {k: v for k, v in p.items() if not isinstance(v, (list, dict))}
        r.pop("shape", None)
        r["obs_hartree_b2_over_b0"] = float(h.loc[mid, "median_hartree_ratio_beta2_over_beta0"])
        r["obs_ef_b1_over_b0"] = float(e.loc[mid, "median_error_ratio_beta1_over_beta0"])
        r["obs_ef_b1_over_b2"] = float(e.loc[mid, "median_error_ratio_beta1_over_beta2"])
        r["obs_ef_beta_opt"] = float(bm.loc[mid, "beta_opt"])
        for b in (0, 1, 2):
            r[f"obs_ef_dead_zone_beta{b}"] = float(dg.loc[mid, f"dead_zone_fraction_beta{b}"])
        r["d1_ef_b1_over_b0"] = float(dg.loc[mid, "theory_ef_beta1_over_beta0"])
        r["d1_hartree_b2_over_b0"] = float(dg.loc[mid, "theory_hartree_beta2_over_beta0"])
        # absolute fidelity of the model curves at the frozen ladder points (beta = 0, 1, 2)
        dcr, derr = [], []
        for b in ("0", "1", "2"):
            z = rows_ef[(rows_ef.material_id == mid) & np.isclose(rows_ef.beta, float(b))].sort_values("alpha_rel_ptp")
            lad = p["ladder_ef"][b]
            dcr += list(np.log10(np.asarray(lad["cr"]) / z.compression_ratio.to_numpy(float)))
            derr += list(np.log10(np.asarray(lad["err"]) / z.electric_field_error_rel_RMSE_safe.to_numpy(float)))
        r["b_ef_curve_median_abs_log10_cr_error"] = float(np.median(np.abs(dcr)))
        r["b_ef_curve_median_abs_log10_err_error"] = float(np.median(np.abs(derr)))
        cal.append(r)
        table += p["prediction_table"]
    cal = pd.DataFrame(cal).sort_values("material_id")
    table = pd.DataFrame(table)
    if "a_log10_matched_rate_rmse_ratio" not in table:
        table["a_log10_matched_rate_rmse_ratio"] = np.nan
    miss = table.a_log10_matched_rate_rmse_ratio.isna()
    table.loc[miss, "a_log10_matched_rate_rmse_ratio"] = np.log10(table.loc[miss, "a_matched_rate_rmse_ratio"])
    cal.to_csv(out / "calibration_material.csv", index=False)
    table.to_csv(out / "prediction_table.csv", index=False)

    comp = {}
    for q in ("hartree_b2_over_b0", "ef_b1_over_b0", "ef_b1_over_b2"):
        comp[q] = {"a_highrate": _agreement(cal[f"a_{q}"], cal[f"obs_{q}"]),
                   "b_finite_rate_ladder": _agreement(cal[f"b_{q}"], cal[f"obs_{q}"]),
                   "b_finite_rate_tau1e-6": _agreement(cal[f"b_tau1e-6_{q}"], cal[f"obs_{q}"])}
    comp["ef_beta_opt"] = {"a_highrate_grid": _agreement(cal.a_ef_beta_opt_grid, cal.obs_ef_beta_opt, log=False),
                           "a_highrate_continuous": _agreement(cal.a_ef_beta_opt_continuous, cal.obs_ef_beta_opt, log=False),
                           "b_finite_rate_betamap": _agreement(cal.b_ef_beta_opt_betamap, cal.obs_ef_beta_opt, log=False),
                           "b_finite_rate_tau1e-6": _agreement(cal["b_tau1e-6_ef_beta_opt"], cal.obs_ef_beta_opt, log=False)}
    comp["ef_dead_zone"] = {f"beta{b}": _agreement(cal[f"b_ef_dead_zone_beta{b}"], cal[f"obs_ef_dead_zone_beta{b}"])
                            for b in (0, 1, 2)}
    comp["model_curve_fidelity"] = {
        "median_abs_log10_cr_error": float(cal.b_ef_curve_median_abs_log10_cr_error.median()),
        "median_abs_log10_err_error": float(cal.b_ef_curve_median_abs_log10_err_error.median())}
    comp["d1_closure_max_rel"] = float(max(np.max(np.abs(cal.a_ef_b1_over_b0 / cal.d1_ef_b1_over_b0 - 1)),
                                           np.max(np.abs(cal.a_hartree_b2_over_b0 / cal.d1_hartree_b2_over_b0 - 1))))

    pt = table.groupby(["operator", "target_rel_rmse"]).agg(
        a_matched_rate_rmse_ratio=("a_matched_rate_rmse_ratio", "median"),
        a_log10_matched_rate_rmse_ratio=("a_log10_matched_rate_rmse_ratio", "median"),
        a_rate_saving_bits_per_point=("a_rate_saving_bits_per_point", "median"),
        b_reachable=("b_reachable", "sum"),
        b_bits_per_point_optimal=("b_bits_per_point_optimal", "median"),
        b_bits_per_point_blind=("b_bits_per_point_blind", "median"),
        b_rate_ratio_optimal_over_blind=("b_rate_ratio_optimal_over_blind", "median"),
        b_rate_ratio_min=("b_rate_ratio_optimal_over_blind", "min"),
        b_rate_ratio_max=("b_rate_ratio_optimal_over_blind", "max"),
        b_matched_rate_rmse_ratio=("b_matched_rate_rmse_ratio", "median"),
        b_dead_zone_optimal=("b_dead_zone_optimal", "median"),
        b_dead_zone_blind=("b_dead_zone_blind", "median")).reset_index()
    summary = {
        "status": "RETROSPECTIVE_CALIBRATION",
        "note": "Observed ratios were known before the predictors were written; this is not a confirmation. "
                "The prediction table covers operators without any compression run and is not compared with one.",
        "population": "12 engineering materials of operator_aware_codec_hartree/results/PILOT_MANIFEST.csv",
        "settings": {"alpha_rel_ladder": "logspace(-7,1,25) * ptp(rho)", "beta_grid": BETAS.tolist(),
                     "variance_bins": gp.VARIANCE_BINS, "caliper_dex": CALIPER_DEX, "taus": list(TAUS),
                     "gaussian_sigma_angstrom": GAUSS_SIGMA},
        "calibration": comp,
        "prediction_table_median": json.loads(pt.to_json(orient="records")),
    }
    (out / "SUMMARY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(comp, indent=1))
    print(pt.to_string())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("phase", choices=("compute", "aggregate"))
    p.add_argument("--cache-dir", type=Path, default=Path(r"D:\Research\QoI-delegation\scratch_wsb\cache"))
    p.add_argument("--work-dir", type=Path, default=Path(r"D:\Research\QoI-delegation\scratch_wsb\pred"))
    p.add_argument("--output-dir", type=Path, default=HERE / "results")
    p.add_argument("--only", default="", help="comma-separated material ids (compute phase)")
    a = p.parse_args()
    phase_compute(a) if a.phase == "compute" else phase_aggregate(a)


if __name__ == "__main__":
    main()
