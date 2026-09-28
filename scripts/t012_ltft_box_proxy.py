"""T-012 exploratory LTFT bbox-only association; no images or check-in claims."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


SOURCE_SHA256 = {
    "choke1": "e79b7eccd835a449505d6998112b5104a480abec0b5f6cd0d69162b846222274",
    "choke2": "0b91483182869ba513164c23b587f3078fa7810966aec1858c61fc446b40d3d2",
}
WINDOW = 16
OUTCOMES = ("correct-track", "wrong-track", "unresolved")


@dataclass(frozen=True)
class Box:
    identity: int
    x: float
    y: float
    width: float
    height: float


def source_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse(path: Path, expected_sha256: str) -> list[list[Box]]:
    actual = source_digest(path)
    if actual != expected_sha256:
        raise ValueError(f"{path.name}: source SHA-256 {actual} differs from audited LTFT file")
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError(f"{path.name}: empty annotation")
    declared = int(lines[0])
    if declared != len(lines) - 1:
        raise ValueError(f"{path.name}: header {declared} != {len(lines) - 1} frame rows")
    frames: list[list[Box]] = []
    for expected_frame, line in enumerate(lines[1:]):
        row = line.split()
        if len(row) < 2 or int(row[0]) != expected_frame:
            raise ValueError(f"{path.name}: non-sequential frame at row {expected_frame}")
        count = int(row[1])
        if count < 0 or len(row) != 2 + 7 * count:
            raise ValueError(f"{path.name}: malformed detection count at frame {expected_frame}")
        frame: list[Box] = []
        ids: set[int] = set()
        for i in range(count):
            offset = 2 + 7 * i
            identity = int(row[offset])
            x, y, width, height = map(float, row[offset + 1 : offset + 5])
            face = int(row[offset + 5])
            confidence = float(row[offset + 6])
            if face not in (0, 1) or not all(
                math.isfinite(value) for value in (x, y, width, height, confidence)
            ):
                raise ValueError(f"{path.name}: invalid box/flag at frame {expected_frame}")
            if face == 0:
                continue
            if width <= 0 or height <= 0 or identity in ids:
                raise ValueError(f"{path.name}: invalid face box/duplicate ID at frame {expected_frame}")
            ids.add(identity)
            frame.append(Box(identity, x, y, width, height))
        frames.append(frame)
    return frames


def iou(left: Box, right: Box) -> float:
    x0 = max(left.x, right.x)
    y0 = max(left.y, right.y)
    x1 = min(left.x + left.width, right.x + right.width)
    y1 = min(left.y + left.height, right.y + right.height)
    intersection = max(0.0, x1 - x0) * max(0.0, y1 - y0)
    if intersection == 0:
        return 0.0
    union = left.width * left.height + right.width * right.height - intersection
    return intersection / union


def select(reference: Box, candidates: list[Box]) -> Box | None:
    if not candidates:
        return None
    scores = [iou(reference, candidate) for candidate in candidates]
    best = max(scores)
    if best <= 0 or scores.count(best) != 1:
        return None
    return candidates[scores.index(best)]


def outcome(chosen: Box | None, target_id: int) -> str:
    if chosen is None:
        return "unresolved"
    return "correct-track" if chosen.identity == target_id else "wrong-track"


def analyze(frames: list[list[Box]]) -> dict[str, object]:
    counts: dict[str, Counter[str]] = {
        "all": Counter(),
        "target-annotated-at-end": Counter(),
        "target-not-annotated-at-end": Counter(),
        "multi-face-at-start": Counter(),
        "face-count-at-start/1": Counter(),
        "face-count-at-start/2": Counter(),
        "face-count-at-start/3+": Counter(),
    }
    for start in range(0, len(frames) - WINDOW + 1, WINDOW):
        end = start + WINDOW - 1
        for target in frames[start]:
            groups = ["all"]
            face_count = len(frames[start])
            groups.append(f"face-count-at-start/{face_count if face_count < 3 else '3+'}")
            end_ids = {box.identity for box in frames[end]}
            groups.append(
                "target-annotated-at-end"
                if target.identity in end_ids
                else "target-not-annotated-at-end"
            )
            if len(frames[start]) >= 2:
                groups.append("multi-face-at-start")
            static = select(target, frames[end])
            sequential: Box | None = target
            for index in range(start + 1, end + 1):
                if sequential is None:
                    break
                sequential = select(sequential, frames[index])
            for group in groups:
                counts[group]["denominator"] += 1
                counts[group][f"P0-static/{outcome(static, target.identity)}"] += 1
                counts[group][f"P1-sequential/{outcome(sequential, target.identity)}"] += 1
    for group, counter in counts.items():
        for candidate in ("P0-static", "P1-sequential"):
            total = sum(counter[f"{candidate}/{label}"] for label in OUTCOMES)
            if total != counter["denominator"]:
                raise AssertionError(f"{group}: outcomes do not reconcile for {candidate}")
    for key in counts["all"]:
        if sum(counts[f"face-count-at-start/{label}"][key] for label in ("1", "2", "3+")) != counts["all"][key]:
            raise AssertionError(f"face-count groups do not reconcile for {key}")
    return {
        group: {key: counter[key] for key in ["denominator"] + [
            f"{candidate}/{label}"
            for candidate in ("P0-static", "P1-sequential")
            for label in OUTCOMES
        ]}
        for group, counter in counts.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--choke1", type=Path, required=True)
    parser.add_argument("--choke2", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results: dict[str, object] = {}
    for name in ("choke1", "choke2"):
        path = getattr(args, name)
        frames = parse(path, SOURCE_SHA256[name])
        results[name] = {"frames": len(frames), "groups": analyze(frames)}
    summary = {
        "scope": "Exploratory annotation-only geometry; oracle initial bbox; not video, identity verification or check-in",
        "protocol": "T-012-S4-box-only-proxy-protocol.md, preregistered at 0540452",
        "source_sha256": SOURCE_SHA256,
        "window_frames": WINDOW,
        "candidate_rule": "unique maximum IoU > 0; otherwise unresolved",
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
