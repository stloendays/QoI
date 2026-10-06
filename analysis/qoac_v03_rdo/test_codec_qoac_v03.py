import sys, unittest
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import codec_qoac_v03 as v3
v02 = v3.v02

def synth(shape=(24, 20, 28), seed=0):
    rng = np.random.default_rng(seed)
    lat = np.array([[4.0, 0, 0], [1.1, 4.4, 0], [0.3, 0.6, 5.2]])
    k = [np.fft.fftfreq(n) * n for n in shape]
    g = np.sqrt(k[0][:, None, None] ** 2 + k[1][None, :, None] ** 2 + k[2][None, None, :] ** 2)
    spec = (rng.normal(size=shape) + 1j * rng.normal(size=shape)) / (1 + g) ** 3
    x = np.fft.ifftn(spec).real
    return x - x.min() + 0.1, lat

class T(unittest.TestCase):
    def test_certificate_and_closure(self):
        x, lat = synth()
        rh, rs = v02.reference_hartree_rms(x, lat)
        for prior in ("operator", "flat"):
            an = v3.analyze(x, lat, prior=prior, reference_historical_rms=rh)
            for tau in (1e-3, 1e-5):
                ch = v3.select(an, tau)
                blob = v3.encode(an, ch)
                y = v3.decode(blob)
                eh, es = v02.hartree_error_metrics(y - x, lat, rh, rs)
                b, d1, d2 = v3._totals(an, ch)
                self.assertLess(eh, tau); self.assertLess(es, tau)
                # spectral safe prediction equals decoded safe error
                self.assertAlmostEqual(np.sqrt(d2 / an.ref_safe_spec) / es, 1.0, places=6)
                # conservative bound >= historical
                self.assertGreaterEqual(np.sqrt(d1 / an.ref_cons_spec) * (1 + 1e-9), eh)
                self.assertEqual(int(b) + (len(blob) - int(b)), len(blob))

    def test_rdo_not_worse_than_powerlaw(self):
        x, lat = synth(seed=3)
        rh, rs = v02.reference_hartree_rms(x, lat)
        tau = 1e-4
        an = v3.analyze(x, lat, prior="operator", reference_historical_rms=rh)
        rdo = len(v3.encode(an, v3.select(an, tau)))
        # best uniform-multiplier (pure power law beta=2) stream on the same ladder meeting tau
        best = None
        for j in range(an.mult.size):
            ch = []
            for c in an.curves:
                hit = np.flatnonzero(c.j == j)
                ch.append(int(hit[0]) if hit.size else int(np.argmin(np.abs(c.j - j)) if c.j.size > 1 else 0))
            b, d1, d2 = v3._totals(an, ch)
            if d1 <= (0.995 * tau) ** 2 * an.ref_cons_spec and d2 <= (0.995 * tau) ** 2 * an.ref_safe_spec:
                n = len(v3.encode(an, ch)); best = n if best is None else min(best, n)
        self.assertIsNotNone(best)
        self.assertLessEqual(rdo, best)

if __name__ == "__main__":
    unittest.main()
