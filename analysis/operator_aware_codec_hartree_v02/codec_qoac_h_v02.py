#!/usr/bin/env python3
"""QOAC-H v0.2: full-spectrum Hermitian-orbit quantization.

The v0.2 representation removes the v0.1 exact Nyquist-plane rate floor while
keeping the operator-derived beta=2 allocation law unchanged.
"""
from __future__ import annotations

import json
import math
import struct
import time
import zlib
from dataclasses import dataclass
from itertools import product
from typing import Any

import numpy as np

MAGIC = b"QOACH02\n"
HEADER_LEN = struct.Struct("<Q")
DTYPES = (np.dtype("<i1"), np.dtype("<i2"), np.dtype("<i4"), np.dtype("<i8"))


@dataclass
class HermitianTopology:
    shape: tuple[int, int, int]
    lattice: np.ndarray
    rep_flat: np.ndarray
    partner_flat: np.ndarray
    self_conjugate: np.ndarray
    q: np.ndarray
    shell_ids: np.ndarray
    shell_count: int
    g2_safe_rep: np.ndarray
    g2_safe_max: float


@dataclass
class PreparedSpectrum:
    field: np.ndarray
    topology: HermitianTopology
    spectrum: np.ndarray


def _freq_axis(n: int) -> np.ndarray:
    return np.rint(np.fft.fftfreq(int(n)) * int(n)).astype(np.int64)


def reciprocal_metric(lattice: np.ndarray) -> np.ndarray:
    lat = np.asarray(lattice, dtype=np.float64)
    if lat.shape != (3, 3):
        raise ValueError("lattice must have shape (3,3)")
    b = 2.0 * np.pi * np.linalg.inv(lat).T
    return b @ b.T


def conservative_g2(shape: tuple[int, int, int], lattice: np.ndarray) -> np.ndarray:
    """Minimum |G|^2 over alias-equivalent Nyquist sign choices."""
    nx, ny, nz = (int(x) for x in shape)
    axes = [_freq_axis(nx).astype(np.float64),
            _freq_axis(ny).astype(np.float64),
            _freq_axis(nz).astype(np.float64)]
    metric = reciprocal_metric(lattice)
    best = np.full((nx, ny, nz), np.inf, dtype=np.float64)

    sign_options = [(-1.0, 1.0) if n % 2 == 0 else (1.0,) for n in (nx, ny, nz)]
    nyquist_index = [n // 2 if n % 2 == 0 else None for n in (nx, ny, nz)]

    for signs in product(*sign_options):
        vals = []
        for axis, n, idx, sign in zip(axes, (nx, ny, nz), nyquist_index, signs):
            v = axis.copy()
            if idx is not None:
                v[idx] = sign * (n / 2.0)
            vals.append(v)
        a = vals[0][:, None, None]
        b = vals[1][None, :, None]
        c = vals[2][None, None, :]
        cur = (
            metric[0, 0] * a * a
            + metric[1, 1] * b * b
            + metric[2, 2] * c * c
            + 2.0 * metric[0, 1] * a * b
            + 2.0 * metric[0, 2] * a * c
            + 2.0 * metric[1, 2] * b * c
        )
        best = np.minimum(best, cur)

    best[np.abs(best) < 1e-24] = 0.0
    if not np.all(np.isfinite(best)) or np.any(best < 0.0):
        raise ValueError("invalid conservative reciprocal metric")
    return best


def build_topology(
    shape: tuple[int, int, int],
    lattice: np.ndarray,
    shell_count: int = 32,
) -> HermitianTopology:
    nx, ny, nz = (int(x) for x in shape)
    if min(nx, ny, nz) < 2:
        raise ValueError("all grid dimensions must be >=2")
    if int(shell_count) < 1:
        raise ValueError("shell_count must be >=1")

    g2 = conservative_g2((nx, ny, nz), lattice)

    i = np.arange(nx, dtype=np.int64)[:, None, None]
    j = np.arange(ny, dtype=np.int64)[None, :, None]
    k = np.arange(nz, dtype=np.int64)[None, None, :]
    pi = (-i) % nx
    pj = (-j) % ny
    pk = (-k) % nz

    canonical = (
        (i < pi)
        | ((i == pi) & (j < pj))
        | ((i == pi) & (j == pj) & (k <= pk))
    )
    active = canonical & (g2 > 0.0)
    rep_flat = np.flatnonzero(active).astype(np.int64)

    yz = ny * nz
    ri = rep_flat // yz
    rem = rep_flat % yz
    rj = rem // nz
    rk = rem % nz
    partner_flat = (((-ri) % nx) * ny + ((-rj) % ny)) * nz + ((-rk) % nz)
    partner_flat = partner_flat.astype(np.int64)
    self_conjugate = rep_flat == partner_flat

    g2_rep = g2.ravel()[rep_flat]
    g2_max = float(np.max(g2[g2 > 0.0]))
    q = np.sqrt(g2_rep / g2_max)
    shell_ids = np.floor(q * int(shell_count)).astype(np.int64)
    shell_ids = np.clip(shell_ids, 0, int(shell_count) - 1).astype(np.int16)

    # Each nonzero grid point must be covered exactly once by rep or partner.
    covered = np.zeros(nx * ny * nz, dtype=np.uint8)
    covered[0] = 1
    covered[rep_flat] += 1
    nonself = ~self_conjugate
    covered[partner_flat[nonself]] += 1
    if not np.all(covered == 1):
        raise RuntimeError("Hermitian orbit partition does not cover the grid exactly once")

    # Conservative |G| must be orbit symmetric.
    flat_g2 = g2.ravel()
    if not np.allclose(flat_g2[rep_flat], flat_g2[partner_flat], rtol=0.0, atol=1e-12):
        raise RuntimeError("conservative reciprocal metric is not Hermitian-orbit symmetric")

    return HermitianTopology(
        shape=(nx, ny, nz),
        lattice=np.asarray(lattice, dtype=np.float64).copy(),
        rep_flat=rep_flat,
        partner_flat=partner_flat,
        self_conjugate=self_conjugate,
        q=q,
        shell_ids=shell_ids,
        shell_count=int(shell_count),
        g2_safe_rep=g2_rep,
        g2_safe_max=g2_max,
    )


def prepare_field(
    field: np.ndarray,
    lattice: np.ndarray,
    shell_count: int = 32,
) -> PreparedSpectrum:
    x = np.ascontiguousarray(np.asarray(field, dtype=np.float64))
    if x.ndim != 3:
        raise ValueError("field must be three-dimensional")
    if not np.all(np.isfinite(x)):
        raise ValueError("field contains non-finite values")
    topo = build_topology(tuple(int(v) for v in x.shape), lattice, shell_count=shell_count)
    spectrum = np.asarray(np.fft.fftn(x, norm="ortho"), dtype=np.complex128)
    return PreparedSpectrum(field=x, topology=topo, spectrum=spectrum)


def quantization_steps(topology: HermitianTopology, alpha: float, beta: float = 2.0) -> np.ndarray:
    a, b = float(alpha), float(beta)
    if not (math.isfinite(a) and a > 0.0):
        raise ValueError("alpha must be finite and >0")
    if not (math.isfinite(b) and b >= 0.0):
        raise ValueError("beta must be finite and >=0")
    if b == 0.0:
        steps = np.full(topology.q.shape, a, dtype=np.float64)
    else:
        steps = a * np.power(topology.q, b)
    if not np.all(np.isfinite(steps)) or np.any(steps <= 0.0):
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


def encode_prepared(
    prepared: PreparedSpectrum,
    alpha: float,
    beta: float = 2.0,
    zlib_level: int = 6,
) -> tuple[bytes, dict[str, Any]]:
    t0 = time.perf_counter()
    if not 0 <= int(zlib_level) <= 9:
        raise ValueError("zlib_level must be in [0,9]")
    topo = prepared.topology
    steps = quantization_steps(topo, alpha=alpha, beta=beta)

    coeff = prepared.spectrum.ravel()[topo.rep_flat]
    qr = _quantize(coeff.real, steps)
    qi = _quantize(coeff.imag, steps)
    qi[topo.self_conjugate] = 0

    dc_raw = np.asarray([prepared.spectrum.ravel()[0]], dtype="<c16").tobytes(order="C")

    blocks: list[bytes] = []
    records: list[dict[str, Any]] = []
    for shell in range(topo.shell_count):
        idx = topo.shell_ids == shell
        count = int(np.count_nonzero(idx))
        if count == 0:
            records.append({"shell": shell, "count": 0, "dtype": "<i1", "raw_bytes": 0, "compressed_bytes": 0})
            continue
        rr, ii = qr[idx], qi[idx]
        max_abs = max(int(np.max(np.abs(rr))), int(np.max(np.abs(ii))))
        dt = _smallest_signed_dtype(max_abs)
        inter = np.empty(count * 2, dtype=dt)
        inter[0::2] = rr
        inter[1::2] = ii
        raw = inter.tobytes(order="C")
        comp = zlib.compress(raw, int(zlib_level))
        blocks.append(comp)
        records.append({
            "shell": shell,
            "count": count,
            "dtype": dt.str,
            "raw_bytes": len(raw),
            "compressed_bytes": len(comp),
        })

    header = {
        "version": 2,
        "shape": [int(v) for v in topo.shape],
        "lattice": topo.lattice.tolist(),
        "alpha": float(alpha),
        "beta": float(beta),
        "shell_count": int(topo.shell_count),
        "zlib_level": int(zlib_level),
        "dc_bytes": len(dc_raw),
        "representative_modes": int(topo.rep_flat.size),
        "self_conjugate_nonzero_modes": int(np.count_nonzero(topo.self_conjugate)),
        "shells": records,
    }
    hb = json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    blob = MAGIC + HEADER_LEN.pack(len(hb)) + hb + dc_raw + b"".join(blocks)
    return blob, {
        "encoded_bytes": len(blob),
        "header_bytes": len(MAGIC) + HEADER_LEN.size + len(hb),
        "dc_bytes": len(dc_raw),
        "representative_modes": int(topo.rep_flat.size),
        "self_conjugate_nonzero_modes": int(np.count_nonzero(topo.self_conjugate)),
        "exact_modes": 1,
        "encode_seconds": time.perf_counter() - t0,
    }


def _parse_blob(blob: bytes) -> tuple[dict[str, Any], memoryview, int]:
    if not blob.startswith(MAGIC):
        raise ValueError("not a QOAC-H v0.2 stream")
    p = len(MAGIC)
    if len(blob) < p + HEADER_LEN.size:
        raise ValueError("truncated stream")
    nhead = HEADER_LEN.unpack(blob[p:p + HEADER_LEN.size])[0]
    p += HEADER_LEN.size
    end = p + int(nhead)
    if end > len(blob):
        raise ValueError("truncated header")
    return json.loads(blob[p:end].decode("utf-8")), memoryview(blob), end


def decode_blob(blob: bytes, return_spectrum: bool = False):
    t0 = time.perf_counter()
    header, view, p = _parse_blob(blob)
    shape = tuple(int(v) for v in header["shape"])
    lattice = np.asarray(header["lattice"], dtype=np.float64)
    topo = build_topology(shape, lattice, shell_count=int(header["shell_count"]))
    steps = quantization_steps(topo, alpha=float(header["alpha"]), beta=float(header["beta"]))

    dc_bytes = int(header["dc_bytes"])
    dc = np.frombuffer(view[p:p + dc_bytes], dtype="<c16")
    p += dc_bytes
    if dc.size != 1:
        raise ValueError("invalid DC block")

    f = np.zeros(shape, dtype=np.complex128)
    flat = f.ravel()
    flat[0] = complex(dc[0])

    for rec in header["shells"]:
        count = int(rec["count"])
        if count == 0:
            continue
        cbytes = int(rec["compressed_bytes"])
        raw = zlib.decompress(view[p:p + cbytes])
        p += cbytes
        if len(raw) != int(rec["raw_bytes"]):
            raise ValueError("shell raw byte-count mismatch")
        vals = np.frombuffer(raw, dtype=np.dtype(rec["dtype"]))
        if vals.size != 2 * count:
            raise ValueError("shell value-count mismatch")
        idx = topo.shell_ids == int(rec["shell"])
        if int(np.count_nonzero(idx)) != count:
            raise ValueError("shell topology mismatch")
        rep = topo.rep_flat[idx]
        partner = topo.partner_flat[idx]
        selfc = topo.self_conjugate[idx]
        st = steps[idx]
        coeff = vals[0::2].astype(np.float64) * st + 1j * vals[1::2].astype(np.float64) * st
        coeff[selfc] = coeff[selfc].real + 0j
        flat[rep] = coeff
        ns = ~selfc
        flat[partner[ns]] = np.conj(coeff[ns])

    if p != len(blob):
        raise ValueError("unexpected trailing bytes")

    inverse = np.fft.ifftn(f, norm="ortho")
    imag_max = float(np.max(np.abs(inverse.imag)))
    real_scale = max(1.0, float(np.max(np.abs(inverse.real))))
    if imag_max > 1e-11 * real_scale:
        raise RuntimeError(f"decoded spectrum violates real-field invariant: imag_max={imag_max:g}")
    field = np.ascontiguousarray(inverse.real, dtype=np.float64)
    stats = {"decode_seconds": time.perf_counter() - t0, "imaginary_leakage_max": imag_max}
    return (field, f, header, stats) if return_spectrum else (field, header, stats)


def reciprocal_g2_historical(shape: tuple[int, int, int], lattice: np.ndarray) -> np.ndarray:
    nx, ny, nz = (int(v) for v in shape)
    b = 2.0 * np.pi * np.linalg.inv(np.asarray(lattice, dtype=np.float64)).T
    n1 = np.fft.fftfreq(nx) * nx
    n2 = np.fft.fftfreq(ny) * ny
    n3 = np.fft.rfftfreq(nz) * nz
    a, c, d = np.meshgrid(n1, n2, n3, indexing="ij")
    g = a[..., None] * b[0] + c[..., None] * b[1] + d[..., None] * b[2]
    return np.einsum("...k,...k->...", g, g)


def nyquist_mask_rfft(shape: tuple[int, int, int]) -> np.ndarray:
    nx, ny, nz = (int(v) for v in shape)
    m = np.zeros((nx, ny, nz // 2 + 1), dtype=bool)
    if nx % 2 == 0:
        m[nx // 2, :, :] = True
    if ny % 2 == 0:
        m[:, ny // 2, :] = True
    if nz % 2 == 0:
        m[:, :, -1] = True
    return m


def hartree_potential_from_field(field: np.ndarray, lattice: np.ndarray, safe: bool = False) -> np.ndarray:
    x = np.asarray(field, dtype=np.float64)
    g2 = reciprocal_g2_historical(tuple(x.shape), lattice)
    nyq = nyquist_mask_rfft(tuple(x.shape))
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
    if not (math.isfinite(rh) and rh > 0.0 and math.isfinite(rs) and rs > 0.0):
        raise ValueError("invalid reference Hartree RMS")
    return rh, rs


def hartree_error_metrics(
    error: np.ndarray,
    lattice: np.ndarray,
    reference_rms_historical: float,
    reference_rms_safe: float,
) -> tuple[float, float]:
    dh = hartree_potential_from_field(error, lattice, safe=False)
    ds = hartree_potential_from_field(error, lattice, safe=True)
    eh = float(np.sqrt(np.mean(dh * dh)) / float(reference_rms_historical))
    es = float(np.sqrt(np.mean(ds * ds)) / float(reference_rms_safe))
    return eh, es
