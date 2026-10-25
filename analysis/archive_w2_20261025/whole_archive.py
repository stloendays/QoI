#!/usr/bin/env python3
"""Whole-object archive estimates for every writer on one footing: L and P (committed records, one decoded density
per run, unaffected by the partition defect), T and O (revision 10's writers) and W and Q (revision 11's writers)
from the partition-fix rerun, V and VP (this study). Stored bytes, failure rule, moment fallback (reference atom map
plus reference-frame m of S2), stratified expansion estimator and paired bootstrap (seed 20261012, 2,000 resamples)
are those of `run_archive_truncation.aggregate`. Also: the moment-stream comparison W2M vs pointwise on the same
partition, the Porod exponents, the W2S variants, and the change of T, O, W, Q against their committed estimates.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
AN = HERE.parent
_spec = importlib.util.spec_from_file_location("run_archive_truncation", AN / "archive_truncation_20261024" /
                                               "run_archive_truncation.py")
RAT = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RAT)
tkey, TAUS_H = RAT.tkey, RAT.TAUS_H
COMMITTED = {"T": AN / "archive_truncation_20261024" / "results" / "SUMMARY.json",
             "O": AN / "archive_truncation_20261024" / "results" / "SUMMARY.json",
             "W": AN / "archive_waterfill_20261025" / "results" / "SUMMARY.json",
             "Q": AN / "archive_waterfill_20261025" / "results" / "SUMMARY.json"}


def _ck(d: Path) -> dict:
    out = {}
    for p in sorted(d.glob("*.json")):
        x = json.loads(p.read_text(encoding="utf-8"))
        out[x["task_id"]] = x
    return out


def med_ci(v, rng, nboot=10000):
    v = np.asarray(v, float)
    b = np.median(rng.choice(v, size=(nboot, v.size), replace=True), axis=1)
    return {"median": float(np.median(v)), "ci95": [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))],
            "n": int(v.size), "wins": int(np.sum(v > 1.0)), "ties": int(np.sum(v == 1.0))}


def aggregate(ck_v: Path, ck_trunc: Path, ck_w1: Path, repo: Path, out: Path) -> dict:
    se = repo / "analysis" / "scope_expansion_20261022"
    har = RAT._read(se / "archive_hartree_objects.csv")
    s2 = {r["task_id"]: r for r in RAT._read(se / "results" / "s2_archive_whole_object" / "objects_spin_store.csv")}
    s2b = {r["task_id"]: r for r in RAT._read(se / "results" / "s2b_archive_hartree_decframe" / "objects.csv")}
    s2c = {r["task_id"]: r for r in RAT._read(se / "results" / "s2c_archive_hartree_decframe_1e-4" / "objects.csv")}
    s2d = {r["task_id"]: r for r in RAT._read(se / "results" / "s2d_archive_pointwise_decframe_1e-6" / "objects.csv")}
    cks = {"V": _ck(ck_v), "VP": None, "T": _ck(ck_trunc), "O": None, "W": _ck(ck_w1), "Q": None}
    cks["VP"], cks["O"], cks["Q"] = cks["V"], cks["T"], cks["W"]
    assert len(har) == 300
    strata = np.array([r["stratum"] for r in har])
    idx = {h: np.flatnonzero(strata == h) for h in RAT.N_FRAME}
    js = np.array([float(r["frame_bytes"]) for r in har])

    def m_map(t):
        r = s2[t]
        return float(r["m_store_0.01"]) + float(r["label_atom_xz_bytes"])

    def m_hybrid(dec_row):
        return lambda t: (float(dec_row[t]["m_store_0.01"]) if dec_row.get(t, {}).get("status") == "OK"
                          and dec_row[t]["m_codec_0.01"] in ("zfp", "sz3", "sperr") else m_map(t))

    stored, failed, mshare = {}, {}, {}
    for tau in TAUS_H:
        k = tkey(tau)
        mL = m_hybrid(s2b if tau == 1e-6 else s2c)
        stored[("L", k)] = np.array([float(r[f"stored_L_{k}"]) + mL(r["task_id"]) for r in har])
        if tau == 1e-6:
            mP = m_hybrid(s2d)
            stored[("P", k)] = np.array([float(r[f"stored_P_{k}"]) + mP(r["task_id"]) for r in har])
        for w, ck in cks.items():
            vals, ms, nf = [], [], 0
            for r in har:
                c = ck.get(r["task_id"])
                if c is None or c["status"] != "SUCCESS" or f"{w}_{k}" not in c["results"]:
                    vals.append(float(r["frame_bytes"]))
                    ms.append(0.0)
                    nf += 1
                    continue
                x = c["results"][f"{w}_{k}"]
                m_b = x["m_decframe_bytes"] if x["m_decframe_bytes"] is not None else m_map(r["task_id"])
                vals.append(float(x["rho_bytes"]) + float(m_b))
                ms.append(float(m_b))
            stored[(w, k)] = np.array(vals)
            mshare[(w, k)] = RAT._tot(np.array(ms), idx) / RAT._tot(stored[(w, k)], idx)
            failed[(w, k)] = nf
    names = sorted(stored)
    point = {n: RAT._tot(js, idx) / RAT._tot(stored[n], idx) for n in names}
    rng = np.random.default_rng(RAT.SEED)
    boot = {n: np.empty(RAT.NBOOT) for n in names}
    for b in range(RAT.NBOOT):
        ib = {h: rng.choice(ix, size=len(ix), replace=True) for h, ix in idx.items()}
        tj = RAT._tot(js, ib)
        for n in names:
            boot[n][b] = tj / RAT._tot(stored[n], ib)
    ci = lambda a: [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]  # noqa: E731
    summ = {"seed": RAT.SEED, "resamples": RAT.NBOOT, "tau_mu_muB": RAT.TAU_MU, "archive_bytes": RAT._tot(js, idx),
            "objects_success": {w: sum(c["status"] == "SUCCESS" for c in ck.values()) for w, ck in cks.items()},
            "estimates": {}, "paired": {}, "m_share": {}, "committed": {}, "moment_stream": {}, "variants": {}}
    for (w, k) in names:
        summ["estimates"][f"{w}_{k}"] = {"R": point[(w, k)], "ci95": ci(boot[(w, k)]),
                                         "stored_bytes": RAT._tot(stored[(w, k)], idx),
                                         "objects_failed_as_json": failed.get((w, k), 0)}
        if (w, k) in mshare:
            summ["m_share"][f"{w}_{k}"] = mshare[(w, k)]
    for k in (tkey(t) for t in TAUS_H):
        for a, bb in (("V", "W"), ("V", "O"), ("V", "L"), ("V", "T"), ("V", "P"), ("V", "Q"), ("VP", "W"),
                      ("V", "VP"), ("W", "O"), ("W", "L"), ("W", "T"), ("O", "L"), ("O", "T"), ("L", "T"),
                      ("W", "P"), ("O", "P"), ("Q", "W")):
            if (a, k) in point and (bb, k) in point:
                summ["paired"][f"{a}/{bb}_{k}"] = {"ratio": point[(a, k)] / point[(bb, k)],
                                                   "ci95": ci(boot[(a, k)] / boot[(bb, k)])}
        for w in ("T", "O", "W", "Q"):
            try:
                old = json.loads(COMMITTED[w].read_text(encoding="utf-8"))["estimates"][f"{w}_{k}"]
            except (KeyError, FileNotFoundError):
                continue
            if (w, k) in point:
                summ["committed"][f"{w}_{k}"] = {"committed_R": old["R"], "fixed_R": point[(w, k)],
                                                 "change": point[(w, k)] / old["R"] - 1.0}
        # moment stream: W2M vs pointwise on the same decoded partition (m-eligible, both certified)
        vv = [c["results"][f"V_{k}"] for c in cks["V"].values() if c["status"] == "SUCCESS"]
        both = [x for x in vv if x.get("m_eligible") and x.get("w2m_bytes") and x.get("pw_bytes")]
        summ["moment_stream"][k] = {
            "m_eligible": sum(bool(x.get("m_eligible")) for x in vv),
            "w2m_certified": sum(x.get("w2m_bytes") is not None for x in vv if x.get("m_eligible")),
            "pw_certified": sum(x.get("pw_bytes") is not None for x in vv if x.get("m_eligible")),
            "pw_over_w2m": med_ci([x["pw_bytes"] / x["w2m_bytes"] for x in both], np.random.default_rng(RAT.SEED))
            if both else None,
            "w2m_bytes_median": float(np.median([x["w2m_bytes"] for x in both])) if both else None,
            "pw_bytes_median": float(np.median([x["pw_bytes"] for x in both])) if both else None}
        vr = [x.get("variant") for x in vv if x.get("certified")]
        summ["variants"][k] = {v: vr.count(v) for v in sorted(set(vr))}
        rr = [x["w1s_rho_bytes"] / x["rho_bytes"] for x in vv if x.get("certified") and x.get("w1s_rho_bytes")]
        summ["variants"][k]["w1s_over_w2s_rho"] = med_ci(rr, np.random.default_rng(RAT.SEED)) if rr else None
    po = [c.get("porod_exponent") for c in cks["V"].values() if c.get("porod_exponent") is not None]
    summ["porod_exponent"] = {"n": len(po), "median": float(np.median(po)) if po else None,
                              "iqr": [float(np.percentile(po, 25)), float(np.percentile(po, 75))] if po else None}
    out.mkdir(parents=True, exist_ok=True)
    with (out / "objects.csv").open("w", newline="", encoding="utf-8") as fh:
        cols = ["task_id", "stratum", "status", "npoints", "spacegroup", "ops", "m_ops", "porod_exponent", "floor_muB"]
        for t in TAUS_H:
            k = tkey(t)
            cols += [f"V_{k}_{f}" for f in ("certified", "rho_bytes", "variant", "w1s_rho_bytes", "w2m_bytes",
                                            "pw_bytes", "pw_codec", "w2m_err_binary", "pw_err_binary")]
            cols += [f"{w}_{k}_stored" for w in ("V", "VP", "W", "Q", "T", "O") if (w, k) in stored]
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        for i, r in enumerate(har):
            c = cks["V"].get(r["task_id"], {"status": "MISSING", "results": {}})
            row = {"task_id": r["task_id"], "stratum": r["stratum"], "status": c["status"], "npoints": c.get("npoints"),
                   "spacegroup": c.get("symmetry", {}).get("spacegroup"), "ops": c.get("symmetry", {}).get("ops"),
                   "m_ops": c.get("m_symmetry", {}).get("ops"), "porod_exponent": c.get("porod_exponent"),
                   "floor_muB": c.get("floor_muB")}
            for t in TAUS_H:
                k = tkey(t)
                x = c["results"].get(f"V_{k}", {})
                for f in ("certified", "rho_bytes", "variant", "w1s_rho_bytes", "w2m_bytes", "pw_bytes", "pw_codec",
                          "w2m_err_binary", "pw_err_binary"):
                    row[f"V_{k}_{f}"] = x.get(f)
                for w in ("V", "VP", "W", "Q", "T", "O"):
                    if (w, k) in stored:
                        row[f"{w}_{k}_stored"] = stored[(w, k)][i]
            wr.writerow(row)
    (out / "SUMMARY.json").write_text(json.dumps(summ, indent=1) + "\n", encoding="utf-8")
    return summ


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--checkpoints-v", type=Path, required=True)
    ap.add_argument("--checkpoints-trunc", type=Path, required=True)
    ap.add_argument("--checkpoints-w1", type=Path, required=True)
    ap.add_argument("--repo-root", type=Path, default=HERE.parents[1])
    ap.add_argument("--out", type=Path, default=HERE / "results")
    a = ap.parse_args()
    s = aggregate(a.checkpoints_v, a.checkpoints_trunc, a.checkpoints_w1, a.repo_root.resolve(), a.out)
    print(json.dumps({k: s[k] for k in ("estimates", "paired", "committed", "moment_stream")}, indent=1))
