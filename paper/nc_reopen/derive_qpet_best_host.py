#!/usr/bin/env python3
"""Best QPET host per material and tolerance, from the committed baseline results (SI 5.1, input precision).

Reads analysis/hartree_baselines_mgard_qpet_20261007/results/run_{P1,P3B}_CONFIRMATORY/material.csv and writes
paper/nc_reopen/derived/qpet_best_host.csv. The SPERR host reads float64; the hpez program (SZ3 and HPEZ hosts)
reads float32. Run from the repository root.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "analysis/hartree_baselines_mgard_qpet_20261007/results"
HOSTS = {"Q_sperr": "sperr", "Q_sz3": "sz3", "Q_hpez": "hpez"}

rows = []
for cohort in ("P1", "P3B"):
    d = pd.read_csv(RES / f"run_{cohort}_CONFIRMATORY/material.csv")
    for _, r in d.iterrows():
        best = max(HOSTS, key=lambda c: r[c])
        rows.append({"cohort": cohort, "material_id": r["material_id"], "tau": r["tau"],
                     "best_host": HOSTS[best], "best_host_float64": best == "Q_sperr",
                     "Q": r["Q"], "Q_sperr": r["Q_sperr"], "A1": r["A1"],
                     "A1_over_Q": r["A1"] / r["Q"], "A1_over_Q_sperr": r["A1"] / r["Q_sperr"]})
out = pd.DataFrame(rows)
dst = ROOT / "paper/nc_reopen/derived/qpet_best_host.csv"
out.to_csv(dst, index=False, lineterminator="\n")
s = out.groupby(["cohort", "tau"]).agg(n=("material_id", "size"),
                                       n_best_float64=("best_host_float64", "sum"),
                                       n_best_hpez=("best_host", lambda x: int((x == "hpez").sum())),
                                       median_A1_over_Q=("A1_over_Q", "median"),
                                       median_A1_over_Q_sperr=("A1_over_Q_sperr", "median"))
print(s.to_string())
