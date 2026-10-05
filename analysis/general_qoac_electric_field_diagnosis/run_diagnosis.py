#!/usr/bin/env python3
"""Finite-rate diagnosis of the General-QOAC electric-field codec (diagnosis only; see DESIGN.md)."""
from __future__ import annotations
import argparse,csv,hashlib,json,math,sys,tempfile,time,zlib
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
ALPHA_REL=np.logspace(-7.0,1.0,25)
BETAS=(0.0,1.0,1.25,2.0)
THEORY_BETAS=tuple(np.round(np.arange(0,2.0001,0.25),2))
SHELL_COUNT=32; FINE_BINS=128; ZLIB_LEVEL=6

def parse_args():
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,required=True)
    p.add_argument("--cache-dir",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--only",default="")
    return p.parse_args()

def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    fields=[]
    for r in rows:
        for k in r:
            if k not in fields: fields.append(k)
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def load_blob(dev,meta,cache):
    path=cache/f"{meta['material_id']}.src"
    if path.exists():
        blob=path.read_bytes()
        if hashlib.sha256(blob).hexdigest()==meta["sha256"]: return blob
    blob=dev.fetch_exact(meta["url"],meta["sha256"],int(meta["source_bytes"]))
    path.write_bytes(blob); return blob

def h0_bits(values,groups,ngroups):
    """Zeroth-order entropy (bits) of integer symbols, pooled per group."""
    out=np.zeros(ngroups)
    order=np.lexsort((values,groups))
    g=groups[order]; v=values[order]
    brk=np.flatnonzero((np.diff(g)!=0)|(np.diff(v)!=0))+1
    starts=np.r_[0,brk]; counts=np.diff(np.r_[starts,v.size]); gs=g[starts]
    tot=np.bincount(gs,weights=counts,minlength=ngroups)
    p=counts/tot[gs]
    np.add.at(out,gs,-counts*np.log2(p))
    return out

def theory_rows(mid,topo,safe,m,n):
    q=topo.q; lq=np.log(q); mean_lq=float(np.sum(n*lq)/np.sum(n))
    rows=[]
    for name,wexp in (("electric_field",-2.0),("hartree",-4.0)):
        logD={}
        for b in THEORY_BETAS:
            s=float(np.sum((m*n*np.power(q,2*b+wexp))[safe]))
            logD[b]=-2*b*mean_lq+math.log(s)
        for b in THEORY_BETAS:
            rows.append({"material_id":mid,"operator":name,"beta":b,
                         "pred_rmse_ratio_vs_beta1":math.exp(0.5*(logD[b]-logD[1.0])),
                         "pred_rmse_ratio_vs_beta0":math.exp(0.5*(logD[b]-logD[0.0])),
                         "pred_rmse_ratio_vs_beta2":math.exp(0.5*(logD[b]-logD[2.0]))})
    return rows

def main():
    a=parse_args(); repo=a.repo_root.resolve(); out=a.output_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
    a.cache_dir.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(repo/"analysis"/"operator_aware_codec_hartree_v02"))
    sys.path.insert(0,str(repo/"validation"/"qsq_prospective"))
    import codec_qoac_h_v02 as qoac
    import development_compatibility_smoke as dev
    frozen={}
    for r in csv.DictReader(open(repo/"analysis/general_qoac_electric_field_beta_map/results/beta_map_rows.csv",encoding="utf-8")):
        frozen[(r["material_id"],round(float(r["beta"]),4),round(math.log10(float(r["alpha_rel_ptp"])),6))]=r
    manifest=list(csv.DictReader(open(repo/"analysis/operator_aware_codec_hartree/results/PILOT_MANIFEST.csv",encoding="utf-8")))
    if a.only: manifest=[r for r in manifest if r["material_id"] in a.only.split(",")]
    for meta in manifest:
        mid=meta["material_id"]; t0=time.perf_counter()
        if (out/f"settings_{mid}.csv").exists(): print("SKIP",mid,flush=True); continue
        blob=load_blob(dev,meta,a.cache_dir)
        with tempfile.TemporaryDirectory(prefix="efdiag_") as td:
            grid,_=dev.build_grid(meta,blob,Path(td))
            field=np.ascontiguousarray(np.asarray(grid.total,dtype=np.float64))
            lattice=np.asarray(grid.structure.lattice.matrix,dtype=np.float64)
        ptp=float(np.ptp(field))
        prep=qoac.prepare_field(field,lattice,shell_count=SHELL_COUNT); topo=prep.topology
        shape=topo.shape; yz=shape[1]*shape[2]
        ri=topo.rep_flat//yz; rj=(topo.rep_flat%yz)//shape[2]; rk=topo.rep_flat%shape[2]
        nyq=np.zeros(ri.size,bool)
        for idx,nn in ((ri,shape[0]),(rj,shape[1]),(rk,shape[2])):
            if nn%2==0: nyq|=idx==nn//2
        safe=~nyq
        selfc=topo.self_conjugate; m=np.where(selfc,1.0,2.0); n=m.copy()
        w=1.0/topo.g2_safe_rep
        coeff=prep.spectrum.ravel()[topo.rep_flat]; cr=coeff.real; ci=np.where(selfc,0.0,coeff.imag)
        ref=float(np.sum((m*w*(cr*cr+ci*ci))[safe]))
        shell=topo.shell_ids.astype(np.int64); fine=np.clip(np.floor(topo.q*FINE_BINS).astype(np.int64),0,FINE_BINS-1)
        nshell=np.bincount(shell,minlength=SHELL_COUNT)
        ref_shell=np.bincount(shell[safe],weights=(m*w*(cr*cr+ci*ci))[safe],minlength=SHELL_COUNT)
        qmid=np.bincount(shell,weights=topo.q,minlength=SHELL_COUNT)/np.maximum(nshell,1)
        write_csv(out/f"theory_{mid}.csv",theory_rows(mid,topo,safe,m,n))
        settings=[]; shells=[]
        for beta in BETAS:
            for arel in ALPHA_REL:
                alpha=float(arel*ptp)
                stream,enc=qoac.encode_prepared(prep,alpha=alpha,beta=beta,zlib_level=ZLIB_LEVEL)
                header,_,_=qoac._parse_blob(stream)
                zb=np.array([rec["compressed_bytes"] for rec in header["shells"]],float)
                steps=qoac.quantization_steps(topo,alpha=alpha,beta=beta)
                qr=np.rint(cr/steps); qi=np.rint(ci/steps); qi[selfc]=0
                er=cr-qr*steps; ei=ci-qi*steps
                e_orb=m*w*(er*er+ei*ei)*safe
                zero=(qr==0)&(qi==0)
                hr=m*n*w*steps*steps/12.0*safe
                err_shell=np.bincount(shell,weights=e_orb,minlength=SHELL_COUNT)
                err_zero=np.bincount(shell,weights=e_orb*zero,minlength=SHELL_COUNT)
                hr_shell=np.bincount(shell,weights=hr,minlength=SHELL_COUNT)
                zfrac=np.bincount(shell,weights=zero.astype(float),minlength=SHELL_COUNT)/np.maximum(nshell,1)
                sym=np.concatenate([qr,qi]).astype(np.int64)
                h32=h0_bits(sym,np.concatenate([shell,shell]),SHELL_COUNT)
                h128=float(np.sum(h0_bits(sym,np.concatenate([fine,fine]),FINE_BINS)))
                es=math.sqrt(float(err_shell.sum())/ref)
                fr=frozen.get((mid,round(beta,4),round(math.log10(arel),6)))
                fixed=len(stream)-int(zb.sum())
                settings.append({"material_id":mid,"system_type":meta["system_type"],"beta":beta,"alpha_rel_ptp":float(arel),
                    "encoded_bytes":len(stream),"raw_bytes":field.nbytes,"fixed_bytes":fixed,
                    "rate_zlib_bytes":len(stream),"rate_h0_32_bytes":fixed+float(h32.sum())/8.0,"rate_h0_128_bytes":fixed+h128/8.0,
                    "ef_rel_rmse_safe":es,"ef_rel_rmse_safe_zero_part":math.sqrt(float(err_zero.sum())/ref),
                    "ef_rel_rmse_safe_highrate_pred":math.sqrt(float(hr_shell.sum())/ref),
                    "dead_zone_fraction":float(zero.mean()),
                    "frozen_encoded_bytes":int(fr["encoded_bytes"]) if fr else "",
                    "frozen_ef_rel_rmse_safe":float(fr["electric_field_error_rel_RMSE_safe"]) if fr else "",
                    "closure_rel":abs(es/float(fr["electric_field_error_rel_RMSE_safe"])-1) if fr else ""})
                for s in range(SHELL_COUNT):
                    shells.append({"material_id":mid,"beta":beta,"alpha_rel_ptp":float(arel),"shell":s,"q_mid":float(qmid[s]),
                        "orbits":int(nshell[s]),"ref_weighted_share":float(ref_shell[s]/ref),
                        "err_weighted":float(err_shell[s]/ref),"err_zero_weighted":float(err_zero[s]/ref),
                        "highrate_pred_weighted":float(hr_shell[s]/ref),"dead_zone_fraction":float(zfrac[s]),
                        "zlib_bytes":float(zb[s]),"h0_bytes":float(h32[s])/8.0})
        write_csv(out/f"shells_{mid}.csv",shells); write_csv(out/f"settings_{mid}.csv",settings)
        print(f"EFDIAG_DONE {mid} seconds={time.perf_counter()-t0:.1f} max_closure={max(float(s['closure_rel']) for s in settings if s['closure_rel']!=''):.2e}",flush=True)
    return 0

if __name__=="__main__": raise SystemExit(main())
