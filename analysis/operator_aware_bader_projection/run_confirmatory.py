#!/usr/bin/env python3
"""Confirm QOAC-B2 on a frozen holdout shard, verifying every transformed row."""
from __future__ import annotations

import argparse,csv,hashlib,itertools,json,os,subprocess,sys,tempfile,time,traceback,urllib.request
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"operator_aware_bader_fixed_partition"))
import qoac_b_core as qb

BUCKET="https://materialsproject-parsed.s3.amazonaws.com/"
USER_AGENT="QOAC-B2-confirmatory/1.0 research"


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
    d=hashlib.sha256(("QOAC-B2-CONFIRM|"+mid).encode()).digest()
    return int.from_bytes(d[:8],"big")%n


def fetch(url):
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
        f.write("QOAC-B2 confirmatory\n1.0\n")
        np.savetxt(f,lattice,fmt="%.17g")
        f.write(" ".join(s for s,n in groups)+"\n"+" ".join(str(n) for s,n in groups)+"\nDirect\n")
        np.savetxt(f,frac,fmt="%.17g")
        f.write("\n"+" ".join(map(str,field.shape))+"\n")
        flat=np.asarray(field,dtype=float).ravel(order="F"); end=len(flat)//5*5
        if end: np.savetxt(f,flat[:end].reshape(-1,5),fmt="%.17g")
        if end<len(flat): f.write(" ".join(format(v,".17g") for v in flat[end:])+"\n")


def read_atindex(path,shape):
    txt=path.read_text().split("\n"); dims=" ".join(map(str,shape))
    i=next(k for k,ln in enumerate(txt) if ln.split()==dims.split())
    vals=np.array(" ".join(txt[i+1:]).split()[:int(np.prod(shape))],dtype=float)
    return np.rint(vals).astype(np.int32)


class Solver:
    def __init__(self,bader,lattice,frac,symbols,shape,work):
        self.bader=Path(bader); self.lattice=lattice; self.frac=frac; self.symbols=symbols; self.shape=shape; self.work=work
        self.ref_written=False; self.n=0
    def __call__(self,field,reference):
        for p in self.work.glob("*.dat"): p.unlink()
        write_chgcar(self.work/"CHGCAR",field,self.lattice,self.frac,self.symbols)
        if not self.ref_written:
            write_chgcar(self.work/"REFCAR",reference,self.lattice,self.frac,self.symbols); self.ref_written=True
        cmd=[str(self.bader),"CHGCAR","-ref","REFCAR","-b","ongrid","-vac","0.001","-p","atom_index"]
        with (self.work/"bader.log").open("w") as f:
            rc=subprocess.call(cmd,cwd=self.work,stdout=f,stderr=subprocess.STDOUT)
        if rc: raise RuntimeError(f"Henkelman exit {rc}: "+(self.work/"bader.log").read_text()[-500:])
        rr=[ln.split() for ln in (self.work/"ACF.dat").read_text().splitlines()]
        data=[[float(x) for x in row[:7]] for row in rr if len(row)>=7 and row[0].isdigit()]
        if len(data)!=len(self.symbols): raise RuntimeError("ACF atom count mismatch")
        self.n+=1
        return np.array([x[4] for x in data],float),read_atindex(self.work/"AtIndex.dat",self.shape)


def process(meta,repo,frozen,bader,outdir):
    mid=meta["material_id"]; task_id=meta["task_id"]; t0=time.time()
    out={"material_id":mid,"status":"SUCCESS","rows":[],"failures":[]}
    try:
        sys.path.insert(0,str(frozen/"validation")); sys.path.insert(0,str(repo/"validation"/"qsq_prospective"))
        import external_end_to_end as core
        import development_compatibility_smoke as dev
        chg_blob=fetch(meta["url"])
        if hashlib.sha256(chg_blob).hexdigest()!=meta["sha256"] or len(chg_blob)!=int(meta["source_bytes"]):
            raise RuntimeError("CHGCAR checksum/byte mismatch")
        a0=fetch(BUCKET+f"aeccar0s/{task_id}.json.gz"); a2=fetch(BUCKET+f"aeccar2s/{task_id}.json.gz")
        with tempfile.TemporaryDirectory(prefix="qoacb2_") as td:
            work=Path(td)
            grid,_=dev.build_grid(meta,chg_blob,work)
            chg=np.ascontiguousarray(np.asarray(grid.total,dtype=np.float64))
            ae=np.asarray(dev.decode_mp_chgcar(a0).data["total"],float)+np.asarray(dev.decode_mp_chgcar(a2).data["total"],float)
            if ae.shape!=chg.shape or not np.all(np.isfinite(ae)): raise RuntimeError("invalid AECCAR")
            st=grid.structure; lattice=np.asarray(st.lattice.matrix,float); frac=np.asarray(st.frac_coords,float); symbols=[s.specie.symbol for s in st]
            S=Solver(bader,lattice,frac,symbols,chg.shape,work)
            qref,lflat=S(chg,ae); labels=qb.label_grid_from_fortran_flat(lflat,chg.shape)
            side=qb.side_channel_from_field(chg,labels); side_bytes=len(side.to_bytes())
            rows=[r for r in csv.DictReader(open(repo/"analysis/extensions_20260930/WP-G/rows.csv",encoding="utf-8"))
                  if r["material_id"]==mid and r["status"]=="OK"]
            if not rows: raise RuntimeError("no frozen WP-G rows")
            for rr in rows:
                rec,nb,_=core.codec_roundtrip(rr["codec"].lower(),chg,float(rr["nominal_tolerance_absolute"]),work)
                rec=np.asarray(rec,dtype=np.float64)
                proj=qb.project_to_region_sums(rec,labels,side.sums)
                fm=qb.field_metrics(chg,proj); cm=qb.closure_metrics(chg,proj,labels)
                q,lab=S(proj,ae)
                berr=float(np.max(np.abs(q-qref))); reass=float(np.mean(lab!=lflat))
                out["rows"].append({
                    "material_id":mid,"codec":rr["codec"],
                    "nominal_tolerance_relative":float(rr["nominal_tolerance_relative"]),
                    "nominal_tolerance_absolute":float(rr["nominal_tolerance_absolute"]),
                    "generic_payload_bytes":int(rr["chgcar_bytes"]),
                    "side_channel_bytes":side_bytes,"total_bytes":int(nb)+side_bytes,
                    "generic_cr":chg.nbytes/int(rr["chgcar_bytes"]),
                    "qoac_b_cr":chg.nbytes/(int(nb)+side_bytes),
                    "generic_Linf":float(rr["realized_Linf"]),
                    "generic_bader_error_e":float(rr["g1_error_e"]),
                    "generic_reassigned_frac":float(rr["g1_reassigned_frac"]),
                    **fm,**cm,
                    "actual_bader_error_e":berr,"actual_reassigned_frac":reass,
                    "rate_overhead_fraction":side_bytes/max(int(nb),1),
                    "linf_inflation_ratio":fm["final_Linf"]/max(float(rr["realized_Linf"]),1e-300),
                })
            out.update(npoints=int(chg.size),raw_bytes=int(chg.nbytes),natoms=len(symbols),nlabels=int(side.sums.size),
                       side_channel_bytes=side_bytes,bader_solves=S.n,
                       extra_partition_label_count=max(0,int(side.sums.size)-1-len(symbols)))
    except Exception as e:
        out["status"]="FAILED"; out["failures"].append({"error":f"{type(e).__name__}: {e}"}); out["traceback"]=traceback.format_exc()
    out["wall_seconds"]=time.time()-t0
    (outdir/f"{mid}.json").write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    print("QOAC_B2_DONE",mid,out["status"],"rows",len(out["rows"]),"solves",out.get("bader_solves"),flush=True)
    return out["status"]=="SUCCESS"


def main():
    a=parse_args(); repo=a.repo_root.resolve(); frozen=a.frozen_root.resolve(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    manifest=list(csv.DictReader(open(a.manifest,encoding="utf-8")))
    planned=[m for m in manifest if shard_for(m["material_id"],a.shard_count)==a.shard_index]
    ok=True
    for m in planned: ok=process(m,repo,frozen,a.bader,out) and ok
    (out/f"planned_shard_{a.shard_index:02d}.json").write_text(json.dumps([m["material_id"] for m in planned],indent=2)+"\n")
    return 0 if ok else 1
if __name__=="__main__": raise SystemExit(main())
