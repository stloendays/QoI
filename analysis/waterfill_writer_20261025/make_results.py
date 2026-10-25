#!/usr/bin/env python3
"""Write results/RESULTS.md of study 1 from results/SUMMARY.json (numbers first)."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def f(v, d=2):
    return "—" if v is None else f"{v:.{d}f}"


def line(R, key, label):
    v = R.get(key)
    if not v:
        return f"| {label} | — | — | — |"
    return (f"| {label} | {f(v['median'], 3)} | {f(v['ci95'][0], 3)}–{f(v['ci95'][1], 3)} | "
            f"{v['wins']}/{v['n']} |")


def main():
    s = json.loads((HERE / "results/SUMMARY.json").read_text(encoding="utf-8"))
    R, C = s["ratios"], s["criteria"]
    out = ["# Water-filling law and the W1 writer on the law-protocol cohort — results", "",
           f"Materials analyzable {s['materials_success']}/{s['materials_checkpointed']} (failed: "
           f"{', '.join(s['failed']) or 'none'}). Every W1-family stream decoded from its bytes and certified "
           "(historical and Nyquist-safe Hartree relative RMS < tau). Ratios are medians over materials of per-material "
           "compression-ratio ratios, 95% bootstrap intervals of the median (seed 20261025, 10,000 resamples); wins = "
           "materials with ratio > 1.", "", "## Criteria", ""]
    for k, lab in (("H1_closed_form_at_optimum", "H1 closed form at the optimum (O1S/W1S <= 1.05, CI upper <= 1.08, 1e-6 and 1e-4)"),
                   ("H2_waterfill_over_truncation", "H2 water-filling over truncation (W1S > T1S in >= 90%, 1e-6 and 1e-4)"),
                   ("H3_writer_over_A3", "H3 writer over revision-10 A3 (median W1S/A3 > 1.3, CI lower > 1.2, 1e-6)"),
                   ("validity", "validity (>= 90/92 analyzable, all W1 arms certified)")):
        out.append(f"- **{lab}: {'met' if C[k]['met'] else 'not met'}.**")
    for tau in ("1e-06", "0.0001", "1e-08"):
        out += ["", f"## tau_H = {tau}", "", "| ratio (CR) | median | 95% CI | wins |", "|---|---|---|---|"]
        for a, b, lab in (("O1S", "W1S", "operational / water-filling, same writer (H1)"),
                          ("W1S", "T1S", "water-filling / truncation, same writer (H2)"),
                          ("W1S", "A3", "W1S / revision-10 operational allocation A3 (H3)"),
                          ("W1S", "A1", "W1S / revision-10 law A1"), ("W1S", "A2", "W1S / revision-10 truncation A2"),
                          ("W1S", "A6", "W1S / best pointwise codec A6"),
                          ("L1", "A1", "attribution: container + coder (L1 / A1)"),
                          ("W1", "L1", "attribution: water-filling (W1 / L1)"),
                          ("W1S", "W1", "attribution: symmetry (W1S / W1)"),
                          ("O1", "W1", "operational / water-filling without symmetry (O1 / W1)"),
                          ("O1S", "A3", "O1S / A3"), ("T1S", "A2", "T1S / A2")):
            out.append(line(R, f"{a}/{b}_{tau}_all", lab))
        out += ["", "By cohort (P1 bulk / P3b slabs):", "", "| ratio | P1 median (wins/n) | P3b median (wins/n) |",
                "|---|---|---|"]
        for a, b in (("O1S", "W1S"), ("W1S", "T1S"), ("W1S", "A3"), ("W1S", "A1"), ("W1S", "A6"), ("W1S", "W1")):
            p, q = R.get(f"{a}/{b}_{tau}_P1"), R.get(f"{a}/{b}_{tau}_P3B")
            out.append(f"| {a}/{b} | {f(p and p['median'], 3)} ({p and p['wins']}/{p and p['n']}) | "
                       f"{f(q and q['median'], 3)} ({q and q['wins']}/{q and q['n']}) |")
        out += ["", "Symmetry gain W1S/W1 by number of grid operations:", ""]
        for k in ("1", "2-8", "9-24", ">24"):
            v = R.get(f"W1S/W1_{tau}_ops{k}")
            if v:
                out.append(f"- {k} operations: median {f(v['median'], 3)} (n = {v['n']})")
    sy = s["symmetry"]
    out += ["", "## Symmetry", "", f"Materials with a symmetry group used: {sy['with_symmetry']}/{s['materials_success']}; "
            f"median group order {sy['ops_median']}; status counts {sy['status_counts']}.", "",
            "## Certified counts", "", ", ".join(f"{k} {v}" for k, v in s["certified"].items())]
    (HERE / "results/RESULTS.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
