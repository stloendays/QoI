#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,sys,tempfile,time,zlib
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
B3=HERE.parent/"operator_aware_bader_partition_compiled"
B1=HERE.parent/"operator_aware_bader_fixed_partition"
sys.path.insert(0,str(B3)); sys.path.insert(0,str(B1))
import partition_codec as pc
import run_engineering as b1

TAU=1e-3
AE_HEADER_BYTES=32

def read_csv(path):
    with Path(path).open(newline="",encoding="utf-8") as f: return list(csv.DictReader(f))

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--frozen-root",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--shard-count",type=int,required=True)
    p.add_argument("--shard-index",type=int,required=True)
    p.add_argument("--bader",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    return p.parse_args()

def b2_map(repo):
    out={}
    eng=read_csv(repo/"analysis/operator_aware_bader_projection/results/engineering_frontier.csv")
    for r in eng:
        if abs(float(r["kappa"])-4.0)<1e-12:
            out[r["material_id"]]=("engineering",int(r["total_bytes"]))
    hold=read_csv(repo/"analysis/operator_aware_bader_projection_confirmatory/results/confirmatory_material.csv")
    for r in hold:
        mid=r["material_id"]
        if mid in out: raise RuntimeError(f"duplicate B2 material {mid}")
        out[mid]=("holdout",int(r["total_bytes"]))
    if len(out)!=50: raise RuntimeError(f"expected 50 frozen B2 rows, got {len(out)}")
    return out

def best_g1(mid,wp,raw_bytes):
    z=[r for r in wp if r["material_id"]==mid and r["status"]=="OK" and float(r["g1_error_e"])<TAU]
    if not z: raise RuntimeError("no G1 baseline at tau=1e-3")
    return max(z,key=lambda r:raw_bytes/int(r["chgcar_bytes"]))

def process(meta,a,core,dev,b2,wp):
    mid=meta["material_id"]; t0=time.time()
    result={"material_id":mid,"status":"SUCCESS","failures":[]}
    try:
        chg_blob=b1.fetch(meta["url"])
        if hashlib.sha256(chg_blob).hexdigest()!=meta["sha256"] or len(chg_blob)!=int(meta["source_bytes"]):
            raise RuntimeError("CHGCAR checksum mismatch")
        a0=b1.fetch(b1.BUCKET+f"aeccar0s/{meta['task_id']}.json.gz")
        a2=b1.fetch(b1.BUCKET+f"aeccar2s/{meta['task_id']}.json.gz")
        with tempfile.TemporaryDirectory(prefix="qoacb3c_") as td:
            work=Path(td)
            grid,_=dev.build_grid(meta,chg_blob,work)
            chg=np.ascontiguousarray(np.asarray(grid.total,dtype=np.float64))
            ae=np.asarray(dev.decode_mp_chgcar(a0).data["total"],dtype=np.float64)+np.asarray(dev.decode_mp_chgcar(a2).data["total"],dtype=np.float64)
            st=grid.structure; lattice=np.asarray(st.lattice.matrix,float); frac=np.asarray(st.frac_coords,float); symbols=[s.specie.symbol for s in st]
            S=b1.Solver(a.bader,lattice,frac,symbols,chg.shape,work)
            qref,lflat=S(chg,ae)
            labels=b1.qb.label_grid_from_fortran_flat(lflat,chg.shape)

            raw_blob=pc.encode_raw(labels); rle_blob=pc.encode_rle(labels); best_blob,best_meta=pc.encode_best(labels)
            exact_raw=bool(np.array_equal(pc.decode(raw_blob),labels))
            exact_rle=bool(np.array_equal(pc.decode(rle_blob),labels))
            exact_best=bool(np.array_equal(pc.decode(best_blob),labels))
            qmap=pc.direct_atomic_charges(chg,pc.decode(best_blob),lattice,len(symbols))
            direct_error=float(np.max(np.abs(qmap-qref)))

            ae_raw=np.asarray(ae,dtype="<f8").ravel(order="F").tobytes()
            ae_lossless=AE_HEADER_BYTES+len(zlib.compress(ae_raw,6))
            g1=best_g1(mid,wp,int(chg.nbytes))
            b2_source,b2_bytes=b2[mid]

            baseline_archive=int(g1["chgcar_bytes"])+ae_lossless
            compiled_archive=b2_bytes+len(best_blob)
            result.update({
              "npoints":int(chg.size),"natoms":len(symbols),"nlabels":int(labels.max())+1,
              "max_partition_label":int(labels.max()),
              "packed_zlib_bytes":len(raw_blob),"rle_zlib_bytes":len(rle_blob),
              "best_partition_method":best_meta["method"],"best_partition_bytes":len(best_blob),
              "partition_decode_exact_raw":exact_raw,"partition_decode_exact_rle":exact_rle,"partition_decode_exact_best":exact_best,
              "direct_charge_max_error_e":direct_error,
              "ae_lossless_zlib_bytes":ae_lossless,
              "partition_replacement_ratio":ae_lossless/len(best_blob),
              "baseline_g1_codec":g1["codec"],"baseline_g1_chgcar_bytes":int(g1["chgcar_bytes"]),
              "b2_source":b2_source,"b2_chgcar_total_bytes":b2_bytes,
              "baseline_archive_bytes":baseline_archive,"compiled_archive_bytes":compiled_archive,
              "archive_ratio_baseline_over_compiled":baseline_archive/compiled_archive,
              "partition_fraction_of_compiled_archive":len(best_blob)/compiled_archive,
              "bader_solves":S.n
            })
    except Exception as e:
        import traceback
        result["status"]="FAILED"; result["failures"].append({"error":f"{type(e).__name__}: {e}"}); result["traceback"]=traceback.format_exc()
    result["wall_seconds"]=time.time()-t0
    return result

def main():
    a=parse_args(); repo=a.repo_root.resolve(); frozen=a.frozen_root.resolve(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    manifest=read_csv(a.manifest)
    if len(manifest)!=50: raise RuntimeError(f"expected 50 materials, got {len(manifest)}")
    b2=b2_map(repo); wp=read_csv(repo/"analysis/extensions_20260930/WP-G/rows.csv")
    sys.path.insert(0,str(frozen/"validation")); sys.path.insert(0,str(repo/"validation"/"qsq_prospective"))
    import external_end_to_end as core
    import development_compatibility_smoke as dev
    planned=[m for i,m in enumerate(manifest) if i%a.shard_count==a.shard_index]
    rc=0
    for meta in planned:
        z=process(meta,a,core,dev,b2,wp)
        (out/f"{meta['material_id']}.json").write_text(json.dumps(z,indent=2)+"\n",encoding="utf-8")
        print("QOAC_B3_CENSUS_DONE",meta["material_id"],z["status"],"charge",z.get("direct_charge_max_error_e"),"archive",z.get("archive_ratio_baseline_over_compiled"),flush=True)
        if z["status"]!="SUCCESS": rc=1
    return rc
if __name__=="__main__": raise SystemExit(main())
