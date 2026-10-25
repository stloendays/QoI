#!/usr/bin/env python3
"""Tests of the W1 writer: coder round trips, symmetry relations, decoder agreement and certificate arithmetic."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import qac  # noqa: E402
import symmetry as sym  # noqa: E402
import w1  # noqa: E402


def test_qac_round_trip():
    rng = np.random.default_rng(1)
    for scale in (0.2, 3.0, 1e3, 1e9, 1e15):
        n = 5000
        qr = np.rint(rng.laplace(0, scale, n)).astype(np.int64)
        qi = np.rint(rng.laplace(0, scale, n)).astype(np.int64)
        sc = rng.random(n) < 0.02
        qi[sc] = 0
        kind = (rng.random(n) < 0.5).astype(np.int64)
        b = qac.encode(qr, qi, sc, kind)
        r, i = qac.decode(b, sc, kind)
        assert np.array_equal(r, qr) and np.array_equal(i, qi)
    assert qac.encode(np.zeros(7, np.int64), np.zeros(7, np.int64), np.zeros(7, bool)) == b""


def _cubic(n=(24, 24, 24), a=4.1):
    from pymatgen.core import Lattice, Structure
    st = Structure(Lattice.cubic(a), ["Na", "Cl"], [[0, 0, 0], [0.5, 0.5, 0.5]])
    g = np.indices(n).reshape(3, -1).T / np.asarray(n)
    rho = np.zeros(g.shape[0])
    for f, w, s in (([0, 0, 0], 3.0, 0.08), ([0.5, 0.5, 0.5], 1.0, 0.12)):
        d = g - np.asarray(f)
        d -= np.rint(d)
        r2 = np.sum((d @ st.lattice.matrix) ** 2, axis=1)
        rho += w * np.exp(-r2 / (2 * (s * a) ** 2))
    return st, rho.reshape(n), np.asarray(st.lattice.matrix)


def _rms_pair(x, lat):
    return w1.v02.reference_hartree_rms(x, lat)


def test_symmetry_relations_hold_on_spectrum():
    st, x, lat = _cubic()
    group, status = sym.grid_group(st, x)
    assert status["status"] == "OK" and status["ops"] == 48
    topo = w1.v02.build_topology(x.shape, lat, shell_count=32)
    c = np.fft.fftn(x, norm="ortho").ravel()[topo.rep_flat]
    for p, conj, ph in sym.orbit_relations(topo, group):
        tgt = np.where(conj, np.conj(c[p]), c[p])
        assert np.max(np.abs(c - ph * tgt)) < 1e-12 * np.max(np.abs(c))
    plan = sym.Plan(topo, group)
    assert plan.classes < topo.rep_flat.size / 10
    gens = sym.generators(group, np.asarray(x.shape))
    assert len(sym.closure(gens, np.asarray(x.shape))) == 48 and len(gens) <= 4


@pytest.mark.parametrize("use_sym", [False, True])
@pytest.mark.parametrize("mode", ["law", "wf", "trunc", "rdo"])
def test_decoder_matches_encoder_and_certificate(mode, use_sym):
    st, x, lat = _cubic()
    rh, rs = _rms_pair(x, lat)
    F = w1.prepare(x, lat, rh, st, use_symmetry=use_sym)
    ptp = float(np.ptp(x))
    tau = 1e-4
    if mode == "rdo":
        an = w1.rdo_analysis(F, ptp)
        ch = w1.v3.select(an, tau, margin=w1.MARGIN, polish=True)
        kw = dict(ptp=ptp, shells=np.array([int(cv.j[i]) for cv, i in zip(an.curves, ch)]))
    elif mode == "trunc":
        kw = dict(alpha=1e-3 * ptp, q_cut=0.5)
    else:
        kw = dict(alpha=1e-2 * ptp)
    steps = w1.steps_of(F, mode, kw.get("alpha"), kw.get("ptp"), kw.get("shells"))
    keep = w1.keep_mask(F, mode, kw.get("alpha"), kw.get("q_cut"), kw.get("shells"))
    d_cons, d_safe = w1.distortion(F, steps, keep)
    blob = w1.encode(F, mode, **kw)
    rec = w1.decode(blob)
    eh, es = w1.v02.hartree_error_metrics(rec - x, lat, rh, rs)
    assert abs(es ** 2 - d_safe) <= 1e-6 * d_safe + 1e-30
    assert eh ** 2 <= d_cons * (1 + 1e-6) + 1e-30          # conservative metric bounds the historical one
    assert np.array_equal(rec, w1.decode(w1.encode(F, mode, **kw)))


def test_waterfill_limits():
    st, x, lat = _cubic()
    rh, _ = _rms_pair(x, lat)
    F = w1.prepare(x, lat, rh, st)
    ptp = float(np.ptp(x))
    E = np.bincount(F.shell, weights=F.e_sig, minlength=32)
    assert w1.wf_shells(F, 1e-12 * ptp)[E > 1e-20 * E.sum()].all()
    assert not w1.wf_shells(F, 1e6 * ptp).any()


def test_symmetry_shrinks_stream_and_rdo_curves_are_separable():
    st, x, lat = _cubic()
    rh, rs = _rms_pair(x, lat)
    ptp = float(np.ptp(x))
    cert = lambda r: w1.v02.hartree_error_metrics(r - x, lat, rh, rs)  # noqa: E731
    F0 = w1.prepare(x, lat, rh, st, use_symmetry=False)
    F1 = w1.prepare(x, lat, rh, st, use_symmetry=True)
    b0 = w1.search_scalar(F0, "wf", 1e-6, ptp, cert)
    b1 = w1.search_scalar(F1, "wf", 1e-6, ptp, cert)
    assert b1["bytes"] < 0.5 * b0["bytes"]
    an = w1.rdo_analysis(F1, ptp)
    ch = w1.v3.select(an, 1e-6, margin=w1.MARGIN, polish=True)
    shells = np.array([int(cv.j[i]) for cv, i in zip(an.curves, ch)])
    blob = w1.encode(F1, "rdo", ptp=ptp, shells=shells)
    predicted = sum(cv.bytes[i] for cv, i in zip(an.curves, ch))
    head = len(w1.encode(F1, "rdo", ptp=ptp, shells=np.full(32, -1)))
    assert abs(len(blob) - head - predicted) <= 32
