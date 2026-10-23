"""Before any T/O object counts: the aggregator reproduces the published whole-object estimates from the records."""
import tempfile
import unittest
from pathlib import Path

import run_archive_truncation as A

REPO = Path(__file__).resolve().parents[2]


class Aggregator(unittest.TestCase):
    def test_published_L_and_P(self):
        with tempfile.TemporaryDirectory() as ck, tempfile.TemporaryDirectory() as out:
            s = A.aggregate(Path(ck), REPO, Path(out))
        e = s["estimates"]
        self.assertAlmostEqual(e["L_1e-06"]["R"], 316.407836194927, places=6)
        self.assertEqual([round(x, 1) for x in e["L_1e-06"]["ci95"]], [290.4, 349.9])
        self.assertAlmostEqual(e["L_0.0001"]["R"], 1036.3, delta=0.05)
        self.assertAlmostEqual(e["P_1e-06"]["R"], 34.57, delta=0.005)
        self.assertAlmostEqual(s["paired"]["L/P_1e-06"]["ratio"], 9.153, delta=0.0005)
        for w in ("T", "O"):          # no checkpoint: every object counted at its json bytes
            self.assertEqual(e[f"{w}_1e-06"]["R"], 1.0)


if __name__ == "__main__":
    unittest.main()
