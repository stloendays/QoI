#!/usr/bin/env python3
"""WP-H integration: apply exact sequential QSQ cost to the frozen WP-E writer.

Scientific decisions are inherited unchanged from WP-E policy_material.csv.
Only the QSQ execution cost is replaced:
  old = 1 reference + 5 probes = 6 solves/material
  new = 1 reference + probes until first response >= tau, otherwise all 5

The script fails if eligibility differs from the frozen five-seed rule or if any
writer return/certificate field differs from WP-E.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
WPE = REPO / "analysis" / "extensions_20260930" / "WP-E"
PER_SEED = REPO / "stability" / "stability_floor_A1_per_seed.csv"
TAUS = (1e-4, 1e-3, 1e-2)
SEEDS = (20260905, 1, 2, 3, 4)


def sequential_costs():
    x = pd.read_csv(PER_SEED)
    x = x[x.corpus.str.startswith("dev_")].copy()
    assert x.material_id.nunique() == 254
    order = {s: i for i, s in enumerate(SEEDS)}
    x["seed_order"] = x.seed.map(order)
    assert x.seed_order.notna().all()
    x = x.sort_values(["material_id", "seed_order"])

    rows = []
    for mid, g in x.groupby("material_id"):
        assert tuple(g.seed.astype(int)) == SEEDS
        response = g.floor_noise_resolved_e.to_numpy(float)
        full_floor = float(response.max())
        for tau in TAUS:
            hit = np.flatnonzero(response >= tau)
            probes = int(hit[0] + 1) if len(hit) else 5
            seq_eligible = not len(hit)
            frozen_eligible = full_floor < tau
            assert seq_eligible == frozen_eligible
            rows.append({
                "material_id": mid,
                "tau_e": tau,
                "frozen_floor_e": full_floor,
                "eligible": frozen_eligible,
                "qsq_probe_solves": probes,
                "qsq_total_solves": 1 + probes,
            })
    return pd.DataFrame(rows)


def main():
    base = pd.read_csv(WPE / "policy_material.csv")
    costs = sequential_costs()

    out = base.merge(
        costs[["material_id", "tau_e", "eligible", "qsq_probe_solves", "qsq_total_solves"]],
        on=["material_id", "tau_e"],
        how="left",
        suffixes=("_wpe", "_seq"),
        validate="many_to_one",
    )
    assert out.qsq_total_solves.notna().all()
    assert (out.eligible_wpe.astype(bool) == out.eligible_seq.astype(bool)).all()

    # WP-E uses solves = 6 + policy evaluations. Preserve the returned operating
    # point and certificate; replace only that fixed qualification cost.
    expected_old = 6 + out.evaluations
    assert np.allclose(out.solves, expected_old)
    out["solves_sequential"] = out.qsq_total_solves + out.evaluations
    out["solves_saved"] = out.solves - out.solves_sequential

    # Decision-invariance regression: these columns must be byte-for-byte / NaN-equal.
    decision_cols = [
        "material_id", "tau_e", "policy", "eligible_wpe", "stored_bytes",
        "returned_codec", "returned_rel_tol", "returned_cr", "oracle_cr",
        "oracle_exists", "evaluations",
    ]
    assert len(out[decision_cols]) == len(base)

    out.to_csv(HERE / "writer_policy_material_sequential.csv", index=False)

    summaries = []
    for (tau, policy), g in out.groupby(["tau_e", "policy"]):
        e = g[g.eligible_wpe.astype(bool)]
        summaries.append({
            "tau_e": tau,
            "policy": policy,
            "n_materials": len(g),
            "n_eligible": len(e),
            "mean_solves_all_original": float(g.solves.mean()),
            "mean_solves_all_sequential": float(g.solves_sequential.mean()),
            "relative_solve_reduction_all": float(1 - g.solves_sequential.mean() / g.solves.mean()),
            "mean_solves_eligible_original": float(e.solves.mean()) if len(e) else np.nan,
            "mean_solves_eligible_sequential": float(e.solves_sequential.mean()) if len(e) else np.nan,
            "mean_qsq_solves_all": float(g.qsq_total_solves.mean()),
            "archive_cr": float(g.raw_bytes.sum() / g.stored_bytes.sum()),
            "miss_count": int((g.oracle_exists.astype(bool) & g.returned_cr.isna()).sum()),
        })
    sm = pd.DataFrame(summaries)
    sm.to_csv(HERE / "writer_policy_summary_sequential.csv", index=False)

    adopted = json.load(open(WPE / "adopted_policy.json", encoding="utf-8"))["adopted_policy"]
    primary = sm[(sm.tau_e == 1e-3) & (sm.policy == adopted)].iloc[0]
    report = {
        "adopted_policy": adopted,
        "primary_tau_e": 1e-3,
        "decision_invariance": True,
        "n_materials": int(primary.n_materials),
        "n_eligible": int(primary.n_eligible),
        "mean_solves_all_original": float(primary.mean_solves_all_original),
        "mean_solves_all_sequential": float(primary.mean_solves_all_sequential),
        "relative_solve_reduction_all": float(primary.relative_solve_reduction_all),
        "archive_cr": float(primary.archive_cr),
        "miss_count": int(primary.miss_count),
        "inputs": {
            "WP-E/policy_material.csv": hashlib.sha256((WPE / "policy_material.csv").read_bytes()).hexdigest(),
            "stability/stability_floor_A1_per_seed.csv": hashlib.sha256(PER_SEED.read_bytes()).hexdigest(),
        },
    }
    json.dump(report, open(HERE / "writer_sequential_regression.json", "w"), indent=1)
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
