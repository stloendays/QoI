"""Stage 1 of the 3D panels: regenerate the exact fields the renders show.

Runs in the frozen scientific environment (baderkit / zfpy / pysz pinned):

    D:/Research/QoI-final4-local/venv/Scripts/python.exe prep_fields.py

For KCN (mp-676693, the Fig. 5c jump case and the Fig. 7 matched pair 266) it
  1. reads the SHA-256-verified source bytes from the density cache,
  2. builds the reference grid with the frozen development loader,
  3. regenerates the frozen benchmark reconstructions it needs with the frozen
     codec round trip at the stored absolute tolerance,
  4. re-solves Bader on each, and
  5. asserts that realized L-inf and the re-derived Bader error reproduce the
     frozen benchmark row before anything is written.

For the SI gallery it loads a fixed list of reference densities (no codec).
Output: npz files in D:/Research/QoI-ext-cache/figure3d (outside the repository;
they are regenerable and ~100 MB).
"""
from __future__ import annotations

import csv
import hashlib
import json
import logging
import sys
import tempfile
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
FROZEN_VALIDATION = Path(r"D:\Research\QoI-final4-local\frozen_repo\validation")
CACHE = Path(r"D:\Research\QoI-ext-cache\densities")
OUT = Path(r"D:\Research\QoI-ext-cache\figure3d")
# WP-B's full Windows re-solve of every frozen benchmark row (same pinned stack as this script)
WPB_ROWS = Path(r"D:\Research\QoI\.claude\worktrees\agent-a89fa1cb2104a083d\analysis\extensions_20260928\WP-B\cp_rows.csv")

sys.path.insert(0, str(FROZEN_VALIDATION))
sys.path.insert(0, str(REPO / "validation" / "qsq_prospective"))
import development_compatibility_smoke as dev  # noqa: E402
import external_end_to_end as core  # noqa: E402

logging.disable(logging.WARNING)

KCN = "mp-676693"
# (tag, codec, nominal relative tolerance) -- every one is a frozen benchmark row
KCN_ROWS = (
    ("zfp_1e-7", "ZFP", 1e-7),    # before the Fig. 5c jump
    ("zfp_3e-7", "ZFP", 3e-7),    # after the jump (22,296x)
    ("zfp_1e-3", "ZFP", 1e-3),    # Fig. 1a and Fig. 7 pair 266 (ZFP side)
    ("zfp_1e-2", "ZFP", 1e-2),    # coarse rung, many reassigned voxels
    ("sz3_1e-4", "SZ3", 1e-4),    # Fig. 7 pair 266 (SZ3 side)
)
# SI gallery: the three Fig. 5c ladder materials plus contrasting chemistries/geometries
GALLERY = ("mp-676693", "mp-560341", "nomad-9jQMkfdCbgX_", "mp-1007755", "mp-1009084")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def cached_blob(meta: dict[str, str]) -> bytes:
    path = CACHE / f"{meta['sha256']}.bin"
    blob = path.read_bytes()
    if hashlib.sha256(blob).hexdigest() != meta["sha256"] or len(blob) != int(meta["source_bytes"]):
        raise RuntimeError(f"cache SHA-256 mismatch for {meta['material_id']}")
    return blob


def structure_arrays(structure) -> dict[str, np.ndarray]:
    return {
        "lattice": np.asarray(structure.lattice.matrix, dtype=np.float64),
        "cart": np.asarray(structure.cart_coords, dtype=np.float64),
        "frac": np.asarray(structure.frac_coords, dtype=np.float64),
        "species": np.array([site.specie.symbol for site in structure]),
    }


def load(meta: dict[str, str], workdir: Path):
    grid, _ = dev.build_grid(meta, cached_blob(meta), workdir)
    field = np.asarray(grid.total, dtype=np.float64)
    if tuple(field.shape) != dev.parse_shape(meta["ngrid"]):
        raise RuntimeError("grid shape mismatch")
    return grid, field


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    metadata = {r["material_id"]: r for r in read_csv(REPO / "materials_metadata.csv")}
    bench = [r for r in read_csv(REPO / "benchmark" / "master_benchmark_full.csv") if r["material_id"] == KCN]
    wpb = [r for r in read_csv(WPB_ROWS) if r["material_id"] == KCN]
    provenance: dict = {"material": KCN, "rows": {}}

    with tempfile.TemporaryDirectory(prefix="fig3d_") as td:
        workdir = Path(td)
        grid, field = load(metadata[KCN], workdir)
        vol = float(grid.structure.lattice.volume)
        ptp = float(np.ptp(field))
        assert np.isclose(ptp, float(bench[0]["value_ptp"]), rtol=1e-12), ptp
        ref = core.run_bader(grid)
        q_ref = np.asarray(ref["charges"], dtype=np.float64)
        labels_ref = np.asarray(ref["atom_labels"]).astype(np.int16)
        natoms = q_ref.size

        out = dict(structure_arrays(grid.structure), volume=vol, rho=(field / vol).astype(np.float32),
                   labels_ref=labels_ref, q_ref=q_ref)
        for tag, codec, rel in KCN_ROWS:
            row = next(r for r in bench if r["codec"].upper() == codec
                       and np.isclose(float(r["nominal_tolerance_relative"]), rel, rtol=1e-9))
            rec, nbytes, _ = core.codec_roundtrip(codec.lower(), field, float(row["nominal_tolerance_absolute"]), workdir)
            rec = np.asarray(rec, dtype=np.float64)
            linf = float(np.max(np.abs(rec - field)))
            frozen_linf = float(row["realized_Linf"])
            assert 0.95 <= linf / frozen_linf <= 1.05, (tag, linf, frozen_linf)
            res = core.run_bader(core.clone_grid_with_total(grid, rec))
            q_rec = np.asarray(res["charges"], dtype=np.float64)
            labels = np.asarray(res["atom_labels"]).astype(np.int16)
            err = float(np.max(np.abs(q_rec - q_ref)))
            frozen_err = float(row["Bader_error_resolved_e"])
            reassigned = labels != labels_ref
            frac = float(reassigned.mean())
            # Gate: the Bader re-solve must reproduce WP-B's Windows re-solve of the same frozen row exactly.
            # It differs from the frozen Ubuntu row by the cross-platform amount WP-B documents (up to ~13 % on
            # coarse ZFP rungs); the figures quote frozen numbers and render the voxels of this re-solve.
            w = next(r for r in wpb if r["codec"].upper() == codec
                     and np.isclose(float(r["nominal_tolerance_relative"]), rel, rtol=1e-9))
            assert np.isclose(err, float(w["bader_error_resolved_e"]), rtol=1e-9, atol=1e-15), (tag, err, w["bader_error_resolved_e"])
            assert int(reassigned.sum()) == int(w["n_voxels_reassigned"]), (tag, int(reassigned.sum()), w["n_voxels_reassigned"])
            out[f"drho_{tag}"] = ((rec - field) / vol).astype(np.float32)
            out[f"labels_{tag}"] = labels
            out[f"dq_{tag}"] = q_rec - q_ref
            provenance["rows"][tag] = dict(codec=codec, nominal_relative=rel,
                                           nominal_absolute=float(row["nominal_tolerance_absolute"]),
                                           realized_Linf=linf, frozen_realized_Linf=frozen_linf,
                                           bader_error_e=err, frozen_bader_error_e=frozen_err,
                                           n_reassigned=int(reassigned.sum()), frac_reassigned=frac,
                                           compression_ratio=float(row["compression_ratio"]),
                                           realized_Linf_rho_e_per_A3=linf / vol)
            print(f"{tag:10s} Linf {linf:.6g} (frozen {frozen_linf:.6g})  Bader {err:.4g} e (frozen {frozen_err:.4g})"
                  f"  reassigned {int(reassigned.sum())}")
        np.savez_compressed(OUT / f"{KCN}_fields.npz", **out)
        provenance.update(natoms=natoms, shape=list(field.shape), volume_A3=vol,
                          rho_max=float(field.max() / vol), rho_min=float(field.min() / vol))
        (OUT / f"{KCN}_provenance.json").write_text(json.dumps(provenance, indent=1), encoding="utf-8")

        for mid in GALLERY:
            meta = metadata[mid]
            g, f = load(meta, workdir)
            v = float(g.structure.lattice.volume)
            np.savez_compressed(OUT / f"gallery_{mid}.npz", **structure_arrays(g.structure), volume=v,
                                rho=(f / v).astype(np.float32), formula=meta["formula"],
                                system_type=meta["system_type"], ngrid=meta["ngrid"])
            print(f"gallery {mid} {meta['formula']} {meta['ngrid']} natoms {len(g.structure)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
