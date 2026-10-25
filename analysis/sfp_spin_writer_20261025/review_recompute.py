#!/usr/bin/env python3
"""Independent review of study 3: recompute the per-material ratios (medians, wins, N) from results/rows.csv and the
law-protocol rows, the W1S reproduction count, and the Hartree certificates; compare with results/SUMMARY.json."""
from __future__ import annotations

import csv
import json
import statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
TAUS = (1e-6, 1e-4)


def main():
    rows = list(csv.DictReader(open(HERE / "results/rows.csv", encoding="utf-8")))
    raw, coh, cr = {}, {}, {}
    bad_cert = []
    for r in rows:
        m, t = r["material_id"], float(r["tau"])
        raw[m], coh[m] = int(r["raw_bytes"]), r["cohort"]
        if r["certified"] == "True":
            cr[(m, r["arm"], t)] = int(r["raw_bytes"]) / int(r["bytes"])
            if not (float(r["hartree_hist"]) < t and float(r["hartree_safe"]) < t):
                bad_cert.append((m, r["arm"], t))
    best = {}
    for run in ("run_P1_CONFIRMATORY", "run_P3B_CONFIRMATORY"):
        for r in csv.DictReader(open(REPO / "analysis/general_qoac_law/results" / run / "part_a_rows.csv",
                                     encoding="utf-8")):
            if r["certified"] == "True" and r["arm"] in ("A1", "A2", "A3", "A6") and r["material_id"] in raw:
                k = (r["material_id"], r["arm"], float(r["tau"]))
                best[k] = min(best.get(k, 10 ** 18), int(r["bytes"]))
    for (m, a, t), b in best.items():
        cr[(m, a, t)] = raw[m] / b
    S = json.loads((HERE / "results/SUMMARY.json").read_text(encoding="utf-8"))
    mats = sorted(raw)
    out, mism = {}, []
    for t in TAUS:
        for a, b in (("W2S", "W1S"), ("O2S", "W2S"), ("W2S", "A3"), ("W2S", "A6"), ("W2", "W1S"), ("W2S", "A1"),
                     ("W2S", "A2"), ("W2S", "W2"), ("O2S", "A3")):
            for name in ("all", "P1", "P3B"):
                v = [cr[(m, a, t)] / cr[(m, b, t)] for m in mats if (m, a, t) in cr and (m, b, t) in cr
                     and name in ("all", coh[m])]
                key = f"{a}/{b}_{t:g}_{name}"
                mine = {"median": st.median(v), "wins": sum(x > 1 for x in v), "n": len(v)}
                out[key] = mine
                s = S["ratios"][key]
                if abs(s["median"] - mine["median"]) > 1e-9 * mine["median"] or s["wins"] != mine["wins"] \
                        or s["n"] != mine["n"]:
                    mism.append(key)
    r11 = {(r["material_id"], float(r["tau"])): int(r["bytes"]) for r in
           csv.DictReader(open(REPO / "analysis/waterfill_writer_20261025/results/rows.csv", encoding="utf-8"))
           if r["arm"] == "W1S" and r["certified"] == "True"}
    rep = {}
    for t in TAUS:
        w1s = {r["material_id"]: int(r["bytes"]) for r in rows if r["arm"] == "W1S" and float(r["tau"]) == t}
        rep[f"{t:g}"] = sum(w1s[m] == r11.get((m, t)) for m in mats)
    cert = {f"{a}_{t:g}": sum((m, a, t) in cr for m in mats) for a in ("W1S", "W2S", "W2", "O2S") for t in TAUS}
    res = {"materials": len(mats), "certified": cert, "hartree_violations": bad_cert, "w1s_reproduction": rep,
           "ratio_mismatches": mism, "ratios": out}
    (HERE / "results/REVIEW_RECOMPUTE.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k != "ratios"}, indent=1))
    for k in ("W2S/W1S_1e-06_all", "W2S/W1S_0.0001_all", "O2S/W2S_1e-06_all", "O2S/W2S_0.0001_all",
              "W2S/A3_1e-06_all", "W2S/A3_0.0001_all", "W2S/A6_1e-06_all", "W2/W1S_1e-06_all", "W2/W1S_0.0001_all"):
        print(k, out[k])
    assert not mism and not bad_cert


if __name__ == "__main__":
    main()
