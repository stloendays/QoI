import csv
import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vacuum_level as vl  # noqa: E402

TRICLINIC = np.array([[4.0, 0.0, 0.0], [1.1, 4.4, 0.0], [0.3, 0.6, 25.2]])


def frac_grid(shape):
    f = [np.arange(n) / n for n in shape]
    return np.meshgrid(*f, indexing="ij")


class Units(unittest.TestCase):
    def analytic(self, lat, shape, m, amp=0.37):
        """rho = A cos(G0 . r) with G0 = m . b; returns CHGCAR-unit field and the analytic V (eV)."""
        f = frac_grid(shape)
        phase = 2.0 * np.pi * (m[0] * f[0] + m[1] * f[1] + m[2] * f[2])     # G0 . r
        g0 = m[0] * vl.reciprocal_vectors(lat)[0] + m[1] * vl.reciprocal_vectors(lat)[1] + m[2] * vl.reciprocal_vectors(lat)[2]
        rho = amp * np.cos(phase)
        v = 4.0 * np.pi * vl.K_E * amp * np.cos(phase) / float(g0 @ g0)
        return rho * vl.cell_volume(lat), v

    def test_cosine_orthorhombic(self):
        lat = np.diag([5.0, 6.0, 30.0])
        x, v = self.analytic(lat, (10, 12, 60), (1, 0, 0))
        np.testing.assert_allclose(vl.hartree_potential_ev(x, lat), v, rtol=0, atol=1e-10 * np.abs(v).max())
        # explicit numbers: |G0| = 2 pi / 5 A^-1, A = 0.37 e/A^3
        self.assertAlmostEqual(np.abs(v).max(), 4 * math.pi * 14.399645 * 0.37 / (2 * math.pi / 5.0) ** 2, places=9)

    def test_cosine_triclinic_mixed(self):
        for m in ((1, 0, 0), (0, 0, 3), (2, -1, 3), (1, 1, -2)):
            x, v = self.analytic(TRICLINIC, (12, 14, 64), m)
            np.testing.assert_allclose(vl.hartree_potential_ev(x, TRICLINIC), v, rtol=0, atol=1e-10 * np.abs(v).max())

    def test_planar_cosine(self):
        for axis, m in ((2, (0, 0, 2)), (0, (3, 0, 0)), (1, (0, 1, 0))):
            x, v = self.analytic(TRICLINIC, (12, 14, 64), m)
            vp = vl.planar_hartree_ev(x, TRICLINIC, axis)
            np.testing.assert_allclose(vp, vl.planar_average(v, axis), rtol=0, atol=1e-10 * np.abs(v).max())

    def test_planar_equals_plane_average_of_3d(self):
        rng = np.random.default_rng(7)
        x = rng.normal(size=(10, 12, 40))
        v3 = vl.hartree_potential_ev(x, TRICLINIC)
        for axis in range(3):
            np.testing.assert_allclose(vl.planar_hartree_ev(x, TRICLINIC, axis), vl.planar_average(v3, axis),
                                       rtol=0, atol=1e-11 * np.abs(v3).max())

    def test_uniform_field_has_zero_potential(self):
        x = np.full((8, 8, 20), 3.0)
        self.assertLess(np.abs(vl.hartree_potential_ev(x, TRICLINIC)).max(), 1e-12)
        self.assertLess(np.abs(vl.planar_hartree_ev(x, TRICLINIC, 2)).max(), 1e-12)

    def test_spacing(self):
        lat = np.diag([5.0, 6.0, 30.0])
        self.assertAlmostEqual(vl.interplanar_spacing(lat, 2), 30.0)
        self.assertAlmostEqual(vl.interplanar_spacing(TRICLINIC, 2), vl.cell_volume(TRICLINIC) / np.linalg.norm(np.cross(TRICLINIC[0], TRICLINIC[1])))


def synthetic_slab(shape=(12, 12, 120), c=30.0, centre=0.5, half_width=4.0, decay=2.0):
    lat = np.array([[4.0, 0.0, 0.0], [1.5, 4.0, 0.0], [0.0, 0.0, c]])
    f = frac_grid(shape)
    z = ((f[2] - centre + 0.5) % 1.0 - 0.5) * c                  # signed distance from slab centre (A)
    rho = np.where(np.abs(z) <= half_width, 0.5, 0.5 * np.exp(-decay * (np.abs(z) - half_width)))
    rho = rho * (1.0 + 0.2 * np.cos(2 * np.pi * f[0]) * np.cos(2 * np.pi * f[1]))
    return rho * vl.cell_volume(lat), lat


class Vacuum(unittest.TestCase):
    def test_slab_normal_and_window(self):
        x, lat = synthetic_slab()
        w = vl.vacuum_window(x, lat)
        self.assertTrue(w["qualifies"])
        self.assertEqual(w["normal_axis"], 2)
        # vacuum where 0.5 exp(-2 d) < 0.5e-3 * 1.2 max factor -> d > ~3.36 A beyond the 4 A half width
        self.assertGreater(w["run_A"], 10.0)
        self.assertLess(w["run_A"], 16.0)
        self.assertAlmostEqual(w["window_planes"], w["run_planes"] - 2 * (w["run_planes"] // 4))
        z = (w["window_index"] / x.shape[2] - 0.5) * 30.0
        self.assertTrue(np.all(np.abs(np.abs(z) - 15.0) < 0.6 * w["run_A"] / 2 + 1e-9))   # window sits mid-vacuum

    def test_window_wraps_periodically(self):
        x, lat = synthetic_slab(centre=0.5)
        y, _ = synthetic_slab(centre=0.0)                       # slab across the cell boundary... vacuum in the middle
        a, b = vl.vacuum_window(x, lat), vl.vacuum_window(y, lat)
        self.assertEqual(a["run_planes"], b["run_planes"])
        self.assertEqual(a["window_planes"], b["window_planes"])
        self.assertTrue(set(((a["window_index"] + 60) % 120).tolist()) == set(b["window_index"].tolist()))

    def test_no_vacuum(self):
        rng = np.random.default_rng(3)
        x = 1.0 + 0.1 * rng.random((10, 10, 30))
        w = vl.vacuum_window(x, TRICLINIC)
        self.assertFalse(w["qualifies"])
        self.assertEqual(w["run_planes"], 0)
        self.assertTrue(all(math.isnan(v) for v in vl.vacuum_shift(x - 1.0, TRICLINIC, w)))

    def test_thin_vacuum_rejected(self):
        x, lat = synthetic_slab(shape=(8, 8, 60), c=12.0, half_width=3.0)
        self.assertFalse(vl.vacuum_window(x, lat)["qualifies"])

    def test_longest_run(self):
        self.assertEqual(vl._longest_periodic_run(np.array([1, 1, 0, 1, 1, 0, 1, 1], bool)), (4, 6))   # wraps 6,7,0,1
        self.assertEqual(vl._longest_periodic_run(np.array([1, 1, 0, 1, 1, 1, 0, 1], bool)), (3, 3))   # tie: first after a solid plane
        self.assertEqual(vl._longest_periodic_run(np.array([0, 1, 1, 0, 1, 1], bool)), (2, 1))

    def test_constant_shift_is_dphi(self):
        """A dipole-free error whose planar average is flat in the window gives Delta Phi = that plateau."""
        x, lat = synthetic_slab()
        w = vl.vacuum_window(x, lat)
        rng = np.random.default_rng(5)
        d = rng.normal(size=x.shape)
        d -= vl.planar_average(d, 2)[None, None, :]             # zero planar average -> zero planar potential
        dphi, dmax = vl.vacuum_shift(d, lat, w)
        self.assertLess(abs(dphi), 1e-9)
        self.assertLess(dmax, 1e-9)


class Stats(unittest.TestCase):
    def test_summarize(self):
        s = vl.summarize([-0.5, 2.0, 0.9, 30.0, -12.0])
        self.assertEqual(s["n"], 5)
        self.assertAlmostEqual(s["median"], 2.0)
        self.assertAlmostEqual(s["max"], 30.0)
        self.assertAlmostEqual(s["p95"], float(np.quantile([0.5, 0.9, 2.0, 12.0, 30.0], 0.95)))
        self.assertEqual(s["n_lt_1meV"], 2)
        self.assertAlmostEqual(s["frac_lt_10meV"], 3 / 5)

    def test_empty(self):
        s = vl.summarize([])
        self.assertEqual(s["n"], 0)
        self.assertTrue(math.isnan(s["median"]))


class Streams(unittest.TestCase):
    def setUp(self):
        sys.path.insert(0, str(HERE.parent / "qoac_v03_rdo"))
        import run_vacuum_level as rv
        self.rv = rv

    def test_selection_and_params(self):
        rows = [
            {"material_id": "m", "arm": "A2", "tau": "1e-06", "param": "q_cut=0.09375;alpha_rel=0.00264161672", "bytes": "900", "cr": "10", "certified": "True"},
            {"material_id": "m", "arm": "A2", "tau": "1e-06", "param": "q_cut=0.125;alpha_rel=0.0039", "bytes": "800", "cr": "11.25", "certified": "True"},
            {"material_id": "m", "arm": "A2", "tau": "1e-06", "param": "q_cut=0.15625;alpha_rel=0.0039", "bytes": "800", "cr": "11.25", "certified": "True"},
            {"material_id": "m", "arm": "A6", "tau": "0.0001", "param": "codec=sz3;abs_tol_rel=1e-4", "bytes": "50", "cr": "180", "certified": "False"},
            {"material_id": "m", "arm": "A6", "tau": "0.0001", "param": "codec=zfp;abs_tol_rel=1e-3", "bytes": "60", "cr": "150", "certified": "True"},
            {"material_id": "m", "arm": "A0", "tau": "0.0001", "param": "alpha_rel=1", "bytes": "1", "cr": "9000", "certified": "True"},
            {"material_id": "other", "arm": "A1", "tau": "0.0001", "param": "alpha_rel=1", "bytes": "1", "cr": "9000", "certified": "True"},
        ]
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "rows.csv"
            with p.open("w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(rows)
            s = self.rv.certified_streams(p, "m")
        self.assertEqual(set(s), {("A2", 1e-6), ("A6", 1e-4)})
        self.assertEqual(s[("A2", 1e-6)]["param"], "q_cut=0.125;alpha_rel=0.0039")       # first of the tied best
        self.assertEqual(self.rv.parse_param(s[("A6", 1e-4)]["param"]), {"codec": "zfp", "abs_tol_rel": "1e-3"})
        self.assertEqual(float("0.09375") * 32, 3.0)

    def test_reproduction_check(self):
        rec = {"bytes": "1000", "hartree_hist": "9.95e-07", "hartree_safe": "9.9e-07"}
        self.assertEqual(self.rv.check(1000, 9.95e-07, 9.9e-07, rec, 1e-6), (True, True))
        self.assertEqual(self.rv.check(1016, 9.95e-07 * (1 + 9e-7), 9.9e-07, rec, 1e-6), (True, False))
        self.assertEqual(self.rv.check(1017, 9.95e-07, 9.9e-07, rec, 1e-6), (False, False))           # bytes
        self.assertEqual(self.rv.check(1000, 9.95e-07 * (1 + 2e-6), 9.9e-07, rec, 1e-6), (False, False))  # error
        rec2 = {"bytes": "1000", "hartree_hist": "1e-06", "hartree_safe": "9.9e-07"}
        self.assertEqual(self.rv.check(1000, 1e-06, 9.9e-07, rec2, 1e-6), (False, True))         # not certified

    def test_margin(self):
        self.assertEqual(self.rv.margin_value("0.9950"), 0.995)
        self.assertEqual(self.rv.margin_value("0.9900"), 0.995 * 0.995)
        with self.assertRaises(ValueError):
            self.rv.margin_value("0.5000")


if __name__ == "__main__":
    unittest.main()
