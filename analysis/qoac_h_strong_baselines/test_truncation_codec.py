import sys, unittest
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import truncation_codec as t1
qoac = t1.qoac

class T(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(0)
        self.x = rng.normal(size=(10, 12, 9))
        self.lat = np.array([[3.0, 0, 0], [0.7, 3.4, 0], [0.2, 0.3, 4.1]])
        self.p = qoac.prepare_field(self.x, self.lat)

    def test_full_cut_near_lossless(self):
        y = t1.decode(t1.encode(self.p, alpha=1e-9, q_cut=1.0))
        self.assertLess(np.max(np.abs(y - self.x)), 1e-8)

    def test_cut_equals_lowpass(self):
        qc = 0.4
        y = t1.decode(t1.encode(self.p, alpha=1e-12, q_cut=qc))
        topo = self.p.topology
        f = np.zeros(self.x.shape, complex).ravel(); s = self.p.spectrum.ravel()
        f[0] = s[0]; keep = topo.q <= qc
        f[topo.rep_flat[keep]] = s[topo.rep_flat[keep]]; f[topo.partner_flat[keep]] = s[topo.partner_flat[keep]]
        ref = np.fft.ifftn(f.reshape(self.x.shape), norm="ortho").real
        self.assertLess(np.max(np.abs(y - ref)), 1e-9)
        self.assertGreater(np.max(np.abs(y - self.x)), 1e-2)

if __name__ == "__main__":
    unittest.main()
