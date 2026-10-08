#!/usr/bin/env python3
"""Codec invocations for the M (MGARD) and Q (QPET) strongest-baseline arms; see PROTOCOL.md.

M reuses the MGARD CLI invocation of the SI Note 2.4 study unchanged (`run_baselines.mgard_roundtrip`).
Q drives the QPET authors' own command-line programs (`hpez` for SZ3-QPET / HPEZ-QPET, `sperr3d` for SPERR-QPET).
Every Q stream is written to a file by the compressor process and decoded by a separate decompressor process.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "qoac_h_strong_baselines"))
from run_baselines import mgard_roundtrip  # noqa: E402,F401  (verbatim reuse of the SI Note 2.4 MGARD invocation)

MGARD_S = ("inf", "0", "-1", "-2")
QPET_HOSTS = ("hpez", "sperr", "sz3")          # order = execution priority (slowest first)
QPET_LEVEL = {"sz3": "0", "hpez": "3"}        # hpez -q 0 = SZ3.1 host, -q 3 = HPEZ host (authors' default)
QPET_BLOCKS = (4, 8, 16)
CALL_TIMEOUT = 1800                            # seconds per compress or decompress process


def fastest_first(shape) -> list[str]:
    """QPET CLIs take dimensions fastest-varying first; numpy C-order arrays are slowest-first."""
    return [str(int(v)) for v in reversed(tuple(shape))]


def qpet_sz_config(block: int) -> str:
    """QPET szfamily QoI config: regional (block) average of f(x) = x over block^3 cubes."""
    return ("[QoISettings]\n"
            "qoi = 14\n"
            "qoi_string = x\n"
            "qoiRegionMode = 1\n"
            f"qoiRegionSize = {int(block)}\n")


def _exe(env: str, name: str) -> str:
    p = os.environ.get(env) or shutil.which(name)
    if not p:
        raise RuntimeError(f"{name} CLI not found")
    return p


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=CALL_TIMEOUT)
    if r.returncode != 0:
        raise RuntimeError(f"{Path(cmd[0]).name} rc={r.returncode} stderr={r.stderr[-300:]!r} stdout={r.stdout[-300:]!r}")
    return r


def hpez_commands(exe: str, host: str, block: int, shape, ptp: float, tol: float, src, cmp, dst, cfg):
    dims = fastest_first(shape)
    comp = [exe, "-q", QPET_LEVEL[host], "-f", "-i", str(src), "-z", str(cmp), "-3", *dims,
            "-M", "ABS", repr(float(ptp)), "-c", str(cfg), "-m", "ABS", "-e", repr(float(tol))]
    deco = [exe, "-f", "-z", str(cmp), "-o", str(dst), "-3", *dims]
    return comp, deco


def sperr_commands(exe: str, block: int, shape, ptp: float, tol: float, src, cmp, dst):
    comp = [exe, "-c", str(src), "--ftype", "64", "--dims", *fastest_first(shape), "--bitstream", str(cmp),
            "--pwe", repr(float(ptp)), "--qoi_id", "14", "--qoi_string", "x", "--qoi_bs", str(int(block)),
            "--qoi_tol", repr(float(tol))]
    deco = [exe, "-d", str(cmp), "--decomp_d", str(dst)]
    return comp, deco


def qpet_roundtrip(x: np.ndarray, tol: float, host: str, block: int, ptp: float, td: Path):
    """Compress x with a QPET host at QoI (block-average) tolerance `tol`; return (decoded float64, file bytes)."""
    td = Path(td)
    cmp = td / "q.stream"
    if host in QPET_LEVEL:
        exe = _exe("HBMQ_HPEZ", "hpez")
        src = td / "q_in.f32"; dst = td / "q_rec.f32"; cfg = td / f"qoi_b{int(block)}.config"
        cfg.write_text(qpet_sz_config(block), encoding="utf-8")
        np.ascontiguousarray(x, dtype="<f4").tofile(src)   # the authors' hpez CLI compiles only the float32 path
        comp, deco = hpez_commands(exe, host, block, x.shape, ptp, tol, src, cmp, dst, cfg)
        dtype = "<f4"
    elif host == "sperr":
        exe = _exe("HBMQ_SPERR3D", "sperr3d")
        src = td / "q_in.f64"; dst = td / "q_rec.f64"
        np.ascontiguousarray(x, dtype="<f8").tofile(src)
        comp, deco = sperr_commands(exe, block, x.shape, ptp, tol, src, cmp, dst)
        dtype = "<f8"
    else:
        raise ValueError(f"unknown QPET host {host!r}")
    for f in (cmp, dst):
        f.unlink(missing_ok=True)
    try:
        _run(comp)
        if not cmp.exists():
            raise RuntimeError("compressor wrote no stream")
        nbytes = cmp.stat().st_size
        _run(deco)
        rec = np.fromfile(dst, dtype=dtype)
        if rec.size != x.size:
            raise RuntimeError(f"decoded size {rec.size} != {x.size}")
        rec = rec.reshape(x.shape).astype(np.float64)
        if not np.all(np.isfinite(rec)):
            raise RuntimeError("non-finite decoded values")
        return rec, int(nbytes)
    finally:
        for f in (src, cmp, dst, td / "q_in.f32.qoz.tmp"):
            f.unlink(missing_ok=True)


def block_means(a: np.ndarray, block: int) -> np.ndarray:
    """Means over block^3 cubes aligned at index 0 (partial cubes at the upper ends), as in QPET."""
    a = np.asarray(a, dtype=np.float64)
    for ax in range(a.ndim):
        idx = np.arange(0, a.shape[ax], block)
        s = np.add.reduceat(a, idx, axis=ax)
        cnt = np.diff(np.append(idx, a.shape[ax])).astype(np.float64)
        shp = [1] * a.ndim; shp[ax] = -1
        a = s / cnt.reshape(shp)
    return a
