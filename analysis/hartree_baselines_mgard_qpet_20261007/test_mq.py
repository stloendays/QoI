import math
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import codecs_mq as C  # noqa: E402
import run_mq as R  # noqa: E402
import aggregate_mq as A  # noqa: E402


class Search(unittest.TestCase):
    def fake(self, err_below=0.0):
        """bytes fall and error rises with the tolerance; execution error below err_below."""
        calls = []

        def ev(t):
            calls.append(t)
            if t < err_below:
                return None
            return {"bytes": int(1e6 / (1 + t)), "hartree_hist": t * 1e-3, "hartree_safe": t * 1e-3}
        return ev, calls

    def test_highest_ratio_passing_point(self):
        ev, calls = self.fake()
        best, seen, skipped = R.search(ev, 1e-6, 1e-14, 1e3, 1e-2)
        self.assertEqual(skipped, 0)
        self.assertTrue(all(v["hartree_hist"] < 1e-6 for v in seen.values()))
        self.assertEqual(best, max(seen))                    # fewest bytes = largest passing tolerance here
        self.assertAlmostEqual(best, 1e-3, delta=1e-3 * 1e-6)
        self.assertLessEqual(len(calls), 2 + R.eng.BISECT_ITERS)

    def test_execution_error_raises_lower_bound_by_decades(self):
        ev, _ = self.fake(err_below=3e-12)
        best, seen, skipped = R.search(ev, 1e-6, 1e-14, 1e3, 1e-2)
        self.assertEqual(skipped, 3)
        self.assertIsNotNone(best)

    def test_never_executes(self):
        best, seen, skipped = R.search(lambda t: None, 1e-6, 1e-14, 1e3, 1e-2)
        self.assertIsNone(best); self.assertEqual(skipped, -1)

    def test_certificate_fail_at_lower_bound_is_never_certified(self):
        ev = lambda t: {"bytes": 10, "hartree_hist": 1.0, "hartree_safe": 1.0}
        best, seen, skipped = R.search(ev, 1e-6, 1e-14, 1e3, 1e-2)
        self.assertIsNone(best); self.assertEqual(skipped, 0); self.assertEqual(seen, {})


class Codecs(unittest.TestCase):
    def test_dims_fastest_first(self):
        self.assertEqual(C.fastest_first((20, 28, 36)), ["36", "28", "20"])

    def test_hpez_commands(self):
        comp, deco = C.hpez_commands("hpez", "hpez", 8, (2, 3, 4), 5.0, 1e-3, "i", "c", "o", "q.cfg")
        self.assertEqual(comp[:3], ["hpez", "-q", "3"])
        self.assertEqual(comp[comp.index("-3") + 1:comp.index("-3") + 4], ["4", "3", "2"])
        self.assertEqual(comp[-4:], ["-m", "ABS", "-e", "0.001"])   # value via -e (the CLI does not parse '-m ABS <v>')
        self.assertEqual(comp[comp.index("-M") + 1:comp.index("-M") + 3], ["ABS", "5.0"])
        self.assertIn("-q", C.hpez_commands("hpez", "sz3", 8, (2, 3, 4), 5.0, 1e-3, "i", "c", "o", "q")[0])
        self.assertEqual(C.hpez_commands("hpez", "sz3", 8, (2, 3, 4), 5.0, 1e-3, "i", "c", "o", "q")[0][2], "0")

    def test_sperr_commands(self):
        comp, _ = C.sperr_commands("sperr3d", 16, (2, 3, 4), 5.0, 1e-3, "i", "c", "o")
        self.assertEqual(comp[comp.index("--dims") + 1:comp.index("--dims") + 4], ["4", "3", "2"])
        self.assertEqual(comp[comp.index("--qoi_bs") + 1], "16")
        self.assertEqual(comp[comp.index("--ftype") + 1], "64")

    def test_config(self):
        t = C.qpet_sz_config(8)
        for s in ("qoi = 14", "qoi_string = x", "qoiRegionMode = 1", "qoiRegionSize = 8"):
            self.assertIn(s, t)

    def test_block_means(self):
        a = np.random.default_rng(0).normal(size=(5, 6, 7)); b = 4
        m = C.block_means(a, b)
        self.assertEqual(m.shape, (2, 2, 2))
        self.assertAlmostEqual(m[1, 0, 1], a[4:5, 0:4, 4:7].mean())
        self.assertAlmostEqual(m[0, 1, 0], a[0:4, 4:6, 0:4].mean())

    def test_config_list(self):
        cf = R.configs({"M", "Q"})
        self.assertEqual(len(cf), 4 + 9)
        self.assertEqual(sorted(l for a, l, _ in cf if a == "M"), sorted(A.M_COLS))
        self.assertEqual(sorted(l for a, l, _ in cf if a == "Q"), sorted(A.Q_COLS))


class Aggregate(unittest.TestCase):
    def setUp(self):
        ids = ["a", "b", "c", "d"]
        self.ids = ids
        law = pd.DataFrame([{"material_id": m, "tau": t, "A1": 100.0, "A2": 50.0, "A3": 120.0, "A6": 10.0}
                            for m in ids for t in (1e-4, 1e-6, 1e-8)])
        rows = []
        for m in ids:
            for t in (1e-4, 1e-6, 1e-8):
                for col in A.M_COLS + A.Q_COLS:
                    cert = not (m == "d" and col.startswith("Q"))         # d: Q never certifies
                    cr = {"a": 50.0, "b": 200.0, "c": 80.0, "d": 40.0}[m] if cert else np.nan
                    if col == "M_s=-2":
                        cr = cr / 2
                    rows.append({"material_id": m, "tau": t, "config": col, "certified": cert, "cr": cr,
                                 "search_seconds": 1.0, "lo_decades_skipped": 0})
        self.rows = pd.DataFrame(rows); self.law = law

    def test_wide_and_ratios(self):
        tab = A.wide_table(self.rows, self.law, self.ids)
        ran = A.ran_table(self.rows, self.ids)
        tt = tab.xs(1e-6, level="tau"); rt = ran.xs(1e-6, level="tau")
        self.assertEqual(tt.loc["b", "Mbest"], 200.0); self.assertEqual(tt.loc["b", "M2"], 100.0)
        self.assertTrue(math.isnan(tt.loc["d", "Q"]))
        s = A.ratio_stats(tt, rt, "A1", "Q")
        self.assertEqual(s["n_both_certified"], 3)                # d dropped from the median (aggregate_law convention)
        self.assertEqual(s["baseline_never_certified"], 1)
        self.assertEqual(s["wins"], 2)                            # a (2.0) and c (1.25); b is 0.5
        self.assertEqual(s["wins_incl_never_certified"], 3)
        self.assertAlmostEqual(s["median"], 1.25)
        self.assertEqual(s["ci95"], A.boot(np.array([2.0, 0.5, 1.25])))

    def test_not_run_is_not_never_certified(self):
        rows = self.rows[~((self.rows.material_id == "d") & self.rows.config.str.startswith("Q"))]
        tab = A.wide_table(rows, self.law, self.ids); ran = A.ran_table(rows, self.ids)
        s = A.ratio_stats(tab.xs(1e-6, level="tau"), ran.xs(1e-6, level="tau"), "A1", "Q")
        self.assertEqual(s["baseline_never_certified"], 0); self.assertEqual(s["baseline_not_run"], 1)

    def test_m2_infeasible_excluded_from_mbest(self):
        tab = A.wide_table(self.rows, self.law, self.ids, m2_feasible=False)
        self.assertTrue(tab.M2.isna().all())
        self.assertEqual(tab.xs(1e-6, level="tau").loc["a", "Mbest"], 50.0)

    def test_boot_reproducible(self):
        x = np.array([1.0, 2.0, 3.0, 4.0, 10.0])
        self.assertEqual(A.boot(x), A.boot(x))


class Inputs(unittest.TestCase):
    def test_input_hashes(self):
        self.assertEqual(R.check_inputs(HERE.parents[1]), [])

    def test_matrix(self):
        m = R.matrix(HERE.parents[1], "run")
        self.assertEqual(len(m), 92)
        self.assertEqual(len({x["id"] for x in m}), 92)
        self.assertEqual(R.matrix(HERE.parents[1], "probe"), [{"manifest": R.SHAKEDOWN[0], "id": "mp-3148759"}])


if __name__ == "__main__":
    unittest.main()
