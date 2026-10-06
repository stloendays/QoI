import sys, unittest
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import policy_codec as pc
v02 = pc.v02

def synth(shape=(20, 18, 24), seed=1):
    rng = np.random.default_rng(seed)
    lat = np.array([[4.0, 0, 0], [1.1, 4.4, 0], [0.3, 0.6, 5.2]])
    k = [np.fft.fftfreq(n) * n for n in shape]
    g = np.sqrt(k[0][:, None, None] ** 2 + k[1][None, :, None] ** 2 + k[2][None, None, :] ** 2)
    x = np.fft.ifftn((rng.normal(size=shape) + 1j * rng.normal(size=shape)) / (1 + g) ** 3).real
    return x - x.min() + 0.1, lat

class T(unittest.TestCase):
    def test_hartree_closure_and_certificate(self):
        x, lat = synth(); rh, rs = v02.reference_hartree_rms(x, lat)
        prep = v02.prepare_field(x, lat); spec = pc.OrbitSpectrum(prep)
        mw, ref = spec.weight_cache(lambda g2: g2 ** -2.0)
        for pol in ({"kind": "power_q", "p": 2.0}, {"kind": "flat"}, {"kind": "power_q", "p": -1.0}):
            u = pc.policy_shape(prep.topology, pol)
            a = pc.bisect_alpha(spec, u, mw, ref, 1e-4, float(np.ptp(x)))
            y = pc.decode(pc.encode(prep, a, pol))
            eh, es = v02.hartree_error_metrics(y - x, lat, rh, rs)
            self.assertLess(es, 1e-4)
            self.assertAlmostEqual(spec.rel_error_safe(a * u, mw, ref) / es, 1.0, places=6)

    def test_gaussian_policy_in_gaussian_metric(self):
        x, lat = synth(seed=2); prep = v02.prepare_field(x, lat); spec = pc.OrbitSpectrum(prep)
        s2 = 0.5 ** 2
        mw, ref = spec.weight_cache(lambda g2: np.exp(-s2 * g2))
        pol = {"kind": "gaussian", "sigma_angstrom": 0.5}
        u = pc.policy_shape(prep.topology, pol)
        a = pc.bisect_alpha(spec, u, mw, ref, 1e-4, float(np.ptp(x)))
        self.assertIsNotNone(a)
        y = pc.decode(pc.encode(prep, a, pol))
        # independent decoded check in the same metric, via a fresh orbit spectrum of the error field
        e = pc.OrbitSpectrum(v02.prepare_field(y - x + 0.0, lat))
        mwe, _ = e.weight_cache(lambda g2: np.exp(-s2 * g2))
        err = np.sqrt(float(np.sum(mwe * (e.cr[e.safe] ** 2 + e.ci[e.safe] ** 2))) / ref)
        self.assertLess(err, 1e-4)
        self.assertAlmostEqual(spec.rel_error_safe(a * u, mw, ref) / err, 1.0, places=6)

    def test_matches_v02_bytes(self):
        x, lat = synth(seed=4); prep = v02.prepare_field(x, lat)
        for beta in (0.0, 1.0, 2.0):
            a = 1e-4 * float(np.ptp(x))
            b2, _ = v02.encode_prepared(prep, alpha=a, beta=beta)
            y2, _, _ = v02.decode_blob(b2)
            y = pc.decode(pc.encode(prep, a, {"kind": "power_q", "p": beta} if beta else {"kind": "flat"}))
            self.assertLess(np.max(np.abs(y - y2)), 1e-12)

if __name__ == "__main__":
    unittest.main()
