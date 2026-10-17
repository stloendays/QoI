from __future__ import annotations

import math
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import codecs_ffcz as C  # noqa: E402
import probe_ffcz as P  # noqa: E402
import run_ffcz as R  # noqa: E402


class FrozenContract(unittest.TestCase):
    def test_exact_18_configurations(self):
        expected = [
            ("zfp", 1e-2, "REL"), ("zfp", 1e-2, "PTW"),
            ("zfp", 1e-3, "REL"), ("zfp", 1e-3, "PTW"),
            ("zfp", 1e-4, "REL"), ("zfp", 1e-4, "PTW"),
            ("sz3", 1e-2, "REL"), ("sz3", 1e-2, "PTW"),
            ("sz3", 1e-3, "REL"), ("sz3", 1e-3, "PTW"),
            ("sz3", 1e-4, "REL"), ("sz3", 1e-4, "PTW"),
            ("sperr", 1e-2, "REL"), ("sperr", 1e-2, "PTW"),
            ("sperr", 1e-3, "REL"), ("sperr", 1e-3, "PTW"),
            ("sperr", 1e-4, "REL"), ("sperr", 1e-4, "PTW"),
        ]
        self.assertEqual(len(R.CONFIGS), 18)
        self.assertEqual([(c.codec, c.eps_rel, c.mode) for c in R.CONFIGS], expected)

    def test_intervals(self):
        self.assertEqual(R.INTERVALS, {"REL": (1e-14, 1.0), "PTW": (1e-14, 10.0)})

    def test_compression_ratio_arithmetic(self):
        self.assertEqual(C.stored_bytes(100, 25), 125)
        self.assertAlmostEqual(C.compression_ratio(1000, 100, 25), 64.0)

    def test_numpy_frequency_and_spatial_bound_checks(self):
        original = np.ones((4, 5, 6), dtype=np.float64)
        r = 1e-3
        reconstructed = original + r
        self.assertAlmostEqual(P.frequency_bound_ratio(original, reconstructed, r, "REL"), 1.0)
        self.assertAlmostEqual(P.frequency_bound_ratio(original, reconstructed, r, "PTW"), 1.0)
        self.assertAlmostEqual(P.spatial_bound_ratio(original, reconstructed, 2 * r), 0.5)

    def test_c_order_axis_command(self):
        command = C.ffcz_command("ffcz_cpu", "REL", 1e-4, (48, 56, 72), 0.01, "rho.raw", "base.raw", "edits")
        at = command.index("-3")
        self.assertEqual(command[at + 1:at + 4], ["48", "56", "72"])


class TaskMatrix(unittest.TestCase):
    def test_task_list_size(self):
        tasks = R.task_ids(HERE.parents[1], "run")
        self.assertEqual(len(tasks), 92 * 18)
        self.assertEqual(len(set(tasks)), 92 * 18)
        self.assertEqual(tasks[0].split(":", 1)[1], R.CONFIGS[0].config_id)


class MockedSearch(unittest.TestCase):
    def test_mocked_ffcz_runner_through_one_search(self):
        runner = Mock()
        runner.side_effect = lambda r: {"bytes": int(1000 / (1 + r)), "hartree_hist": r * 1e-3,
                                        "hartree_safe": r * 1e-3}

        def evaluate(r: float):
            return runner(float(r))

        best, seen, skipped = R.search(evaluate, 1e-6, 1e-14, 1.0)
        self.assertEqual(skipped, 0)
        self.assertIsNotNone(best)
        self.assertGreater(runner.call_count, 2)
        self.assertTrue(all(v["hartree_hist"] < 1e-6 and v["hartree_safe"] < 1e-6 for v in seen.values()))
        self.assertAlmostEqual(best, 1e-3, delta=1e-3 * 1e-6)


class BaseCodecSubprocess(unittest.TestCase):
    def test_compress_command_carries_input_and_bound(self):
        captured = {}

        def fake_run(cmd, cwd=None):
            captured["cmd"] = [str(x) for x in cmd]
            return Mock(stdout='{"stream_bytes": 1, "stream_file_bytes": 1}\n')

        original = C._run_process
        C._run_process = fake_run
        try:
            with tempfile.TemporaryDirectory() as tmp:
                C.compress_base("sz3", np.zeros((2, 3, 4)), 3.5e-3, Path(tmp))
        finally:
            C._run_process = original
        cmd = captured["cmd"]
        self.assertEqual(cmd[cmd.index("--abs-bound") + 1], repr(3.5e-3))
        self.assertTrue(cmd[cmd.index("--input") + 1].endswith("base.input.raw"))
        self.assertNotIn("--output", cmd)

    def test_subprocess_roundtrip_respects_bound(self):
        rng = np.random.default_rng(0)
        array = rng.standard_normal((12, 14, 16))
        abs_bound = 1e-3
        for codec, module in (("zfp", "zfpy"), ("sz3", "pysz"), ("sperr", "hdf5plugin")):
            with self.subTest(codec=codec):
                try:
                    __import__(module)
                except ImportError:
                    continue
                with tempfile.TemporaryDirectory() as tmp:
                    base = C.prepare_base(codec, array, abs_bound, Path(tmp))
                    self.assertGreater(base.stream_bytes, 0)
                    decoded = np.fromfile(base.decoded_path, dtype="<f8").reshape(array.shape)
                    self.assertLessEqual(float(np.max(np.abs(decoded - array))), abs_bound * (1 + 1e-12))


if __name__ == "__main__":
    unittest.main()
