#!/usr/bin/env python3
"""Core fixed-partition transforms for QOAC-B1."""
from __future__ import annotations

import struct
from dataclasses import dataclass

import numpy as np

MAGIC = b"QOACB1\0\0"
HEADER = struct.Struct("<8sII")  # magic, number of labels, version
VERSION = 1


@dataclass(frozen=True)
class BasinSideChannel:
    """Exact discrete target sums for integer partition labels 0..L."""

    sums: np.ndarray

    def to_bytes(self) -> bytes:
        x = np.ascontiguousarray(np.asarray(self.sums, dtype="<f8"))
        return HEADER.pack(MAGIC, int(x.size), VERSION) + x.tobytes(order="C")

    @classmethod
    def from_bytes(cls, blob: bytes) -> "BasinSideChannel":
        if len(blob) < HEADER.size:
            raise ValueError("truncated QOAC-B1 side channel")
        magic, n, version = HEADER.unpack(blob[:HEADER.size])
        if magic != MAGIC or version != VERSION:
            raise ValueError("invalid QOAC-B1 side channel")
        raw = blob[HEADER.size:]
        if len(raw) != int(n) * 8:
            raise ValueError("side-channel byte-count mismatch")
        return cls(np.frombuffer(raw, dtype="<f8").astype(np.float64, copy=True))


def label_grid_from_fortran_flat(labels_flat: np.ndarray, shape: tuple[int, int, int]) -> np.ndarray:
    labels = np.asarray(labels_flat, dtype=np.int64)
    if labels.size != int(np.prod(shape)):
        raise ValueError("label count does not match grid shape")
    out = labels.reshape(shape, order="F")
    if np.any(out < 0):
        raise ValueError("negative Bader partition labels are unsupported")
    return np.ascontiguousarray(out)


def _validate(field: np.ndarray, labels: np.ndarray) -> tuple[np.ndarray, np.ndarray, int]:
    x = np.ascontiguousarray(np.asarray(field, dtype=np.float64))
    lab = np.ascontiguousarray(np.asarray(labels, dtype=np.int64))
    if x.shape != lab.shape:
        raise ValueError("field/label shape mismatch")
    if x.ndim != 3:
        raise ValueError("QOAC-B1 expects a 3-D field")
    if not np.all(np.isfinite(x)):
        raise ValueError("field contains non-finite values")
    if np.any(lab < 0):
        raise ValueError("labels must be non-negative integers")
    max_label = int(lab.max()) if lab.size else 0
    return x, lab, max_label


def region_counts(labels: np.ndarray) -> np.ndarray:
    lab = np.asarray(labels, dtype=np.int64)
    if np.any(lab < 0):
        raise ValueError("labels must be non-negative")
    return np.bincount(lab.ravel(), minlength=int(lab.max()) + 1).astype(np.int64)


def region_sums(field: np.ndarray, labels: np.ndarray) -> np.ndarray:
    x, lab, max_label = _validate(field, labels)
    return np.bincount(
        lab.ravel(),
        weights=x.ravel(),
        minlength=max_label + 1,
    ).astype(np.float64)


def side_channel_from_field(field: np.ndarray, labels: np.ndarray) -> BasinSideChannel:
    return BasinSideChannel(region_sums(field, labels))


def means_from_sums(sums: np.ndarray, labels: np.ndarray) -> np.ndarray:
    counts = region_counts(labels)
    target = np.asarray(sums, dtype=np.float64)
    if target.shape != counts.shape:
        raise ValueError("sum/count label cardinality mismatch")
    means = np.zeros_like(target)
    nz = counts > 0
    means[nz] = target[nz] / counts[nz]
    return means


def mean_map(sums: np.ndarray, labels: np.ndarray) -> np.ndarray:
    means = means_from_sums(sums, labels)
    return means[np.asarray(labels, dtype=np.int64)]


def project_to_region_sums(
    field: np.ndarray,
    labels: np.ndarray,
    target_sums: np.ndarray,
) -> np.ndarray:
    """Uniformly shift each populated region until its discrete sum matches target."""
    x, lab, max_label = _validate(field, labels)
    target = np.asarray(target_sums, dtype=np.float64)
    if target.shape != (max_label + 1,):
        raise ValueError("target sum cardinality mismatch")
    counts = region_counts(lab)
    current = region_sums(x, lab)
    shift = np.zeros_like(target)
    nz = counts > 0
    shift[nz] = (target[nz] - current[nz]) / counts[nz]
    y = x + shift[lab]

    # A second pass removes most floating accumulation residual without changing
    # the basin geometry. It is intentionally done in float64.
    current2 = region_sums(y, lab)
    shift2 = np.zeros_like(target)
    shift2[nz] = (target[nz] - current2[nz]) / counts[nz]
    y = y + shift2[lab]
    return np.ascontiguousarray(y, dtype=np.float64)


def decompose_to_basin_residual(
    field: np.ndarray,
    labels: np.ndarray,
) -> tuple[BasinSideChannel, np.ndarray]:
    """Return exact region sums plus a residual whose region sums are ~0."""
    side = side_channel_from_field(field, labels)
    residual = np.asarray(field, dtype=np.float64) - mean_map(side.sums, labels)
    zeros = np.zeros_like(side.sums)
    residual = project_to_region_sums(residual, labels, zeros)
    return side, residual


def reconstruct_from_basin_residual(
    decoded_residual: np.ndarray,
    labels: np.ndarray,
    side: BasinSideChannel,
) -> np.ndarray:
    zeros = np.zeros_like(side.sums)
    residual = project_to_region_sums(decoded_residual, labels, zeros)
    recon = residual + mean_map(side.sums, labels)
    # Final projection is a numerical closure step only.
    return project_to_region_sums(recon, labels, side.sums)


def closure_metrics(
    reference: np.ndarray,
    reconstruction: np.ndarray,
    labels: np.ndarray,
) -> dict[str, float]:
    s0 = region_sums(reference, labels)
    s1 = region_sums(reconstruction, labels)
    delta = np.abs(s1 - s0)
    scale = max(1.0, float(np.max(np.abs(s0))) if s0.size else 1.0)
    return {
        "max_abs_region_sum_error": float(np.max(delta)) if delta.size else 0.0,
        "max_rel_region_sum_error_scaled": float(np.max(delta) / scale) if delta.size else 0.0,
    }


def field_metrics(reference: np.ndarray, reconstruction: np.ndarray) -> dict[str, float]:
    x = np.asarray(reference, dtype=np.float64)
    y = np.asarray(reconstruction, dtype=np.float64)
    e = y - x
    return {
        "final_Linf": float(np.max(np.abs(e))),
        "final_RMSE": float(np.sqrt(np.mean(e * e))),
        "mean_density_deviation": float(abs(np.mean(y) - np.mean(x))),
    }
