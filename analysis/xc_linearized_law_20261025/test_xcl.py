"""xcl.py: v_xc is the derivative of xc.py's discrete PBE energy; the v0.3 streams decode within their steps."""
import unittest

import numpy as np

import xcl
from xcl import v02, v03, xc


def field(shape=(20, 18, 24), lat=None, seed=0):
    lat = np.diag([4.0, 3.6, 5.0]) if lat is None else lat
    rng = np.random.default_rng(seed)
    g = np.meshgrid(*[np.arange(n) / n for n in shape], indexing="ij")
    x = np.full(shape, 2.0)
    for _ in range(4):                                   # smooth periodic bumps on a background, CHGCAR units
        c, k = rng.random(3), rng.integers(1, 3, 3)
        x += 30.0 * np.exp(sum(np.cos(2 * np.pi * k[i] * (g[i] - c[i])) for i in range(3)) - 3.0)
    return x, lat


def e_pbe_au(total, lat):
    rho, dv = xc.density_au(total, lat)
    s = xc.grad_sq(rho, lat)
    ok = rho > xc.RHO_MIN
    return float(np.sum(rho[ok] * xc.eps_pbe(rho[ok], s[ok])) * dv), rho, dv


class Potential(unittest.TestCase):
    def test_directional_derivative(self):
        x, lat = field()
        _, rho, dv = e_pbe_au(x, lat)
        v = xcl.pbe_potential(x, lat)
        eta = np.random.default_rng(1).standard_normal(x.shape)
        eta = np.fft.ifftn(np.fft.fftn(eta) * (np.abs(np.fft.fftfreq(x.shape[0]))[:, None, None] < 0.3)).real
        conv = rho / x                                   # CHGCAR units -> bohr^-3, a constant
        t = 1e-4 * float(np.max(np.abs(x))) / float(np.max(np.abs(eta)))
        ep, _, _ = e_pbe_au(x + t * eta, lat)
        em, _, _ = e_pbe_au(x - t * eta, lat)
        fd = (ep - em) / (2 * t)
        an = float(np.sum(v * eta * conv) * dv)
        self.assertLess(abs(fd - an) / abs(an), 1e-6)

    def test_lda_limit(self):
        x, lat = field()
        rho, _ = xc.density_au(x, lat)                   # at zero gradient PBE is LDA: compare the f_rho part
        r = rho.ravel()[:50]
        f_rho = np.imag(xcl._f(r + 1j * xcl.H * r, np.zeros_like(r))) / (xcl.H * r)
        np.testing.assert_allclose(f_rho, xc._vxc_lda(r), rtol=1e-10)


class Stream(unittest.TestCase):
    def setUp(self):
        self.x, self.lat = field()
        self.prep = v02.prepare_field(self.x, self.lat, shell_count=32)
        self.ptp = float(np.ptp(self.x))
        self.W = xcl.shell_weights(self.prep, xcl.pbe_potential(self.x, self.lat))

    def test_weights_and_shape(self):
        self.assertEqual(self.W.shape, (32,))
        u = xcl.shape_of(self.W, "X")
        self.assertAlmostEqual(float(np.nanmin(u[np.isfinite(u)])), 1.0)
        self.assertTrue(np.all(xcl.shape_of(self.W, "F") == 1.0))

    def test_roundtrip_within_steps(self):
        for w in ("X", "F"):
            u = xcl.shape_of(self.W, w)
            a = 1e-4 * self.ptp
            rec = xcl.decode(xcl.encode(self.prep, self.ptp, u, a))
            err = np.fft.fftn(rec - self.x, norm="ortho").ravel()[self.prep.topology.rep_flat]
            st = (self.ptp * v03.LADDER_STEP ** xcl.ladder_index(a * u / self.ptp).astype(float))[self.prep.topology.shell_ids]
            self.assertTrue(np.all(np.abs(err.real) <= 0.5 * st * (1 + 1e-9) + 1e-12))
            self.assertAlmostEqual(float(rec.sum()), float(self.x.sum()), places=6)   # G = 0 stored exactly

    def test_drop_everything_keeps_the_mean(self):
        rec = xcl.decode(xcl.encode(self.prep, self.ptp, np.ones(32), 1e9 * self.ptp))
        np.testing.assert_allclose(rec, np.full_like(self.x, self.x.mean()), rtol=1e-12)

    def test_floor_fits_the_integer_range(self):
        u = xcl.shape_of(self.W, "X")
        f = xcl.alpha_floor(self.prep, u, self.ptp)
        rung = xcl.ladder_index(f * u / self.ptp).astype(float)
        st = self.ptp * v03.LADDER_STEP ** rung
        c = self.prep.spectrum.ravel()[self.prep.topology.rep_flat]
        q = np.abs(c.real) / st[self.prep.topology.shell_ids]
        self.assertLessEqual(float(q.max()), 0.95 * float(np.iinfo(np.int64).max))


if __name__ == "__main__":
    unittest.main()
