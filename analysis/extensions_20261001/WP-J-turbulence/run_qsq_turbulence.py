#!/usr/bin/env python3
"""Run five-probe QSQ and 59 fresh turbulence probes on fetched JHTDB cutouts."""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
QUAL = (20260905, 1, 2, 3, 4)
FRESH = tuple(range(10000, 10059))

def seed64(sample_id: str, label: int) -> int:
    s = f"QSQ-JHTDB|{sample_id}|velocity|{label}"
    return int.from_bytes(hashlib.sha256(s.encode()).digest()[:8], "little")

def grad_centered(u: np.ndarray, dx: float) -> np.ndarray:
    # u shape: (x,y,z,component); A[...,i,j] = d u_i / d x_j.
    core = (slice(1,-1), slice(1,-1), slice(1,-1))
    g = np.empty((u.shape[0]-2,u.shape[1]-2,u.shape[2]-2,3,3), dtype=np.float64)
    for comp in range(3):
        g[...,comp,0] = (u[2:,1:-1,1:-1,comp] - u[:-2,1:-1,1:-1,comp])/(2*dx)
        g[...,comp,1] = (u[1:-1,2:,1:-1,comp] - u[1:-1,:-2,1:-1,comp])/(2*dx)
        g[...,comp,2] = (u[1:-1,1:-1,2:,comp] - u[1:-1,1:-1,:-2,comp])/(2*dx)
    return g

def fields(u: np.ndarray, dx: float):
    A = grad_centered(u, dx)
    AT = np.swapaxes(A, -1, -2)
    S = 0.5*(A+AT)
    O = 0.5*(A-AT)
    q = 0.5*(np.sum(O*O,axis=(-2,-1)) - np.sum(S*S,axis=(-2,-1)))
    wx = A[...,2,1] - A[...,1,2]
    wy = A[...,0,2] - A[...,2,0]
    wz = A[...,1,0] - A[...,0,1]
    ens = float(np.mean(wx*wx + wy*wy + wz*wz))
    return A, q, ens

def response(u0, up, dx, theta, mask0, ens0, delta):
    _, q, ens = fields(up, dx)
    mask = q > theta
    inter = np.count_nonzero(mask & mask0)
    union = np.count_nonzero(mask | mask0)
    r_mask = 1.0 - (inter/union if union else 1.0)
    r_ens = abs(ens-ens0)/abs(ens0)
    gd = grad_centered(delta, dx)
    dcore = delta[1:-1,1:-1,1:-1,:]
    amp = float(np.linalg.norm(gd.ravel()) / max(np.linalg.norm(dcore.ravel()), 1e-300))
    return float(r_mask), float(r_ens), amp

def write_rows(path, rows):
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=str(HERE/"data"))
    a=ap.parse_args()
    data=Path(a.data_dir)
    manifest=list(csv.DictReader((HERE/"sample_manifest.csv").open()))
    refs=[]; qual=[]; fresh=[]; failures=[]
    for row in manifest:
        sid=row["sample_id"]; path=data/f"{sid}.npy"
        try:
            u=np.asarray(np.load(path),dtype=np.float64)
            if u.shape != (15,15,15,3) or not np.isfinite(u).all():
                raise ValueError(f"invalid velocity shape/finiteness: {u.shape}")
            dx=float(row["dx"])
            A0,q0,e0=fields(u,dx)
            theta=float(np.quantile(q0,0.90,method="linear"))
            mask0=q0>theta
            eps=float(np.max(np.abs(u.astype(np.float16).astype(np.float64)-u)))
            if not np.isfinite(eps) or eps<=0:
                raise ValueError(f"invalid float16 scale {eps}")
            refs.append({
                "sample_id":sid,"epsilon_velocity":eps,"enstrophy":e0,
                "q_threshold_p90":theta,"reference_mask_voxels":int(mask0.sum()),
                "reference_q_mean":float(q0.mean()),"reference_q_rms":float(np.sqrt(np.mean(q0*q0))),
            })
            for family, labels, dest in (("qualification",QUAL,qual),("fresh",FRESH,fresh)):
                for label in labels:
                    rng=np.random.Generator(np.random.PCG64(seed64(sid,label)))
                    delta=rng.uniform(-eps,eps,size=u.shape)
                    rm,re,amp=response(u,u+delta,dx,theta,mask0,e0,delta)
                    dest.append({
                        "sample_id":sid,"seed":label,
                        "mask_response_1mIoU":rm,
                        "enstrophy_relative_response":re,
                        "gradient_amplification":amp,
                    })
        except Exception as exc:
            failures.append({"sample_id":sid,"stage":"analysis","error":f"{type(exc).__name__}: {exc}"})
    if refs: write_rows(HERE/"reference_metrics.csv",refs)
    if qual: write_rows(HERE/"qualification_probes.csv",qual)
    if fresh: write_rows(HERE/"fresh_probes.csv",fresh)
    if failures:
        write_rows(HERE/"failures.csv",failures)
    else:
        (HERE/"failures.csv").write_text("sample_id,stage,error\n",encoding="utf-8")
    print(json.dumps({"reference":len(refs),"qualification":len(qual),"fresh":len(fresh),"failures":len(failures)}))

if __name__=="__main__":
    main()
