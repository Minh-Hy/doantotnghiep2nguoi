"""Compare E1 detector call times on identical decoded frames in one CPU process.

The output contains aggregate measurements only. Input images and model files stay
outside Git; no predictions, image identifiers, or face crops are written.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import time
import zipfile
from pathlib import Path

from t011_widerface_predict import (
    EXPECTED_IMAGE_COUNT,
    IMAGE_PREFIX,
    IMAGE_SHA256,
    MODEL_SHA256,
    adapter_for,
    sha256,
)

SAMPLE_COUNT = 60
WARMUP_COUNT = 8
REPEATS = 3
CANDIDATES = ("yunet", "blazeface", "scrfd")
PROTOCOL_ID = "T-011-M1-reference-v1"


def spaced_positions(total: int, sample_count: int) -> list[int]:
    if total < sample_count or sample_count < 2:
        raise ValueError("Not enough images for the fixed M1 sample")
    positions = [round(i * (total - 1) / (sample_count - 1)) for i in range(sample_count)]
    if len(set(positions)) != sample_count:
        raise ValueError("Sample positions are not unique")
    return positions


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    at = (len(ordered) - 1) * fraction
    lower = math.floor(at)
    upper = math.ceil(at)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (at - lower)


def load_frames(archive_path: Path) -> tuple[list[object], list[tuple[int, int]]]:
    import cv2
    import numpy as np

    if sha256(archive_path) != IMAGE_SHA256:
        raise ValueError("WIDER image archive hash differs from pinned E1 input")
    with zipfile.ZipFile(archive_path) as archive:
        names = sorted(
            name for name in archive.namelist()
            if name.startswith(IMAGE_PREFIX) and name.lower().endswith(".jpg")
        )
        if len(names) != EXPECTED_IMAGE_COUNT:
            raise ValueError("WIDER image manifest count differs from E1")
        selected = [names[index] for index in spaced_positions(len(names), SAMPLE_COUNT)]
        frames = []
        shapes = []
        for name in selected:
            frame = cv2.imdecode(np.frombuffer(archive.read(name), dtype=np.uint8), cv2.IMREAD_COLOR)
            if frame is None:
                raise ValueError("Unable to decode selected WIDER image")
            frames.append(frame)
            shapes.append((int(frame.shape[1]), int(frame.shape[0])))
    return frames, shapes


def benchmark(models: dict[str, Path], frames: list[object]) -> dict[str, object]:
    adapters = {}
    try:
        for candidate in CANDIDATES:
            if sha256(models[candidate]) != MODEL_SHA256[candidate]:
                raise ValueError(f"{candidate} model hash differs from E1")
            adapters[candidate] = adapter_for(candidate, models[candidate])

        for candidate in CANDIDATES:
            for frame in frames[:WARMUP_COUNT]:
                adapters[candidate].detect(frame)

        elapsed = {candidate: [] for candidate in CANDIDATES}
        box_counts = {candidate: 0 for candidate in CANDIDATES}
        for repeat in range(REPEATS):
            order = CANDIDATES[repeat:] + CANDIDATES[:repeat]
            for candidate in order:
                for frame in frames:
                    started = time.perf_counter_ns()
                    boxes = adapters[candidate].detect(frame)
                    elapsed[candidate].append((time.perf_counter_ns() - started) / 1_000_000)
                    box_counts[candidate] += len(boxes)

        return {
            candidate: {
                "calls": len(elapsed[candidate]),
                "median_ms": percentile(elapsed[candidate], 0.5),
                "p95_ms": percentile(elapsed[candidate], 0.95),
                "min_ms": min(elapsed[candidate]),
                "max_ms": max(elapsed[candidate]),
                "total_boxes": box_counts[candidate],
                "runtime": adapters[candidate].configuration["runtime"],
            }
            for candidate in CANDIDATES
        }
    finally:
        for adapter in adapters.values():
            adapter.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", required=True, type=Path)
    for candidate in CANDIDATES:
        parser.add_argument(f"--{candidate}", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    frames, shapes = load_frames(args.images)
    models = {candidate: getattr(args, candidate) for candidate in CANDIDATES}
    measurements = benchmark(models, frames)
    widths = [shape[0] for shape in shapes]
    heights = [shape[1] for shape in shapes]
    result = {
        "protocol_id": PROTOCOL_ID,
        "commit": os.environ.get("GITHUB_SHA", "local-unpinned"),
        "image_sha256": IMAGE_SHA256,
        "model_sha256": {candidate: MODEL_SHA256[candidate] for candidate in CANDIDATES},
        "image_manifest_count": EXPECTED_IMAGE_COUNT,
        "sample_count": len(frames),
        "sample_rule": "60 evenly spaced positions in sorted WIDER ZIP image paths",
        "warmup_frames_per_candidate": WARMUP_COUNT,
        "repeats": REPEATS,
        "frame_width_range": [min(widths), max(widths)],
        "frame_height_range": [min(heights), max(heights)],
        "measurement_scope": "adapter.detect only; decoded BGR frames; model init excluded",
        "platform": platform.platform(),
        "processor": platform.processor(),
        "logical_cpu_count": os.cpu_count(),
        "candidates": measurements,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
