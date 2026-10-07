#!/usr/bin/env python3
"""Toolchain probe on tiny synthetic arrays (no cohort material): MGARD smoothness acceptance including s = -2,
and a roundtrip of every QPET configuration with a block-average check. See PROTOCOL.md, "Feasibility probes"."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import codecs_mq as C  # noqa: E402


def mgard_tiny(td: Path) -> dict:
    """The SI Note 2.4 probe (16^3 standard normal, seed 0, tolerance 0.01), extended to s = -2."""
    out = {}
    exe = shutil.which("mgard")
    x = np.random.default_rng(0).normal(size=(16, 16, 16)); src = td / "in.dat"; x.tofile(src)
    for s in C.MGARD_S:
        o = td / "o.mgard"; r_ = td / "r.dat"
        for f in (o, r_):
            f.unlink(missing_ok=True)
        d = {"cli": exe}
        if exe is None:
            d |= {"feasible": False, "error": "mgard CLI not found"}
            out[s] = d; continue
        c = subprocess.run([exe, "compress", "--datatype", "double", "--shape", "16x16x16", "--smoothness", s,
                            "--tolerance", "0.01", "--input", str(src), "--output", str(o)], capture_output=True, text=True)
        d |= {"compress_rc": c.returncode, "compress_stdout": c.stdout[-600:], "compress_stderr": c.stderr[-600:]}
        if c.returncode == 0:
            dd = subprocess.run([exe, "decompress", "--input", str(o), "--output", str(r_)], capture_output=True, text=True)
            d |= {"decompress_rc": dd.returncode, "decompress_stderr": dd.stderr[-600:]}
            if dd.returncode == 0 and r_.exists():
                y = np.fromfile(r_)
                d |= {"decoded_size_ok": bool(y.size == x.size), "finite": bool(np.all(np.isfinite(y))),
                      "Linf": float(np.max(np.abs(y - x.ravel()))) if y.size == x.size else None,
                      "bytes": int(o.stat().st_size)}
        d["feasible"] = bool(d.get("compress_rc") == 0 and d.get("decompress_rc") == 0 and d.get("decoded_size_ok")
                             and d.get("finite"))
        out[s] = d
    return out


def smooth_field(shape=(48, 56, 72)) -> np.ndarray:
    i, j, k = np.meshgrid(*[np.arange(n) for n in shape], indexing="ij")
    f = (np.sin(2 * np.pi * i / shape[0]) + 0.5 * np.cos(2 * np.pi * 2 * j / shape[1]) * np.sin(2 * np.pi * k / shape[2])
         + 0.3 * np.cos(2 * np.pi * 3 * k / shape[2]))
    return f + 0.01 * np.random.default_rng(1).normal(size=shape)


def mgard_smooth(td: Path) -> dict:
    x = smooth_field(); ptp = float(np.ptp(x)); out = {}
    for s in C.MGARD_S:
        try:
            rec, nb = C.mgard_roundtrip(x, 1e-3 * ptp, s, td)
            out[s] = {"ok": True, "bytes": nb, "Linf_rel": float(np.max(np.abs(rec - x)) / ptp)}
        except Exception as exc:
            out[s] = {"ok": False, "error": f"{type(exc).__name__}: {getattr(exc, 'stderr', None) or exc}"[:600]}
    return out


def qpet(td: Path) -> dict:
    """Every QPET configuration at QoI tolerance t = 1e-3 ptp on a non-cubic 48 x 56 x 72 smooth array (axis-order check:
    the block averages are evaluated in numpy on the C-order axes)."""
    x = smooth_field(); ptp = float(np.ptp(x)); t = 1e-3 * ptp; out = {}
    for h in C.QPET_HOSTS:
        for b in C.QPET_BLOCKS:
            lab = f"Q_{h}_b{b}"
            try:
                rec, nb = C.qpet_roundtrip(x, t, h, b, ptp, td)
                e = rec - x
                be = float(np.max(np.abs(C.block_means(e, b))))
                out[lab] = {"ok": True, "bytes": nb, "cr": x.nbytes / nb, "pointwise_Linf_over_t": float(np.max(np.abs(e)) / t),
                            "block_avg_maxerr_over_t": be / t, "block_avg_within_t": bool(be <= t * (1 + 1e-6) + 1e-7 * ptp)}
            except Exception as exc:
                out[lab] = {"ok": False, "error": f"{type(exc).__name__}: {exc}"[:600]}
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--output-dir", type=Path, required=True)
    a = ap.parse_args(); a.output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="hbmq_probe_") as tds:
        td = Path(tds)
        res = {"mgard_tiny": mgard_tiny(td), "mgard_smooth": mgard_smooth(td), "qpet": qpet(td)}
    res["m2_feasible"] = res["mgard_tiny"]["-2"]["feasible"]
    res["qpet_configs_feasible"] = sorted(k for k, v in res["qpet"].items() if v.get("ok"))
    (a.output_dir / "probe.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    lines = [f"MGARD s={s}: feasible={d['feasible']} rc=({d.get('compress_rc')},{d.get('decompress_rc')}) Linf={d.get('Linf')} "
             f"stderr={d.get('compress_stderr', d.get('error', ''))!r}" for s, d in res["mgard_tiny"].items()]
    lines += [f"MGARD smooth s={s}: {d}" for s, d in res["mgard_smooth"].items()]
    lines += [f"{k}: {v}" for k, v in res["qpet"].items()]
    (a.output_dir / "probe_summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
