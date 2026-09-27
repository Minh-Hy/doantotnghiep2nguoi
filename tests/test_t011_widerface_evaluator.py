"""Protocol checks for the T-011 E1 evaluator; all inputs are synthetic boxes."""

import importlib.util
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "t011_widerface_evaluate.py"
spec = importlib.util.spec_from_file_location("t011_widerface_evaluate", MODULE_PATH)
evaluator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluator)


class WiderFaceEvaluatorTests(unittest.TestCase):
    def test_parse_retains_valid_ignore_and_nonpositive_as_distinct_counts(self):
        text = (
            "event/one.jpg\n"
            "3\n"
            "0 0 10 10 0 0 0 0 0 0\n"
            "20 20 10 10 0 0 0 1 0 0\n"
            "30 30 0 10 0 0 0 1 0 0\n"
        )
        truth, counts = evaluator.parse_annotations(text)
        self.assertEqual(len(truth["event/one.jpg"]["valid"]), 1)
        self.assertEqual(len(truth["event/one.jpg"]["ignored"]), 1)
        self.assertEqual(
            (counts["box_rows"], counts["invalid_flag_rows"], counts["nonpositive_rows"]),
            (3, 2, 1),
        )
        self.assertEqual((counts["valid_gt"], counts["ignored_gt"]), (1, 1))

    def test_high_score_false_positive_reduces_ap(self):
        truth = {
            "a.jpg": {"valid": [(0.0, 0.0, 10.0, 10.0)], "ignored": []},
            "b.jpg": {"valid": [], "ignored": []},
        }
        predictions = {
            "a.jpg": [[0, 0, 10, 10, 0.8]],
            "b.jpg": [[0, 0, 10, 10, 0.9]],
        }
        metrics = evaluator.evaluate(truth, predictions, {"a.jpg": (40, 40), "b.jpg": (40, 40)})
        self.assertEqual((metrics["tp"], metrics["fp"], metrics["neutral"]), (1, 1, 0))
        self.assertAlmostEqual(metrics["ap_iou_gt_0_5_project"], 0.5)

    def test_duplicate_valid_detection_is_fp_even_when_ignore_overlaps(self):
        truth = {
            "a.jpg": {
                "valid": [(0.0, 0.0, 10.0, 10.0)],
                "ignored": [(0.0, 0.0, 10.0, 10.0)],
            }
        }
        predictions = {"a.jpg": [[0, 0, 10, 10, 0.9], [0, 0, 10, 10, 0.8]]}
        metrics = evaluator.evaluate(truth, predictions, {"a.jpg": (40, 40)})
        self.assertEqual((metrics["tp"], metrics["fp"], metrics["neutral"]), (1, 1, 0))
        self.assertAlmostEqual(metrics["ap_iou_gt_0_5_project"], 1.0)

    def test_ignored_region_is_neutral_before_valid_true_positive(self):
        truth = {
            "a.jpg": {
                "valid": [(0.0, 0.0, 10.0, 10.0)],
                "ignored": [(20.0, 20.0, 30.0, 30.0)],
            }
        }
        predictions = {"a.jpg": [[20, 20, 30, 30, 0.95], [0, 0, 10, 10, 0.8]]}
        metrics = evaluator.evaluate(truth, predictions, {"a.jpg": (40, 40)})
        self.assertEqual((metrics["tp"], metrics["fp"], metrics["neutral"]), (1, 0, 1))
        self.assertAlmostEqual(metrics["ap_iou_gt_0_5_project"], 1.0)

    def test_iou_boundary_and_tied_scores_are_deterministic(self):
        truth = {
            "a.jpg": {"valid": [(0.0, 0.0, 10.0, 10.0)], "ignored": []},
            "b.jpg": {"valid": [], "ignored": []},
        }
        predictions = {
            "a.jpg": [[0, 0, 10, 5, 0.9], [0, 0, 10, 10, 0.9]],
            "b.jpg": [[0, 0, 5, 5, 0.9]],
        }
        metrics = evaluator.evaluate(truth, predictions, {"a.jpg": (40, 40), "b.jpg": (40, 40)})
        # Exactly 0.5 IoU is excluded; a.jpg row order breaks the score tie.
        self.assertEqual((metrics["tp"], metrics["fp"]), (1, 2))
        self.assertAlmostEqual(metrics["ap_iou_gt_0_5_project"], 0.5)

    def test_clipped_and_empty_predictions_do_not_remove_images(self):
        truth = {
            "a.jpg": {"valid": [(0.0, 0.0, 10.0, 10.0)], "ignored": []},
            "b.jpg": {"valid": [], "ignored": []},
        }
        predictions = {"a.jpg": [[-5, -5, 10, 10, 0.9], [30, 30, 50, 50, 0.8]], "b.jpg": []}
        metrics = evaluator.evaluate(truth, predictions, {"a.jpg": (10, 10), "b.jpg": (10, 10)})
        self.assertEqual(metrics["images"], 2)
        self.assertEqual(metrics["images_with_no_predictions"], 1)
        self.assertEqual(metrics["predictions_clipped"], 1)
        self.assertEqual(metrics["predictions_dropped_empty_box"], 1)
        self.assertEqual((metrics["tp"], metrics["fp"]), (1, 0))

    def test_missing_manifest_image_or_nonfinite_prediction_is_rejected(self):
        truth = {"a.jpg": {"valid": [], "ignored": []}}
        with self.assertRaises(ValueError):
            evaluator.evaluate(truth, {}, {"a.jpg": (10, 10)})
        with self.assertRaises(ValueError):
            evaluator.evaluate(
                truth, {"a.jpg": [[0, 0, 10, 10, float("nan")]]}, {"a.jpg": (10, 10)}
            )


if __name__ == "__main__":
    unittest.main()
