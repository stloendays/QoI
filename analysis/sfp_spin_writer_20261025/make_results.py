#!/usr/bin/env python3
"""results/RESULTS.md of study 3 from results/SUMMARY.json (numbers first)."""
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
    return f"| {label} | {f(v['median'])} ({f(v['ci95'][0])}–{f(v['ci95'][1])}) | {v['wins']}/{v['n']} | {f(v['min'])}–{f(v['max'])} |"


def main():
    S = json.loads((HERE / "results" / "SUMMARY.json").read_text(encoding="utf-8"))
    R, C = S["ratios"], S["criteria"]
    out = ["# Study 3 — structure-factor prediction in the water-filling writer (W2): results", "",
           f"{S['materials_success']}/{S['materials_checkpointed']} materials analyzable; failed: {S['failed'] or 'none'}.", "",
           "## Criteria", ""]
    g1 = C["G1_prediction_gain"]
    v = g1["values"]
    out.append(f"- **G1 prediction gain** cr(W2S)/cr(W1S) at 1e-6: median {f(v.get('median'))} "
               f"(95% CI {f(v['ci95'][0]) if v else '—'}–{f(v['ci95'][1]) if v else '—'}), "
               f"W2S smaller in {v.get('wins')}/{v.get('n')} — **{'met' if g1['met'] else 'not met'}**.")
    g2 = C["G2_closed_form_at_optimum_with_prediction"]
    vals = "; ".join(f"{t}: median {f(x.get('median'), 3)} (CI {f(x['ci95'][0], 3)}–{f(x['ci95'][1], 3)})"
                     for t, x in g2["values"].items() if x)
    out.append(f"- **G2 closed form at the optimum with prediction** cr(O2S)/cr(W2S): {vals} — "
               f"**{'met' if g2['met'] else 'not met'}**.")
    va = C["validity"]
    out.append(f"- **Validity:** {va['analyzable']} analyzable; all arms certified: {va['all_arms_certified']}; W1S "
               f"reproduces revision 11: {va['w1s_reproduces_rev11']} "
               f"({', '.join(f'{k}: {x['equal']}/{x['of']}' for k, x in S['reproduction'].items())}) — "
               f"**{'met' if va['met'] else 'not met'}**.")
    out += ["", "## Ratios (cr = raw bytes / stream bytes; median, 95% bootstrap CI, wins, range)", "",
            "| ratio | median (CI) | wins | range |", "|---|---|---|---|"]
    for t in ("1e-06", "0.0001"):
        for a, b in (("W2S", "W1S"), ("O2S", "W2S"), ("W2S", "A3"), ("W2S", "A1"), ("W2S", "A2"), ("W2S", "A6"),
                     ("W2", "W1S"), ("W2S", "W2")):
            for c in ("all", "P1", "P3B"):
                out.append(line(R, f"{a}/{b}_{t}_{c}", f"{a}/{b} {t} {c}"))
        for k in ("1", "2-8", "9-24", ">24"):
            out.append(line(R, f"W2S/W1S_{t}_ops{k}", f"W2S/W1S {t} symmetry operations {k}"))
    out += ["", "## Writer", "", f"- Variants chosen by W2S: {json.dumps(S['variants'])}",
            f"- Materials with a kept prediction: {S['sfp']['materials_with_prediction']}; median predicted shells "
            f"{S['sfp']['shells_median']}; median SFP block {S['sfp']['block_bytes_median']} bytes.",
            f"- Certified per arm: {json.dumps(S['certified'])}", ""]
    (HERE / "results" / "RESULTS.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("\n".join(out[:12]))


if __name__ == "__main__":
    main()
