"""Perturbation-amplitude response of a grid-based atomic charge partition.

For one volumetric field, measures how far the partitioned per-atom charges move
when the field is perturbed by additive uniform noise, as a function of the noise
amplitude. The amplitude is expressed as a multiple of the field's own
float64 -> float32 rounding scale.

The source field is downloaded from a URL supplied at run time and checked against
the checksum supplied with it. The target list is not stored in this repository:
it is injected from a repository secret, and results are keyed by target index
only, so neither the run logs nor the artifacts identify the dataset entries.

Emits one CSV row per (amplitude, seed). Amplitude 1.0 is included as a platform
control: its value is compared off-runner against the reference value measured
elsewhere, and a mismatch invalidates this runner's rows rather than being
silently merged.
"""

from __future__ import annotations

import argparse
import bz2
import csv
import gzip
import hashlib
import json
import lzma
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vaspio import read_volumetric  # noqa: E402

SEEDS = [20260905, 1, 2, 3, 4]
ALPHAS = [1.0, 1e1, 1e2, 1e3, 1e4, 1e5]

FIELDS = [
    "target_index", "alpha", "seed", "npoints", "natoms",
    "eps_m", "probe_linf", "probe_rel_error",
    "response_resolved_e", "response_fixed_e",
    "n_voxels_reassigned", "frac_voxels_reassigned",
    "frac_negative_voxels", "bader_seconds",
    "runner", "source_sha256_ok",
]


def labels(lattice, frac, symbols, values):
    from baderkit.bader import Bader
    from baderkit.toolkit import Grid, Structure

    st = Structure(lattice=lattice, species=list(symbols), frac_coords=np.asarray(frac))
    b = Bader(charge_grid=Grid(structure=st, data={"total": np.ascontiguousarray(values)}),
              method="ongrid")
    return np.asarray(b.atom_labels).ravel()


def charges(field, lab, natoms):
    flat = np.asarray(field).ravel()
    return np.bincount(lab, weights=flat, minlength=natoms)[:natoms] / flat.size


def decompress(name: str, blob: bytes) -> bytes:
    if name.endswith(".bz2"):
        return bz2.decompress(blob)
    if name.endswith(".gz"):
        return gzip.decompress(blob)
    if name.endswith((".xz", ".lzma")):
        return lzma.decompress(blob)
    return blob


def fetch(target: dict) -> tuple[bytes, bool]:
    req = urllib.request.Request(target["url"], headers={"User-Agent": "amplitude-sweep/1.0"})
    with urllib.request.urlopen(req, timeout=900) as r:
        blob = r.read()
    ok = hashlib.sha256(blob).hexdigest() == target["sha256"]
    if len(blob) != target["source_bytes"]:
        ok = False
    return blob, ok


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--targets", type=Path, required=True,
                    help="JSONL written at run time from a repository secret; never committed")
    ap.add_argument("--index", type=int, required=True, help="0-based row of the target manifest")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    rows = [json.loads(l) for l in args.targets.read_text(encoding="utf-8").splitlines() if l.strip()]
    t = rows[args.index]
    mid = f"target-{args.index}"  # identity stays off the public runner
    runner = f"{sys.platform}-py{sys.version_info.major}.{sys.version_info.minor}"
    print(f"[{mid}] fetching {t['source_bytes']/1e6:.0f} MB", flush=True)

    blob, sha_ok = fetch(t)
    if not sha_ok:
        raise SystemExit(f"[{mid}] source checksum or byte count mismatch; refusing to compute")
    text = decompress(t["file_name"], blob)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "field.CHGCAR"
        p.write_bytes(text)
        vol = read_volumetric(p)
    del blob, text

    symbols = np.array([s for s, c in zip(vol.species, vol.counts) for _ in range(c)])
    grid = np.ascontiguousarray(vol.data, dtype=np.float64)
    lattice, frac = vol.lattice, vol.frac_coords
    natoms = len(symbols)
    if not np.all(np.isfinite(grid)):
        raise SystemExit(f"[{mid}] non-finite field")

    lab0 = labels(lattice, frac, symbols, grid)
    q0 = charges(grid, lab0, natoms)
    eps_m = float(np.abs(grid.astype(np.float32).astype(np.float64) - grid).max())
    ptp = float(np.ptp(grid))
    print(f"[{mid}] {grid.size} points, {natoms} atoms, eps_m {eps_m:.3e}", flush=True)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fo:
        w = csv.DictWriter(fo, fieldnames=FIELDS)
        w.writeheader()
        for alpha in ALPHAS:
            amp = alpha * eps_m
            for seed in SEEDS:
                noisy = grid + np.random.default_rng(seed).uniform(-amp, amp, grid.shape)
                t0 = time.time()
                lab = labels(lattice, frac, symbols, noisy)
                dt = time.time() - t0
                reass = int((lab0 != lab).sum())
                w.writerow({
                    "target_index": args.index, "alpha": alpha, "seed": seed,
                    "npoints": int(grid.size), "natoms": natoms,
                    "eps_m": eps_m, "probe_linf": amp, "probe_rel_error": amp / ptp,
                    "response_resolved_e": float(np.abs(charges(noisy, lab, natoms) - q0).max()),
                    "response_fixed_e": float(np.abs(charges(noisy, lab0, natoms) - q0).max()),
                    "n_voxels_reassigned": reass,
                    "frac_voxels_reassigned": reass / grid.size,
                    "frac_negative_voxels": float((noisy < 0).mean()),
                    "bader_seconds": round(dt, 2),
                    "runner": runner, "source_sha256_ok": sha_ok,
                })
                del noisy, lab
            fo.flush()
            print(f"[{mid}] alpha {alpha:.0e} done", flush=True)

    print(f"[{mid}] wrote {args.out}", flush=True)


if __name__ == "__main__":
    main()
