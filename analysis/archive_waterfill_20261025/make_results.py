#!/usr/bin/env python3
"""Write results/RESULTS.md of study 2 from results/SUMMARY.json (numbers first)."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    s = json.loads((HERE / "results/SUMMARY.json").read_text(encoding="utf-8"))
    E, P = s["estimates"], s["paired"]

    def est(k):
        v = E.get(k)
        return "—" if not v else f"{v['R']:,.1f} ({v['ci95'][0]:,.1f}–{v['ci95'][1]:,.1f})"

    def pr(k):
        v = P.get(k)
        return "—" if not v else f"{v['ratio']:.3f} ({v['ci95'][0]:.3f}–{v['ci95'][1]:.3f})"

    out = ["# Whole-object archive under the W1 writer — results", "",
           f"Objects checkpointed {s['objects_checkpointed']}, SUCCESS {s['objects_success']} of 300. Fold reduction R of "
           "the 8.50 TB Materials Project archive (Hartree-certified complete objects), stratified expansion estimate with "
           f"95% bootstrap interval (seed {s['seed']}, {s['resamples']} resamples, paired across writers).", "",
           "| writer | tau_H = 1e-6 | tau_H = 1e-4 |", "|---|---|---|"]
    for w, lab in (("P", "P pointwise (recorded)"), ("T", "T truncation A2 (revision 10)"), ("L", "L closed-form law A1 (revision 10)"),
                   ("O", "O operational allocation A3 (revision 10)"), ("W", "W water-filling law, W1 writer, symmetry"),
                   ("Q", "Q operational allocation, W1 writer, symmetry")):
        out.append(f"| {lab} | {est(w + '_1e-06')} | {est(w + '_0.0001')} |")
    out += ["", "| paired ratio | 1e-6 | 1e-4 |", "|---|---|---|"]
    for a, b in (("W", "O"), ("W", "L"), ("W", "T"), ("W", "P"), ("Q", "O"), ("Q", "W")):
        out.append(f"| {a}/{b} | {pr(f'{a}/{b}_1e-06')} | {pr(f'{a}/{b}_0.0001')} |")
    out += ["", "Counts:", ""]
    for w in ("W", "Q"):
        for k in ("1e-06", "0.0001"):
            c = s.get(f"counts_{w}_{k}", {})
            out.append(f"- {w} {k}: eligible {c.get('eligible')}, certified {c.get('certified')}, decoded-frame m "
                       f"{c.get('m_decoded_frame')}")
    sy = s.get("symmetry", {})
    out += ["", f"Objects with a symmetry group used: {sy.get('with_symmetry')}/{sy.get('objects')}; median group order "
            f"{sy.get('ops_median')}."]
    (HERE / "results/RESULTS.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
