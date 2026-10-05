#!/usr/bin/env python3
from __future__ import annotations

import unittest
import numpy as np

import qoac_b_core as q


class QoacB1CoreTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(1207)
        self.x = rng.normal(size=(9, 8, 7))
        self.labels = np.zeros(self.x.shape, dtype=np.int64)
        self.labels[:3, :, :] = 1
        self.labels[3:6, :, :] = 2
        self.labels[6:, :, :] = 3
        self.labels[0, 0, :2] = 0

    def test_side_channel_roundtrip(self):
        side = q.side_channel_from_field(self.x, self.labels)
        blob = side.to_bytes()
        got = q.BasinSideChannel.from_bytes(blob)
        np.testing.assert_array_equal(got.sums, side.sums)
        self.assertEqual(len(blob), q.HEADER.size + 8 * side.sums.size)

    def test_projection_closes_region_sums(self):
        rng = np.random.default_rng(8)
        y = self.x + 0.2 * rng.normal(size=self.x.shape)
        side = q.side_channel_from_field(self.x, self.labels)
        z = q.project_to_region_sums(y, self.labels, side.sums)
        m = q.closure_metrics(self.x, z, self.labels)
        self.assertLess(m["max_rel_region_sum_error_scaled"], 5e-15)

    def test_residual_is_region_zero_sum(self):
        side, residual = q.decompose_to_basin_residual(self.x, self.labels)
        sums = q.region_sums(residual, self.labels)
        scale = max(1.0, float(np.max(np.abs(side.sums))))
        self.assertLess(float(np.max(np.abs(sums))) / scale, 5e-15)

    def test_residual_reconstruction_preserves_target_sums(self):
        rng = np.random.default_rng(9)
        side, residual = q.decompose_to_basin_residual(self.x, self.labels)
        noisy = residual + 0.1 * rng.normal(size=residual.shape)
        z = q.reconstruct_from_basin_residual(noisy, self.labels, side)
        m = q.closure_metrics(self.x, z, self.labels)
        self.assertLess(m["max_rel_region_sum_error_scaled"], 5e-15)
        self.assertGreater(float(np.max(np.abs(z - self.x))), 0.0)

    def test_fortran_flat_label_adapter(self):
        flat = self.labels.ravel(order="F")
        got = q.label_grid_from_fortran_flat(flat, self.labels.shape)
        np.testing.assert_array_equal(got, self.labels)


if __name__ == "__main__":
    unittest.main()
