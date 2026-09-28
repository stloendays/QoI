"""Data layer for the QoI composite figures.

Every figure reads the frozen repository tables through here so that a number
shown in a panel is the number in the CSV, never a transcription. Paths are
relative to the repository root (two levels above this file).
"""
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
TAUS = (1e-4, 1e-3, 1e-2)


def p(*parts):
    return os.path.join(REPO, *parts)


def csv(*parts, **kw):
    return pd.read_csv(p(*parts), **kw)


def truthy(s):
    return s.astype(str).str.lower().isin(["true", "1", "1.0"])


# ---- frozen benchmark -----------------------------------------------------------
def master():
    return csv("benchmark", "master_benchmark_full.csv")


def tight_ladder():
    return csv("benchmark", "master_benchmark_tight_ladder.csv")


# ---- stability / QSQ --------------------------------------------------------------
def floor_a1():
    return csv("stability", "stability_floor_A1.csv")


def floor_archived():
    return csv("stability", "stability_floor_A_archived_float32.csv")


def eligibility_summary():
    return csv("stability", "eligibility_summary_A1.csv")


def paired_floors():
    """Development materials with both the archived float32 probe and the QSQ floor."""
    a1 = floor_a1()[["material_id", "domain", "stability_floor_A1_e"]]
    a0 = floor_archived()[["material_id", "floor_resolved_e"]].rename(columns={"floor_resolved_e": "archived"})
    m = a1.merge(a0, on="material_id")
    m = m[np.isfinite(m.archived) & np.isfinite(m.stability_floor_A1_e) & (m.archived > 0) & (m.stability_floor_A1_e > 0)]
    m["ratio"] = m.stability_floor_A1_e / m.archived
    return m.reset_index(drop=True)


# ---- research upgrade P1 / P2 -------------------------------------------------------
def p1_common_tight():
    return csv("analysis", "research_upgrade", "p1_common_tight_summary.csv")


def p2_fresh_probes():
    return csv("analysis", "research_upgrade", "p2_fresh_probe_cohort_summary.csv")


# ---- operator controls -----------------------------------------------------------
def hartree_rows(gate_only=True):
    r = csv("analysis", "hartree_potential_expansion", "rows.csv")
    if gate_only:
        r = r[truthy(r.reproduction_gate_pass)]
    return r


def hartree_smoothness():
    return csv("analysis", "hartree_potential_expansion", "material_smoothness.csv")


def hartree_dispersion():
    return csv("analysis", "hartree_potential_expansion", "matched_error_dispersion.csv")


# ---- matched realized-Linf ----------------------------------------------------------
def matched_effects():
    return csv("analysis", "matched_realized_linf_v1", "matched_effects_summary.csv")


def equal_nominal():
    return csv("analysis", "matched_realized_linf_v1", "equal_nominal_diagnostics.csv")


# ---- mechanism ---------------------------------------------------------------------
def mechanism_summary():
    return csv("mechanism", "basin_error_decomposition_summary.csv")


def mechanism_per_atom():
    return csv("mechanism", "basin_error_decomposition_per_atom.csv")


# ---- Fourier / Hartree spectral mechanism ---------------------------------------------
def spectral_radial():
    return csv("analysis", "hartree_spectral_mechanism", "results", "radial_spectrum_summary.csv")


def spectral_ratio_summary():
    return csv("analysis", "hartree_spectral_mechanism", "results", "mechanism_ratio_summary.csv")


def spectral_pairs():
    return csv("analysis", "hartree_spectral_mechanism", "results", "matched_pair_mechanism.csv")


def spectral_summary():
    with open(p("analysis", "hartree_spectral_mechanism", "results", "SUMMARY.json"), encoding="utf-8") as f:
        return json.load(f)


# ---- external confirmatory cohort -----------------------------------------------------
EXT = ("validation", "final_external_confirmatory63_20260908", "confirmatory63")


def external_summary():
    return csv(*EXT, "external_summary_a1.csv")


def external_pairwise():
    return csv(*EXT, "pairwise_external.csv")


def external_best():
    return csv(*EXT, "best_certified_external.csv")


def external_audit():
    with open(p(*EXT, "summary.json"), encoding="utf-8") as f:
        return json.load(f)


# ---- supplement tables --------------------------------------------------------------
def supp(name):
    return csv("supplement", name)
