"""Shared loaders for the NC figures (General-QOAC law cohorts and the joint-certification cohort)."""
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "figures", "composite"))
LAW = os.path.join(ROOT, "analysis", "general_qoac_law", "results")
HB = os.path.join(ROOT, "analysis", "qoac_hb_v2", "results")
TAUS = (1e-4, 1e-6, 1e-8)
TAU_KEY = {1e-4: "tau_0.0001", 1e-6: "tau_1e-06", 1e-8: "tau_1e-08"}
TAU_LAB = {1e-4: "10$^{-4}$", 1e-6: "10$^{-6}$", 1e-8: "10$^{-8}$"}


FRESH = os.path.join(ROOT, "analysis", "fresh_population_20261006")


def part_a():
    """Per-material Part A table restricted to the confirmatory manifests.

    The P1 file also carries the 12 shakedown materials (the aggregator wrote the unfiltered table); the
    pre-registered criteria were computed on the 60 confirmatory materials only, so the figures filter the same way.
    """
    ids1 = set(pd.read_csv(os.path.join(FRESH, "P1_CONFIRMATORY_MANIFEST.csv")).material_id)
    ids3 = set(pd.read_csv(os.path.join(FRESH, "P3B_CONFIRMATORY_MANIFEST.csv")).material_id)
    a = pd.read_csv(os.path.join(LAW, "run_P1_CONFIRMATORY", "part_a_material.csv"))
    b = pd.read_csv(os.path.join(LAW, "run_P3B_CONFIRMATORY", "part_a_material.csv"))
    a = a[a.material_id.isin(ids1)].assign(cohort="bulk")
    b = b[b.material_id.isin(ids3)].assign(cohort="slab")
    assert a.material_id.nunique() == 60 and b.material_id.nunique() == 32
    return pd.concat([a, b], ignore_index=True)


def summaries():
    s = {}
    for coh, d in (("bulk", "run_P1_CONFIRMATORY"), ("slab", "run_P3B_CONFIRMATORY")):
        s[coh] = json.load(open(os.path.join(LAW, d, "SUMMARY.json")))
    return s


def check_median(df, num, den, coh, tau, summ, key):
    """Assert that the plotted per-material median equals the committed SUMMARY median."""
    t = df[(df.cohort == coh) & np.isclose(df.tau, tau)]
    r = (t[num] / t[den]).dropna()
    got = float(np.median(r))
    want = summ[coh]["part_A"][TAU_KEY[tau]][key]["median"]
    assert abs(got - want) < 1e-9 * max(1.0, want), (coh, tau, key, got, want)
    return r, summ[coh]["part_A"][TAU_KEY[tau]][key]


# One colour per allocation family across Figs. 4-7: green = operator-aware (law light, operational optimum dark),
# blue = operator-blind transform coding, navy = spectral truncation, grey = pointwise codecs. Cohort is the marker:
# filled circle = bulk crystal, open triangle = surface slab.
ARM = {"A1": "#89AA7B", "A3": "#5E7A52", "A5": "#7789B7", "A2": "#5A6480", "A6": "#9AA0A8"}
ARM_NAME = {"A6": "pointwise\ncodecs", "A5": "blind\noptimum", "A1": "closed-form\nlaw", "A3": "operational\noptimum",
            "A2": "spectral\ntruncation"}
