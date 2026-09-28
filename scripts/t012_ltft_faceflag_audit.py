"""T-012 D2: audit raw LTFT face flags at P1's first wrong-ID frame."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from t012_ltft_box_proxy import Box, SOURCE_SHA256, WINDOW, parse, select


EXPECTED_FIRST_WRONG = {"choke1": 18, "choke2": 23}


def raw_flags(path: Path, frame_count: int) -> list[dict[int, set[int]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if int(lines[0]) != frame_count or len(lines) - 1 != frame_count:
        raise ValueError("Raw rows differ from validated frame count")
    result: list[dict[int, set[int]]] = []
    for expected_frame, line in enumerate(lines[1:]):
        parts = line.split()
        if int(parts[0]) != expected_frame or len(parts) != 2 + 7 * int(parts[1]):
            raise ValueError("Raw row structure differs from validated annotation")
        flags: dict[int, set[int]] = {}
        for detection in range(int(parts[1])):
            index = 2 + 7 * detection
            flags.setdefault(int(parts[index]), set()).add(int(parts[index + 5]))
        result.append(flags)
    return result


def audit(frames: list[list[Box]], flags: list[dict[int, set[int]]]) -> dict[str, int]:
    if len(frames) != len(flags):
        raise ValueError("Frame/flag count differs")
    counts: Counter[str] = Counter()
    for start in range(0, len(frames) - WINDOW + 1, WINDOW):
        for target in frames[start]:
            selected = target
            for frame_index in range(start + 1, start + WINDOW):
                selected = select(selected, frames[frame_index])
                if selected is None:
                    break
                if selected.identity != target.identity:
                    counts["first-wrong"] += 1
                    raw = flags[frame_index].get(target.identity, set())
                    if 1 in raw:
                        raise ValueError("First wrong frame unexpectedly has a valid target box")
                    if raw == {0}:
                        counts["target-ID-face-0"] += 1
                    elif not raw:
                        counts["target-ID-not-in-raw-frame"] += 1
                    else:
                        raise ValueError(f"Unexpected raw face flag set: {raw}")
                    break
    if counts["target-ID-face-0"] + counts["target-ID-not-in-raw-frame"] != counts[
        "first-wrong"
    ]:
        raise AssertionError("D2 categories do not reconcile")
    return {key: counts[key] for key in (
        "first-wrong", "target-ID-face-0", "target-ID-not-in-raw-frame"
    )}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--choke1", type=Path, required=True)
    parser.add_argument("--choke2", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = {}
    for name in ("choke1", "choke2"):
        path = getattr(args, name)
        frames = parse(path, SOURCE_SHA256[name])
        result = audit(frames, raw_flags(path, len(frames)))
        if result["first-wrong"] != EXPECTED_FIRST_WRONG[name]:
            raise ValueError(f"{name}: D2 first-wrong count differs from D1")
        results[name] = result
    summary = {
        "scope": "D2 post-hoc raw face-flag audit; not physical absence or check-in",
        "source_sha256": SOURCE_SHA256,
        "first_wrong_gate": EXPECTED_FIRST_WRONG,
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
