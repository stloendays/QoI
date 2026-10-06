#!/usr/bin/env python3
"""QOAC-HB: certify one stream for Hartree potential and Bader charge (see DESIGN.md)."""
from __future__ import annotations
import argparse,csv,hashlib,json,sys,tempfile,time
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
A=HERE.parent
sys.path.insert(0,str(A/"operator_aware_bader_fixed_partition"))
sys.path.insert(0,str(A/"qoac_h_strong_baselines"))
import qoac_b_core as qb
import run_engineering as b1
import truncation_codec as t1
qoac=t1.qoac

TAU_H=1e-6; TAU_B=1e-3; CLOSURE=1e-9; MAX_ATTEMPTS=5
ALPHA_REL=np.logspace(-7.0,1.0,25)
Q_CUTS=(0.05,0.075,0.10,0.15,0.20,0.30,0.50,0.75,1.00)

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

def shard_for(mid,n):
    return int.from_bytes(hashlib.sha256(("QOAC-HB-JOINT|"+mid).encode()).digest()[:8],"big")%n

def write_csv(path,rows):
    fields=[]
    for r in rows:
        for k in r:
            if k not in fields: fields.append(k)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def process(meta,a,core,dev,wp_all):
    mid=meta["material_id"]; out={"material_id":mid,"system_type":meta["system_type"],"rows":[],"bader":[],"failures":[]}
    chg_blob=b1.fetch(meta["url"])
    if hashlib.sha256(chg_blob).hexdigest()!=meta["sha256"]: raise RuntimeError("CHGCAR checksum mismatch")
    a0=b1.fetch(b1.BUCKET+f"aeccar0s/{meta['task_id']}.json.gz"); a2=b1.fetch(b1.BUCKET+f"aeccar2s/{meta['task_id']}.json.gz")
    with tempfile.TemporaryDirectory(prefix="qoachb_") as td:
        work=Path(td)
        grid,_=dev.build_grid(meta,chg_blob,work)
        chg=np.ascontiguousarray(np.asarray(grid.total,dtype=np.float64))
        ae=np.asarray(dev.decode_mp_chgcar(a0).data["total"],float)+np.asarray(dev.decode_mp_chgcar(a2).data["total"],float)
        if ae.shape!=chg.shape or not np.all(np.isfinite(ae)): raise RuntimeError("invalid AECCAR")
        st=grid.structure; lat=np.asarray(st.lattice.matrix,float)
        S=b1.Solver(a.bader,lat,np.asarray(st.frac_coords,float),[s.specie.symbol for s in st],chg.shape,work)
        qref,lflat=S(chg,ae)
        labels=qb.label_grid_from_fortran_flat(lflat,chg.shape)
        side=qb.side_channel_from_field(chg,labels); side_bytes=len(side.to_bytes())
        rh,rs=qoac.reference_hartree_rms(chg,lat); ptp=float(np.ptp(chg)); raw=chg.nbytes
        out.update(npoints=int(chg.size),raw_bytes=int(raw),side_channel_bytes=side_bytes,natoms=len(qref))
        prep=qoac.prepare_field(chg,lat,shell_count=32)
        wp=[r for r in wp_all if r["material_id"]==mid and r["status"]=="OK"]
        gens=[]
        for ar in ALPHA_REL: gens.append(("J",f"alpha_rel={ar:.6g}",("J",float(ar))))
        for qc in Q_CUTS:
            for ar in ALPHA_REL: gens.append(("T1P",f"q_cut={qc};alpha_rel={ar:.6g}",("T1",qc,float(ar))))
        for r in wp: gens.append(("GP",f"{r['codec']};tol_rel={r['nominal_tolerance_relative']}",("GP",r["codec"].lower(),float(r["nominal_tolerance_absolute"]))))
        def decode(spec):
            if spec[0]=="J":
                blob,_=qoac.encode_prepared(prep,alpha=spec[1]*ptp,beta=2.0,zlib_level=6); rec,_,_=qoac.decode_blob(blob); return rec,len(blob)
            if spec[0]=="T1":
                blob=t1.encode(prep,alpha=spec[2]*ptp,q_cut=spec[1]); return t1.decode(blob),len(blob)
            rec,nb,_=core.codec_roundtrip(spec[1],chg,spec[2],work); return np.asarray(rec,float),int(nb)
        specs={}
        for arm,param,spec in gens:
            try:
                rec,nb=decode(spec)
                h0=qoac.hartree_error_metrics(rec-chg,lat,rh,rs)
                prj=qb.project_to_region_sums(rec,labels,side.sums)
                eh,es=qoac.hartree_error_metrics(prj-chg,lat,rh,rs)
                cm=qb.closure_metrics(chg,prj,labels); e=prj-chg; tot=nb+side_bytes
                key=f"{arm}|{param}"; specs[key]=spec
                out["rows"].append({"material_id":mid,"arm":arm,"param":param,"payload_bytes":nb,"total_bytes":tot,
                    "compression_ratio":raw/tot,"hartree_hist_pre":h0[0],"hartree_safe_pre":h0[1],
                    "hartree_hist":eh,"hartree_safe":es,"closure_scaled":cm["max_rel_region_sum_error_scaled"],
                    "density_Linf":float(np.max(np.abs(e))),"density_RMSE":float(np.sqrt(np.mean(e*e))),
                    "side_channel_fraction":side_bytes/tot})
            except Exception as exc:
                out["failures"].append({"material_id":mid,"arm":arm,"param":param,"error":f"{type(exc).__name__}: {exc}"[:400]})
        for arm in ("J","T1P","GP"):
            ok=[r for r in out["rows"] if r["arm"]==arm and r["hartree_hist"]<TAU_H and r["hartree_safe"]<TAU_H and r["closure_scaled"]<=CLOSURE]
            ok.sort(key=lambda r:-r["compression_ratio"])
            for k,r in enumerate(ok[:MAX_ATTEMPTS]):
                rec,_=decode(specs[f"{arm}|{r['param']}"])
                prj=qb.project_to_region_sums(rec,labels,side.sums)
                q,lab=S(prj,ae); err=float(np.max(np.abs(q-qref))); rea=float(np.mean(lab!=lflat))
                rowb={"material_id":mid,"arm":arm,"param":r["param"],"attempt":k+1,"compression_ratio":r["compression_ratio"],
                      "bader_error_e":err,"reassigned_frac":rea,"certified":bool(err<=TAU_B and rea==0.0)}
                if arm=="J":
                    q0,lab0=S(rec,ae); rowb["unprojected_bader_error_e"]=float(np.max(np.abs(q0-qref))); rowb["unprojected_reassigned_frac"]=float(np.mean(lab0!=lflat))
                out["bader"].append(rowb)
                if rowb["certified"]: break
    return out

def main():
    a=parse_args(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(a.frozen_root.resolve()/"validation")); sys.path.insert(0,str(a.repo_root.resolve()/"validation"/"qsq_prospective"))
    import external_end_to_end as core
    import development_compatibility_smoke as dev
    wp_all=list(csv.DictReader(open(a.repo_root/"analysis/extensions_20260930/WP-G/rows.csv",encoding="utf-8")))
    manifest=list(csv.DictReader(open(a.manifest,encoding="utf-8")))
    planned=[m for m in manifest if shard_for(m["material_id"],a.shard_count)==a.shard_index]
    rows=[]; bader=[]; fails=[]; mats=[]
    for meta in planned:
        t0=time.time()
        try:
            r=process(meta,a,core,dev,wp_all)
            rows+=r.pop("rows"); bader+=r.pop("bader"); fails+=r.pop("failures"); mats.append(r|{"status":"SUCCESS","seconds":time.time()-t0})
        except Exception as exc:
            mats.append({"material_id":meta["material_id"],"status":"FAILED","error":f"{type(exc).__name__}: {exc}"[:400]})
        print(f"QOACHB_DONE {meta['material_id']} {mats[-1]['status']} seconds={time.time()-t0:.1f}",flush=True)
    i=a.shard_index
    for name,data in (("rows",rows),("bader",bader),("failures",fails),("materials",mats)):
        write_csv(out/f"{name}_shard_{i:02d}.csv",data if data else [{"material_id":""}])
    return 0

if __name__=="__main__": raise SystemExit(main())
