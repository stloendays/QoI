#!/usr/bin/env python3
"""Run one deterministic shard of the prospective QOAC-H v0.1 pilot."""
from __future__ import annotations
import argparse,csv,hashlib,math,sys,tempfile,time
from pathlib import Path
from typing import Any
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import codec_qoac_h as qoac
BETA_VALUES=(0.0,2.0)
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

def shard_for(material_id,n):
    d=hashlib.sha256(("QOAC-H-V01-SHARD|"+material_id).encode()).digest()
    return int.from_bytes(d[:8],"big")%n

def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    if not rows:
        path.write_text("",encoding="utf-8"); return
    fields=[]
    for row in rows:
        for k in row:
            if k not in fields: fields.append(k)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def main():
    args=parse_args()
    if args.shard_count<=0 or not (0<=args.shard_index<args.shard_count): raise SystemExit("invalid shard parameters")
    repo=args.repo_root.resolve(); out=args.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(repo/"validation"/"qsq_prospective"))
    import development_compatibility_smoke as dev
    with args.manifest.open(newline="",encoding="utf-8") as f: manifest=list(csv.DictReader(f))
    planned=[r for r in manifest if shard_for(r["material_id"],args.shard_count)==args.shard_index]
    rows=[]; failures=[]; planned_rows=[{"material_id":r["material_id"]} for r in planned]
    for meta in planned:
        mid=meta["material_id"]; t0=time.perf_counter()
        try:
            blob=dev.fetch_exact(meta["url"],meta["sha256"],int(meta["source_bytes"]))
            with tempfile.TemporaryDirectory(prefix="qoac_h_") as td:
                grid,loader=dev.build_grid(meta,blob,Path(td))
                field=np.ascontiguousarray(np.asarray(grid.total,dtype=np.float64))
                lattice=np.asarray(grid.structure.lattice.matrix,dtype=np.float64)
                if tuple(field.shape)!=tuple(int(x) for x in meta["ngrid"].split("x")): raise RuntimeError("grid shape mismatch")
                if field.size!=int(meta["npoints"]): raise RuntimeError("grid npoints mismatch")
                if not np.all(np.isfinite(field)): raise RuntimeError("non-finite source field")
                ptp=float(np.ptp(field))
                if not (math.isfinite(ptp) and ptp>0): raise RuntimeError("invalid source ptp")
                raw_bytes=int(field.nbytes); neg_ref=float(np.mean(field<0.0))
                prep=qoac.prepare_field(field,lattice,shell_count=SHELL_COUNT)
                ref_hist,ref_safe=qoac.reference_hartree_rms(field,lattice)
                for beta in BETA_VALUES:
                    for alpha_rel in ALPHA_REL:
                        alpha=float(alpha_rel*ptp)
                        try:
                            stream,enc=qoac.encode_prepared(prep,alpha=alpha,beta=beta,zlib_level=ZLIB_LEVEL)
                            recon,_,dec=qoac.decode_blob(stream,return_spectrum=False)
                            if not np.all(np.isfinite(recon)): raise RuntimeError("non-finite reconstruction")
                            err=recon-field
                            h_hist,h_safe=qoac.hartree_error_metrics(err,lattice,ref_hist,ref_safe)
                            rows.append({
                                "material_id":mid,"system_type":meta["system_type"],"formula":meta["formula"],"source":meta["source"],
                                "source_sha256":meta["sha256"],"loader":loader,"npoints":int(field.size),"raw_bytes":raw_bytes,
                                "beta":beta,"alpha_rel_ptp":float(alpha_rel),"alpha_abs":alpha,"encoded_bytes":len(stream),
                                "compression_ratio":raw_bytes/len(stream),"hartree_error_rel_RMSE_historical":h_hist,
                                "hartree_error_rel_RMSE_safe":h_safe,"density_Linf":float(np.max(np.abs(err))),
                                "density_RMSE":float(np.sqrt(np.mean(err*err))),"mean_density_deviation":float(abs(np.mean(recon)-np.mean(field))),
                                "negative_fraction_reference":neg_ref,"negative_fraction_reconstruction":float(np.mean(recon<0.0)),
                                "negative_fraction_delta":float(np.mean(recon<0.0)-neg_ref),"encode_seconds":float(enc["encode_seconds"]),
                                "decode_seconds":float(dec["decode_seconds"]),"special_modes":int(enc["special_modes"]),
                                "active_modes":int(enc["active_modes"]),"zlib_level":ZLIB_LEVEL,"shell_count":SHELL_COUNT
                            })
                        except Exception as exc:
                            failures.append({"material_id":mid,"stage":"setting","beta":beta,"alpha_rel_ptp":float(alpha_rel),"error":f"{type(exc).__name__}: {exc}"[:500]})
        except Exception as exc:
            failures.append({"material_id":mid,"stage":"material","error":f"{type(exc).__name__}: {exc}"[:500]})
        print(f"QOAC_H_MATERIAL_DONE {mid} seconds={time.perf_counter()-t0:.1f}",flush=True)
    write_csv(out/f"rows_shard_{args.shard_index:02d}.csv",rows)
    write_csv(out/f"failures_shard_{args.shard_index:02d}.csv",failures)
    write_csv(out/f"planned_shard_{args.shard_index:02d}.csv",planned_rows)
    print(f"QOAC_H_SHARD_DONE shard={args.shard_index} materials={len(planned)} rows={len(rows)} failures={len(failures)}")
    return 0
if __name__=="__main__": raise SystemExit(main())
