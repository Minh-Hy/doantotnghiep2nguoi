"""Post-hoc LTFT box-only path diagnosis; does not alter the P0/P1 run."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from t012_ltft_box_proxy import Box, OUTCOMES, SOURCE_SHA256, WINDOW, analyze, outcome, parse, select


EXPECTED_P1_ENDPOINT = {
    "choke1": {"correct-track": 384, "wrong-track": 17, "unresolved": 94},
    "choke2": {"correct-track": 374, "wrong-track": 21, "unresolved": 134},
}


def diagnose(frames: list[list[Box]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for start in range(0, len(frames) - WINDOW + 1, WINDOW):
        end = start + WINDOW - 1
        for target in frames[start]:
            counts["denominator"] += 1
            selected = target
            first_wrong_target_annotated: bool | None = None
            for frame_index in range(start + 1, end + 1):
                selected = select(selected, frames[frame_index])
                if selected is None:
                    break
                if selected.identity != target.identity and first_wrong_target_annotated is None:
                    first_wrong_target_annotated = any(
                        box.identity == target.identity for box in frames[frame_index]
                    )
            endpoint = outcome(selected, target.identity)
            counts[f"end/{endpoint}"] += 1
            if first_wrong_target_annotated is None:
                counts["never-wrong"] += 1
                counts[f"never-wrong/end-{endpoint}"] += 1
            else:
                counts["ever-wrong"] += 1
                label = (
                    "target-annotated-at-first-wrong"
                    if first_wrong_target_annotated
                    else "target-not-annotated-at-first-wrong"
                )
                counts[label] += 1
                counts[f"ever-wrong/end-{endpoint}"] += 1
    if counts["ever-wrong"] + counts["never-wrong"] != counts["denominator"]:
        raise AssertionError("Ever/never-wrong does not reconcile")
    if sum(counts[f"end/{label}"] for label in OUTCOMES) != counts["denominator"]:
        raise AssertionError("Endpoint outcomes do not reconcile")
    return dict(sorted(counts.items()))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--choke1", type=Path, required=True)
    parser.add_argument("--choke2", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = {}
    for name in ("choke1", "choke2"):
        frames = parse(getattr(args, name), SOURCE_SHA256[name])
        replay = analyze(frames)["all"]
        actual = {label: replay[f"P1-sequential/{label}"] for label in EXPECTED_P1_ENDPOINT[name]}
        if actual != EXPECTED_P1_ENDPOINT[name]:
            raise ValueError(f"{name}: endpoint replay differs from original report: {actual}")
        counts = diagnose(frames)
        for label, expected in actual.items():
            if counts[f"end/{label}"] != expected:
                raise ValueError(f"{name}: path diagnosis differs from endpoint replay for {label}")
        results[name] = counts
    summary = {
        "scope": "Post-hoc descriptive diagnosis of intermediate P1 ID switches; not check-in",
        "source_sha256": SOURCE_SHA256,
        "window_frames": WINDOW,
        "original_endpoint_gate": EXPECTED_P1_ENDPOINT,
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
