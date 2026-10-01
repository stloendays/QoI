#!/usr/bin/env python3
"""WP-I on Vanda: perturb only the partition-defining all-electron reference.

Self-contained staging semantics:
  charge field: exact CHGCAR
  partition field: AECCAR0 + AECCAR2 + frozen WP-G reference perturbation

The stage directory contains:
  frozen/                  exact decoder/runtime copied from commit 893f931
  reference_source/bader   Henkelman Bader 1.05 binary
  inputs/                  SHA-verified CHGCAR/AECCAR payloads
  tasks.json               WP-G task registry with AECCAR hashes
  wpg_reference.csv        completed WP-G G1/G2 floors and epsilon_AE

One exact-reference solve plus five G3 probe solves are performed per analyzable
material. No codec ladder is rerun.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import os
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "frozen"))
from development_compatibility_smoke import decode_mp_chgcar  # type: ignore  # noqa: E402

BADER = ROOT / "reference_source" / "bader"
TASKS = ROOT / "tasks.json"
WPG_REFERENCE = ROOT / "wpg_reference.csv"
INPUTS = ROOT / "inputs"
SEEDS = (20260905, 1, 2, 3, 4)
CKPT = ROOT / "results" / "checkpoints"


def write_chgcar(path, field, lattice, frac, symbols):
    groups = [(s, len(list(g))) for s, g in itertools.groupby(symbols)]
    with path.open("w") as f:
        f.write("QoI QSQ reference-only perturbation\n1.0\n")
        np.savetxt(f, lattice, fmt="%.17g")
        f.write(" ".join(s for s, n in groups) + "\n" + " ".join(str(n) for s, n in groups) + "\nDirect\n")
        np.savetxt(f, frac, fmt="%.17g")
        f.write("\n" + " ".join(map(str, field.shape)) + "\n")
        flat = field.ravel(order="F")
        end = len(flat) // 5 * 5
        np.savetxt(f, flat[:end].reshape(-1, 5), fmt="%.17g")
        if end < len(flat):
            f.write(" ".join(format(v, ".17g") for v in flat[end:]) + "\n")


def read_atindex(path, shape):
    txt = path.read_text().split("\n")
    dims = " ".join(map(str, shape))
    i = next(k for k, ln in enumerate(txt) if ln.split() == dims.split())
    vals = np.array(" ".join(txt[i + 1:]).split()[: int(np.prod(shape))], dtype=float)
    return np.rint(vals).astype(np.int32)


class Solver:
    def __init__(self, lattice, frac, symbols, shape, work):
        self.lattice = lattice
        self.frac = frac
        self.symbols = symbols
        self.shape = shape
        self.work = work
        self.n = 0

    def __call__(self, charge, ref):
        w = self.work
        for p in w.glob("*.dat"):
            p.unlink()
        write_chgcar(w / "CHGCAR", charge, self.lattice, self.frac, self.symbols)
        write_chgcar(w / "REFCAR", ref, self.lattice, self.frac, self.symbols)
        cmd = [str(BADER), "CHGCAR", "-ref", "REFCAR", "-b", "ongrid", "-vac", "0.001", "-p", "atom_index"]
        with (w / "bader.log").open("w") as f:
            rc = subprocess.call(cmd, cwd=w, stdout=f, stderr=subprocess.STDOUT)
        if rc:
            raise RuntimeError("Henkelman exit %d: %s" % (rc, (w / "bader.log").read_text()[-400:]))
        rows = [ln.split() for ln in (w / "ACF.dat").read_text().splitlines()]
        data = [[float(x) for x in r[:7]] for r in rows if len(r) >= 7 and r[0].isdigit()]
        if len(data) != len(self.symbols):
            raise RuntimeError("ACF atom count mismatch")
        self.n += 1
        return np.array([x[4] for x in data]), read_atindex(w / "AtIndex.dat", self.shape)


def ae_seed(mid, seed):
    return int.from_bytes(hashlib.sha256(("QSQ-WPG|%s|%d" % (mid, seed)).encode()).digest()[:8], "little")


def f32_eps(x):
    return float(np.max(np.abs(x.astype(np.float32).astype(np.float64) - x)))


def load(path):
    c = decode_mp_chgcar(path.read_bytes())
    return c, np.ascontiguousarray(np.asarray(c.data["total"], dtype=np.float64))


def read_wpg_reference(mid):
    with WPG_REFERENCE.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["material_id"] == mid:
                return r
    raise KeyError(mid)


def run(mid):
    tasks = json.loads(TASKS.read_text())
    task = tasks[mid]
    wpg = read_wpg_reference(mid)
    if wpg["status"] != "SUCCESS":
        return {
            "material_id": mid,
            "task_id": task["task_id"],
            "status": "FAILED",
            "stage": "wp_g_input",
            "error": "WP-G material was not analyzable",
            "probes": [],
            "wpg_status": wpg["status"],
        }

    t0 = time.time()
    out = {
        "material_id": mid,
        "task_id": task["task_id"],
        "status": "SUCCESS",
        "probes": [],
        "epsilon_ae_wp_g": float(wpg["epsilon_ae"]),
        "g1_floor_e": float(wpg["g1_floor_e"]),
        "g2_floor_e": float(wpg["g2_floor_e"]),
        "bader_sha256": hashlib.sha256(BADER.read_bytes()).hexdigest(),
        "pbs_job_id": os.environ.get("PBS_JOBID"),
    }

    try:
        chg_path = INPUTS / ("%s_chgcar.json.gz" % mid)
        a0_path = INPUTS / ("%s_aeccar0.json.gz" % mid)
        a2_path = INPUTS / ("%s_aeccar2.json.gz" % mid)
        for p, expected in (
            (chg_path, task["chgcar_sha256"]),
            (a0_path, task["aeccar0_sha256"]),
            (a2_path, task["aeccar2_sha256"]),
        ):
            got = hashlib.sha256(p.read_bytes()).hexdigest()
            if got != expected:
                raise RuntimeError("input SHA mismatch for %s" % p.name)

        cc, chg = load(chg_path)
        _, a0 = load(a0_path)
        _, a2 = load(a2_path)
        if not (chg.shape == a0.shape == a2.shape):
            raise RuntimeError("grid mismatch")
        if not (np.isfinite(a0).all() and np.isfinite(a2).all()):
            raise RuntimeError("non-finite AECCAR input")
        ae = a0 + a2
        eps_a = f32_eps(ae)
        if not np.isclose(eps_a, float(wpg["epsilon_ae"]), rtol=1e-12, atol=0.0):
            raise RuntimeError("epsilon_AE reproduction mismatch")
        st = cc.structure
        lattice = st.lattice.matrix
        frac = st.frac_coords
        symbols = [s.specie.symbol for s in st]
        out.update(shape="x".join(map(str, chg.shape)), natoms=len(symbols), epsilon_ae=eps_a)
    except Exception as e:
        out.update(status="FAILED", stage="inputs", error="%s: %s" % (type(e).__name__, e), traceback=traceback.format_exc())
        return out

    (ROOT / "temp").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="wpi_%s_" % mid, dir=ROOT / "temp") as td:
        solver = Solver(lattice, frac, symbols, chg.shape, Path(td))
        try:
            q0, l0 = solver(chg, ae)
            for seed in SEEDS:
                rng = np.random.Generator(np.random.PCG64(ae_seed(mid, seed)))
                noise = rng.uniform(-eps_a, eps_a, size=ae.shape)
                q, lab = solver(chg, ae + noise)
                response = float(np.max(np.abs(q - q0)))
                reassigned = float(np.mean(lab != l0))
                out["probes"].append({
                    "seed": seed,
                    "g3_response_e": response,
                    "g3_reassigned_frac": reassigned,
                })
            out["g3_floor_e"] = max(p["g3_response_e"] for p in out["probes"])
            out["g3_reassigned_median"] = float(np.median([p["g3_reassigned_frac"] for p in out["probes"]]))
            out["bader_solves"] = solver.n
        except Exception as e:
            out.update(status="FAILED", stage="g3", error="%s: %s" % (type(e).__name__, e), traceback=traceback.format_exc())

    out["wall_seconds"] = time.time() - t0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--material", required=True)
    a = ap.parse_args()
    CKPT.mkdir(parents=True, exist_ok=True)
    dst = CKPT / (a.material + ".json")
    if dst.exists() and json.loads(dst.read_text()).get("status") == "SUCCESS":
        print("already done", a.material)
        return
    res = run(a.material)
    tmp = dst.with_suffix(".tmp")
    tmp.write_text(json.dumps(res, indent=1))
    os.replace(tmp, dst)
    print(a.material, res["status"], "g3", res.get("g3_floor_e"), "solves", res.get("bader_solves"), flush=True)


if __name__ == "__main__":
    main()
