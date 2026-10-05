#!/usr/bin/env python3
from __future__ import annotations
import unittest
import numpy as np
import codec_qoac_h as q

class QoacHTests(unittest.TestCase):
    def setUp(self):
        rng=np.random.default_rng(123)
        self.field=2.0+0.2*rng.normal(size=(8,10,12))
        self.lattice=np.array([[5.1,0.2,0.0],[0.4,6.2,0.3],[0.1,0.5,7.4]])
    def test_roundtrip_stream_and_exact_special_modes(self):
        prep=q.prepare_field(self.field,self.lattice,shell_count=8)
        blob,stats=q.encode_prepared(prep,alpha=1e-2,beta=2.0,zlib_level=1)
        recon,frecon,header,dstats=q.decode_blob(blob,return_spectrum=True)
        self.assertEqual(recon.shape,self.field.shape)
        self.assertTrue(np.all(np.isfinite(recon)))
        self.assertEqual(header["beta"],2.0)
        self.assertGreater(stats["encoded_bytes"],0)
        self.assertGreaterEqual(dstats["decode_seconds"],0.0)
        special=~prep.active
        np.testing.assert_allclose(frecon[special],prep.spectrum[special],rtol=0.0,atol=0.0)
        self.assertAlmostEqual(float(np.mean(recon)),float(np.mean(self.field)),places=12)
    def test_beta_zero_is_constant_step(self):
        prep=q.prepare_field(self.field,self.lattice,shell_count=8)
        s=q.quantization_steps(prep,alpha=0.123,beta=0.0)
        np.testing.assert_allclose(s[prep.active],0.123,rtol=0.0,atol=0.0)
    def test_beta_two_tracks_g_squared(self):
        prep=q.prepare_field(self.field,self.lattice,shell_count=8)
        s=q.quantization_steps(prep,alpha=0.5,beta=2.0)
        idx=np.argwhere(prep.active); a=tuple(idx[0]); b=tuple(idx[len(idx)//2])
        self.assertAlmostEqual(float(s[a]/s[b]),float(prep.g2[a]/prep.g2[b]),places=12)
    def test_hartree_error_finite(self):
        prep=q.prepare_field(self.field,self.lattice,shell_count=8)
        blob,_=q.encode_prepared(prep,alpha=1e-2,beta=2.0,zlib_level=1)
        recon,_,_=q.decode_blob(blob)
        rh,rs=q.reference_hartree_rms(self.field,self.lattice)
        eh,es=q.hartree_error_metrics(recon-self.field,self.lattice,rh,rs)
        self.assertTrue(np.isfinite(eh) and eh>=0)
        self.assertTrue(np.isfinite(es) and es>=0)
if __name__=="__main__": unittest.main()
