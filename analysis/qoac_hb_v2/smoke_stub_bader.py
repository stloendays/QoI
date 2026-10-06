#!/usr/bin/env python3
"""Plumbing smoke test of run_joint_v2 with a stub Bader solver (no Fortran Henkelman binary on this machine).

The stub replaces run_engineering.Solver: labels are the 8 grid octants (1..8, Fortran flat order, as
AtIndex.dat) and "charges" are the octant sums / npoints. Its numbers have no scientific meaning; the test only
checks that the runner completes with zero failures and that the outputs have the expected shape.

    python smoke_stub_bader.py --frozen-root D:\\Research\\QoI-final4-local\\frozen_repo --output-dir <dir>
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import run_joint_v2 as rj  # noqa: E402

MATERIAL = "mp-10761"


class StubSolver:
    def __init__(self, bader, lattice, frac, symbols, shape, work):
        self.shape = tuple(int(v) for v in shape)
        idx = np.indices(self.shape)
        oct_ = sum(((idx[k] >= self.shape[k] // 2).astype(np.int64) << k) for k in range(3)) + 1
        self.labels = oct_
        self.flat = oct_.ravel(order="F").astype(np.int32)
        self.n = 0

    def __call__(self, field, reference):
        self.n += 1
        s = np.bincount(self.labels.ravel(), weights=np.asarray(field, float).ravel(), minlength=9)[1:]
        return s / float(np.prod(self.shape)), self.flat.copy()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--frozen-root", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--mu", nargs="+", default=["1e-6", "1e-2", "1"])
    a = p.parse_args()
    rj.b1.Solver = StubSolver
    t0 = time.time()
    rj.main(["--repo-root", str(REPO), "--frozen-root", str(a.frozen_root),
             "--manifest", str(REPO / "analysis/operator_aware_bader_fixed_partition/results/ENGINEERING_MANIFEST.csv"),
             "--material-id", MATERIAL, "--bader", "stub", "--output-dir", str(a.output_dir), "--mu", *a.mu])
    wall = time.time() - t0

    def read(name):
        with open(a.output_dir / f"{name}_shard_00.csv", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    mats, rows, sel, bad, fails = (read(n) for n in ("materials", "rows", "selected", "bader", "failures"))
    mus = [float(m) for m in a.mu]
    posts = rj.post_names(mus)
    bases = list(rj.REGISTRY)
    fails = [f for f in fails if f.get("material_id")]
    assert len(mats) == 1 and mats[0]["status"] == "SUCCESS", mats
    assert not fails, fails
    m = mats[0]
    n_cand = {b: len({r["param"] for r in rows if r["base"] == b}) for b in bases}
    assert n_cand["J"] == len(rj.ALPHA_REL) and n_cand["T1"] == len(rj.ALPHA_REL) * len(rj.Q_CUTS) and n_cand["GP"] > 0, n_cand
    per_param = 1 + 1 + len(mus) + 2 * (1 + len(mus))  # none, uniform, hap*, ctp-uniform (U,P), ctp-hap* (U,P)
    assert len(rows) == sum(n_cand.values()) * per_param, (len(rows), n_cand, per_param)
    assert sorted((s["base"], s["post"]) for s in sel) == sorted((b, q) for b in bases for q in posts)
    for r in rows:
        if r["stored"] != "U":
            assert float(r["closure_scaled"]) <= rj.CLOSURE, r
    for b in bad:
        assert int(b["attempt"]) <= rj.MAX_ATTEMPTS
    print(f"SMOKE OK material={MATERIAL} npoints={m['npoints']} regions={m['n_regions']} candidates={n_cand} "
          f"rows={len(rows)} selected={len(sel)} certified={sum(s['certified'] == 'True' for s in sel)} "
          f"bader_attempt_rows={len(bad)} stub_bader_solves={m['bader_solves']}")
    print(f"runtime: material {float(m['seconds']):.1f} s (wall incl. download {wall:.1f} s); "
          f"HAP precompute {float(m['hap_precompute_seconds']):.2f} s for {len(mus)} mu; "
          f"{m['projections_applied']} projections in {float(m['projection_seconds_total']):.1f} s")
    print("gram condition:", {k: f"{float(v):.3g}" for k, v in m.items() if k.startswith("gram_cond")})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
