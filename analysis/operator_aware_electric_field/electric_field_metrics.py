#!/usr/bin/env python3
"""Periodic Hartree electric-field metrics for QOAC operator-generality tests."""
from __future__ import annotations
import math
import numpy as np


def reciprocal_components_rfft(shape: tuple[int,int,int], lattice: np.ndarray):
    nx,ny,nz=(int(v) for v in shape)
    b=2.0*np.pi*np.linalg.inv(np.asarray(lattice,dtype=np.float64)).T
    n1=np.fft.fftfreq(nx)*nx
    n2=np.fft.fftfreq(ny)*ny
    n3=np.fft.rfftfreq(nz)*nz
    a,c,d=np.meshgrid(n1,n2,n3,indexing="ij")
    gx=a*b[0,0]+c*b[1,0]+d*b[2,0]
    gy=a*b[0,1]+c*b[1,1]+d*b[2,1]
    gz=a*b[0,2]+c*b[1,2]+d*b[2,2]
    g2=gx*gx+gy*gy+gz*gz
    return gx,gy,gz,g2


def nyquist_mask_rfft(shape: tuple[int,int,int]) -> np.ndarray:
    nx,ny,nz=(int(v) for v in shape)
    m=np.zeros((nx,ny,nz//2+1),dtype=bool)
    if nx%2==0: m[nx//2,:,:]=True
    if ny%2==0: m[:,ny//2,:]=True
    if nz%2==0: m[:,:,-1]=True
    return m


def electric_field_from_density(field: np.ndarray, lattice: np.ndarray, safe: bool=False):
    x=np.asarray(field,dtype=np.float64)
    if x.ndim!=3 or not np.all(np.isfinite(x)):
        raise ValueError("invalid density field")
    gx,gy,gz,g2=reciprocal_components_rfft(tuple(x.shape),lattice)
    f=np.fft.rfftn(x)
    mask=g2>0.0
    if safe:
        mask &= ~nyquist_mask_rfft(tuple(x.shape))
    out=[]
    for gc in (gx,gy,gz):
        eh=np.zeros_like(f)
        eh[mask]=(-1j)*(4.0*np.pi)*gc[mask]*f[mask]/g2[mask]
        out.append(np.fft.irfftn(eh,s=x.shape))
    return tuple(out)


def vector_rms(v) -> float:
    s=np.zeros_like(np.asarray(v[0],dtype=np.float64))
    for x in v:
        a=np.asarray(x,dtype=np.float64)
        s += a*a
    z=float(np.sqrt(np.mean(s)))
    if not math.isfinite(z):
        raise ValueError("non-finite vector RMS")
    return z


def reference_electric_rms(field: np.ndarray, lattice: np.ndarray):
    hist=electric_field_from_density(field,lattice,safe=False)
    safe=electric_field_from_density(field,lattice,safe=True)
    rh=vector_rms(hist); rs=vector_rms(safe)
    if rh<=0.0 or rs<=0.0:
        raise ValueError("zero electric-field reference RMS")
    return rh,rs


def electric_error_metrics(error: np.ndarray, lattice: np.ndarray, ref_hist: float, ref_safe: float):
    hist=electric_field_from_density(error,lattice,safe=False)
    safe=electric_field_from_density(error,lattice,safe=True)
    return vector_rms(hist)/float(ref_hist), vector_rms(safe)/float(ref_safe)
