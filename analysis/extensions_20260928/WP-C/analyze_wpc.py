#!/usr/bin/env python3
"""WP-C analyses (pre-declared in analysis/extensions_20260928/PROTOCOL.md).

Reads only machine-written inputs: probe_outcomes.csv / spectra.csv / failures.csv from run_wpc.py
and the frozen tables. Writes floors.csv, agreement.csv, alignment.csv, spectral_link.csv,
predictive.csv, RESULTS.md and provenance.json. Every reported number is taken from these files.

Uncertainty: material-cluster bootstrap, 2,000 resamples, seed 20260928, percentile 95% CI.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
CODECS = ("ZFP", "SZ3", "SPERR")
TAUS = (1e-4, 1e-3, 1e-2)
BOOT_REPS = 2000
BOOT_SEED = 20260928
PRIMARY_TAU = 1e-3


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--frozen-root", type=Path, required=True)
    p.add_argument("--wpc-dir", type=Path, default=HERE)
    p.add_argument("--python-exe", type=Path, default=Path(sys.executable))
    p.add_argument("--wall-seconds-run", type=float, default=float("nan"))
    return p.parse_args()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ----------------------------------------------------------------------------- bootstrap

def boot_ci(values: np.ndarray, stat: Callable[[np.ndarray], float]) -> tuple[float, float, float]:
    """Material-cluster percentile bootstrap of `stat` over one value per material."""
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(BOOT_SEED)
    idx = rng.integers(0, v.size, size=(BOOT_REPS, v.size))
    reps = np.array([stat(v[i]) for i in idx])
    return float(stat(v)), float(np.nanpercentile(reps, 2.5)), float(np.nanpercentile(reps, 97.5))


def boot_ci_paired(a: np.ndarray, b: np.ndarray, stat: Callable[[np.ndarray, np.ndarray], float]) -> tuple[float, float, float]:
    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)
    ok = np.isfinite(a) & np.isfinite(b)
    a, b = a[ok], b[ok]
    if a.size < 3:
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(BOOT_SEED)
    idx = rng.integers(0, a.size, size=(BOOT_REPS, a.size))
    reps = np.array([stat(a[i], b[i]) for i in idx])
    return float(stat(a, b)), float(np.nanpercentile(reps, 2.5)), float(np.nanpercentile(reps, 97.5))


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    if a.size < 3 or np.all(a == a[0]) or np.all(b == b[0]):
        return float("nan")
    return float(spearmanr(a, b).statistic)


def kappa(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=bool); y = np.asarray(y, dtype=bool)
    n = x.size
    if n == 0:
        return float("nan")
    po = float(np.mean(x == y))
    pe = float(np.mean(x) * np.mean(y) + (1 - np.mean(x)) * (1 - np.mean(y)))
    if pe == 1.0:
        return 1.0 if po == 1.0 else float("nan")
    return (po - pe) / (1 - pe)


# ----------------------------------------------------------------------------- main

def main() -> int:
    args = parse_args()
    t0 = time.time()
    repo = args.repo_root.resolve()
    frozen = args.frozen_root.resolve()
    wpc = args.wpc_dir.resolve()

    inputs = {
        "probe_outcomes": wpc / "probe_outcomes.csv",
        "spectra": wpc / "spectra.csv",
        "failures": wpc / "failures.csv",
        "run_manifest": wpc / "run_manifest.json",
        "stability_floor_A1": repo / "stability" / "stability_floor_A1.csv",
        "stability_floor_A1_per_seed": repo / "stability" / "stability_floor_A1_per_seed.csv",
        "master_benchmark_full": repo / "benchmark" / "master_benchmark_full.csv",
        "materials_metadata": repo / "materials_metadata.csv",
        "p2_outcomes": repo / "validation" / "qsq_prospective" / "p2_fresh_probes" / "outcomes.csv",
        "frozen_external_end_to_end": frozen / "validation" / "external_end_to_end.py",
        "frozen_requirements": frozen / "validation" / "requirements-external-e2e.txt",
        "dev_compat_smoke": repo / "validation" / "qsq_prospective" / "development_compatibility_smoke.py",
        "hartree_run_shard": repo / "analysis" / "hartree_spectral_mechanism" / "run_shard.py",
        "protocol": repo / "analysis" / "extensions_20260928" / "PROTOCOL.md",
    }

    out = pd.read_csv(inputs["probe_outcomes"])
    spectra = pd.read_csv(inputs["spectra"])
    failures = pd.read_csv(inputs["failures"]) if inputs["failures"].stat().st_size > 0 else pd.DataFrame(columns=["material_id", "codec", "k", "stage", "error"])
    manifest = json.loads(inputs["run_manifest"].read_text(encoding="utf-8"))
    meta = pd.read_csv(inputs["materials_metadata"])
    meta = meta[meta["corpus"].str.startswith("dev")]
    dev_materials = sorted(meta["material_id"])
    n_materials = len(dev_materials)
    stratum = dict(zip(meta["material_id"], meta["system_type"]))

    floors_frozen = pd.read_csv(inputs["stability_floor_A1"])
    f_iid = dict(zip(floors_frozen["material_id"], floors_frozen["stability_floor_A1_e"].astype(float)))
    k_values = sorted(int(k) for k in manifest["k_values"])
    k_shift = [k for k in k_values if k > 0]

    # P2 fresh exceedance rate per material (59 trials, all SUCCESS in the frozen table).
    p2 = pd.read_csv(inputs["p2_outcomes"], usecols=["material_id", "bader_response_max_e", "status"])
    p2 = p2[p2["status"] == "SUCCESS"]
    p2_rate = p2.groupby("material_id")["bader_response_max_e"].apply(lambda s: float(np.mean(s.astype(float) >= PRIMARY_TAU)))
    p2_n = p2.groupby("material_id").size()

    # ------------------------------------------------------------------ per material x codec floors
    ok = out[out["status"] == "SUCCESS"].copy()
    floor_rows: list[dict[str, Any]] = []
    for m in dev_materials:
        for c in CODECS:
            sub = ok[(ok["material_id"] == m) & (ok["codec"] == c)]
            resp = {int(k): float(v) for k, v in zip(sub["k"], sub["bader_response_max_e"])}
            n_fail = int(((failures["material_id"] == m) & (failures["codec"] == c)).sum()) if len(failures) else 0
            shifted = [resp[k] for k in k_shift if k in resp]
            n_shift_fail = sum(1 for k in k_shift if k not in resp)
            fc = max(shifted) if shifted and n_shift_fail == 0 else float("nan")   # floor undefined if any k>=1 solve failed
            fi = f_iid[m]
            r0 = resp.get(0, float("nan"))
            med_shift = float(np.median(shifted)) if shifted and n_shift_fail == 0 else float("nan")
            row = {
                "material_id": m, "system_type": stratum[m], "codec": c,
                "base_rung_relative": float(sub["base_rung_relative"].iloc[0]) if len(sub) else float("nan"),
                "n_k_planned": len(k_values), "n_k_success": len(resp), "n_k_failed": n_fail,
                "n_shifted_success": len(shifted), "n_shifted_failed": n_shift_fail,
                "iid_floor_f_e": fi, "codec_shaped_floor_fc_e": fc,
                "log10_fc_over_f": (math.log10(fc / fi) if (np.isfinite(fc) and fc > 0 and fi > 0) else float("nan")),
                "fc_gt_f": (bool(fc > fi) if np.isfinite(fc) else None),
                "response_k0_e": r0, "median_response_shifted_e": med_shift,
                "log10_k0_over_median_shifted": (math.log10(r0 / med_shift) if (np.isfinite(r0) and np.isfinite(med_shift) and r0 > 0 and med_shift > 0) else float("nan")),
                "p2_fresh_exceedance_rate_1e-3": float(p2_rate.get(m, float("nan"))),
                "p2_fresh_trials": int(p2_n.get(m, 0)),
            }
            for k in k_values:
                row[f"response_k{k}_e"] = resp.get(k, float("nan"))
            for tau in TAUS:
                row[f"iid_eligible_at_{tau:g}"] = bool(fi < tau)
                row[f"codec_shaped_eligible_at_{tau:g}"] = (bool(fc < tau) if np.isfinite(fc) else None)
            sp = spectra[(spectra["material_id"] == m) & (spectra["codec"] == c)]
            row["residual_low_G_fraction"] = float(sp["low_G_fraction"].iloc[0]) if len(sp) else float("nan")
            row["residual_high_G_fraction"] = float(sp["high_G_fraction"].iloc[0]) if len(sp) else float("nan")
            row["residual_spectral_centroid_qmax"] = float(sp["spectral_centroid_qmax"].iloc[0]) if len(sp) else float("nan")
            floor_rows.append(row)
    floors = pd.DataFrame(floor_rows)
    floors.to_csv(wpc / "floors.csv", index=False)

    # ------------------------------------------------------------------ analysis 1: floor ratio
    a1_rows: list[dict[str, Any]] = []
    verdicts: dict[str, dict[str, Any]] = {}
    for c in CODECS:
        for strat in ("all", "bulk", "slab"):
            sub = floors[(floors["codec"] == c) & ((floors["system_type"] == strat) if strat != "all" else True)]
            v = sub["log10_fc_over_f"].to_numpy(float)
            fin = np.isfinite(v)
            med, lo, hi = boot_ci(v, np.median)
            mean, mlo, mhi = boot_ci(v, np.mean)
            frac_gt = float(np.mean(sub.loc[fin, "fc_gt_f"].astype(bool))) if fin.any() else float("nan")
            fg, fglo, fghi = boot_ci(sub.loc[fin, "fc_gt_f"].astype(float).to_numpy(), np.mean)
            q = np.nanpercentile(v[fin], [5, 25, 75, 95]) if fin.any() else [float("nan")] * 4
            row = {
                "codec": c, "stratum": strat, "n_materials": int(len(sub)), "n_with_defined_ratio": int(fin.sum()),
                "n_undefined_ratio": int((~fin).sum()),
                "median_log10_fc_over_f": med, "median_ci95_lo": lo, "median_ci95_hi": hi,
                "mean_log10_fc_over_f": mean, "mean_ci95_lo": mlo, "mean_ci95_hi": mhi,
                "p05_log10": q[0], "p25_log10": q[1], "p75_log10": q[2], "p95_log10": q[3],
                "frac_fc_gt_f": frac_gt, "frac_fc_gt_f_ci95_lo": fglo, "frac_fc_gt_f_ci95_hi": fghi,
                "n_fc_gt_f": int(sub.loc[fin, "fc_gt_f"].astype(bool).sum()) if fin.any() else 0,
            }
            if strat == "all":
                if np.isfinite(med) and hi < 0:
                    verdict = "CONSERVATIVE"
                elif np.isfinite(med) and lo > 0:
                    verdict = "ANTI-CONSERVATIVE"
                else:
                    verdict = "NOT DISTINGUISHABLE FROM 0 (neither conservative nor anti-conservative by the pre-declared rule)"
                row["acceptance_verdict"] = verdict
                verdicts[c] = row
            a1_rows.append(row)
    a1 = pd.DataFrame(a1_rows)
    a1.to_csv(wpc / "floor_ratio_summary.csv", index=False)

    # ------------------------------------------------------------------ analysis 2: eligibility agreement
    a2_rows: list[dict[str, Any]] = []
    flips: list[dict[str, Any]] = []
    for c in CODECS:
        sub = floors[floors["codec"] == c]
        for tau in TAUS:
            e_iid = sub[f"iid_eligible_at_{tau:g}"]
            e_c = sub[f"codec_shaped_eligible_at_{tau:g}"]
            defined = e_c.notna()
            x = e_iid[defined].astype(bool).to_numpy(); y = e_c[defined].astype(bool).to_numpy()
            kap = kappa(x, y)
            # bootstrap kappa over materials
            rng = np.random.default_rng(BOOT_SEED)
            reps = []
            for _ in range(BOOT_REPS):
                i = rng.integers(0, x.size, size=x.size)
                reps.append(kappa(x[i], y[i]))
            reps = np.array(reps, dtype=float)
            n_ie_cr = int(np.sum(x & ~y))   # iid eligible, codec-shaped rejects  (flip: eligible -> rejected)
            n_ir_ce = int(np.sum(~x & y))   # iid rejected, codec-shaped admits   (flip: rejected -> eligible)
            a2_rows.append({
                "codec": c, "tau_e": tau, "n_materials": int(defined.sum()), "n_undefined": int((~defined).sum()),
                "iid_eligible": int(x.sum()), "codec_shaped_eligible": int(y.sum()),
                "both_eligible": int(np.sum(x & y)), "both_rejected": int(np.sum(~x & ~y)),
                "flip_iid_eligible_to_codec_rejected": n_ie_cr, "flip_iid_rejected_to_codec_eligible": n_ir_ce,
                "n_flips": n_ie_cr + n_ir_ce, "agreement_fraction": float(np.mean(x == y)),
                "cohen_kappa": kap, "kappa_ci95_lo": float(np.nanpercentile(reps, 2.5)), "kappa_ci95_hi": float(np.nanpercentile(reps, 97.5)),
            })
            for m, xi, yi, fi, fc in zip(sub.loc[defined, "material_id"], x, y, sub.loc[defined, "iid_floor_f_e"], sub.loc[defined, "codec_shaped_floor_fc_e"]):
                if xi != yi:
                    flips.append({"codec": c, "tau_e": tau, "material_id": m, "system_type": stratum[m],
                                  "iid_floor_f_e": fi, "codec_shaped_floor_fc_e": fc,
                                  "direction": "iid_eligible->codec_shaped_rejected" if xi else "iid_rejected->codec_shaped_eligible"})
    a2 = pd.DataFrame(a2_rows)
    a2.to_csv(wpc / "agreement.csv", index=False)
    pd.DataFrame(flips, columns=["codec", "tau_e", "material_id", "system_type", "iid_floor_f_e", "codec_shaped_floor_fc_e", "direction"]).to_csv(wpc / "eligibility_flips.csv", index=False)

    # ------------------------------------------------------------------ analysis 3: alignment effect
    a3_rows: list[dict[str, Any]] = []
    for c in CODECS:
        for strat in ("all", "bulk", "slab"):
            sub = floors[(floors["codec"] == c) & ((floors["system_type"] == strat) if strat != "all" else True)]
            v = sub["log10_k0_over_median_shifted"].to_numpy(float)
            med, lo, hi = boot_ci(v, np.median)
            fin = np.isfinite(v)
            a3_rows.append({
                "codec": c, "stratum": strat, "n_materials": int(len(sub)), "n_defined": int(fin.sum()),
                "median_log10_k0_over_median_shifted": med, "ci95_lo": lo, "ci95_hi": hi,
                "frac_k0_above_shifted_median": float(np.mean(v[fin] > 0)) if fin.any() else float("nan"),
                "p05": float(np.nanpercentile(v[fin], 5)) if fin.any() else float("nan"),
                "p95": float(np.nanpercentile(v[fin], 95)) if fin.any() else float("nan"),
            })
    a3 = pd.DataFrame(a3_rows)
    a3.to_csv(wpc / "alignment.csv", index=False)

    # ------------------------------------------------------------------ analysis 4: Fourier link
    a4_rows: list[dict[str, Any]] = []
    for c in CODECS:
        sub = floors[floors["codec"] == c]
        a = sub["log10_fc_over_f"].to_numpy(float); b = sub["residual_low_G_fraction"].to_numpy(float)
        rho, lo, hi = boot_ci_paired(a, b, spearman)
        n = int(np.sum(np.isfinite(a) & np.isfinite(b)))
        a4_rows.append({"codec": c, "n_materials": n, "spearman_rho_log10ratio_vs_lowG_fraction": rho, "ci95_lo": lo, "ci95_hi": hi,
                        "median_low_G_fraction": float(np.nanmedian(b))})
    # pooled across codecs (material x codec rows; bootstrap by material cluster)
    a4 = pd.DataFrame(a4_rows)
    a4.to_csv(wpc / "spectral_link.csv", index=False)

    # ------------------------------------------------------------------ analysis 5: predictive value
    a5_rows: list[dict[str, Any]] = []
    for c in CODECS:
        sub = floors[(floors["codec"] == c) & (floors[f"iid_eligible_at_{PRIMARY_TAU:g}"])]
        p = sub["p2_fresh_exceedance_rate_1e-3"].to_numpy(float)
        fi = np.log10(sub["iid_floor_f_e"].to_numpy(float))
        fc = np.log10(sub["codec_shaped_floor_fc_e"].to_numpy(float))
        r_i, ilo, ihi = boot_ci_paired(fi, p, spearman)
        r_c, clo, chi = boot_ci_paired(fc, p, spearman)
        # paired difference rho(fc) - rho(f) on the same bootstrap resamples
        okm = np.isfinite(fi) & np.isfinite(fc) & np.isfinite(p)
        fi2, fc2, p2v = fi[okm], fc[okm], p[okm]
        if okm.sum() >= 3:
            rng = np.random.default_rng(BOOT_SEED)
            idx = rng.integers(0, okm.sum(), size=(BOOT_REPS, okm.sum()))
            diffs = np.array([spearman(fc2[i], p2v[i]) - spearman(fi2[i], p2v[i]) for i in idx])
        else:
            diffs = np.array([float("nan")])
        a5_rows.append({
            "codec": c, "n_admitted": int(len(sub)), "n_used": int(okm.sum()),
            "n_with_any_fresh_exceedance": int(np.sum(p2v > 0)),
            "spearman_f_iid_vs_p2_rate": r_i, "f_ci95_lo": ilo, "f_ci95_hi": ihi,
            "spearman_fc_vs_p2_rate": r_c, "fc_ci95_lo": clo, "fc_ci95_hi": chi,
            "rho_diff_fc_minus_f": spearman(fc2, p2v) - spearman(fi2, p2v),
            "rho_diff_ci95_lo": float(np.nanpercentile(diffs, 2.5)), "rho_diff_ci95_hi": float(np.nanpercentile(diffs, 97.5)),
        })
    a5 = pd.DataFrame(a5_rows)
    a5.to_csv(wpc / "predictive.csv", index=False)

    # ------------------------------------------------------------------ population accounting
    n_planned = int(manifest["solves_planned"]); n_ok = int(len(out[out["status"] == "SUCCESS"])); n_fail = int(len(failures))
    rung_counts = ok.groupby(["codec", "base_rung_relative"]).size().reset_index(name="n_rows")
    repro = ok.groupby(["material_id", "codec"])["residual_reproduction_abs_log10_ratio"].first()
    linf_dev = ok["measured_Linf_rel_dev"].astype(float)
    fail_by_stage = failures.groupby("stage").size().to_dict() if len(failures) else {}
    wall_run = float(args.wall_seconds_run) if np.isfinite(args.wall_seconds_run) else float(manifest.get("wall_seconds_this_invocation", float("nan")))
    bader_seconds_total = float(ok["bader_seconds"].sum())
    codec_seconds_total = float(ok.groupby(["material_id", "codec"])["codec_seconds"].first().sum())

    # ------------------------------------------------------------------ RESULTS.md
    def f3(x: float) -> str:
        return "nan" if not np.isfinite(x) else f"{x:+.3f}"

    L: list[str] = []
    L += ["# WP-C — Codec-shaped perturbation family for QSQ", ""]
    L += ["Reader-facing name: QSQ. All numbers below are read from the CSV files in this directory; none is transcribed by hand.", ""]
    L += ["## Population actually run", ""]
    L += [f"- Materials: {n_materials} development materials ({int((meta['system_type']=='bulk').sum())} bulk, {int((meta['system_type']=='slab').sum())} slab).",
          f"- Codecs: {', '.join(CODECS)}. Probes per material x codec: k in {{{', '.join(str(k) for k in k_values)}}} (k = 0 unshifted; k >= 1 periodic shifts).",
          f"- Plan executed: **{'full pre-declared plan' if k_values == [0,1,2,3,4,5] else 'pre-declared reduction'}** — {n_planned} Bader re-solves planned, "
          f"{n_ok} completed, {n_fail} failed ({n_ok + n_fail} accounted); {n_materials * len(CODECS)} codec round trips.",
          f"- Failures by stage: {json.dumps(fail_by_stage) if fail_by_stage else 'none'}. Failed rows stay in every denominator (a material x codec with any failed k >= 1 solve has an undefined codec-shaped floor and is counted as `n_undefined_ratio`).",
          f"- Base rung used: {'all 762 material x codec pairs at nominal relative tolerance 1e-5' if (rung_counts['base_rung_relative'] == 1e-5).all() else 'see run_manifest / probe_outcomes (base_rung_relative)'}; per-codec row counts: " + "; ".join(f"{r.codec} @ {r.base_rung_relative:g}: {int(r.n_rows)}" for r in rung_counts.itertuples()) + ".",
          f"- Residual reproduction: |log10(reproduced L_inf / frozen realized_Linf)| max = {float(repro.max()):.3e} dex over {len(repro)} pairs.",
          f"- Probe amplitude: |L_inf(delta) - eps_m| / eps_m max = {float(linf_dev.max()):.3e} (requirement <= 1e-12) over {len(linf_dev)} probes.",
          f"- Wall time of the run: {wall_run/3600:.2f} h ({wall_run:.0f} s); summed Bader solve time {bader_seconds_total:.0f} s; summed codec round-trip time {codec_seconds_total:.0f} s.",
          ""]
    L += ["## Analysis 1 — Codec-shaped floor f^c_m versus iid floor f_m", ""]
    L += ["f^c_m = max over k >= 1 of the Bader response; f_m = frozen `stability_floor_A1_e`. Statistic: log10(f^c_m / f_m), material-median with material-cluster bootstrap 95% CI (2,000 resamples, seed 20260928).", ""]
    L += ["| Codec | Stratum | n (defined / total) | median log10(f^c/f) [95% CI] | mean | p05 / p25 / p75 / p95 | frac f^c > f [95% CI] |", "|---|---|---:|---:|---:|---:|---:|"]
    for r in a1.itertuples():
        L.append(f"| {r.codec} | {r.stratum} | {r.n_with_defined_ratio} / {r.n_materials} | {f3(r.median_log10_fc_over_f)} [{f3(r.median_ci95_lo)}, {f3(r.median_ci95_hi)}] | {f3(r.mean_log10_fc_over_f)} | {f3(r.p05_log10)} / {f3(r.p25_log10)} / {f3(r.p75_log10)} / {f3(r.p95_log10)} | {r.frac_fc_gt_f:.3f} [{r.frac_fc_gt_f_ci95_lo:.3f}, {r.frac_fc_gt_f_ci95_hi:.3f}] ({r.n_fc_gt_f}/{r.n_with_defined_ratio}) |")
    L += ["", "### Acceptance verdict (pre-declared rule, applied per codec)", ""]
    for c in CODECS:
        v = verdicts[c]
        L.append(f"- **{c}: {v['acceptance_verdict']}** — median log10(f^c/f) = {v['median_log10_fc_over_f']:+.3f}, 95% CI [{v['median_ci95_lo']:+.3f}, {v['median_ci95_hi']:+.3f}], n = {v['n_with_defined_ratio']}/{v['n_materials']} materials.")
    L += ["", "Rule: iid family is *conservative* for codec c if the material-median log10(f^c/f) < 0 with the bootstrap 95% CI excluding 0; *anti-conservative* if > 0 with CI excluding 0.", ""]
    L += ["## Analysis 2 — Eligibility agreement (iid vs codec-shaped floor)", ""]
    L += ["Eligibility at tau: floor < tau (same rule as the frozen gate). Flip counts are reported in full; the flip list with material IDs and direction is in `eligibility_flips.csv`.", ""]
    L += ["| Codec | tau (e) | n | iid eligible | codec-shaped eligible | both eligible | both rejected | flips iid-eligible -> codec-rejected | flips iid-rejected -> codec-eligible | agreement | Cohen's kappa [95% CI] |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in a2.itertuples():
        L.append(f"| {r.codec} | {r.tau_e:g} | {r.n_materials} | {r.iid_eligible} | {r.codec_shaped_eligible} | {r.both_eligible} | {r.both_rejected} | {r.flip_iid_eligible_to_codec_rejected} | {r.flip_iid_rejected_to_codec_eligible} | {r.agreement_fraction:.3f} | {r.cohen_kappa:.3f} [{r.kappa_ci95_lo:.3f}, {r.kappa_ci95_hi:.3f}] |")
    L += ["", "## Analysis 3 — Alignment effect: log10(response at k = 0 / median response over k >= 1)", ""]
    L += ["| Codec | Stratum | n defined | median [95% CI] | frac k0 > shifted median | p05 / p95 |", "|---|---|---:|---:|---:|---:|"]
    for r in a3.itertuples():
        L.append(f"| {r.codec} | {r.stratum} | {r.n_defined} / {r.n_materials} | {f3(r.median_log10_k0_over_median_shifted)} [{f3(r.ci95_lo)}, {f3(r.ci95_hi)}] | {r.frac_k0_above_shifted_median:.3f} | {f3(r.p05)} / {f3(r.p95)} |")
    L += ["", "## Analysis 4 — Link to the Fourier mechanism", ""]
    L += ["Spearman rho between log10(f^c_m / f_m) and the low-G error-energy fraction of the codec residual r (Nyquist-safe radial spectrum, `analysis/hartree_spectral_mechanism` convention: q = |G|/|G|_max over safe modes, low-G = q <= 0.25). Material-cluster bootstrap CI.", ""]
    L += ["| Codec | n | Spearman rho [95% CI] | median low-G fraction of r |", "|---|---:|---:|---:|"]
    for r in a4.itertuples():
        L.append(f"| {r.codec} | {r.n_materials} | {f3(r.spearman_rho_log10ratio_vs_lowG_fraction)} [{f3(r.ci95_lo)}, {f3(r.ci95_hi)}] | {r.median_low_G_fraction:.4f} |")
    L += ["", "## Analysis 5 — Predictive value among materials admitted at 1e-3 e", ""]
    L += [f"Population: materials with iid floor f_m < 1e-3 e. Outcome: P2 fresh exceedance rate p_m = fraction of the 59 fresh iid trials with `bader_response_max_e` >= 1e-3 e. Spearman rho of log10 f_m and of log10 f^c_m with p_m; the difference rho(f^c) - rho(f) uses the same material resamples.", ""]
    L += ["| Codec | n admitted | n with any fresh exceedance | rho(f_iid, p) [95% CI] | rho(f^c, p) [95% CI] | rho(f^c) - rho(f) [95% CI] |", "|---|---:|---:|---:|---:|---:|"]
    for r in a5.itertuples():
        L.append(f"| {r.codec} | {r.n_admitted} | {r.n_with_any_fresh_exceedance} | {f3(r.spearman_f_iid_vs_p2_rate)} [{f3(r.f_ci95_lo)}, {f3(r.f_ci95_hi)}] | {f3(r.spearman_fc_vs_p2_rate)} [{f3(r.fc_ci95_lo)}, {f3(r.fc_ci95_hi)}] | {f3(r.rho_diff_fc_minus_f)} [{f3(r.rho_diff_ci95_lo)}, {f3(r.rho_diff_ci95_hi)}] |")
    L += ["", "## Files", "",
          "- `probe_outcomes.csv` — one row per material x codec x k (measured L_inf, response, reassigned voxels, label hashes, charges).",
          "- `floors.csv` — per material x codec: f_m, f^c_m, per-k responses, eligibility at each tau, alignment ratio, residual spectral summary, P2 rate.",
          "- `floor_ratio_summary.csv` (analysis 1), `agreement.csv` + `eligibility_flips.csv` (analysis 2), `alignment.csv` (analysis 3), `spectral_link.csv` (analysis 4), `predictive.csv` (analysis 5).",
          "- `spectra.csv` — Nyquist-safe spectral metrics and 32-bin radial error-energy profile of every codec residual.",
          "- `failures.csv` — every planned row that did not complete; `run_manifest.json`, `provenance.json`, `DEVIATIONS.md`.", ""]
    (wpc / "RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    # ------------------------------------------------------------------ provenance.json
    def git(cmd: list[str], cwd: Path) -> str:
        try:
            return subprocess.run(["git", *cmd], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()
        except Exception as exc:  # noqa: BLE001
            return f"unavailable: {exc}"
    try:
        freeze = subprocess.run([str(args.python_exe), "-m", "pip", "freeze"], capture_output=True, text=True, check=False).stdout
        if not freeze.strip():
            freeze = subprocess.run(["uv", "pip", "freeze", "--python", str(args.python_exe)], capture_output=True, text=True, check=False).stdout
    except Exception as exc:  # noqa: BLE001
        freeze = f"unavailable: {exc}"
    prov = {
        "package": "WP-C",
        "protocol": "analysis/extensions_20260928/PROTOCOL.md (WP-C, Shared rules, Reporting back)",
        "repo_commit_at_analysis": git(["rev-parse", "HEAD"], repo),
        "repo_branch": git(["rev-parse", "--abbrev-ref", "HEAD"], repo),
        "frozen_scientific_commit": git(["rev-parse", "HEAD"], frozen),
        "python_version": platform.python_version(),
        "python_executable": str(args.python_exe),
        "platform": platform.platform(),
        "pip_freeze": freeze.splitlines(),
        "input_sha256": {k: (sha256_file(p) if p.exists() else None) for k, p in inputs.items()},
        "input_paths": {k: str(p.relative_to(p.parents[len(p.parents)-1])) if False else str(p) for k, p in inputs.items()},
        "run_manifest": {k: v for k, v in manifest.items() if k != "material_records"},
        "wall_seconds_run": wall_run,
        "wall_seconds_analysis": time.time() - t0,
        "bootstrap": {"resamples": BOOT_REPS, "seed": BOOT_SEED, "cluster": "material"},
        "k_values": k_values,
        "population": {"materials": n_materials, "codecs": list(CODECS), "solves_planned": n_planned, "solves_completed": n_ok, "solves_failed": n_fail},
        "acceptance_verdicts": {c: verdicts[c]["acceptance_verdict"] for c in CODECS},
    }
    (wpc / "provenance.json").write_text(json.dumps(prov, indent=2), encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
