import importlib.util
import pathlib
import unittest

import numpy as np

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "t011_xqlfw_baseline.py"
spec = importlib.util.spec_from_file_location("t011_xqlfw_baseline", MODULE_PATH)
baseline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(baseline)


class ProtocolTests(unittest.TestCase):
    def test_threshold_selects_balanced_dev_operating_point(self):
        scores = np.array([0.9, 0.8, 0.7, 0.6])
        labels = np.array([True, False, True, False])
        threshold = baseline.select_threshold(scores, labels)
        self.assertEqual(threshold, 0.8)
        self.assertEqual(
            baseline.counts(scores, labels, threshold),
            {"genuine": 2, "impostor": 2, "false_reject": 1, "false_accept": 1},
        )

    def test_pair_image_rejects_missing_source(self):
        lookup = {("synthetic", "synthetic_0001.jpg"): "archive/synthetic/synthetic_0001.jpg"}
        self.assertEqual(
            baseline.pair_image("synthetic", "1", lookup),
            "archive/synthetic/synthetic_0001.jpg",
        )
        with self.assertRaises(ValueError):
            baseline.pair_image("synthetic", "2", lookup)

    def test_wilson_retains_uncertainty_with_zero_errors(self):
        lower, upper = baseline.wilson(0, 300)
        self.assertAlmostEqual(lower, 0.0)
        self.assertGreater(upper, 0.0)


if __name__ == "__main__":
    unittest.main()
