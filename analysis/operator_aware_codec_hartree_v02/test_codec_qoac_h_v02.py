#!/usr/bin/env python3
from __future__ import annotations
import unittest
import numpy as np
import codec_qoac_h_v02 as q

class QoacHV02Tests(unittest.TestCase):
    def setUp(self):
        rng=np.random.default_rng(1234)
        self.field=1.5+0.1*rng.normal(size=(8,10,12))
        self.lattice=np.array([[5.1,0.2,0.0],[0.4,6.2,0.3],[0.1,0.5,7.4]],dtype=float)

    def test_orbit_roundtrip_and_hermitian_invariant(self):
        prep=q.prepare_field(self.field,self.lattice,shell_count=8)
        blob,stats=q.encode_prepared(prep,alpha=1e-2,beta=2.0,zlib_level=1)
        recon,frecon,header,dstats=q.decode_blob(blob,return_spectrum=True)
        topo=prep.topology
        self.assertEqual(stats["exact_modes"],1)
        self.assertEqual(header["beta"],2.0)
        self.assertTrue(np.all(np.isfinite(recon)))
        np.testing.assert_allclose(
            frecon.ravel()[topo.partner_flat],
            np.conj(frecon.ravel()[topo.rep_flat]),
            rtol=0.0,atol=1e-13
        )
        self.assertLess(dstats["imaginary_leakage_max"],1e-11)

    def test_safe_nyquist_metric_is_conservative(self):
        safe=q.conservative_g2(self.field.shape,self.lattice)
        b=2*np.pi*np.linalg.inv(self.lattice).T
        ns=[np.fft.fftfreq(n)*n for n in self.field.shape]
        a,c,d=np.meshgrid(*ns,indexing="ij")
        g=a[...,None]*b[0]+c[...,None]*b[1]+d[...,None]*b[2]
        hist=np.einsum("...k,...k->...",g,g)
        self.assertTrue(np.all(safe<=hist+1e-10))
        self.assertGreater(int(np.count_nonzero(safe<hist-1e-8)),0)

    def test_beta_two_tracks_safe_g_squared(self):
        topo=q.build_topology(self.field.shape,self.lattice,shell_count=8)
        s=q.quantization_steps(topo,alpha=0.5,beta=2.0)
        i,j=0,len(s)//2
        self.assertAlmostEqual(float(s[i]/s[j]),float(topo.g2_safe_rep[i]/topo.g2_safe_rep[j]),places=12)

    def test_only_dc_is_exact_and_floor_collapses(self):
        field=np.ones((32,32,32),dtype=float)
        field[3,5,7]+=0.25
        prep=q.prepare_field(field,np.diag([8.0,9.0,10.0]),shell_count=16)
        blob,stats=q.encode_prepared(prep,alpha=1e12,beta=2.0,zlib_level=6)
        self.assertEqual(stats["exact_modes"],1)
        self.assertGreater(field.nbytes/len(blob),10.0)

    def test_alpha_changes_reconstruction_and_hartree_is_finite(self):
        prep=q.prepare_field(self.field,self.lattice,shell_count=8)
        b1,_=q.encode_prepared(prep,alpha=1e-3,beta=2.0,zlib_level=1)
        b2,_=q.encode_prepared(prep,alpha=1e-1,beta=2.0,zlib_level=1)
        r1,_,_=q.decode_blob(b1)
        r2,_,_=q.decode_blob(b2)
        self.assertGreater(float(np.max(np.abs(r1-r2))),0.0)
        rh,rs=q.reference_hartree_rms(self.field,self.lattice)
        eh,es=q.hartree_error_metrics(r1-self.field,self.lattice,rh,rs)
        self.assertTrue(np.isfinite(eh) and eh>=0.0)
        self.assertTrue(np.isfinite(es) and es>=0.0)

if __name__=="__main__":
    unittest.main()
