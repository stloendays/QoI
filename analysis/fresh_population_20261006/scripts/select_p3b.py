#!/usr/bin/env python3
"""Draw the P3b fresh slab cohort under P3B_SELECTION_RULE.md (metadata only; no QoI outcome is computed)."""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,os,sys,tempfile,time,urllib.request
from pathlib import Path
import numpy as np
import pandas as pd

TAG="QOAC-FRESH-SLAB-20261006|"
API="https://nomad-lab.eu/prod/v1/api/v1"
UPLOAD_CAP=6

def h(s): return hashlib.sha256((TAG+s).encode()).hexdigest()

def fetch(url):
    err=None
    for k in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"QoI-P3b/1.0"}),timeout=900) as r: return r.read()
        except Exception as e: err=e; time.sleep(5*(k+1))
    raise RuntimeError(f"download failed: {err}")

def main():
    p=argparse.ArgumentParser(); p.add_argument("--repo-root",type=Path,required=True); a=p.parse_args()
    repo=a.repo_root.resolve(); F=repo/"analysis/fresh_population_20261006"
    sys.path.insert(0,str(repo/"validation/qsq_prospective"))
    import development_compatibility_smoke as dev
    from pymatgen.core import Composition
    frame=pd.read_csv(F/"nomad_frame_surface_vasp.csv.gz")
    feas=json.load(open(F/"p3_feasibility.json")); bad_uploads=set(feas["excluded_uploads"])
    ex_ids=set(pd.read_csv(F/"exclusion_ids.csv").id.astype(str))
    ex_f=set(pd.read_csv(F/"exclusion_formulas.csv").reduced_formula.astype(str))
    for m in ("P1_ENGINEERING","P1_CONFIRMATORY","P2_ENGINEERING","P2_CONFIRMATORY"):
        ex_f|=set(Composition(f).reduced_formula for f in pd.read_csv(F/f"{m}_MANIFEST.csv").formula)
    fr=frame[(frame.chgcar_bytes>=1e6)&(frame.chgcar_bytes<=80e6)&(~frame.upload_id.isin(bad_uploads))]
    fr=fr[~fr.entry_id.isin(ex_ids)&~("nomad-"+fr.entry_id.str[:12]).isin(ex_ids)]
    fr=fr[~fr.reduced_formula.isin(ex_f)]
    formulas=sorted(fr.reduced_formula.unique(),key=h)
    attempts=[]; accepted=[]; per_upload={}
    for f in formulas:
        rows=sorted(fr[fr.reduced_formula==f].to_dict("records"),key=lambda r:h(r["entry_id"]))
        for r in rows:
            rec={"reduced_formula":f,"entry_id":r["entry_id"],"upload_id":r["upload_id"],"chgcar_bytes":int(r["chgcar_bytes"])}
            if per_upload.get(r["upload_id"],0)>=UPLOAD_CAP: attempts.append(rec|{"decision":"reject","reason":"upload_cap"}); continue
            url=f"{API}/entries/{r['entry_id']}/raw/{os.path.basename(r['chgcar_path'])}"
            try:
                blob=fetch(url); sha=hashlib.sha256(blob).hexdigest(); nbytes=len(blob)
                meta={"source":"NOMAD surfaces/adsorbates","url":url}
                with tempfile.TemporaryDirectory(prefix="p3b_") as td:
                    grid,_=dev.build_grid(meta,blob,Path(td))
                    x=np.asarray(grid.total,dtype=np.float64); st=grid.structure
                    shape=x.shape; n=int(x.size); ok=bool(np.all(np.isfinite(x)) and float(x.sum())>0)
                    form=st.composition.reduced_formula; nat=len(st)
                del blob
                if not ok: attempts.append(rec|{"decision":"reject","reason":"invalid_density"}); continue
                if not (1.5e5<=n<=6.0e6): attempts.append(rec|{"decision":"reject","reason":"npoints_out_of_range","npoints":n}); continue
                if form in ex_f: attempts.append(rec|{"decision":"reject","reason":"excluded_parsed_formula"}); continue
                mid="nomad-"+r["entry_id"][:12]
                accepted.append({"material_id":mid,"task_id":r["entry_id"],"corpus":"fresh_p3b_slab","system_type":"slab",
                    "source":"NOMAD surfaces/adsorbates","formula":form,"ngrid":"x".join(map(str,shape)),"sha256":sha,"url":url,
                    "source_bytes":nbytes,"npoints":n,"natoms":nat,
                    "selection_stratum":f"formula:{f}","selection_hash":h(r["entry_id"])})
                attempts.append(rec|{"decision":"accept","npoints":n,"sha256":sha})
                per_upload[r["upload_id"]]=per_upload.get(r["upload_id"],0)+1
                break
            except Exception as e:
                attempts.append(rec|{"decision":"reject","reason":f"error:{type(e).__name__}:{str(e)[:200]}"})
    pd.DataFrame(attempts).to_csv(F/"p3b_attempts.csv",index=False)
    pd.DataFrame(accepted).to_csv(F/"P3B_CONFIRMATORY_MANIFEST.csv",index=False)
    print(json.dumps({"formulas_in_frame":len(formulas),"accepted":len(accepted),"attempts":len(attempts)}))

if __name__=="__main__": raise SystemExit(main())
