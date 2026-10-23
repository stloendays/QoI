#!/usr/bin/env python3
"""Aggregate the XC study checkpoints (PROTOCOL.md §6): Part 1 transfer table, Part 2 XC-contract certification.

    python aggregate_xc.py --checkpoints <dir> --out results
Medians with the law protocol's bootstrap of the median (seed 20261006, 10,000 resamples), per cohort.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

SEED, NBOOT = 20261006, 10000


def boot(x):
    x = np.asarray(x, float)
    if x.size == 0:
        return [None, None]
    rng = np.random.default_rng(SEED)
    m = np.median(x[rng.integers(0, x.size, (NBOOT, x.size))], axis=1)
    return [float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoints", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    cks = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(a.checkpoints.glob("*.json"))]
    ok = [c for c in cks if c["status"] == "SUCCESS"]
    tr = pd.DataFrame([dict(r, material_id=c["material_id"], cohort=c["cohort"]) for c in ok for r in c["transfer"]])
    xc = pd.DataFrame([dict(r, material_id=c["material_id"], cohort=c["cohort"], floor=c["xc_floor_meV_per_atom"])
                       for c in ok for r in c["xc_contract"]])
    a.out.mkdir(parents=True, exist_ok=True)
    tr.to_csv(a.out / "transfer_rows.csv", index=False)
    xc.to_csv(a.out / "xc_contract_rows.csv", index=False)
    summ = {"materials": len(cks), "success": len(ok), "failed": [c["material_id"] for c in cks if c["status"] != "SUCCESS"],
            "transfer": [], "xc_contract": [], "paired": []}
    t = tr[tr.status == "OK"]
    for (coh, arm, tau), g in t.groupby(["cohort", "arm", "tau_H"]):
        summ["transfer"].append({
            "cohort": coh, "arm": arm, "tau_H": tau, "n": int(len(g)), "hartree_certified": int(g.hartree_certified.sum()),
            "median_dE_pbe_meV_per_atom": float(g.dE_pbe_meV_per_atom.median()), "ci95": boot(g.dE_pbe_meV_per_atom),
            "max_dE_pbe_meV_per_atom": float(g.dE_pbe_meV_per_atom.max()),
            "median_dE_lda_meV_per_atom": float(g.dE_lda_meV_per_atom.median()),
            "below_1meV": int((g.dE_pbe_meV_per_atom < 1.0).sum()), "below_0.1meV": int((g.dE_pbe_meV_per_atom < 0.1).sum()),
            "median_vxc_lda_rel_rms": float(g.vxc_lda_rel_rms.median())})
    for (coh, w, tx), g in xc.groupby(["cohort", "writer", "tau_x"]):
        c = g[g.get("certified", False) == True]  # noqa: E712
        summ["xc_contract"].append({"cohort": coh, "writer": w, "tau_x_meV_per_atom": tx, "n": int(len(g)),
                                    "eligible": int(g.eligible.sum()), "certified": int(len(c)),
                                    "median_cr": float(c.cr.median()) if len(c) else None, "ci95": boot(c.cr) if len(c) else None})
    if len(xc):
        cr = xc[xc.get("certified", False) == True].pivot_table(index=["cohort", "material_id", "tau_x"],  # noqa: E712
                                                                 columns="writer", values="cr")
        for (coh, tx), g in cr.groupby(level=["cohort", "tau_x"]):
            for num, den in (("L", "P"), ("U", "P"), ("L", "U")):
                if num in g and den in g:
                    r = (g[num] / g[den]).dropna()
                    summ["paired"].append({"cohort": coh, "tau_x_meV_per_atom": tx, "ratio": f"{num}/{den}", "n": int(r.size),
                                           "wins": int((r > 1).sum()), "median": float(r.median()) if r.size else None,
                                           "ci95": boot(r)})
    (a.out / "SUMMARY.json").write_text(json.dumps(summ, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summ, indent=1)[:4000])


if __name__ == "__main__":
    main()
