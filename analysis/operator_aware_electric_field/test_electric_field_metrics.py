#!/usr/bin/env python3
import unittest
import numpy as np
import electric_field_metrics as ef

class ElectricFieldMetricTests(unittest.TestCase):
    def test_single_mode_inverse_g_scaling(self):
        n=32
        x=np.arange(n,dtype=float)
        f1=np.cos(2*np.pi*x/n)[:,None,None]*np.ones((1,n,n))
        f2=np.cos(4*np.pi*x/n)[:,None,None]*np.ones((1,n,n))
        lat=np.diag([10.0,10.0,10.0])
        e1=ef.vector_rms(ef.electric_field_from_density(f1,lat,safe=True))
        e2=ef.vector_rms(ef.electric_field_from_density(f2,lat,safe=True))
        self.assertAlmostEqual(e1/e2,2.0,places=10)

    def test_safe_and_historical_agree_without_nyquist_content(self):
        n=24
        x=np.arange(n,dtype=float)
        f=np.cos(6*np.pi*x/n)[:,None,None]*np.ones((1,n,n))
        lat=np.array([[7.0,.2,0.0],[0.0,8.0,.1],[.1,0.0,9.0]])
        h=ef.vector_rms(ef.electric_field_from_density(f,lat,safe=False))
        s=ef.vector_rms(ef.electric_field_from_density(f,lat,safe=True))
        self.assertAlmostEqual(h/s,1.0,places=10)

if __name__=="__main__":
    unittest.main()
