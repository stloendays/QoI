"""xc.py: PW92 reference values, PBE -> LDA at zero gradient, V_xc^LDA = d(rho eps)/d rho, electron count."""
import math
import unittest

import numpy as np

import xc


class XC(unittest.TestCase):
    def test_pw92(self):
        self.assertAlmostEqual(float(xc._pw92(np.array([1.0]))[0]), -0.0597739, places=6)
        self.assertAlmostEqual(float(xc._pw92(np.array([2.0]))[0]), -0.0447596, places=6)

    def test_pbe_zero_gradient(self):
        r = np.logspace(-6, 1, 50)
        np.testing.assert_allclose(xc.eps_pbe(r, np.zeros_like(r)), xc.eps_lda(r), rtol=1e-14)

    def test_vxc_derivative(self):
        r, h = np.logspace(-6, 1, 50), 1e-6
        f = lambda z: z * xc.eps_lda(z)  # noqa: E731
        np.testing.assert_allclose((f(r * (1 + h)) - f(r * (1 - h))) / (2 * r * h), xc._vxc_lda(r), rtol=1e-7)

    def test_uniform_gas_energy(self):
        lat = np.eye(3) * 4.0
        n = 10.0                             # 10 electrons in 64 A^3: CHGCAR value = rho * V_cell
        e = xc.exc_energies(np.full((16, 16, 16), n), lat, natoms=1)
        rho = 10 / 64.0 * xc.BOHR ** 3
        want = rho * float(xc.eps_lda(np.array([rho]))[0]) * 64.0 / xc.BOHR ** 3 * xc.HARTREE_EV
        self.assertAlmostEqual(e["E_lda_eV_per_atom"], want, places=9)
        self.assertAlmostEqual(e["E_pbe_eV_per_atom"], want, places=9)


if __name__ == "__main__":
    unittest.main()
