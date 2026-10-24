#!/usr/bin/env python3
"""Aggregate the linearized-XC study (PROTOCOL.md §6): certification of X and F under the XC contract, paired with
each other and with the P, L and U writers of `nonlinear_xc_20261024` (same platform, contract and search).

    python aggregate_xcl.py --checkpoints <dir> --out results
Medians with the bootstrap of the median used by the XC study (seed 20261006, 10,000 resamples), per cohort.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
import sys  # noqa: E402
sys.path.insert(0, str(HERE.parent / "nonlinear_xc_20261024"))
from aggregate_xc import boot  # noqa: E402

PRIOR = HERE.parent / "nonlinear_xc_20261024" / "results" / "xc_contract_rows.csv"
PAIRS = (("X", "F"), ("X", "U"), ("X", "L"), ("X", "P"), ("F", "U"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoints", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    cks = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(a.checkpoints.glob("*.json"))]
    ok = [c for c in cks if c["status"] == "SUCCESS"]
    rows = pd.DataFrame([dict(r, material_id=c["material_id"], cohort=c["cohort"], floor=c["xc_floor_meV_per_atom"])
                         for c in ok for r in c["xc_contract"]])
    a.out.mkdir(parents=True, exist_ok=True)
    rows.to_csv(a.out / "xcl_rows.csv", index=False)
    pd.DataFrame([{"material_id": c["material_id"], "cohort": c["cohort"], **{f"W{s:02d}": w for s, w in
                   enumerate(c["shell_weight_rel"])}} for c in ok]).to_csv(a.out / "shell_weights.csv", index=False)
    summ = {"materials": len(cks), "success": len(ok), "failed": [c["material_id"] for c in cks if c["status"] != "SUCCESS"],
            "xc_contract": [], "paired": []}
    cert = rows[rows.get("certified", False) == True]  # noqa: E712
    for (coh, w, tx), g in rows.groupby(["cohort", "writer", "tau_x"]):
        c = cert[(cert.cohort == coh) & (cert.writer == w) & (cert.tau_x == tx)]
        summ["xc_contract"].append({"cohort": coh, "writer": w, "tau_x_meV_per_atom": tx, "n": int(len(g)),
                                    "eligible": int(g.eligible.sum()), "certified": int(len(c)),
                                    "median_cr": float(c.cr.median()) if len(c) else None, "ci95": boot(c.cr) if len(c) else None})
    prior = pd.read_csv(PRIOR)
    prior = prior[prior.certified == True]  # noqa: E712
    both = pd.concat([cert[["cohort", "material_id", "tau_x", "writer", "cr"]],
                      prior[["cohort", "material_id", "tau_x", "writer", "cr"]]], ignore_index=True)
    piv = both.pivot_table(index=["cohort", "material_id", "tau_x"], columns="writer", values="cr")
    for (coh, tx), g in piv.groupby(level=["cohort", "tau_x"]):
        for num, den in PAIRS:
            if num in g and den in g:
                r = (g[num] / g[den]).dropna()
                summ["paired"].append({"cohort": coh, "tau_x_meV_per_atom": tx, "ratio": f"{num}/{den}", "n": int(r.size),
                                       "wins": int((r > 1).sum()), "median": float(r.median()) if r.size else None,
                                       "ci95": boot(r)})
    (a.out / "SUMMARY.json").write_text(json.dumps(summ, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summ, indent=1)[:4000])


if __name__ == "__main__":
    main()
