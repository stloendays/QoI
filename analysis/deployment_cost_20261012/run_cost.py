#!/usr/bin/env python3
"""Deployment cost of certified Hartree compression: encode time, certified-search time, decode time, peak memory
and retrieval cost for the arms of Fig. 5, on the P1 and P3b cohorts; see PROTOCOL.md.

Every certified stream is regenerated from the parameter recorded in the committed results (law run and MGARD/QPET
run), decoded, and its Hartree certificate recomputed. Each measured operation runs in its own fresh Python process
(single thread), so the peak resident set of that process belongs to that operation alone.

Orchestrator:  run_cost.py --repo-root R --frozen-root F --manifest M --cache-dir C --output-dir O --only ID
Child (internal): run_cost.py --child JSON
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
import traceback
import zlib
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ANALYSIS = HERE.parent
for sub in ("qoac_h_strong_baselines", "hartree_baselines_mgard_qpet_20261007", "operator_aware_codec_hartree_v02",
            "qoac_v03_rdo"):                 # last inserted wins: run_engineering must resolve to qoac_v03_rdo
    sys.path.insert(0, str(ANALYSIS / sub))

TAUS = (1e-4, 1e-6, 1e-8)
REPS = 5                       # timed repetitions of each one-shot encode/decode, after one warm-up
LAW = ANALYSIS / "general_qoac_law" / "results"
MQ = ANALYSIS / "hartree_baselines_mgard_qpet_20261007" / "results"
COHORT_OF = {"fresh_p1_confirmatory": "P1_CONFIRMATORY", "fresh_p3b_confirmatory": "P3B_CONFIRMATORY"}
ONE_THREAD = {k: "1" for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
                               "VECLIB_MAXIMUM_THREADS", "NUMBA_NUM_THREADS")}


# ----------------------------------------------------------------------------------------------- memory and time
def peak_rss_bytes() -> int:
    """High-water resident set of this process (Linux ru_maxrss in KiB; Windows PeakWorkingSetSize)."""
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        class PMC(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t)]
        c = PMC(); c.cb = ctypes.sizeof(PMC)
        k32, psapi = ctypes.WinDLL("kernel32"), ctypes.WinDLL("psapi")
        k32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
        if not psapi.GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(c), c.cb):
            raise OSError("GetProcessMemoryInfo failed")
        return int(c.PeakWorkingSetSize)
    import resource
    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024


def reset_peak_rss() -> int:
    """Reset this process's resident-set high-water mark where the kernel allows it (Linux clear_refs = 5) and
    return the current resident set; elsewhere return the current high-water mark (no reset)."""
    status = Path("/proc/self/status")
    if status.exists():
        try:
            Path("/proc/self/clear_refs").write_text("5")
            for line in status.read_text().splitlines():
                if line.startswith("VmRSS:"):
                    return int(line.split()[1]) * 1024
        except OSError:
            pass
    return peak_rss_bytes()


def current_peak_rss() -> int:
    status = Path("/proc/self/status")
    if status.exists():
        for line in status.read_text().splitlines():
            if line.startswith("VmHWM:"):
                return int(line.split()[1]) * 1024
    return peak_rss_bytes()


def run_cli(cmd: list[str]) -> tuple[float, int | None]:
    """Run a codec CLI; return (wall seconds, peak RSS bytes of that process or None if not measurable)."""
    with tempfile.TemporaryFile() as errf:          # a file, not a pipe: wait4 must not block on a full pipe
        t0 = time.perf_counter()
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=errf)
        if hasattr(os, "wait4"):
            _, status, ru = os.wait4(p.pid, 0)
            wall = time.perf_counter() - t0
            p.returncode = rc = os.waitstatus_to_exitcode(status)
            peak = int(ru.ru_maxrss) * 1024
        else:
            p.wait()
            wall = time.perf_counter() - t0
            rc, peak = p.returncode, None
        errf.seek(0); err = errf.read().decode(errors="replace")
    if rc != 0:
        raise RuntimeError(f"{Path(cmd[0]).name} rc={rc} stderr={err[-300:]!r}")
    return wall, peak


# ----------------------------------------------------------------------------------------------- codecs
sys.path.insert(0, str(HERE))
import fast_codec as F  # noqa: E402
import importlib.util as _ilu  # noqa: E402
# several analysis folders define run_engineering.py; the arms' search is the qoac_v03_rdo one (also for run_mq)
_spec = _ilu.spec_from_file_location("run_engineering", ANALYSIS / "qoac_v03_rdo" / "run_engineering.py")
sys.modules["run_engineering"] = _eng = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_eng)


def lazy():
    import codec_qoac_h_v02 as v02
    import codec_qoac_v03 as v3
    return v02, v3


def law_refs(prep, rh):
    """Spectral reference energies of the Hartree certificate, as computed by codec_qoac_v03.analyze."""
    v02, v3 = lazy()
    topo = prep.topology
    w = v3.operator_weight(topo, "hartree_potential")
    safe = ~v3.nyquist_orbits(topo)
    m = np.where(topo.self_conjugate, 1.0, 2.0)
    c = prep.spectrum.ravel()[topo.rep_flat]
    cr = c.real; ci = np.where(topo.self_conjugate, 0.0, c.imag)
    ref_safe = float(np.sum((m * w * (cr * cr + ci * ci))[safe]))
    ref_cons = prep.field.size * rh ** 2 / (4 * math.pi) ** 2 / topo.g2_safe_max ** -2
    return ref_cons, ref_safe


def pointwise_encode(codec: str, x: np.ndarray, tol: float, work: Path) -> bytes | Path:
    if codec == "zfp":
        import zfpy
        return zfpy.compress_numpy(x, tolerance=tol)
    if codec == "sz3":
        from pysz import sz, szConfig, szErrorBoundMode
        cfg = szConfig(); cfg.errorBoundMode = szErrorBoundMode.ABS; cfg.absErrorBound = float(tol)
        comp, _ = sz.compress(x, cfg)
        return np.asarray(comp).tobytes()
    if codec == "sperr":
        import h5py, hdf5plugin
        h5path = work / "sperr.h5"
        with h5py.File(h5path, "w") as h5:
            h5.create_dataset("density", data=x, chunks=x.shape, **hdf5plugin.Sperr(absolute=float(tol)))
        return h5path
    raise ValueError(codec)


def pointwise_bytes(codec: str, stream) -> int:
    if codec == "sperr":
        import h5py, hdf5plugin  # noqa: F401
        with h5py.File(stream, "r") as h5:
            return int(h5["density"].id.get_storage_size())
    return len(stream)


def pointwise_decode(codec: str, stream, shape) -> np.ndarray:
    if codec == "zfp":
        import zfpy
        return np.asarray(zfpy.decompress_numpy(stream), dtype=np.float64)
    if codec == "sz3":
        from pysz import sz
        rec, _ = sz.decompress(np.frombuffer(stream, dtype=np.uint8), np.float64, tuple(shape))
        return np.asarray(rec, dtype=np.float64)
    if codec == "sperr":
        import h5py, hdf5plugin  # noqa: F401
        with h5py.File(stream, "r") as h5:
            return np.asarray(h5["density"][()], dtype=np.float64)
    raise ValueError(codec)


# ----------------------------------------------------------------------------------------------- child operations
def certify(rec, x, lat, rh, rs):
    v02, _ = lazy()
    return v02.hartree_error_metrics(rec - x, lat, rh, rs)


def timed(fn, reps=REPS):
    fn()                                                    # warm-up (imports, caches, page faults)
    ts = []
    for _ in range(reps):
        t0 = time.perf_counter(); out = fn(); ts.append(time.perf_counter() - t0)
    return out, ts


def child(job: dict) -> dict:
    """One operation in a fresh process. Returns timings, peak RSS above the loaded-input baseline, stream bytes."""
    v02, v3 = lazy()
    work = Path(job["work"])
    x = np.load(work / "rho.npy")
    info = json.loads((work / "info.json").read_text())
    lat = np.asarray(info["lattice"]); rh, rs, ptp = info["rh"], info["rs"], info["ptp"]
    arm, tau, op, p = job["arm"], job["tau"], job["op"], job["param"]
    stream_path = work / f"stream_{arm}_{tau:g}.bin"
    res = {"arm": arm, "tau": tau, "op": op}
    for mod in ("zfpy", "pysz", "h5py", "hdf5plugin", "zstandard"):   # imports are not part of an operation's memory
        try:
            __import__(mod)
        except ImportError:
            pass
    cli_peak = cli_base = None
    if arm in ("M2", "Q") and op in ("encode", "decode") and hasattr(os, "wait4"):
        cli_base = cli_baseline(arm, p, op)
    rss0 = reset_peak_rss()

    if op == "encode":
        if arm == "A1":                                     # production implementation (byte-identical stream)
            def f():
                return F.encode_law(x, lat, p["alpha_rel"] * ptp)
        elif arm == "A1ref":                                # reference implementation of the committed runs
            def f():
                prep = v02.prepare_field(x, lat, shell_count=32)
                return v02.encode_prepared(prep, alpha=p["alpha_rel"] * ptp, beta=2.0, zlib_level=6)[0]
        elif arm in ("A3", "A3ref"):                        # one implementation: the RD analysis is the encoder
            def f():
                an = v3.analyze(x, lat, prior="operator", reference_historical_rms=rh, d_floor_rel=1e-3 * min(TAUS) ** 2 / 32)
                return v3.encode(an, v3.select(an, tau, margin=p["margin"], polish=True))
        elif arm == "A6":
            def f():
                return pointwise_encode(p["codec"], x, p["abs_tol_rel"] * ptp, work)
        elif arm in ("L_zlib", "L_zstd"):
            def f():
                if arm == "L_zlib":
                    return zlib.compress(x.tobytes(), 6)
                import zstandard
                return zstandard.ZstdCompressor(level=3).compress(x.tobytes())
        elif arm in ("M2", "Q"):
            walls, peaks = [], []
            def f():
                comp, src = cli_commands(arm, p, x, ptp, work, stream_path)
                t0 = time.perf_counter(); write_input(arm, p, x, src); tw = time.perf_counter() - t0
                wall, pk = run_cli(comp); walls.append((tw, wall)); peaks.append(pk)
                return stream_path
        else:
            raise ValueError(arm)
        out, ts = timed(f)
        rss_op = current_peak_rss()
        if arm == "A6" and p["codec"] == "sperr":
            shutil.copyfile(out, stream_path); nbytes = pointwise_bytes("sperr", out)
        elif arm in ("M2", "Q"):
            nbytes = stream_path.stat().st_size
            res["input_write_seconds"] = statistics.median(w[0] for w in walls[1:])
            res["cli_seconds"] = statistics.median(w[1] for w in walls[1:])
            cli_peak = max((k for k in peaks if k), default=None)
        else:
            stream_path.write_bytes(out); nbytes = len(out)
        res["bytes"] = int(nbytes)

    elif op == "decode":
        if arm in ("M2", "Q"):
            walls, peaks = [], []
            def f():
                deco, dst, dtype = cli_decode_commands(arm, p, x, work, stream_path)
                wall, pk = run_cli(deco)
                t0 = time.perf_counter(); rec = np.fromfile(dst, dtype=dtype).reshape(x.shape).astype(np.float64)
                walls.append((wall, time.perf_counter() - t0)); peaks.append(pk)
                return rec
        else:
            blob = stream_path.read_bytes() if not (arm == "A6" and p["codec"] == "sperr") else stream_path
            if arm == "A1":
                def f(): return F.decode_law(blob)
            elif arm == "A1ref":
                def f(): return v02.decode_blob(blob)[0]
            elif arm == "A3":
                def f(): return F.decode_operational(blob)
            elif arm == "A3ref":
                def f(): return v3.decode(blob)
            elif arm == "A6":
                def f(): return pointwise_decode(p["codec"], blob, x.shape)
            elif arm == "L_zlib":
                def f(): return np.frombuffer(zlib.decompress(blob), dtype=np.float64).reshape(x.shape)
            elif arm == "L_zstd":
                import zstandard
                def f(): return np.frombuffer(zstandard.ZstdDecompressor().decompress(blob), dtype=np.float64).reshape(x.shape)
            else:
                raise ValueError(arm)
        rec, ts = timed(f)
        rss_op = current_peak_rss()                         # before the certificate, which is not part of decoding
        if arm in ("M2", "Q"):
            res["cli_seconds"] = statistics.median(w[0] for w in walls[1:])
            res["output_read_seconds"] = statistics.median(w[1] for w in walls[1:])
            cli_peak = max((k for k in peaks if k), default=None)
        eh, es = certify(rec, x, lat, rh, rs)
        res |= {"hartree_hist": eh, "hartree_safe": es, "certified": bool(eh < tau and es < tau),
                "max_abs_dev": float(np.max(np.abs(rec - x)))}

    elif op == "search":
        t0 = time.perf_counter()
        res |= search(arm, tau, x, lat, rh, rs, ptp, work)
        ts = [time.perf_counter() - t0]
    else:
        raise ValueError(op)

    rss1 = rss_op if op in ("encode", "decode") else current_peak_rss()
    res |= {"seconds_median": statistics.median(ts), "seconds_min": min(ts), "seconds_all": ts,
            "peak_rss_bytes": rss1, "baseline_rss_bytes": rss0, "peak_rss_above_input_bytes": max(0, rss1 - rss0),
            "cli_peak_rss_bytes": cli_peak, "cli_baseline_rss_bytes": cli_base,
            "cli_peak_above_baseline_bytes": (max(0, cli_peak - cli_base) if cli_peak and cli_base else None),
            "raw_bytes": int(x.nbytes)}
    return res


def cli_baseline(arm, p, op) -> int | None:
    """Peak resident set of the same codec program on a 16^3 field: its fixed footprint, subtracted from its peak."""
    rng = np.random.default_rng(0)
    xt = 1.0 + 0.01 * rng.random((16, 16, 16))
    with tempfile.TemporaryDirectory(prefix="clibase_") as td:
        td = Path(td); sp = td / "s.bin"
        comp, src = cli_commands(arm, p, xt, float(np.ptp(xt)), td, sp)
        write_input(arm, p, xt, src)
        _, pe = run_cli(comp)
        if op == "encode":
            return pe
        deco, _, _ = cli_decode_commands(arm, p, xt, td, sp)
        return run_cli(deco)[1]


# MGARD / QPET command lines are those of the committed baseline run (codecs_mq.py, run_baselines.mgard_roundtrip).
def cli_commands(arm, p, x, ptp, work, stream_path):
    import codecs_mq as C
    if arm == "M2":
        src = work / "m_in.dat"
        cmd = [shutil.which("mgard"), "compress", "--datatype", "double", "--shape", "x".join(map(str, x.shape)),
               "--smoothness", "-2", "--tolerance", repr(float(p["tol_rel"] * ptp)), "--input", str(src),
               "--output", str(stream_path)]
        return cmd, src
    host, block, tol = p["host"], p["block"], p["tol_rel"] * ptp
    if host in C.QPET_LEVEL:
        src = work / "q_in.f32"; cfg = work / f"qoi_b{block}.config"
        cfg.write_text(C.qpet_sz_config(block), encoding="utf-8")
        comp, _ = C.hpez_commands(C._exe("HBMQ_HPEZ", "hpez"), host, block, x.shape, ptp, tol, src, stream_path,
                                  work / "q_rec.f32", cfg)
    else:
        src = work / "q_in.f64"
        comp, _ = C.sperr_commands(C._exe("HBMQ_SPERR3D", "sperr3d"), block, x.shape, ptp, tol, src, stream_path,
                                   work / "q_rec.f64")
    return comp, src


def write_input(arm, p, x, src):
    dtype = "<f4" if arm == "Q" and p["host"] != "sperr" else "<f8"    # hpez CLI compiles only the float32 path
    np.ascontiguousarray(x, dtype=dtype).tofile(src)


def cli_decode_commands(arm, p, x, work, stream_path):
    import codecs_mq as C
    if arm == "M2":
        dst = work / "m_rec.dat"
        return [shutil.which("mgard"), "decompress", "--input", str(stream_path), "--output", str(dst)], dst, "<f8"
    if p["host"] in C.QPET_LEVEL:
        dst = work / "q_rec.f32"
        _, deco = C.hpez_commands(C._exe("HBMQ_HPEZ", "hpez"), p["host"], p["block"], x.shape, 1.0, 1.0,
                                  work / "q_in.f32", stream_path, dst, work / "unused.config")
        return deco, dst, "<f4"
    dst = work / "q_rec.f64"
    _, deco = C.sperr_commands(C._exe("HBMQ_SPERR3D", "sperr3d"), p["block"], x.shape, 1.0, 1.0,
                               work / "q_in.f64", stream_path, dst)
    return deco, dst, "<f8"


# ----------------------------------------------------------------------------------------------- certified search
def search(arm, tau, x, lat, rh, rs, ptp, work) -> dict:
    """The arm's complete certified compression from the raw field: the same search the committed run used,
    ending with a decoded certificate. Reports the chosen parameter and bytes for comparison with the record."""
    v02, v3 = lazy()
    import run_engineering as eng
    if arm == "A1":
        prep = F.prepare_field(x, lat)
        ref_cons, ref_safe = law_refs(prep, rh)
        S = eng.Spec(prep, ref_cons, ref_safe); q2 = prep.topology.q ** 2
        a = eng.bisect_scale(lambda s: S.ok(s * q2, tau), 1e-14 * ptp, 1e3 * ptp)
        for _ in range(40):
            blob, _ = v02.encode_prepared(prep, alpha=a, beta=2.0, zlib_level=6)
            eh, es = certify(F.decode_law(blob), x, lat, rh, rs)
            if eh < tau and es < tau:
                return {"param": f"alpha_rel={a / ptp:.9g}", "bytes": len(blob), "evaluations": 1}
            a *= 0.99
        return {"param": "", "bytes": None}
    if arm == "A3":
        an = v3.analyze(x, lat, prior="operator", reference_historical_rms=rh, d_floor_rel=1e-3 * min(TAUS) ** 2 / 32)
        mg = eng.MARGIN
        for _ in range(20):
            b3 = v3.encode(an, v3.select(an, tau, margin=mg, polish=True))
            eh, es = certify(F.decode_operational(b3), x, lat, rh, rs)
            if eh < tau and es < tau:
                return {"param": f"margin={mg:.4f}", "bytes": len(b3)}
            mg *= 0.995
        return {"param": "", "bytes": None}
    if arm == "A6":                       # best of three pointwise codecs: all three are searched
        best, per = None, {}
        for codec in ("zfp", "sz3", "sperr"):
            t0 = time.perf_counter(); seen = {}
            def ok(t):
                s = pointwise_encode(codec, x, float(t), work)
                nb = pointwise_bytes(codec, s); rec = pointwise_decode(codec, s, x.shape)
                eh, es = certify(rec, x, lat, rh, rs); good = eh < tau and es < tau
                if good: seen[t] = nb
                return good
            eng.bisect_scale(ok, 1e-14 * ptp, 1.0 * ptp)
            per[codec] = time.perf_counter() - t0
            if seen:
                t = max(seen, key=lambda k: -seen[k])
                if best is None or seen[t] < best[2]: best = (codec, t, seen[t])
        return {"param": f"codec={best[0]};abs_tol_rel={best[1] / ptp:.9g}" if best else "",
                "bytes": best[2] if best else None, "per_codec_seconds": per}
    if arm in ("M2", "Q"):                # M2: MGARD s=-2; Q: best of the nine QPET configurations
        import run_mq as R
        import codecs_mq as C
        cfgs = [("M", "M_s=-2", {"s": "-2"})] if arm == "M2" else R.configs({"Q"})
        best, per = None, {}
        for a, label, cfg in cfgs:
            t0 = time.perf_counter(); cache = {}
            td = work / f"search_{label}"; td.mkdir(exist_ok=True)
            def ev(t):
                t = float(t)
                if t not in cache:
                    try:
                        rec, nb = (C.mgard_roundtrip(x, t, cfg["s"], td) if a == "M"
                                   else C.qpet_roundtrip(x, t, cfg["host"], cfg["block"], ptp, td))
                        eh, es = certify(rec, x, lat, rh, rs)
                        cache[t] = {"bytes": int(nb), "hartree_hist": eh, "hartree_safe": es}
                    except Exception:
                        cache[t] = None
                return cache[t]
            lo, hi = R.INTERVAL[a]
            bt, seen, _ = R.search(ev, tau, lo * ptp, hi * ptp, R.LO_ERROR_CAP * ptp)
            per[label] = time.perf_counter() - t0
            if bt is not None and (best is None or seen[bt]["bytes"] < best[2]):
                best = (label, bt, seen[bt]["bytes"])
        return {"param": f"{best[0]};tol_rel={best[1] / ptp:.9g}" if best else "", "bytes": best[2] if best else None,
                "per_config_seconds": per}
    raise ValueError(arm)


# ----------------------------------------------------------------------------------------------- recorded parameters
def recorded(cohort: str, mid: str) -> dict:
    """Certified parameters recorded by the committed runs, per (arm, tau)."""
    out = {}
    with open(LAW / f"run_{cohort}" / "part_a_rows.csv", encoding="utf-8") as f:
        law = [r for r in csv.DictReader(f) if r["material_id"] == mid and r["certified"] == "True"]
    with open(MQ / f"run_{cohort}" / "rows.csv", encoding="utf-8") as f:
        mq = [r for r in csv.DictReader(f) if r["material_id"] == mid and r["certified"] == "True"]
    for tau in TAUS:
        rows = [r for r in law if float(r["tau"]) == tau]
        def best(arm):
            c = [r for r in rows if r["arm"] == arm]
            return min(c, key=lambda r: int(r["bytes"])) if c else None
        for arm in ("A1", "A3", "A6"):
            r = best(arm)
            if r is None:
                continue
            kv = dict(s.split("=", 1) for s in r["param"].split(";"))
            p = {"bytes": int(r["bytes"])}
            if arm == "A1": p["alpha_rel"] = float(kv["alpha_rel"])
            if arm == "A3": p["margin"] = float(kv["margin"])
            if arm == "A6": p |= {"codec": kv["codec"], "abs_tol_rel": float(kv["abs_tol_rel"])}
            out[(arm, tau)] = p
            if arm in ("A1", "A3"):
                out[(arm + "ref", tau)] = dict(p)
        m = [r for r in mq if float(r["tau"]) == tau and r["config"] == "M_s=-2"]
        if m:
            out[("M2", tau)] = {"bytes": int(m[0]["bytes"]), "tol_rel": float(m[0]["param"].split("tol_rel=")[1])}
        q = [r for r in mq if float(r["tau"]) == tau and r["arm"] == "Q"]
        if q:
            r = min(q, key=lambda r: int(r["bytes"]))
            _, host, b = r["config"].split("_")
            out[("Q", tau)] = {"bytes": int(r["bytes"]), "host": host, "block": int(b[1:]),
                               "tol_rel": float(r["param"].split("tol_rel=")[1]), "config": r["config"]}
    return out


# ----------------------------------------------------------------------------------------------- orchestration
def calibration() -> dict:
    """Fixed micro-benchmark per runner so that machines can be compared: FFT, zlib and memory bandwidth."""
    rng = np.random.default_rng(0)
    a = rng.standard_normal((96, 96, 96))
    _, t_fft = timed(lambda: np.fft.fftn(a), 5)
    b = (rng.integers(0, 64, 16_000_000, dtype=np.int64)).astype(np.int8).tobytes()
    _, t_z = timed(lambda: zlib.compress(b, 6), 3)
    c = np.ones(50_000_000)
    _, t_m = timed(lambda: c.copy(), 3)
    cpu = ""
    if Path("/proc/cpuinfo").exists():
        cpu = next((l.split(":", 1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")), "")
    return {"cpu": cpu or platform.processor(), "nproc": os.cpu_count(), "python": sys.version.split()[0],
            "numpy": np.__version__, "fft96_s": statistics.median(t_fft), "zlib16MB_s": statistics.median(t_z),
            "copy400MB_s": statistics.median(t_m)}


def spawn(job: dict) -> dict:
    env = os.environ | ONE_THREAD
    r = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--child", json.dumps(job)],
                       capture_output=True, text=True, env=env, timeout=7200)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-1500:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def material(meta: dict, a) -> tuple[list, list, dict]:
    sys.path.insert(0, str(a.frozen_root.resolve() / "validation"))
    sys.path.insert(0, str(a.repo_root.resolve() / "validation" / "qsq_prospective"))
    import development_compatibility_smoke as dev
    mid = meta["material_id"]; cohort = "P3B_CONFIRMATORY" if "P3B" in a.manifest.name else "P1_CONFIRMATORY"
    rows, fails = [], []
    info = {"material_id": mid, "cohort": cohort, "system_type": meta["system_type"],
            "source_bytes": int(meta["source_bytes"]), "calibration": calibration()}
    cp = a.cache_dir / f"{mid}.src"
    if cp.exists() and hashlib.sha256(cp.read_bytes()).hexdigest() == meta["sha256"]:
        blob = cp.read_bytes(); info["source_download_seconds"] = None
    else:
        t0 = time.perf_counter(); blob = dev.fetch_exact(meta["url"], meta["sha256"], int(meta["source_bytes"]))
        info["source_download_seconds"] = time.perf_counter() - t0; cp.write_bytes(blob)
    work = Path(tempfile.mkdtemp(prefix=f"cost_{mid}_"))
    try:
        # current-archive retrieval: source bytes -> float64 field, with the project's loader (timed, 3 repetitions)
        ts = []
        for _ in range(3):
            with tempfile.TemporaryDirectory() as td:
                t0 = time.perf_counter(); grid, loader = dev.build_grid(meta, blob, Path(td))
                x = np.ascontiguousarray(np.asarray(grid.total, dtype=np.float64)); ts.append(time.perf_counter() - t0)
        lat = np.asarray(grid.structure.lattice.matrix, float)
        v02, _ = lazy()
        rh, rs = v02.reference_hartree_rms(x, lat)
        info |= {"loader": loader, "shape": list(x.shape), "npoints": int(x.size), "raw_bytes": int(x.nbytes),
                 "source_parse_seconds_median": statistics.median(ts), "source_parse_seconds_all": ts}
        np.save(work / "rho.npy", x)
        (work / "info.json").write_text(json.dumps({"lattice": lat.tolist(), "rh": rh, "rs": rs, "ptp": float(np.ptp(x))}))
        rec = recorded(cohort, mid)
        plan = [(arm, tau) for tau in TAUS for arm in ("A1", "A1ref", "A3", "A3ref", "A6", "M2", "Q")
                if (arm, tau) in rec]
        plan += [("L_zlib", 0.0), ("L_zstd", 0.0)]
        for arm, tau in plan:
            p = rec.get((arm, tau), {})
            for op in ("encode", "decode", "search"):
                if arm.startswith("L_") and op == "search":
                    continue
                if op == "search" and (a.skip_search or arm.endswith("ref")):
                    continue
                if op == "search" and tau != 1e-6 and not a.search_all_taus:
                    continue
                t0 = time.time()
                try:
                    r = spawn({"work": str(work), "arm": arm, "tau": tau, "op": op, "param": p})
                    r |= {"material_id": mid, "cohort": cohort, "system_type": meta["system_type"],
                          "recorded_bytes": p.get("bytes"), "recorded_param": json.dumps(p)}
                    rows.append(r)
                    print(f"COST {mid} {arm} tau={tau:g} {op} {r['seconds_median']:.3f}s bytes={r.get('bytes')} "
                          f"cert={r.get('certified')} ({time.time() - t0:.0f}s)", flush=True)
                except Exception as exc:
                    fails.append({"material_id": mid, "arm": arm, "tau": tau, "op": op, "error": str(exc)[-800:]})
                    print(f"COST_FAIL {mid} {arm} {tau:g} {op}: {str(exc)[-300:]}", flush=True)
    except Exception:
        fails.append({"material_id": mid, "arm": "material", "tau": "", "op": "", "error": traceback.format_exc()[-800:]})
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return rows, fails, info


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--child")
    p.add_argument("--repo-root", type=Path); p.add_argument("--frozen-root", type=Path)
    p.add_argument("--manifest", type=Path); p.add_argument("--cache-dir", type=Path)
    p.add_argument("--output-dir", type=Path); p.add_argument("--only", default="")
    p.add_argument("--skip-search", action="store_true"); p.add_argument("--search-all-taus", action="store_true")
    a = p.parse_args()
    if a.child:
        print(json.dumps(child(json.loads(a.child))))
        return 0
    a.output_dir.mkdir(parents=True, exist_ok=True); a.cache_dir.mkdir(parents=True, exist_ok=True)
    man = list(csv.DictReader(open(a.manifest, encoding="utf-8")))
    if a.only:
        man = [m for m in man if m["material_id"] in a.only.split(",")]
    for meta in man:
        rows, fails, info = material(meta, a)
        mid = meta["material_id"]
        with (a.output_dir / f"cost_{mid}.jsonl").open("w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        (a.output_dir / f"info_{mid}.json").write_text(json.dumps(info, indent=2), encoding="utf-8")
        (a.output_dir / f"failures_{mid}.json").write_text(json.dumps(fails, indent=2), encoding="utf-8")
        print(f"COST_DONE {mid} rows={len(rows)} failures={len(fails)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
