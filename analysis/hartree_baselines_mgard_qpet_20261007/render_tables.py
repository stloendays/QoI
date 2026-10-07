#!/usr/bin/env python3
"""Format the RESULTS.md tables. Statistics are copied from results/*/SUMMARY.json as written by aggregate_mq.py
(nothing is recomputed). The failure tables tabulate results/run_*/failures.csv by configuration and return code."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ARMS = ("A1", "A2", "A3", "A6", "M2", "Mbest", "Q")
SUB = ("M_s=inf", "M_s=0", "M_s=-1", "M_s=-2", "Q_hpez", "Q_sperr", "Q_sz3")
QCFG = [f"Q_{h}_b{b}" for h in ("hpez", "sperr", "sz3") for b in (4, 8, 16)]
RATIOS = ("A1_over_M2", "A1_over_Mbest", "A1_over_Q", "A3_over_M2", "A3_over_Q")
LABEL = {"1e-06": "1e-6 (primary)", "0.0001": "1e-4", "1e-08": "1e-8"}
COH = {"P1_CONFIRMATORY": "P1 (60 MP bulk)", "P3B_CONFIRMATORY": "P3b (32 NOMAD slabs)"}


def f(x):
    return "—" if x is None else (f"{x:.3g}" if abs(x) < 1000 else f"{x:.0f}")


def stats_tables(s) -> list[str]:
    out = []
    for tau in ("1e-06", "0.0001", "1e-08"):
        out.append(f"\n### τ = {LABEL[tau]}\n")
        for c, lab in COH.items():
            t = s[c][f"tau_{tau}"]
            out.append(f"\n#### {lab}\n")
            out.append("| | " + " | ".join(a.replace("Mbest", "M-best") for a in ARMS) + " |")
            out.append("|---|" + "---|" * len(ARMS))
            out.append("| median certified CR | " + " | ".join(f(t["median_cr"][a]["median_cr"]) for a in ARMS) + " |")
            out.append("| n certified | " + " | ".join(str(t["median_cr"][a]["n_certified"]) for a in ARMS) + " |")
            out.append("")
            out.append("| ratio | median | 95% CI | wins / n both certified | baseline never certified | wins incl. never certified | min | max |")
            out.append("|---|---|---|---|---|---|---|---|")
            for r in RATIOS:
                d = t["ratios"][r]
                name = r.replace("_over_", "/").replace("Mbest", "M-best")
                if d.get("M2_infeasible"):
                    out.append(f"| {name} | M2 infeasible | | | | | | |"); continue
                ci = d["ci95"]
                out.append(f"| {name} | {f(d['median'])} | {'—' if ci is None else f'{ci[0]:.3g}–{ci[1]:.3g}'} | "
                           f"{d['wins']} / {d['n_both_certified']} | {d['baseline_never_certified']} | "
                           f"{d['wins_incl_never_certified']} | {f(d['min'])} | {f(d['max'])} |")
            out.append("")
            out.append("Sub-arms, median certified CR (n): " + "; ".join(
                f"{a} {f(t['median_cr'][a]['median_cr'])} ({t['median_cr'][a]['n_certified']})" for a in SUB) + ".")
            out.append("")
            out.append("QPET configurations, median certified CR (n): " + "; ".join(
                f"{a} {f(t['median_cr'][a]['median_cr'])} ({t['median_cr'][a]['n_certified']})" for a in QCFG) + ".")
    return out


def failure_tables(s) -> list[str]:
    out = []
    for c, lab in COH.items():
        p = HERE / "results" / f"run_{c}" / "failures.csv"
        fl = pd.read_csv(p) if p.exists() and p.stat().st_size > 2 else pd.DataFrame(columns=["config", "error", "material_id"])
        fl["rc"] = fl.error.astype(str).str.extract(r"rc=(-?\d+)")[0].fillna("other")
        out.append(f"\n#### {lab}\n")
        out.append("| configuration | failed evaluations | rc −6 | rc −11 | rc −9 | other | materials affected |")
        out.append("|---|---|---|---|---|---|---|")
        for cfg, g in fl.groupby("config"):
            n = g.rc.value_counts()
            out.append(f"| {cfg} | {len(g)} | {n.get('-6', 0)} | {n.get('-11', 0)} | {n.get('-9', 0)} | "
                       f"{len(g) - n.get('-6', 0) - n.get('-11', 0) - n.get('-9', 0)} | {g.material_id.nunique()} |")
        ft = s[c]["failures_and_wall_time"]
        out.append("")
        out.append("| arm | evaluations | failed evaluations | materials with failed evaluations | searches | "
                   "searches, lower bound raised | searches, codec never executed | search wall time per material, "
                   "median s (τ = 1e-6 / 1e-4 / 1e-8) | codec + certificate h |")
        out.append("|---|---|---|---|---|---|---|---|---|")
        for arm in ("M2", "Mbest", "Q"):
            d = ft[arm]; w = d["search_wall_time"]
            out.append(f"| {arm.replace('Mbest', 'M-best')} | {d['evaluations']} | {d['failed_evaluations']} | "
                       f"{d['materials_with_failed_evaluations']} | {d['searches']} | {d['searches_lower_bound_raised']} | "
                       f"{d['searches_codec_never_executed']} | "
                       + " / ".join(f"{w[k]['median_seconds_per_material']:.0f}" for k in ("tau_1e-06", "tau_0.0001", "tau_1e-08"))
                       + f" | {d['codec_plus_certificate_hours']:.2f} |")
        out.append("")
        out.append(f"Material-level failures: {len(ft['material_level_failures'])}.")
    return out


def main():
    s = {c: json.loads((HERE / "results" / f"run_{c}" / "SUMMARY.json").read_text(encoding="utf-8")) for c in COH}
    what = sys.argv[1] if len(sys.argv) > 1 else "stats"
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(stats_tables(s) if what == "stats" else failure_tables(s)))


if __name__ == "__main__":
    sys.exit(main())
