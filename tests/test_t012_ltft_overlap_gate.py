"""Check X-012-H gate semantics and outcome accounting on small synthetic tracks."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from t012_ltft_box_proxy import Box, WINDOW
from t012_ltft_overlap_gate import analyze, select, trace


def box(identity: int, x: float) -> Box:
    return Box(identity=identity, x=x, y=0.0, width=10.0, height=10.0)


class OverlapGateTests(unittest.TestCase):
    def test_gate_rejects_weak_overlap_that_p1_would_accept(self) -> None:
        target = box(1, 0)
        distractor = box(2, 8)  # IoU = 2/18: positive but below 0.3.
        self.assertEqual(select(target, [distractor], 0.0), distractor)
        self.assertIsNone(select(target, [distractor], 0.3))

    def test_missing_target_can_be_wrong_for_p1_and_unresolved_for_p2(self) -> None:
        target = box(1, 0)
        frames = [[target]] + [[box(2, 8)]] + [[box(2, 8)] for _ in range(WINDOW - 2)]
        self.assertEqual(trace(frames, 0, target, 0.0), ("wrong-track", True))
        self.assertEqual(trace(frames, 0, target, 0.3), ("unresolved", False))
        result = analyze(frames)
        counts = result["groups"]["all"]
        self.assertEqual(counts["denominator"], 1)
        self.assertEqual(counts["P1/wrong-track"], 1)
        self.assertEqual(counts["P2/unresolved"], 1)
        self.assertEqual(result["transitions"]["wrong-track->unresolved"], 1)


if __name__ == "__main__":
    unittest.main()
