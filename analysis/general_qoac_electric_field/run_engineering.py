#!/usr/bin/env python3
"""Run General-QOAC electric-field engineering settings on one deterministic shard."""
from __future__ import annotations
import argparse,csv,hashlib,math,sys,tempfile,time
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import electric_field_operator as ef

BETA_VALUES=(0.0,1.0,2.0)
ALPHA_REL=np.logspace(-7.0,1.0,25)
ZLIB_LEVEL=6
SHELL_COUNT=32

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--shard-count",type=int,required=True)
    p.add_argument("--shard-index",type=int,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    return p.parse_args()

def shard_for(mid,n):
    d=hashlib.sha256(("GENERAL-QOAC-EFIELD|"+mid).encode()).digest()
    return int.from_bytes(d[:8],"big")%n

def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:
        path.write_text("",encoding="utf-8"); return
    fields=[]
    for r in rows:
        for k in r:
            if k not in fields: fields.append(k)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def main():
    a=parse_args()
    if a.shard_count<=0 or not (0<=a.shard_index<a.shard_count): raise SystemExit("invalid shard parameters")
    repo=a.repo_root.resolve(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(repo/"analysis"/"operator_aware_codec_hartree_v02"))
    import codec_qoac_h_v02 as qoac
    sys.path.insert(0,str(repo/"validation"/"qsq_prospective"))
    import development_compatibility_smoke as dev

    with a.manifest.open(newline="",encoding="utf-8") as f: manifest=list(csv.DictReader(f))
    planned=[r for r in manifest if shard_for(r["material_id"],a.shard_count)==a.shard_index]
    rows=[]; failures=[]

    for meta in planned:
        mid=meta["material_id"]; t0=time.perf_counter()
        try:
            blob=dev.fetch_exact(meta["url"],meta["sha256"],int(meta["source_bytes"]))
            with tempfile.TemporaryDirectory(prefix="general_qoac_efield_") as td:
                grid,loader=dev.build_grid(meta,blob,Path(td))
                field=np.ascontiguousarray(np.asarray(grid.total,dtype=np.float64))
                lattice=np.asarray(grid.structure.lattice.matrix,dtype=np.float64)
                if field.size!=int(meta["npoints"]): raise RuntimeError("npoints mismatch")
                if not np.all(np.isfinite(field)): raise RuntimeError("non-finite field")
                ptp=float(np.ptp(field))
                if not (math.isfinite(ptp) and ptp>0): raise RuntimeError("invalid ptp")
                prep=qoac.prepare_field(field,lattice,shell_count=SHELL_COUNT)
                ref_hist,ref_safe=ef.reference_energies(field,lattice)
                for beta in BETA_VALUES:
                    for arel in ALPHA_REL:
                        try:
                            alpha=float(arel*ptp)
                            stream,enc=qoac.encode_prepared(prep,alpha=alpha,beta=beta,zlib_level=ZLIB_LEVEL)
                            recon,_,dec=qoac.decode_blob(stream,return_spectrum=False)
                            err=np.ascontiguousarray(recon-field,dtype=np.float64)
                            e_hist,e_safe=ef.relative_error(err,lattice,ref_hist,ref_safe)
                            rows.append({
                              "material_id":mid,"system_type":meta["system_type"],"formula":meta["formula"],
                              "source":meta["source"],"source_sha256":meta["sha256"],"loader":loader,
                              "npoints":int(field.size),"raw_bytes":int(field.nbytes),
                              "beta":float(beta),"alpha_rel_ptp":float(arel),"alpha_abs":alpha,
                              "encoded_bytes":len(stream),"compression_ratio":field.nbytes/len(stream),
                              "electric_field_error_rel_RMSE_historical":e_hist,
                              "electric_field_error_rel_RMSE_safe":e_safe,
                              "density_Linf":float(np.max(np.abs(err))),
                              "density_RMSE":float(np.sqrt(np.mean(err*err))),
                              "mean_density_deviation":float(abs(np.mean(recon)-np.mean(field))),
                              "encode_seconds":float(enc["encode_seconds"]),
                              "decode_seconds":float(dec["decode_seconds"]),
                              "imaginary_leakage_max":float(dec["imaginary_leakage_max"]),
                              "exact_modes":int(enc["exact_modes"]),
                              "representative_modes":int(enc["representative_modes"]),
                              "zlib_level":ZLIB_LEVEL,"shell_count":SHELL_COUNT,
                            })
                        except Exception as exc:
                            failures.append({"material_id":mid,"stage":"setting","beta":beta,"alpha_rel_ptp":float(arel),"error":f"{type(exc).__name__}: {exc}"[:500]})
        except Exception as exc:
            failures.append({"material_id":mid,"stage":"material","error":f"{type(exc).__name__}: {exc}"[:500]})
        print(f"GENERAL_QOAC_EFIELD_MATERIAL_DONE {mid} seconds={time.perf_counter()-t0:.1f}",flush=True)

    write_csv(out/f"rows_shard_{a.shard_index:02d}.csv",rows)
    write_csv(out/f"failures_shard_{a.shard_index:02d}.csv",failures)
    write_csv(out/f"planned_shard_{a.shard_index:02d}.csv",[{"material_id":r["material_id"]} for r in planned])
    print(f"GENERAL_QOAC_EFIELD_SHARD_DONE shard={a.shard_index} materials={len(planned)} rows={len(rows)} failures={len(failures)}")
    return 0

if __name__=="__main__": raise SystemExit(main())
