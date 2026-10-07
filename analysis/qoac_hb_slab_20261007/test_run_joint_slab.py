"""Data-free tests of the NOMAD AECCAR source (stdlib unittest; numpy only, baderkit parts skip without baderkit)."""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_joint_slab as rs  # noqa: E402

rj = rs.load_hb_v2()
HAVE_BADERKIT = importlib.util.find_spec("baderkit") is not None
ENTRY = "TESTentry0000000000000000000"
LAT = np.array([[4.0, 0.0, 0.0], [0.5, 5.0, 0.0], [0.0, 0.0, 12.0]])


def vasp_text(field: np.ndarray) -> bytes:
    """VASP volumetric file with VASP's fixed-width data format (5 x ' 0.12345678901E+00' per line)."""
    head = ["fabricated AECCAR", "1.0", *(" ".join(f"{x:.10f}" for x in v) for v in LAT), "O Ti", "1 1", "Direct",
            "0.1 0.2 0.3", "0.6 0.5 0.4", "", " ".join(map(str, field.shape))]
    flat = field.ravel(order="F")
    body = ["".join(f" {v:.11E}" for v in flat[i:i + 5]) for i in range(0, flat.size, 5)]
    return ("\n".join(head + body) + "\n").encode()


def decompress(name: str, blob: bytes) -> bytes:
    return gzip.decompress(blob) if name.endswith(".gz") else blob


class StubB1:
    BUCKET = "https://materialsproject-parsed.s3.amazonaws.com/"

    def __init__(self, files):
        self.files, self.calls = files, []

    def fetch(self, url):
        self.calls.append(url)
        if url not in self.files:
            raise RuntimeError(f"download failed {url}")
        return self.files[url]


def table_for(blobs):
    row = {"entry_id": ENTRY, "aeccar_available": "1"}
    for k, (name, blob) in blobs.items():
        row.update({f"aeccar{k}_path": f"some/dir/{name}", f"aeccar{k}_bytes": str(len(blob)),
                    f"aeccar{k}_sha256": hashlib.sha256(blob).hexdigest()})
    return {ENTRY: row}


class TestAeccarSource(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(1)
        self.f0 = rng.random((4, 5, 6)) + 0.1
        self.f2 = rng.random((4, 5, 6)) + 0.2
        self.b0 = gzip.compress(vasp_text(self.f0), mtime=0)
        self.b2 = vasp_text(self.f2)
        self.files = {rs.NOMAD_RAW.format(entry=ENTRY, name="AECCAR0.gz"): self.b0,
                      rs.NOMAD_RAW.format(entry=ENTRY, name="AECCAR2"): self.b2,
                      StubB1.BUCKET + "chgcars/mp-1.json.gz": b"mp-chgcar",
                      StubB1.BUCKET + "aeccar0s/mp-1.json.gz": b"mp-aeccar0"}
        self.table = table_for({"0": ("AECCAR0.gz", self.b0), "2": ("AECCAR2", self.b2)})

    def test_routes_nomad_entry_to_its_raw_directory(self):
        b1 = StubB1(self.files)
        src = rs.AeccarSource(b1, decompress, self.table)
        a0 = src.fetch(b1.BUCKET + f"aeccar0s/{ENTRY}.json.gz")
        a2 = src.fetch(b1.BUCKET + f"aeccar2s/{ENTRY}.json.gz")
        self.assertIsInstance(a0, rs.NomadVaspBytes)
        self.assertEqual(bytes(a0), gzip.decompress(self.b0))
        self.assertEqual(bytes(a2), self.b2)
        self.assertEqual(b1.calls, [rs.NOMAD_RAW.format(entry=ENTRY, name="AECCAR0.gz"),
                                    rs.NOMAD_RAW.format(entry=ENTRY, name="AECCAR2")])
        self.assertEqual([r["file"] for r in src.log], ["AECCAR0", "AECCAR2"])

    def test_other_urls_and_task_ids_are_untouched(self):
        b1 = StubB1(self.files)
        src = rs.AeccarSource(b1, decompress, self.table)
        self.assertEqual(src.fetch(b1.BUCKET + "chgcars/mp-1.json.gz"), b"mp-chgcar")
        self.assertEqual(src.fetch(b1.BUCKET + "aeccar0s/mp-1.json.gz"), b"mp-aeccar0")
        self.assertNotIsInstance(src.fetch(b1.BUCKET + "aeccar0s/mp-1.json.gz"), rs.NomadVaspBytes)
        self.assertIs(src.BUCKET, b1.BUCKET)

    def test_missing_aeccar_raises_without_download(self):
        b1 = StubB1(self.files)
        table = {ENTRY: {"entry_id": ENTRY, "aeccar_available": "0", "aeccar0_path": "", "aeccar2_path": ""}}
        src = rs.AeccarSource(b1, decompress, table)
        with self.assertRaisesRegex(RuntimeError, "AECCAR0 unavailable"):
            src.fetch(b1.BUCKET + f"aeccar0s/{ENTRY}.json.gz")
        self.assertEqual(b1.calls, [])

    def test_checksum_mismatch_raises(self):
        b1 = StubB1(self.files)
        table = table_for({"0": ("AECCAR0.gz", self.b0 + b"x"), "2": ("AECCAR2", self.b2)})
        src = rs.AeccarSource(b1, decompress, table)
        with self.assertRaisesRegex(RuntimeError, "checksum mismatch"):
            src.fetch(b1.BUCKET + f"aeccar0s/{ENTRY}.json.gz")

    def test_frozen_table_matches_manifest(self):
        man = {r["task_id"]: r for r in __import__("csv").DictReader(open(HERE / "manifest.csv", encoding="utf-8"))}
        tab = rs.read_sources(HERE / "aeccar_sources.csv")
        self.assertEqual(set(man), set(tab))
        for e, r in tab.items():
            self.assertEqual(r["material_id"], man[e]["material_id"])
            avail = r["aeccar_available"] == "1"
            self.assertEqual(avail, bool(r["aeccar0_path"]) and bool(r["aeccar2_path"]))
            if avail:
                self.assertEqual(r["aeccar0_ngrid"], man[e]["ngrid"])
                self.assertEqual(r["aeccar2_ngrid"], man[e]["ngrid"])

    def test_install_patches_runner_and_loader(self):
        dev = types.ModuleType("fake_dev_loader_for_test")
        dev.decompress_nomad = decompress
        dev.decode_mp_chgcar = lambda blob: ("mp", blob)
        old_b1 = rj.b1
        try:
            src = rs.install(rj, dev, self.table)
            self.assertIs(rj.b1, src)
            proxy = sys.modules["fake_dev_loader_for_test"]
            self.assertEqual(proxy.decode_mp_chgcar(b"abc"), ("mp", b"abc"))
        finally:
            rj.b1 = old_b1
            sys.modules.pop("fake_dev_loader_for_test", None)

    @unittest.skipUnless(HAVE_BADERKIT, "baderkit not installed")
    def test_parse_matches_nomad_chgcar_loader(self):
        """AECCAR text parses with the parser and units build_grid uses for a NOMAD CHGCAR."""
        from baderkit import Grid
        raw = vasp_text(self.f2)
        total = rs.parse_vasp_total(raw)
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "CHGCAR"
            p.write_bytes(raw)
            ref = np.asarray(Grid.from_dynamic(p).total, dtype=np.float64)
        self.assertEqual(total.shape, self.f2.shape)
        np.testing.assert_array_equal(total, ref)
        np.testing.assert_allclose(total, self.f2, rtol=1e-10)
        proxy = rs.nomad_aware_dev(types.SimpleNamespace(__name__="x", decode_mp_chgcar=None))
        np.testing.assert_array_equal(proxy.decode_mp_chgcar(rs.NomadVaspBytes(raw)).data["total"], ref)


if __name__ == "__main__":
    unittest.main()
