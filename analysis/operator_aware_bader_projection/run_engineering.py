#!/usr/bin/env python3
"""Verify QOAC-B2 projection-aware frontier on one engineering material."""
from __future__ import annotations

import argparse,csv,hashlib,json,sys,tempfile,time
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
B1=HERE.parent/"operator_aware_bader_fixed_partition"
sys.path.insert(0,str(B1))
import qoac_b_core as qb
import run_engineering as b1

KAPPAS=(1.0,2.0,4.0,8.0,16.0)
TAU=1e-3


def parse_csv(path):
    with Path(path).open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--frozen-root",type=Path,required=True)
    p.add_argument("--engineering-manifest",type=Path,required=True)
    p.add_argument("--engineering-rows",type=Path,required=True)
    p.add_argument("--engineering-verification",type=Path,required=True)
    p.add_argument("--index",type=int,required=True)
    p.add_argument("--bader",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    return p.parse_args()


def select_candidates(mid,rows,verification):
    base=[r for r in verification if r["material_id"]==mid and r["method"]=="P" and r["status"]=="OK" and abs(float(r["tau_e"])-TAU)<1e-15]
    if len(base)!=1:
        raise RuntimeError(f"expected one primary baseline record, got {len(base)}")
    b=base[0]
    base_cr=float(b["baseline_best_cr"]); base_linf=float(b["baseline_Linf"])
    prow=[r for r in rows if r["material_id"]==mid and r["method"]=="P" and float(r["max_rel_region_sum_error_scaled"])<=1e-9]
    out={}
    for k in KAPPAS:
        valid=[r for r in prow if float(r["final_Linf"])<=k*base_linf]
        if not valid:
            raise RuntimeError(f"no projected candidate at kappa={k:g}")
        best=max(valid,key=lambda r:float(r["compression_ratio"]))
        out[k]={
            "codec":best["codec"],
            "nominal_tolerance_relative":float(best["nominal_tolerance_relative"]),
            "nominal_tolerance_absolute":float(best["nominal_tolerance_absolute"]),
            "expected_payload_bytes":int(best["payload_bytes"]),
            "expected_side_channel_bytes":int(best["side_channel_bytes"]),
            "expected_total_bytes":int(best["total_bytes"]),
            "expected_cr":float(best["compression_ratio"]),
            "expected_linf":float(best["final_Linf"]),
            "baseline_cr":base_cr,
            "baseline_linf":base_linf,
        }
    return out


def main():
    a=parse_args()
    repo=a.repo_root.resolve(); frozen=a.frozen_root.resolve(); outdir=a.output_dir.resolve(); outdir.mkdir(parents=True,exist_ok=True)
    manifest=parse_csv(a.engineering_manifest)
    if not 0<=a.index<len(manifest): raise SystemExit("index out of range")
    meta=manifest[a.index]; mid=meta["material_id"]
    rows=parse_csv(a.engineering_rows); verification=parse_csv(a.engineering_verification)
    selected=select_candidates(mid,rows,verification)

    sys.path.insert(0,str(frozen/"validation"))
    sys.path.insert(0,str(repo/"validation"/"qsq_prospective"))
    import external_end_to_end as core
    import development_compatibility_smoke as dev

    t0=time.time()
    result={"material_id":mid,"status":"SUCCESS","frontier":[],"failures":[]}
    try:
        chg_blob=b1.fetch(meta["url"])
        if hashlib.sha256(chg_blob).hexdigest()!=meta["sha256"] or len(chg_blob)!=int(meta["source_bytes"]):
            raise RuntimeError("CHGCAR checksum/byte mismatch")
        a0=b1.fetch(b1.BUCKET+f"aeccar0s/{meta['task_id']}.json.gz")
        a2=b1.fetch(b1.BUCKET+f"aeccar2s/{meta['task_id']}.json.gz")
        with tempfile.TemporaryDirectory(prefix="qoacb2_") as td:
            work=Path(td)
            grid,_=dev.build_grid(meta,chg_blob,work)
            chg=np.ascontiguousarray(np.asarray(grid.total,dtype=np.float64))
            ae=np.asarray(dev.decode_mp_chgcar(a0).data["total"],dtype=np.float64)+np.asarray(dev.decode_mp_chgcar(a2).data["total"],dtype=np.float64)
            st=grid.structure; lattice=np.asarray(st.lattice.matrix,float); frac=np.asarray(st.frac_coords,float); symbols=[s.specie.symbol for s in st]
            S=b1.Solver(a.bader,lattice,frac,symbols,chg.shape,work)
            qref,lflat=S(chg,ae)
            labels=qb.label_grid_from_fortran_flat(lflat,chg.shape)
            side=qb.side_channel_from_field(chg,labels); side_bytes=len(side.to_bytes())

            # Deduplicate codec/tolerance candidates selected by multiple kappas.
            cache={}
            for k,c in selected.items():
                key=(c["codec"],c["nominal_tolerance_relative"],c["nominal_tolerance_absolute"])
                if key not in cache:
                    rr={
                        "codec":c["codec"],
                        "nominal_tolerance_relative":str(c["nominal_tolerance_relative"]),
                        "nominal_tolerance_absolute":str(c["nominal_tolerance_absolute"]),
                    }
                    rec,nb=b1.rebuild("P",rr,chg,None,labels,side,core,work)
                    fm=qb.field_metrics(chg,rec); cm=qb.closure_metrics(chg,rec,labels)
                    total=int(nb)+side_bytes
                    if int(nb)!=c["expected_payload_bytes"] or total!=c["expected_total_bytes"]:
                        raise RuntimeError(f"byte-accounting drift for {key}: got {nb}+{side_bytes}, expected {c['expected_payload_bytes']}+{c['expected_side_channel_bytes']}")
                    if abs(fm["final_Linf"]-c["expected_linf"])>max(1e-10,1e-10*abs(c["expected_linf"])):
                        raise RuntimeError(f"Linf reproduction drift for {key}")
                    q,lab=S(rec,ae)
                    cache[key]={
                        "codec":c["codec"],
                        "nominal_tolerance_relative":c["nominal_tolerance_relative"],
                        "nominal_tolerance_absolute":c["nominal_tolerance_absolute"],
                        "payload_bytes":int(nb),"side_channel_bytes":side_bytes,"total_bytes":total,
                        "compression_ratio":chg.nbytes/total,
                        **fm,**cm,
                        "actual_bader_error_e":float(np.max(np.abs(q-qref))),
                        "actual_reassigned_frac":float(np.mean(lab!=lflat)),
                    }

            for k,c in selected.items():
                key=(c["codec"],c["nominal_tolerance_relative"],c["nominal_tolerance_absolute"])
                z=dict(cache[key])
                z.update({
                    "kappa":k,
                    "baseline_cr":c["baseline_cr"],
                    "baseline_Linf":c["baseline_linf"],
                    "cr_ratio_over_baseline":z["compression_ratio"]/c["baseline_cr"],
                    "linf_ratio_over_baseline":z["final_Linf"]/c["baseline_linf"],
                    "side_channel_fraction":side_bytes/z["total_bytes"],
                })
                result["frontier"].append(z)
            result["bader_solves"]=S.n
            result["nlabels"]=int(side.sums.size)
            result["natoms"]=len(symbols)
    except Exception as e:
        import traceback
        result["status"]="FAILED"
        result["failures"].append({"error":f"{type(e).__name__}: {e}"})
        result["traceback"]=traceback.format_exc()
    result["wall_seconds"]=time.time()-t0
    (outdir/f"{mid}.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    if result["status"]!="SUCCESS":
        print("QOAC_B2_FAILURE",mid,result["failures"],flush=True)
    print("QOAC_B2_DONE",mid,result["status"],"frontier",len(result["frontier"]),"solves",result.get("bader_solves"),flush=True)
    return 0 if result["status"]=="SUCCESS" else 1

if __name__=="__main__":
    raise SystemExit(main())
