#!/usr/bin/env python3
"""Lossless serialization of an exact on-grid Bader partition map."""
from __future__ import annotations

import struct
import zlib
import numpy as np

MAGIC=b"QOABMAP1"
HEADER=struct.Struct("<8sIIIIBBI")
METHOD_RAW=1
METHOD_RLE=2
DTYPES={1:np.dtype("<u1"),2:np.dtype("<u2"),4:np.dtype("<u4")}


def label_dtype(max_label:int)->np.dtype:
    if max_label < 0:
        raise ValueError("negative label")
    if max_label <= np.iinfo(np.uint8).max: return DTYPES[1]
    if max_label <= np.iinfo(np.uint16).max: return DTYPES[2]
    return DTYPES[4]


def _header(shape,max_label,itemsize,method,nruns):
    nx,ny,nz=(int(x) for x in shape)
    return HEADER.pack(MAGIC,nx,ny,nz,int(max_label),int(itemsize),int(method),int(nruns))


def encode_raw(labels:np.ndarray,level:int=6)->bytes:
    lab=np.asarray(labels)
    if lab.ndim!=3 or np.any(lab<0): raise ValueError("invalid labels")
    mx=int(lab.max()) if lab.size else 0
    dt=label_dtype(mx)
    raw=np.asarray(lab,dtype=dt).ravel(order="F").tobytes()
    return _header(lab.shape,mx,dt.itemsize,METHOD_RAW,0)+zlib.compress(raw,level)


def _runs(flat):
    if len(flat)==0:
        return np.array([],dtype=np.int64),np.array([],dtype=np.uint32)
    cut=np.flatnonzero(flat[1:]!=flat[:-1])+1
    starts=np.r_[0,cut]
    ends=np.r_[cut,len(flat)]
    vals=flat[starts]
    lens=(ends-starts).astype(np.uint64)
    if np.any(lens>np.iinfo(np.uint32).max):
        raise OverflowError("RLE run too long")
    return vals,lens.astype(np.uint32)


def encode_rle(labels:np.ndarray,level:int=6)->bytes:
    lab=np.asarray(labels)
    if lab.ndim!=3 or np.any(lab<0): raise ValueError("invalid labels")
    mx=int(lab.max()) if lab.size else 0
    dt=label_dtype(mx)
    flat=np.asarray(lab,dtype=dt).ravel(order="F")
    vals,lens=_runs(flat)
    rec=bytearray()
    for v,n in zip(vals,lens):
        rec.extend(np.asarray([v],dtype=dt).tobytes())
        rec.extend(struct.pack("<I",int(n)))
    return _header(lab.shape,mx,dt.itemsize,METHOD_RLE,len(vals))+zlib.compress(bytes(rec),level)


def encode_best(labels:np.ndarray,level:int=6):
    a=encode_raw(labels,level)
    b=encode_rle(labels,level)
    if len(a)<=len(b): return a,{"method":"packed_zlib","bytes":len(a)}
    return b,{"method":"rle_zlib","bytes":len(b)}


def decode(blob:bytes)->np.ndarray:
    if len(blob)<HEADER.size: raise ValueError("truncated stream")
    magic,nx,ny,nz,mx,itemsize,method,nruns=HEADER.unpack(blob[:HEADER.size])
    if magic!=MAGIC or itemsize not in DTYPES: raise ValueError("invalid header")
    dt=DTYPES[itemsize]; n=int(nx)*int(ny)*int(nz)
    raw=zlib.decompress(blob[HEADER.size:])
    if method==METHOD_RAW:
        x=np.frombuffer(raw,dtype=dt)
        if x.size!=n: raise ValueError("raw label count mismatch")
    elif method==METHOD_RLE:
        step=itemsize+4
        if len(raw)!=int(nruns)*step: raise ValueError("RLE byte count mismatch")
        vals=[]; lens=[]
        p=0
        for _ in range(int(nruns)):
            vals.append(int(np.frombuffer(raw[p:p+itemsize],dtype=dt,count=1)[0])); p+=itemsize
            lens.append(struct.unpack("<I",raw[p:p+4])[0]); p+=4
        if sum(lens)!=n: raise ValueError("RLE voxel count mismatch")
        x=np.repeat(np.asarray(vals,dtype=dt),np.asarray(lens,dtype=np.int64))
    else:
        raise ValueError("unknown method")
    out=x.reshape((int(nx),int(ny),int(nz)),order="F").astype(np.int32)
    if out.size and int(out.max())!=int(mx): raise ValueError("max-label mismatch")
    return out


def direct_atomic_charges(field,labels,lattice,natoms):
    rho=np.asarray(field,dtype=np.float64)
    lab=np.asarray(labels,dtype=np.int64)
    if rho.shape!=lab.shape: raise ValueError("shape mismatch")
    # VASP CHGCAR grid values in the repository decoder integrate to
    # electron count by the grid average: sum(values) / N_grid.
    # The cell-volume factor is already contained in the stored convention.
    scale=1.0/rho.size
    sums=np.bincount(lab.ravel(),weights=rho.ravel(),minlength=max(int(lab.max())+1,natoms+1))
    return sums[1:natoms+1]*scale
