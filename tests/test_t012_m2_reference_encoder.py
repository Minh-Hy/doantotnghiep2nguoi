"""Guard the M2 shared-sample timing schedule and output shape."""

import pathlib
import sys
import unittest

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from t012_m2_reference_encoder import SAMPLE_COUNT, benchmark, candidate_order, percentile  # noqa: E402


class FakeEncoder:
    def get_feat(self, crop):
        return np.full((1, 512), float(crop) + 1.0, dtype=np.float32)


class EncoderTimingTests(unittest.TestCase):
    def test_order_and_call_count(self):
        self.assertEqual([candidate_order(i) for i in range(3)], [
            ("mbf", "r50"), ("r50", "mbf"), ("mbf", "r50")
        ])
        result = benchmark({"mbf": FakeEncoder(), "r50": FakeEncoder()}, list(range(SAMPLE_COUNT)))
        for candidate in ("mbf", "r50"):
            self.assertEqual(result[candidate]["calls"], 180)
            self.assertGreaterEqual(result[candidate]["p95_ms"], result[candidate]["median_ms"])

    def test_percentile_and_bad_sample(self):
        self.assertEqual(percentile([1.0, 3.0], 0.5), 2.0)
        with self.assertRaisesRegex(ValueError, "fixed sample"):
            benchmark({"mbf": FakeEncoder(), "r50": FakeEncoder()}, [0])


if __name__ == "__main__":
    unittest.main()
