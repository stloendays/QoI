#!/usr/bin/env python3
"""T1 baseline: uniform quantization of reciprocal modes with q <= q_c; modes above q_c are not stored.

Reuses the frozen QOAC-H v0.2 Hermitian-orbit topology (conservative Nyquist metric, G=0 exact,
per-shell integer width + zlib). Only the allocation differs: beta=0 inside the cutoff, nothing outside.
"""
from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "operator_aware_codec_hartree_v02"))
import codec_qoac_h_v02 as qoac  # noqa: E402

MAGIC = b"QOACT01\n"


def encode(prepared: qoac.PreparedSpectrum, alpha: float, q_cut: float, zlib_level: int = 6) -> bytes:
    topo = prepared.topology
    keep = topo.q <= float(q_cut)
    coeff = prepared.spectrum.ravel()[topo.rep_flat]
    qr = np.rint(coeff.real / alpha).astype(np.int64)
    qi = np.rint(coeff.imag / alpha).astype(np.int64)
    qi[topo.self_conjugate] = 0
    blocks, records = [], []
    for shell in range(topo.shell_count):
        idx = (topo.shell_ids == shell) & keep
        count = int(np.count_nonzero(idx))
        if count == 0:
            records.append({"shell": shell, "count": 0})
            continue
        rr, ii = qr[idx], qi[idx]
        dt = qoac._smallest_signed_dtype(max(int(np.max(np.abs(rr))), int(np.max(np.abs(ii)))))
        inter = np.empty(2 * count, dtype=dt)
        inter[0::2] = rr
        inter[1::2] = ii
        raw = inter.tobytes()
        comp = zlib.compress(raw, int(zlib_level))
        blocks.append(comp)
        records.append({"shell": shell, "count": count, "dtype": dt.str, "raw_bytes": len(raw), "compressed_bytes": len(comp)})
    header = {"version": 1, "shape": list(topo.shape), "lattice": topo.lattice.tolist(), "alpha": float(alpha),
              "q_cut": float(q_cut), "shell_count": topo.shell_count, "shells": records}
    hb = json.dumps(header, separators=(",", ":"), sort_keys=True).encode()
    dc = np.asarray([prepared.spectrum.ravel()[0]], dtype="<c16").tobytes()
    return MAGIC + struct.pack("<Q", len(hb)) + hb + dc + b"".join(blocks)


def decode(blob: bytes) -> np.ndarray:
    if not blob.startswith(MAGIC):
        raise ValueError("not a T1 stream")
    p = len(MAGIC)
    nh = struct.unpack("<Q", blob[p:p + 8])[0]
    p += 8
    header = json.loads(blob[p:p + nh])
    p += nh
    shape = tuple(header["shape"])
    topo = qoac.build_topology(shape, np.asarray(header["lattice"]), shell_count=header["shell_count"])
    keep = topo.q <= header["q_cut"]
    f = np.zeros(shape, dtype=np.complex128)
    flat = f.ravel()
    flat[0] = np.frombuffer(blob[p:p + 16], dtype="<c16")[0]
    p += 16
    for rec in header["shells"]:
        if rec["count"] == 0:
            continue
        raw = zlib.decompress(blob[p:p + rec["compressed_bytes"]])
        p += rec["compressed_bytes"]
        vals = np.frombuffer(raw, dtype=np.dtype(rec["dtype"])).astype(np.float64)
        idx = (topo.shell_ids == rec["shell"]) & keep
        if int(np.count_nonzero(idx)) != rec["count"]:
            raise ValueError("shell topology mismatch")
        coeff = (vals[0::2] + 1j * vals[1::2]) * header["alpha"]
        selfc = topo.self_conjugate[idx]
        coeff[selfc] = coeff[selfc].real
        flat[topo.rep_flat[idx]] = coeff
        ns = ~selfc
        flat[topo.partner_flat[idx][ns]] = np.conj(coeff[ns])
    if p != len(blob):
        raise ValueError("trailing bytes")
    out = np.fft.ifftn(f, norm="ortho")
    if float(np.max(np.abs(out.imag))) > 1e-11 * max(1.0, float(np.max(np.abs(out.real)))):
        raise RuntimeError("real-field invariant violated")
    return np.ascontiguousarray(out.real)
