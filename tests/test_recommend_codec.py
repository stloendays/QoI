import csv
import tempfile
import unittest
from pathlib import Path
import importlib.util
import sys

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "recommend_codec.py"
spec = importlib.util.spec_from_file_location("recommend_codec", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


FIELDNAMES = [
    "material_id", "codec", "codec_config", "compression_ratio",
    "Bader_error_resolved_e", "realized_Linf", "encode_seconds", "bader_seconds",
    "nominal_tolerance_relative", "nominal_tolerance_absolute",
    "stability_floor_A1_e"
]


def write_csv(path: Path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


class RecommendationTests(unittest.TestCase):
    def test_rejects_non_evaluable_material(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.csv"
            write_csv(path, [{
                "material_id": "m1", "codec": "zfp", "codec_config": "a",
                "compression_ratio": "100", "Bader_error_resolved_e": "0.0001",
                "realized_Linf": "0.1", "encode_seconds": "1", "bader_seconds": "2",
                "nominal_tolerance_relative": "1e-4", "nominal_tolerance_absolute": "0.1",
                "stability_floor_A1_e": "0.002"
            }])
            result = mod.recommend(path, "m1", 1e-3, "max-compression")
            self.assertEqual(result["status"], "NON_EVALUABLE_BADER_UNSTABLE")
            self.assertIsNone(result["recommendation"])

    def test_max_compression_only_considers_certified_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.csv"
            common = {
                "material_id": "m1", "realized_Linf": "0.1", "encode_seconds": "1",
                "bader_seconds": "2", "nominal_tolerance_relative": "1e-4",
                "nominal_tolerance_absolute": "0.1", "stability_floor_A1_e": "0.0001"
            }
            write_csv(path, [
                {**common, "codec": "zfp", "codec_config": "a", "compression_ratio": "20", "Bader_error_resolved_e": "0.0009"},
                {**common, "codec": "sz3", "codec_config": "b", "compression_ratio": "100", "Bader_error_resolved_e": "0.002"},
                {**common, "codec": "sperr", "codec_config": "c", "compression_ratio": "15", "Bader_error_resolved_e": "0.0002"}
            ])
            result = mod.recommend(path, "m1", 1e-3, "max-compression")
            self.assertEqual(result["status"], "CERTIFIED_RECOMMENDATION")
            self.assertEqual(result["recommendation"]["codec"], "zfp")

    def test_no_certified_candidate_is_distinct_from_qsq_rejection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.csv"
            write_csv(path, [{
                "material_id": "m1", "codec": "zfp", "codec_config": "a",
                "compression_ratio": "100", "Bader_error_resolved_e": "0.002",
                "realized_Linf": "0.1", "encode_seconds": "1", "bader_seconds": "2",
                "nominal_tolerance_relative": "1e-4", "nominal_tolerance_absolute": "0.1",
                "stability_floor_A1_e": "0.0001"
            }])
            result = mod.recommend(path, "m1", 1e-3, "balanced")
            self.assertEqual(result["status"], "NO_CERTIFIED_CANDIDATE")
            self.assertTrue(result["eligible"])


if __name__ == "__main__":
    unittest.main()
