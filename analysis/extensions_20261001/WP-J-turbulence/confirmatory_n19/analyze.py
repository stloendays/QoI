#!/usr/bin/env python3
"""Pre-declared analysis of the second JHTDB confirmation (PROTOCOL.md)."""
from __future__ import annotations
import csv, json, math
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
NBOOT, SEED = 5000, 20261003
TARGETS = {"mask_response_1mIoU": 0.01, "enstrophy_relative_response": 1e-4}
PANEL19 = tuple(range(30001, 30020))
PANEL5 = tuple(range(30001, 30006))


def bound(n):
    return n ** n / (n + 1) ** (n + 1)


def read(name):
    return list(csv.DictReader((HERE / name).open(encoding="utf-8")))


def kappa(a, b):
    a = np.asarray(a, bool); b = np.asarray(b, bool); po = float(np.mean(a == b))
    pa, pb = float(a.mean()), float(b.mean()); pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else math.nan


def ranks(x):
    x = np.asarray(x, float); o = np.argsort(x, kind="mergesort"); r = np.empty(len(x)); i = 0
    while i < len(x):
        j = i + 1
        while j < len(x) and x[o[j]] == x[o[i]]:
            j += 1
        r[o[i:j]] = (i + j - 1) / 2 + 1; i = j
    return r


q = read("qualification_probes.csv"); f = read("fresh_probes.csv")
ids = sorted({r["sample_id"] for r in q})
qby = {sid: {} for sid in ids}
for r in q:
    qby[r["sample_id"]][int(r["seed"])] = r
fby = {sid: [] for sid in ids}
for r in f:
    fby[r["sample_id"]].append(r)


def endpoint(metric, tau, panel, rng):
    floors = {sid: max(float(qby[sid][lab][metric]) for lab in panel) for sid in ids}
    elig = {sid for sid in ids if floors[sid] < tau}; rej = set(ids) - elig
    fresh = {sid: [float(r[metric]) >= tau for r in fby[sid]] for sid in ids}

    def risk(group):
        vals = [x for sid in group for x in fresh[sid]]
        return float(np.mean(vals)) if vals else math.nan

    re, rr = risk(elig), risk(rej)
    boots = []
    for _ in range(NBOOT):
        draw = rng.choice(ids, size=len(ids), replace=True)
        eg = [x for x in draw if x in elig]; rg = [x for x in draw if x in rej]
        if eg and rg:
            boots.append(risk(rg) - risk(eg))
    lo, hi = (np.quantile(boots, [.025, .975]) if boots else (math.nan, math.nan))
    ratio = rr / re if re > 0 else (math.inf if rr > 0 else math.nan)
    total = sum(len(fresh[s]) for s in ids)
    joint = sum(sum(fresh[s]) for s in elig)
    return floors, {
        "metric": metric, "tau": tau, "panel_size": len(panel), "n_eligible": len(elig), "n_rejected": len(rej),
        "fresh_risk_eligible": re, "fresh_risk_rejected": rr, "risk_ratio": ratio, "risk_difference": rr - re,
        "ci_low": float(lo), "ci_high": float(hi),
        "acceptance_met": bool(len(elig) >= 10 and len(rej) >= 10 and ratio >= 5 and lo > 0),
        "joint_admission_exceedance_rate": joint / total, "joint_bound": bound(len(panel)),
        "eligible_any_exceed": sum(any(fresh[s]) for s in elig), "rejected_any_exceed": sum(any(fresh[s]) for s in rej),
    }


rng = np.random.default_rng(SEED)
rows, floors19 = [], {}
for panel in (PANEL19, PANEL5):
    for metric, tau in TARGETS.items():
        fl, row = endpoint(metric, tau, panel, rng)
        rows.append(row)
        if panel is PANEL19:
            floors19[metric] = fl
with (HERE / "summary.csv").open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

me = [floors19["mask_response_1mIoU"][s] < 0.01 for s in ids]
ee = [floors19["enstrophy_relative_response"][s] < 1e-4 for s in ids]
cross = {"agreement": float(np.mean(np.asarray(me) == np.asarray(ee))), "kappa": kappa(me, ee),
         "floor_spearman": float(np.corrcoef(ranks([floors19["mask_response_1mIoU"][s] for s in ids]),
                                             ranks([floors19["enstrophy_relative_response"][s] for s in ids]))[0, 1])}
primary, secondary = rows[0], rows[1]
out = {"n_samples": len(ids), "vortex_confirmed": primary["acceptance_met"],
       "enstrophy_confirmed": secondary["acceptance_met"], "cross_qoi_n19": cross, "endpoints": rows}
(HERE / "provenance.json").write_text(json.dumps(out, indent=2, allow_nan=True) + "\n", encoding="utf-8")

lines = ["# Second independent JHTDB confirmation (19-probe qualification panel)", "",
         f"Cutouts analysed: **{len(ids)}/64**. Protocol: `PROTOCOL.md`.", ""]
for r in rows:
    tag = "pre-registered endpoint" if r["panel_size"] == 19 else "secondary: first five labels only"
    lines += [f"## {r['metric']} — n = {r['panel_size']} ({tag})",
              f"- eligible/rejected: **{r['n_eligible']}/{r['n_rejected']}**",
              f"- fresh risks: **{100 * r['fresh_risk_eligible']:.3f}% vs {100 * r['fresh_risk_rejected']:.3f}%**",
              f"- rejected/eligible RR: **{r['risk_ratio']:.3g}**",
              f"- risk-difference 95% cluster-bootstrap CI: **[{r['ci_low']:.4f}, {r['ci_high']:.4f}]**",
              f"- joint admission-and-exceedance rate: {100 * r['joint_admission_exceedance_rate']:.2f}% "
              f"(bound {100 * r['joint_bound']:.2f}%)"]
    if r["panel_size"] == 19:
        lines.append(f"- acceptance: **{'MET' if r['acceptance_met'] else 'NOT MET'}**")
    lines.append("")
lines += ["## Cross-QoI (n = 19)", f"- agreement: **{cross['agreement']:.3f}**", f"- kappa: **{cross['kappa']:.3f}**",
          f"- floor Spearman rho: **{cross['floor_spearman']:.3f}**"]
(HERE / "RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
