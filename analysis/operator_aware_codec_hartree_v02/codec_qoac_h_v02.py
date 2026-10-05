#!/usr/bin/env python3
"""QOAC-H v0.2: conservative Nyquist-aware Hermitian-orbit quantization."""
from __future__ import annotations

import json
import math
import struct
import time
import zlib
from dataclasses import dataclass

import numpy as np

MAGIC = b"QOACH02\n"
HEADER_LEN = struct.Struct("<Q")
DTYPES = (np.dtype("<i1"), np.dtype("<i2"), np.dtype("<i4"), np.dtype("<i8"))


@dataclass
class OrbitGeometry:
    shape: tuple[int, int, int]
    canonical_flat: np.ndarray
    partner_flat: np.ndarray
    self_mask: np.ndarray
    g2_cons: np.ndarray
    q: np.ndarray
    shell_ids: np.ndarray
    shell_count: int


@dataclass
class Prepared:
    field: np.ndarray
    lattice: np.ndarray
    spectrum: np.ndarray
    geometry: OrbitGeometry


def _coords_from_flat(flat: np.ndarray, shape: tuple[int, int, int]):
    nx, ny, nz = shape
    plane = ny * nz
    i = flat // plane
    rem = flat - i * plane
    j = rem // nz
    k = rem - j * nz
    return i, j, k


def _canonical_flat(shape: tuple[int, int, int]) -> np.ndarray:
    nx, ny, nz = shape
    i = np.arange(nx, dtype=np.int64)
    j = np.arange(ny, dtype=np.int64)
    k = np.arange(nz, dtype=np.int64)
    pi = (-i) % nx
    pj = (-j) % ny
    pk = (-k) % nz

    I, PI = i[:, None, None], pi[:, None, None]
    J, PJ = j[None, :, None], pj[None, :, None]
    K, PK = k[None, None, :], pk[None, None, :]
    canon = (I < PI) | ((I == PI) & ((J < PJ) | ((J == PJ) & (K <= PK))))
    return np.flatnonzero(canon.ravel())


def _partner_flat(flat: np.ndarray, shape: tuple[int, int, int]) -> np.ndarray:
    nx, ny, nz = shape
    i, j, k = _coords_from_flat(flat, shape)
    return (((-i) % nx) * ny + ((-j) % ny)) * nz + ((-k) % nz)


def alias_safe_g2_for_flat(
    flat: np.ndarray,
    shape: tuple[int, int, int],
    lattice: np.ndarray,
) -> np.ndarray:
    """Conservative min |G|^2 across alias-equivalent Nyquist sign choices."""
    nx, ny, nz = shape
    i, j, k = _coords_from_flat(flat, shape)

    f1 = np.fft.fftfreq(nx) * nx
    f2 = np.fft.fftfreq(ny) * ny
    f3 = np.fft.fftfreq(nz) * nz
    m1, m2, m3 = f1[i], f2[j], f3[k]

    ny1 = (i == nx // 2) if nx % 2 == 0 else np.zeros_like(i, dtype=bool)
    ny2 = (j == ny // 2) if ny % 2 == 0 else np.zeros_like(j, dtype=bool)
    ny3 = (k == nz // 2) if nz % 2 == 0 else np.zeros_like(k, dtype=bool)

    b = 2.0 * np.pi * np.linalg.inv(np.asarray(lattice, dtype=np.float64)).T
    metric = b @ b.T

    out = np.full(flat.size, np.inf, dtype=np.float64)
    for s1 in (-1.0, 1.0):
        a = np.where(ny1, s1 * (nx / 2.0), m1)
        for s2 in (-1.0, 1.0):
            bb = np.where(ny2, s2 * (ny / 2.0), m2)
            for s3 in (-1.0, 1.0):
                c = np.where(ny3, s3 * (nz / 2.0), m3)
                g2 = (
                    metric[0, 0] * a * a
                    + metric[1, 1] * bb * bb
                    + metric[2, 2] * c * c
                    + 2.0 * metric[0, 1] * a * bb
                    + 2.0 * metric[0, 2] * a * c
                    + 2.0 * metric[1, 2] * bb * c
                )
                np.minimum(out, g2, out=out)

    if float(np.min(out)) < -1e-10:
        raise RuntimeError("negative reciprocal norm")
    np.maximum(out, 0.0, out=out)
    out[np.abs(out) < 1e-28] = 0.0
    return out


def build_geometry(
    shape: tuple[int, int, int],
    lattice: np.ndarray,
    shell_count: int = 32,
) -> OrbitGeometry:
    shape = tuple(int(x) for x in shape)
    if shell_count < 1:
        raise ValueError("shell_count must be >=1")

    canonical = _canonical_flat(shape)
    partner = _partner_flat(canonical, shape)
    self_mask = canonical == partner
    g2_cons = alias_safe_g2_for_flat(canonical, shape, lattice)

    nonzero = g2_cons > 0.0
    if not np.any(nonzero):
        raise ValueError("no non-zero reciprocal orbit")
    gmax2 = float(g2_cons[nonzero].max())

    q = np.zeros_like(g2_cons)
    q[nonzero] = np.sqrt(g2_cons[nonzero] / gmax2)

    shell_ids = np.full(canonical.size, -1, dtype=np.int16)
    sid = np.floor(q[nonzero] * shell_count).astype(np.int64)
    shell_ids[nonzero] = np.clip(sid, 0, shell_count - 1).astype(np.int16)

    return OrbitGeometry(
        shape=shape,
        canonical_flat=canonical,
        partner_flat=partner,
        self_mask=self_mask,
        g2_cons=g2_cons,
        q=q,
        shell_ids=shell_ids,
        shell_count=int(shell_count),
    )


def prepare(field: np.ndarray, lattice: np.ndarray, shell_count: int = 32) -> Prepared:
    x = np.ascontiguousarray(np.asarray(field, dtype=np.float64))
    lat = np.asarray(lattice, dtype=np.float64)
    if x.ndim != 3:
        raise ValueError("field must be three-dimensional")
    if lat.shape != (3, 3):
        raise ValueError("lattice must have shape (3,3)")
    if not np.all(np.isfinite(x)):
        raise ValueError("field contains non-finite values")

    geometry = build_geometry(tuple(x.shape), lat, shell_count)
    spectrum = np.asarray(np.fft.fftn(x, norm="ortho"), dtype=np.complex128)
    return Prepared(x, lat.copy(), spectrum, geometry)


def quantization_steps(geometry: OrbitGeometry, alpha: float, beta: float = 2.0) -> np.ndarray:
    a, b = float(alpha), float(beta)
    if not (math.isfinite(a) and a > 0):
        raise ValueError("alpha must be finite and >0")
    if not (math.isfinite(b) and b >= 0):
        raise ValueError("beta must be finite and >=0")

    steps = np.zeros(geometry.q.size, dtype=np.float64)
    nonzero = geometry.g2_cons > 0.0
    if b == 0.0:
        steps[nonzero] = a
    else:
        steps[nonzero] = a * np.power(geometry.q[nonzero], b)
    if np.any(steps[nonzero] <= 0) or not np.all(np.isfinite(steps[nonzero])):
        raise ValueError("invalid quantization steps")
    return steps


def _quantize(values: np.ndarray, steps: np.ndarray) -> np.ndarray:
    scaled = np.asarray(values, dtype=np.float64) / np.asarray(steps, dtype=np.float64)
    if not np.all(np.isfinite(scaled)):
        raise OverflowError("non-finite scaled coefficient")
    if scaled.size and float(np.max(np.abs(scaled))) > float(np.iinfo(np.int64).max) * 0.95:
        raise OverflowError("quantized coefficient would overflow int64")
    return np.rint(scaled).astype(np.int64)


def _smallest_signed_dtype(max_abs: int) -> np.dtype:
    for dtype in DTYPES:
        if int(max_abs) <= int(np.iinfo(dtype).max):
            return dtype
    raise OverflowError("quantized integer exceeds int64 range")


def encode_prepared(
    prepared: Prepared,
    alpha: float,
    beta: float = 2.0,
    zlib_level: int = 6,
) -> tuple[bytes, dict]:
    t0 = time.perf_counter()
    if not 0 <= int(zlib_level) <= 9:
        raise ValueError("zlib_level must be in [0,9]")

    geometry = prepared.geometry
    steps = quantization_steps(geometry, alpha, beta)
    values = prepared.spectrum.ravel()[geometry.canonical_flat]

    blocks: list[bytes] = []
    records: list[dict] = []

    for shell in range(geometry.shell_count):
        selected = geometry.shell_ids == shell
        count = int(selected.sum())
        if count == 0:
            records.append({
                "shell": shell,
                "count": 0,
                "complex_count": 0,
                "dtype": "<i1",
                "raw_bytes": 0,
                "compressed_bytes": 0,
                "all_zero": True,
            })
            continue

        shell_values = values[selected]
        shell_steps = steps[selected]
        shell_self = geometry.self_mask[selected]

        qr = _quantize(shell_values.real, shell_steps)
        qi = _quantize(shell_values.imag[~shell_self], shell_steps[~shell_self])
        max_abs = max(
            int(np.max(np.abs(qr))) if qr.size else 0,
            int(np.max(np.abs(qi))) if qi.size else 0,
        )

        if max_abs == 0:
            records.append({
                "shell": shell,
                "count": count,
                "complex_count": int((~shell_self).sum()),
                "dtype": "<i1",
                "raw_bytes": 0,
                "compressed_bytes": 0,
                "all_zero": True,
            })
            continue

        dtype = _smallest_signed_dtype(max_abs)
        packed = np.empty(qr.size + qi.size, dtype=dtype)
        packed[:qr.size] = qr
        packed[qr.size:] = qi
        raw = packed.tobytes(order="C")
        compressed = zlib.compress(raw, int(zlib_level))
        blocks.append(compressed)
        records.append({
            "shell": shell,
            "count": count,
            "complex_count": int(qi.size),
            "dtype": dtype.str,
            "raw_bytes": len(raw),
            "compressed_bytes": len(compressed),
            "all_zero": False,
        })

    header = {
        "version": 2,
        "shape": list(geometry.shape),
        "lattice": prepared.lattice.tolist(),
        "alpha": float(alpha),
        "beta": float(beta),
        "shell_count": int(geometry.shell_count),
        "zlib_level": int(zlib_level),
        "dc_real": float(prepared.spectrum.ravel()[0].real),
        "shells": records,
    }
    header_bytes = json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    blob = MAGIC + HEADER_LEN.pack(len(header_bytes)) + header_bytes + b"".join(blocks)

    return blob, {
        "encoded_bytes": len(blob),
        "header_bytes": len(MAGIC) + HEADER_LEN.size + len(header_bytes),
        "canonical_reps": int(geometry.canonical_flat.size),
        "self_reps": int(geometry.self_mask.sum()),
        "encode_seconds": time.perf_counter() - t0,
    }


def _parse_header(blob: bytes):
    if not blob.startswith(MAGIC):
        raise ValueError("not a QOAC-H v0.2 stream")
    p = len(MAGIC)
    if len(blob) < p + HEADER_LEN.size:
        raise ValueError("truncated stream")
    n_header = HEADER_LEN.unpack(blob[p:p + HEADER_LEN.size])[0]
    p += HEADER_LEN.size
    end = p + int(n_header)
    if end > len(blob):
        raise ValueError("truncated header")
    return json.loads(blob[p:end].decode("utf-8")), end


def decode_blob(
    blob: bytes,
    return_spectrum: bool = False,
    geometry: OrbitGeometry | None = None,
):
    t0 = time.perf_counter()
    header, p = _parse_header(blob)
    shape = tuple(int(x) for x in header["shape"])
    lattice = np.asarray(header["lattice"], dtype=np.float64)
    shell_count = int(header["shell_count"])

    if geometry is None:
        geometry = build_geometry(shape, lattice, shell_count)
    elif tuple(geometry.shape) != shape or geometry.shell_count != shell_count:
        raise ValueError("cached geometry does not match stream")

    steps = quantization_steps(geometry, float(header["alpha"]), float(header["beta"]))
    spectrum = np.zeros(shape, dtype=np.complex128)
    flat = spectrum.ravel()
    flat[0] = complex(float(header["dc_real"]), 0.0)

    for record in header["shells"]:
        shell = int(record["shell"])
        selected = geometry.shell_ids == shell
        count = int(selected.sum())
        if count != int(record["count"]):
            raise ValueError("shell count mismatch")

        idx = geometry.canonical_flat[selected]
        partner = geometry.partner_flat[selected]
        shell_self = geometry.self_mask[selected]
        shell_steps = steps[selected]

        if bool(record["all_zero"]):
            values = np.zeros(count, dtype=np.complex128)
        else:
            compressed_bytes = int(record["compressed_bytes"])
            raw = zlib.decompress(memoryview(blob)[p:p + compressed_bytes])
            p += compressed_bytes
            if len(raw) != int(record["raw_bytes"]):
                raise ValueError("shell raw byte-count mismatch")

            packed = np.frombuffer(raw, dtype=np.dtype(record["dtype"]))
            complex_count = int(record["complex_count"])
            if packed.size != count + complex_count:
                raise ValueError("shell value-count mismatch")

            qr = packed[:count].astype(np.float64) * shell_steps
            values = qr.astype(np.complex128)
            if complex_count:
                values[~shell_self] += (
                    1j
                    * packed[count:].astype(np.float64)
                    * shell_steps[~shell_self]
                )

        flat[idx] = values
        flat[partner] = np.conj(values)

    if p != len(blob):
        raise ValueError("unexpected trailing bytes")

    inverse = np.fft.ifftn(spectrum, norm="ortho")
    max_imag = float(np.max(np.abs(inverse.imag)))
    field = np.ascontiguousarray(inverse.real, dtype=np.float64)
    stats = {
        "max_ifft_imag": max_imag,
        "decode_seconds": time.perf_counter() - t0,
    }
    if return_spectrum:
        return field, spectrum, header, stats
    return field, header, stats


def conservative_hartree_relative(
    prepared: Prepared,
    reconstructed_spectrum: np.ndarray,
) -> float:
    """Conservative alias-safe relative Hartree norm from full spectra."""
    geometry = prepared.geometry
    nonzero = geometry.g2_cons > 0.0
    idx = geometry.canonical_flat[nonzero]
    multiplicity = np.where(geometry.self_mask[nonzero], 1.0, 2.0)

    reference = prepared.spectrum.ravel()[idx]
    reconstructed = np.asarray(reconstructed_spectrum, dtype=np.complex128).ravel()[idx]
    denom = np.sum(
        multiplicity * np.abs(reference) ** 2 / (geometry.g2_cons[nonzero] ** 2)
    )
    numer = np.sum(
        multiplicity * np.abs(reconstructed - reference) ** 2
        / (geometry.g2_cons[nonzero] ** 2)
    )
    if not (np.isfinite(denom) and denom > 0 and np.isfinite(numer) and numer >= 0):
        raise ValueError("invalid conservative Hartree norm")
    return float(np.sqrt(numer / denom))
