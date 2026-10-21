#!/usr/bin/env python3
"""QOAC-B4 synthetic study: B3 tier-B correction (theta = 0, strict) against
B4 budgeted leaf relaxation at several budgets, on the B3 synthetic field set.

Synthetic charges are in arbitrary units, so the tolerance is set relative to
the largest atomic charge: tau = TAU_REL * max|q|. Descriptive only.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "qoac_b3_design"))

from b3_correct import correct, label_map_cost, lorenzo_bytes, make_reference, rel_quantize  # noqa: E402
from b4_relax import Budget, atom_charges, changed_only_in_R, correct_budgeted, remap_volnum  # noqa: E402
from ongrid import atom_map, ongrid_partition  # noqa: E402
from synthetic import LATTICES, make_lattice, random_field  # noqa: E402

VAC = 1e-3
SHAPE = (32, 30, 34)
SEEDS = (0, 1, 2, 3)
DELTAS = (1e-3, 1e-2, 5e-2)
TAU_REL = (1e-3, 1e-4)
THETAS = (0.1, 0.5, 1.0)


def main(out: Path = HERE / "results") -> int:
    out.mkdir(exist_ok=True)
    rows = []
    t0 = time.time()
    for kind in LATTICES:
        for seed in SEEDS:
            rng = np.random.default_rng(1000 * LATTICES.index(kind) + seed)
            L = make_lattice(kind, rng, scale=9.0)
            f, frac = random_field(SHAPE, L, rng, n_atoms=int(rng.integers(4, 8)), vacuum_slab=bool(seed % 2))
            natoms = frac.shape[0]
            ref = make_reference(f, L, VAC)
            amap = atom_map(ref.part, L, frac).ravel()
            charge = f.ravel() / f.size
            q_ref = atom_charges(charge, amap, natoms)
            lab = label_map_cost(ref.part.volnum)
            for delta in DELTAS:
                qidx, g0, eps = rel_quantize(ref.f, delta, 1e-9 * ref.f.max())
                base = lorenzo_bytes(qidx.reshape(SHAPE))
                b3 = correct(ref, eps, tier="B", g0=g0)
                common = {"lattice": kind, "seed": seed, "delta": delta, "natoms": natoms,
                          "base_bytes": base, "label_ctx_bytes": lab["ctx_bytes"],
                          "b3_side_bytes": b3.side_bytes, "b3_edits": b3.n_edits}
                for tau_rel in TAU_REL:
                    tau = tau_rel * float(np.abs(q_ref).max())
                    for theta in THETAS:
                        bud = Budget.make(amap, charge, theta * tau, natoms)
                        r = correct_budgeted(ref, eps, bud, natoms, g0=g0)
                        p = ongrid_partition(r.g, L, VAC)
                        dq = float(np.max(np.abs(atom_charges(charge, atom_map(p, L, frac).ravel(), natoms) - q_ref)))
                        rows.append({**common, "tau_rel": tau_rel, "theta": theta,
                                     "b4_side_bytes": r.side_bytes, "b4_edits": r.n_edits,
                                     "b4_relaxed": r.n_relaxed, "b4_bound_over_tau": r.max_atom_bound_e / tau,
                                     "b4_actual_dq_over_tau": dq / tau,
                                     "only_R_changed": changed_only_in_R(remap_volnum(p, ref.part), ref.part.volnum, r.relaxed),
                                     "side_ratio_b4_b3": r.side_bytes / max(b3.side_bytes, 1),
                                     "total_ratio_b4_b3": (base + r.side_bytes) / (base + b3.side_bytes)})
                print(kind, seed, delta, f"b3 side {b3.side_bytes}",
                      [(r_["tau_rel"], r_["theta"], r_["b4_side_bytes"], r_["b4_relaxed"]) for r_ in rows[-len(TAU_REL) * len(THETAS):]],
                      f"{time.time() - t0:.0f}s", flush=True)
    (out / "synthetic_study.json").write_text(json.dumps(rows, indent=1) + "\n")
    summarize(rows, out / "synthetic_study.md")
    return 0


def summarize(rows, path: Path):
    lines = ["# QOAC-B4 synthetic study (descriptive)", "",
             f"{len({(r['lattice'], r['seed']) for r in rows})} fields, grid {SHAPE}. "
             "Ratios are B4 / B3 (B3 = strict tier-B correction on the same base stream).", "",
             "| delta | tau_rel | theta | median side ratio | median total ratio | median relaxed | max bound/tau | max actual dq/tau | only R changed |",
             "|---|---|---|---|---|---|---|---|---|"]
    for delta in DELTAS:
        for tau_rel in TAU_REL:
            for theta in THETAS:
                s = [r for r in rows if r["delta"] == delta and r["tau_rel"] == tau_rel and r["theta"] == theta]
                if not s:
                    continue
                lines.append(
                    f"| {delta:g} | {tau_rel:g} | {theta:g} | {np.median([r['side_ratio_b4_b3'] for r in s]):.3f} | "
                    f"{np.median([r['total_ratio_b4_b3'] for r in s]):.3f} | {np.median([r['b4_relaxed'] for r in s]):.0f} | "
                    f"{max(r['b4_bound_over_tau'] for r in s):.3f} | {max(r['b4_actual_dq_over_tau'] for r in s):.3f} | "
                    f"{sum(r['only_R_changed'] for r in s)}/{len(s)} |")
    path.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
