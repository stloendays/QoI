#!/usr/bin/env python3
"""Run QOAC-B3 compiled-partition engineering on one material."""
from __future__ import annotations
import argparse,csv,hashlib,json,sys,tempfile,time,zlib
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
B1=HERE.parent/"operator_aware_bader_fixed_partition"
sys.path.insert(0,str(HERE)); sys.path.insert(0,str(B1))
import partition_codec as pc
import run_engineering as b1

TAU=1e-3
AE_HEADER_BYTES=32


def read_csv(path):
    with Path(path).open(newline="",encoding="utf-8") as f: return list(csv.DictReader(f))


def args():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--frozen-root",type=Path,required=True)
    p.add_argument("--engineering-manifest",type=Path,required=True)
    p.add_argument("--b2-frontier",type=Path,required=True)
    p.add_argument("--index",type=int,required=True)
    p.add_argument("--bader",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    return p.parse_args()


def best_g1(mid,wp,raw_bytes):
    z=[r for r in wp if r["material_id"]==mid and r["status"]=="OK" and float(r["g1_error_e"])<TAU]
    if not z: raise RuntimeError("no G1 baseline at tau=1e-3")
    r=max(z,key=lambda r:raw_bytes/int(r["chgcar_bytes"]))
    return r


def main():
    a=args(); repo=a.repo_root.resolve(); frozen=a.frozen_root.resolve(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    manifest=read_csv(a.engineering_manifest)
    meta=manifest[a.index]; mid=meta["material_id"]; t0=time.time()
    result={"material_id":mid,"status":"SUCCESS","failures":[]}
    sys.path.insert(0,str(frozen/"validation")); sys.path.insert(0,str(repo/"validation"/"qsq_prospective"))
    import development_compatibility_smoke as dev
    try:
        chg_blob=b1.fetch(meta["url"])
        if hashlib.sha256(chg_blob).hexdigest()!=meta["sha256"] or len(chg_blob)!=int(meta["source_bytes"]): raise RuntimeError("CHGCAR checksum mismatch")
        a0=b1.fetch(b1.BUCKET+f"aeccar0s/{meta['task_id']}.json.gz")
        a2=b1.fetch(b1.BUCKET+f"aeccar2s/{meta['task_id']}.json.gz")
        with tempfile.TemporaryDirectory(prefix="qoacb3_") as td:
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

            qmap=pc.direct_atomic_charges(chg,labels,lattice,len(symbols))
            direct_error=float(np.max(np.abs(qmap-qref)))

            ae_raw=np.asarray(ae,dtype="<f8").ravel(order="F").tobytes()
            ae_lossless_bytes=AE_HEADER_BYTES+len(zlib.compress(ae_raw,6))

            wp=read_csv(repo/"analysis/extensions_20260930/WP-G/rows.csv")
            g1=best_g1(mid,wp,int(chg.nbytes))
            baseline_chg_bytes=int(g1["chgcar_bytes"])

            b2=[r for r in read_csv(a.b2_frontier) if r["material_id"]==mid and abs(float(r["kappa"])-4.0)<1e-12]
            if len(b2)!=1: raise RuntimeError("expected one B2 kappa=4 row")
            b2=b2[0]; b2_total=int(b2["total_bytes"])

            baseline_archive=baseline_chg_bytes+ae_lossless_bytes
            compiled_archive=b2_total+len(best_blob)
            result.update({
              "npoints":int(chg.size),"natoms":len(symbols),"nlabels":int(labels.max())+1,
              "max_partition_label":int(labels.max()),
              "raw_partition_bytes_uint32":int(labels.size*4),
              "packed_zlib_bytes":len(raw_blob),"rle_zlib_bytes":len(rle_blob),
              "best_partition_method":best_meta["method"],"best_partition_bytes":len(best_blob),
              "partition_decode_exact_raw":exact_raw,"partition_decode_exact_rle":exact_rle,"partition_decode_exact_best":exact_best,
              "direct_charge_max_error_e":direct_error,
              "ae_raw_float64_bytes":len(ae_raw),"ae_lossless_zlib_bytes":ae_lossless_bytes,
              "partition_replacement_ratio":ae_lossless_bytes/len(best_blob),
              "baseline_g1_codec":g1["codec"],"baseline_g1_chgcar_bytes":baseline_chg_bytes,
              "b2_chgcar_total_bytes":b2_total,
              "baseline_archive_bytes":baseline_archive,"compiled_archive_bytes":compiled_archive,
              "archive_ratio_baseline_over_compiled":baseline_archive/compiled_archive,
              "partition_fraction_of_compiled_archive":len(best_blob)/compiled_archive,
              "bader_solves":S.n
            })
    except Exception as e:
        import traceback
        result["status"]="FAILED"; result["failures"].append({"error":f"{type(e).__name__}: {e}"}); result["traceback"]=traceback.format_exc()
    result["wall_seconds"]=time.time()-t0
    (out/f"{mid}.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("QOAC_B3_DONE",mid,result["status"],"charge_error",result.get("direct_charge_max_error_e"),"partition_ratio",result.get("partition_replacement_ratio"),flush=True)
    return 0 if result["status"]=="SUCCESS" else 1

if __name__=="__main__": raise SystemExit(main())
