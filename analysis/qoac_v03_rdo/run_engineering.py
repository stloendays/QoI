#!/usr/bin/env python3
"""QOAC v0.3 engineering: arms A0-A6 on the 12 QOAC-H engineering materials (see DESIGN.md)."""
from __future__ import annotations
import argparse,csv,hashlib,json,math,sys,tempfile,time,traceback
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE)); sys.path.insert(0,str(HERE.parent/"qoac_h_strong_baselines"))
import codec_qoac_v03 as v3
import truncation_codec as t1
v02=v3.v02

TAUS=(1e-4,1e-6,1e-8)
ALPHA_REL=np.logspace(-7.0,1.0,25)
MARGIN=0.995
BISECT_ITERS=60

def args():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--frozen-root",type=Path,required=True)
    p.add_argument("--cache-dir",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--workers",type=int,default=4)
    p.add_argument("--only",default="")
    return p.parse_args()

class Spec:
    """Exact spectral Hartree distortion for arbitrary per-orbit steps and keep masks."""
    def __init__(s,prep,ref_cons,ref_safe):
        topo=prep.topology; s.topo=topo
        c=prep.spectrum.ravel()[topo.rep_flat]; s.cr=c.real.copy(); s.ci=np.where(topo.self_conjugate,0.0,c.imag)
        s.selfc=topo.self_conjugate; s.m=np.where(s.selfc,1.0,2.0)
        s.w=v3.operator_weight(topo,"hartree_potential"); s.safe=~v3.nyquist_orbits(topo)
        s.mw=s.m*s.w; s.ref_cons=ref_cons; s.ref_safe=ref_safe
    def dist(s,steps,keep=None):
        qr=np.rint(s.cr/steps); qi=np.rint(s.ci/steps); qi[s.selfc]=0
        er=s.cr-qr*steps; ei=s.ci-qi*steps; e=s.mw*(er*er+ei*ei)
        if keep is not None: e=np.where(keep,e,s.mw*(s.cr*s.cr+s.ci*s.ci))
        return float(e.sum())/s.ref_cons, float(e[s.safe].sum())/s.ref_safe
    def ok(s,steps,tau,keep=None):
        a,b=s.dist(steps,keep); t=(MARGIN*tau)**2
        return a<=t and b<=t

def bisect_scale(ok,lo,hi):
    """Largest scale in [lo,hi] (log space) for which ok(scale) holds; returns None if ok(lo) fails."""
    if not ok(lo): return None
    if ok(hi): return hi
    best=lo; a,b=math.log(lo),math.log(hi)
    for _ in range(BISECT_ITERS):
        mid=0.5*(a+b)
        if ok(math.exp(mid)): a=mid; best=math.exp(mid)
        else: b=mid
        if b-a<1e-9: break
    return best

def certify(rec,x,lat,rh,rs):
    eh,es=v02.hartree_error_metrics(rec-x,lat,rh,rs); e=rec-x
    return eh,es,float(np.max(np.abs(e))),float(np.sqrt(np.mean(e*e)))

def material(job):
    meta,repo,frozen,cache=job
    sys.path.insert(0,str(Path(frozen)/"validation")); sys.path.insert(0,str(Path(repo)/"validation"/"qsq_prospective"))
    import development_compatibility_smoke as dev
    import external_end_to_end as core
    mid=meta["material_id"]; rows=[]; fails=[]; t0=time.time()
    try:
        cp=Path(cache)/f"{mid}.src"
        if cp.exists() and hashlib.sha256(cp.read_bytes()).hexdigest()==meta["sha256"]: blob=cp.read_bytes()
        else:
            blob=dev.fetch_exact(meta["url"],meta["sha256"],int(meta["source_bytes"])); cp.write_bytes(blob)
        with tempfile.TemporaryDirectory(prefix="v03eng_") as td:
            grid,_=dev.build_grid(meta,blob,Path(td))
            x=np.ascontiguousarray(np.asarray(grid.total,dtype=np.float64)); lat=np.asarray(grid.structure.lattice.matrix,float)
            work=Path(td)
            raw=x.nbytes; ptp=float(np.ptp(x)); rh,rs=v02.reference_hartree_rms(x,lat)
            base={"material_id":mid,"system_type":meta["system_type"],"npoints":x.size,"raw_bytes":raw}
            def add(arm,tau,param,nbytes,rec,secs):
                eh,es,li,rm=certify(rec,x,lat,rh,rs)
                rows.append(base|{"arm":arm,"tau":tau,"param":param,"bytes":int(nbytes),"cr":raw/nbytes,"hartree_hist":eh,
                    "hartree_safe":es,"certified":bool(eh<tau and es<tau),"density_Linf":li,"density_RMSE":rm,"seconds":secs})
                return eh<tau and es<tau
            # RDO analyses (one per variant, reused across tolerances)
            ts=time.time(); anO=v3.analyze(x,lat,prior="operator",reference_historical_rms=rh,d_floor_rel=1e-3*min(TAUS)**2/32)
            tO=time.time()-ts; ts=time.time()
            anF=v3.analyze(x,lat,prior="flat",reference_historical_rms=rh,d_floor_rel=1e-3*min(TAUS)**2/32); tF=time.time()-ts; ts=time.time()
            anB=v3.analyze(x,lat,prior="flat",reference_historical_rms=rh,d_floor_rel=1e-3*min(TAUS)**2/32,select_operator="density"); tB=time.time()-ts
            prep=anO.prep; S=Spec(prep,anO.ref_cons_spec,anO.ref_safe_spec)
            q2=prep.topology.q**2
            ladder0=[]
            for ar in ALPHA_REL:
                blob0,_=v02.encode_prepared(prep,alpha=float(ar*ptp),beta=2.0,zlib_level=6); rec,_,_=v02.decode_blob(blob0)
                eh,es=v02.hartree_error_metrics(rec-x,lat,rh,rs); ladder0.append((ar,len(blob0),eh,es))
            for tau in TAUS:
                # A0 frozen ladder (metrics computed once, re-decoded for the chosen rung)
                best=None
                for ar,nb,eh,es in ladder0:
                    if eh<tau and es<tau and (best is None or nb<best[1]): best=(ar,nb)
                if best:
                    blob0,_=v02.encode_prepared(prep,alpha=float(best[0]*ptp),beta=2.0,zlib_level=6); rec,_,_=v02.decode_blob(blob0)
                    add("A0",tau,f"alpha_rel={best[0]:.6g}",len(blob0),rec,0.0)
                # A1 v0.2 continuous alpha
                ts=time.time(); a=bisect_scale(lambda s:S.ok(s*q2,tau),1e-14*ptp,1e3*ptp)
                if a:
                    for _ in range(40):
                        blob1,_=v02.encode_prepared(prep,alpha=a,beta=2.0,zlib_level=6); rec,_,_=v02.decode_blob(blob1)
                        if add("A1",tau,f"alpha_rel={a/ptp:.9g}",len(blob1),rec,time.time()-ts): break
                        rows.pop(); a*=0.99
                # A2 T1 continuous alpha per q_c = k/32
                ts=time.time(); cand=[]
                for k in range(1,33):
                    qc=k/32; keep=prep.topology.q<=qc
                    a=bisect_scale(lambda s:S.ok(np.full(q2.shape,s),tau,keep),1e-14*ptp,1e3*ptp)
                    if a: cand.append((len(t1.encode(prep,alpha=a,q_cut=qc)),qc,a))
                for nb,qc,a in sorted(cand)[:3]:
                    for _ in range(40):
                        b2=t1.encode(prep,alpha=a,q_cut=qc); rec=t1.decode(b2)
                        if add("A2",tau,f"q_cut={qc:.6g};alpha_rel={a/ptp:.9g}",len(b2),rec,time.time()-ts): break
                        rows.pop(); a*=0.99
                # A3/A4/A5 RDO
                for arm,an,pol,tan in (("A3",anO,True,tO),("A4",anF,True,tF),("A5",anB,False,tB)):
                    ts=time.time(); mg=MARGIN
                    for _ in range(20):
                        try: ch=v3.select(an,tau,margin=mg,polish=pol)
                        except RuntimeError as exc: fails.append(base|{"arm":arm,"tau":tau,"error":str(exc)}); break
                        b3=v3.encode(an,ch); rec=v3.decode(b3)
                        if add(arm,tau,f"margin={mg:.4f}",len(b3),rec,tan+time.time()-ts): break
                        rows.pop(); mg*=0.995
                # A6 pointwise codecs with tolerance bisection
                for codec in ("zfp","sz3","sperr"):
                    ts=time.time(); seen={}
                    def okc(t):
                        rec,nb,_=core.codec_roundtrip(codec,x,float(t),work); rec=np.asarray(rec,float)
                        eh,es=v02.hartree_error_metrics(rec-x,lat,rh,rs); good=eh<tau and es<tau
                        if good: seen[t]=(nb,rec)
                        return good
                    try:
                        bisect_scale(okc,1e-14*ptp,1.0*ptp)
                        if seen:
                            t=max(seen,key=lambda k:raw/seen[k][0]); add("A6",tau,f"codec={codec};abs_tol_rel={t/ptp:.9g}",seen[t][0],seen[t][1],time.time()-ts)
                    except Exception as exc: fails.append(base|{"arm":"A6","tau":tau,"error":f"{codec}: {type(exc).__name__}: {exc}"[:300]})
    except Exception as exc:
        fails.append({"material_id":mid,"arm":"material","error":traceback.format_exc()[-800:]})
    return mid,rows,fails,time.time()-t0

def main():
    a=args(); out=a.output_dir; out.mkdir(parents=True,exist_ok=True); a.cache_dir.mkdir(parents=True,exist_ok=True)
    man=list(csv.DictReader(open(a.repo_root/"analysis/operator_aware_codec_hartree/results/PILOT_MANIFEST.csv",encoding="utf-8")))
    if a.only: man=[m for m in man if m["material_id"] in a.only.split(",")]
    jobs=[(m,str(a.repo_root.resolve()),str(a.frozen_root.resolve()),str(a.cache_dir.resolve())) for m in man]
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for mid,rows,fails,secs in ex.map(material,jobs):
            for name,data in (("rows",rows),("failures",fails)):
                if data:
                    p=out/f"{name}_{mid}.csv"; f=list(dict.fromkeys(k for r in data for k in r))
                    with p.open("w",newline="",encoding="utf-8") as fh: w=csv.DictWriter(fh,fieldnames=f); w.writeheader(); w.writerows(data)
            print(f"V03_DONE {mid} rows={len(rows)} failures={len(fails)} seconds={secs:.0f}",flush=True)

if __name__=="__main__": raise SystemExit(main())
