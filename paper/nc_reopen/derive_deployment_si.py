#!/usr/bin/env python3
"""Supplementary Note 3.3 tables (deployment cost) from the deployment-cost run, as Markdown.

Input:  analysis/deployment_cost_20261012/results/{per_material.csv, SUMMARY.json, runners.csv}
Output: paper/nc_reopen/derived/deployment_cost_si.md

    D:/Research/CatalystForge/.venv/Scripts/python.exe paper/nc_reopen/derive_deployment_si.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "analysis" / "deployment_cost_20261012" / "results"
OUT = ROOT / "paper" / "nc_reopen" / "derived" / "deployment_cost_si.md"
COH = (("P1_CONFIRMATORY", "bulk"), ("P3B_CONFIRMATORY", "slabs"))
NAMES = {"A1": "A1 law", "A1ref": "A1 law, reference decoder", "A3": "A3 operational optimum",
         "A3ref": "A3, reference decoder", "A6": "A6 best of ZFP/SZ3/SPERR", "Q": "QPET, best of nine",
         "M2": "MGARD $s=-2$", "L_zstd": "float64 + zstd-3", "L_zlib": "float64 + zlib-6", "SRC": "archived file",
         "RAW": "raw float64"}


def g(x, d=3):
    if x != x:
        return "–"
    return f"{x:.{d}g}" if abs(x) < 1e3 else f"{x:,.0f}"


def main():
    t = pd.read_csv(RES / "per_material.csv")
    S = json.loads((RES / "SUMMARY.json").read_text(encoding="utf-8"))
    run = pd.read_csv(RES / "runners.csv")
    L = []
    for tau in (1e-4, 1e-6, 1e-8):
        L += [f"**Medians at $\\tau={tau:.0e}$, bulk / slabs**".replace("e-0", "e-").replace("1e-", "10^{-") .replace("$\\tau=10^{-4", "$\\tau=10^{-4}").replace("$\\tau=10^{-6", "$\\tau=10^{-6}").replace("$\\tau=10^{-8", "$\\tau=10^{-8}"),
              "",
              "| arm | certified | CR | stream (kB) | encode (s) | decode (ms) | decode MB/s | encode memory (× field) | decode memory (× field) | time to field 0.1 / 1 / 10 Gbit/s (ms) |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for arm in ("A1", "A1ref", "A3", "A3ref", "A6", "Q", "M2", "L_zstd", "L_zlib", "SRC", "RAW"):
            cells = {k: [] for k in ("cert", "cr", "kb", "enc", "dec", "mbs", "me", "md", "ttf")}
            for coh, _ in COH:
                s = t[(t.cohort == coh) & (t.tau == tau) & (t.arm == arm)]
                if s.empty:
                    continue
                cli = arm in ("Q", "M2")
                cells["cert"].append(f"{int((s.certified == True).sum())}/{len(s)}" if arm not in ("SRC", "RAW", "L_zstd", "L_zlib") else "–")  # noqa: E712
                cells["cr"].append(g(np.median(s.cr)))
                cells["kb"].append(g(np.median(s.bytes) / 1e3))
                cells["enc"].append(g(np.median(s.encode_s)) if s.encode_s.notna().any() else "–")
                cells["dec"].append(g(np.median(s.decode_s) * 1e3) if arm != "RAW" else "0")
                cells["mbs"].append(g(np.median(s.decode_MBps)) if arm != "RAW" else "–")
                me = s.encode_cli_mem_x if cli else s.encode_mem_x
                md = s.decode_cli_mem_x if cli else s.decode_mem_x
                cells["me"].append("n.s." if cli else (g(np.median(me), 2) if me.notna().any() else "–"))
                cells["md"].append(g(np.median(md), 2) if md.notna().any() else "–")
                cells["ttf"].append(" / ".join(g(np.median(s[f"ttf_{b}"]) * 1e3) for b in ("0.1Gbps", "1Gbps", "10Gbps")))
            L.append(f"| {NAMES[arm]} | " + " | ".join("; ".join(v) if k in ("ttf", "cert") else " / ".join(v)
                                                       for k, v in cells.items()) + " |")
        L.append("")
    # paired ratios at 1e-6
    L += ["**Paired ratios arm / A1 at $\\tau=10^{-6}$: median [95% CI]; materials in which A1 is lower**", "",
          "| arm | cohort | certified search | encode | decode | time to field 0.1 Gbit/s | 1 Gbit/s | 10 Gbit/s |",
          "|---|---|---|---|---|---|---|---|"]
    for arm in ("A3", "A6", "Q", "M2", "L_zstd", "SRC", "A1ref"):
        for coh, lab in COH:
            C = S["cohorts"][coh]["1e-06"]; n = 60 if lab == "bulk" else 32
            def cell(key):
                v = C.get(key, {}).get(arm)
                if not v:
                    return "–"
                m = v["median_ratio_vs_A1"]
                return f"{g(m[0])} [{g(m[1])}, {g(m[2])}]; {v['ref_better']}/{v['n']}"
            L.append(f"| {NAMES[arm]} | {lab} | " + " | ".join(cell(k) for k in (
                "paired_search", "paired_encode", "paired_decode", "paired_ttf_0.1Gbps", "paired_ttf_1Gbps",
                "paired_ttf_10Gbps")) + " |")
    L.append("")
    be = []
    for coh, lab in COH:
        b = S["cohorts"][coh]["1e-06"]["breakeven"]
        be.append(f"{lab}: A6 {g(b['A6']['median_breakeven_Gbps'])}, float64 + zstd-3 {g(b['L_zstd']['median_breakeven_Gbps'])}, "
                  f"raw float64 {g(b['RAW']['median_breakeven_Gbps'])} Gbit/s; A1 is both smaller and faster to decode than "
                  f"QPET in {b['Q']['A1_dominates']}/{b['Q']['n']}, MGARD in {b['M2']['A1_dominates']}/{b['M2']['n']} and "
                  f"the archived file in {b['SRC']['A1_dominates']}/{b['SRC']['n']}")
    L += ["**Break-even bandwidth at $\\tau=10^{-6}$** (median over materials; below it A1 delivers the field first): "
          + "; ".join(be) + ".", ""]
    L += ["**Runners.** " + "; ".join(f"{c} ({n})" for c, n in run.cpu.value_counts().items()) + ".", ""]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
