#!/usr/bin/env python3
"""Offline unit tests for the self-contained-byte analysis."""
from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from aggregate_selfcontained import build_per_material_table
from run_selfcontained import (
    HEADER_BYTES,
    charges_from_labels,
    check_stored_labels,
    decode_label_stream,
    encode_label_stream,
)


class LabelStreamTests(unittest.TestCase):
    def test_header_and_round_trip_on_synthetic_map(self):
        labels = np.array(
            [
                [[0, 1], [1, 2], [2, 0]],
                [[1, 1], [2, 2], [0, 0]],
            ],
            dtype=np.int64,
        )
        stored = encode_label_stream(labels, natoms=2)
        self.assertGreaterEqual(len(stored), HEADER_BYTES)
        shape, natoms, decoded = decode_label_stream(stored)
        self.assertEqual(shape, labels.shape)
        self.assertEqual(natoms, 2)
        np.testing.assert_array_equal(decoded, labels)
        checks = check_stored_labels(
            stored,
            labels,
            np.ones(labels.shape, dtype=np.float64),
            charges_from_labels(np.ones(labels.shape), labels, 2),
            2,
        )
        self.assertTrue(checks["roundtrip_ok"])
        self.assertTrue(checks["charge_check_ok"])

    def test_charge_summation_against_hand_computed_case(self):
        chg = np.array([[[1.0, 2.0], [3.0, 4.0]]])
        labels = np.array([[[0, 1], [1, 2]]], dtype=np.int64)
        # The fixed-grid Bader convention divides each basin sum by the four
        # voxels in the CHGCAR grid: (2+3)/4 and 4/4.
        np.testing.assert_allclose(charges_from_labels(chg, labels, 2), [1.25, 1.0])


class MetricTests(unittest.TestCase):
    def test_cr_arithmetic_on_two_material_table(self):
        materials = pd.DataFrame(
            [
                {
                    "material_id": "m1",
                    "raw_bytes": 100,
                    "label_bytes_primary": 10,
                    "label_bytes_ctx": 8,
                    "n_labels": 3,
                    "status": "SUCCESS",
                    "roundtrip_ok": True,
                    "charge_check_ok": True,
                },
                {
                    "material_id": "m2",
                    "raw_bytes": 200,
                    "label_bytes_primary": 20,
                    "label_bytes_ctx": 15,
                    "n_labels": 4,
                    "status": "SUCCESS",
                    "roundtrip_ok": True,
                    "charge_check_ok": True,
                },
            ]
        )
        best = pd.DataFrame(
            [
                {"material_id": "m1", "base": "R3", "tau_bader": 1e-4, "best_joint_cr": 10.0, "hartree_only_cr": 20.0},
                {"material_id": "m1", "base": "GF", "tau_bader": 1e-4, "best_joint_cr": 20.0, "hartree_only_cr": 20.0},
                {"material_id": "m2", "base": "R3", "tau_bader": 1e-4, "best_joint_cr": 10.0, "hartree_only_cr": 20.0},
                {"material_id": "m2", "base": "GF", "tau_bader": 1e-4, "best_joint_cr": 40.0, "hartree_only_cr": 20.0},
            ]
        )
        per = build_per_material_table(best, materials, bases=["R3", "GF"], taus=["0.0001"])
        r3 = per[per["base"] == "R3"].sort_values("material_id")
        gf = per[per["base"] == "GF"].sort_values("material_id")
        np.testing.assert_array_equal(r3["S"].to_numpy(), [10, 20])
        np.testing.assert_allclose(r3["L"].to_numpy(), [10, 20])
        np.testing.assert_allclose(r3["CR_sc"].to_numpy(), [5.0, 5.0])
        np.testing.assert_array_equal(gf["S"].to_numpy(), [5, 5])
        np.testing.assert_allclose(gf["CR_sc"].to_numpy(), [100.0 / 15.0, 200.0 / 25.0])
        np.testing.assert_allclose(r3["U_sc"].to_numpy(), [0.75, 0.625])
        np.testing.assert_allclose(r3["versus_best_pointwise"].to_numpy(), [0.75, 0.625])


if __name__ == "__main__":
    unittest.main()
