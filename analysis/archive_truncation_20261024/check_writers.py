#!/usr/bin/env python3
"""Known-answer check: writers T (A2) and O (A3) of run_archive_truncation.py reproduce the law protocol's recorded
certified stream sizes on P1 materials (`analysis/general_qoac_law/results/run_P1_CONFIRMATORY/part_a_rows.csv`).

    python check_writers.py --repo-root R --frozen-root F --cache DIR [--materials mp-2475284 ...] [--out check.json]
Exit 0 only if every (material, writer, tau) reproduces the recorded bytes within max(3 bytes, 0.1%)
(zlib builds can differ by a few bytes; the archive-law regenerations matched within 0.016%).
"""
import argparse
import csv
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_archive_truncation as A  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--frozen-root", type=Path, required=True)
    ap.add_argument("--cache", type=Path, required=True)
    ap.add_argument("--materials", nargs="*", default=["mp-2475284", "mp-1790941"])
    ap.add_argument("--taus", nargs="*", type=float, default=[1e-6, 1e-4])
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    repo = a.repo_root.resolve()
    S = A.load_stack(repo, a.frozen_root.resolve())
    sys.path.insert(0, str(repo / "validation" / "qsq_prospective"))
    import development_compatibility_smoke as dev
    man = {r["material_id"]: r for r in csv.DictReader(open(repo / "analysis/fresh_population_20261006/P1_CONFIRMATORY_MANIFEST.csv", encoding="utf-8"))}
    rec_rows = [r for r in csv.DictReader(open(repo / "analysis/general_qoac_law/results/run_P1_CONFIRMATORY/part_a_rows.csv", encoding="utf-8"))
                if r["certified"] == "True"]
    a.cache.mkdir(parents=True, exist_ok=True)
    out, ok = [], True
    for mid in a.materials:
        meta = man[mid]
        cp = a.cache / f"{mid}.src"
        blob = cp.read_bytes() if cp.exists() else dev.fetch_exact(meta["url"], meta["sha256"], int(meta["source_bytes"]))
        cp.write_bytes(blob)
        with tempfile.TemporaryDirectory() as td:
            grid, _ = dev.build_grid(meta, blob, Path(td))
            x = np.ascontiguousarray(np.asarray(grid.total, dtype=np.float64))
            lat = np.asarray(grid.structure.lattice.matrix, float)
        v02, v3, RC = S["v02"], S["v3"], S["RC"]
        rh, rs = v02.reference_hartree_rms(x, lat)
        ptp = float(np.ptp(x))
        prep = RC.F.prepare_field(x, lat)
        an = v3.analyze(x, lat, prior="operator", reference_historical_rms=rh, d_floor_rel=1e-3 * min(RC.TAUS) ** 2 / 32)
        for tau in a.taus:
            for w, arm in (("T", "A2"), ("O", "A3")):
                res = A.writer_T(S, prep, x, lat, rh, rs, ptp, tau) if w == "T" else A.writer_O(S, an, x, lat, rh, rs, tau)
                recorded = min(int(r["bytes"]) for r in rec_rows if r["material_id"] == mid and r["arm"] == arm
                               and float(r["tau"]) == tau)
                got = res["bytes"] if res else None
                match = got is not None and abs(got - recorded) <= max(3, 1e-3 * recorded)
                ok &= match
                out.append({"material_id": mid, "writer": w, "arm": arm, "tau": tau, "bytes": got,
                            "recorded": recorded, "match": match, "param": res["param"] if res else ""})
                print(out[-1], flush=True)
    if a.out:
        a.out.write_text(json.dumps({"ok": ok, "rows": out}, indent=1) + "\n", encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
