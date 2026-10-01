#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, time
from pathlib import Path
import numpy as np
from givernylocal.turbulence_dataset import turb_dataset
from givernylocal.turbulence_toolkit import getData

HERE=Path(__file__).resolve().parent
TOKEN="edu.jhu.pha.turbulence.testing-201406"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

rows=list(csv.DictReader((HERE/"sample_manifest.csv").open()))
out=HERE/"data"; out.mkdir(exist_ok=True)
ds=turb_dataset(dataset_title="isotropic1024coarse",output_path=str(HERE/"giverny_output"),auth_token=TOKEN)
status=[]
for j,row in enumerate(rows):
    sid=row["sample_id"]; dst=out/f"{sid}.npy"
    if dst.exists():
        status.append({"sample_id":sid,"status":"EXISTS","sha256":sha(dst),"bytes":dst.stat().st_size}); continue
    side=int(row["side"]); dx=float(row["dx"])
    axes=[np.arange(int(row[k]),int(row[k])+side,dtype=float)*dx for k in ("x0_index","y0_index","z0_index")]
    X,Y,Z=np.meshgrid(*axes,indexing="ij")
    pts=np.column_stack((X.ravel(),Y.ravel(),Z.ravel()))
    last=""
    for attempt in range(1,4):
        try:
            raw=getData(ds,"velocity",float(row["time"]),"none","none","field",pts)
            arr=np.asarray(raw,dtype=np.float32).squeeze().reshape(side,side,side,3)
            if not np.isfinite(arr).all(): raise ValueError("non-finite velocity")
            np.save(dst,arr,allow_pickle=False)
            status.append({"sample_id":sid,"status":"OK","sha256":sha(dst),"bytes":dst.stat().st_size})
            print(f"{j+1}/64 {sid} ok",flush=True); break
        except Exception as exc:
            last=f"{type(exc).__name__}: {exc}"
            print(f"{sid} attempt {attempt}: {last}",flush=True)
            time.sleep(5*attempt)
    else:
        status.append({"sample_id":sid,"status":"FAILED","sha256":"","bytes":0,"error":last})
    time.sleep(1)
fields=sorted({k for r in status for k in r})
with (HERE/"fetch_status.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(status)
