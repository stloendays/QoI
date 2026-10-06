#!/usr/bin/env python3
"""Registry of linear, diagonal-in-Fourier downstream operators on a periodic density.

Every operator L acts on the density as (L rho)_c(G) = a_c(G) rho(G) for c = 1..n_components. It provides

- ``weight(g2)``: the normalized squared spectral weight w(|G|^2) ∝ sum_c |a_c(G)|^2 used for error
  allocation (physical constants dropped; they cancel in every relative error and in every allocation ratio);
- exact spectral relative-RMSE error metrics (rFFT + Parseval) in three variants:
    ``safe``                 all modes except G = 0 (for singular operators) and the even-grid Nyquist planes;
    ``historical``           all modes, as realized in real space by ``numpy.fft.irfftn`` (on even grids the
                             historical reciprocal vector of a Nyquist index is not Hermitian-consistent, and
                             irfftn keeps only the Hermitian part of the kz = 0 and kz = Nyquist planes; this
                             variant applies exactly that projection, so it equals the real-space RMS);
    ``historical_spectral``  all modes, plain spectral sum without that projection (the definition used by
                             ``general_qoac_electric_field/electric_field_operator.py``);
- an explicit real-space implementation (``explicit_realspace_rms``) for small-grid validation.

``legacy_relative_error`` returns the (historical, safe) pair under the convention of the frozen code the
operator was first used in: QOAC-H v0.2 ``hartree_error_metrics`` (real-space historical) for
``hartree_potential`` and ``electric_field_operator.relative_error`` (spectral historical) for
``hartree_field``. The two historical definitions coincide on all-odd grids (no Nyquist planes) and, for
scalar operators, on orthogonal cells; they differ on even grids of non-orthogonal cells, and for vector
operators also on orthogonal cells (irfftn drops the odd i*G_c component at a Nyquist index).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

FOUR_PI = 4.0 * np.pi
VARIANTS = ("historical", "safe", "historical_spectral")


# ---------------------------------------------------------------------------------------------------------
# reciprocal-space geometry (identical conventions to codec_qoac_h_v02 / electric_field_operator)
# ---------------------------------------------------------------------------------------------------------
def reciprocal_basis(lattice: np.ndarray) -> np.ndarray:
    lat = np.asarray(lattice, dtype=np.float64)
    if lat.shape != (3, 3):
        raise ValueError("lattice must have shape (3,3)")
    return 2.0 * np.pi * np.linalg.inv(lat).T


def reciprocal_vectors_rfft(shape: tuple[int, int, int], lattice: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Historical rFFT reciprocal vectors G (..., 3) and |G|^2 (fftfreq sign convention at Nyquist)."""
    nx, ny, nz = (int(v) for v in shape)
    b = reciprocal_basis(lattice)
    n1 = np.fft.fftfreq(nx) * nx
    n2 = np.fft.fftfreq(ny) * ny
    n3 = np.fft.rfftfreq(nz) * nz
    a, c, d = np.meshgrid(n1, n2, n3, indexing="ij")
    g = a[..., None] * b[0] + c[..., None] * b[1] + d[..., None] * b[2]
    return g, np.einsum("...k,...k->...", g, g)


def rfft_multiplicity(shape: tuple[int, int, int]) -> np.ndarray:
    nx, ny, nz = (int(v) for v in shape)
    w = np.full((nx, ny, nz // 2 + 1), 2.0, dtype=np.float64)
    w[:, :, 0] = 1.0
    if nz % 2 == 0:
        w[:, :, -1] = 1.0
    return w


def nyquist_mask_rfft(shape: tuple[int, int, int]) -> np.ndarray:
    nx, ny, nz = (int(v) for v in shape)
    m = np.zeros((nx, ny, nz // 2 + 1), dtype=bool)
    if nx % 2 == 0:
        m[nx // 2, :, :] = True
    if ny % 2 == 0:
        m[:, ny // 2, :] = True
    if nz % 2 == 0:
        m[:, :, -1] = True
    return m


def hermitian_project_rfft(v: np.ndarray, shape: tuple[int, int, int]) -> np.ndarray:
    """Half spectrum of irfftn(v, s=shape): Hermitian part of the kz=0 (and kz=Nyquist) planes."""
    nx, ny, nz = (int(s) for s in shape)
    out = np.array(v, dtype=np.complex128, copy=True)
    pi = (-np.arange(nx)) % nx
    pj = (-np.arange(ny)) % ny
    planes = [0] + ([nz // 2] if nz % 2 == 0 else [])
    for k in planes:
        p = v[:, :, k]
        out[:, :, k] = 0.5 * (p + np.conj(p[pi][:, pj]))
    return out


# ---------------------------------------------------------------------------------------------------------
# operator registry
# ---------------------------------------------------------------------------------------------------------
Amplitudes = Callable[[np.ndarray, np.ndarray], list]


@dataclass(frozen=True)
class DiagonalOperator:
    name: str
    n_components: int
    singular_at_zero: bool               # G = 0 excluded from every metric (Hartree potential / field)
    _weight: Callable[[np.ndarray], np.ndarray] = field(repr=False)
    _amplitudes: Amplitudes = field(repr=False)
    params: tuple = ()

    def weight(self, g2: np.ndarray) -> np.ndarray:
        """Normalized squared spectral weight w(|G|^2); 0 where the operator is undefined/zero."""
        g2 = np.asarray(g2, dtype=np.float64)
        out = np.zeros_like(g2)
        pos = g2 > 0.0
        out[pos] = self._weight(g2[pos])
        if not self.singular_at_zero:
            out[~pos] = self._weight(np.zeros(int(np.count_nonzero(~pos))))
        return out

    def amplitudes(self, gvec: np.ndarray, g2: np.ndarray) -> list:
        """Complex multipliers a_c(G) (physical constants included), valid where ``support`` is True."""
        return self._amplitudes(gvec, g2)

    def support(self, g2: np.ndarray) -> np.ndarray:
        return (g2 > 0.0) if self.singular_at_zero else np.ones(g2.shape, dtype=bool)

    @property
    def label(self) -> str:
        if self.params:
            return self.name + "(" + ",".join(f"{k}={v:g}" for k, v in self.params) + ")"
        return self.name


def _safe_div(num, den):
    out = np.zeros(np.broadcast(num, den).shape, dtype=np.result_type(num, den, np.float64))
    np.divide(num, den, out=out, where=np.broadcast_to(den, out.shape) > 0.0)
    return out


def density() -> DiagonalOperator:
    return DiagonalOperator("density", 1, False, lambda g2: np.ones_like(g2),
                            lambda g, g2: [np.ones(g2.shape, dtype=np.complex128)])


def hartree_potential() -> DiagonalOperator:
    return DiagonalOperator("hartree_potential", 1, True, lambda g2: g2 ** -2.0,
                            lambda g, g2: [FOUR_PI * _safe_div(1.0, g2).astype(np.complex128)])


def hartree_field() -> DiagonalOperator:
    # E = -grad V_H, E(G) = -i G V(G) = -i 4 pi G rho(G) / |G|^2
    return DiagonalOperator("hartree_field", 3, True, lambda g2: g2 ** -1.0,
                            lambda g, g2: [-1j * FOUR_PI * _safe_div(g[..., c], g2) for c in range(3)])


def density_gradient() -> DiagonalOperator:
    return DiagonalOperator("density_gradient", 3, False, lambda g2: g2.copy(),
                            lambda g, g2: [1j * g[..., c] for c in range(3)])


def density_laplacian() -> DiagonalOperator:
    return DiagonalOperator("density_laplacian", 1, False, lambda g2: g2 * g2,
                            lambda g, g2: [(-g2).astype(np.complex128)])


def gaussian_smoothed_density(sigma_angstrom: float) -> DiagonalOperator:
    s = float(sigma_angstrom)
    if not (math.isfinite(s) and s > 0.0):
        raise ValueError("sigma_angstrom must be finite and >0")
    return DiagonalOperator("gaussian_smoothed_density", 1, False, lambda g2: np.exp(-s * s * g2),
                            lambda g, g2: [np.exp(-0.5 * s * s * g2).astype(np.complex128)],
                            params=(("sigma_angstrom", s),))


OPERATORS: dict[str, Callable[..., DiagonalOperator]] = {
    "density": density,
    "hartree_potential": hartree_potential,
    "hartree_field": hartree_field,
    "density_gradient": density_gradient,
    "density_laplacian": density_laplacian,
    "gaussian_smoothed_density": gaussian_smoothed_density,
}


def get_operator(name: str, **params) -> DiagonalOperator:
    if name not in OPERATORS:
        raise KeyError(f"unknown operator {name!r}; known: {sorted(OPERATORS)}")
    return OPERATORS[name](**params)


# ---------------------------------------------------------------------------------------------------------
# spectral metrics
# ---------------------------------------------------------------------------------------------------------
def _component_spectra(field: np.ndarray, lattice: np.ndarray, op: DiagonalOperator, variant: str) -> list:
    x = np.asarray(field, dtype=np.float64)
    if x.ndim != 3 or not np.all(np.isfinite(x)):
        raise ValueError("field must be finite 3-D float data")
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}")
    shape = tuple(int(v) for v in x.shape)
    f = np.fft.rfftn(x)
    gvec, g2 = reciprocal_vectors_rfft(shape, lattice)
    mask = op.support(g2)
    if variant == "safe":
        mask &= ~nyquist_mask_rfft(shape)
    out = []
    for amp in op.amplitudes(gvec, g2):
        v = np.zeros_like(f)
        v[mask] = amp[mask] * f[mask]
        out.append(v)
    return out


def operator_energy(field: np.ndarray, lattice: np.ndarray, op: DiagonalOperator, variant: str = "safe") -> float:
    """sum over real-space points of |L field|^2, times N (unnormalized-FFT Parseval constant)."""
    shape = tuple(int(v) for v in np.shape(field))
    mult = rfft_multiplicity(shape)
    total = 0.0
    for v in _component_spectra(field, lattice, op, variant):
        if variant != "historical_spectral":
            v = hermitian_project_rfft(v, shape)
        total += float(np.sum(mult * (v.real * v.real + v.imag * v.imag)))
    if not math.isfinite(total) or total < 0.0:
        raise ValueError("invalid operator energy")
    return total


def reference_energies(field: np.ndarray, lattice: np.ndarray, op: DiagonalOperator) -> dict:
    ref = {v: operator_energy(field, lattice, op, v) for v in VARIANTS}
    if not all(r > 0.0 for r in ref.values()):
        raise ValueError("reference operator energy must be positive")
    return ref


def relative_error(error: np.ndarray, lattice: np.ndarray, op: DiagonalOperator, reference: dict) -> dict:
    """Relative RMSE ||L error|| / ||L reference|| for every variant in ``reference``."""
    return {v: float(math.sqrt(operator_energy(error, lattice, op, v) / float(reference[v]))) for v in reference}


LEGACY_HISTORICAL = {"hartree_potential": "historical", "hartree_field": "historical_spectral"}


def legacy_relative_error(error: np.ndarray, lattice: np.ndarray, op: DiagonalOperator, reference: dict) -> tuple:
    """(historical, safe) under the frozen-code convention for this operator (see module docstring)."""
    hv = LEGACY_HISTORICAL.get(op.name, "historical")
    r = relative_error(error, lattice, op, {hv: reference[hv], "safe": reference["safe"]})
    return r[hv], r["safe"]


# ---------------------------------------------------------------------------------------------------------
# explicit real-space implementation (validation)
# ---------------------------------------------------------------------------------------------------------
def apply_realspace(field: np.ndarray, lattice: np.ndarray, op: DiagonalOperator, safe: bool = False) -> np.ndarray:
    """Return the operator output in real space, shape (n_components, *field.shape)."""
    x = np.asarray(field, dtype=np.float64)
    shape = tuple(int(v) for v in x.shape)
    f = np.fft.rfftn(x)
    gvec, g2 = reciprocal_vectors_rfft(shape, lattice)
    mask = op.support(g2)
    if safe:
        mask &= ~nyquist_mask_rfft(shape)
    comps = []
    for amp in op.amplitudes(gvec, g2):
        v = np.zeros_like(f)
        v[mask] = amp[mask] * f[mask]
        comps.append(np.fft.irfftn(v, s=shape, axes=(0, 1, 2)))
    return np.stack(comps)


def explicit_realspace_rms(field: np.ndarray, lattice: np.ndarray, op: DiagonalOperator, safe: bool = False) -> float:
    y = apply_realspace(field, lattice, op, safe=safe)
    return float(np.sqrt(np.mean(np.sum(y * y, axis=0))))


def standard_operators(gaussian_sigmas=(0.5,)) -> list:
    ops = [density(), hartree_potential(), hartree_field(), density_gradient(), density_laplacian()]
    ops += [gaussian_smoothed_density(s) for s in gaussian_sigmas]
    return ops
