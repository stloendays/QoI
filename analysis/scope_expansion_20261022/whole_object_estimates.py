#!/usr/bin/env python3
"""Whole-object counterparts of every archive number in the rev5 manuscript.

Inputs are committed per-object tables only:
  wpf_objects_completed_v2.csv            (Bader contract; published WP-F stores)
  archive_hartree_objects.csv             (Hartree contract; published L/P stores)
  results/s0b_archive_spin_bytes/objects_spin_bytes.csv   (lossless sizes of rho and m)
  results/s2_archive_whole_object/objects_spin_store.csv  (m under the moment contract, reference frame; atom map)
  results/s2b_archive_hartree_decframe/objects.csv        (m on the law's decoded partition, tau_H = 1e-6)

m policy per object ("whole object"):
  Bader rows       : m at tau_mu = 1e-2 mu_B, reference-frame certificate + atom map (the Bader-certified
                     rho' composes in the decoded frame in 60/62 engineering pairs, S3 v2, but the archive run
                     certified in the reference frame, so the map is carried: conservative).
  Hartree law 1e-6 : m on the law's decoded partition at 1e-2 mu_B (S2b), no map.
  other Hartree    : reference-frame m + atom map (conservative), since decoded-frame m was measured at 1e-6 only.
Failed pipeline objects keep their current file (which already contains m): no m bytes added.
Frozen estimator; bootstrap 2,000 within-stratum resamples with the protocol seeds (Bader 20260930,
Hartree 20261012). Writes results/whole_object_estimates/{TABLE.md, estimates.json}.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
N_FRAME = {"D01": 41527, "D02": 41531, "D03": 41529, "D04": 41529, "D05": 41528, "D06": 41529,
           "D07": 41529, "D08": 41529, "D09": 41529, "D10a": 33105, "D10b": 6741, "D10c": 1683}
FRAME_TB = 8.4976
CODECS = {"sz3", "sperr", "zfp"}


def rows(p):
    return list(csv.DictReader((HERE / p).read_text(encoding="utf-8").splitlines()))


def tot(x, idx):
    return sum(N_FRAME[h] / len(ix) * x[ix].sum() for h, ix in idx.items())


def boot(fn, idx, seed, B=2000):
    rng = np.random.default_rng(seed)
    out = np.empty(B)
    for b in range(B):
        out[b] = fn({h: rng.choice(ix, size=len(ix), replace=True) for h, ix in idx.items()})
    return np.percentile(out, [2.5, 97.5]).tolist()


def main():
    wpf, har = rows("wpf_objects_completed_v2.csv"), rows("archive_hartree_objects.csv")
    s0b = {r["task_id"]: r for r in rows("results/s0b_archive_spin_bytes/objects_spin_bytes.csv")}
    s2 = {r["task_id"]: r for r in rows("results/s2_archive_whole_object/objects_spin_store.csv")}
    s2b = {r["task_id"]: r for r in rows("results/s2b_archive_hartree_decframe/objects.csv")}
    res = []

    def m_ref_map(t):
        return float(s2[t]["m_store_0.01"]) + float(s2[t]["label_atom_xz_bytes"])

    # ---------------- Bader contract
    st = np.array([r["stratum"] for r in wpf]); idx = {h: np.flatnonzero(st == h) for h in N_FRAME}
    js = np.array([float(r["frame_bytes"]) for r in wpf])
    failed = np.array([r["status"] != "SUCCESS" for r in wpf])
    m = np.array([0.0 if f else m_ref_map(r["task_id"]) for r, f in zip(wpf, failed)])
    lr = np.array([float(s0b[r["task_id"]]["lossless_total"]) for r in wpf])
    lm = np.array([float(s0b[r["task_id"]]["lossless_diff"]) for r in wpf])
    for tau in ("0.0001", "0.001", "0.01"):
        sto = np.array([float(r[f"stored_{tau}"]) if r[f"stored_{tau}"] else float(r["frame_bytes"]) for r in wpf])
        f_pub = lambda ix, s=sto: tot(js, ix) / tot(s, ix)                       # noqa: E731
        f_who = lambda ix, s=sto: tot(js, ix) / (tot(s, ix) + tot(m, ix))         # noqa: E731
        Rw = f_who(idx)
        res.append({"quantity": f"Bader archive R at {float(tau):g} e", "published": f_pub(idx),
                    "whole_object": Rw, "whole_object_ci": boot(f_who, idx, 20260930),
                    "saving_TB_whole": FRAME_TB * (1 - 1 / Rw)})
        if tau == "0.001":
            ok = ~failed
            fmt_pub = tot(js * ok, idx) / tot(lr * ok, idx)
            fmt_who = tot(js * ok, idx) / tot((lr + lm) * ok, idx)
            res.append({"quantity": "format gain: gzipped JSON over lossless float64 (successful objects)",
                        "published": fmt_pub, "whole_object": fmt_who})
            cert_who = lambda ix: tot((lr + lm) * ok, ix) / (tot(sto * ok, ix) + tot(m * ok, ix))  # noqa: E731
            res.append({"quantity": "certified compression over lossless binary at 1e-3 e (successful objects)",
                        "published": tot(lr * ok, idx) / tot(sto * ok, idx), "whole_object": cert_who(idx),
                        "whole_object_ci": boot(cert_who, idx, 20260930)})

    # ---------------- Hartree contract
    st = np.array([r["stratum"] for r in har]); idx = {h: np.flatnonzero(st == h) for h in N_FRAME}
    js = np.array([float(r["frame_bytes"]) for r in har])
    m_map = np.array([m_ref_map(r["task_id"]) for r in har])
    m_dec = np.array([float(s2b[r["task_id"]]["m_store_0.01"]) if s2b[r["task_id"]]["m_codec_0.01"] in CODECS
                      else m_ref_map(r["task_id"]) for r in har])
    for tau in ("0.0001", "1e-06", "1e-08"):
        L = np.array([float(r[f"stored_L_{tau}"]) for r in har]); P = np.array([float(r[f"stored_P_{tau}"]) for r in har])
        mL = m_dec if tau == "1e-06" else m_map
        fL = lambda ix, a=L, mm=mL: tot(js, ix) / (tot(a, ix) + tot(mm, ix))       # noqa: E731
        fP = lambda ix, a=P: tot(js, ix) / (tot(a, ix) + tot(m_map, ix))           # noqa: E731
        fLP = lambda ix, a=L, b=P, mm=mL: (tot(b, ix) + tot(m_map, ix)) / (tot(a, ix) + tot(mm, ix))  # noqa: E731
        RL = fL(idx)
        res.append({"quantity": f"Hartree archive R_L (law) at {float(tau):g}", "published": tot(js, idx) / tot(L, idx),
                    "whole_object": RL, "whole_object_ci": boot(fL, idx, 20261012),
                    "m_policy": "decoded frame, no map" if tau == "1e-06" else "reference frame + atom map",
                    "archive_GB_whole": FRAME_TB * 1e3 / RL})
        res.append({"quantity": f"Hartree archive R_P (pointwise) at {float(tau):g}", "published": tot(js, idx) / tot(P, idx),
                    "whole_object": fP(idx), "whole_object_ci": boot(fP, idx, 20261012),
                    "m_policy": "reference frame + atom map"})
        res.append({"quantity": f"Hartree R_L / R_P at {float(tau):g}", "published": tot(P, idx) / tot(L, idx),
                    "whole_object": fLP(idx), "whole_object_ci": boot(fLP, idx, 20261012)})
    out = HERE / "results" / "whole_object_estimates"
    out.mkdir(parents=True, exist_ok=True)
    (out / "estimates.json").write_text(json.dumps(res, indent=2) + "\n")
    lines = ["# Whole-object counterparts of the manuscript's archive numbers", "",
             "Computed by `whole_object_estimates.py` from committed per-object tables (see its docstring for the m policy).", "",
             "| quantity | published | whole object [95% CI] | note |", "|---|---|---|---|"]
    for e in res:
        ci = f" [{e['whole_object_ci'][0]:.3g}, {e['whole_object_ci'][1]:.3g}]" if "whole_object_ci" in e else ""
        note = e.get("m_policy", "")
        if "saving_TB_whole" in e:
            note = f"saving {e['saving_TB_whole']:.2f} TB"
        if "archive_GB_whole" in e:
            note += f"; archive {e['archive_GB_whole']:.1f} GB"
        lines.append(f"| {e['quantity']} | {e['published']:.4g} | {e['whole_object']:.4g}{ci} | {note} |")
    (out / "TABLE.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
