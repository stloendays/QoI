#!/usr/bin/env python3
"""File-backed base codecs and the pinned FFCz CPU command path.

The base-codec branches below are the file-backed equivalents of the frozen
``codec_roundtrip`` branches at QoI commit 893f931.  Compression and
decompression are deliberately separate Python processes: the decompressor is
given only the stream file, its shape, and its dtype.  FFCz itself writes a
prefix plus the five sidecar files used by the authors' CPU executable.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np


CALL_TIMEOUT = 1800
FFCZ_SUFFIXES = (".fedits", ".fflags", ".sedits", ".sflags", ".extreme")
FFCZ_AXIS_ORDER = "C-order shape (Nx, Ny, Nz) passed directly to -3"


class CodecExecutionError(RuntimeError):
    """A compressor, decompressor, or FFCz process did not produce a valid result."""


@dataclass(frozen=True)
class BaseArtifact:
    codec: str
    abs_bound: float
    shape: tuple[int, int, int]
    stream_path: Path
    decoded_path: Path
    stream_bytes: int
    stream_file_bytes: int


def _shape_text(shape: Sequence[int]) -> str:
    values = tuple(int(v) for v in shape)
    if len(values) != 3 or any(v <= 0 for v in values):
        raise ValueError(f"FFCz requires a positive 3-D shape, got {values!r}")
    return "x".join(str(v) for v in values)


def _shape_from_text(text: str) -> tuple[int, int, int]:
    values = tuple(int(v) for v in text.lower().split("x"))
    if len(values) != 3 or any(v <= 0 for v in values):
        raise ValueError(f"invalid shape {text!r}")
    return values


def _run_process(cmd: Sequence[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            [str(x) for x in cmd],
            cwd=str(cwd) if cwd is not None else None,
            capture_output=True,
            text=True,
            timeout=CALL_TIMEOUT,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise CodecExecutionError(
            f"timeout after {CALL_TIMEOUT}s: {' '.join(str(x) for x in cmd)}"
        ) from exc
    except OSError as exc:
        raise CodecExecutionError(f"could not execute {cmd[0]!r}: {exc}") from exc
    if result.returncode != 0:
        raise CodecExecutionError(
            f"{Path(str(cmd[0])).name} rc={result.returncode}; "
            f"stderr={result.stderr[-600:]!r}; stdout={result.stdout[-600:]!r}"
        )
    return result


def _raw_array(path: Path, shape: tuple[int, int, int]) -> np.ndarray:
    data = np.fromfile(path, dtype="<f8")
    expected = int(np.prod(shape))
    if data.size != expected:
        raise CodecExecutionError(f"raw input size {data.size} != {expected}")
    return np.ascontiguousarray(data.reshape(shape), dtype=np.float64)


def _write_raw(path: Path, array: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.ascontiguousarray(np.asarray(array, dtype="<f8")).tofile(path)


def _payload_bytes(compressed: Any) -> bytes:
    if isinstance(compressed, (bytes, bytearray, memoryview)):
        return bytes(compressed)
    return np.ascontiguousarray(np.asarray(compressed)).tobytes(order="C")


def _compress_impl(codec: str, input_path: Path, stream_path: Path, shape: tuple[int, int, int], abs_bound: float) -> dict[str, int]:
    """Run exactly the frozen base-codec settings in the compressor worker."""
    array = _raw_array(input_path, shape)
    stream_path.parent.mkdir(parents=True, exist_ok=True)
    stream_path.unlink(missing_ok=True)
    codec = codec.lower()

    if codec == "zfp":
        import zfpy

        compressed = zfpy.compress_numpy(array, tolerance=float(abs_bound))
        stream_path.write_bytes(_payload_bytes(compressed))
        logical_bytes = len(_payload_bytes(compressed))
    elif codec == "sz3":
        from pysz import sz, szConfig, szErrorBoundMode

        config = szConfig()
        config.errorBoundMode = szErrorBoundMode.ABS
        config.absErrorBound = float(abs_bound)
        compressed, _ratio = sz.compress(array, config)
        payload = _payload_bytes(compressed)
        stream_path.write_bytes(payload)
        logical_bytes = int(np.asarray(compressed).nbytes) if not isinstance(compressed, (bytes, bytearray, memoryview)) else len(payload)
    elif codec == "sperr":
        import h5py
        import hdf5plugin

        with h5py.File(stream_path, "w") as h5:
            dataset = h5.create_dataset(
                "density",
                data=array,
                chunks=array.shape,
                **hdf5plugin.Sperr(absolute=float(abs_bound)),
            )
            h5.flush()
            logical_bytes = int(dataset.id.get_storage_size())
    else:
        raise ValueError(f"unknown base codec {codec!r}")

    return {"stream_bytes": int(logical_bytes), "stream_file_bytes": int(stream_path.stat().st_size)}


def _decompress_impl(codec: str, stream_path: Path, output_path: Path, shape: tuple[int, int, int]) -> None:
    """Decode a stream without opening or consulting the original field."""
    codec = codec.lower()
    if codec == "zfp":
        import zfpy

        reconstructed = zfpy.decompress_numpy(stream_path.read_bytes())
    elif codec == "sz3":
        from pysz import sz

        raw = stream_path.read_bytes()
        attempts: list[Any] = [raw, np.frombuffer(raw, dtype=np.uint8)]
        last: Exception | None = None
        reconstructed = None
        for payload in attempts:
            try:
                reconstructed, _config = sz.decompress(payload, np.dtype("<f8").type, shape)
                break
            except Exception as exc:  # pysz versions differ on bytes vs uint8 input.
                last = exc
        if reconstructed is None:
            raise CodecExecutionError(f"SZ3 decompression failed: {last}") from last
    elif codec == "sperr":
        import h5py
        import hdf5plugin  # noqa: F401  registers the SPERR filter in this fresh process

        with h5py.File(stream_path, "r") as h5:
            reconstructed = h5["density"][()]
    else:
        raise ValueError(f"unknown base codec {codec!r}")

    result = np.asarray(reconstructed, dtype=np.float64)
    if result.size != int(np.prod(shape)):
        raise CodecExecutionError(f"decoded size {result.size} != {int(np.prod(shape))}")
    result = np.ascontiguousarray(result.reshape(shape), dtype="<f8")
    if not np.all(np.isfinite(result)):
        raise CodecExecutionError("base decoder returned non-finite values")
    result.tofile(output_path)


def _worker_main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("operation", choices=("base-compress", "base-decompress"))
    parser.add_argument("--codec", required=True)
    parser.add_argument("--shape", required=True)
    parser.add_argument("--input")
    parser.add_argument("--stream", required=True)
    parser.add_argument("--output")
    parser.add_argument("--abs-bound", type=float)
    args = parser.parse_args(list(argv))
    shape = _shape_from_text(args.shape)
    if args.operation == "base-compress":
        if not args.input or args.abs_bound is None:
            parser.error("base-compress requires --input and --abs-bound")
        result = _compress_impl(args.codec, Path(args.input), Path(args.stream), shape, args.abs_bound)
        print(json.dumps(result, sort_keys=True))
        return 0
    if not args.output:
        parser.error("base-decompress requires --output")
    _decompress_impl(args.codec, Path(args.stream), Path(args.output), shape)
    return 0


def _worker_cmd(operation: str, codec: str, shape: tuple[int, int, int], stream: Path, input_path: Path | None = None,
                output_path: Path | None = None, abs_bound: float | None = None) -> list[str]:
    cmd = [sys.executable, str(Path(__file__).resolve()), operation, "--codec", codec, "--shape", _shape_text(shape),
           "--stream", str(stream)]
    if input_path is not None:
        cmd += ["--input", str(input_path)]
    if output_path is not None:
        cmd += ["--output", str(output_path)]
    if abs_bound is not None:
        cmd += ["--abs-bound", repr(float(abs_bound))]
    return cmd


def compress_base(codec: str, array: np.ndarray, abs_bound: float, workdir: Path, name: str = "base",
                  source_raw: Path | None = None) -> tuple[Path, int, int]:
    """Compress in a subprocess and return (stream path, logical bytes, file bytes)."""
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    source = Path(source_raw) if source_raw is not None else workdir / f"{name}.input.raw"
    if source_raw is None:
        _write_raw(source, array)
    stream = workdir / f"{name}.stream"
    result = _run_process(_worker_cmd("base-compress", codec, tuple(array.shape), stream,
                                      input_path=source, abs_bound=abs_bound), workdir)
    try:
        metadata = json.loads(result.stdout.strip().splitlines()[-1])
        return stream, int(metadata["stream_bytes"]), int(metadata["stream_file_bytes"])
    except (ValueError, KeyError, IndexError, json.JSONDecodeError) as exc:
        raise CodecExecutionError(f"invalid compressor metadata: {result.stdout!r}") from exc


def decompress_base(codec: str, stream: Path, shape: tuple[int, int, int], output: Path, workdir: Path) -> None:
    """Decode in a fresh subprocess from the stream path alone."""
    output = Path(output)
    output.unlink(missing_ok=True)
    _run_process(_worker_cmd("base-decompress", codec, shape, Path(stream), output_path=output), Path(workdir))
    if not output.exists():
        raise CodecExecutionError("base decompressor wrote no output")
    expected_bytes = int(np.prod(shape)) * np.dtype("<f8").itemsize
    if output.stat().st_size != expected_bytes:
        raise CodecExecutionError(f"base output bytes {output.stat().st_size} != {expected_bytes}")


def prepare_base(codec: str, array: np.ndarray, abs_bound: float, workdir: Path, name: str = "base",
                 source_raw: Path | None = None) -> BaseArtifact:
    shape = tuple(int(v) for v in np.asarray(array).shape)
    if len(shape) != 3:
        raise ValueError(f"FFCz base fields must be 3-D, got {shape!r}")
    stream, stream_bytes, stream_file_bytes = compress_base(codec, array, abs_bound, workdir, name, source_raw)
    decoded = Path(workdir) / f"{name}.decoded.raw"
    decompress_base(codec, stream, shape, decoded, workdir)
    return BaseArtifact(codec.lower(), float(abs_bound), shape, stream, decoded, stream_bytes, stream_file_bytes)


def ffcz_edit_paths(prefix: Path) -> tuple[Path, ...]:
    prefix = Path(prefix)
    return tuple(Path(str(prefix) + suffix) for suffix in FFCZ_SUFFIXES)


def remove_ffcz_edits(prefix: Path) -> None:
    for path in ffcz_edit_paths(prefix):
        path.unlink(missing_ok=True)


def ffcz_command(exe: str | Path, mode: str, r: float, shape: tuple[int, int, int], spatial_bound: float,
                 original_raw: Path | None, base_raw: Path, edits_prefix: Path, decoded_raw: Path | None = None) -> list[str]:
    # ffcz_cpu's parser rejects "-3 Nx Ny Nz" as the last arguments, so the size follows "-d".
    cmd = [str(exe), "-d", "-3", *[str(v) for v in shape]]
    if original_raw is not None:
        cmd += ["-i", str(original_raw)]
    cmd += ["-e", str(base_raw), "-z", str(edits_prefix)]
    if decoded_raw is not None:
        cmd += ["-o", str(decoded_raw)]
    cmd += ["-M", "ABS", repr(float(spatial_bound)), "-F", str(mode), repr(float(r))]
    return cmd


def run_ffcz_roundtrip(exe: str | Path, original_raw: Path, base: BaseArtifact, spatial_bound: float, mode: str,
                       r: float, workdir: Path, tag: str | None = None) -> tuple[np.ndarray, int, int, dict[str, Any]]:
    """Apply FFCz correction and decode it in two executable invocations."""
    mode = str(mode).upper()
    if mode not in {"REL", "PTW"}:
        raise ValueError(f"unknown FFCz frequency mode {mode!r}")
    workdir = Path(workdir)
    label = tag or f"{mode}_{r:.17g}"
    prefix = workdir / f"edits_{label}"
    decoded = workdir / f"decoded_{label}.raw"
    remove_ffcz_edits(prefix)
    decoded.unlink(missing_ok=True)

    _run_process(ffcz_command(exe, mode, r, base.shape, spatial_bound, original_raw, base.decoded_path, prefix), workdir)
    edit_paths = ffcz_edit_paths(prefix)
    missing = [str(path) for path in edit_paths if not path.exists()]
    if missing:
        raise CodecExecutionError(f"FFCz correction wrote no complete edit set: {missing}")
    edits_bytes = int(sum(path.stat().st_size for path in edit_paths))

    _run_process(ffcz_command(exe, mode, r, base.shape, spatial_bound, None, base.decoded_path, prefix, decoded), workdir)
    expected_bytes = int(np.prod(base.shape)) * np.dtype("<f8").itemsize
    if not decoded.exists() or decoded.stat().st_size != expected_bytes:
        raise CodecExecutionError("FFCz decoder wrote no valid-sized output")
    reconstructed = np.fromfile(decoded, dtype="<f8")
    if reconstructed.size != int(np.prod(base.shape)) or not np.all(np.isfinite(reconstructed)):
        raise CodecExecutionError("FFCz decoder returned the wrong size or non-finite values")
    reconstructed = reconstructed.reshape(base.shape).astype(np.float64, copy=False)
    details = {
        "base_stream_bytes": int(base.stream_bytes),
        "base_stream_file_bytes": int(base.stream_file_bytes),
        "edits_bytes": edits_bytes,
        "edit_files": {suffix: int((Path(str(prefix) + suffix).stat().st_size)) for suffix in FFCZ_SUFFIXES},
        "stored_bytes": int(base.stream_bytes + edits_bytes),
        "axis_order": FFCZ_AXIS_ORDER,
    }
    return reconstructed, int(base.stream_bytes), edits_bytes, details


def stored_bytes(base_stream_bytes: int, edits_bytes: int) -> int:
    total = int(base_stream_bytes) + int(edits_bytes)
    if total <= 0:
        raise ValueError(f"stored byte count must be positive, got {total}")
    return total


def compression_ratio(npoints: int, base_stream_bytes: int, edits_bytes: int) -> float:
    return float(8.0 * int(npoints) / stored_bytes(base_stream_bytes, edits_bytes))


def resolve_ffcz(executable: str | Path | None = None) -> str:
    candidate = str(executable) if executable else os.environ.get("FFCZ_CPU") or shutil.which("ffcz_cpu")
    if not candidate:
        raise CodecExecutionError("ffcz_cpu executable not found; set --ffcz-exe or FFCZ_CPU")
    return candidate


def main() -> int:
    return _worker_main(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
