#!/usr/bin/env python3
"""HB v2 runner for the self-computed slab cohort: run_joint_v2 unchanged, with the density files served from the
GitHub release `data-hb-selfslab-20261008` of stloendays/QoI.

Modelled on analysis/qoac_hb_slab_20261007/run_joint_slab.py (whose NOMAD AECCAR marker, parser and loader proxy are
imported and reused). run_joint_v2.process makes three downloads per material:

    chg_blob = b1.fetch(meta["url"])                               # then sha256(chg_blob) == meta["sha256"]
    a0 = b1.fetch(b1.BUCKET + f"aeccar0s/{task_id}.json.gz")       # and aeccar2s/
    grid, _ = dev.build_grid(meta, chg_blob, work)
    ae = dev.decode_mp_chgcar(a0).data["total"] + dev.decode_mp_chgcar(a2).data["total"]

For the material ids in the frozen table `cohort.csv` this module serves them as follows; every other call goes to the
HB v2 objects unchanged:

- fetch: the CHGCAR URL of the manifest and the two AECCAR bucket keys are fetched from
  https://github.com/stloendays/QoI/releases/download/data-hb-selfslab-20261008/<material_id>__<FILE>.gz through
  `b1.fetch` (same retries and user agent as every HB v2 download); the gz byte count and SHA-256 must equal the
  `<FILE>_gz_bytes` and `<FILE>_gz_sha256` of cohort.csv, otherwise the download raises (and run_joint_v2.main records
  the material FAILED, as for any HB v2 download failure). The CHGCAR blob is returned as downloaded, so HB v2's own
  `sha256(chg_blob) == meta["sha256"]` check also runs; the AECCAR blobs are decompressed with `dev.decompress_nomad`
  and marked as VASP text (run_joint_slab.NomadVaspBytes);
- build_grid for source `QoI self-computed slab (VASP 6.3.2)`: `dev.decompress_nomad(url, blob)` and baderkit
  `Grid.from_dynamic`, the two functions `dev.build_grid` uses for a VASP CHGCAR (its NOMAD branch); every other
  source goes to `dev.build_grid` unchanged;
- decode_mp_chgcar of a marked AECCAR: run_joint_slab.parse_vasp_total (baderkit `Grid.from_dynamic`, the same parser),
  so the reference is in the CHGCAR's units, as in the slab runs.

The scientific computation (codecs, post-processors, Hartree certificate, Henkelman Bader, selection, outputs) is
run_joint_v2.process / run_joint_v2.main, imported from analysis/qoac_hb_v2 without modification.

Usage: identical arguments to run_joint_v2.py; optional --cohort (default: cohort.csv next to this file).
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import re
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLAB_ADAPTER = HERE.parent / "qoac_hb_slab_20261007" / "run_joint_slab.py"
DEFAULT_COHORT = HERE / "cohort.csv"
RELEASE = "https://github.com/stloendays/QoI/releases/download/data-hb-selfslab-20261008/"
SOURCE = "QoI self-computed slab (VASP 6.3.2)"
FILES = ("CHGCAR", "AECCAR0", "AECCAR2")
AECCAR_KEY = re.compile(r"aeccar([02])s/(.+)\.json\.gz")


def load_slab_adapter():
    if "run_joint_slab" in sys.modules:
        return sys.modules["run_joint_slab"]
    spec = importlib.util.spec_from_file_location("run_joint_slab", SLAB_ADAPTER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["run_joint_slab"] = mod
    spec.loader.exec_module(mod)
    return mod


rs = load_slab_adapter()


def asset_url(material_id: str, name: str) -> str:
    return f"{RELEASE}{material_id}__{name}.gz"


def read_cohort(path: Path) -> dict[str, dict]:
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    table = {r["material_id"]: r for r in rows}
    if len(table) != len(rows):
        raise RuntimeError(f"duplicate material_id in {path}")
    return table


class ReleaseSource:
    """Stands in for run_joint_v2.b1: serves the cohort's CHGCAR and AECCARs from the release; delegates the rest."""

    def __init__(self, b1, decompress, table: dict[str, dict]):
        self._b1 = b1
        self._decompress = decompress
        self._table = table
        self._chg = {asset_url(m, "CHGCAR"): m for m in table}
        self.log: list[dict] = []

    def __getattr__(self, name):
        return getattr(self._b1, name)

    def fetch(self, url: str) -> bytes:
        if url in self._chg:
            return self._get(self._chg[url], "CHGCAR")
        bucket = self._b1.BUCKET
        if url.startswith(bucket):
            m = AECCAR_KEY.fullmatch(url[len(bucket):])
            if m and m.group(2) in self._table:
                name = f"AECCAR{m.group(1)}"
                blob = self._get(m.group(2), name)
                return rs.NomadVaspBytes(self._decompress(asset_url(m.group(2), name), blob))
        return self._b1.fetch(url)

    def _get(self, material_id: str, name: str) -> bytes:
        row = self._table[material_id]
        url = asset_url(material_id, name)
        blob = self._b1.fetch(url)
        sha = hashlib.sha256(blob).hexdigest()
        if len(blob) != int(row[f"{name}_gz_bytes"]) or sha != row[f"{name}_gz_sha256"]:
            raise RuntimeError(f"{name} checksum mismatch for {material_id}: {len(blob)} bytes, sha256 {sha}")
        self.log.append({"material_id": material_id, "file": name, "url": url, "bytes": len(blob), "sha256": sha})
        return blob


def selfslab_dev(dev):
    """The NOMAD-aware loader proxy of run_joint_slab, plus build_grid for the self-computed slab source."""
    proxy = rs.nomad_aware_dev(dev)
    base_build_grid = dev.build_grid

    def build_grid(meta, blob, workdir):
        if meta["source"] != SOURCE:
            return base_build_grid(meta, blob, workdir)
        from baderkit import Grid
        raw = dev.decompress_nomad(meta["url"], blob)
        chg_path = Path(workdir) / "CHGCAR"
        chg_path.write_bytes(raw)
        return Grid.from_dynamic(chg_path), "selfslab_release_gz_decompress_to_baderkit_grid"

    proxy.build_grid = build_grid
    return proxy


def install(rj, dev, table: dict[str, dict]) -> ReleaseSource:
    """Point run_joint_v2 at the release source and the self-slab-aware loader; returns the source (for its log)."""
    src = ReleaseSource(rj.b1, dev.decompress_nomad, table)
    rj.b1 = src
    sys.modules[dev.__name__] = selfslab_dev(dev)
    return src


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cohort = DEFAULT_COHORT
    if "--cohort" in argv:
        i = argv.index("--cohort")
        cohort = Path(argv[i + 1])
        del argv[i:i + 2]
    rj = rs.load_hb_v2()
    a = rj.parse_args(argv)
    # the same import paths run_joint_v2.main sets before importing the development loader
    sys.path.insert(0, str(a.frozen_root.resolve() / "validation"))
    sys.path.insert(0, str(a.repo_root.resolve() / "validation" / "qsq_prospective"))
    import development_compatibility_smoke as dev
    src = install(rj, dev, read_cohort(cohort))
    rc = rj.main(argv)
    out = a.output_dir.resolve()
    rj.write_csv(out / f"release_downloads_shard_{a.shard_index:02d}.csv", src.log or [{"material_id": ""}])
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
