"""Synthetic checks that T-012 slices replay T-011 matching and annotation order."""

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from t011_widerface_evaluate import evaluate, parse_annotations  # noqa: E402
from t012_widerface_error_slices import analyze, parse_valid_metadata, size_bucket  # noqa: E402


class ErrorSliceTests(unittest.TestCase):
    def test_slice_matches_original_tp_and_excludes_invalid_gt(self):
        annotation = (
            "event/a.jpg\n3\n"
            "0 0 10 10 1 0 0 0 2 0\n"
            "20 20 20 20 2 0 1 0 0 1\n"
            "60 60 10 10 0 0 0 1 0 0\n"
            "event/b.jpg\n1\n"
            "0 0 100 100 0 0 0 0 0 0\n"
        )
        truth, counts = parse_annotations(annotation)
        metadata = parse_valid_metadata(annotation, truth)
        predictions = {
            "event/a.jpg": [[0, 0, 10, 10, 0.9], [0, 0, 10, 10, 0.8]],
            "event/b.jpg": [[-1, -1, 100, 100, 0.7]],
        }
        sizes = {"event/a.jpg": (100, 100), "event/b.jpg": (200, 200)}
        baseline = evaluate(truth, predictions, sizes)
        sliced = analyze(truth, metadata, predictions, sizes)
        self.assertEqual((counts["valid_gt"], counts["ignored_gt"]), (3, 1))
        self.assertEqual(sliced["matched_gt"], baseline["tp"])
        self.assertEqual(sliced["matched_gt"], 2)
        self.assertEqual((sliced["prediction_rows"], sliced["clipped_box"]), (3, 1))
        self.assertEqual(sliced["groups"]["size_px_sqrt_area"]["lt16"]["matched_gt"], 1)
        self.assertEqual(sliced["groups"]["size_px_sqrt_area"]["16to31"]["missed_gt"], 1)
        self.assertEqual(sliced["groups"]["size_px_sqrt_area"]["ge96"]["matched_gt"], 1)
        self.assertEqual(sliced["groups"]["blur_code"]["2"]["missed_gt"], 1)
        cross = sliced["groups"]["image_group_and_size_px_sqrt_area"]
        self.assertEqual(cross["multi_valid:lt16"]["matched_gt"], 1)
        self.assertEqual(cross["multi_valid:16to31"]["missed_gt"], 1)
        self.assertEqual(cross["one_valid:ge96"]["matched_gt"], 1)
        self.assertEqual(sum(row["matched_gt"] for row in cross.values()), baseline["tp"])

    def test_misordered_metadata_is_rejected(self):
        annotation = "a.jpg\n2\n0 0 10 10 0 0 0 0 0 0\n20 20 10 10 0 0 0 0 0 0\n"
        truth, _ = parse_annotations(annotation)
        truth["a.jpg"]["valid"].reverse()
        with self.assertRaisesRegex(ValueError, "order differs"):
            parse_valid_metadata(annotation, truth)

    def test_size_boundaries_are_explicit(self):
        self.assertEqual(size_bucket((0.0, 0.0, 16.0, 16.0)), "16to31")
        self.assertEqual(size_bucket((0.0, 0.0, 32.0, 32.0)), "32to95")
        self.assertEqual(size_bucket((0.0, 0.0, 96.0, 96.0)), "ge96")


if __name__ == "__main__":
    unittest.main()
