"""Describe T-011 E1 matched and missed WIDER faces by annotation attributes.

Replays the pinned IoU > 0.5 matching rule without changing scores or candidate
configuration. Only aggregate counts are written; per-image predictions stay outside Git.
These slices are not the official WIDER difficulty benchmark or a tuning set.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from t011_widerface_evaluate import (
    ANNOTATION_NAME,
    EXPECTED_ANNOTATIONS_SHA256,
    EXPECTED_BOX_ROWS,
    EXPECTED_IMAGE_COUNT,
    EXPECTED_IMAGES_SHA256,
    IOU_THRESHOLD,
    PROTOCOL_VERSION,
    Box,
    checked_zip,
    clip_prediction,
    iou,
    parse_annotations,
    read_image_sizes,
    sha256,
)
from t011_widerface_predict import CONFIGURATION_ID, MODEL_SHA256

SIZE_BUCKETS = ("lt16", "16to31", "32to95", "ge96")
ATTRIBUTES = ("blur", "illumination", "occlusion", "pose")


def parse_valid_metadata(text: str, truth: dict[str, dict[str, list[Box]]]) -> dict[str, list[dict[str, int]]]:
    """Keep original annotation codes in the order of each valid GT box."""
    lines = text.splitlines()
    metadata: dict[str, list[dict[str, int]]] = {}
    position = 0
    while position < len(lines):
        path = lines[position].strip()
        position += 1
        number = int(lines[position].strip())
        position += 1
        if path in metadata or path not in truth:
            raise ValueError("Metadata path missing or duplicated in validated GT")
        valid: list[dict[str, int]] = []
        boxes: list[Box] = []
        for _ in range(number):
            fields = [int(value) for value in lines[position].split()]
            position += 1
            if len(fields) != 10:
                raise ValueError("Unexpected metadata field count")
            x, y, width, height = fields[:4]
            if width <= 0 or height <= 0 or fields[7] == 1:
                continue
            boxes.append((float(x), float(y), float(x + width), float(y + height)))
            valid.append({
                "blur": fields[4],
                "illumination": fields[6],
                "occlusion": fields[8],
                "pose": fields[9],
            })
        if boxes != truth[path]["valid"]:
            raise ValueError("Metadata valid-box order differs from pinned GT parser")
        metadata[path] = valid
    if set(metadata) != set(truth):
        raise ValueError("Metadata manifest differs from pinned GT parser")
    return metadata


def size_bucket(box: Box) -> str:
    edge = math.sqrt((box[2] - box[0]) * (box[3] - box[1]))
    if edge < 16:
        return SIZE_BUCKETS[0]
    if edge < 32:
        return SIZE_BUCKETS[1]
    if edge < 96:
        return SIZE_BUCKETS[2]
    return SIZE_BUCKETS[3]


def analyze(
    truth: dict[str, dict[str, list[Box]]],
    metadata: dict[str, list[dict[str, int]]],
    predictions: dict[str, list[list[int | float]]],
    image_sizes: dict[str, tuple[int, int]],
) -> dict[str, Any]:
    if set(truth) != set(metadata) or set(truth) != set(predictions) or set(truth) != set(image_sizes):
        raise ValueError("Prediction/metadata/image manifest differs from GT")
    totals: dict[str, dict[str, list[int]]] = {
        "size_px_sqrt_area": defaultdict(lambda: [0, 0]),
        **{name + "_code": defaultdict(lambda: [0, 0]) for name in ATTRIBUTES},
    }
    prediction_rows = dropped = clipped = matched_total = 0
    for path in sorted(truth):
        valid = truth[path]["valid"]
        attributes = metadata[path]
        if len(valid) != len(attributes):
            raise ValueError("GT and metadata count differ")
        width, height = image_sizes[path]
        rows = predictions[path]
        if not isinstance(rows, list):
            raise ValueError("Prediction rows must be a list")
        ordered: list[tuple[float, int, Box]] = []
        prediction_rows += len(rows)
        for index, row in enumerate(rows):
            if not isinstance(row, list) or len(row) != 5 or any(
                isinstance(value, bool) or not isinstance(value, (int, float)) for value in row
            ):
                raise ValueError("Prediction must be numeric [x1,y1,x2,y2,score]")
            values = tuple(float(value) for value in row)
            if not all(math.isfinite(value) for value in values):
                raise ValueError("Nonfinite prediction")
            original = values[:4]
            box = clip_prediction(original, width, height)
            if box is None:
                dropped += 1
                continue
            clipped += box != original
            ordered.append((-values[4], index, box))
        ordered.sort(key=lambda item: (item[0], item[1]))
        matched: set[int] = set()
        for _, _, box in ordered:
            best_iou = 0.0
            best_index = -1
            for index, target in enumerate(valid):
                overlap = iou(box, target)
                if overlap > best_iou:
                    best_iou = overlap
                    best_index = index
            if best_iou > IOU_THRESHOLD and best_index not in matched:
                matched.add(best_index)
        matched_total += len(matched)
        for index, box in enumerate(valid):
            hit = int(index in matched)
            groups = {"size_px_sqrt_area": size_bucket(box)}
            groups.update({name + "_code": str(attributes[index][name]) for name in ATTRIBUTES})
            for category, key in groups.items():
                totals[category][key][0] += 1
                totals[category][key][1] += hit
    groups_out: dict[str, dict[str, dict[str, int | float]]] = {}
    for category, groups in totals.items():
        groups_out[category] = {
            key: {
                "valid_gt": values[0],
                "matched_gt": values[1],
                "missed_gt": values[0] - values[1],
                "max_recall": values[1] / values[0],
            }
            for key, values in sorted(groups.items())
        }
    expected_gt = sum(len(entry["valid"]) for entry in truth.values())
    for category, groups in groups_out.items():
        if sum(row["valid_gt"] for row in groups.values()) != expected_gt or sum(
            row["matched_gt"] for row in groups.values()
        ) != matched_total:
            raise ValueError(f"Slice counts do not reconcile for {category}")
    return {
        "images": len(truth),
        "valid_gt": expected_gt,
        "matched_gt": matched_total,
        "missed_gt": expected_gt - matched_total,
        "prediction_rows": prediction_rows,
        "dropped_empty_box": dropped,
        "clipped_box": clipped,
        "groups": groups_out,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-tp", type=int, required=True)
    parser.add_argument("--expected-rows", type=int, required=True)
    parser.add_argument("--expected-dropped", type=int, required=True)
    parser.add_argument("--expected-clipped", type=int, required=True)
    args = parser.parse_args()

    source_hashes = {"images": sha256(args.images), "annotations": sha256(args.annotations)}
    if source_hashes != {"images": EXPECTED_IMAGES_SHA256, "annotations": EXPECTED_ANNOTATIONS_SHA256}:
        raise ValueError("WIDER source hash differs from T-011 data gate")
    with checked_zip(args.annotations) as archive:
        text = archive.read(ANNOTATION_NAME).decode("utf-8")
    truth, counts = parse_annotations(text)
    if counts["images"] != EXPECTED_IMAGE_COUNT or counts["box_rows"] != EXPECTED_BOX_ROWS:
        raise ValueError("GT counts differ from T-011 data gate")
    metadata = parse_valid_metadata(text, truth)
    with checked_zip(args.images) as archive:
        image_sizes, outside = read_image_sizes(archive, truth)
    if outside:
        raise ValueError("GT outside image; T-011 protocol needs review")

    payload: Any = json.loads(args.predictions.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("protocol_version") != PROTOCOL_VERSION:
        raise ValueError("Prediction protocol differs from T-011")
    if payload.get("source_sha256") != source_hashes or not isinstance(payload.get("predictions"), dict):
        raise ValueError("Prediction source or map differs from T-011")
    candidate = payload.get("candidate")
    if not isinstance(candidate, dict) or candidate.get("name") not in CONFIGURATION_ID:
        raise ValueError("Unknown candidate")
    name = candidate["name"]
    if candidate.get("configuration_id") != CONFIGURATION_ID[name] or candidate.get(
        "weight_sha256"
    ) != MODEL_SHA256[name]:
        raise ValueError("Candidate weight/config differs from T-011")
    metrics = analyze(truth, metadata, payload["predictions"], image_sizes)
    expected = (args.expected_tp, args.expected_rows, args.expected_dropped, args.expected_clipped)
    actual = (
        metrics["matched_gt"],
        metrics["prediction_rows"],
        metrics["dropped_empty_box"],
        metrics["clipped_box"],
    )
    if actual != expected:
        raise ValueError(f"T-012 replay does not reconcile with T-011: {actual} != {expected}")
    summary = {
        "scope": "T-012 descriptive WIDER error slices; not official difficulty benchmark or config tuning",
        "protocol_version": PROTOCOL_VERSION,
        "source_sha256": source_hashes,
        "candidate": candidate,
        "size_definition": "sqrt(valid GT box area) in original-image pixels: <16, 16-<32, 32-<96, >=96",
        "attribute_definition": "Raw validation TXT integer codes; no severity interpretation",
        "metrics": metrics,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"candidate": name, "metrics": metrics}, ensure_ascii=False))


if __name__ == "__main__":
    main()
