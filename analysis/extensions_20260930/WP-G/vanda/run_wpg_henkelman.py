#!/usr/bin/env python3
"""WP-G on Vanda: all-electron-reference Bader with Henkelman Bader 1.05 (-b ongrid -vac 0.001), PROTOCOL.md WP-G
and DEVIATIONS.md (baderkit 0.10.2 crashes on AECCAR references).

Per material, three arms with the same binary and settings:
  V   valence reference (the reference density is the CHGCAR itself)       -- pairing arm
  G1  reference = AECCAR0 + AECCAR2, kept exact; CHGCAR perturbed / compressed
  G2  reference perturbed / compressed as well (own float32 amplitude, own relative rung)
Five frozen QSQ seeds; the material's frozen ladder rows (codec, relative rung, absolute CHGCAR bound).
One checkpoint per material (results/checkpoints/<mid>.json); a restart resumes finished materials.

    venv/bin/python run_wpg_henkelman.py --material <mid>
"""
from __future__ import annotations

import argparse
import gzip
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
import external_end_to_end as core  # noqa: E402  (frozen codec round trip, commit 893f931)
from development_compatibility_smoke import decode_mp_chgcar  # noqa: E402

BADER = ROOT / "reference_source" / "bader"
SEEDS = (20260905, 1, 2, 3, 4)
CKPT = ROOT / "results" / "checkpoints"


def write_chgcar(path, field, lattice, frac, symbols):
    """Identical to mechanism/independent_bader_20260908/run_study.py (17 significant digits, Fortran order)."""
    groups = [(s, len(list(g))) for s, g in itertools.groupby(symbols)]
    with path.open("w") as f:
        f.write("QoI independent Bader supplement\n1.0\n")
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
    return np.rint(vals).astype(np.int32)               # Fortran order, same as the written field


class Solver:
    def __init__(self, lattice, frac, symbols, shape, work):
        self.lattice, self.frac, self.symbols, self.shape, self.work = lattice, frac, symbols, shape, work
        self.n = 0
        self._ref_key = None

    def __call__(self, field, ref=None, ref_key=None):
        """Charges and per-voxel atom labels; basins from `ref` (None: the field itself)."""
        w = self.work
        for p in w.glob("*.dat"):
            p.unlink()
        write_chgcar(w / "CHGCAR", field, self.lattice, self.frac, self.symbols)
        cmd = [str(BADER), "CHGCAR"]
        if ref is not None:
            if ref_key is None or ref_key != self._ref_key:          # rewrite the reference only when it changes
                write_chgcar(w / "REFCAR", ref, self.lattice, self.frac, self.symbols)
                self._ref_key = ref_key
            cmd += ["-ref", "REFCAR"]
        cmd += ["-b", "ongrid", "-vac", "0.001", "-p", "atom_index"]
        with (w / "bader.log").open("w") as f:
            rc = subprocess.call(cmd, cwd=w, stdout=f, stderr=subprocess.STDOUT)
        if rc:
            raise RuntimeError("Henkelman exit %d: %s" % (rc, (w / "bader.log").read_text()[-400:]))
        rows = [ln.split() for ln in (w / "ACF.dat").read_text().splitlines()]
        data = [[float(x) for x in r[:7]] for r in rows if len(r) >= 7 and r[0].isdigit()]
        if len(data) != len(self.symbols) or [int(x[0]) for x in data] != list(range(1, len(self.symbols) + 1)):
            raise RuntimeError("ACF atoms/order mismatch")
        self.n += 1
        return np.array([x[4] for x in data]), read_atindex(w / "AtIndex.dat", self.shape)


def f32_eps(x):
    return float(np.max(np.abs(x.astype(np.float32).astype(np.float64) - x)))


def ae_seed(mid, seed):
    return int.from_bytes(hashlib.sha256(("QSQ-WPG|%s|%d" % (mid, seed)).encode()).digest()[:8], "little")


def load(p):
    c = decode_mp_chgcar(p.read_bytes())
    return c, np.ascontiguousarray(np.asarray(c.data["total"], dtype=np.float64))


def run(mid):
    task = json.loads((ROOT / "tasks.json").read_text())[mid]
    t0 = time.time()
    out = dict(material_id=mid, task_id=task["task_id"], status="SUCCESS", probes=[], rows=[], failures=[],
               pbs_job_id=os.environ.get("PBS_JOBID"), bader_sha256=hashlib.sha256(BADER.read_bytes()).hexdigest())
    inp = ROOT / "inputs"
    try:
        for name, sha in (("chgcar", task["chgcar_sha256"]), ("aeccar0", task["aeccar0_sha256"]), ("aeccar2", task["aeccar2_sha256"])):
            got = hashlib.sha256((inp / ("%s_%s.json.gz" % (mid, name))).read_bytes()).hexdigest()
            if got != sha:
                raise RuntimeError("%s SHA-256 %s != %s" % (name, got, sha))
        cc, chg = load(inp / ("%s_chgcar.json.gz" % mid))
        _, a0 = load(inp / ("%s_aeccar0.json.gz" % mid))
        _, a2 = load(inp / ("%s_aeccar2.json.gz" % mid))
        if not (a0.shape == a2.shape == chg.shape):
            raise RuntimeError("grid mismatch chg %s a0 %s a2 %s" % (chg.shape, a0.shape, a2.shape))
        bad = {k: int((~np.isfinite(v)).sum()) for k, v in (("aeccar0", a0), ("aeccar2", a2))}
        if any(bad.values()):                         # published AECCAR with non-finite values (DEVIATIONS.md 5)
            raise RuntimeError("non-finite AECCAR values: %s of %d voxels" % (bad, a0.size))
        ae = a0 + a2
        del a0, a2
        if abs(float(np.ptp(chg)) - task["value_ptp"]) > 1e-9 * max(1.0, abs(task["value_ptp"])):
            raise RuntimeError("CHGCAR value_ptp differs from the frozen rows")
        st = cc.structure
        lattice, frac, symbols = st.lattice.matrix, st.frac_coords, [s.specie.symbol for s in st]
        eps_c, eps_a = f32_eps(chg), f32_eps(ae)
        out.update(shape="x".join(map(str, chg.shape)), natoms=len(symbols), epsilon_chgcar=eps_c, epsilon_ae=eps_a,
                   ae_ptp=float(np.ptp(ae)), ae_min=float(ae.min()), chg_ptp=float(np.ptp(chg)))
    except Exception as e:  # noqa: BLE001
        out.update(status="FAILED", traceback=traceback.format_exc())
        out["failures"].append(dict(material_id=mid, stage="inputs", error="%s: %s" % (type(e).__name__, e)))
        return out

    with tempfile.TemporaryDirectory(prefix="wpg_%s_" % mid, dir=ROOT / "temp") as td:
        work = Path(td)
        S = Solver(lattice, frac, symbols, chg.shape, work)
        try:
            qV, lV = S(chg)                                  # V reference
            qA, lA = S(chg, ae, "ae")                        # G1/G2 reference
            out["reference"] = dict(q_valence=qV.tolist(), q_ae=qA.tolist())

            def resp(q, lab, q0, l0):
                return float(np.max(np.abs(q - q0))), float(np.mean(lab != l0))

            for s in SEEDS:
                n_c = np.random.Generator(np.random.PCG64(s)).uniform(-eps_c, eps_c, size=chg.shape)
                n_a = np.random.Generator(np.random.PCG64(ae_seed(mid, s))).uniform(-eps_a, eps_a, size=ae.shape)
                p = dict(seed=s)
                p["v_response_e"], p["v_reassigned_frac"] = resp(*S(chg + n_c), qV, lV)
                p["g1_response_e"], p["g1_reassigned_frac"] = resp(*S(chg + n_c, ae, "ae"), qA, lA)
                p["g2_response_e"], p["g2_reassigned_frac"] = resp(*S(chg + n_c, ae + n_a, "ae+n%d" % s), qA, lA)
                out["probes"].append(p)
            for arm in ("v", "g1", "g2"):
                out["%s_floor_e" % arm] = max(p["%s_response_e" % arm] for p in out["probes"])
        except Exception as e:  # noqa: BLE001
            out.update(status="FAILED", traceback=traceback.format_exc(), wall_seconds=time.time() - t0)
            out["failures"].append(dict(material_id=mid, stage="qsq", error="%s: %s" % (type(e).__name__, e)))
            return out

        ae_ptp = out["ae_ptp"]
        for r in task["rows"]:
            codec, rel, abs_c = r["codec"], r["rel"], r["abs"]
            row = dict(codec=codec, nominal_tolerance_relative=rel, nominal_tolerance_absolute=abs_c,
                       frozen_realized_Linf=r["realized_Linf"], frozen_bader_error_e=r["bader_error_e"],
                       frozen_compressed_bytes=r["compressed_bytes"])
            try:
                rc_, nb_c, _ = core.codec_roundtrip(codec.lower(), chg, abs_c, work)
                rc_ = np.asarray(rc_, dtype=np.float64)
                linf = float(np.max(np.abs(rc_ - chg)))
                row.update(realized_Linf=linf, reproduced=bool(0.95 <= linf / max(r["realized_Linf"], 1e-300) <= 1.05),
                           chgcar_bytes=int(nb_c))
                row["v_error_e"], row["v_reassigned_frac"] = resp(*S(rc_), qV, lV)
                row["g1_error_e"], row["g1_reassigned_frac"] = resp(*S(rc_, ae, "ae"), qA, lA)
                abs_a = rel * ae_ptp
                ra, nb_a, _ = core.codec_roundtrip(codec.lower(), ae, abs_a, work)
                ra = np.asarray(ra, dtype=np.float64)
                row.update(ae_abs_bound=abs_a, ae_realized_Linf=float(np.max(np.abs(ra - ae))), ae_bytes=int(nb_a))
                row["g2_error_e"], row["g2_reassigned_frac"] = resp(*S(rc_, ra, "ae:%s:%g" % (codec, rel)), qA, lA)
                row["status"] = "OK"
            except Exception as e:  # noqa: BLE001
                row.update(status="FAILED", error="%s: %s" % (type(e).__name__, e))
                out["failures"].append(dict(material_id=mid, stage="row %s %g" % (codec, rel), error=row["error"]))
            out["rows"].append(row)
        out["bader_solves"] = S.n
    out["wall_seconds"] = time.time() - t0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--material", required=True)
    a = ap.parse_args()
    CKPT.mkdir(parents=True, exist_ok=True)
    (ROOT / "temp").mkdir(exist_ok=True)
    dst = CKPT / (a.material + ".json")
    if dst.exists() and json.loads(dst.read_text()).get("status") == "SUCCESS":
        print("already done", a.material)
        return
    res = run(a.material)
    tmp = dst.with_suffix(".tmp")
    tmp.write_text(json.dumps(res, indent=1))
    os.replace(tmp, dst)
    print(a.material, res["status"], "%.0fs" % res.get("wall_seconds", 0), "solves", res.get("bader_solves"), flush=True)


if __name__ == "__main__":
    main()
