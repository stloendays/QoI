#!/usr/bin/env python3
"""Vacuum-level (work-function) error of a decoded slab density: units, vacuum rule and statistics.

Frozen definitions; see PROTOCOL.md. Every field passed in here is in CHGCAR units (rho * V_cell, rho in e/A^3);
the lattice rows are the lattice vectors a_0, a_1, a_2 (A) and grid axis n runs along a_n.
"""
from __future__ import annotations

import math

import numpy as np

K_E = 14.399645            # e^2 / (4 pi eps0), eV * A
VACUUM_FRACTION = 1e-3     # vacuum plane: planar-averaged reference density < VACUUM_FRACTION * its maximum
MIN_VACUUM_A = 3.0         # minimum thickness (A) of the longest contiguous periodic vacuum run
THRESHOLDS_MEV = (1.0, 10.0)
P95 = 0.95


def reciprocal_vectors(lattice: np.ndarray) -> np.ndarray:
    """Rows b_n with a_m . b_n = 2 pi delta_mn (1/A)."""
    return 2.0 * np.pi * np.linalg.inv(np.asarray(lattice, dtype=np.float64)).T


def cell_volume(lattice: np.ndarray) -> float:
    return abs(float(np.linalg.det(np.asarray(lattice, dtype=np.float64))))


def interplanar_spacing(lattice: np.ndarray, axis: int) -> float:
    """Distance (A) between successive lattice planes spanned by the two other lattice vectors."""
    return 2.0 * np.pi / float(np.linalg.norm(reciprocal_vectors(lattice)[axis]))


def _signed_freq(n: int) -> np.ndarray:
    return np.fft.fftfreq(int(n)) * int(n)


def hartree_potential_ev(field: np.ndarray, lattice: np.ndarray) -> np.ndarray:
    """V_H(r) in eV: V_H(G) = 4 pi k_e rho(G) / |G|^2 with rho = field / V_cell (e/A^3) and V_H(G=0) = 0."""
    x = np.asarray(field, dtype=np.float64)
    b = reciprocal_vectors(lattice)
    m = [_signed_freq(n) for n in x.shape]
    g = (m[0][:, None, None, None] * b[0] + m[1][None, :, None, None] * b[1]
         + m[2][None, None, :, None] * b[2])
    g2 = np.einsum("...k,...k->...", g, g)
    rho_g = np.fft.fftn(x / cell_volume(lattice))
    v = np.zeros_like(rho_g)
    mask = g2 > 0.0
    v[mask] = 4.0 * np.pi * K_E * rho_g[mask] / g2[mask]
    return np.fft.ifftn(v).real


def planar_average(field: np.ndarray, axis: int) -> np.ndarray:
    """Mean over the two grid axes other than `axis` (the plane of constant fractional coordinate along `axis`)."""
    other = tuple(i for i in range(3) if i != axis)
    return np.asarray(field, dtype=np.float64).mean(axis=other)


def planar_hartree_ev(field: np.ndarray, lattice: np.ndarray, axis: int) -> np.ndarray:
    """Planar average along `axis` of V_H (eV), computed exactly from the G = m b_axis components.

    The plane average keeps only the G components whose indices along the two other axes are zero, so
    <V_H>(k) = sum_{m != 0} 4 pi k_e rho_m / (m^2 |b_axis|^2) exp(2 pi i m k / N), with rho_m the DFT of <rho>(k).
    """
    return planar_hartree_from_profile(planar_average(field, axis), lattice, axis)


def planar_hartree_from_profile(profile: np.ndarray, lattice: np.ndarray, axis: int) -> np.ndarray:
    """Same as planar_hartree_ev, from the planar average (CHGCAR units) of the field along `axis`."""
    p = np.asarray(profile, dtype=np.float64) / cell_volume(lattice)
    n = p.size
    m = _signed_freq(n)
    bn2 = float(np.sum(reciprocal_vectors(lattice)[axis] ** 2))
    pg = np.fft.fft(p)
    v = np.zeros_like(pg)
    nz = m != 0
    v[nz] = 4.0 * np.pi * K_E * pg[nz] / (m[nz] ** 2 * bn2)
    return np.fft.ifft(v).real


def _longest_periodic_run(mask: np.ndarray) -> tuple[int, int]:
    """(length, start index) of the longest contiguous run of True on a periodic 1-D grid; first run on ties."""
    mask = np.asarray(mask, dtype=bool)
    n = mask.size
    if not mask.any():
        return 0, 0
    if mask.all():
        return n, 0
    r = int(np.argmin(mask))                      # a non-vacuum plane: no run wraps across it
    rolled = np.roll(mask, -r)
    best_len, best_start, cur_len, cur_start = 0, 0, 0, 0
    for i, v in enumerate(rolled):
        if v:
            if cur_len == 0:
                cur_start = i
            cur_len += 1
            if cur_len > best_len:
                best_len, best_start = cur_len, cur_start
        else:
            cur_len = 0
    return best_len, (best_start + r) % n


def vacuum_window(reference: np.ndarray, lattice: np.ndarray, fraction: float = VACUUM_FRACTION,
                  min_thickness: float = MIN_VACUUM_A) -> dict:
    """Surface normal and vacuum window from the reference density only (PROTOCOL.md section 4)."""
    x = np.asarray(reference, dtype=np.float64)
    vol = cell_volume(lattice)
    per_axis = []
    for axis in range(3):
        p = planar_average(x, axis) / vol
        thr = fraction * float(np.max(p))
        length, start = _longest_periodic_run(p < thr)
        d = interplanar_spacing(lattice, axis)
        n = x.shape[axis]
        per_axis.append({"axis": axis, "n": n, "spacing_A": d, "pmax": float(np.max(p)), "threshold": thr,
                         "run_planes": length, "run_start": start, "run_A": length * d / n,
                         "all_vacuum": bool(length == n)})
    best = max(per_axis, key=lambda r: (r["run_A"], -r["axis"]))
    out = {"run_A_axis0": per_axis[0]["run_A"], "run_A_axis1": per_axis[1]["run_A"], "run_A_axis2": per_axis[2]["run_A"],
           "normal_axis": best["axis"], "n_normal": best["n"], "spacing_normal_A": best["spacing_A"],
           "pmax_e_per_A3": best["pmax"], "threshold_e_per_A3": best["threshold"], "run_planes": best["run_planes"],
           "run_start": best["run_start"], "run_A": best["run_A"]}
    length = best["run_planes"]
    qualifies = (not best["all_vacuum"]) and best["run_A"] >= min_thickness and length >= 2
    lo, hi = length // 4, length - length // 4
    idx = (best["run_start"] + np.arange(lo, hi)) % best["n"]
    out.update({"qualifies": bool(qualifies), "window_planes": int(idx.size),
                "window_A": idx.size * best["spacing_A"] / best["n"],
                "window_first": int(idx[0]) if idx.size else -1, "window_last": int(idx[-1]) if idx.size else -1,
                "window_index": idx})
    return out


def vacuum_shift(delta: np.ndarray, lattice: np.ndarray, window: dict) -> tuple[float, float]:
    """(Delta Phi, max |planar-averaged Delta V_H|) over the window, both in meV, for delta = decoded - reference."""
    return vacuum_shift_from_profile(planar_average(delta, window["normal_axis"]), lattice, window)


def vacuum_shift_from_profile(profile: np.ndarray, lattice: np.ndarray, window: dict) -> tuple[float, float]:
    """vacuum_shift from the planar average of (decoded - reference) along the normal axis (CHGCAR units)."""
    if len(window["window_index"]) == 0:
        return math.nan, math.nan
    v = planar_hartree_from_profile(profile, lattice, window["normal_axis"])[window["window_index"]]
    return 1e3 * float(np.mean(v)), 1e3 * float(np.max(np.abs(v)))


def summarize(values) -> dict:
    """Median, P95 (numpy linear quantile), maximum and threshold fractions of |values| (meV)."""
    a = np.abs(np.asarray(list(values), dtype=np.float64))
    n = int(a.size)
    if n == 0:
        return {"n": 0, "median": math.nan, "p95": math.nan, "max": math.nan,
                **{f"frac_lt_{t:g}meV": math.nan for t in THRESHOLDS_MEV}, **{f"n_lt_{t:g}meV": 0 for t in THRESHOLDS_MEV}}
    out = {"n": n, "median": float(np.median(a)), "p95": float(np.quantile(a, P95, method="linear")), "max": float(a.max())}
    for t in THRESHOLDS_MEV:
        k = int(np.sum(a < t))
        out[f"n_lt_{t:g}meV"] = k
        out[f"frac_lt_{t:g}meV"] = k / n
    return out
