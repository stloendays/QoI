#!/usr/bin/env python3
"""Rerun of the two archive studies whose decoded-frame moment certificates could read a stale Bader partition:
`analysis/archive_truncation_20261024/` (writers T, O; revision 10) and `analysis/archive_waterfill_20261025/`
(writers W, Q; revision 11).

Defect (found 2026-10-25 while writing the W2 archive study): `run_spin_s1.Bader` rewrites the partition field
(REFCAR) only when the partition id changes, and `run_archive_truncation.certify_m` passes the id "dec" for every
decoded density. Within one object the first decoded density's partition (the first writer at tau_H = 1e-6) was
therefore reused for the other writer and for tau_H = 1e-4. The density streams and their Hartree certificates are
unaffected; the moment certificates of the later (writer, tau) pairs, and so their magnetization bytes, were computed
on the wrong partition.

Fix: the partition field is rewritten for every call with the id "dec" (each certify_m call then reads its own
decoded density's partition). Nothing else changes: each study's own `process` runs unchanged on the same frame,
sample, inputs and code, into new checkpoints under this directory.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
AN = HERE.parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def patch_bader(s1):
    """Rewrite the partition field on every call with the id 'dec'."""
    B = s1.Bader
    if getattr(B, "_partition_fix", False):
        return
    orig = B.__call__

    def call(self, integrand, partition_field, ref_id):
        if ref_id == "dec":
            self._ref_id = None
        return orig(self, integrand, partition_field, ref_id)

    B.__call__ = call
    B._partition_fix = True


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--study", choices=("trunc", "w1"), required=True)
    ap.add_argument("--task-id", required=True)
    ap.add_argument("--inputs", type=Path, required=True)
    ap.add_argument("--checkpoints", type=Path, required=True)
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--frozen-root", type=Path, required=True)
    ap.add_argument("--bader", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.study == "trunc":
        mod = _load("run_archive_truncation", AN / "archive_truncation_20261024" / "run_archive_truncation.py")
        RAT = mod
    else:
        mod = _load("run_archive_w1", AN / "archive_waterfill_20261025" / "run_archive_w1.py")
        RAT = mod.RAT
    rows = {x["task_id"]: x for x in RAT._read(a.repo_root / "analysis" / "scope_expansion_20261022" /
                                                 "archive_hartree_objects.csv")}
    row = rows[a.task_id]
    a.checkpoints.mkdir(parents=True, exist_ok=True)
    ck = a.checkpoints / f"{a.task_id}.json"
    if ck.exists() and json.loads(ck.read_text(encoding="utf-8")).get("status") == "SUCCESS":
        print("SKIP complete", a.task_id)
        return 0
    S = RAT.load_stack(a.repo_root.resolve(), a.frozen_root.resolve())
    patch_bader(S["s1"])
    rec = mod.process(row, a.inputs / f"{a.task_id}.json.gz", S, a.bader)
    rec["partition_fix"] = True
    tmp = ck.with_suffix(".tmp")
    tmp.write_text(json.dumps(rec, indent=1, default=float) + "\n", encoding="utf-8")
    os.replace(tmp, ck)
    print("DONE", a.task_id, rec["status"], rec.get("error", ""))
    return 0 if rec["status"] == "SUCCESS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
