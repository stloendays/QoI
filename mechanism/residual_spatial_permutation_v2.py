#!/usr/bin/env python3
"""Implementation-v2 of the preregistered residual spatial-permutation test.

Scientific semantics are unchanged from
protocol/ERROR_GEOMETRY_PERMUTATION_V0_1_PREREGISTRATION.md.  V2 fixes only a
provenance implementation defect in V1: some representative 1e-3 mechanism
points are absent from the early-stopped master table, so the released
mechanism table -- which is the preregistered selection source -- is the
operating-point provenance authority for all three codecs.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import random
import statistics
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "mechanism" / "basin_error_decomposition_summary.csv"
METADATA = ROOT / "materials_metadata.csv"
PRIMARY_TOL = 1e-3
CODECS = ("ZFP", "SZ3", "SPERR")
SEEDS = (1701, 1702, 1703, 1704, 1705)
N_STRATA = 20
ERROR_FLOOR = 1e-15
BOOTSTRAP_DRAWS = 5000
MASTER_SEED = "20260907"


def args():
    p = argparse.ArgumentParser()
    p.add_argument("--list-materials", action="store_true")
    p.add_argument("--material-id")
    p.add_argument("--output-dir")
    p.add_argument("--aggregate-root")
    return p.parse_args()


def read_csv(path: Path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def as_bool(x: Any) -> bool:
    return str(x).strip().lower() in {"true", "1", "yes"}


def mechanism_rows(material_id: str) -> dict[str, dict[str, str]]:
    out = {}
    for r in read_csv(SUMMARY):
        if r["material_id"] != material_id or r["domain"] != "bulk":
            continue
        try:
            tol = float(r["relative_tolerance"])
        except ValueError:
            continue
        if abs(tol - PRIMARY_TOL) < 1e-15:
            out[r["codec"].strip().upper()] = r
    return out


def selected_materials() -> list[str]:
    meta = {r["material_id"]: r for r in read_csv(METADATA)}
    by_material: dict[str, set[str]] = defaultdict(set)
    for r in read_csv(SUMMARY):
        try:
            tol = float(r["relative_tolerance"])
        except ValueError:
            continue
        if r["domain"] == "bulk" and abs(tol - PRIMARY_TOL) < 1e-15:
            by_material[r["material_id"]].add(r["codec"].strip().upper())
    return [
        mid for mid in sorted(by_material)
        if mid in meta
        and meta[mid].get("source") == "Materials Project"
        and by_material[mid] == set(CODECS)
    ]


def source_record(material_id: str) -> dict[str, str]:
    for r in read_csv(METADATA):
        if r["material_id"] == material_id:
            return r
    raise KeyError(material_id)


def load_mp_chgcar(record: dict[str, str], workdir: Path):
    import urllib.request
    from monty.json import MontyDecoder
    from pymatgen.io.vasp.outputs import Chgcar

    req = urllib.request.Request(record["url"], headers={"User-Agent": "QoI-geometry-permutation/0.2"})
    with urllib.request.urlopen(req, timeout=240) as response:
        blob = response.read()
    got_sha = hashlib.sha256(blob).hexdigest()
    if got_sha != record["sha256"]:
        raise RuntimeError(f"source SHA256 mismatch {got_sha} != {record['sha256']}")
    if record.get("source_bytes") and len(blob) != int(record["source_bytes"]):
        raise RuntimeError(f"source byte-count mismatch {len(blob)} != {record['source_bytes']}")
    raw = gzip.decompress(blob) if record["url"].endswith(".gz") else blob
    payload = json.loads(raw.decode("utf-8"), cls=MontyDecoder)

    def find(obj: Any, depth: int = 0):
        if depth > 8:
            return None
        if isinstance(obj, Chgcar):
            return obj
        if isinstance(obj, dict):
            for value in obj.values():
                hit = find(value, depth + 1)
                if hit is not None:
                    return hit
        elif isinstance(obj, (list, tuple)):
            for value in obj:
                hit = find(value, depth + 1)
                if hit is not None:
                    return hit
        return None

    chgcar = find(payload)
    if chgcar is None:
        raise RuntimeError(f"{record['material_id']}: no pymatgen Chgcar found in parsed source")
    path = workdir / "CHGCAR"
    chgcar.write_file(path)
    return path, got_sha, len(blob)


def close(a: float, b: float, rtol: float, atol: float) -> bool:
    return abs(a - b) <= atol + rtol * max(abs(a), abs(b))


def process(material_id: str, outdir: Path) -> int:
    import numpy as np
    from baderkit import Grid

    sys.path.insert(0, str(ROOT / "validation"))
    import external_end_to_end as core

    if material_id not in selected_materials():
        raise RuntimeError(f"{material_id} is not in the preregistered selected set")
    record = source_record(material_id)
    mech = mechanism_rows(material_id)
    if set(mech) != set(CODECS):
        raise RuntimeError(f"{material_id}: incomplete released mechanism rows {sorted(mech)}")
    outdir.mkdir(parents=True, exist_ok=True)
    output: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix=f"qoi_geom_{material_id}_") as td:
        workdir = Path(td)
        chgcar, source_sha, source_bytes = load_mp_chgcar(record, workdir)
        grid = Grid.from_dynamic(chgcar)
        field = np.asarray(grid.total, dtype=np.float64)
        if field.size != int(record["npoints"]):
            raise RuntimeError(f"npoints mismatch {field.size} != {record['npoints']}")
        if not np.all(np.isfinite(field)):
            raise RuntimeError("source field contains non-finite values")
        original = core.run_bader(grid)
        q0 = np.asarray(original["charges"], dtype=np.float64)
        labels0 = np.asarray(original["atom_labels"])
        ptp = float(np.ptp(field))
        flat = field.ravel()
        density_order = np.argsort(flat, kind="stable")
        strata = np.array_split(density_order, N_STRATA)

        provenance = {
            "material_id": material_id,
            "source_url": record["url"],
            "source_sha256_verified": source_sha,
            "source_bytes_verified": source_bytes,
            "npoints": int(field.size),
            "natoms_bader": int(q0.size),
            "value_ptp": ptp,
            "operating_point_source": "mechanism/basin_error_decomposition_summary.csv",
            "primary_relative_tolerance": PRIMARY_TOL,
            "n_density_rank_strata": N_STRATA,
            "permutation_seeds": list(SEEDS),
        }
        (outdir / "provenance.json").write_text(json.dumps(provenance, indent=2))

        for codec_name in CODECS:
            codec = codec_name.lower()
            released = mech[codec_name]
            abs_bound = PRIMARY_TOL * ptp
            recon, compressed_bytes, mode = core.codec_roundtrip(codec, field, abs_bound, workdir)
            recon = np.asarray(recon, dtype=np.float64)
            delta = recon - field
            dflat = delta.ravel()
            linf = float(np.max(np.abs(dflat)))
            rmse = float(np.sqrt(np.mean(dflat * dflat)))
            mse = float(np.mean(dflat))
            mae = float(np.mean(np.abs(dflat)))
            resolved = core.run_bader(core.clone_grid_with_total(grid, recon))
            observed_error = float(np.max(np.abs(np.asarray(resolved["charges"], dtype=np.float64) - q0)))
            observed_reassigned = float(np.mean(np.asarray(resolved["atom_labels"]) != labels0))

            expected_linf = float(released["linf"])
            expected_error = float(released["dq_total_max_e"])
            expected_cr = float(released["compression_ratio"])
            actual_cr = float(field.nbytes / compressed_bytes)
            if not close(linf, expected_linf, 2e-6, 2e-10):
                raise RuntimeError(f"{material_id} {codec_name}: Linf provenance mismatch {linf:.12g} vs {expected_linf:.12g}")
            if not close(observed_error, expected_error, 2e-5, 2e-8):
                raise RuntimeError(f"{material_id} {codec_name}: Bader provenance mismatch {observed_error:.12g} vs {expected_error:.12g}")
            if not close(actual_cr, expected_cr, 2e-6, 2e-8):
                raise RuntimeError(f"{material_id} {codec_name}: compression-ratio provenance mismatch {actual_cr:.12g} vs {expected_cr:.12g}")

            for seed in SEEDS:
                rng = np.random.default_rng(seed)
                shuffled = np.empty_like(dflat)
                for indices in strata:
                    values = dflat[indices].copy()
                    rng.shuffle(values)
                    shuffled[indices] = values
                sh_linf = float(np.max(np.abs(shuffled)))
                sh_rmse = float(np.sqrt(np.mean(shuffled * shuffled)))
                sh_mse = float(np.mean(shuffled))
                sh_mae = float(np.mean(np.abs(shuffled)))
                audit = (
                    close(sh_linf, linf, 0.0, 1e-14 * max(1.0, linf))
                    and close(sh_rmse, rmse, 1e-13, 1e-15)
                    and close(sh_mse, mse, 1e-12, 1e-15)
                    and close(sh_mae, mae, 1e-13, 1e-15)
                )
                if not audit:
                    raise RuntimeError(f"{material_id} {codec_name} seed {seed}: residual multiset audit failed")
                try:
                    sh_field = field + shuffled.reshape(field.shape)
                    sh_bader = core.run_bader(core.clone_grid_with_total(grid, sh_field))
                    sh_error = float(np.max(np.abs(np.asarray(sh_bader["charges"], dtype=np.float64) - q0)))
                    sh_reassigned = float(np.mean(np.asarray(sh_bader["atom_labels"]) != labels0))
                    status, etype, detail = "SUCCESS", "", ""
                except Exception as exc:
                    sh_error, sh_reassigned = float("nan"), float("nan")
                    status, etype, detail = "BADER_FAILURE", type(exc).__name__, str(exc)
                    failures.append({"material_id": material_id, "codec": codec_name, "seed": seed, "error_type": etype, "detail": detail})
                output.append({
                    "material_id": material_id, "codec": codec_name, "relative_tolerance": PRIMARY_TOL,
                    "seed": seed, "status": status,
                    "observed_bader_error_e": observed_error, "shuffled_bader_error_e": sh_error,
                    "observed_frac_voxels_reassigned": observed_reassigned, "shuffled_frac_voxels_reassigned": sh_reassigned,
                    "observed_realized_linf": linf, "shuffled_realized_linf": sh_linf, "linf_abs_difference": abs(sh_linf-linf),
                    "observed_rmse": rmse, "shuffled_rmse": sh_rmse, "rmse_abs_difference": abs(sh_rmse-rmse),
                    "observed_mean_signed_error": mse, "shuffled_mean_signed_error": sh_mse, "mean_signed_abs_difference": abs(sh_mse-mse),
                    "observed_mae": mae, "shuffled_mae": sh_mae, "mae_abs_difference": abs(sh_mae-mae),
                    "compression_ratio": actual_cr, "compressed_bytes": compressed_bytes, "codec_mode": mode,
                    "released_mechanism_linf": expected_linf, "released_mechanism_bader_error_e": expected_error,
                    "norm_audit_ok": audit, "error_type": etype, "error_detail": detail,
                })

    def write(path: Path, rows, fields=None):
        if not rows:
            if fields:
                with path.open("w", newline="") as f: csv.DictWriter(f, fieldnames=fields).writeheader()
            else: path.write_text("")
            return
        fields = fields or list(rows[0].keys())
        with path.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    write(outdir / "permutation_rows.csv", output)
    write(outdir / "failures.csv", failures, ["material_id","codec","seed","error_type","detail"])
    print(json.dumps({"material_id": material_id, "rows": len(output), "failures": len(failures), "all_norm_audits": all(as_bool(r["norm_audit_ok"]) for r in output)}))
    return 0


def qtile(values: Iterable[float], q: float):
    xs = sorted(float(x) for x in values)
    if not xs: return None
    if len(xs) == 1: return xs[0]
    p = (len(xs)-1)*q; lo = int(math.floor(p)); hi = int(math.ceil(p))
    if lo == hi: return xs[lo]
    f = p-lo; return xs[lo]*(1-f)+xs[hi]*f


def boot_median(values: list[float], label: str):
    if not values: return None, None
    if len(values) == 1: return values[0], values[0]
    seed = int.from_bytes(hashlib.sha256((MASTER_SEED+"|"+label).encode()).digest()[:8], "big")
    rng = random.Random(seed); n=len(values); reps=[]
    for _ in range(BOOTSTRAP_DRAWS): reps.append(statistics.median(values[rng.randrange(n)] for _ in range(n)))
    return qtile(reps,.025), qtile(reps,.975)


def aggregate(root: Path, outdir: Path) -> int:
    raw=[]; failures=[]
    for p in sorted(root.rglob("permutation_rows.csv")): raw.extend(read_csv(p))
    for p in sorted(root.rglob("failures.csv")):
        failures.extend([r for r in read_csv(p) if any(r.values())])
    if not raw: raise RuntimeError("No permutation rows found")
    selected=selected_materials(); got=sorted({r["material_id"] for r in raw})
    if got != selected: raise RuntimeError(f"coverage mismatch expected={selected} got={got}")
    if not all(as_bool(r["norm_audit_ok"]) for r in raw): raise RuntimeError("norm audit failure")

    success={(r["material_id"],r["codec"],int(r["seed"])):r for r in raw if r["status"]=="SUCCESS"}
    observed={(r["material_id"],r["codec"]):float(r["observed_bader_error_e"]) for r in raw}
    material_codec=[]
    for mid in selected:
        for codec in CODECS:
            vals=[]
            for seed in SEEDS:
                r=success.get((mid,codec,seed))
                if r:
                    vals.append(math.log10(max(float(r["shuffled_bader_error_e"]),ERROR_FLOOR)/max(float(r["observed_bader_error_e"]),ERROR_FLOOR)))
            if vals:
                med=statistics.median(vals)
                material_codec.append({"material_id":mid,"codec":codec,"n_successful_seeds":len(vals),"median_log10_shuffle_over_observed":med,"median_fold_shuffle_over_observed":10**med,"median_abs_log10_change":statistics.median(abs(x) for x in vals)})

    attenuation=[]
    for mid in selected:
        for comp in ("SZ3","SPERR"):
            obslog=math.log10(max(observed[(mid,"ZFP")],ERROR_FLOOR)/max(observed[(mid,comp)],ERROR_FLOOR)); vals=[]
            for seed in SEEDS:
                rz=success.get((mid,"ZFP",seed)); rc=success.get((mid,comp,seed))
                if rz and rc:
                    vals.append(math.log10(max(float(rz["shuffled_bader_error_e"]),ERROR_FLOOR)/max(float(rc["shuffled_bader_error_e"]),ERROR_FLOOR))-obslog)
            if vals:
                med=statistics.median(vals)
                attenuation.append({"material_id":mid,"comparator":comp,"n_paired_seeds":len(vals),"observed_zfp_over_comparator_error_ratio":10**obslog,"median_attenuation_log10":med,"attenuation_fold_on_ratio":10**med})

    codec_summary=[]
    for codec in CODECS:
        vals=[float(r["median_log10_shuffle_over_observed"]) for r in material_codec if r["codec"]==codec]
        if vals:
            point=statistics.median(vals); lo,hi=boot_median(vals,"codec|"+codec)
            codec_summary.append({"codec":codec,"n_materials":len(vals),"median_log10_shuffle_over_observed":point,"median_fold_shuffle_over_observed":10**point,"ci_low_fold":10**lo,"ci_high_fold":10**hi})
    atten_summary=[]
    for comp in ("SZ3","SPERR"):
        vals=[float(r["median_attenuation_log10"]) for r in attenuation if r["comparator"]==comp]
        if vals:
            point=statistics.median(vals); lo,hi=boot_median(vals,"attenuation|"+comp)
            atten_summary.append({"contrast":"ZFP/"+comp,"n_materials":len(vals),"median_attenuation_log10":point,"attenuation_fold_on_error_ratio":10**point,"ci_low_log10":lo,"ci_high_log10":hi,"positive_ci":lo>0})

    outdir.mkdir(parents=True,exist_ok=True)
    def write(path,rows):
        if not rows: path.write_text(""); return
        with path.open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)
    write(outdir/"permutation_rows_all.csv",raw); write(outdir/"failures_all.csv",failures)
    write(outdir/"material_codec_effects.csv",material_codec); write(outdir/"attenuation_material_effects.csv",attenuation)
    write(outdir/"codec_summary.csv",codec_summary); write(outdir/"attenuation_summary.csv",atten_summary)
    supported=len(atten_summary)==2 and all(as_bool(r["positive_ci"]) for r in atten_summary)
    lines=["# Residual spatial-permutation mechanism test v0.1","", "Implementation v2; frozen scientific semantics unchanged. Each intervention preserves the codec residual value multiset within 20 original-density rank strata.","",f"Selected representative bulk Materials Project systems: **{len(selected)}** (`{', '.join(selected)}`).",f"Permutation Bader failures: **{len(failures)}**.","","## Within-codec spatial sensitivity","","| codec | materials | median shuffled/observed Bader error [95% CI] |","|---|---:|---:|"]
    for r in codec_summary: lines.append(f"| {r['codec']} | {r['n_materials']} | {r['median_fold_shuffle_over_observed']:.3g} [{r['ci_low_fold']:.3g}, {r['ci_high_fold']:.3g}] |")
    lines += ["","## ZFP-advantage attenuation","","Positive means the observed ZFP/comparator error-ratio advantage shrinks after fine spatial organization is destroyed.","","| contrast | materials | median attenuation log10 [95% CI] | fold change in ZFP/comparator error ratio | CI > 0? |","|---|---:|---:|---:|---|"]
    for r in atten_summary: lines.append(f"| {r['contrast']} | {r['n_materials']} | {r['median_attenuation_log10']:.3g} [{r['ci_low_log10']:.3g}, {r['ci_high_log10']:.3g}] | {r['attenuation_fold_on_error_ratio']:.3g}x | {r['positive_ci']} |")
    lines += ["",f"**Two-comparator preregistered attenuation criterion:** {'SUPPORTED' if supported else 'NOT SUPPORTED'}.","","## Interpretation guard","","Because the same residual values are permuted, L-infinity, L1/L2, RMSE, mean and histogram are fixed by construction. A reproducible Bader response is therefore direct evidence that spatial assignment matters. Scope remains this preregistered representative bulk mechanism set."]
    (outdir/"RESIDUAL_SPATIAL_PERMUTATION_REPORT.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"selected_materials":selected,"failures":len(failures),"two_comparator_supported":supported}))
    return 0


def main():
    a=args()
    if a.list_materials: print(json.dumps(selected_materials())); return 0
    if a.material_id:
        if not a.output_dir: raise SystemExit("--output-dir required")
        return process(a.material_id,Path(a.output_dir))
    if a.aggregate_root:
        if not a.output_dir: raise SystemExit("--output-dir required")
        return aggregate(Path(a.aggregate_root),Path(a.output_dir))
    raise SystemExit("choose --list-materials, --material-id, or --aggregate-root")


if __name__ == "__main__": raise SystemExit(main())
