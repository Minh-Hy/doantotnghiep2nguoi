"""Check LTFT density slices use the same window-ID cases as the original proxy."""

import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from t012_ltft_box_proxy import Box, WINDOW, analyze  # noqa: E402


class LTFTDensityTests(unittest.TestCase):
    def test_face_count_groups_partition_all_cases(self):
        frames = []
        for count in (1, 2, 3):
            boxes = [Box(identity, float(identity * 20), 0.0, 10.0, 10.0) for identity in range(count)]
            frames.extend([boxes] * WINDOW)

        groups = analyze(frames)
        self.assertEqual(groups["all"]["denominator"], 6)
        self.assertEqual(
            [groups[f"face-count-at-start/{label}"]["denominator"] for label in ("1", "2", "3+")],
            [1, 2, 3],
        )
        self.assertEqual(groups["multi-face-at-start"]["denominator"], 5)
        for candidate in ("P0-static", "P1-sequential"):
            self.assertEqual(groups["all"][f"{candidate}/correct-track"], 6)
            self.assertEqual(groups["all"][f"{candidate}/wrong-track"], 0)
            self.assertEqual(groups["all"][f"{candidate}/unresolved"], 0)


if __name__ == "__main__":
    unittest.main()
