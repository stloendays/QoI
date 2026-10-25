#!/usr/bin/env python3
"""Review: recompute study 1's key ratios from rows.csv and the law-protocol rows, independently of aggregate_w1.py,
and the archive point estimates of study 2 from its objects table; compare with both SUMMARY.json files."""
from __future__ import annotations

import csv
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def law_rows():
    best = {}
    for run in ("run_P1_CONFIRMATORY", "run_P3B_CONFIRMATORY"):
        for r in csv.DictReader(open(REPO / "analysis/general_qoac_law/results" / run / "part_a_rows.csv", encoding="utf-8")):
            if r["certified"] == "True" and r["arm"] in ("A1", "A2", "A3", "A6"):
                k = (r["material_id"], r["arm"], float(r["tau"]))
                best[k] = min(best.get(k, 10 ** 18), int(r["bytes"]))
    return best


def study1():
    rows = list(csv.DictReader(open(HERE / "results/rows.csv", encoding="utf-8")))
    raw = {r["material_id"]: int(r["raw_bytes"]) for r in rows}
    nb = {(r["material_id"], r["arm"], float(r["tau"])): int(r["bytes"]) for r in rows if r["certified"] == "True"}
    bad = [r for r in rows if r["certified"] == "True" and not (float(r["hartree_hist"]) < float(r["tau"])
                                                               and float(r["hartree_safe"]) < float(r["tau"]))]
    for k, v in law_rows().items():
        if k[0] in raw:
            nb[k] = v
    summ = json.loads((HERE / "results/SUMMARY.json").read_text(encoding="utf-8"))["ratios"]
    out, worst = {}, 0.0
    for tau in (1e-6, 1e-4):
        for a, b in (("O1S", "W1S"), ("W1S", "T1S"), ("W1S", "A3"), ("W1S", "A1"), ("W1S", "A6"), ("L1", "A1"),
                     ("W1", "L1"), ("W1S", "W1")):
            v = [nb[(m, b, tau)] / nb[(m, a, tau)] for m in sorted(raw) if (m, a, tau) in nb and (m, b, tau) in nb]
            med = statistics.median(v)            # CR_a / CR_b = bytes_b / bytes_a
            key = f"{a}/{b}_{tau:g}_all"
            ref = summ[key]["median"]
            worst = max(worst, abs(med - ref) / ref)
            out[key] = {"median": med, "n": len(v), "wins": sum(x > 1 for x in v), "summary": ref}
    return out, worst, len(bad)


def study2():
    sys.path.insert(0, str(REPO / "analysis/archive_waterfill_20261025"))
    import run_archive_w1 as A
    se = REPO / "analysis/scope_expansion_20261022"
    har = A.RAT._read(se / "archive_hartree_objects.csv")
    s2 = {r["task_id"]: r for r in A.RAT._read(se / "results/s2_archive_whole_object/objects_spin_store.csv")}
    obj = {r["task_id"]: r for r in A.RAT._read(REPO / "analysis/archive_waterfill_20261025/results/objects.csv")}
    summ = json.loads((REPO / "analysis/archive_waterfill_20261025/results/SUMMARY.json").read_text(encoding="utf-8"))
    out, worst = {}, 0.0
    for w in ("W", "Q"):
        for k in ("1e-06", "0.0001"):
            num = den = 0.0
            for h, n in A.RAT.N_FRAME.items():
                rs = [r for r in har if r["stratum"] == h]
                js = sum(float(r["frame_bytes"]) for r in rs) / len(rs)
                st = []
                for r in rs:
                    o = obj[r["task_id"]]
                    if o["status"] != "SUCCESS":
                        st.append(float(r["frame_bytes"]))
                        continue
                    mb = o[f"{w}_{k}_m_bytes"]
                    m = float(mb) if mb not in ("", "None") else float(s2[r["task_id"]]["m_store_0.01"]) + float(
                        s2[r["task_id"]]["label_atom_xz_bytes"])
                    st.append(float(o[f"{w}_{k}_rho_bytes"]) + m)
                num += n * js
                den += n * sum(st) / len(st)
            R = num / den
            ref = summ["estimates"][f"{w}_{k}"]["R"]
            worst = max(worst, abs(R - ref) / ref)
            out[f"{w}_{k}"] = {"R": R, "summary": ref}
    return out, worst


if __name__ == "__main__":
    r1, w1, bad = study1()
    r2, w2 = study2()
    print(json.dumps({"study1": r1, "study1_max_rel_diff": w1, "study1_certificate_violations": bad,
                      "study2": r2, "study2_max_rel_diff": w2}, indent=1))
    sys.exit(0 if w1 < 1e-9 and w2 < 1e-9 and bad == 0 else 1)
