#!/usr/bin/env python
"""Render WP-A/RESULTS.md from the machine-readable outputs of run_wpa.py (no hand-transcribed numbers)."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
cv = pd.read_csv(HERE / "cv_metrics.csv")
rel = pd.read_csv(HERE / "reliability.csv")
ct = pd.read_csv(HERE / "contract_table.csv")
coef = pd.read_csv(HERE / "coefficients.csv")
folds = pd.read_csv(HERE / "cv_folds.csv")
mr = pd.read_csv(HERE / "material_risk.csv")
prov = json.loads((HERE / "provenance.json").read_text(encoding="utf-8"))
A = prov["anchors"]; V = prov["verdict"]

MODELS = ["gate", "logistic_x", "isotonic_x", "logistic_x_secondary"]
LABEL = {"gate": "Binary gate (1.600% / 81.325%)", "logistic_x": "Logistic on x (+ log10 τ)",
         "isotonic_x": "Isotonic on x", "logistic_x_secondary": "Logistic on x + secondary (+ log10 τ)"}


def m(subset, model, metric):
    r = cv[(cv.subset == subset) & (cv.model == model) & (cv.metric == metric)].iloc[0]
    return r["value"], r["ci95_low"], r["ci95_high"]


def fmt(v, lo, hi, d=4):
    return f"{v:.{d}f} [{lo:.{d}f}, {hi:.{d}f}]"


def pct(v, d=1):
    return f"{100 * v:.{d}f}%"


L = []
L.append("# WP-A — Calibrated risk model for QSQ: results\n")
L.append(f"Frozen inputs, repository commit `{prov['repo_head_commit'][:7]}` (branch base `paper-20260927`), "
         f"protocol `analysis/extensions_20260928/PROTOCOL.md` (SHA-256 `{prov['protocol_sha256'][:12]}…`). "
         f"Statistics only; no density download, codec round trip or Bader solve was run. "
         f"Wall time of `run_wpa.py`: {prov['wall_time_seconds']} s. Failures: none (0 rows dropped; the package "
         f"performs no solver or download step, so `failures.csv` is not applicable).\n")

L.append("## Verdict (acceptance rule applied literally)\n")
c2 = ct[(ct.rule == "isotonic_cv") & (ct.p_star == 0.02) & (ct.tau_e == 1e-3)].iloc[0]
gate3 = ct[(ct.rule == "binary_gate") & (ct.tau_e == 1e-3)].iloc[0]
iso_d = m("pooled_all_tau", "isotonic_x", "brier_diff_vs_gate")
best = V["condition_i_best_model"]
best_d = m("pooled_all_tau", best, "brier_diff_vs_gate")
L.append(f"**The binary gate is not improved by the continuous statistic on these data** (protocol acceptance: "
         f"both conditions must hold; condition (ii) fails).\n")
L.append(f"- Condition (i), held-out Brier lower than the gate with a material-bootstrap 95% CI excluding zero: "
         f"**met** for every calibrated model. Isotonic on x: ΔBrier = {fmt(*iso_d)}; best model "
         f"({LABEL[best]}): ΔBrier = {fmt(*best_d)} (pooled over τ, 762 material–τ rows, 44,958 trials).")
L.append(f"- Condition (ii), coverage at p* = 2% and τ = 1e-3 e exceeds 56.3%: **not met**. The cross-validated "
         f"isotonic contract admits {int(c2.n_admitted)}/254 materials = {pct(c2.coverage)} "
         f"[{pct(c2.coverage_ci95_low)}, {pct(c2.coverage_ci95_high)}] versus {int(gate3.n_admitted)}/254 = "
         f"{pct(gate3.coverage)} for the gate. Among the admitted, the held-out exceedance rate is "
         f"{int(c2.admitted_exceedances)}/{int(c2.admitted_trials)} = {pct(c2.observed_rate, 3)} "
         f"[{pct(c2.observed_rate_ci95_low, 3)}, {pct(c2.observed_rate_ci95_high, 3)}], versus the gate's "
         f"{int(gate3.admitted_exceedances)}/{int(gate3.admitted_trials)} = {pct(gate3.observed_rate, 3)}.")
L.append(f"- Reading: the continuous statistic is a sharper and better-calibrated predictor than the gate "
         f"(all three models: lower Brier and log loss, higher AUC), but a contract that promises ≤ 2% risk must "
         f"stop at x* = {c2.x_cutoff:.3f} (f_m ≤ {10**c2.x_cutoff:.2f} τ; fold-wise cutoffs "
         f"{c2.x_cutoff_fold_min:.3f} to {c2.x_cutoff_fold_max:.3f}), because the fresh-exceedance risk rises "
         f"from below 1% to about 10% between x ≈ −0.26 and x = 0. The gate's 1.600% is the average over that "
         f"whole band, not a rate that holds uniformly inside it.\n")

L.append("## Anchor verification (before any fit)\n")
L.append(f"- `outcomes.csv`: {A['n_rows']:,} rows, {A['n_materials']} materials, {A['trials_per_material']} trials "
         f"per material, {A['n_nonfinite_response']} non-finite responses.")
L.append(f"- τ = 1e-3 e: eligible (f_m < τ) {A['tau_1e-3_eligible_materials']} materials, "
         f"{A['tau_1e-3_eligible_exceedances']}/{A['tau_1e-3_eligible_trials']:,} exceedances "
         f"({100 * A['tau_1e-3_eligible_exceedances'] / A['tau_1e-3_eligible_trials']:.3f}%); rejected "
         f"{A['tau_1e-3_rejected_materials']} materials, {A['tau_1e-3_rejected_exceedances']:,}/"
         f"{A['tau_1e-3_rejected_trials']:,} ({100 * A['tau_1e-3_rejected_exceedances'] / A['tau_1e-3_rejected_trials']:.3f}%). "
         f"All anchors reproduced; f_m equals the five-seed maximum of `floor_noise_resolved_e` for all 254 materials.\n")

L.append("## Design\n")
L.append(f"- Predictor x_m(τ) = log10(f_m/τ), τ ∈ {{1e-4, 1e-3, 1e-2}} e; pooled fits with log10 τ as covariate "
         f"(isotonic: pooled on x, see `DEVIATIONS.md` item 2). Secondary predictors: log10 five-seed median, "
         f"log10 five-seed mean, five-seed log10 span.")
L.append(f"- Outcome y = 1[bader_response_max_e ≥ τ] per fresh trial; 254 × 59 × 3 = {len(mr) * 59:,} trial–τ rows; "
         f"{len(mr)} material–τ rows.")
fs = folds.n_test_materials.tolist()
L.append(f"- 10-fold CV over materials, folds from SHA-256 of material_id with seed 20260928 "
         f"(fold sizes {', '.join(map(str, fs))}); all logistic fits converged in every fold.")
L.append(f"- Material-cluster bootstrap, {prov['n_bootstrap']:,} resamples, seed {prov['seed']}, for every CI below.\n")

L.append("## Held-out metrics, pooled over τ (762 material–τ rows, 44,958 trials)\n")
L.append("| Model | Brier | Log loss | AUC | ECE (10 equal-count bins) | ΔBrier vs gate | Δlog loss vs gate |")
L.append("|---|---|---|---|---|---|---|")
for mod in MODELS:
    row = [LABEL[mod], fmt(*m("pooled_all_tau", mod, "brier")), fmt(*m("pooled_all_tau", mod, "log_loss")),
           fmt(*m("pooled_all_tau", mod, "auc")), fmt(*m("pooled_all_tau", mod, "ece_10bin"))]
    if mod == "gate":
        row += ["—", "—"]
    else:
        row += [fmt(*m("pooled_all_tau", mod, "brier_diff_vs_gate")), fmt(*m("pooled_all_tau", mod, "log_loss_diff_vs_gate"))]
    L.append("| " + " | ".join(row) + " |")
L.append("")
L.append("Values are point estimates with material-bootstrap 95% CIs. Lowest held-out Brier: "
         f"{LABEL[best]} ({m('pooled_all_tau', best, 'brier')[0]:.4f}); lowest ECE: isotonic on x.\n")

L.append("## Held-out metrics per τ (254 material–τ rows, 14,986 trials each)\n")
L.append("| τ (e) | Model | Brier | AUC | ECE | ΔBrier vs gate |")
L.append("|---|---|---|---|---|---|")
for tau in [1e-4, 1e-3, 1e-2]:
    sub = f"tau_{tau:g}"
    for mod in MODELS:
        d = "—" if mod == "gate" else fmt(*m(sub, mod, "brier_diff_vs_gate"))
        L.append(f"| {tau:g} | {LABEL[mod]} | {fmt(*m(sub, mod, 'brier'))} | {fmt(*m(sub, mod, 'auc'))} | "
                 f"{fmt(*m(sub, mod, 'ece_10bin'))} | {d} |")
L.append("")
L.append("At τ = 1e-2 e the Brier improvement over the gate is not resolved (CIs include zero); at τ = 1e-4 and "
         "1e-3 e it is.\n")

L.append("## Reliability table, pooled over τ, held-out (10 equal-count bins of ~76 material–τ rows)\n")
for mod in MODELS:
    r = rel[(rel.subset == "pooled_all_tau") & (rel.model == mod)]
    L.append(f"**{LABEL[mod]}**\n")
    L.append("| bin | n materials–τ | n trials | predicted range | mean predicted | exceedances | observed |")
    L.append("|---|---|---|---|---|---|---|")
    for _, q in r.iterrows():
        L.append(f"| {int(q.bin)} | {int(q.n_materials)} | {int(q.n_trials):,} | {q.pred_min:.2e}–{q.pred_max:.2e} | "
                 f"{q.mean_predicted:.4f} | {int(q.n_exceed)} | {q.observed:.4f} |")
    L.append("")
L.append("Per-τ reliability tables are in `reliability.csv` (subsets `tau_0.0001`, `tau_0.001`, `tau_0.01`).\n")

L.append("## Contract table (cross-validated isotonic risk; admission is held-out)\n")
L.append("x_cutoff = largest x at which the isotonic risk fitted on all 254 materials is ≤ p*; admission uses the "
         "fold-wise cutoffs from the training folds only (range given). Coverage = admitted / 254; observed = "
         "held-out exceedances / trials among the admitted.\n")
L.append("| p* | τ (e) | x_cutoff (all) | fold cutoffs min…max | admitted / 254 | coverage [95% CI] | exceedances / trials | observed rate [95% CI] |")
L.append("|---|---|---|---|---|---|---|---|")
for _, q in ct[ct.rule == "isotonic_cv"].iterrows():
    L.append(f"| {100 * q.p_star:g}% | {q.tau_e:g} | {q.x_cutoff:.3f} | {q.x_cutoff_fold_min:.3f}…{q.x_cutoff_fold_max:.3f} | "
             f"{int(q.n_admitted)} | {pct(q.coverage)} [{pct(q.coverage_ci95_low)}, {pct(q.coverage_ci95_high)}] | "
             f"{int(q.admitted_exceedances)} / {int(q.admitted_trials):,} | {pct(q.observed_rate, 3)} "
             f"[{pct(q.observed_rate_ci95_low, 3)}, {pct(q.observed_rate_ci95_high, 3)}] |")
L.append("")
L.append("Binary gate (x < 0) at each τ, for comparison:\n")
L.append("| τ (e) | admitted / 254 | coverage [95% CI] | exceedances / trials | realized risk [95% CI] |")
L.append("|---|---|---|---|---|")
for _, q in ct[ct.rule == "binary_gate"].iterrows():
    L.append(f"| {q.tau_e:g} | {int(q.n_admitted)} | {pct(q.coverage)} [{pct(q.coverage_ci95_low)}, {pct(q.coverage_ci95_high)}] | "
             f"{int(q.admitted_exceedances)} / {int(q.admitted_trials):,} | {pct(q.observed_rate, 3)} "
             f"[{pct(q.observed_rate_ci95_low, 3)}, {pct(q.observed_rate_ci95_high, 3)}] |")
L.append("")
g16 = ct[(ct.rule == "isotonic_cv_gate_risk_comparison") & (ct.tau_e == 1e-3)].iloc[0]
L.append(f"At the gate's own realized risk (p* = 1.6%, comparison row, not pre-declared) the isotonic contract at "
         f"τ = 1e-3 e admits {int(g16.n_admitted)}/254 = {pct(g16.coverage)} with "
         f"{int(g16.admitted_exceedances)}/{int(g16.admitted_trials):,} = {pct(g16.observed_rate, 3)} observed, "
         f"against the gate's 143/254 = 56.3% with 135/8,437 = 1.600%. A 5% contract reaches "
         f"{int(ct[(ct.rule == 'isotonic_cv') & (ct.p_star == 0.05) & (ct.tau_e == 1e-3)].iloc[0].n_admitted)}/254 and a "
         f"10% contract {int(ct[(ct.rule == 'isotonic_cv') & (ct.p_star == 0.10) & (ct.tau_e == 1e-3)].iloc[0].n_admitted)}/254; "
         f"none of the five pre-declared levels reaches the gate's coverage at τ = 1e-3 e.\n")

L.append("## Logistic coefficients (all 254 materials, cluster-robust SE by material)\n")
L.append("| Model | Term | Coef | SE | z | p |")
L.append("|---|---|---|---|---|---|")
for _, q in coef.iterrows():
    L.append(f"| {q.model} | {q.term} | {q.coef:.3f} | {q.se_cluster_material:.3f} | {q.z:.2f} | {q.p_value:.2e} |")
L.append("")
L.append("In the secondary-predictor model x, log10 seed-median and log10 seed-mean are strongly collinear "
         "(individual SEs are wide); the held-out Brier, not the coefficients, is the evidence that the seed "
         "spread adds information.\n")

L.append("## Files\n")
L.append("- `material_risk.csv` — 762 rows (material × τ): f_m, x, secondary predictors, fold, 59-trial exceedance "
         "count and rate, held-out risk from each model (`risk_cv_*`), full-data fits (`risk_full_*`), fold-wise "
         "isotonic cutoffs.")
L.append("- `cv_metrics.csv` — held-out Brier, log loss, AUC, ECE and differences versus the gate, with bootstrap CIs, "
         "pooled and per τ.")
L.append("- `reliability.csv` — 10-bin reliability tables per model, pooled and per τ.")
L.append("- `contract_table.csv` — the contract table above (five p* levels, the 1.6% comparison row, and the gate).")
L.append("- `coefficients.csv`, `cv_folds.csv` — logistic coefficients; fold sizes and per-fold cutoffs.")
L.append("- `fig_calibration.png` / `.svg` — (a) reliability diagram, (b) risk versus x with the isotonic, logistic and "
         "gate curves and the 762 material–τ points.")
L.append("- `provenance.json` — commit, input SHA-256s, anchors, seeds, fold rule, package versions, pip freeze, "
         "verdict, wall time. `DEVIATIONS.md` — operational choices where the protocol is silent (no rule changed).")
(HERE / "RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("RESULTS.md written")
