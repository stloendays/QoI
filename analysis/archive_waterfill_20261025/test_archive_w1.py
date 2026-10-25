"""Before any W/Q object counts: the aggregator reproduces the published L, P, T and O whole-object estimates."""
import tempfile
import unittest
from pathlib import Path

import run_archive_w1 as A

REPO = Path(__file__).resolve().parents[2]


class Aggregator(unittest.TestCase):
    def test_published_estimates(self):
        with tempfile.TemporaryDirectory() as ck, tempfile.TemporaryDirectory() as out:
            s = A.aggregate(Path(ck), REPO, Path(out))
        e = s["estimates"]
        self.assertAlmostEqual(e["L_1e-06"]["R"], 316.407836194927, places=6)
        self.assertAlmostEqual(e["L_0.0001"]["R"], 1036.3, delta=0.05)
        self.assertAlmostEqual(e["P_1e-06"]["R"], 34.57, delta=0.005)
        self.assertAlmostEqual(e["T_1e-06"]["R"], 232.5, delta=0.05)
        self.assertAlmostEqual(e["O_1e-06"]["R"], 347.2, delta=0.05)
        self.assertAlmostEqual(e["T_0.0001"]["R"], 1142, delta=0.5)
        self.assertAlmostEqual(e["O_0.0001"]["R"], 1371, delta=0.5)
        self.assertEqual([round(x, 1) for x in e["O_1e-06"]["ci95"]], [317.1, 386.6])
        for w in ("W", "Q"):          # no checkpoint: every object counted at its json bytes
            self.assertEqual(e[f"{w}_1e-06"]["R"], 1.0)


if __name__ == "__main__":
    unittest.main()
