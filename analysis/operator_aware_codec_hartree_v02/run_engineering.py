#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,math,sys,tempfile,time
from pathlib import Path
from typing import Any
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import codec_qoac_h_v02 as qoac
ALPHA_REL=np.logspace(-7.0,1.0,25)
FLOOR_ALPHA_REL=1e8
BETA=2.0
ZLIB_LEVEL=6
SHELL_COUNT=32

def args():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--shard-count",type=int,required=True)
    p.add_argument("--shard-index",type=int,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    return p.parse_args()

def shard_for(mid,n):
    return int.from_bytes(hashlib.sha256(("QOAC-H-V02|"+mid).encode()).digest()[:8],"big")%n

def write_csv(path,rows):
    if not rows: path.write_text("",encoding="utf-8"); return
    fields=[]
    for r in rows:
        for k in r:
            if k not in fields: fields.append(k)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def main():
    a=args(); repo=a.repo_root.resolve(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(repo/"validation"/"qsq_prospective"))
    import development_compatibility_smoke as dev
    with a.manifest.open(newline="",encoding="utf-8") as f: manifest=list(csv.DictReader(f))
    planned=[r for r in manifest if shard_for(r["material_id"],a.shard_count)==a.shard_index]
    rows=[]; failures=[]
    for meta in planned:
        mid=meta["material_id"]; t0=time.perf_counter()
        try:
            blob=dev.fetch_exact(meta["url"],meta["sha256"],int(meta["source_bytes"]))
            with tempfile.TemporaryDirectory(prefix="qoac_h_v02_") as td:
                grid,loader=dev.build_grid(meta,blob,Path(td))
                field=np.ascontiguousarray(np.asarray(grid.total,dtype=np.float64))
                lattice=np.asarray(grid.structure.lattice.matrix,dtype=np.float64)
                ptp=float(np.ptp(field))
                if not (math.isfinite(ptp) and ptp>0): raise RuntimeError("invalid ptp")
                prep=qoac.prepare_field(field,lattice,shell_count=SHELL_COUNT)
                rh,rs=qoac.reference_hartree_rms(field,lattice)
                settings=[("certificate",float(x)) for x in ALPHA_REL]+[("floor_probe",FLOOR_ALPHA_REL)]
                for purpose,arel in settings:
                    try:
                        stream,enc=qoac.encode_prepared(prep,alpha=arel*ptp,beta=BETA,zlib_level=ZLIB_LEVEL)
                        recon,_,dec=qoac.decode_blob(stream)
                        err=recon-field
                        eh,es=qoac.hartree_error_metrics(err,lattice,rh,rs)
                        rows.append({
                            "material_id":mid,"system_type":meta["system_type"],"formula":meta["formula"],
                            "source":meta["source"],"source_sha256":meta["sha256"],"loader":loader,
                            "purpose":purpose,"alpha_rel_ptp":arel,"alpha_abs":arel*ptp,"beta":BETA,
                            "npoints":int(field.size),"raw_bytes":int(field.nbytes),"encoded_bytes":len(stream),
                            "compression_ratio":field.nbytes/len(stream),
                            "hartree_error_rel_RMSE_historical":eh,"hartree_error_rel_RMSE_safe":es,
                            "density_Linf":float(np.max(np.abs(err))),"density_RMSE":float(np.sqrt(np.mean(err*err))),
                            "mean_density_deviation":float(abs(np.mean(recon)-np.mean(field))),
                            "encode_seconds":float(enc["encode_seconds"]),"decode_seconds":float(dec["decode_seconds"]),
                            "imaginary_leakage_max":float(dec["imaginary_leakage_max"]),
                            "representative_modes":int(enc["representative_modes"]),"exact_modes":int(enc["exact_modes"])
                        })
                    except Exception as exc:
                        failures.append({"material_id":mid,"purpose":purpose,"alpha_rel_ptp":arel,"error":f"{type(exc).__name__}: {exc}"[:500]})
        except Exception as exc:
            failures.append({"material_id":mid,"purpose":"material","alpha_rel_ptp":"","error":f"{type(exc).__name__}: {exc}"[:500]})
        print(f"QOAC_H_V02_MATERIAL_DONE {mid} seconds={time.perf_counter()-t0:.1f}",flush=True)
    write_csv(out/f"rows_shard_{a.shard_index:02d}.csv",rows)
    write_csv(out/f"failures_shard_{a.shard_index:02d}.csv",failures)
    write_csv(out/f"planned_shard_{a.shard_index:02d}.csv",[{"material_id":r["material_id"]} for r in planned])
    return 0

if __name__=="__main__": raise SystemExit(main())
