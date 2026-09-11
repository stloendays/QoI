#!/usr/bin/env python3
"""Engineering-only retry of the 144 preclassified failed P4 compressed cells.

Scientific settings are unchanged. The only permitted changes are creating the
per-condition directory required by frozen SPERR and the per-condition work
folder required by the validated Henkelman adapter. Successful first-run cells
are not executed here.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, sys, tempfile, time
from collections import defaultdict
from pathlib import Path
from typing import Any
import numpy as np

HERE=Path(__file__).resolve().parent
if str(HERE) not in sys.path: sys.path.insert(0,str(HERE))
from development_compatibility_smoke import build_grid, fetch_exact, load_metadata


def read_csv(p:Path):
    with p.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))

def write_csv(p:Path,rows:list[dict[str,Any]],fallback:list[str]):
    fields=[]
    for r in rows:
        for k in r:
            if k not in fields: fields.append(k)
    if not fields: fields=fallback
    with p.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)

def shard_for(material:str,n:int)->int:
    return int.from_bytes(hashlib.sha256(('P4-RETRY|'+material).encode()).digest()[:8],'big')%n

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--repo-root',type=Path,required=True);ap.add_argument('--frozen-validation-dir',type=Path,required=True);ap.add_argument('--classified-failures',type=Path,required=True);ap.add_argument('--henkelman-binary',type=Path,required=True);ap.add_argument('--shard-count',type=int,required=True);ap.add_argument('--shard-index',type=int,required=True);ap.add_argument('--output-dir',type=Path,required=True);a=ap.parse_args()
    root=a.repo_root.resolve();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    failed=read_csv(a.classified_failures)
    if len(failed)!=144 or any(r.get('failure_family') not in {'SPERR_WORKDIR_NOT_CREATED','HENKELMAN_WORKDIR_NOT_CREATED'} for r in failed):raise RuntimeError('retry input is not the frozen 144-key taxonomy')
    bymat=defaultdict(list)
    for r in failed:bymat[r['material_id']].append(r)
    selected={m:rr for m,rr in bymat.items() if shard_for(m,a.shard_count)==a.shard_index}
    metadata=load_metadata(root)
    sys.path.insert(0,str(a.frozen_validation_dir.resolve()));import external_end_to_end as core  # type: ignore
    mech=root/'mechanism/independent_bader_20260908';sys.path.insert(0,str(mech));import run_study as study  # type: ignore
    study.BADER=a.henkelman_binary.resolve()
    rows=[];failures=[]
    for m,keys in sorted(selected.items()):
        meta=metadata.get(m)
        if meta is None:
            for k in keys: failures.append({**k,'status':'FAILED_RETRY','stage':'metadata_retry','error':'metadata missing'})
            continue
        try:
            blob=fetch_exact(meta['url'],meta['sha256'],int(meta['source_bytes']))
            with tempfile.TemporaryDirectory(prefix='qoi_p4_retry_') as td:
                work=Path(td);grid,loader=build_grid(meta,blob,work);field=np.ascontiguousarray(np.asarray(grid.total,dtype=np.float64));ptp=float(np.ptp(field));lattice=np.asarray(grid.structure.lattice.matrix,dtype=np.float64);frac=np.asarray(grid.structure.frac_coords,dtype=np.float64);species=[str(s.specie.symbol) for s in grid.structure]
                grouped=defaultdict(list)
                for k in keys: grouped[(k['codec'],float(k['relative_tolerance']))].append(k)
                for (codec_label,rel),cell_keys in sorted(grouped.items()):
                    codec={'ZFP':'zfp','SZ3':'sz3','SPERR':'sperr'}[codec_label];abs_bound=rel*ptp;condition=f'{codec_label}_{rel:.0e}';codec_work=work/condition;codec_work.mkdir(parents=True,exist_ok=True)
                    try:
                        t0=time.time();recon,compressed_bytes,config=core.codec_roundtrip(codec,field,abs_bound,codec_work);enc=time.time()-t0;recon=np.ascontiguousarray(np.asarray(recon,dtype=np.float64));linf=float(np.max(np.abs(recon-field)));bound_ok=bool(linf<=abs_bound*(1+1e-6)+1e-15);recon_hash=hashlib.sha256(recon.tobytes(order='C')).hexdigest();recon_grid=core.clone_grid_with_total(grid,recon)
                    except Exception as exc:
                        for k in cell_keys:failures.append({**k,'status':'FAILED_RETRY','stage':'codec_retry','error':f'{type(exc).__name__}: {exc}'})
                        continue
                    for k in cell_keys:
                        solver=k['solver'];base={"material_id":m,"codec":codec_label,"relative_tolerance":rel,"absolute_bound":abs_bound,"solver":solver,"status":"SUCCESS","species_json":json.dumps(species,separators=(',',':')),"realized_Linf":linf,"bound_respected":bound_ok,"compressed_bytes":int(compressed_bytes),"codec_config":config,"encode_seconds":enc,"source_sha256":meta['sha256'],"reconstructed_field_sha256":recon_hash,"loader":loader,"npoints":field.size,"natoms":len(species),"retry_failure_family":k['failure_family']}
                        if solver=='baderkit_ongrid':
                            t0=time.time()
                            try:
                                b=core.run_bader(recon_grid);q=np.asarray(b['charges'],dtype=float)
                                if q.size!=len(species):raise RuntimeError('BaderKit charge count mismatch')
                                rows.append({**base,'charges_json':json.dumps(q.tolist(),separators=(',',':')),'solver_seconds':time.time()-t0})
                            except Exception as exc:failures.append({**k,'status':'FAILED_RETRY','stage':'baderkit_retry','error':f'{type(exc).__name__}: {exc}'})
                        elif solver=='henkelman_ongrid':
                            solver_work=work/'henkelman'/condition;solver_work.mkdir(parents=True,exist_ok=True);logdir=work/'logs'/condition;logdir.mkdir(parents=True,exist_ok=True);t0=time.time()
                            try:
                                q,_,extra=study.solve('henkelman_ongrid',recon,lattice,frac,species,solver_work,logdir);q=np.asarray(q,dtype=float)
                                if q.size!=len(species):raise RuntimeError('Henkelman charge count mismatch')
                                rows.append({**base,'charges_json':json.dumps(q.tolist(),separators=(',',':')),'solver_seconds':time.time()-t0,'vacuum_charge_e':extra.get('vacuum_charge_e','')})
                            except Exception as exc:failures.append({**k,'status':'FAILED_RETRY','stage':'henkelman_retry','error':f'{type(exc).__name__}: {exc}'})
                        else:raise RuntimeError(f'unexpected retry solver {solver}')
        except Exception as exc:
            got={(r['material_id'],r['codec'],str(r['relative_tolerance']),r['solver']) for r in rows+failures}
            for k in keys:
                kk=(m,k['codec'],str(float(k['relative_tolerance'])),k['solver'])
                if kk not in got:failures.append({**k,'status':'FAILED_RETRY','stage':'source_retry','error':f'{type(exc).__name__}: {exc}'})
    planned=sum(len(x) for x in selected.values())
    if len(rows)+len(failures)!=planned:raise RuntimeError(f'retry accounting {len(rows)+len(failures)} != {planned}')
    rows.sort(key=lambda r:(r['material_id'],r['codec'],float(r['relative_tolerance']),r['solver']));failures.sort(key=lambda r:(r['material_id'],r['codec'],float(r['relative_tolerance']),r['solver']))
    write_csv(out/f'retry_rows_shard_{a.shard_index:02d}.csv',rows,['material_id','codec','relative_tolerance','solver','status']);write_csv(out/f'retry_failures_shard_{a.shard_index:02d}.csv',failures,['material_id','codec','relative_tolerance','solver','status','stage','error'])
    manifest={'shard_index':a.shard_index,'shard_count':a.shard_count,'planned_failed_keys':planned,'successful_retry_rows':len(rows),'failed_retry_rows':len(failures),'scientific_definition_changed':False}
    (out/f'manifest_shard_{a.shard_index:02d}.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8');print(json.dumps(manifest,indent=2));return 0 if not failures else 2
if __name__=='__main__':raise SystemExit(main())
