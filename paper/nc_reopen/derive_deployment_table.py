#!/usr/bin/env python3
"""Main-text Table 2 (deployment cost at Hartree tolerance 1e-6) from the deployment-cost run.

Input:  analysis/deployment_cost_20261012/results/per_material.csv and SUMMARY.json (run 38212826078)
Output: paper/nc_reopen/derived/deployment_cost_table.csv (medians per cohort; paired ratios against A1)

    D:/Research/CatalystForge/.venv/Scripts/python.exe paper/nc_reopen/derive_deployment_table.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "analysis" / "deployment_cost_20261012" / "results"
OUT = ROOT / "paper" / "nc_reopen" / "derived" / "deployment_cost_table.csv"
ARMS = ["A1", "A3", "A6", "Q", "M2", "SRC", "L_zstd", "A1ref"]


def main():
    t = pd.read_csv(RES / "per_material.csv")
    S = json.loads((RES / "SUMMARY.json").read_text(encoding="utf-8"))
    rows = []
    for coh, label in (("P1_CONFIRMATORY", "bulk"), ("P3B_CONFIRMATORY", "slab")):
        s = t[(t.cohort == coh) & (t.tau == 1e-6)]
        C = S["cohorts"][coh]["1e-06"]
        for arm in ARMS:
            g = s[s.arm == arm]
            mem = g.decode_cli_mem_x if arm in ("M2", "Q") else g.decode_mem_x
            r = {"cohort": label, "arm": arm, "n": len(g),
                 "certified": int((g.certified == True).sum()) if arm not in ("SRC", "L_zstd") else "",  # noqa: E712
                 "cr": np.median(g.cr), "kB": np.median(g.bytes) / 1e3,
                 "search_s": np.median(g.search_s) if g.search_s.notna().any() else np.nan,
                 "encode_ms": np.median(g.encode_s) * 1e3 if g.encode_s.notna().any() else np.nan,
                 "decode_ms": np.median(g.decode_s) * 1e3, "decode_MBps": np.median(g.decode_MBps),
                 "decode_mem_x": np.median(mem) if mem.notna().any() else np.nan,
                 "ttf_1Gbps_ms": np.median(g["ttf_1Gbps"]) * 1e3, "ttf_0.1Gbps_ms": np.median(g["ttf_0.1Gbps"]) * 1e3}
            for key, col in (("paired_search", "search_vs_A1"), ("paired_decode", "decode_vs_A1"),
                             ("paired_ttf_1Gbps", "ttf1_vs_A1"), ("paired_ttf_0.1Gbps", "ttf01_vs_A1")):
                v = C.get(key, {}).get(arm)
                if v:
                    m = v["median_ratio_vs_A1"]
                    r[col], r[col + "_lo"], r[col + "_hi"], r[col + "_A1_lower"] = m[0], m[1], m[2], v["ref_better"]
            pb = s.pivot_table(index="material_id", columns="arm", values="bytes")
            if arm in pb and arm != "A1":
                r["bytes_vs_A1"] = float(np.median(pb[arm] / pb["A1"]))
            if arm == "A1":
                q = s.pivot_table(index="material_id", columns="arm", values="search_s")
                r["A1_least_search"] = int((q["A1"] < q[["A3", "A6", "M2", "Q"]].min(axis=1)).sum())
            rows.append(r)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False, float_format="%.6g")
    print(pd.DataFrame(rows).to_string())


if __name__ == "__main__":
    main()
