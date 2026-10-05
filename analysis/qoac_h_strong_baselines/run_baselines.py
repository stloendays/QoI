#!/usr/bin/env python3
"""Run the frozen strongest-baseline arms (T1, M, V) for QOAC-H; see DESIGN.md."""
from __future__ import annotations
import argparse,csv,hashlib,math,shutil,subprocess,sys,tempfile,time
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import truncation_codec as t1
qoac=t1.qoac

ALPHA_REL=np.logspace(-7.0,1.0,25)
Q_CUTS=(0.05,0.075,0.10,0.15,0.20,0.30,0.50,0.75,1.00)
MGARD_S=("inf","0","-1")
VH_TOL_REL=np.logspace(-9.0,-1.0,25)
VH_CODECS=("zfp","sz3","sperr")

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--frozen-root",type=Path,required=True,help="checkout of commit 893f931 (codec roundtrips)")
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--arms",default="t1,mgard,vh")
    p.add_argument("--shard-count",type=int,default=1)
    p.add_argument("--shard-index",type=int,default=0)
    p.add_argument("--only",default="")
    p.add_argument("--cache-dir",type=Path,default=None)
    p.add_argument("--output-dir",type=Path,required=True)
    return p.parse_args()

def shard_for(mid,n):
    return int.from_bytes(hashlib.sha256(("QOAC-H-STRONG-BASELINES|"+mid).encode()).digest()[:8],"big")%n

def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    fields=[]
    for r in rows:
        for k in r:
            if k not in fields: fields.append(k)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def mgard_roundtrip(x,tol,s,td):
    exe=shutil.which("mgard")
    if exe is None: raise RuntimeError("mgard CLI not found")
    src=td/"in.dat"; cmp=td/"out.mgard"; dst=td/"rec.dat"
    np.ascontiguousarray(x,dtype="<f8").tofile(src)
    shape="x".join(str(v) for v in x.shape)
    subprocess.run([exe,"compress","--datatype","double","--shape",shape,"--smoothness",s,
                    "--tolerance",repr(float(tol)),"--input",str(src),"--output",str(cmp)],check=True,capture_output=True,text=True)
    subprocess.run([exe,"decompress","--input",str(cmp),"--output",str(dst)],check=True,capture_output=True,text=True)
    nbytes=cmp.stat().st_size
    rec=np.fromfile(dst,dtype="<f8").reshape(x.shape)
    for f in (src,cmp,dst): f.unlink(missing_ok=True)
    return rec,nbytes

def main():
    a=parse_args(); repo=a.repo_root.resolve(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(repo/"validation"/"qsq_prospective"))
    sys.path.insert(0,str(a.frozen_root.resolve()/"validation"))
    import development_compatibility_smoke as dev
    arms=set(a.arms.split(","))
    manifest=list(csv.DictReader(open(a.manifest,encoding="utf-8")))
    if a.only: manifest=[r for r in manifest if r["material_id"] in a.only.split(",")]
    planned=[r for r in manifest if shard_for(r["material_id"],a.shard_count)==a.shard_index]
    rows=[]; failures=[]
    for meta in planned:
        mid=meta["material_id"]; t0=time.perf_counter()
        try:
            cache=(a.cache_dir/f"{mid}.src") if a.cache_dir else None
            if cache and cache.exists() and hashlib.sha256(cache.read_bytes()).hexdigest()==meta["sha256"]:
                blob=cache.read_bytes()
            else:
                blob=dev.fetch_exact(meta["url"],meta["sha256"],int(meta["source_bytes"]))
                if cache: cache.parent.mkdir(parents=True,exist_ok=True); cache.write_bytes(blob)
            with tempfile.TemporaryDirectory(prefix="qoach_sb_") as tds:
                td=Path(tds)
                grid,_=dev.build_grid(meta,blob,td)
                x=np.ascontiguousarray(np.asarray(grid.total,dtype=np.float64))
                lat=np.asarray(grid.structure.lattice.matrix,dtype=np.float64)
                if x.size!=int(meta["npoints"]): raise RuntimeError("npoints mismatch")
                ptp=float(np.ptp(x)); raw=x.nbytes
                rh,rs=qoac.reference_hartree_rms(x,lat)
                base={"material_id":mid,"system_type":meta["system_type"],"npoints":x.size,"raw_bytes":raw}
                def density_row(arm,param,setting,rec,nbytes,sec):
                    e=rec-x; eh,es=qoac.hartree_error_metrics(e,lat,rh,rs)
                    return base|{"arm":arm,"param":param,"setting_rel":float(setting),"total_bytes":int(nbytes),
                        "compression_ratio":raw/nbytes,"hartree_rel_rmse_historical":eh,"hartree_rel_rmse_safe":es,
                        "density_Linf":float(np.max(np.abs(e))),"density_RMSE":float(np.sqrt(np.mean(e*e))),"seconds":sec}
                if "t1" in arms:
                    prep=qoac.prepare_field(x,lat,shell_count=32)
                    for qc in Q_CUTS:
                        for ar in ALPHA_REL:
                            try:
                                s0=time.perf_counter(); blob1=t1.encode(prep,alpha=float(ar*ptp),q_cut=qc); rec=t1.decode(blob1)
                                rows.append(density_row("T1",f"q_cut={qc}",ar,rec,len(blob1),time.perf_counter()-s0))
                            except Exception as exc:
                                failures.append(base|{"arm":"T1","param":f"q_cut={qc}","setting_rel":float(ar),"error":f"{type(exc).__name__}: {exc}"[:400]})
                    del prep
                if "mgard" in arms:
                    for s in MGARD_S:
                        for tr in ALPHA_REL:
                            try:
                                s0=time.perf_counter(); rec,nb=mgard_roundtrip(x,tr*ptp,s,td)
                                rows.append(density_row("M",f"s={s}",tr,rec,nb,time.perf_counter()-s0))
                            except Exception as exc:
                                msg=getattr(exc,"stderr",None) or str(exc)
                                failures.append(base|{"arm":"M","param":f"s={s}","setting_rel":float(tr),"error":f"{type(exc).__name__}: {msg}"[:400]})
                if "vh" in arms:
                    import external_end_to_end as core
                    vh=qoac.hartree_potential_from_field(x,lat,safe=False); vptp=float(np.ptp(vh)); vrms=float(np.sqrt(np.mean(vh*vh)))
                    for codec in VH_CODECS:
                        for tr in VH_TOL_REL:
                            try:
                                s0=time.perf_counter(); rec,nb,_=core.codec_roundtrip(codec,vh,float(tr*vptp),td)
                                e=rec-vh
                                rows.append(base|{"arm":"V","param":f"codec={codec}","setting_rel":float(tr),"total_bytes":int(nb),
                                    "compression_ratio":raw/nb,"hartree_rel_rmse_historical":float(np.sqrt(np.mean(e*e))/vrms),
                                    "hartree_rel_rmse_safe":"","density_Linf":"","density_RMSE":"","seconds":time.perf_counter()-s0})
                            except Exception as exc:
                                failures.append(base|{"arm":"V","param":f"codec={codec}","setting_rel":float(tr),"error":f"{type(exc).__name__}: {exc}"[:400]})
        except Exception as exc:
            failures.append({"material_id":mid,"arm":"material","error":f"{type(exc).__name__}: {exc}"[:400]})
        print(f"QOACH_SB_DONE {mid} seconds={time.perf_counter()-t0:.1f}",flush=True)
    write_csv(out/f"rows_shard_{a.shard_index:02d}.csv",rows)
    write_csv(out/f"failures_shard_{a.shard_index:02d}.csv",failures)
    write_csv(out/f"planned_shard_{a.shard_index:02d}.csv",[{"material_id":r["material_id"]} for r in planned])
    return 0

if __name__=="__main__": raise SystemExit(main())
