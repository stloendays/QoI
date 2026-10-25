#!/usr/bin/env python3
"""QAC: context-adaptive binary arithmetic coding of quantized Fourier coefficients, one segment per shell.

Range coder: the LZMA binary range coder (32-bit range, 11-bit probabilities, adaptation shift 5), jitted with numba.
Every segment starts from fresh models, so a stream's size is the exact sum of its segments (the separability the
operational allocation relies on). The final code value is the number in the last interval with the most trailing zero
bits; trailing zero bytes are not stored, because the decoder reads zeros past the end of a segment.

Binarization of one integer v (real part, then imaginary part unless the orbit is self-conjugate), with two model banks:
kind 0 for a freely coded coefficient and kind 1 for a symmetry-predicted residual.
  zero flag             ctx = (part, bit length of the previous same-kind orbit's max |v| clipped at 5,
                               for the imaginary part also whether the real part is zero)
  sign                  one adaptive bit per part
  bit length - 1        6-level binary tree, ctx = (part, previous bit length clipped at 11, node)
  mantissa              first bit below the MSB adaptive (ctx = part, bit length), the rest equiprobable
"""
from __future__ import annotations

import numpy as np
from numba import njit

PROB_BITS = 11
PROB_INIT = 1 << (PROB_BITS - 1)
MOVE = 5
TOP = 1 << 24
NB = 6             # bit-length tree depth: |v| < 2**63
NCLS = 6           # neighbourhood classes on the previous orbit's bit length: 0..4, >=5
NBC = 12           # bit-length tree contexts on the previous orbit's bit length: 0..10, >=11

# model layout (per part p in {0 real, 1 imag}):
#   zero[p][cls][rz]       rz: for the imaginary part, whether the real part is zero
#   sign[p]
#   tree[p][nbc][node]     node 1..63 of the 6-level binary tree coding bitlen(|v|) - 1
#   mant[p][bitlen]        first bit below the MSB
Z_OFF = 0
Z_N = 2 * NCLS * 2
S_OFF = Z_OFF + Z_N
T_OFF = S_OFF + 2
T_N = 2 * NBC * 64
M_OFF = T_OFF + T_N
NMODEL = M_OFF + 2 * 64


@njit(cache=True)
def _enc_bit(st, out, probs, i, bit):
    # st: [low, range, cache, cache_size, pos]
    p = probs[i]
    bound = (st[1] >> PROB_BITS) * p
    if bit == 0:
        st[1] = bound
        probs[i] = p + (((1 << PROB_BITS) - p) >> MOVE)
    else:
        st[0] += bound
        st[1] -= bound
        probs[i] = p - (p >> MOVE)
    while st[1] < TOP:
        st[1] = (st[1] << 8) & 0xFFFFFFFF
        _shift_low(st, out)


@njit(cache=True)
def _shift_low(st, out):
    low = st[0]
    if low < 0xFF000000 or low > 0xFFFFFFFF:
        carry = low >> 32
        temp = st[2]
        while True:
            if st[4] >= 0 and st[4] < out.size:  # the first (dummy, always 0) byte is not stored
                out[st[4]] = (temp + carry) & 0xFF
            st[4] += 1
            temp = 0xFF
            st[3] -= 1
            if st[3] == 0:
                break
        st[2] = (low >> 24) & 0xFF
    st[3] += 1
    st[0] = (low & 0x00FFFFFF) << 8


@njit(cache=True)
def _bitlen(a):
    n = 0
    while a > 0:
        a >>= 1
        n += 1
    return n


@njit(cache=True)
def _enc_value(st, out, probs, part, pnb, rz, v, bank):
    zi = bank + Z_OFF + (part * NCLS + min(pnb, NCLS - 1)) * 2 + rz
    if v == 0:
        _enc_bit(st, out, probs, zi, 0)
        return
    _enc_bit(st, out, probs, zi, 1)
    _enc_bit(st, out, probs, bank + S_OFF + part, 1 if v < 0 else 0)
    a = abs(v)
    nb = _bitlen(a)
    t = nb - 1
    base = bank + T_OFF + (part * NBC + min(pnb, NBC - 1)) * 64
    node = 1
    for i in range(NB - 1, -1, -1):
        bit = (t >> i) & 1
        _enc_bit(st, out, probs, base + node, bit)
        node = 2 * node + bit
    if nb >= 2:
        _enc_bit(st, out, probs, bank + M_OFF + part * 64 + nb, (a >> (nb - 2)) & 1)
        for i in range(nb - 3, -1, -1):
            _enc_bit_fixed(st, out, (a >> i) & 1)


@njit(cache=True)
def _enc_bit_fixed(st, out, bit):
    st[1] >>= 1
    if bit:
        st[0] += st[1]
    while st[1] < TOP:
        st[1] = (st[1] << 8) & 0xFFFFFFFF
        _shift_low(st, out)


@njit(cache=True)
def encode_segment(qr, qi, selfc, kind, out):
    """Encode one shell into `out` (preallocated); returns the number of bytes written. kind 0: free coefficient,
    kind 1: symmetry-predicted residual (separate model bank and neighbourhood)."""
    probs = np.full(2 * NMODEL, PROB_INIT, dtype=np.int64)
    pk = np.zeros(2, dtype=np.int64)
    st = np.zeros(5, dtype=np.int64)
    st[1] = 0xFFFFFFFF
    st[3] = 1
    st[4] = -1          # skip the leading dummy byte
    for n in range(qr.size):
        kd = kind[n]
        bank = kd * NMODEL
        pnb = pk[kd]
        r = qr[n]
        _enc_value(st, out, probs, 0, pnb, 0, r, bank)
        m = abs(r)
        if not selfc[n]:
            im = qi[n]
            _enc_value(st, out, probs, 1, pnb, 1 if r == 0 else 0, im, bank)
            if abs(im) > m:
                m = abs(im)
        pk[kd] = _bitlen(m)
    # final value: the number in [low, low + range) with the most trailing zero bits, then flush; trailing zero
    # bytes are not stored (the decoder reads zeros past the end of a segment)
    lo = st[0]
    hi = st[0] + st[1]
    for k in range(40, -1, -1):
        mask = (1 << k) - 1
        v = (lo + mask) & ~mask
        if v < hi:
            st[0] = v
            break
    for _ in range(5):
        _shift_low(st, out)
    n = st[4]
    if n > out.size:
        return -1
    while n > 0 and out[n - 1] == 0:
        n -= 1
    return n


# ------------------------------------------------------------------------------------------------ decoder
@njit(cache=True)
def _dec_bit(ds, buf, probs, i):
    # ds: [range, code, pos]
    p = probs[i]
    bound = (ds[0] >> PROB_BITS) * p
    if ds[1] < bound:
        ds[0] = bound
        probs[i] = p + (((1 << PROB_BITS) - p) >> MOVE)
        bit = 0
    else:
        ds[1] -= bound
        ds[0] -= bound
        probs[i] = p - (p >> MOVE)
        bit = 1
    while ds[0] < TOP:
        ds[0] = (ds[0] << 8) & 0xFFFFFFFF
        ds[1] = ((ds[1] << 8) | _byte(buf, ds)) & 0xFFFFFFFF
    return bit


@njit(cache=True)
def _dec_bit_fixed(ds, buf):
    ds[0] >>= 1
    bit = 0
    if ds[1] >= ds[0]:
        ds[1] -= ds[0]
        bit = 1
    while ds[0] < TOP:
        ds[0] = (ds[0] << 8) & 0xFFFFFFFF
        ds[1] = ((ds[1] << 8) | _byte(buf, ds)) & 0xFFFFFFFF
    return bit


@njit(cache=True)
def _byte(buf, ds):
    p = ds[2]
    ds[2] += 1
    if p < buf.size:
        return buf[p]
    return 0


@njit(cache=True)
def _dec_value(ds, buf, probs, part, pnb, rz, bank):
    zi = bank + Z_OFF + (part * NCLS + min(pnb, NCLS - 1)) * 2 + rz
    if _dec_bit(ds, buf, probs, zi) == 0:
        return 0
    neg = _dec_bit(ds, buf, probs, bank + S_OFF + part)
    base = bank + T_OFF + (part * NBC + min(pnb, NBC - 1)) * 64
    node = 1
    for _ in range(NB):
        node = 2 * node + _dec_bit(ds, buf, probs, base + node)
    nb = node - 64 + 1
    a = 1
    if nb >= 2:
        a = (a << 1) | _dec_bit(ds, buf, probs, bank + M_OFF + part * 64 + nb)
        for _ in range(nb - 2):
            a = (a << 1) | _dec_bit_fixed(ds, buf)
    return -a if neg else a


@njit(cache=True)
def decode_segment(buf, selfc, kind, qr, qi):
    probs = np.full(2 * NMODEL, PROB_INIT, dtype=np.int64)
    pk = np.zeros(2, dtype=np.int64)
    ds = np.zeros(3, dtype=np.int64)
    ds[0] = 0xFFFFFFFF
    for _ in range(4):
        ds[1] = ((ds[1] << 8) | _byte(buf, ds)) & 0xFFFFFFFF
    for n in range(qr.size):
        kd = kind[n]
        bank = kd * NMODEL
        pnb = pk[kd]
        r = _dec_value(ds, buf, probs, 0, pnb, 0, bank)
        qr[n] = r
        m = abs(r)
        if not selfc[n]:
            im = _dec_value(ds, buf, probs, 1, pnb, 1 if r == 0 else 0, bank)
            qi[n] = im
            if abs(im) > m:
                m = abs(im)
        else:
            qi[n] = 0
        pk[kd] = _bitlen(m)


def encode(qr: np.ndarray, qi: np.ndarray, selfc: np.ndarray, kind: np.ndarray | None = None) -> bytes:
    qr = np.ascontiguousarray(qr, dtype=np.int64)
    qi = np.ascontiguousarray(qi, dtype=np.int64)
    selfc = np.ascontiguousarray(selfc, dtype=np.bool_)
    kind = np.zeros(qr.size, np.int64) if kind is None else np.ascontiguousarray(kind, dtype=np.int64)
    size = 64 + 4 * qr.size
    while True:
        out = np.zeros(size, dtype=np.uint8)
        n = encode_segment(qr, qi, selfc, kind, out)
        if n >= 0:
            return out[:n].tobytes()
        size *= 4


def decode(buf: bytes, selfc: np.ndarray, kind: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    selfc = np.ascontiguousarray(selfc, dtype=np.bool_)
    kind = np.zeros(selfc.size, np.int64) if kind is None else np.ascontiguousarray(kind, dtype=np.int64)
    qr = np.zeros(selfc.size, dtype=np.int64)
    qi = np.zeros(selfc.size, dtype=np.int64)
    decode_segment(np.frombuffer(buf, dtype=np.uint8), selfc, kind, qr, qi)
    return qr, qi
