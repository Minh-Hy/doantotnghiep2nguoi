"""Synthetic coordinate checks for E1 adapter output normalization."""

import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "t011_widerface_predict.py"
spec = importlib.util.spec_from_file_location("t011_widerface_predict", MODULE_PATH)
predictor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(predictor)


class E1AdapterNormalizationTests(unittest.TestCase):
    def test_native_xywh_box_maps_to_original_xyxy(self):
        self.assertEqual(
            predictor.xywh_to_xyxy(12, 20, 8, 6, 0.75),
            [12.0, 20.0, 20.0, 26.0, 0.75],
        )

    def test_scrfd_xyxy_preserves_score_and_original_coordinates(self):
        self.assertEqual(
            predictor.xyxy_score([12, 20, 20, 26, 0.75]),
            [12.0, 20.0, 20.0, 26.0, 0.75],
        )

    def test_nonfinite_native_output_is_rejected(self):
        with self.assertRaises(ValueError):
            predictor.xywh_to_xyxy(1, 2, float("nan"), 4, 0.7)
        with self.assertRaises(ValueError):
            predictor.xyxy_score([1, 2, 3, 4, float("inf")])


if __name__ == "__main__":
    unittest.main()
