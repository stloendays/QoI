#!/usr/bin/env python3
"""Part B of the General-QOAC law confirmation: predictions (PHASE=predict) or opt/blind compression (PHASE=run).

See DESIGN.md. Predictions use only the reference spectrum and must be committed before any compression run.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,sys,tempfile,time,traceback
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE)); sys.path.insert(0,str(HERE.parent/"general_qoac_operators"))
import policy_codec as pc
import operators as ops
import gain_predictors as gp
import run_calibration as cal
v02=pc.v02

TAUS=(1e-6,1e-4)
SIGMA=0.5
OPERATORS=(("density",{}, {"kind":"flat"}),
           ("density_gradient",{}, {"kind":"power_q","p":-1.0}),
           ("density_laplacian",{}, {"kind":"power_q","p":-2.0}),
           ("hartree_field",{}, {"kind":"power_q","p":1.0}),
           ("hartree_potential",{}, {"kind":"power_q","p":2.0}),
           ("gaussian_smoothed_density",{"sigma_angstrom":SIGMA}, {"kind":"gaussian","sigma_angstrom":SIGMA}))

def load(meta,cache,dev):
    cp=Path(cache)/f"{meta['material_id']}.src"
    if cp.exists() and hashlib.sha256(cp.read_bytes()).hexdigest()==meta["sha256"]: blob=cp.read_bytes()
    else:
        blob=dev.fetch_exact(meta["url"],meta["sha256"],int(meta["source_bytes"])); cp.write_bytes(blob)
    with tempfile.TemporaryDirectory(prefix="lawB_") as td:
        grid,_=dev.build_grid(meta,blob,Path(td))
        x=np.ascontiguousarray(np.asarray(grid.total,dtype=np.float64)); lat=np.asarray(grid.structure.lattice.matrix,float)
    if x.size!=int(meta["npoints"]): raise RuntimeError("npoints mismatch")
    return x,lat

def predict(meta,x,lat):
    shape=tuple(int(v) for v in x.shape)
    topo=v02.build_topology(shape,lat,shell_count=32)
    counts=np.bincount(topo.shell_ids.astype(np.int64),minlength=32)
    model=gp.spectrum_model(x,lat,topology=topo)
    F=cal.fixed_bytes_v02(shape,lat,counts)
    rows=[]
    for name,params,_ in OPERATORS:
        op=ops.get_operator(name,**params); lw=gp.log_weight(op,model)
        ua,ub=gp.operator_optimal(op)(model),gp.blind()(model)
        a_ratio=math.exp(gp.highrate_log_rmse_ratio(model,lw,ua,ub))
        for tau in TAUS:
            g=gp.finite_rate_gain(model,lw,ua,ub,tau)
            ra,rb=g.get("rate_bits_a",float("nan")),g.get("rate_bits_b",float("nan"))
            rows.append({"material_id":meta["material_id"],"operator":op.label,"tau":tau,"reachable":g["reachable"],
                         "R_opt_bits":ra,"R_blind_bits":rb,"F_bytes":F,"G_pred":(F+rb/8)/(F+ra/8) if g["reachable"] else float("nan"),
                         "a_matched_rate_rmse_ratio":a_ratio})
    return rows

def compress(meta,x,lat):
    prep=v02.prepare_field(x,lat,shell_count=32); spec=pc.OrbitSpectrum(prep); ptp=float(np.ptp(x)); raw=x.nbytes
    c0=complex(prep.spectrum.ravel()[0])
    rows=[]
    for name,params,optpol in OPERATORS:
        op=ops.get_operator(name,**params); refs=ops.reference_energies(x,lat,op)
        mw,ref_orb=spec.weight_cache(op.weight)
        w0=0.0 if op.singular_at_zero else float(op.weight(np.zeros(1))[0])
        ref_full=ref_orb+w0*abs(c0)**2           # same denominator as the library's safe metric (G = 0 is never Nyquist)
        for tau in TAUS:
            for arm,pol in (("opt",optpol),("blind",{"kind":"flat"})):
                t0=time.time(); u=pc.policy_shape(prep.topology,pol)
                a=pc.bisect_alpha(spec,u,mw,ref_full,tau,ptp)
                row={"material_id":meta["material_id"],"operator":op.label,"tau":tau,"arm":arm,"policy":json.dumps(pol)}
                if a is None:
                    rows.append(row|{"certified":False,"error":"unreachable"}); continue
                for _ in range(40):
                    blob=pc.encode(prep,a,pol); y=pc.decode(blob)
                    rel=ops.relative_error(y-x,lat,op,{"safe":refs["safe"]})["safe"]
                    if rel<tau: break
                    a*=0.99
                pred=spec.rel_error_safe(a*u,mw,ref_full)
                rows.append(row|{"alpha_rel":a/ptp,"bytes":len(blob),"cr":raw/len(blob),"rel_safe_decoded":rel,
                                 "rel_safe_orbit":pred,"certified":bool(rel<tau),"seconds":time.time()-t0})
    return rows

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--phase",choices=["predict","run"],required=True)
    p.add_argument("--repo-root",type=Path,required=True); p.add_argument("--frozen-root",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True); p.add_argument("--cache-dir",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True); p.add_argument("--only",default="")
    a=p.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True); a.cache_dir.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(a.frozen_root.resolve()/"validation")); sys.path.insert(0,str(a.repo_root.resolve()/"validation"/"qsq_prospective"))
    import development_compatibility_smoke as dev
    man=list(csv.DictReader(open(a.manifest,encoding="utf-8")))
    if a.only: man=[m for m in man if m["material_id"] in a.only.split(",")]
    for meta in man:
        mid=meta["material_id"]; t0=time.time()
        try:
            x,lat=load(meta,a.cache_dir,dev)
            rows=predict(meta,x,lat) if a.phase=="predict" else compress(meta,x,lat)
            fn=f"{'pred' if a.phase=='predict' else 'partb'}_{mid}.csv"
            f=list(dict.fromkeys(k for r in rows for k in r))
            with (a.output_dir/fn).open("w",newline="",encoding="utf-8") as fh:
                w=csv.DictWriter(fh,fieldnames=f); w.writeheader(); w.writerows(rows)
            status="SUCCESS"
        except Exception:
            (a.output_dir/f"failure_{a.phase}_{mid}.txt").write_text(traceback.format_exc()[-2000:],encoding="utf-8"); status="FAILED"
        print(f"PARTB_{a.phase.upper()} {mid} {status} seconds={time.time()-t0:.0f}",flush=True)

if __name__=="__main__": raise SystemExit(main())
