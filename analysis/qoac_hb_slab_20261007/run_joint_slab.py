#!/usr/bin/env python3
"""QOAC-HB slab confirmation runner: HB v2's run_joint_v2 unchanged, plus a NOMAD source for the AECCAR reference.

run_joint_v2.process reads the exact AECCAR0 + AECCAR2 reference with

    b1.fetch(b1.BUCKET + f"aeccar0s/{task_id}.json.gz")    # and aeccar2s/
    dev.decode_mp_chgcar(blob).data["total"]

which is the Materials Project S3 layout. The P3b slabs are NOMAD entries. When their VASP run wrote AECCARs, these
sit next to the CHGCAR in the entry's raw directory. This module serves exactly those two requests from NOMAD for the
entries listed in the frozen table `aeccar_sources.csv` and passes every other call to the HB v2 objects unchanged:

- fetch: GET https://nomad-lab.eu/prod/v1/api/v1/entries/<entry_id>/raw/<basename> through `b1.fetch` (same
  retries and user agent as every HB v2 download), byte count and SHA-256 checked against the table, decompressed by
  extension with `dev.decompress_nomad` (as `dev.build_grid` does for the NOMAD CHGCAR);
- decode: parsed with baderkit `Grid.from_dynamic`, the parser `dev.build_grid` uses for NOMAD CHGCARs, so
  `.data["total"]` is in the same units as the CHGCAR `grid.total` that `process` uses as rho.

An entry without AECCAR0/AECCAR2 raises at the AECCAR fetch, where an HB v2 download failure would raise, and
`run_joint_v2.main` records the material FAILED. Task ids that are not in the table keep the original MP bucket path.
The scientific computation (codecs, post-processors, Hartree certificate, Henkelman Bader, selection, outputs) is
`run_joint_v2.process` / `run_joint_v2.main`, imported from analysis/qoac_hb_v2 without modification.

Usage: identical arguments to run_joint_v2.py; optional --aeccar-sources (default: aeccar_sources.csv next to this file).
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import posixpath
import re
import sys
import tempfile
import types
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
HB_V2 = HERE.parent / "qoac_hb_v2" / "run_joint_v2.py"
DEFAULT_SOURCES = HERE / "aeccar_sources.csv"
NOMAD_RAW = "https://nomad-lab.eu/prod/v1/api/v1/entries/{entry}/raw/{name}"
AECCAR_KEY = re.compile(r"aeccar([02])s/(.+)\.json\.gz")


def load_hb_v2():
    if "run_joint_v2" in sys.modules:
        return sys.modules["run_joint_v2"]
    spec = importlib.util.spec_from_file_location("run_joint_v2", HB_V2)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["run_joint_v2"] = mod
    spec.loader.exec_module(mod)
    return mod


def read_sources(path: Path) -> dict[str, dict]:
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    table = {r["entry_id"]: r for r in rows}
    if len(table) != len(rows):
        raise RuntimeError(f"duplicate entry_id in {path}")
    return table


class NomadVaspBytes(bytes):
    """Decompressed VASP volumetric text of a NOMAD AECCAR; marks the blob for `decode_mp_chgcar`."""


class AeccarSource:
    """Stands in for run_joint_v2.b1: routes the two AECCAR requests of NOMAD entries to NOMAD; delegates the rest."""

    def __init__(self, b1, decompress, table: dict[str, dict]):
        self._b1 = b1
        self._decompress = decompress
        self._table = table
        self.log: list[dict] = []

    def __getattr__(self, name):
        return getattr(self._b1, name)

    def fetch(self, url: str) -> bytes:
        bucket = self._b1.BUCKET
        if url.startswith(bucket):
            m = AECCAR_KEY.fullmatch(url[len(bucket):])
            if m and m.group(2) in self._table:
                return self._nomad(m.group(2), m.group(1))
        return self._b1.fetch(url)

    def _nomad(self, entry: str, k: str) -> NomadVaspBytes:
        row = self._table[entry]
        path = row.get(f"aeccar{k}_path", "")
        if not path:
            raise RuntimeError(f"AECCAR{k} unavailable: NOMAD entry {entry} has no AECCAR{k} next to its CHGCAR "
                               "(frozen listing aeccar_sources.csv)")
        name = posixpath.basename(path)
        blob = self._b1.fetch(NOMAD_RAW.format(entry=entry, name=name))
        sha = hashlib.sha256(blob).hexdigest()
        if len(blob) != int(row[f"aeccar{k}_bytes"]) or sha != row[f"aeccar{k}_sha256"]:
            raise RuntimeError(f"AECCAR{k} checksum mismatch for NOMAD entry {entry}: {len(blob)} bytes, sha256 {sha}")
        self.log.append({"entry_id": entry, "file": f"AECCAR{k}", "name": name, "bytes": len(blob), "sha256": sha})
        return NomadVaspBytes(self._decompress(name, blob))


def parse_vasp_total(raw: bytes) -> np.ndarray:
    from baderkit import Grid

    # ignore_cleanup_errors: on Windows baderkit can still hold the file open when the directory is removed
    with tempfile.TemporaryDirectory(prefix="qoachb_slab_aeccar_", ignore_cleanup_errors=True) as td:
        p = Path(td) / "AECCAR"
        p.write_bytes(raw)
        grid = Grid.from_dynamic(p)
        total = np.array(grid.total, dtype=np.float64, copy=True)
        del grid
    return total


def nomad_aware_dev(dev):
    """A copy of the development loader module whose decode_mp_chgcar also accepts NOMAD AECCAR text."""
    proxy = types.ModuleType(dev.__name__)
    proxy.__dict__.update(dev.__dict__)
    mp_decode = dev.decode_mp_chgcar

    def decode_mp_chgcar(blob):
        if isinstance(blob, NomadVaspBytes):
            return types.SimpleNamespace(data={"total": parse_vasp_total(bytes(blob))})
        return mp_decode(blob)

    proxy.decode_mp_chgcar = decode_mp_chgcar
    return proxy


def install(rj, dev, table: dict[str, dict]) -> AeccarSource:
    """Point run_joint_v2 at the NOMAD AECCAR source and the NOMAD-aware loader; returns the source (for its log)."""
    src = AeccarSource(rj.b1, dev.decompress_nomad, table)
    rj.b1 = src
    sys.modules[dev.__name__] = nomad_aware_dev(dev)
    return src


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    sources = DEFAULT_SOURCES
    if "--aeccar-sources" in argv:
        i = argv.index("--aeccar-sources")
        sources = Path(argv[i + 1])
        del argv[i:i + 2]
    rj = load_hb_v2()
    a = rj.parse_args(argv)
    # the same import paths run_joint_v2.main sets before importing the development loader
    sys.path.insert(0, str(a.frozen_root.resolve() / "validation"))
    sys.path.insert(0, str(a.repo_root.resolve() / "validation" / "qsq_prospective"))
    import development_compatibility_smoke as dev
    src = install(rj, dev, read_sources(sources))
    rc = rj.main(argv)
    out = a.output_dir.resolve()
    rj.write_csv(out / f"aeccar_downloads_shard_{a.shard_index:02d}.csv", src.log or [{"entry_id": ""}])
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
