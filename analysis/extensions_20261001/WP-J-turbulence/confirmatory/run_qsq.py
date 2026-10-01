#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, sys
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent
sys.path.insert(0,str(PARENT))
import run_qsq_turbulence as core

QUAL=(20260905,1,2,3,4)
FRESH=tuple(range(10000,10059))

def seed64(sample_id,label):
    return int.from_bytes(hashlib.sha256(f"QSQ-JHTDB|{sample_id}|velocity|{label}".encode()).digest()[:8],"little")

def write(path,rows):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

manifest=list(csv.DictReader((HERE/"sample_manifest.csv").open()))
refs=[]; qual=[]; fresh=[]; failures=[]
for row in manifest:
    sid=row["sample_id"]
    try:
        u=np.asarray(np.load(HERE/"data"/f"{sid}.npy"),dtype=np.float64)
        dx=float(row["dx"])
        _,q0,e0=core.fields(u,dx)
        theta=float(np.quantile(q0,0.90,method="linear")); mask0=q0>theta
        eps=float(np.max(np.abs(u.astype(np.float16).astype(np.float64)-u)))
        refs.append({"sample_id":sid,"epsilon_velocity":eps,"enstrophy":e0,"q_threshold_p90":theta,
                     "reference_mask_voxels":int(mask0.sum()),"reference_q_mean":float(q0.mean()),
                     "reference_q_rms":float(np.sqrt(np.mean(q0*q0)))})
        for labels,dest in ((QUAL,qual),(FRESH,fresh)):
            for label in labels:
                rng=np.random.Generator(np.random.PCG64(seed64(sid,label)))
                delta=rng.uniform(-eps,eps,size=u.shape)
                rm,re,amp=core.response(u,u+delta,dx,theta,mask0,e0,delta)
                dest.append({"sample_id":sid,"seed":label,"mask_response_1mIoU":rm,
                             "enstrophy_relative_response":re,"gradient_amplification":amp})
    except Exception as exc:
        failures.append({"sample_id":sid,"stage":"analysis","error":f"{type(exc).__name__}: {exc}"})
write(HERE/"reference_metrics.csv",refs); write(HERE/"qualification_probes.csv",qual); write(HERE/"fresh_probes.csv",fresh)
if failures: write(HERE/"failures.csv",failures)
else: (HERE/"failures.csv").write_text("sample_id,stage,error\n",encoding="utf-8")
print("reference",len(refs),"qualification",len(qual),"fresh",len(fresh),"failures",len(failures))
