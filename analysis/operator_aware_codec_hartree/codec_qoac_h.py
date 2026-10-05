#!/usr/bin/env python3
"""QOAC-H v0.1: operator-aware spectral quantization for Hartree fidelity."""
from __future__ import annotations

import json
import math
import struct
import time
import zlib
from dataclasses import dataclass
from typing import Any

import numpy as np

MAGIC = b"QOACH01\n"
HEADER_LEN = struct.Struct("<Q")
DTYPES = (np.dtype("<i1"), np.dtype("<i2"), np.dtype("<i4"), np.dtype("<i8"))


@dataclass
class PreparedSpectrum:
    field: np.ndarray
    lattice: np.ndarray
    spectrum: np.ndarray
    g2: np.ndarray
    nyquist: np.ndarray
    active: np.ndarray
    q: np.ndarray
    shell_ids: np.ndarray
    shell_count: int


def reciprocal_g2(shape: tuple[int, int, int], lattice: np.ndarray) -> np.ndarray:
    nx, ny, nz = (int(x) for x in shape)
    lat = np.asarray(lattice, dtype=np.float64)
    if lat.shape != (3, 3):
        raise ValueError("lattice must have shape (3,3)")
    b = 2.0 * np.pi * np.linalg.inv(lat).T
    n1 = np.fft.fftfreq(nx) * nx
    n2 = np.fft.fftfreq(ny) * ny
    n3 = np.fft.rfftfreq(nz) * nz
    n1g, n2g, n3g = np.meshgrid(n1, n2, n3, indexing="ij")
    g = n1g[..., None] * b[0] + n2g[..., None] * b[1] + n3g[..., None] * b[2]
    return np.einsum("...k,...k->...", g, g)


def nyquist_mask(shape: tuple[int, int, int]) -> np.ndarray:
    nx, ny, nz = (int(x) for x in shape)
    m = np.zeros((nx, ny, nz // 2 + 1), dtype=bool)
    if nx % 2 == 0:
        m[nx // 2, :, :] = True
    if ny % 2 == 0:
        m[:, ny // 2, :] = True
    if nz % 2 == 0:
        m[:, :, -1] = True
    return m


def _shell_ids(q: np.ndarray, active: np.ndarray, shell_count: int) -> np.ndarray:
    if shell_count < 1:
        raise ValueError("shell_count must be >=1")
    out = np.full(q.shape, -1, dtype=np.int16)
    x = np.floor(q[active] * shell_count).astype(np.int64)
    x = np.clip(x, 0, shell_count - 1)
    out[active] = x.astype(np.int16)
    return out


def prepare_field(field: np.ndarray, lattice: np.ndarray, shell_count: int = 32) -> PreparedSpectrum:
    x = np.ascontiguousarray(np.asarray(field, dtype=np.float64))
    lat = np.asarray(lattice, dtype=np.float64)
    if x.ndim != 3:
        raise ValueError("field must be three-dimensional")
    if not np.all(np.isfinite(x)):
        raise ValueError("field contains non-finite values")
    g2 = reciprocal_g2(tuple(x.shape), lat)
    nyq = nyquist_mask(tuple(x.shape))
    active = (g2 > 0.0) & (~nyq)
    if not np.any(active):
        raise ValueError("no active reciprocal modes")
    g = np.sqrt(g2)
    gmax = float(g[active].max())
    q = np.zeros_like(g, dtype=np.float64)
    q[active] = g[active] / gmax
    shells = _shell_ids(q, active, shell_count)
    f = np.fft.rfftn(x, norm="ortho")
    return PreparedSpectrum(x, lat.copy(), np.asarray(f, dtype=np.complex128), g2, nyq, active, q, shells, int(shell_count))


def quantization_steps(prepared: PreparedSpectrum, alpha: float, beta: float) -> np.ndarray:
    a, b = float(alpha), float(beta)
    if not (math.isfinite(a) and a > 0):
        raise ValueError("alpha must be finite and >0")
    if not (math.isfinite(b) and b >= 0):
        raise ValueError("beta must be finite and >=0")
    steps = np.zeros(prepared.q.shape, dtype=np.float64)
    if b == 0.0:
        steps[prepared.active] = a
    else:
        steps[prepared.active] = a * np.power(prepared.q[prepared.active], b)
    if not np.all(np.isfinite(steps[prepared.active])) or np.any(steps[prepared.active] <= 0):
        raise ValueError("invalid quantization step")
    return steps


def _smallest_signed_dtype(max_abs: int) -> np.dtype:
    for dt in DTYPES:
        if int(max_abs) <= int(np.iinfo(dt).max):
            return dt
    raise OverflowError("quantized integer exceeds int64 range")


def _quantize(values: np.ndarray, steps: np.ndarray) -> np.ndarray:
    scaled = np.asarray(values, dtype=np.float64) / np.asarray(steps, dtype=np.float64)
    if not np.all(np.isfinite(scaled)):
        raise OverflowError("non-finite scaled coefficient")
    if scaled.size and float(np.max(np.abs(scaled))) > float(np.iinfo(np.int64).max) * 0.95:
        raise OverflowError("quantized coefficient would overflow int64")
    return np.rint(scaled).astype(np.int64)


def encode_prepared(prepared: PreparedSpectrum, alpha: float, beta: float = 2.0, zlib_level: int = 6) -> tuple[bytes, dict[str, Any]]:
    t0 = time.perf_counter()
    if not 0 <= int(zlib_level) <= 9:
        raise ValueError("zlib_level must be in [0,9]")
    steps = quantization_steps(prepared, alpha, beta)
    f, active = prepared.spectrum, prepared.active
    special = ~active

    qr = np.zeros(f.shape, dtype=np.int64)
    qi = np.zeros(f.shape, dtype=np.int64)
    qr[active] = _quantize(f.real[active], steps[active])
    qi[active] = _quantize(f.imag[active], steps[active])

    special_values = np.empty(int(special.sum()) * 2, dtype="<f8")
    special_values[0::2] = f.real[special]
    special_values[1::2] = f.imag[special]
    special_raw = special_values.tobytes(order="C")
    special_comp = zlib.compress(special_raw, int(zlib_level))

    blocks, records = [], []
    qr_flat, qi_flat = qr.ravel(), qi.ravel()
    shell_flat = prepared.shell_ids.ravel()
    for shell in range(prepared.shell_count):
        idx = shell_flat == shell
        count = int(np.count_nonzero(idx))
        if count == 0:
            records.append({"shell": shell, "count": 0, "dtype": "<i1", "raw_bytes": 0, "compressed_bytes": 0})
            continue
        rr, ii = qr_flat[idx], qi_flat[idx]
        max_abs = max(int(np.max(np.abs(rr))), int(np.max(np.abs(ii))))
        dt = _smallest_signed_dtype(max_abs)
        inter = np.empty(count * 2, dtype=dt)
        inter[0::2], inter[1::2] = rr, ii
        raw = inter.tobytes(order="C")
        comp = zlib.compress(raw, int(zlib_level))
        blocks.append(comp)
        records.append({"shell": shell, "count": count, "dtype": dt.str, "raw_bytes": len(raw), "compressed_bytes": len(comp)})

    header = {
        "version": 1,
        "shape": [int(x) for x in prepared.field.shape],
        "lattice": prepared.lattice.tolist(),
        "alpha": float(alpha),
        "beta": float(beta),
        "shell_count": int(prepared.shell_count),
        "zlib_level": int(zlib_level),
        "special_count": int(special.sum()),
        "special_raw_bytes": len(special_raw),
        "special_compressed_bytes": len(special_comp),
        "shells": records,
    }
    hb = json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    blob = MAGIC + HEADER_LEN.pack(len(hb)) + hb + special_comp + b"".join(blocks)
    return blob, {
        "encoded_bytes": len(blob),
        "header_bytes": len(MAGIC) + HEADER_LEN.size + len(hb),
        "special_compressed_bytes": len(special_comp),
        "active_modes": int(active.sum()),
        "special_modes": int(special.sum()),
        "encode_seconds": time.perf_counter() - t0,
    }


def _parse_blob(blob: bytes) -> tuple[dict[str, Any], memoryview, int]:
    if not blob.startswith(MAGIC):
        raise ValueError("not a QOAC-H v0.1 stream")
    p = len(MAGIC)
    if len(blob) < p + HEADER_LEN.size:
        raise ValueError("truncated QOAC-H stream")
    nhead = HEADER_LEN.unpack(blob[p:p + HEADER_LEN.size])[0]
    p += HEADER_LEN.size
    end = p + int(nhead)
    if end > len(blob):
        raise ValueError("truncated QOAC-H header")
    return json.loads(blob[p:end].decode("utf-8")), memoryview(blob), end


def decode_blob(blob: bytes, return_spectrum: bool = False):
    t0 = time.perf_counter()
    header, view, p = _parse_blob(blob)
    shape = tuple(int(x) for x in header["shape"])
    lattice = np.asarray(header["lattice"], dtype=np.float64)
    alpha, beta = float(header["alpha"]), float(header["beta"])
    shell_count = int(header["shell_count"])

    g2 = reciprocal_g2(shape, lattice)
    nyq = nyquist_mask(shape)
    active = (g2 > 0.0) & (~nyq)
    g = np.sqrt(g2)
    q = np.zeros_like(g)
    q[active] = g[active] / float(g[active].max())
    shells = _shell_ids(q, active, shell_count)
    stub = PreparedSpectrum(np.empty(shape), lattice, np.empty(g2.shape, dtype=np.complex128), g2, nyq, active, q, shells, shell_count)
    steps = quantization_steps(stub, alpha, beta)

    f = np.zeros(g2.shape, dtype=np.complex128)
    special = ~active
    clen = int(header["special_compressed_bytes"])
    special_raw = zlib.decompress(view[p:p + clen])
    p += clen
    if len(special_raw) != int(header["special_raw_bytes"]):
        raise ValueError("special block byte-count mismatch")
    vals = np.frombuffer(special_raw, dtype="<f8")
    if vals.size != int(header["special_count"]) * 2:
        raise ValueError("special block count mismatch")
    f.real[special], f.imag[special] = vals[0::2], vals[1::2]

    flat_r, flat_i = f.real.ravel(), f.imag.ravel()
    shell_flat, step_flat = shells.ravel(), steps.ravel()
    for rec in header["shells"]:
        count = int(rec["count"])
        if count == 0:
            continue
        cbytes = int(rec["compressed_bytes"])
        raw = zlib.decompress(view[p:p + cbytes])
        p += cbytes
        if len(raw) != int(rec["raw_bytes"]):
            raise ValueError("shell raw byte-count mismatch")
        arr = np.frombuffer(raw, dtype=np.dtype(rec["dtype"]))
        if arr.size != count * 2:
            raise ValueError("shell value-count mismatch")
        idx = shell_flat == int(rec["shell"])
        if int(np.count_nonzero(idx)) != count:
            raise ValueError("shell topology mismatch")
        flat_r[idx] = arr[0::2].astype(np.float64) * step_flat[idx]
        flat_i[idx] = arr[1::2].astype(np.float64) * step_flat[idx]
    if p != len(blob):
        raise ValueError("unexpected trailing bytes")

    field = np.ascontiguousarray(np.fft.irfftn(f, s=shape, norm="ortho").real, dtype=np.float64)
    stats = {"decode_seconds": time.perf_counter() - t0}
    return (field, f, header, stats) if return_spectrum else (field, header, stats)


def hartree_potential_from_field(field: np.ndarray, lattice: np.ndarray, safe: bool = False) -> np.ndarray:
    x = np.asarray(field, dtype=np.float64)
    g2 = reciprocal_g2(tuple(x.shape), lattice)
    nyq = nyquist_mask(tuple(x.shape))
    f = np.fft.rfftn(x)
    v = np.zeros_like(f)
    mask = g2 > 0.0
    if safe:
        mask &= ~nyq
    v[mask] = 4.0 * np.pi * f[mask] / g2[mask]
    return np.fft.irfftn(v, s=x.shape)


def reference_hartree_rms(field: np.ndarray, lattice: np.ndarray) -> tuple[float, float]:
    vh = hartree_potential_from_field(field, lattice, safe=False)
    vs = hartree_potential_from_field(field, lattice, safe=True)
    rh = float(np.sqrt(np.mean(vh * vh)))
    rs = float(np.sqrt(np.mean(vs * vs)))
    if not (math.isfinite(rh) and rh > 0 and math.isfinite(rs) and rs > 0):
        raise ValueError("invalid reference Hartree RMS")
    return rh, rs


def hartree_error_metrics(error: np.ndarray, lattice: np.ndarray, reference_rms_historical: float, reference_rms_safe: float) -> tuple[float, float]:
    dh = hartree_potential_from_field(error, lattice, safe=False)
    ds = hartree_potential_from_field(error, lattice, safe=True)
    eh = float(np.sqrt(np.mean(dh * dh)) / float(reference_rms_historical))
    es = float(np.sqrt(np.mean(ds * ds)) / float(reference_rms_safe))
    return eh, es
