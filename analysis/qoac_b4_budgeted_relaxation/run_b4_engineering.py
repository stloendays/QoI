#!/usr/bin/env python3
"""QOAC-B4 real-material engineering run (PROTOCOL.md section 4).

Reuses the QOAC-B3 real-material pipeline (download + sha256 check, decode,
compiled Henkelman Bader on (CHGCAR, REFCAR = AECCAR0 + AECCAR2), Gate 0, arm L)
and replaces its correction arms with:

* B3   : strict tier-B correction (QOAC-B3 arm A2), recomputed on the same base
         stream so that every B4 row has a paired baseline;
* B4   : budgeted leaf relaxation for every (tau_B, theta) in the grid.

For every arm the decoded partition field is handed to the compiled binary and
the per-atom Bader error against the reference ACF is recorded together with
the a-priori bound, so the guarantee is checked by the real analysis code.

``aggregate`` merges per-material JSON files into rows.csv, failures.csv and
SUMMARY.json. Descriptive only; nothing here is a pass/fail gate.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import time
import traceback
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
B3 = HERE.parent / "qoac_b3_design"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(B3))

import run_real_engineering as b3r  # noqa: E402  (QOAC-B3 runner, reused)
from b3_correct import correct, lorenzo_bytes, rel_quantize  # noqa: E402
from b4_relax import Budget, correct_budgeted  # noqa: E402

DELTAS = (1e-3, 1e-2, 5e-2)
TAUS_E = (1e-3, 1e-4)
THETAS = (0.5, 0.9)

ROW_FIELDS = [
    "material_id", "npoints", "natoms", "delta", "arm", "tau_B_e", "theta", "status", "error",
    "base_bytes", "side_bytes", "total_bytes", "label_atom_xz_bytes", "total_over_label",
    "edits", "relaxed", "iterations", "bound_e", "bader_err_max_e", "err_over_tau", "bound_over_tau",
    "certified", "atom_reassigned_voxels", "atom_changed_outside_R", "nbasins_reference", "nbasins_decoded",
    "linf_over_bound", "encode_seconds", "bader_seconds",
]


class B4Binary(b3r.Binary):
    """Same binary wrapper; additionally keeps the exact CHGCAR for the budget."""

    def __init__(self, bader, chg, lattice, frac, symbols, work):
        super().__init__(bader, chg, lattice, frac, symbols, work)
        self.chg = np.ascontiguousarray(chg, dtype=np.float64)


def run_arms_b4(mid, ref, chg_size, natoms, gate0, label_rec, ref_out, bader_fn, deltas=DELTAS):
    """Drop-in replacement for the B3 ``run_arms`` (same signature)."""
    q_ref, vol_ref, atom_ref, nb_ref = ref_out
    charge = bader_fn.chg.ravel() / bader_fn.chg.size          # bader_calc: CHGCAR / npoints
    atom_flat = np.asarray(atom_ref).ravel()
    gamma, vac_margin = b3r.robust_margins(ref)
    floor = b3r.base_floor(ref)
    label_bytes = label_rec.get("label_roundtrip_xz_bytes_atom") if label_rec else None
    common = {"material_id": mid, "npoints": int(chg_size), "natoms": int(natoms),
              "nbasins_reference": int(nb_ref), "label_atom_xz_bytes": label_bytes}
    rows, failures = [], []

    def finish(row, g, side_bytes, relaxed_flat, base, enc):
        t = time.perf_counter()
        qd, _vd, ad, nbd = bader_fn(g)
        bsec = time.perf_counter() - t
        err_e = float(np.max(np.abs(qd - q_ref))) if natoms else 0.0
        changed = np.asarray(ad).ravel() != atom_flat
        outside = int(np.count_nonzero(changed & ~relaxed_flat))
        e = np.abs(np.asarray(g).ravel() - ref.f)
        total = int(base + side_bytes)
        row.update(status="OK", side_bytes=int(side_bytes), total_bytes=total,
                   total_over_label=(total / label_bytes) if label_bytes else None,
                   bader_err_max_e=err_e, atom_reassigned_voxels=int(changed.sum()),
                   atom_changed_outside_R=outside, nbasins_decoded=int(nbd),
                   linf_over_bound=float(np.max(e / np.maximum(np.broadcast_to(eps, e.shape), 1e-300))),
                   encode_seconds=enc, bader_seconds=bsec)
        if row.get("tau_B_e"):
            row["err_over_tau"] = err_e / row["tau_B_e"]
            row["certified"] = bool(err_e < row["tau_B_e"])
        return row

    for delta in deltas:
        try:
            t = time.perf_counter()
            qidx, g0, eps = rel_quantize(ref.f, delta, floor)
            base = lorenzo_bytes(qidx.reshape(ref.shape))
            base_sec = time.perf_counter() - t
        except Exception as e:  # noqa: BLE001
            failures.append({"stage": f"base delta={delta}", "error": f"{type(e).__name__}: {e}",
                             "traceback": traceback.format_exc()})
            continue
        # strict B3 baseline on the same stream (no relaxed voxels)
        row = {**common, "delta": delta, "arm": "B3", "tau_B_e": None, "theta": 0.0, "base_bytes": int(base),
               "relaxed": 0, "bound_e": 0.0}
        try:
            t = time.perf_counter()
            r = correct(ref, eps, tier="B", margin=gamma, vac_margin=vac_margin, g0=g0)
            enc = time.perf_counter() - t + base_sec
            row.update(edits=int(r.n_edits), iterations=int(r.iterations))
            rows.append(finish(row, r.g, r.side_bytes, np.zeros(ref.f.size, bool), base, enc))
        except Exception as e:  # noqa: BLE001
            row.update(status="FAILED", error=f"{type(e).__name__}: {e}")
            failures.append({"stage": f"B3 delta={delta}", "error": row["error"], "traceback": traceback.format_exc()})
            rows.append(row)
        for tau in TAUS_E:
            for theta in THETAS:
                row = {**common, "delta": delta, "arm": "B4", "tau_B_e": tau, "theta": theta,
                       "base_bytes": int(base)}
                try:
                    t = time.perf_counter()
                    bud = Budget.make(atom_flat, charge, theta * tau, natoms)
                    r = correct_budgeted(ref, eps, bud, natoms, margin=gamma, vac_margin=vac_margin, g0=g0)
                    enc = time.perf_counter() - t + base_sec
                    row.update(edits=int(r.n_edits), relaxed=int(r.n_relaxed), iterations=int(r.iterations),
                               bound_e=r.max_atom_bound_e, bound_over_tau=r.max_atom_bound_e / tau)
                    rows.append(finish(row, r.g, r.side_bytes, r.relaxed.ravel(), base, enc))
                except Exception as e:  # noqa: BLE001
                    row.update(status="FAILED", error=f"{type(e).__name__}: {e}")
                    failures.append({"stage": f"B4 delta={delta} tau={tau} theta={theta}", "error": row["error"],
                                     "traceback": traceback.format_exc()})
                    rows.append(row)
    return rows, failures


# --------------------------------------------------------------------------
# Output and aggregate
# --------------------------------------------------------------------------

def _cell(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return repr(v) if math.isfinite(v) else str(v)
    return v


def write_csv(rows, path: Path):
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ROW_FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: _cell(r.get(k)) for k in ROW_FIELDS})


def aggregate(results: list[dict], expected: list[str]) -> tuple[dict, list, list]:
    rows = [r for res in results for r in res.get("rows", [])]
    fails = [{"material_id": res["material_id"], "stage": f["stage"], "error": f["error"]}
             for res in results for f in res.get("failures", [])]
    base = {(r["material_id"], r["delta"]): r for r in rows if r.get("arm") == "B3" and r.get("status") == "OK"}
    groups: dict = {}
    for r in rows:
        if r.get("arm") != "B4" or r.get("status") != "OK":
            continue
        b = base.get((r["material_id"], r["delta"]))
        if b is None:
            continue
        key = f"delta={r['delta']:g}|tau={r['tau_B_e']:g}|theta={r['theta']:g}"
        g = groups.setdefault(key, {"total_ratio": [], "side_ratio": [], "err_over_tau": [], "bound_over_tau": [],
                                    "certified": 0, "n": 0, "outside_R": 0, "bound_violations": 0,
                                    "total_over_label": []})
        g["n"] += 1
        g["total_ratio"].append(r["total_bytes"] / b["total_bytes"])
        g["side_ratio"].append(r["side_bytes"] / max(b["side_bytes"], 1))
        g["err_over_tau"].append(r["err_over_tau"])
        g["bound_over_tau"].append(r["bound_over_tau"])
        g["certified"] += int(bool(r["certified"]))
        g["outside_R"] += int(r["atom_changed_outside_R"])
        # actual error above the a-priori bound (+ ACF print precision 1e-6 e) would falsify the construction
        g["bound_violations"] += int(r["bader_err_max_e"] > r["bound_e"] + 2e-6)
        if r.get("total_over_label") is not None:
            g["total_over_label"].append(r["total_over_label"])
    med = lambda xs: float(np.median(xs)) if xs else None  # noqa: E731
    summary = {
        "materials_expected": len(expected),
        "materials_with_rows": len({r["material_id"] for r in rows}),
        "failures": len(fails),
        "groups": {k: {"n": g["n"], "median_total_ratio_B4_over_B3": med(g["total_ratio"]),
                       "min_total_ratio": min(g["total_ratio"]), "median_side_ratio": med(g["side_ratio"]),
                       "max_err_over_tau": max(g["err_over_tau"]), "max_bound_over_tau": max(g["bound_over_tau"]),
                       "certified": g["certified"], "atom_changes_outside_R": g["outside_R"],
                       "bound_violations": g["bound_violations"],
                       "median_total_over_label": med(g["total_over_label"])}
                   for k, g in sorted(groups.items())},
        "b3_baseline": {f"delta={d:g}": {"median_total_over_label": med([r["total_over_label"] for r in rows
                                         if r.get("arm") == "B3" and r.get("status") == "OK" and r["delta"] == d
                                         and r.get("total_over_label") is not None]),
                                         "atom_changes_outside_R": sum(int(r["atom_changed_outside_R"]) for r in rows
                                         if r.get("arm") == "B3" and r.get("status") == "OK" and r["delta"] == d)}
                        for d in DELTAS},
    }
    return summary, rows, fails


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


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--repo-root", type=Path, required=True)
    r.add_argument("--frozen-root", type=Path, required=True)
    r.add_argument("--manifest", type=Path, required=True)
    r.add_argument("--index", type=int, required=True)
    r.add_argument("--bader", type=Path, required=True)
    r.add_argument("--output-dir", type=Path, required=True)
    a = sub.add_parser("aggregate")
    a.add_argument("--manifest", type=Path, required=True)
    a.add_argument("--inputs-root", type=Path, required=True)
    a.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args(argv)
    manifest = list(csv.DictReader(args.manifest.read_text(encoding="utf-8").splitlines()))
    if args.cmd == "run":
        if not 0 <= args.index < len(manifest):
            raise SystemExit("manifest index out of range")
        # plug the B4 arms and the charge-keeping binary into the B3 pipeline
        b3r.run_arms = run_arms_b4
        b3r.Binary = B4Binary
        res = b3r.run_material(manifest[args.index], args.bader, args.repo_root.resolve(),
                               args.frozen_root.resolve(), deltas=DELTAS)
        out = args.output_dir.resolve()
        out.mkdir(parents=True, exist_ok=True)
        mid = res["material_id"]
        (out / f"{mid}.json").write_text(json.dumps(res, indent=2, default=_json_default) + "\n", encoding="utf-8")
        write_csv(res.get("rows", []), out / f"{mid}_rows.csv")
        print("QOAC_B4_DONE", mid, res["status"], "rows", len(res["rows"]), "failures", len(res["failures"]),
              flush=True)
        return 0
    results = []
    for path in sorted(Path(args.inputs_root).rglob("*.json")):
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(d, dict) and "material_id" in d and "rows" in d:
            results.append(d)
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    summary, rows, fails = aggregate(results, [m["material_id"] for m in manifest])
    write_csv(rows, out / "rows.csv")
    with (out / "failures.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["material_id", "stage", "error"])
        w.writeheader()
        w.writerows(fails)
    (out / "SUMMARY.json").write_text(json.dumps(summary, indent=2, default=_json_default) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1, default=_json_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
