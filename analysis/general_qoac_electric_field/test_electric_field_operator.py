#!/usr/bin/env python3
from __future__ import annotations
import unittest
import numpy as np
import electric_field_operator as ef


class ElectricFieldOperatorTests(unittest.TestCase):
    def test_spectral_ratio_matches_explicit_vector_rms(self):
        rng=np.random.default_rng(20261005)
        x=rng.normal(size=(8,7,10))
        e=0.01*rng.normal(size=x.shape)
        lattice=np.array([[5.0,0.2,0.1],[0.4,6.0,0.3],[0.2,0.5,7.0]])
        # Nyquist-safe spectral differentiation has a unique real-space
        # vector-field representation and must close exactly.
        sx=ef.electric_field_energy(x,lattice,True)
        se=ef.electric_field_energy(e,lattice,True)
        ratio=(se/sx)**0.5
        explicit=ef.explicit_vector_rms(e,lattice,True)/ef.explicit_vector_rms(x,lattice,True)
        self.assertAlmostEqual(ratio,explicit,places=12)

    def test_constant_field_has_no_electric_field(self):
        x=np.ones((7,8,9))
        lattice=np.eye(3)*5.0
        self.assertLess(ef.electric_field_energy(x,lattice,False),1e-24)
        self.assertLess(ef.electric_field_energy(x,lattice,True),1e-24)

    def test_safe_energy_not_greater_than_historical(self):
        rng=np.random.default_rng(3)
        x=rng.normal(size=(8,10,12))
        lattice=np.array([[4.0,.2,.1],[.1,5.0,.4],[.2,.3,6.0]])
        h=ef.electric_field_energy(x,lattice,False)
        s=ef.electric_field_energy(x,lattice,True)
        self.assertLessEqual(s,h*(1+1e-14))


if __name__=="__main__":
    unittest.main()
