"""Data-free tests of the release source of the self-computed slab cohort (stdlib unittest; numpy; the parser parts
skip without baderkit / pymatgen). Covers routing, checksums, delegation, installation and the manifest tables."""
from __future__ import annotations

import csv
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
import run_joint_selfslab as rss  # noqa: E402

rs = rss.rs
rj = rs.load_hb_v2()
HAVE_BADERKIT = importlib.util.find_spec("baderkit") is not None
HAVE_PMG = importlib.util.find_spec("pymatgen") is not None
MID = "mp-testtest"
LAT = np.array([[4.0, 0.0, 0.0], [0.5, 5.0, 0.0], [0.0, 0.0, 12.0]])


def vasp_text(field: np.ndarray) -> bytes:
    """VASP volumetric file with VASP's fixed-width data format (5 x ' 0.12345678901E+00' per line)."""
    head = ["fabricated", "1.0", *(" ".join(f"{x:.10f}" for x in v) for v in LAT), "O Ti", "1 1", "Direct",
            "0.1 0.2 0.3", "0.6 0.5 0.4", "", " ".join(map(str, field.shape))]
    flat = field.ravel(order="F")
    body = ["".join(f" {v:.11E}" for v in flat[i:i + 5]) for i in range(0, flat.size, 5)]
    return ("\n".join(head + body) + "\n").encode()


def decompress(url: str, blob: bytes) -> bytes:
    return gzip.decompress(blob) if url.endswith(".gz") else blob


class StubB1:
    BUCKET = "https://materialsproject-parsed.s3.amazonaws.com/"

    def __init__(self, files):
        self.files, self.calls = files, []

    def fetch(self, url):
        self.calls.append(url)
        if url not in self.files:
            raise RuntimeError(f"download failed {url}")
        return self.files[url]


class TestReleaseSource(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(7)
        self.fields = {n: rng.random((4, 5, 6)) + 0.1 * (i + 1) for i, n in enumerate(rss.FILES)}
        self.blobs = {n: gzip.compress(vasp_text(f), mtime=0) for n, f in self.fields.items()}
        self.files = {rss.asset_url(MID, n): b for n, b in self.blobs.items()}
        self.files[StubB1.BUCKET + "aeccar0s/mp-1.json.gz"] = b"mp-aeccar0"
        self.files["https://example.org/other"] = b"other"
        self.table = {MID: {"material_id": MID, **{f"{n}_gz_bytes": str(len(b)) for n, b in self.blobs.items()},
                            **{f"{n}_gz_sha256": hashlib.sha256(b).hexdigest() for n, b in self.blobs.items()}}}

    def test_chgcar_url_is_served_as_downloaded(self):
        b1 = StubB1(self.files)
        src = rss.ReleaseSource(b1, decompress, self.table)
        blob = src.fetch(rss.asset_url(MID, "CHGCAR"))
        self.assertEqual(blob, self.blobs["CHGCAR"])
        self.assertNotIsInstance(blob, rs.NomadVaspBytes)
        self.assertEqual(b1.calls, [rss.RELEASE + f"{MID}__CHGCAR.gz"])
        self.assertEqual(src.log[0]["file"], "CHGCAR")

    def test_aeccar_bucket_keys_route_to_release_assets(self):
        b1 = StubB1(self.files)
        src = rss.ReleaseSource(b1, decompress, self.table)
        a0 = src.fetch(b1.BUCKET + f"aeccar0s/{MID}.json.gz")
        a2 = src.fetch(b1.BUCKET + f"aeccar2s/{MID}.json.gz")
        self.assertIsInstance(a0, rs.NomadVaspBytes)
        self.assertEqual(bytes(a0), gzip.decompress(self.blobs["AECCAR0"]))
        self.assertEqual(bytes(a2), gzip.decompress(self.blobs["AECCAR2"]))
        self.assertEqual(b1.calls, [rss.RELEASE + f"{MID}__AECCAR0.gz", rss.RELEASE + f"{MID}__AECCAR2.gz"])
        self.assertEqual([r["file"] for r in src.log], ["AECCAR0", "AECCAR2"])

    def test_other_urls_and_ids_are_untouched(self):
        b1 = StubB1(self.files)
        src = rss.ReleaseSource(b1, decompress, self.table)
        self.assertEqual(src.fetch(b1.BUCKET + "aeccar0s/mp-1.json.gz"), b"mp-aeccar0")
        self.assertEqual(src.fetch("https://example.org/other"), b"other")
        self.assertIs(src.BUCKET, b1.BUCKET)
        self.assertEqual(src.log, [])

    def test_byte_count_mismatch_raises(self):
        for name in rss.FILES:
            files = dict(self.files)
            files[rss.asset_url(MID, name)] = self.blobs[name] + b"x"
            b1 = StubB1(files)
            src = rss.ReleaseSource(b1, decompress, self.table)
            url = rss.asset_url(MID, "CHGCAR") if name == "CHGCAR" else b1.BUCKET + f"aeccar{name[-1]}s/{MID}.json.gz"
            with self.assertRaisesRegex(RuntimeError, f"{name} checksum mismatch"):
                src.fetch(url)

    def test_sha256_mismatch_raises(self):
        files = dict(self.files)
        b = bytearray(self.blobs["AECCAR2"])
        b[-1] ^= 1
        files[rss.asset_url(MID, "AECCAR2")] = bytes(b)
        b1 = StubB1(files)
        src = rss.ReleaseSource(b1, decompress, self.table)
        with self.assertRaisesRegex(RuntimeError, "AECCAR2 checksum mismatch"):
            src.fetch(b1.BUCKET + f"aeccar2s/{MID}.json.gz")

    def test_install_patches_runner_and_loader(self):
        dev = types.ModuleType("fake_dev_loader_for_selfslab_test")
        dev.decompress_nomad = decompress
        dev.decode_mp_chgcar = lambda blob: ("mp", blob)
        dev.build_grid = lambda meta, blob, workdir: ("base", meta["source"])
        old_b1 = rj.b1
        try:
            src = rss.install(rj, dev, self.table)
            self.assertIs(rj.b1, src)
            proxy = sys.modules["fake_dev_loader_for_selfslab_test"]
            self.assertEqual(proxy.decode_mp_chgcar(b"abc"), ("mp", b"abc"))
            self.assertEqual(proxy.build_grid({"source": "Materials Project"}, b"", "."), ("base", "Materials Project"))
        finally:
            rj.b1 = old_b1
            sys.modules.pop("fake_dev_loader_for_selfslab_test", None)

    @unittest.skipUnless(HAVE_BADERKIT and HAVE_PMG, "baderkit or pymatgen not installed")
    def test_parsers_match_hb_v2_vasp_chgcar_route(self):
        """CHGCAR and AECCARs are decompressed and parsed exactly as dev.build_grid parses a VASP CHGCAR."""
        sys.path.insert(0, str(HERE.parents[1] / "validation" / "qsq_prospective"))
        import development_compatibility_smoke as dev
        proxy = rss.selfslab_dev(dev)
        url = rss.asset_url(MID, "CHGCAR")
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
            g_self, loader = proxy.build_grid({"source": rss.SOURCE, "url": url}, self.blobs["CHGCAR"], Path(td))
            ours = np.asarray(g_self.total, dtype=np.float64)
            del g_self
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as td:
            g_ref, _ = dev.build_grid({"source": "NOMAD surfaces/adsorbates", "url": url}, self.blobs["CHGCAR"], Path(td))
            ref = np.asarray(g_ref.total, dtype=np.float64)
            del g_ref
        self.assertEqual(loader, "selfslab_release_gz_decompress_to_baderkit_grid")
        np.testing.assert_array_equal(ours, ref)
        np.testing.assert_allclose(ours, self.fields["CHGCAR"], rtol=1e-10)
        src = rss.ReleaseSource(StubB1(self.files), dev.decompress_nomad, self.table)
        a0 = src.fetch(StubB1.BUCKET + f"aeccar0s/{MID}.json.gz")
        np.testing.assert_allclose(proxy.decode_mp_chgcar(a0).data["total"], self.fields["AECCAR0"], rtol=1e-10)


class TestCohortTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cohort = list(csv.DictReader(open(HERE / "cohort.csv", encoding="utf-8")))
        cls.man = list(csv.DictReader(open(HERE / "manifest.csv", encoding="utf-8")))
        cls.qc = {r["material_id"]: r for r in csv.DictReader(open(HERE / "qc" / "qc.csv", encoding="utf-8"))}
        cls.drawn = list(csv.DictReader(open(HERE / "selection" / "drawn.csv", encoding="utf-8")))
        cls.status = {r["material_id"]: r for r in csv.DictReader(open(HERE / "runs" / "STATUS.csv", encoding="utf-8"))}

    def test_manifest_matches_cohort_in_order(self):
        self.assertEqual(len(self.man), 32)
        self.assertEqual([r["material_id"] for r in self.man], [r["material_id"] for r in self.cohort])
        for m, c in zip(self.man, self.cohort):
            self.assertEqual(m["task_id"], m["material_id"])
            self.assertEqual(m["source"], rss.SOURCE)
            self.assertEqual(m["system_type"], "slab")
            self.assertEqual(m["url"], rss.asset_url(m["material_id"], "CHGCAR"))
            self.assertEqual(m["sha256"], c["CHGCAR_gz_sha256"])
            self.assertEqual(m["source_bytes"], c["CHGCAR_gz_bytes"])
            self.assertEqual(m["ngrid"], c["ngrid"])
            self.assertEqual(m["selection_hash"],
                             hashlib.sha256(("QOAC-HB-SELFSLAB-20261007|" + m["material_id"]).encode()).hexdigest())

    def test_cohort_is_first_32_converged_and_qc_pass_in_draw_order(self):
        ok = [r["material_id"] for r in self.drawn
              if self.status[r["material_id"]]["status"].startswith("converged")
              and self.qc.get(r["material_id"], {}).get("qc_pass") == "1"]
        self.assertEqual([r["material_id"] for r in self.cohort], ok[:32])
        self.assertEqual(len({r["reduced_formula"] for r in self.cohort}), 32)

    def test_cohort_checksums_match_qc_and_table_routes_every_file(self):
        table = rss.read_cohort(HERE / "cohort.csv")
        for c in self.cohort:
            for n in rss.FILES:
                self.assertEqual(c[f"{n}_sha256"], self.qc[c["material_id"]][f"{n}_sha256"])
                self.assertEqual(c[f"{n}_gz_sha256"], self.qc[c["material_id"]][f"{n}_gz_sha256"])
                self.assertRegex(table[c["material_id"]][f"{n}_gz_sha256"], r"^[0-9a-f]{64}$")

    def test_shard_load(self):
        loads = {}
        for m in self.man:
            s = rj.shard_for(m["material_id"], 19)
            loads[s] = loads.get(s, 0) + 1
        self.assertLessEqual(max(loads.values()), 4)


if __name__ == "__main__":
    unittest.main()
