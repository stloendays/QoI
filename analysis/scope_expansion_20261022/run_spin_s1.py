#!/usr/bin/env python3
"""WS-S S1: the spin channel as a measurement contract (engineering, descriptive).

Stored object: the pair (rho, m) of a spin-polarized MP CHGCAR (total and
magnetization blocks). QoIs:

* per-atom magnetic moments mu_a: compiled Henkelman Bader 1.05,
  ``bader CHGCAR(m) -ref REFCAR(rho) -b ongrid -vac 0.001`` (the standard
  way per-atom moments are obtained from a VASP CHGCAR);
* total magnetization M = mean(m) (mu_B per cell), recorded alongside.

Per material:

1. reference moments (binary);
2. QSQ floor for the moment contract: five pre-registered seeds
   {20260905, 1, 2, 3, 4}; each probe perturbs rho and m with U(-eps, eps),
   eps = that field's float32 round-trip L-infinity; floor = max over seeds of
   max_a |mu_a - mu_a^ref|; eligible(tau) := floor < tau;
3. codec arms on m with rho exact (partition fixed): ZFP, SZ3, SPERR, each
   with a bisection on the absolute bound (as a fraction of ptp(m)) for the
   largest bound whose moments meet tau. With rho exact the partition is the
   reference one, so moments during the search are per-atom sums of m over the
   reference AtIndex map (QOAC-B3 arm L showed these match ACF.dat to 5e-7 e);
   the final certified point of every arm is re-run through the binary.
4. bytes: certified m stream vs lossless (zlib-6) m and lossless rho.

Nothing here is a confirmatory gate.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import subprocess
import sys
import tempfile
import time
import traceback
import urllib.request
import zlib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "analysis" / "operator_aware_bader_fixed_partition"))

SEEDS = (20260905, 1, 2, 3, 4)
TAUS_MU = (1e-1, 1e-2, 1e-3)
CODECS = ("zfp", "sz3", "sperr")
REL_LO, REL_HI, STEPS = 1e-9, 1e-1, 14

ROW_FIELDS = ["material_id", "formula", "magnetic", "npoints", "natoms", "max_abs_moment_muB", "floor_muB",
              "tau_muB", "eligible", "codec", "status", "error", "rel_bound", "abs_bound", "m_bytes", "m_cr",
              "lossless_m_bytes", "lossless_rho_bytes", "m_bytes_over_lossless_rho", "err_python_muB",
              "err_binary_muB", "dM_muB", "certified", "search_steps"]


def fetch(url: str, tries: int = 5) -> bytes:
    last = None
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=900) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(5 * (k + 1))
    raise RuntimeError(f"download failed: {last}")


def decode(blob: bytes) -> dict:
    doc = json.loads(gzip.decompress(blob).decode("utf-8"))
    data = doc["data"] if "data" in doc and "poscar" not in doc else doc
    st = data["poscar"]["structure"] if "structure" in data["poscar"] else data["poscar"]
    blocks = data["data"]
    tot = blocks["total"]; diff = blocks.get("diff")
    if diff is None:
        raise RuntimeError("no magnetization block")
    rho = np.array(tot["data"] if isinstance(tot, dict) else tot, dtype=np.float64)
    m = np.array(diff["data"] if isinstance(diff, dict) else diff, dtype=np.float64)
    return {"rho": np.ascontiguousarray(rho), "m": np.ascontiguousarray(m),
            "lattice": np.array(st["lattice"]["matrix"], dtype=np.float64),
            "frac": np.array([s["abc"] for s in st["sites"]], dtype=np.float64),
            "symbols": [s["species"][0]["element"] for s in st["sites"]]}


def _bcore():
    """The QOAC-B1 helpers (CHGCAR writer, AtIndex reader), loaded by file path so that another module
    named ``run_engineering`` on sys.path (e.g. qoac_v03_rdo's) cannot shadow them."""
    import importlib.util
    name = "qoacb1_run_engineering"
    if name not in sys.modules:
        path = REPO / "analysis" / "operator_aware_bader_fixed_partition" / "run_engineering.py"
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
    return sys.modules[name]


class Bader:
    """Compiled Henkelman binary on (CHGCAR = integrand, REFCAR = partition field)."""

    def __init__(self, exe, lattice, frac, symbols, shape, work: Path):
        write_chgcar = _bcore().write_chgcar
        self.exe, self.lattice, self.frac, self.symbols, self.shape, self.work = Path(exe), lattice, frac, symbols, shape, work
        self.write = write_chgcar
        self.n = 0
        self._ref_id = None

    def __call__(self, integrand, partition_field, ref_id: str):
        read_atindex = _bcore().read_atindex
        import qoac_b_core as qb
        w = self.work
        for p in w.glob("*.dat"):
            p.unlink()
        self.write(w / "CHGCAR", integrand, self.lattice, self.frac, self.symbols)
        if ref_id != self._ref_id:
            self.write(w / "REFCAR", partition_field, self.lattice, self.frac, self.symbols)
            self._ref_id = ref_id
        cmd = [str(self.exe), "CHGCAR", "-ref", "REFCAR", "-b", "ongrid", "-vac", "0.001", "-p", "atom_index"]
        with (w / "bader.log").open("w") as fh:
            rc = subprocess.call(cmd, cwd=w, stdout=fh, stderr=subprocess.STDOUT)
        if rc:
            raise RuntimeError(f"Henkelman exit {rc}: " + (w / "bader.log").read_text()[-400:])
        rows = [ln.split() for ln in (w / "ACF.dat").read_text().splitlines()]
        data = [[float(x) for x in r[:7]] for r in rows if len(r) >= 7 and r[0].isdigit()]
        if len(data) != len(self.symbols):
            raise RuntimeError("ACF atom count mismatch")
        self.n += 1
        atom = qb.label_grid_from_fortran_flat(read_atindex(w / "AtIndex.dat", self.shape), self.shape)
        return np.array([x[4] for x in data]), atom


def f32_eps(x: np.ndarray) -> float:
    return float(np.max(np.abs(x.astype(np.float32).astype(np.float64) - x)))


def sums(m, atom, natoms):
    s = np.bincount(atom.ravel(), weights=m.ravel(), minlength=natoms + 2)
    return s[1:natoms + 1] / m.size


def run_material(meta: dict, magnetic: bool, bader_exe: Path, frozen: Path) -> dict:
    sys.path.insert(0, str(frozen / "validation"))
    import external_end_to_end as core  # frozen codec wrappers (ZFP, SZ3, SPERR)
    mid = meta["material_id"]
    res = {"material_id": mid, "formula": meta.get("formula", ""), "magnetic": magnetic, "status": "SUCCESS",
           "rows": [], "failures": []}
    t0 = time.time()
    try:
        blob = fetch(meta["url"])
        if hashlib.sha256(blob).hexdigest() != meta["sha256"]:
            raise RuntimeError("sha256 mismatch against manifest")
        d = decode(blob)
        rho, m = d["rho"], d["m"]
        natoms = len(d["symbols"])
        with tempfile.TemporaryDirectory(prefix="ws_s1_") as td:
            B = Bader(bader_exe, d["lattice"], d["frac"], d["symbols"], rho.shape, Path(td))
            mu_ref, atom_ref = B(m, rho, "ref")
            mu_py = sums(m, atom_ref, natoms)
            res.update(npoints=int(rho.size), natoms=natoms, mu_ref=mu_ref.tolist(),
                       max_abs_moment_muB=float(np.max(np.abs(mu_ref))),
                       python_vs_binary_muB=float(np.max(np.abs(mu_py - mu_ref))),
                       M_ref_muB=float(m.mean()))
            # QSQ floor for the moment contract
            e_r, e_m = f32_eps(rho), f32_eps(m)
            per_seed = []
            for s in SEEDS:
                rng = np.random.default_rng(s)
                rp = rho + rng.uniform(-e_r, e_r, rho.shape)
                mp = m + rng.uniform(-e_m, e_m, m.shape)
                mu_p, _ = B(mp, rp, f"probe{s}")
                per_seed.append(float(np.max(np.abs(mu_p - mu_ref))))
            floor = max(per_seed)
            res.update(eps_rho=e_r, eps_m=e_m, floor_per_seed=per_seed, floor_muB=floor)
            lossless_m = len(zlib.compress(m.tobytes(), 6))
            lossless_rho = len(zlib.compress(rho.tobytes(), 6))
            ptp = float(np.ptp(m)) or 1.0
            work = Path(td) / "codec"
            work.mkdir()
            for tau in TAUS_MU:
                eligible = floor < tau
                for codec in CODECS:
                    row = {"material_id": mid, "formula": res["formula"], "magnetic": magnetic, "npoints": rho.size,
                           "natoms": natoms, "max_abs_moment_muB": res["max_abs_moment_muB"], "floor_muB": floor,
                           "tau_muB": tau, "eligible": eligible, "codec": codec, "status": "OK", "error": "",
                           "lossless_m_bytes": lossless_m, "lossless_rho_bytes": lossless_rho}
                    try:
                        # bisection in log(rel bound): largest bound whose python moments meet tau
                        lo, hi = math.log10(REL_LO), math.log10(REL_HI)
                        best = None
                        steps = 0
                        for _ in range(STEPS):
                            mid_b = 0.5 * (lo + hi)
                            ab = 10 ** mid_b * ptp
                            rec, nb, _ = core.codec_roundtrip(codec, m, ab, work)
                            rec = np.asarray(rec, dtype=np.float64)
                            err = float(np.max(np.abs(sums(rec, atom_ref, natoms) - mu_ref)))
                            steps += 1
                            if err < tau:
                                best = (10 ** mid_b, ab, int(nb), rec, err)
                                lo = mid_b
                            else:
                                hi = mid_b
                        if best is None:
                            row.update(status="NO_CERTIFIED_POINT", search_steps=steps, certified=False)
                        else:
                            rel, ab, nb, rec, err = best
                            mu_b, _ = B(rec, rho, "ref")
                            err_b = float(np.max(np.abs(mu_b - mu_ref)))
                            row.update(rel_bound=rel, abs_bound=ab, m_bytes=nb, m_cr=m.nbytes / nb,
                                       m_bytes_over_lossless_rho=nb / lossless_rho, err_python_muB=err,
                                       err_binary_muB=err_b, dM_muB=float(abs(rec.mean() - m.mean())),
                                       certified=bool(err_b < tau), search_steps=steps)
                    except Exception as e:  # noqa: BLE001
                        row.update(status="FAILED", error=f"{type(e).__name__}: {e}")
                        res["failures"].append({"stage": f"{codec} tau={tau}", "error": row["error"],
                                                "traceback": traceback.format_exc()})
                    res["rows"].append(row)
            res["bader_solves"] = B.n
    except Exception as e:  # noqa: BLE001
        res["status"] = "FAILED"
        res["failures"].append({"stage": "material", "error": f"{type(e).__name__}: {e}",
                                "traceback": traceback.format_exc()})
    res["wall_seconds"] = time.time() - t0
    return res


def select(census_csv: Path, metadata_csv: Path, n_mag: int = 12, n_non: int = 4) -> list[dict]:
    """Deterministic engineering selection from the S0 census of the development panel:
    the n_mag smallest grids with max |mu_atom| >= 0.1 mu_B and the n_non smallest with
    max |mu_atom| < 0.01 mu_B."""
    meta = {r["material_id"]: r for r in csv.DictReader(metadata_csv.read_text(encoding="utf-8").splitlines())}
    cen = [r for r in csv.DictReader(census_csv.read_text(encoding="utf-8").splitlines())
           if r["source_manifest"] == "materials_metadata.csv" and r["status"] == "OK"]
    mag = sorted([r for r in cen if float(r["max_abs_atom_moment_muB"] or 0) >= 0.1], key=lambda r: (int(r["npoints"]), r["material_id"]))
    non = sorted([r for r in cen if float(r["max_abs_atom_moment_muB"] or 0) < 0.01], key=lambda r: (int(r["npoints"]), r["material_id"]))
    out = [dict(meta[r["material_id"]], magnetic="True") for r in mag[:n_mag]]
    out += [dict(meta[r["material_id"]], magnetic="False") for r in non[:n_non]]
    return out


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


def write_rows(rows, path: Path):
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=ROW_FIELDS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in ROW_FIELDS})


def aggregate(results: list[dict]) -> dict:
    rows = [r for res in results for r in res.get("rows", [])]
    summ = {"materials": len(results), "materials_ok": sum(r["status"] == "SUCCESS" for r in results),
            "python_vs_binary_max_muB": max((r.get("python_vs_binary_muB", 0) for r in results), default=None),
            "by_tau": {}}
    for tau in TAUS_MU:
        sel = [r for r in rows if r["tau_muB"] == tau and r["status"] == "OK"]
        for group in ("True", "False"):
            g = [r for r in sel if str(r["magnetic"]) == group]
            mats = sorted({r["material_id"] for r in g})
            elig = sorted({r["material_id"] for r in g if r["eligible"]})
            best = {}
            for r in g:
                if r.get("certified"):
                    b = best.get(r["material_id"])
                    if b is None or r["m_bytes"] < b["m_bytes"]:
                        best[r["material_id"]] = r
            key = f"tau={tau:g}|magnetic={group}"
            summ["by_tau"][key] = {
                "materials": len(mats), "eligible": len(elig),
                "certified_any_codec": len(best),
                "median_best_m_cr": float(np.median([b["m_cr"] for b in best.values()])) if best else None,
                "median_best_m_bytes_over_lossless_rho": float(np.median([b["m_bytes_over_lossless_rho"] for b in best.values()])) if best else None,
                "codec_wins": {c: sum(b["codec"] == c for b in best.values()) for c in CODECS},
                "binary_certified_all": all(b.get("certified") for b in best.values()),
            }
    return summ


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("select")
    s.add_argument("--census", type=Path, required=True)
    s.add_argument("--metadata", type=Path, required=True)
    s.add_argument("--out", type=Path, required=True)
    r = sub.add_parser("run")
    r.add_argument("--manifest", type=Path, required=True)
    r.add_argument("--index", type=int, required=True)
    r.add_argument("--bader", type=Path, required=True)
    r.add_argument("--frozen-root", type=Path, required=True)
    r.add_argument("--out", type=Path, required=True)
    a = sub.add_parser("aggregate")
    a.add_argument("--inputs", type=Path, required=True)
    a.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    if args.cmd == "select":
        rows = select(args.census, args.metadata)
        with args.out.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(len(rows))
        return 0
    if args.cmd == "run":
        man = list(csv.DictReader(args.manifest.read_text(encoding="utf-8").splitlines()))
        meta = man[args.index]
        res = run_material(meta, meta["magnetic"] == "True", args.bader, args.frozen_root.resolve())
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / f"{meta['material_id']}.json").write_text(json.dumps(res, indent=2, default=_json_default) + "\n")
        write_rows(res["rows"], args.out / f"{meta['material_id']}_rows.csv")
        print("WS_S1_DONE", meta["material_id"], res["status"], len(res["rows"]), "failures", len(res["failures"]))
        return 0
    results = []
    for p in sorted(args.inputs.rglob("*.json")):
        try:
            dd = json.loads(p.read_text())
        except json.JSONDecodeError:
            continue
        if isinstance(dd, dict) and "rows" in dd and "material_id" in dd:
            results.append(dd)
    args.out.mkdir(parents=True, exist_ok=True)
    write_rows([r for res in results for r in res["rows"]], args.out / "rows.csv")
    summ = aggregate(results)
    (args.out / "SUMMARY.json").write_text(json.dumps(summ, indent=2, default=_json_default) + "\n")
    with (args.out / "failures.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["material_id", "stage", "error"])
        w.writeheader()
        for res in results:
            for f in res["failures"]:
                w.writerow({"material_id": res["material_id"], "stage": f["stage"], "error": f["error"]})
    print(json.dumps(summ, indent=1, default=_json_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
