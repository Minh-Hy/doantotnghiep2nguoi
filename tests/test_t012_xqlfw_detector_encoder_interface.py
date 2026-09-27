"""Guard YuNet landmark schema and pair-set intersection before the real run."""

import pathlib
import sys
import unittest

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from t012_xqlfw_detector_encoder_interface import valid_pair_indices, yunet_landmarks  # noqa: E402


class DetectorEncoderInterfaceTests(unittest.TestCase):
    def test_common_pair_set_requires_both_images_for_each_detector(self):
        pairs = [
            ("a", "b", True, 0),
            ("a", "c", False, 0),
            ("b", "c", False, 1),
        ]
        scrfd = set(valid_pair_indices(pairs, {"a", "b", "c"}))
        yunet = set(valid_pair_indices(pairs, {"a", "b"}))
        self.assertEqual(scrfd, {0, 1, 2})
        self.assertEqual(yunet, {0})
        self.assertEqual(scrfd & yunet, {0})

    def test_yunet_landmark_columns_and_invalid_row(self):
        row = np.array([0, 0, 10, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0.9], dtype=np.float32)
        np.testing.assert_array_equal(yunet_landmarks(row), [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]])
        with self.assertRaisesRegex(ValueError, "15 finite"):
            yunet_landmarks(row[:14])


if __name__ == "__main__":
    unittest.main()
