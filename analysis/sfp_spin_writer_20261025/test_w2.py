#!/usr/bin/env python3
"""Tests of the W2 writer: SFP block round trip, decoder agreement and certificate, the gain of the prediction on a
superposition of atoms, the W2M sub-stream round trip and the moment certificate."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w2  # noqa: E402

w1, v02 = w2.w1, w2.v02


def _crystal(n=(30, 30, 30), a=5.2, bond=0.15):
    """A low-symmetry two-species cell: Gaussian atoms plus a bond charge (the part no superposition can predict)."""
    from pymatgen.core import Lattice, Structure
    frac = [[0.02, 0.05, 0.01], [0.48, 0.53, 0.47], [0.27, 0.71, 0.22], [0.73, 0.24, 0.81]]
    sym = ["Mg", "O", "Mg", "O"]
    st = Structure(Lattice.from_parameters(a, a * 1.07, a * 0.93, 88, 93, 101), sym, frac)
    lat = np.asarray(st.lattice.matrix)
    g = np.indices(n).reshape(3, -1).T / np.asarray(n)
    rho = np.zeros(g.shape[0])
    for f, s in zip(frac, sym):
        d = g - np.asarray(f)
        d -= np.rint(d)
        r2 = np.sum((d @ lat) ** 2, axis=1)
        w, sg = (2.0, 0.5) if s == "Mg" else (6.0, 0.35)
        rho += w * np.exp(-r2 / (2 * sg ** 2))
    mid = (np.asarray(frac[0]) + np.asarray(frac[1])) / 2
    d = g - mid
    d -= np.rint(d)
    rho += bond * np.exp(-np.sum((d @ lat) ** 2, axis=1) / (2 * 0.6 ** 2))
    return st, sym, np.asarray(frac), rho.reshape(n) * 50.0, lat


def _cert(x, lat):
    rh, rs = v02.reference_hartree_rms(x, lat)
    return lambda r: v02.hartree_error_metrics(r - x, lat, rh, rs), rh


def test_sfp_block_round_trip_and_prediction():
    st, sym, frac, x, lat = _crystal()
    certify, rh = _cert(x, lat)
    F = w1.prepare(x, lat, rh, st, use_symmetry=True)
    info = w2.sfp_fit(F, sym, frac)
    assert info is not None and len(info["used"]) >= 5
    back = w2.parse_sfp_block(w2.sfp_block(info), w2.shell_counts(F.topo))
    for k in ("zs", "used", "exps"):
        assert list(back[k]) == list(info[k])
    assert np.array_equal(back["sp"], info["sp"]) and np.array_equal(back["f32"], info["f32"])
    assert all(np.array_equal(a, b) for a, b in zip(back["codes"], info["codes"]))
    S = w2.structure_factors(F.topo, back["sp"], back["f32"], len(back["zs"]))
    assert np.array_equal(w2.prediction(F.topo, S, back["used"], back["exps"], back["codes"]), info["pred"])
    G = w2.residual_field(F, info["pred"])
    assert G.e_sig.sum() < 0.05 * F.e_sig.sum()


def test_decoder_matches_encoder_and_certificate():
    st, sym, frac, x, lat = _crystal()
    certify, rh = _cert(x, lat)
    ptp = float(np.ptp(x))
    F = w1.prepare(x, lat, rh, st, use_symmetry=True)
    info = w2.sfp_fit(F, sym, frac)
    for tau in (1e-4, 1e-6):
        r = w2.search_wf(F, info, tau, ptp, certify)
        assert r is not None and r["blob"][4] == 1
        rec = w2.decode(r["blob"])
        assert np.array_equal(rec, r["rec"])
        eh, es = certify(rec)
        assert eh < tau and es < tau
        r0 = w2.search_wf(F, None, tau, ptp, certify)
        assert w2.decode(r0["blob"]).shape == x.shape
        best = w2.search_w2(F, info, tau, ptp, certify)
        assert best["bytes"] <= min(r["bytes"], r0["bytes"])
    # the prediction pays on a superposition of atoms at the primary tolerance
    assert w2.search_wf(F, info, 1e-6, ptp, certify)["bytes"] < 0.8 * w2.search_wf(F, None, 1e-6, ptp, certify)["bytes"]


def test_rdo_on_residual_is_certified():
    st, sym, frac, x, lat = _crystal(n=(24, 24, 24))
    certify, rh = _cert(x, lat)
    ptp = float(np.ptp(x))
    F = w1.prepare(x, lat, rh, st, use_symmetry=True)
    info = w2.sfp_fit(F, sym, frac)
    r = w2.search_rdo(F, info, 1e-5, ptp, certify)
    assert r is not None
    eh, es = certify(r["rec"])
    assert eh < 1e-5 and es < 1e-5


def test_w2m_round_trip_and_moment_certificate():
    st, sym, frac, x, lat = _crystal()
    rng = np.random.default_rng(3)
    g = np.indices(x.shape).reshape(3, -1).T / np.asarray(x.shape)
    m = np.zeros(g.shape[0])
    for f, mu in zip(frac, (1.5, -0.2, 1.3, 0.1)):
        d = g - f
        d -= np.rint(d)
        m += mu * np.exp(-np.sum((d @ lat) ** 2, axis=1) / (2 * 0.4 ** 2))
    m = m.reshape(x.shape) * 40.0 + 1e-4 * rng.standard_normal(x.shape)
    # Voronoi partition, 1-based labels
    best = np.full(g.shape[0], np.inf)
    atom = np.zeros(g.shape[0], dtype=np.int64)
    for a, f in enumerate(frac):
        d = g - f
        d -= np.rint(d)
        r2 = np.sum((d @ lat) ** 2, axis=1)
        u = r2 < best
        best[u] = r2[u]
        atom[u] = a + 1
    atom = atom.reshape(x.shape)
    mu_ref = w2.moments(m, atom, 4)
    rhm, _ = v02.reference_hartree_rms(m, lat)
    Fm = w1.prepare(m, lat, rhm, st, use_symmetry=True)
    full = w1.encode(Fm, "wf", alpha=1e-3 * float(np.ptp(m)))
    cb = w2.compact_m(full)
    assert w2.expand_m(cb, x.shape, lat) == full and len(cb) < len(full)
    assert np.array_equal(w2.decode_m(cb, x.shape, lat), w1.decode(full))
    r = w2.search_m(Fm, x.shape, lat, atom, 4, mu_ref, 0.01, float(np.ptp(m)))
    assert r is not None and r["err_final"] < 0.01
    assert np.max(np.abs(w2.moments(w2.decode_m(r["blob"], x.shape, lat), atom, 4) - mu_ref)) < 0.01
    # a vanishing magnetization costs only the sub-stream header
    z = 1e-7 * rng.standard_normal(x.shape)
    Fz = w1.prepare(z, lat, max(v02.reference_hartree_rms(z, lat)[0], 1e-30), st, use_symmetry=False)
    rz = w2.search_m(Fz, x.shape, lat, atom, 4, w2.moments(z, atom, 4), 0.01, float(np.ptp(z)))
    assert rz is not None and rz["bytes"] < 40 and rz["shells_written"] == 0
    p = w2.porod_exponent(atom, 4, lat)
    assert p is not None and -5.5 < p < -2.5
