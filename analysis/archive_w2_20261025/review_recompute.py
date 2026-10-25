#!/usr/bin/env python3
"""Independent review of studies 4 and 5: point estimates of V, VP, W, Q, T, O, L, P at both tolerances from
results/objects.csv (L and P from the committed archive-law records) with the stratified expansion estimator, the
paired ratios, the W2M-vs-pointwise moment-stream statistics, and the density and magnetization certificates read from
the collected checkpoints; compared with results/SUMMARY.json."""
from __future__ import annotations

import argparse
import csv
import json
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
AN = HERE.parent
N_FRAME = {"D01": 41527, "D02": 41531, "D03": 41529, "D04": 41529, "D05": 41528, "D06": 41529,
           "D07": 41529, "D08": 41529, "D09": 41529, "D10a": 33105, "D10b": 6741, "D10c": 1683}
KS = ("1e-06", "0.0001")
TAU = {"1e-06": 1e-6, "0.0001": 1e-4}


def rd(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def tot(vals, strata):
    s, n = defaultdict(float), Counter(strata)
    for v, h in zip(vals, strata):
        s[h] += v
    return sum(N_FRAME[h] / n[h] * s[h] for h in s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoints", type=Path, default=AN / "server_runs_20261025c/collected/checkpoints")
    a = ap.parse_args()
    se = AN / "scope_expansion_20261022"
    har = rd(se / "archive_hartree_objects.csv")
    obj = {r["task_id"]: r for r in rd(HERE / "results/objects.csv")}
    s2 = {r["task_id"]: r for r in rd(se / "results/s2_archive_whole_object/objects_spin_store.csv")}
    dec = {"1e-06": {r["task_id"]: r for r in rd(se / "results/s2b_archive_hartree_decframe/objects.csv")},
           "0.0001": {r["task_id"]: r for r in rd(se / "results/s2c_archive_hartree_decframe_1e-4/objects.csv")},
           "P": {r["task_id"]: r for r in rd(se / "results/s2d_archive_pointwise_decframe_1e-6/objects.csv")}}

    def m_l(t, d):
        r = d.get(t)
        if r and r.get("status") == "OK" and r["m_codec_0.01"] in ("zfp", "sz3", "sperr"):
            return float(r["m_store_0.01"])
        return float(s2[t]["m_store_0.01"]) + float(s2[t]["label_atom_xz_bytes"])

    strata = [r["stratum"] for r in har]
    frame = tot([float(r["frame_bytes"]) for r in har], strata)
    stored = {}
    for k in KS:
        for w in ("V", "VP", "W", "Q", "T", "O"):
            stored[(w, k)] = [float(obj[r["task_id"]][f"{w}_{k}_stored"]) for r in har]
        stored[("L", k)] = [float(r[f"stored_L_{k}"]) + m_l(r["task_id"], dec[k]) for r in har]
    stored[("P", "1e-06")] = [float(r["stored_P_1e-06"]) + m_l(r["task_id"], dec["P"]) for r in har]
    S = json.loads((HERE / "results/SUMMARY.json").read_text(encoding="utf-8"))
    R = {f"{w}_{k}": frame / tot(v, strata) for (w, k), v in stored.items()}
    mism = [n for n, v in R.items() if abs(v / S["estimates"][n]["R"] - 1) > 1e-12]
    paired = {}
    for k in KS:
        for x, y in (("V", "W"), ("V", "O"), ("V", "Q"), ("V", "L"), ("V", "T"), ("V", "VP"), ("VP", "W"), ("V", "P")):
            if f"{y}_{k}" in R:
                paired[f"{x}/{y}_{k}"] = R[f"{x}_{k}"] / R[f"{y}_{k}"]
                if abs(paired[f"{x}/{y}_{k}"] / S["paired"][f"{x}/{y}_{k}"]["ratio"] - 1) > 1e-12:
                    mism.append(f"{x}/{y}_{k}")
    # checkpoints: certificates and the moment stream
    ck = {d: {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (a.checkpoints / d).glob("*.json")}
          for d in ("v", "trunc", "w1")}
    cert = {}
    for k in KS:
        t = TAU[k]
        for d, ws in (("v", ("V",)), ("trunc", ("T", "O")), ("w1", ("W", "Q"))):
            for w in ws:
                xs = [c["results"].get(f"{w}_{k}", {}) for c in ck[d].values() if c["status"] == "SUCCESS"]
                cd = [x for x in xs if x.get("certified")]
                viol = [x for x in cd if not (float(x["hartree_hist"]) < t and float(x["hartree_safe"]) < t)]
                cert[f"{w}_{k}_density"] = {"success": len(xs), "eligible": sum(bool(x.get("eligible")) for x in xs),
                                            "certified": len(cd), "hartree_violations": len(viol)}
                if w in ("T", "O", "W", "Q"):
                    m_ok = [x for x in xs if x.get("m_decframe_bytes") is not None]
                    cert[f"{w}_{k}_moment"] = {"decoded_frame": len(m_ok), "binary_err_ge_tau": sum(
                        float(x["m_err_binary"]) >= 1e-2 for x in m_ok)}
        vv = [c["results"][f"V_{k}"] for c in ck["v"].values() if c["status"] == "SUCCESS"]
        me = [x for x in vv if x.get("m_eligible")]
        w2m = [x for x in me if x.get("w2m_bytes") is not None]
        pw = [x for x in me if x.get("pw_bytes") is not None]
        both = [x for x in me if x.get("w2m_bytes") and x.get("pw_bytes")]
        r = [x["pw_bytes"] / x["w2m_bytes"] for x in both]
        cert[f"V_{k}_moment"] = {"m_eligible": len(me), "w2m": len(w2m), "pw": len(pw),
                                 "w2m_binary_ge_tau": sum(x["w2m_err_binary"] >= 1e-2 for x in w2m),
                                 "pw_binary_ge_tau": sum(x["pw_err_binary"] >= 1e-2 for x in pw),
                                 "w2m_max_err": max(x["w2m_err_binary"] for x in w2m),
                                 "pw_max_err": max(x["pw_err_binary"] for x in pw),
                                 "ref_map_fallback": len(me) - len(w2m),
                                 "pw_over_w2m_median": st.median(r), "w2m_wins": sum(v > 1 for v in r), "n": len(r),
                                 "w2m_bytes_median": st.median(x["w2m_bytes"] for x in both),
                                 "pw_bytes_median": st.median(x["pw_bytes"] for x in both)}
        s = S["moment_stream"][k]
        if abs(s["pw_over_w2m"]["median"] - st.median(r)) > 1e-12 or s["pw_over_w2m"]["wins"] != sum(v > 1 for v in r):
            mism.append(f"moment_stream_{k}")
    res = {"archive_bytes": frame, "estimates": R, "paired": paired, "certificates": cert, "mismatches": mism}
    (HERE / "results/REVIEW_RECOMPUTE.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=1))
    assert not mism


if __name__ == "__main__":
    main()
