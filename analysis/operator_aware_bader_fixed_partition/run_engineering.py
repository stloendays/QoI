#!/usr/bin/env python3
"""Run one QOAC-B1 engineering material with exact AECCAR partition."""
from __future__ import annotations
import argparse,csv,gzip,hashlib,itertools,json,math,os,subprocess,sys,tempfile,time,urllib.request
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import qoac_b_core as qb

TAUS=(1e-4,1e-3,1e-2)
MATCH_LINF_FACTOR=1.05
BUCKET="https://materialsproject-parsed.s3.amazonaws.com/"
USER_AGENT="QOAC-B1/1.0 research"


def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--frozen-root",type=Path,required=True)
    p.add_argument("--engineering-manifest",type=Path,required=True)
    p.add_argument("--index",type=int,required=True)
    p.add_argument("--bader",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    return p.parse_args()


def fetch(url:str)->bytes:
    err=None
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":USER_AGENT}),timeout=900) as r:
                return r.read()
        except Exception as e:
            err=e; time.sleep(5*(k+1))
    raise RuntimeError(f"download failed {url}: {type(err).__name__}: {err}")


def write_chgcar(path,field,lattice,frac,symbols):
    groups=[(s,len(list(g))) for s,g in itertools.groupby(symbols)]
    with path.open("w") as f:
        f.write("QOAC-B1 exact-reference Bader\n1.0\n")
        np.savetxt(f,lattice,fmt="%.17g")
        f.write(" ".join(s for s,n in groups)+"\n"+" ".join(str(n) for s,n in groups)+"\nDirect\n")
        np.savetxt(f,frac,fmt="%.17g")
        f.write("\n"+" ".join(map(str,field.shape))+"\n")
        flat=np.asarray(field,dtype=float).ravel(order="F")
        end=len(flat)//5*5
        if end: np.savetxt(f,flat[:end].reshape(-1,5),fmt="%.17g")
        if end<len(flat): f.write(" ".join(format(v,".17g") for v in flat[end:])+"\n")


def read_atindex(path,shape):
    txt=path.read_text().split("\n"); dims=" ".join(map(str,shape))
    i=next(k for k,ln in enumerate(txt) if ln.split()==dims.split())
    vals=np.array(" ".join(txt[i+1:]).split()[:int(np.prod(shape))],dtype=float)
    return np.rint(vals).astype(np.int32)


class Solver:
    def __init__(self,bader,lattice,frac,symbols,shape,work):
        self.bader=Path(bader); self.lattice=lattice; self.frac=frac; self.symbols=symbols; self.shape=shape; self.work=work; self.n=0
        self.ref_written=False
    def __call__(self,field,reference):
        w=self.work
        for p in w.glob("*.dat"): p.unlink()
        write_chgcar(w/"CHGCAR",field,self.lattice,self.frac,self.symbols)
        if not self.ref_written:
            write_chgcar(w/"REFCAR",reference,self.lattice,self.frac,self.symbols); self.ref_written=True
        cmd=[str(self.bader),"CHGCAR","-ref","REFCAR","-b","ongrid","-vac","0.001","-p","atom_index"]
        with (w/"bader.log").open("w") as f:
            rc=subprocess.call(cmd,cwd=w,stdout=f,stderr=subprocess.STDOUT)
        if rc: raise RuntimeError(f"Henkelman exit {rc}: "+(w/"bader.log").read_text()[-500:])
        rr=[ln.split() for ln in (w/"ACF.dat").read_text().splitlines()]
        data=[[float(x) for x in row[:7]] for row in rr if len(row)>=7 and row[0].isdigit()]
        if len(data)!=len(self.symbols): raise RuntimeError("ACF atom count mismatch")
        self.n+=1
        return np.array([x[4] for x in data],dtype=float), read_atindex(w/"AtIndex.dat",self.shape)


def rebuild(method,row,chg,residual,labels,side,core,work):
    codec=row["codec"].lower(); abs_c=float(row["nominal_tolerance_absolute"])
    if method=="P":
        rec,nb,_=core.codec_roundtrip(codec,chg,abs_c,work)
        rec=np.asarray(rec,dtype=np.float64)
        out=qb.project_to_region_sums(rec,labels,side.sums)
    elif method=="R":
        rec,nb,_=core.codec_roundtrip(codec,residual,abs_c,work)
        rec=np.asarray(rec,dtype=np.float64)
        out=qb.reconstruct_from_basin_residual(rec,labels,side)
    else:
        raise ValueError(method)
    return out,int(nb)


def main():
    a=parse_args(); repo=a.repo_root.resolve(); frozen=a.frozen_root.resolve(); outdir=a.output_dir.resolve(); outdir.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(frozen/"validation"))
    sys.path.insert(0,str(repo/"validation"/"qsq_prospective"))
    import external_end_to_end as core
    import development_compatibility_smoke as dev

    manifest=list(csv.DictReader(open(a.engineering_manifest,encoding="utf-8")))
    if not 0<=a.index<len(manifest): raise SystemExit("engineering index out of range")
    meta=manifest[a.index]; mid=meta["material_id"]; task_id=meta["task_id"]
    t0=time.time(); result={"material_id":mid,"status":"SUCCESS","rows":[],"verification":[],"failures":[]}
    try:
        chg_blob=fetch(meta["url"])
        if hashlib.sha256(chg_blob).hexdigest()!=meta["sha256"] or len(chg_blob)!=int(meta["source_bytes"]): raise RuntimeError("CHGCAR checksum/byte mismatch")
        a0=fetch(BUCKET+f"aeccar0s/{task_id}.json.gz"); a2=fetch(BUCKET+f"aeccar2s/{task_id}.json.gz")
        with tempfile.TemporaryDirectory(prefix="qoacb1_") as td:
            work=Path(td)
            grid,_=dev.build_grid(meta,chg_blob,work)
            chg=np.ascontiguousarray(np.asarray(grid.total,dtype=np.float64))
            ae=np.asarray(dev.decode_mp_chgcar(a0).data["total"],dtype=np.float64)+np.asarray(dev.decode_mp_chgcar(a2).data["total"],dtype=np.float64)
            if ae.shape!=chg.shape or not np.all(np.isfinite(ae)): raise RuntimeError("invalid AECCAR")
            st=grid.structure; lattice=np.asarray(st.lattice.matrix,float); frac=np.asarray(st.frac_coords,float); symbols=[s.specie.symbol for s in st]
            S=Solver(a.bader,lattice,frac,symbols,chg.shape,work)
            qref,lflat=S(chg,ae)
            labels=qb.label_grid_from_fortran_flat(lflat,chg.shape)
            side,residual=qb.decompose_to_basin_residual(chg,labels); side_blob=side.to_bytes()
            residual_fraction=float(np.sum(residual*residual)/max(np.sum(chg*chg),1e-300))
            counts=qb.region_counts(labels)
            result.update(
                npoints=int(chg.size),raw_bytes=int(chg.nbytes),natoms=len(symbols),nlabels=int(side.sums.size),
                max_partition_label=int(labels.max()),extra_partition_label_count=max(0,int(side.sums.size)-1-len(symbols)),
                label0_voxels=int(counts[0] if len(counts) else 0),label0_fraction=float((counts[0] if len(counts) else 0)/chg.size),
                side_channel_bytes=len(side_blob),residual_energy_fraction=residual_fraction,
                aeccar0_sha256=hashlib.sha256(a0).hexdigest(),aeccar2_sha256=hashlib.sha256(a2).hexdigest(),
                reference_q=qref.tolist()
            )
            wp=[r for r in csv.DictReader(open(repo/"analysis/extensions_20260930/WP-G/rows.csv",encoding="utf-8")) if r["material_id"]==mid and r["status"]=="OK"]
            if not wp: raise RuntimeError("no WP-G rows")
            candidates={"P":[],"R":[]}
            for rr in wp:
                base={
                    "material_id":mid,"codec":rr["codec"],"nominal_tolerance_relative":float(rr["nominal_tolerance_relative"]),
                    "nominal_tolerance_absolute":float(rr["nominal_tolerance_absolute"]),
                    "baseline_bytes":int(rr["chgcar_bytes"]),"baseline_cr":chg.nbytes/int(rr["chgcar_bytes"]),
                    "baseline_Linf":float(rr["realized_Linf"]),"baseline_g1_error_e":float(rr["g1_error_e"]),
                    "baseline_g1_reassigned_frac":float(rr["g1_reassigned_frac"])
                }
                for method in ("P","R"):
                    ts=time.perf_counter(); rec,nb=rebuild(method,rr,chg,residual,labels,side,core,work)
                    fm=qb.field_metrics(chg,rec); cm=qb.closure_metrics(chg,rec,labels)
                    total=int(nb)+len(side_blob)
                    row=dict(base,method=method,payload_bytes=int(nb),side_channel_bytes=len(side_blob),total_bytes=total,
                             compression_ratio=chg.nbytes/total,encode_decode_seconds=time.perf_counter()-ts,**fm,**cm)
                    result["rows"].append(row); candidates[method].append((row,rr))
            # Frozen matched-Linf selection followed by actual Bader verification.
            for tau in TAUS:
                eligible=[r for r in wp if float(r["g1_error_e"])<tau]
                if not eligible:
                    result["verification"].append({"tau_e":tau,"status":"NO_BASELINE"})
                    continue
                bbest=max(eligible,key=lambda r:chg.nbytes/int(r["chgcar_bytes"]))
                eps=float(bbest["realized_Linf"]); bcr=chg.nbytes/int(bbest["chgcar_bytes"])
                for method in ("P","R"):
                    valid=[x for x in candidates[method] if x[0]["final_Linf"]<=MATCH_LINF_FACTOR*eps and x[0]["max_rel_region_sum_error_scaled"]<=1e-9]
                    if not valid:
                        result["verification"].append({"tau_e":tau,"method":method,"status":"NO_MATCH","baseline_best_cr":bcr,"baseline_Linf":eps})
                        continue
                    row,rr=max(valid,key=lambda x:x[0]["compression_ratio"])
                    rec,_=rebuild(method,rr,chg,residual,labels,side,core,work)
                    q,lab=S(rec,ae)
                    verr=float(np.max(np.abs(q-qref))); reass=float(np.mean(lab!=lflat))
                    result["verification"].append({
                        "tau_e":tau,"method":method,"status":"OK","codec":row["codec"],
                        "nominal_tolerance_relative":row["nominal_tolerance_relative"],
                        "baseline_best_cr":bcr,"baseline_Linf":eps,
                        "candidate_cr":row["compression_ratio"],"candidate_Linf":row["final_Linf"],
                        "cr_ratio_candidate_over_baseline":row["compression_ratio"]/bcr,
                        "actual_bader_error_e":verr,"actual_reassigned_frac":reass,
                        "closure_scaled":row["max_rel_region_sum_error_scaled"],
                    })
            result["bader_solves"]=S.n
    except Exception as e:
        import traceback
        result["status"]="FAILED"; result["failures"].append({"stage":"material","error":f"{type(e).__name__}: {e}"}); result["traceback"]=traceback.format_exc()
    result["wall_seconds"]=time.time()-t0
    (outdir/f"{mid}.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    if result["status"]!="SUCCESS":
        print("QOAC_B1_FAILURE",mid,result.get("failures"),flush=True)
    print("QOAC_B1_DONE",mid,result["status"],"rows",len(result["rows"]),"verifications",len(result["verification"]),"solves",result.get("bader_solves"))
    return 0 if result["status"]=="SUCCESS" else 1

if __name__=="__main__": raise SystemExit(main())
