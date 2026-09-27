"""Check that one/multi-face E1 groups preserve the original matching counts."""

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from t011_widerface_evaluate import evaluate  # noqa: E402
from t012_widerface_one_multi import score_groups  # noqa: E402


class OneMultiTests(unittest.TestCase):
    def setUp(self):
        self.truth = {
            "one.jpg": {"valid": [(0.0, 0.0, 10.0, 10.0)], "ignored": []},
            "multi.jpg": {
                "valid": [(0.0, 0.0, 10.0, 10.0), (20.0, 20.0, 40.0, 40.0)],
                "ignored": [],
            },
            "zero.jpg": {"valid": [], "ignored": [(50.0, 50.0, 60.0, 60.0)]},
        }
        self.predictions = {
            "one.jpg": [[0, 0, 10, 10, 0.9]],
            "multi.jpg": [
                [0, 0, 10, 10, 0.95],
                [20, 20, 40, 40, 0.8],
                [70, 70, 80, 80, 0.7],
            ],
            "zero.jpg": [[50, 50, 60, 60, 0.85], [0, 0, 10, 10, 0.6]],
        }
        self.sizes = {name: (100, 100) for name in self.truth}

    def test_groups_reconcile_and_zero_valid_has_no_ap(self):
        original = evaluate(self.truth, self.predictions, self.sizes)
        result = score_groups(self.truth, self.predictions, self.sizes, original)
        self.assertEqual([result[name]["images"] for name in ("zero_valid", "one_valid", "multi_valid")], [1, 1, 1])
        self.assertEqual([result[name]["valid_gt"] for name in ("zero_valid", "one_valid", "multi_valid")], [0, 1, 2])
        self.assertEqual(result["zero_valid"]["metrics"]["ap_iou_gt_0_5_project"], None)
        self.assertEqual(result["zero_valid"]["metrics"]["neutral"], 1)
        self.assertEqual(sum(result[name]["metrics"]["tp"] for name in result), original["tp"])
        self.assertEqual(sum(result[name]["metrics"]["fp"] for name in result), original["fp"])

    def test_bad_reference_is_rejected(self):
        original = evaluate(self.truth, self.predictions, self.sizes)
        original["fp"] += 1
        with self.assertRaisesRegex(ValueError, "does not reconcile"):
            score_groups(self.truth, self.predictions, self.sizes, original)


if __name__ == "__main__":
    unittest.main()
