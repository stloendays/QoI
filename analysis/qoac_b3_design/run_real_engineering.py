#!/usr/bin/env python3
"""QOAC-B3 real-material engineering run (DESIGN_STUDY.md section 7).

Per material of the fresh P2 engineering manifest:

1. download CHGCAR, AECCAR0 and AECCAR2 (sha256 + byte check of the CHGCAR
   against the manifest), form ref = AECCAR0 + AECCAR2 and run the compiled
   Henkelman binary once on (CHGCAR, REFCAR) for the reference labels
   (``-b ongrid -vac 0.001 -ref REFCAR -p atom_index -p bader_index``);
2. Gate 0: compare the binary's volume map (BvIndex), atom map (AtIndex),
   basin count and maxima with ``ongrid.ongrid_partition`` (fast) and, when
   npoints <= LITERAL_MAX_NPOINTS, with ``ongrid.ongrid_literal`` on the same
   ref field; report agreement fractions, mismatch voxels and R1/R2;
3. arms A2 (iterative tier-B correction) and A1 (one-shot allowance) on the
   log-domain relative base quantizer, delta in DELTAS: decode, rerun the
   binary on (CHGCAR, decoded ref) and record reassignment, Bader charge
   error, base payload bytes, side-information bytes and wall time;
4. arm L: label-map bytes from the prototype coder, an lzma round trip of the
   stored atom/volume labels, and per-region sums of the exact CHGCAR over the
   decoded labels compared with the binary's charges;
5. write ``<material_id>.json`` (everything, including failures) and
   ``<material_id>_rows.csv``.

``aggregate`` merges per-material outputs into rows.csv, gate0.csv,
failures.csv and SUMMARY.json. Only Gate 0 agreement statistics are reported;
no other pass/fail gate is evaluated here.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import lzma
import math
import re
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "operator_aware_bader_fixed_partition"))

from b3_correct import (correct, label_map_cost, lorenzo_bytes, make_reference,  # noqa: E402
                        oneshot_allowance, oneshot_levels, rel_quantize)
from ongrid import atom_map, ongrid_literal, regularity_report  # noqa: E402

VACVAL = 1e-3
DELTAS = (1e-3, 1e-2, 5e-2)
ARMS = ("A2", "A1")
LITERAL_MAX_NPOINTS = 400_000
MARGIN_ULPS = 64.0
CHARGE_MATCH_TOL_E = 1e-5     # ACF.dat prints charges with 6 decimals
BUCKET = "https://materialsproject-parsed.s3.amazonaws.com/"

ROW_FIELDS = [
    "material_id", "npoints", "natoms", "arm", "delta", "status", "error",
    "gate0_regular", "gate0_fast_volnum_agreement",
    "base_bytes", "side_bytes", "side_over_base", "total_bytes", "raw_ref_bytes",
    "label_ctx_bytes_volnum", "label_ctx_bytes_atom",
    "reassigned_volnum_frac_before", "reassigned_atom_frac_before",
    "reassigned_volnum_frac", "reassigned_atom_frac", "reassigned_volnum_voxels",
    "nbasins_decoded", "nbasins_reference",
    "bader_charge_err_max_e", "bader_charge_err_max_e_before",
    "linf_over_bound", "max_pointwise_rel_err",
    "iterations", "edits", "edits_by_level",
    "encode_seconds", "bader_seconds",
]
GATE0_FIELDS = [
    "material_id", "status", "npoints", "natoms", "R1_violations", "R2_violations", "regular",
    "nbasins_binary", "nbasins_fast", "nbasins_literal",
    "fast_volnum_agreement", "fast_volnum_mismatch_voxels",
    "fast_atom_agreement", "fast_atom_mismatch_voxels",
    "fast_maxima_match", "bcf_maxima_matched", "bcf_maxima_total",
    "literal_run", "literal_note", "literal_volnum_agreement", "literal_volnum_mismatch_voxels",
    "literal_vs_fast_mismatch_voxels",
]


# --------------------------------------------------------------------------
# Binary output parsing (pure; unit-tested on fabricated text)
# --------------------------------------------------------------------------

def parse_acf(text: str, natoms: int) -> np.ndarray:
    """Per-atom Bader charges, column CHARGE of ACF.dat."""
    rows = [ln.split() for ln in text.splitlines()]
    data = [float(r[4]) for r in rows if len(r) >= 7 and r[0].isdigit()]
    if len(data) != natoms:
        raise RuntimeError(f"ACF atom count mismatch: {len(data)} != {natoms}")
    return np.array(data, dtype=np.float64)


def parse_bcf(text: str) -> np.ndarray:
    """Cartesian positions of the significant Bader maxima in BCF.dat."""
    out = []
    for ln in text.splitlines():
        r = ln.split()
        if len(r) >= 7 and r[0].isdigit():
            out.append([float(r[1]), float(r[2]), float(r[3])])
    return np.array(out, dtype=np.float64).reshape(-1, 3)


def parse_nbasins(log: str) -> int:
    m = re.search(r"NUMBER OF BADER MAXIMA FOUND:\s*(\d+)", log)
    if not m:
        raise RuntimeError("binary log lacks 'NUMBER OF BADER MAXIMA FOUND'")
    return int(m.group(1))


# --------------------------------------------------------------------------
# Gate 0 comparisons (pure)
# --------------------------------------------------------------------------

def map_agreement(a: np.ndarray, b: np.ndarray) -> tuple[float, int]:
    a = np.asarray(a); b = np.asarray(b)
    if a.shape != b.shape:
        raise ValueError("label map shape mismatch")
    mism = int(np.count_nonzero(a != b))
    return 1.0 - mism / a.size, mism


def basin_argmax(field: np.ndarray, volnum: np.ndarray, nbasins: int) -> np.ndarray:
    """Flat index of the largest field value inside each basin 1..nbasins
    (first in C order on ties; -1 for an empty basin). For a regular field
    this is the basin's on-grid maximum."""
    f = np.asarray(field, dtype=np.float64).ravel()
    v = np.asarray(volnum, dtype=np.int64).ravel()
    out = np.full(nbasins, -1, dtype=np.int64)
    live = (v >= 1) & (v <= nbasins)
    idx = np.flatnonzero(live)
    if idx.size == 0:
        return out
    order = np.lexsort((idx, -f[idx], v[idx]))   # by basin, value desc, index asc
    s = idx[order]
    first = np.ones(s.size, dtype=bool)
    first[1:] = v[s[1:]] != v[s[:-1]]
    out[v[s[first]] - 1] = s[first]
    return out


def maxima_cartesian(maxima_flat: np.ndarray, shape, lattice) -> np.ndarray:
    ijk = np.array(np.unravel_index(np.asarray(maxima_flat, dtype=np.int64), shape)).T
    return (ijk / np.array(shape, dtype=np.float64)) @ np.asarray(lattice, dtype=np.float64)


def match_positions(points: np.ndarray, targets: np.ndarray, lattice, tol: float = 2e-4) -> int:
    """Number of ``points`` within ``tol`` (Angstrom, minimum image over the
    27 neighbouring cells) of some target. BCF.dat prints 4 decimals."""
    P = np.asarray(points, dtype=np.float64).reshape(-1, 3)
    T = np.asarray(targets, dtype=np.float64).reshape(-1, 3)
    if P.size == 0 or T.size == 0:
        return 0
    L = np.asarray(lattice, dtype=np.float64)
    imgs = np.array([(a, b, c) for a in (-1, 0, 1) for b in (-1, 0, 1) for c in (-1, 0, 1)], float) @ L
    d = P[:, None, None, :] - T[None, :, None, :] - imgs[None, None, :, :]
    dmin = np.sqrt(np.min(np.sum(d * d, axis=-1), axis=(1, 2)))
    return int(np.count_nonzero(dmin <= tol))


def gate0_record(mid, ref_field, lattice, frac, bin_vol, bin_atom, bin_nb, bcf_pos,
                 literal_max_npoints=LITERAL_MAX_NPOINTS) -> tuple[dict, object]:
    """Gate 0 statistics for one material (fields in C-index (n1,n2,n3))."""
    f = np.ascontiguousarray(ref_field, dtype=np.float64)
    ref = make_reference(f, lattice, VACVAL)
    part = ref.part
    reg = regularity_report(f, lattice, VACVAL, ref.st)
    emu_atom = atom_map(part, lattice, frac)
    va, vm = map_agreement(part.volnum, bin_vol)
    aa, am = map_agreement(emu_atom, bin_atom)
    bin_max = basin_argmax(f, bin_vol, bin_nb)
    fast_max_match = bool(bin_nb == part.nbasins and np.array_equal(bin_max, part.maxima))
    rec = {"material_id": mid, "status": "OK", "npoints": int(f.size), "natoms": int(len(frac)),
           **{k: reg[k] for k in ("R1_violations", "R2_violations", "regular")},
           "nbasins_binary": int(bin_nb), "nbasins_fast": int(part.nbasins), "nbasins_literal": None,
           "fast_volnum_agreement": va, "fast_volnum_mismatch_voxels": vm,
           "fast_atom_agreement": aa, "fast_atom_mismatch_voxels": am,
           "fast_maxima_match": fast_max_match,
           "bcf_maxima_matched": match_positions(bcf_pos, maxima_cartesian(part.maxima, f.shape, lattice), lattice),
           "bcf_maxima_total": int(len(bcf_pos)),
           "literal_run": False, "literal_note": "", "literal_volnum_agreement": None,
           "literal_volnum_mismatch_voxels": None, "literal_vs_fast_mismatch_voxels": None}
    if f.size <= literal_max_npoints:
        t = time.perf_counter()
        lit, lnb = ongrid_literal(f, lattice, VACVAL)
        la, lm = map_agreement(lit, bin_vol)
        rec.update(literal_run=True, nbasins_literal=int(lnb), literal_volnum_agreement=la,
                   literal_volnum_mismatch_voxels=lm,
                   literal_vs_fast_mismatch_voxels=map_agreement(lit, part.volnum)[1],
                   literal_note=f"ran in {time.perf_counter() - t:.1f}s")
    else:
        rec["literal_note"] = f"skipped: npoints {f.size} > {literal_max_npoints} (pure-Python transcription too slow)"
    return rec, ref


# --------------------------------------------------------------------------
# Arm rows (pure apart from the binary callback)
# --------------------------------------------------------------------------

def robust_margins(ref) -> tuple[float, float]:
    """DESIGN_STUDY.md section 7 robust mode: gamma = 64 ulp(max|f|)(1 + w_max);
    the vacuum test |g|/V - vacval gets 64 ulp(vacval)."""
    gamma = MARGIN_ULPS * float(np.spacing(np.max(np.abs(ref.f)))) * (1.0 + float(ref.st.w.max()))
    return gamma, MARGIN_ULPS * float(np.spacing(VACVAL))


def base_floor(ref) -> float:
    """Values below the floor decode to 0 (vacuum). Kept far below the vacuum
    threshold so the floor alone never moves the vacuum boundary."""
    return min(1e-9 * float(np.max(np.abs(ref.f))), 1e-2 * VACVAL * ref.volume)


def label_roundtrip(labels: np.ndarray) -> tuple[np.ndarray, int]:
    """Actual lossless storage of a label map: uint16 C order, xz."""
    lab = np.asarray(labels, dtype=np.int64)
    if lab.min(initial=0) < 0 or lab.max(initial=0) >= 2 ** 16:
        raise ValueError("labels out of uint16 range")
    blob = lzma.compress(lab.astype("<u2").tobytes(), preset=9 | lzma.PRESET_EXTREME)
    dec = np.frombuffer(lzma.decompress(blob), dtype="<u2").astype(np.int64).reshape(lab.shape)
    return dec, len(blob)


def arm_l_record(chg, bin_vol, bin_atom, q_ref, natoms) -> dict:
    """Arm L: labels only, no AECCAR. Per-atom sums of the exact CHGCAR over
    the decoded atom map, divided by npoints as in bader_calc, against ACF."""
    import qoac_b_core as qb
    c_vol = label_map_cost(bin_vol)
    c_atom = label_map_cost(bin_atom)
    dec_atom, atom_xz = label_roundtrip(bin_atom)
    dec_vol, vol_xz = label_roundtrip(bin_vol)
    sums = qb.side_channel_from_field(chg, dec_atom).sums
    full = np.zeros(natoms + 2)
    full[:sums.size] = sums
    q_lab = full[1:natoms + 1] / chg.size
    err = float(np.max(np.abs(q_lab - q_ref))) if natoms else 0.0
    # every Bader volume must map to one atom (consistency of the two stored maps)
    pairs = np.unique(np.stack([dec_vol.ravel(), dec_atom.ravel()]), axis=1)
    vol_to_atom_function = bool(np.unique(pairs[0]).size == pairs.shape[1])
    return {"label_ctx_bytes_volnum": c_vol["ctx_bytes"], "label_lzma_bytes_volnum": c_vol["lzma_bytes"],
            "label_ctx_bytes_atom": c_atom["ctx_bytes"], "label_lzma_bytes_atom": c_atom["lzma_bytes"],
            "label_boundary_voxels_volnum": c_vol["boundary_voxels"],
            "label_roundtrip_xz_bytes_atom": atom_xz, "label_roundtrip_xz_bytes_volnum": vol_xz,
            "label_roundtrip_exact": bool(np.array_equal(dec_atom, bin_atom) and np.array_equal(dec_vol, bin_vol)),
            "label_charge_err_max_e": err, "label_charges_match_binary": bool(err <= CHARGE_MATCH_TOL_E),
            "vol_to_atom_is_function": vol_to_atom_function,
            "label_charges_e": q_lab.tolist()}


def run_arms(mid, ref, chg_size, natoms, gate0, label_rec, ref_out, bader_fn, deltas=DELTAS) -> tuple[list, list]:
    """A2 and A1 rows for every delta. ``bader_fn(decoded_ref_c_order)`` must
    return (charges, volnum_c, atom_c, nbasins). ``ref_out`` is the reference
    binary output tuple of the same form."""
    q_ref, vol_ref, atom_ref, nb_ref = ref_out
    rows, failures = [], []
    gamma, vac_margin = robust_margins(ref)
    floor = base_floor(ref)
    t = time.perf_counter()
    allow = oneshot_allowance(ref)
    allow_seconds = time.perf_counter() - t
    common = {"material_id": mid, "npoints": int(chg_size), "natoms": int(natoms),
              "gate0_regular": gate0.get("regular"), "gate0_fast_volnum_agreement": gate0.get("fast_volnum_agreement"),
              "raw_ref_bytes": int(ref.f.size * 8), "nbasins_reference": int(nb_ref),
              "label_ctx_bytes_volnum": label_rec.get("label_ctx_bytes_volnum"),
              "label_ctx_bytes_atom": label_rec.get("label_ctx_bytes_atom")}
    for delta in deltas:
        try:
            t = time.perf_counter()
            qidx, g0, eps = rel_quantize(ref.f, delta, floor)
            base = lorenzo_bytes(qidx.reshape(ref.shape))
            base_seconds = time.perf_counter() - t
            t = time.perf_counter()
            qb0, vb0, ab0, _ = bader_fn(g0.reshape(ref.shape))
            before = {"reassigned_volnum_frac_before": float(np.mean(vb0 != vol_ref)),
                      "reassigned_atom_frac_before": float(np.mean(ab0 != atom_ref)),
                      "bader_charge_err_max_e_before": float(np.max(np.abs(qb0 - q_ref)))}
            before_seconds = time.perf_counter() - t
        except Exception as e:  # noqa: BLE001
            failures.append({"stage": f"base delta={delta}", "error": f"{type(e).__name__}: {e}",
                             "traceback": traceback.format_exc()})
            for arm in ARMS:
                rows.append({**common, "arm": arm, "delta": delta, "status": "FAILED", "error": f"base: {e}"})
            continue
        for arm in ARMS:
            row = {**common, "arm": arm, "delta": delta, "status": "OK", "error": "", "base_bytes": int(base),
                   **before}
            try:
                t = time.perf_counter()
                kw = {"level0": oneshot_levels(allow, eps)} if arm == "A1" else {}
                r = correct(ref, eps, tier="B", margin=gamma, vac_margin=vac_margin, g0=g0, **kw)
                enc = time.perf_counter() - t + base_seconds + (allow_seconds if arm == "A1" else 0.0)
                g = r.g.ravel()
                t = time.perf_counter()
                qd, vd, ad, nbd = bader_fn(r.g)
                bsec = time.perf_counter() - t
                err = np.abs(g - ref.f)
                nz = np.abs(ref.f) > 0
                row.update(side_bytes=int(r.side_bytes), side_over_base=r.side_bytes / max(base, 1),
                           total_bytes=int(base + r.side_bytes),
                           reassigned_volnum_frac=float(np.mean(vd != vol_ref)),
                           reassigned_atom_frac=float(np.mean(ad != atom_ref)),
                           reassigned_volnum_voxels=int(np.count_nonzero(vd != vol_ref)),
                           nbasins_decoded=int(nbd), bader_charge_err_max_e=float(np.max(np.abs(qd - q_ref))),
                           linf_over_bound=float(np.max(err / np.maximum(np.broadcast_to(eps, err.shape), 1e-300))),
                           max_pointwise_rel_err=float(np.max(err[nz] / np.abs(ref.f[nz]))) if nz.any() else 0.0,
                           iterations=int(r.iterations), edits=int(r.n_edits),
                           edits_by_level=json.dumps(r.edits_by_level, sort_keys=True),
                           encode_seconds=enc, bader_seconds=bsec + before_seconds / len(ARMS))
            except Exception as e:  # noqa: BLE001
                row.update(status="FAILED", error=f"{type(e).__name__}: {e}")
                failures.append({"stage": f"{arm} delta={delta}", "error": row["error"],
                                 "traceback": traceback.format_exc()})
            rows.append(row)
    return rows, failures


# --------------------------------------------------------------------------
# CSV and aggregate (pure)
# --------------------------------------------------------------------------

def _cell(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return repr(v) if math.isfinite(v) else str(v)
    return v


def write_csv(rows, path: Path, fields):
    with Path(path).open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: _cell(r.get(k)) for k in fields})


def _median(xs):
    xs = [float(x) for x in xs if x is not None and x != "" and math.isfinite(float(x))]
    return float(np.median(xs)) if xs else None


def _max(xs):
    xs = [float(x) for x in xs if x is not None and x != "" and math.isfinite(float(x))]
    return float(np.max(xs)) if xs else None


def aggregate(results: list[dict], expected: list[str] | None = None) -> tuple[dict, list, list, list]:
    """Merge per-material results. Returns (summary, rows, gate0_rows, failures).
    The summary states Gate 0 agreement statistics and descriptive per-arm
    statistics only; it declares no pass/fail outcome for any other gate."""
    rows, gate0, failures = [], [], []
    seen = set()
    for res in sorted(results, key=lambda r: r.get("material_id", "")):
        mid = res.get("material_id")
        seen.add(mid)
        rows.extend(res.get("rows", []))
        if res.get("gate0"):
            gate0.append(res["gate0"])
        for f in res.get("failures", []):
            failures.append({"material_id": mid, "stage": f.get("stage", ""), "error": f.get("error", "")})
    for mid in sorted(set(expected or []) - seen):
        failures.append({"material_id": mid, "stage": "missing", "error": "no result file"})
    ok_g0 = [g for g in gate0 if g.get("status") == "OK"]
    lit = [g for g in ok_g0 if g.get("literal_run")]
    g0 = {
        "materials_with_gate0": len(ok_g0),
        "regular_R1_R2": sum(bool(g.get("regular")) for g in ok_g0),
        "R1_violations_total": sum(int(g.get("R1_violations") or 0) for g in ok_g0),
        "R2_violations_total": sum(int(g.get("R2_violations") or 0) for g in ok_g0),
        "fast_volnum_identical": sum(int(g.get("fast_volnum_mismatch_voxels") or 0) == 0 for g in ok_g0),
        "fast_atom_identical": sum(int(g.get("fast_atom_mismatch_voxels") or 0) == 0 for g in ok_g0),
        "fast_nbasins_equal": sum(g.get("nbasins_fast") == g.get("nbasins_binary") for g in ok_g0),
        "fast_maxima_match": sum(bool(g.get("fast_maxima_match")) for g in ok_g0),
        "fast_volnum_agreement_min": min((g["fast_volnum_agreement"] for g in ok_g0), default=None),
        "fast_volnum_agreement_median": _median([g["fast_volnum_agreement"] for g in ok_g0]),
        "fast_volnum_mismatch_voxels_total": sum(int(g.get("fast_volnum_mismatch_voxels") or 0) for g in ok_g0),
        "fast_atom_agreement_min": min((g["fast_atom_agreement"] for g in ok_g0), default=None),
        "bcf_maxima_matched_total": sum(int(g.get("bcf_maxima_matched") or 0) for g in ok_g0),
        "bcf_maxima_total": sum(int(g.get("bcf_maxima_total") or 0) for g in ok_g0),
        "literal_run": len(lit),
        "literal_skipped": len(ok_g0) - len(lit),
        "literal_volnum_identical": sum(int(g.get("literal_volnum_mismatch_voxels") or 0) == 0 for g in lit),
        "literal_vs_fast_identical": sum(int(g.get("literal_vs_fast_mismatch_voxels") or 0) == 0 for g in lit),
        "literal_max_npoints": LITERAL_MAX_NPOINTS,
    }
    arms = {}
    for arm in ARMS:
        for delta in sorted({float(r["delta"]) for r in rows if r.get("arm") == arm}):
            rs = [r for r in rows if r.get("arm") == arm and float(r["delta"]) == delta]
            ok = [r for r in rs if r.get("status") == "OK"]
            arms[f"{arm}@{delta:g}"] = {
                "rows": len(rs), "ok": len(ok),
                "zero_reassignment_volnum": sum(float(r["reassigned_volnum_frac"]) == 0.0 for r in ok),
                "zero_reassignment_atom": sum(float(r["reassigned_atom_frac"]) == 0.0 for r in ok),
                "max_reassigned_volnum_frac": _max([r["reassigned_volnum_frac"] for r in ok]),
                "median_reassigned_volnum_frac_before": _median([r.get("reassigned_volnum_frac_before") for r in ok]),
                "max_bader_charge_err_e": _max([r["bader_charge_err_max_e"] for r in ok]),
                "median_base_bytes": _median([r["base_bytes"] for r in ok]),
                "median_side_bytes": _median([r["side_bytes"] for r in ok]),
                "median_side_over_base": _median([r["side_over_base"] for r in ok]),
                "median_total_over_label_ctx_atom": _median(
                    [float(r["total_bytes"]) / float(r["label_ctx_bytes_atom"]) for r in ok
                     if r.get("label_ctx_bytes_atom") not in (None, "", 0)]),
                "max_linf_over_bound": _max([r["linf_over_bound"] for r in ok]),
                "max_iterations": _max([r["iterations"] for r in ok]),
                "median_encode_seconds": _median([r["encode_seconds"] for r in ok]),
            }
    arm_l = [res["arm_L"] for res in results if res.get("arm_L")]
    summary = {
        "study": "QOAC-B3 real engineering (DESIGN_STUDY.md section 7, Gate 0 + descriptive arms)",
        "materials_expected": len(expected) if expected is not None else None,
        "materials_with_results": len(results),
        "materials_success": sum(r.get("status") == "SUCCESS" for r in results),
        "failures": len(failures),
        "gate0": g0,
        "arms": arms,
        "arm_L": {
            "materials": len(arm_l),
            "charges_match_binary": sum(bool(a.get("label_charges_match_binary")) for a in arm_l),
            "max_label_charge_err_e": _max([a.get("label_charge_err_max_e") for a in arm_l]),
            "roundtrip_exact": sum(bool(a.get("label_roundtrip_exact")) for a in arm_l),
            "median_label_ctx_bytes_atom": _median([a.get("label_ctx_bytes_atom") for a in arm_l]),
            "median_label_ctx_bytes_volnum": _median([a.get("label_ctx_bytes_volnum") for a in arm_l]),
        },
        "note": "No pass/fail gate other than the Gate 0 agreement statistics is evaluated.",
    }
    return summary, rows, gate0, failures


# --------------------------------------------------------------------------
# Binary driver and material run (network + binary; not unit-tested)
# --------------------------------------------------------------------------

class Binary:
    """Run the compiled Henkelman binary on (CHGCAR, REFCAR). CHGCAR is written
    once; REFCAR is rewritten for every call."""

    def __init__(self, bader, chg, lattice, frac, symbols, work: Path):
        from run_engineering import write_chgcar
        self.bader = Path(bader); self.lattice = lattice; self.frac = frac; self.symbols = symbols
        self.shape = chg.shape; self.work = work; self.n = 0
        self.write = write_chgcar
        write_chgcar(work / "CHGCAR", chg, lattice, frac, symbols)

    def __call__(self, ref_field):
        from run_engineering import read_atindex
        import qoac_b_core as qb
        w = self.work
        for p in list(w.glob("*.dat")) + [w / "REFCAR"]:
            if p.exists():
                p.unlink()
        self.write(w / "REFCAR", np.asarray(ref_field, dtype=np.float64).reshape(self.shape),
                   self.lattice, self.frac, self.symbols)
        cmd = [str(self.bader), "CHGCAR", "-ref", "REFCAR", "-b", "ongrid", "-vac", "0.001",
               "-p", "atom_index", "-p", "bader_index"]
        with (w / "bader.log").open("w") as fh:
            rc = subprocess.call(cmd, cwd=w, stdout=fh, stderr=subprocess.STDOUT)
        log = (w / "bader.log").read_text()
        if rc:
            raise RuntimeError(f"Henkelman exit {rc}: " + log[-500:])
        self.n += 1
        q = parse_acf((w / "ACF.dat").read_text(), len(self.symbols))
        atom = qb.label_grid_from_fortran_flat(read_atindex(w / "AtIndex.dat", self.shape), self.shape)
        vol = qb.label_grid_from_fortran_flat(read_atindex(w / "BvIndex.dat", self.shape), self.shape)
        self.last_bcf = parse_bcf((w / "BCF.dat").read_text())
        return q, vol, atom, parse_nbasins(log)


def run_material(meta: dict, bader: Path, repo: Path, frozen: Path, deltas=DELTAS) -> dict:
    from run_engineering import fetch
    sys.path.insert(0, str(frozen / "validation"))
    sys.path.insert(0, str(repo / "validation" / "qsq_prospective"))
    import development_compatibility_smoke as dev

    mid = meta["material_id"]; task_id = meta["task_id"]
    t0 = time.time()
    res = {"material_id": mid, "status": "SUCCESS", "rows": [], "gate0": None, "arm_L": None, "failures": []}
    stage = "download"
    try:
        chg_blob = fetch(meta["url"])
        if hashlib.sha256(chg_blob).hexdigest() != meta["sha256"] or len(chg_blob) != int(meta["source_bytes"]):
            raise RuntimeError("CHGCAR sha256/byte mismatch against manifest")
        a0 = fetch(BUCKET + f"aeccar0s/{task_id}.json.gz")
        a2 = fetch(BUCKET + f"aeccar2s/{task_id}.json.gz")
        res.update(chgcar_sha256=meta["sha256"], aeccar0_sha256=hashlib.sha256(a0).hexdigest(),
                   aeccar2_sha256=hashlib.sha256(a2).hexdigest())
        with tempfile.TemporaryDirectory(prefix="qoacb3_") as td:
            work = Path(td)
            stage = "decode"
            grid, _ = dev.build_grid(meta, chg_blob, work)
            chg = np.ascontiguousarray(np.asarray(grid.total, dtype=np.float64))
            ae = (np.asarray(dev.decode_mp_chgcar(a0).data["total"], dtype=np.float64)
                  + np.asarray(dev.decode_mp_chgcar(a2).data["total"], dtype=np.float64))
            ae = np.ascontiguousarray(ae)
            if ae.shape != chg.shape or not np.all(np.isfinite(ae)):
                raise RuntimeError("invalid AECCAR (shape or non-finite)")
            st = grid.structure
            lattice = np.asarray(st.lattice.matrix, float); frac = np.asarray(st.frac_coords, float)
            symbols = [s.specie.symbol for s in st]
            res.update(npoints=int(chg.size), natoms=len(symbols), shape=list(chg.shape))
            stage = "reference binary"
            B = Binary(bader, chg, lattice, frac, symbols, work)
            t = time.perf_counter()
            ref_out = B(ae)
            res["reference_bader_seconds"] = time.perf_counter() - t
            q_ref, vol_ref, atom_ref, nb_ref = ref_out
            res["reference_q"] = q_ref.tolist(); res["reference_nbasins"] = nb_ref
            bcf = B.last_bcf
            stage = "gate0"
            try:
                g0, ref = gate0_record(mid, ae, lattice, frac, vol_ref, atom_ref, nb_ref, bcf)
            except Exception as e:  # noqa: BLE001
                res["failures"].append({"stage": "gate0", "error": f"{type(e).__name__}: {e}",
                                        "traceback": traceback.format_exc()})
                g0 = {"material_id": mid, "status": "FAILED", "npoints": int(chg.size)}
                ref = make_reference(ae, lattice, VACVAL)
            res["gate0"] = g0
            stage = "arm L"
            try:
                res["arm_L"] = arm_l_record(chg, vol_ref, atom_ref, q_ref, len(symbols))
            except Exception as e:  # noqa: BLE001
                res["failures"].append({"stage": "arm L", "error": f"{type(e).__name__}: {e}",
                                        "traceback": traceback.format_exc()})
                res["arm_L"] = {}
            stage = "arms A2/A1"
            rows, fails = run_arms(mid, ref, chg.size, len(symbols), g0, res["arm_L"], ref_out, B, deltas)
            res["rows"] = rows; res["failures"].extend(fails)
            res["bader_solves"] = B.n
    except Exception as e:  # noqa: BLE001
        res["failures"].append({"stage": stage, "error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()})
    if res["failures"]:
        res["status"] = "FAILED" if (res["gate0"] is None or not res["rows"]) else "PARTIAL"
    res["wall_seconds"] = time.time() - t0
    return res


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def write_material(res: dict, outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    mid = res["material_id"]
    (outdir / f"{mid}.json").write_text(json.dumps(res, indent=2, default=_json_default) + "\n", encoding="utf-8")
    write_csv(res.get("rows", []), outdir / f"{mid}_rows.csv", ROW_FIELDS)


def write_aggregate(results, expected, outdir: Path) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    summary, rows, gate0, failures = aggregate(results, expected)
    write_csv(rows, outdir / "rows.csv", ROW_FIELDS)
    write_csv(gate0, outdir / "gate0.csv", GATE0_FIELDS)
    write_csv(failures, outdir / "failures.csv", ["material_id", "stage", "error"])
    (outdir / "SUMMARY.json").write_text(json.dumps(summary, indent=2, default=_json_default) + "\n", encoding="utf-8")
    return summary


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run one material")
    r.add_argument("--repo-root", type=Path, required=True)
    r.add_argument("--frozen-root", type=Path, required=True)
    r.add_argument("--manifest", type=Path, required=True)
    r.add_argument("--index", type=int, required=True)
    r.add_argument("--bader", type=Path, required=True)
    r.add_argument("--output-dir", type=Path, required=True)
    a = sub.add_parser("aggregate", help="merge per-material JSON files")
    a.add_argument("--manifest", type=Path, required=True)
    a.add_argument("--inputs-root", type=Path, required=True)
    a.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args(argv)
    manifest = list(csv.DictReader(args.manifest.read_text(encoding="utf-8").splitlines()))
    if args.cmd == "run":
        if not 0 <= args.index < len(manifest):
            raise SystemExit("manifest index out of range")
        res = run_material(manifest[args.index], args.bader, args.repo_root.resolve(), args.frozen_root.resolve())
        write_material(res, args.output_dir.resolve())
        print("QOAC_B3_DONE", res["material_id"], res["status"], "rows", len(res["rows"]),
              "failures", len(res["failures"]), flush=True)
        return 0
    results = []
    for path in sorted(Path(args.inputs_root).rglob("*.json")):
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(d, dict) and "material_id" in d and "rows" in d:
            results.append(d)
    summary = write_aggregate(results, [m["material_id"] for m in manifest], args.output_dir)
    print(json.dumps(summary["gate0"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
