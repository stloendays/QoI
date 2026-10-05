#!/usr/bin/env python3
"""Exact reciprocal-space electric-field error metrics for General-QOAC."""
from __future__ import annotations

import math
import numpy as np


def reciprocal_g2_rfft(shape: tuple[int,int,int], lattice: np.ndarray) -> np.ndarray:
    nx,ny,nz=(int(v) for v in shape)
    b=2.0*np.pi*np.linalg.inv(np.asarray(lattice,dtype=np.float64)).T
    n1=np.fft.fftfreq(nx)*nx
    n2=np.fft.fftfreq(ny)*ny
    n3=np.fft.rfftfreq(nz)*nz
    a,c,d=np.meshgrid(n1,n2,n3,indexing="ij")
    g=a[...,None]*b[0]+c[...,None]*b[1]+d[...,None]*b[2]
    return np.einsum("...k,...k->...",g,g)


def rfft_multiplicity(shape: tuple[int,int,int]) -> np.ndarray:
    nx,ny,nz=(int(v) for v in shape)
    w=np.full((nx,ny,nz//2+1),2.0,dtype=np.float64)
    w[:,:,0]=1.0
    if nz%2==0:
        w[:,:,-1]=1.0
    return w


def nyquist_mask_rfft(shape: tuple[int,int,int]) -> np.ndarray:
    nx,ny,nz=(int(v) for v in shape)
    m=np.zeros((nx,ny,nz//2+1),dtype=bool)
    if nx%2==0: m[nx//2,:,:]=True
    if ny%2==0: m[:,ny//2,:]=True
    if nz%2==0: m[:,:,-1]=True
    return m


def electric_field_energy(field: np.ndarray, lattice: np.ndarray, safe: bool=False) -> float:
    """Return quantity proportional to real-space ||E_H||_2^2.

    Constants (4*pi)^2 and FFT normalization are omitted because they cancel
    exactly in relative-RMSE ratios.
    """
    x=np.asarray(field,dtype=np.float64)
    if x.ndim!=3 or not np.all(np.isfinite(x)):
        raise ValueError("field must be finite 3-D float data")
    f=np.fft.rfftn(x)
    g2=reciprocal_g2_rfft(tuple(x.shape),lattice)
    w=rfft_multiplicity(tuple(x.shape))
    mask=g2>0.0
    if safe:
        mask &= ~nyquist_mask_rfft(tuple(x.shape))
    val=float(np.sum(w[mask]*(np.abs(f[mask])**2)/g2[mask]))
    if not math.isfinite(val) or val<0.0:
        raise ValueError("invalid electric-field energy")
    return val


def reference_energies(field: np.ndarray, lattice: np.ndarray) -> tuple[float,float]:
    hist=electric_field_energy(field,lattice,False)
    safe=electric_field_energy(field,lattice,True)
    if not (hist>0.0 and safe>0.0):
        raise ValueError("reference electric-field energy must be positive")
    return hist,safe


def relative_error(
    error: np.ndarray,
    lattice: np.ndarray,
    reference_historical_energy: float,
    reference_safe_energy: float,
) -> tuple[float,float]:
    eh=electric_field_energy(error,lattice,False)
    es=electric_field_energy(error,lattice,True)
    if not (reference_historical_energy>0.0 and reference_safe_energy>0.0):
        raise ValueError("reference energies must be positive")
    return (
        float(math.sqrt(eh/float(reference_historical_energy))),
        float(math.sqrt(es/float(reference_safe_energy))),
    )


def explicit_vector_rms(field: np.ndarray, lattice: np.ndarray, safe: bool=False) -> float:
    """Small-grid validation implementation using explicit vector inverse FFT."""
    x=np.asarray(field,dtype=np.float64)
    nx,ny,nz=x.shape
    b=2.0*np.pi*np.linalg.inv(np.asarray(lattice,dtype=np.float64)).T
    n1=np.fft.fftfreq(nx)*nx
    n2=np.fft.fftfreq(ny)*ny
    n3=np.fft.rfftfreq(nz)*nz
    a,c,d=np.meshgrid(n1,n2,n3,indexing="ij")
    gv=np.stack([
        a*b[0,0]+c*b[1,0]+d*b[2,0],
        a*b[0,1]+c*b[1,1]+d*b[2,1],
        a*b[0,2]+c*b[1,2]+d*b[2,2],
    ],axis=-1)
    g2=np.einsum("...k,...k->...",gv,gv)
    mask=g2>0.0
    if safe: mask &= ~nyquist_mask_rfft(tuple(x.shape))
    f=np.fft.rfftn(x)
    ss=np.zeros(x.shape,dtype=np.float64)
    for comp in range(3):
        ek=np.zeros_like(f,dtype=np.complex128)
        ek[mask]=-1j*4.0*np.pi*f[mask]*gv[...,comp][mask]/g2[mask]
        e=np.fft.irfftn(ek,s=x.shape,axes=(0,1,2))
        ss += e*e
    return float(np.sqrt(np.mean(ss)))
