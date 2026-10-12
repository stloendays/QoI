#!/usr/bin/env python3
"""Local tests for the frozen archive-law runner and aggregator."""
from __future__ import annotations

import math
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

import aggregate_archive_law as aggregate
import run_archive_law as runner


HERE = Path(__file__).resolve().parent


class ArchiveLawTests(unittest.TestCase):
    def test_storage_rule_all_branches(self) -> None:
        certified = runner.stored_bytes(
            status="SUCCESS",
            eligible=True,
            certified_bytes=10,
            lossless_bytes=40,
            frame_bytes=100,
        )
        self.assertEqual(certified, (10, "certified stream"))

        eligible_no_writer = runner.stored_bytes(
            status="SUCCESS",
            eligible=True,
            certified_bytes=None,
            lossless_bytes=40,
            frame_bytes=100,
        )
        self.assertEqual(eligible_no_writer[0], 40)
        self.assertIn("none certified", eligible_no_writer[1])

        non_evaluable = runner.stored_bytes(
            status="SUCCESS",
            eligible=False,
            certified_bytes=10,
            lossless_bytes=40,
            frame_bytes=100,
        )
        self.assertEqual(non_evaluable, (40, "lossless (non-evaluable)"))

        unknown_eligibility = runner.stored_bytes(
            status="SUCCESS",
            eligible=None,
            certified_bytes=10,
            lossless_bytes=40,
            frame_bytes=100,
        )
        self.assertEqual(unknown_eligibility[0], 40)

        failed = runner.stored_bytes(
            status="FAILED",
            eligible=True,
            certified_bytes=10,
            lossless_bytes=40,
            frame_bytes=100,
        )
        self.assertEqual(failed, (100, "failed: current MP json.gz"))

    def test_stratified_expansion_hand_answer(self) -> None:
        strata = pd.DataFrame(
            {
                "stratum": ["H1", "H2"],
                "N_frame": [100, 200],
                "n_sample": [2, 2],
            }
        ).set_index("stratum")
        df = pd.DataFrame(
            {
                "stratum": ["H1", "H1", "H2", "H2"],
                "json_bytes": [10, 20, 30, 40],
                "stored_L_1e-06": [5, 10, 15, 20],
                "stored_P_1e-06": [4, 8, 12, 16],
                "status": ["SUCCESS"] * 4,
                "eligible_1e-06": [True] * 4,
                "writer_L_certified_1e-06": [True] * 4,
                "writer_P_certified_1e-06": [True] * 4,
                "writer_L_stream_bytes_1e-06": [5, 10, 15, 20],
                "writer_P_stream_bytes_1e-06": [4, 8, 12, 16],
                "raw64_bytes": [100, 100, 200, 200],
                "lossless_bytes": [50, 50, 100, 100],
            }
        )
        # H1: 100/2 * (10+20) = 1500; H2: 200/2 * (30+40) = 7000.
        self.assertEqual(aggregate.stratified_total(df, strata, "json_bytes"), 8500.0)
        self.assertEqual(aggregate.stratified_total(df, strata, "stored_L_1e-06"), 4250.0)
        metrics = aggregate.point_metrics(df, strata, 1e-6)
        self.assertAlmostEqual(metrics["R_L_vs_json"], 2.0)
        self.assertAlmostEqual(metrics["R_P_vs_json"], 2.5)
        self.assertAlmostEqual(metrics["R_L_over_R_P"], 0.8)

    def test_bootstrap_is_paired(self) -> None:
        strata = pd.DataFrame(
            {
                "stratum": ["H1", "H2"],
                "N_frame": [4, 4],
                "n_sample": [2, 2],
            }
        ).set_index("stratum")
        df = pd.DataFrame(
            {
                "stratum": ["H1", "H1", "H2", "H2"],
                "json_bytes": [10, 20, 30, 40],
                "stored_L_1e-06": [2, 5, 10, 20],
                "stored_P_1e-06": [4, 10, 20, 40],
                "status": ["SUCCESS"] * 4,
                "eligible_1e-06": [True] * 4,
                "writer_L_certified_1e-06": [True] * 4,
                "writer_P_certified_1e-06": [True] * 4,
                "writer_L_stream_bytes_1e-06": [2, 5, 10, 20],
                "writer_P_stream_bytes_1e-06": [4, 10, 20, 40],
                "raw64_bytes": [100, 100, 200, 200],
                "lossless_bytes": [50, 50, 100, 100],
            }
        )
        samples = aggregate.paired_bootstrap(
            df, strata, 1e-6, n_boot=25, seed=20261012, return_samples=True
        )
        self.assertEqual(len(samples["R_L_vs_json"]), 25)
        self.assertTrue(
            np.allclose(
                samples["R_L_over_R_P"],
                samples["R_L_vs_json"] / samples["R_P_vs_json"],
                equal_nan=False,
            )
        )

    def test_format_comparisons_restrict_both_totals_to_successes(self) -> None:
        strata = pd.DataFrame(
            {
                "stratum": ["H1", "H2"],
                "N_frame": [100, 200],
                "n_sample": [2, 2],
            }
        ).set_index("stratum")
        df = pd.DataFrame(
            {
                "stratum": ["H1", "H1", "H2", "H2"],
                "json_bytes": [10, 20, 30, 40],
                "stored_L_1e-06": [10, 10, 15, 20],
                "stored_P_1e-06": [10, 8, 12, 16],
                "status": ["FAILED", "SUCCESS", "SUCCESS", "SUCCESS"],
                "eligible_1e-06": [np.nan, True, True, True],
                "writer_L_certified_1e-06": [np.nan, True, True, True],
                "writer_P_certified_1e-06": [np.nan, True, True, True],
                "writer_L_stream_bytes_1e-06": [np.nan, 10, 15, 20],
                "writer_P_stream_bytes_1e-06": [np.nan, 8, 12, 16],
                "raw64_bytes": [np.nan, 100, 200, 200],
                "lossless_bytes": [np.nan, 50, 100, 100],
            }
        )
        metrics = aggregate.point_metrics(df, strata, 1e-6)
        # Successful-only expansion: raw=45,000 and law stored=4,000.
        self.assertAlmostEqual(metrics["R_L_vs_float64"], 11.25)
        self.assertAlmostEqual(metrics["R_L_vs_lossless"], 5.625)

    def test_qsq_floor_matches_direct_hartree_computation(self) -> None:
        grid = np.indices((3, 3, 3), dtype=np.float64)
        field = (
            0.25
            + 0.13 * np.sin(2.0 * np.pi * grid[0] / 3.0)
            + 0.07 * np.cos(2.0 * np.pi * grid[1] / 3.0)
            + 0.05 * np.sin(2.0 * np.pi * grid[2] / 3.0)
        )
        lattice = np.eye(3, dtype=np.float64) * 5.0
        got = runner.qsq_floor(field, lattice)
        ref_h, ref_s = runner.ENG.v02.reference_hartree_rms(field, lattice)
        epsilon = float(np.max(np.abs(field.astype(np.float32).astype(np.float64) - field)))
        expected_responses = []
        for seed in runner.wpf.SEEDS:
            noise = np.random.Generator(np.random.PCG64(seed)).uniform(
                -epsilon, epsilon, size=field.shape
            )
            eh, es = runner.ENG.v02.hartree_error_metrics(noise, lattice, ref_h, ref_s)
            expected_responses.append(max(eh, es))
        self.assertAlmostEqual(got["epsilon"], epsilon, places=20)
        self.assertAlmostEqual(got["reference_rms_historical"], ref_h, places=14)
        self.assertAlmostEqual(got["reference_rms_safe"], ref_s, places=14)
        self.assertAlmostEqual(got["floor_hartree"], max(expected_responses), places=14)

    def test_task_list_is_300_with_frozen_strata_counts(self) -> None:
        tasks = runner.load_tasks()
        self.assertEqual(len(tasks), 300)
        counts = {}
        for task in tasks:
            counts[task["stratum"]] = counts.get(task["stratum"], 0) + 1
        self.assertEqual(
            counts,
            {
                "D01": 30,
                "D02": 30,
                "D03": 30,
                "D04": 30,
                "D05": 30,
                "D06": 30,
                "D07": 30,
                "D08": 30,
                "D09": 30,
                "D10a": 15,
                "D10b": 10,
                "D10c": 5,
            },
        )
        self.assertEqual(len(runner.list_task_lines(tasks)), 300)
        self.assertTrue(all("\t" in line for line in runner.list_task_lines(tasks)))


if __name__ == "__main__":
    unittest.main()
