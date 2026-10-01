#!/usr/bin/env python3
"""Reproduce WP-H: exact sequential early-rejection QSQ."""
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = REPO / "stability" / "stability_floor_A1_per_seed.csv"
SEEDS = ("20260905", "1", "2", "3", "4")
TAUS = (1e-4, 1e-3, 1e-2)

def main():
    by = defaultdict(list)
    with SOURCE.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if not r["corpus"].startswith("dev_"):
                continue
            by[r["material_id"]].append(r)
    for rows in by.values():
        rows.sort(key=lambda r: SEEDS.index(str(r["seed"])))
        assert [str(r["seed"]) for r in rows] == list(SEEDS)

    material_rows, summary_rows = [], []
    for tau in TAUS:
        total = eligible = agreement = 0
        probes_e = probes_r = n_e = n_r = 0
        rejected_after = [0] * 5
        for mid in sorted(by):
            rows = by[mid]
            responses = [float(r["floor_noise_resolved_e"]) for r in rows]
            full_eligible = max(responses) < tau
            sequential_eligible, used, stop_seed = True, 5, ""
            for i, response in enumerate(responses):
                if response >= tau:
                    sequential_eligible, used, stop_seed = False, i + 1, SEEDS[i]
                    rejected_after[i] += 1
                    break
            total += used
            eligible += int(sequential_eligible)
            agreement += int(sequential_eligible == full_eligible)
            if full_eligible:
                probes_e += used; n_e += 1
            else:
                probes_r += used; n_r += 1
            material_rows.append({
                "material_id": mid, "domain": rows[0]["domain"], "tau_e": tau,
                "frozen_eligible": int(full_eligible),
                "sequential_eligible": int(sequential_eligible),
                "probes_used": used, "stop_seed": stop_seed,
                "max_response_e": max(responses),
            })
        mean_probe = total / len(by)
        summary_rows.append({
            "tau_e": tau, "n_materials": len(by), "n_eligible": eligible,
            "agreement": agreement, "mean_probe_solves": mean_probe,
            "mean_total_bader_solves": 1 + mean_probe,
            "probe_solve_reduction": 1 - total / (5 * len(by)),
            "total_solve_reduction": 1 - (1 + mean_probe) / 6,
            "mean_probe_solves_eligible": probes_e / n_e,
            "mean_probe_solves_rejected": probes_r / n_r,
            **{"rejected_after_seed%d" % (i + 1): rejected_after[i] for i in range(5)},
        })

    for name, rows in (("sequential_material.csv", material_rows), ("sequential_summary.csv", summary_rows)):
        with (HERE / name).open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader(); w.writerows(rows)

if __name__ == "__main__":
    main()
