"""Before any V object counts: the aggregator reproduces the published L and P estimates, counts writers without
checkpoints at their json bytes, and the partition fix rewrites the partition field on every decoded call."""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import whole_archive as A  # noqa: E402

REPO = Path(__file__).resolve().parents[2]


def _fix():
    spec = importlib.util.spec_from_file_location("run_fix", HERE.parent / "archive_partition_fix_20261025" / "run_fix.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Aggregator(unittest.TestCase):
    def test_published_estimates(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b, \
                tempfile.TemporaryDirectory() as c, tempfile.TemporaryDirectory() as out:
            s = A.aggregate(Path(a), Path(b), Path(c), REPO, Path(out))
        e = s["estimates"]
        self.assertAlmostEqual(e["L_1e-06"]["R"], 316.407836194927, places=6)
        self.assertAlmostEqual(e["L_0.0001"]["R"], 1036.3, delta=0.05)
        self.assertAlmostEqual(e["P_1e-06"]["R"], 34.57, delta=0.005)
        for w in ("V", "VP", "T", "O", "W", "Q"):     # no checkpoint: every object counted at its json bytes
            self.assertEqual(e[f"{w}_1e-06"]["R"], 1.0)


class PartitionFix(unittest.TestCase):
    def test_dec_rewrites_partition(self):
        fix = _fix()

        class Bader:                                   # the caching logic of run_spin_s1.Bader
            def __init__(self):
                self._ref_id, self.writes = None, 0

            def __call__(self, integrand, partition_field, ref_id):
                if ref_id != self._ref_id:
                    self.writes += 1
                    self._ref_id = ref_id
                return self.writes

        class S1:
            pass

        S1.Bader = Bader
        b = S1.Bader()
        b(0, 1, "dec"), b(0, 2, "dec")
        self.assertEqual(b.writes, 1)                  # the defect: the second decoded density reused the first
        fix.patch_bader(S1)
        b = S1.Bader()
        b(0, 1, "dec"), b(0, 2, "dec"), b(0, 3, "ref"), b(0, 3, "ref")
        self.assertEqual(b.writes, 3)                  # every "dec" call rewrites; other ids still cache


if __name__ == "__main__":
    unittest.main()
