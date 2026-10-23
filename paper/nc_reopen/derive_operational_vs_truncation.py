"""Operational optimum (A3) and closed-form law (A1) against spectral truncation (A2), per tolerance.

Reads the committed per-material certified compression ratios of the law protocol (P1: 60 bulk crystals, P3b: 32
slabs; `analysis/general_qoac_law/results/run_*_CONFIRMATORY/part_a_material.csv`, restricted to the confirmatory
manifests) and reports paired medians with the law protocol's bootstrap (`aggregate_law.boot`: seed 20261006,
10,000 resamples). Checks the published A1/A2 and A3/A1 medians first.

    python paper/nc_reopen/derive_operational_vs_truncation.py   -> paper/nc_reopen/derived/operational_vs_truncation.csv
"""
import csv
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
LAW = ROOT / "analysis/general_qoac_law/results"
SEED, NBOOT = 20261006, 10000
PUBLISHED = {("P1", "A1/A2"): (0.79, 1.32, 1.59), ("P3B", "A1/A2"): (0.69, 1.41, 2.16),
             ("P1", "A3/A1"): (1.58, 1.10, 1.03), ("P3B", "A3/A1"): (2.22, 1.22, 1.08)}


def boot(x):
    x = np.asarray(x, float)
    rng = np.random.default_rng(SEED)
    m = np.median(x[rng.integers(0, x.size, (NBOOT, x.size))], axis=1)
    return float(np.quantile(m, 0.025)), float(np.quantile(m, 0.975))


rows = []
for cohort, run, manifest in (("P1", "run_P1_CONFIRMATORY", "P1_CONFIRMATORY_MANIFEST.csv"),
                              ("P3B", "run_P3B_CONFIRMATORY", "P3B_CONFIRMATORY_MANIFEST.csv")):
    ids = pd.read_csv(ROOT / "analysis/fresh_population_20261006" / manifest).material_id.tolist()
    d = pd.read_csv(LAW / run / "part_a_material.csv")
    d = d[d.material_id.isin(ids)]
    assert d.material_id.nunique() == len(ids), (cohort, d.material_id.nunique(), len(ids))
    for (num, den) in (("A1", "A2"), ("A3", "A1"), ("A3", "A2")):
        meds = []
        for tau in (1e-4, 1e-6, 1e-8):
            t = d[np.isclose(d.tau, tau)].set_index("material_id").reindex(ids)
            r = (t[num] / t[den]).dropna()
            lo, hi = boot(r)
            meds.append(float(r.median()))
            rows.append({"cohort": cohort, "ratio": f"{num}/{den}", "tau": f"{tau:g}", "n": int(r.size),
                         "wins": int((r > 1).sum()), "median": f"{r.median():.4f}", "median_2dp": f"{r.median():.2f}", "ci_lo": f"{lo:.4f}",
                         "ci_hi": f"{hi:.4f}"})
        key = (cohort, f"{num}/{den}")
        if key in PUBLISHED:
            assert all(abs(m - p) < 0.006 for m, p in zip(meds, PUBLISHED[key])), (key, meds)
out = ROOT / "paper/nc_reopen/derived/operational_vs_truncation.csv"
with out.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
for r in rows:
    print(r)
