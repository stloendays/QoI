#!/usr/bin/env python3
"""Synthetic QOAC-B3 design study (no material data).

For random smooth periodic fields on non-orthogonal lattices, compare:
  A2-B  iterative basin-faithful correction (tier B)
  A2-S  iterative successor-exact correction (tier S)
  A1    one-shot margin allowance (tier B witness), codec-agnostic
  L     lossless label map (alternative contract)
under an absolute and a pointwise-relative base quantizer.
Writes results/synthetic_study.json and results/synthetic_study.md.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from b3_correct import (correct, label_map_cost, lorenzo_bytes, make_reference,
                        oneshot_allowance, oneshot_levels, quantize, rel_quantize)
from ongrid import atom_map, ongrid_literal, ongrid_partition, regularity_report
from synthetic import LATTICES, make_lattice, random_field

VAC = 1e-3
SHAPE = (32, 30, 34)
SEEDS = range(4)
SETTINGS = [("abs", 1e-4), ("abs", 1e-3), ("abs", 1e-2), ("rel", 1e-3), ("rel", 1e-2), ("rel", 5e-2)]


def main():
    out = Path(__file__).with_name("results")
    out.mkdir(exist_ok=True)
    rows = []
    t0 = time.time()
    for kind in LATTICES:
        for seed in SEEDS:
            rng = np.random.default_rng(1000 * LATTICES.index(kind) + seed)
            L = make_lattice(kind, rng, scale=9.0)
            f, frac = random_field(SHAPE, L, rng, n_atoms=int(rng.integers(4, 8)), vacuum_slab=bool(seed % 2))
            reg = regularity_report(f, L, VAC)
            ref = make_reference(f, L, VAC)
            amap = atom_map(ref.part, L, frac)
            lab = label_map_cost(ref.part.volnum)
            allow = oneshot_allowance(ref)
            for mode, par in SETTINGS:
                if mode == "abs":
                    eps = par * f.max()
                    q, g0 = quantize(f, eps)
                else:
                    q, g0, eps = rel_quantize(f.ravel(), par, 1e-9 * f.max())
                base = lorenzo_bytes(q.reshape(f.shape))
                pb = ongrid_partition(g0.reshape(f.shape), L, VAC)
                atom_before = float(np.mean(atom_map(pb, L, frac) != amap))
                row = {"lattice": kind, "seed": seed, "npts": int(f.size), "nbasins": ref.part.nbasins,
                       "vacuum_frac": float(np.mean(ref.part.vacuum)), "regular": reg["regular"],
                       "mode": mode, "bound": par, "base_bytes": base,
                       "atom_reassigned_before": atom_before,
                       "volnum_mismatch_before": float(np.mean(pb.volnum != ref.part.volnum)),
                       "label_ctx_bytes": lab["ctx_bytes"], "label_lzma_bytes": lab["lzma_bytes"],
                       "label_boundary_voxels": lab["boundary_voxels"]}
                arms = {"A2B": dict(tier="B"), "A2S": dict(tier="S"),
                        "A1": dict(tier="B", level0=oneshot_levels(allow, eps))}
                for name, kw in arms.items():
                    r = correct(ref, eps, g0=g0, **kw)
                    p = ongrid_partition(r.g, L, VAC)
                    ok = bool(np.array_equal(p.volnum, ref.part.volnum))
                    atom_ok = bool(np.array_equal(atom_map(p, L, frac), amap))
                    lit_ok = None
                    if name in ("A2B", "A1") and par in (1e-2,):
                        lit_ok = bool(np.array_equal(ongrid_literal(r.g, L, VAC)[0], ref.part.volnum))
                    linf_over_eps = float(np.max(np.abs(r.g.ravel() - ref.f) / np.maximum(np.broadcast_to(eps, ref.f.shape), 1e-300)))
                    row[name] = {"zero_reassignment": ok, "atom_map_identical": atom_ok, "literal_identical": lit_ok,
                                 "iterations": r.iterations, "edits": r.n_edits, "edits_by_level": r.edits_by_level,
                                 "side_bytes": r.side_bytes, "linf_over_bound": linf_over_eps}
                rows.append(row)
                print(kind, seed, mode, par, "base", base, {k: (row[k]["side_bytes"], row[k]["zero_reassignment"]) for k in arms},
                      "L", lab["ctx_bytes"], f"{time.time() - t0:.0f}s", flush=True)
    (out / "synthetic_study.json").write_text(json.dumps(rows, indent=1))
    summarize(rows, out / "synthetic_study.md")


def summarize(rows, path):
    lines = ["| base | bound | fields | atom reass. before (median) | A2-B zero reass. | A2-B side B (median) | A2-B side/base | A2-S side B | A1 side B | A1 extra iters (max) | L ctx B (median) | L / base |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for mode, par in SETTINGS:
        rs = [r for r in rows if r["mode"] == mode and r["bound"] == par]
        med = lambda xs: float(np.median(xs))
        lines.append("| {} | {:g} | {} | {:.3f} | {}/{} | {:.0f} | {:.3f} | {:.0f} | {:.0f} | {} | {:.0f} | {:.3f} |".format(
            mode, par, len(rs), med([r["atom_reassigned_before"] for r in rs]),
            sum(r["A2B"]["zero_reassignment"] and r["A2S"]["zero_reassignment"] and r["A1"]["zero_reassignment"] for r in rs), len(rs),
            med([r["A2B"]["side_bytes"] for r in rs]), med([r["A2B"]["side_bytes"] / r["base_bytes"] for r in rs]),
            med([r["A2S"]["side_bytes"] for r in rs]), med([r["A1"]["side_bytes"] for r in rs]),
            max(r["A1"]["iterations"] for r in rs),
            med([r["label_ctx_bytes"] for r in rs]), med([r["label_ctx_bytes"] / r["base_bytes"] for r in rs])))
    lit = [r[a]["literal_identical"] for r in rows for a in ("A2B", "A1") if r[a]["literal_identical"] is not None]
    lines.append("")
    lines.append(f"Literal-Fortran-transcription cross-check of corrected fields: {sum(lit)}/{len(lit)} identical.")
    lines.append(f"All reference fields regular (R1, R2): {all(r['regular'] for r in rows)}.")
    lines.append(f"Max Linf / bound over all corrected fields: {max(r[a]['linf_over_bound'] for r in rows for a in ('A2B','A2S','A1')):.6f}.")
    lines.append(f"Grid {rows[0]['npts']} voxels; basins per field: {min(r['nbasins'] for r in rows)}-{max(r['nbasins'] for r in rows)}.")
    path.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
