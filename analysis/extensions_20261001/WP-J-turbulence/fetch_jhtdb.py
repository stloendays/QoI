#!/usr/bin/env python3
"""Fetch the frozen JHTDB 15^3 velocity cutouts sequentially with givernylocal."""
from __future__ import annotations
import argparse, csv, hashlib, json, time
from pathlib import Path
import numpy as np
from givernylocal.turbulence_dataset import turb_dataset
from givernylocal.turbulence_toolkit import getData

HERE=Path(__file__).resolve().parent
DEFAULT_TOKEN="edu.jhu.pha.turbulence.testing-201406"

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--token",default=DEFAULT_TOKEN)
    ap.add_argument("--start",type=int,default=0)
    ap.add_argument("--stop",type=int,default=64)
    ap.add_argument("--sleep",type=float,default=1.0)
    a=ap.parse_args()
    rows=list(csv.DictReader((HERE/"sample_manifest.csv").open()))
    out=HERE/"data"; out.mkdir(exist_ok=True)
    meta=[]
    dataset=turb_dataset(dataset_title="isotropic1024coarse",output_path=str(HERE/"giverny_output"),auth_token=a.token)
    for j,row in enumerate(rows[a.start:a.stop], start=a.start):
        sid=row["sample_id"]; dst=out/f"{sid}.npy"
        if dst.exists():
            meta.append({"sample_id":sid,"status":"EXISTS","sha256":sha256(dst),"bytes":dst.stat().st_size})
            continue
        side=int(row["side"]); dx=float(row["dx"])
        ix=np.arange(int(row["x0_index"]),int(row["x0_index"])+side,dtype=np.float64)*dx
        iy=np.arange(int(row["y0_index"]),int(row["y0_index"])+side,dtype=np.float64)*dx
        iz=np.arange(int(row["z0_index"]),int(row["z0_index"])+side,dtype=np.float64)*dx
        X,Y,Z=np.meshgrid(ix,iy,iz,indexing="ij")
        points=np.column_stack((X.ravel(),Y.ravel(),Z.ravel()))
        if len(points)>=4096:
            raise RuntimeError("public-token query exceeds frozen <4096-point limit")
        err=None
        for attempt in range(1,4):
            try:
                raw=getData(dataset,"velocity",float(row["time"]),"none","none","field",points)
                arr=np.asarray(raw,dtype=np.float32)
                arr=np.squeeze(arr)
                if arr.shape!=(side**3,3):
                    arr=arr.reshape(side**3,3)
                arr=arr.reshape(side,side,side,3)
                if not np.isfinite(arr).all():
                    raise ValueError("non-finite velocity returned")
                np.save(dst,arr,allow_pickle=False)
                meta.append({"sample_id":sid,"status":"OK","sha256":sha256(dst),"bytes":dst.stat().st_size})
                print(f"{j+1}/{min(a.stop,len(rows))} {sid} ok",flush=True)
                break
            except Exception as exc:
                err=f"{type(exc).__name__}: {exc}"
                print(f"{sid} attempt {attempt} failed: {err}",flush=True)
                if attempt<3: time.sleep(5*attempt)
        else:
            meta.append({"sample_id":sid,"status":"FAILED","sha256":"","bytes":0,"error":err})
        time.sleep(a.sleep)
    fields=sorted({k for r in meta for k in r})
    with (HERE/"fetch_status.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(meta)
    print(json.dumps({"attempted":len(meta),"ok":sum(r["status"] in ("OK","EXISTS") for r in meta)}))

if __name__=="__main__":
    main()
