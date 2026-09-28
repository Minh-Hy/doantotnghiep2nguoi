"""Evaluate T-011 WIDER FACE validation predictions with project E1 AP protocol.

Only aggregate metrics are written. Prediction JSON with image paths and boxes stays
outside Git. This is not the official WIDER Easy/Medium/Hard evaluator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import zipfile
from pathlib import Path
from typing import Any

PROTOCOL_VERSION = "T-010-E1-2026-09-27"
EXPECTED_IMAGES_SHA256 = "f9efbd09f28c5d2d884be8c0eaef3967158c866a593fc36ab0413e4b2a58a17a"
EXPECTED_ANNOTATIONS_SHA256 = "c7561e4f5e7a118c249e0a5c5c902b0de90bbf120d7da9fa28d99041f68a8a5c"
ANNOTATION_NAME = "wider_face_split/wider_face_val_bbx_gt.txt"
IMAGE_PREFIX = "WIDER_val/images/"
EXPECTED_IMAGE_COUNT = 3226
EXPECTED_BOX_ROWS = 39708
IOU_THRESHOLD = 0.5

Box = tuple[float, float, float, float]
GroundTruth = dict[str, dict[str, list[Box]]]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checked_zip(path: Path) -> zipfile.ZipFile:
    archive = zipfile.ZipFile(path)
    for name in archive.namelist():
        normalized = Path(name.replace("\\", "/"))
        if normalized.is_absolute() or ".." in normalized.parts:
            archive.close()
            raise ValueError("Unsafe archive path")
    bad = archive.testzip()
    if bad is not None:
        archive.close()
        raise ValueError("ZIP CRC failure")
    return archive


def parse_annotations(text: str) -> tuple[GroundTruth, dict[str, int]]:
    """Parse the original validation TXT without silently dropping annotation rows."""
    lines = text.splitlines()
    position = 0
    truth: GroundTruth = {}
    counts = {
        "images": 0,
        "box_rows": 0,
        "invalid_flag_rows": 0,
        "nonpositive_rows": 0,
        "valid_gt": 0,
        "ignored_gt": 0,
    }
    while position < len(lines):
        relative = lines[position].strip()
        position += 1
        if not relative or relative in truth or position >= len(lines):
            raise ValueError("Missing or duplicate annotation image path")
        try:
            number = int(lines[position].strip())
        except ValueError as exc:
            raise ValueError("Invalid annotation box count") from exc
        position += 1
        if number < 0 or position + number > len(lines):
            raise ValueError("Negative box count or truncated annotation")
        valid: list[Box] = []
        ignored: list[Box] = []
        for _ in range(number):
            fields = lines[position].split()
            position += 1
            if len(fields) != 10:
                raise ValueError("Unexpected annotation field count")
            try:
                values = [int(field) for field in fields]
            except ValueError as exc:
                raise ValueError("Noninteger annotation") from exc
            x, y, width, height = values[:4]
            invalid = values[7]
            if invalid not in (0, 1):
                raise ValueError("Unexpected invalid flag")
            counts["box_rows"] += 1
            counts["invalid_flag_rows"] += invalid == 1
            if width <= 0 or height <= 0:
                counts["nonpositive_rows"] += 1
                continue
            box = (float(x), float(y), float(x + width), float(y + height))
            if invalid:
                ignored.append(box)
                counts["ignored_gt"] += 1
            else:
                valid.append(box)
                counts["valid_gt"] += 1
        truth[relative] = {"valid": valid, "ignored": ignored}
        counts["images"] += 1
    return truth, counts


def iou(left: Box, right: Box) -> float:
    """Continuous-coordinate intersection over union, without a +1 pixel rule."""
    x1 = max(left[0], right[0])
    y1 = max(left[1], right[1])
    x2 = min(left[2], right[2])
    y2 = min(left[3], right[3])
    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    left_area = (left[2] - left[0]) * (left[3] - left[1])
    right_area = (right[2] - right[0]) * (right[3] - right[1])
    union = left_area + right_area - intersection
    return intersection / union if union > 0 else 0.0


def clip_prediction(box: Box, width: int, height: int) -> Box | None:
    if width <= 0 or height <= 0 or not all(math.isfinite(value) for value in box):
        raise ValueError("Invalid image size or nonfinite prediction box")
    x1 = min(max(box[0], 0.0), float(width))
    y1 = min(max(box[1], 0.0), float(height))
    x2 = min(max(box[2], 0.0), float(width))
    y2 = min(max(box[3], 0.0), float(height))
    if x2 <= x1 or y2 <= y1:
        return None
    return (x1, y1, x2, y2)


def ap_all_points(outcomes: list[str], total_gt: int) -> tuple[float, float]:
    """VOC-style all-points precision envelope after neutral predictions are removed."""
    if total_gt < 0:
        raise ValueError("Negative ground-truth count")
    if total_gt == 0:
        return 0.0, 0.0
    tp = fp = 0
    recalls = [0.0]
    precisions = [0.0]
    for outcome in outcomes:
        if outcome == "neutral":
            continue
        if outcome == "tp":
            tp += 1
        elif outcome == "fp":
            fp += 1
        else:
            raise ValueError("Unknown prediction outcome")
        recalls.append(tp / total_gt)
        precisions.append(tp / (tp + fp))
    recalls.append(1.0)
    precisions.append(0.0)
    for index in range(len(precisions) - 2, -1, -1):
        precisions[index] = max(precisions[index], precisions[index + 1])
    ap = sum(
        (recalls[index + 1] - recalls[index]) * precisions[index + 1]
        for index in range(len(recalls) - 1)
        if recalls[index + 1] > recalls[index]
    )
    return ap, tp / total_gt


def evaluate(
    truth: GroundTruth,
    predictions: dict[str, list[list[int | float]]],
    image_sizes: dict[str, tuple[int, int]],
) -> dict[str, int | float]:
    """Score all manifest images; each valid GT can be matched once."""
    if set(predictions) != set(truth) or set(image_sizes) != set(truth):
        raise ValueError("Prediction/image-size manifest differs from ground truth")
    total_gt = sum(len(entry["valid"]) for entry in truth.values())
    ordered: list[tuple[float, str, int, Box]] = []
    dropped = clipped = empty_images = 0
    for image_path in sorted(truth):
        width, height = image_sizes[image_path]
        rows = predictions[image_path]
        if not isinstance(rows, list):
            raise ValueError("Prediction rows must be a list")
        if not rows:
            empty_images += 1
        for index, row in enumerate(rows):
            if not isinstance(row, list) or len(row) != 5:
                raise ValueError("Prediction must be [x1,y1,x2,y2,score]")
            if any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in row):
                raise ValueError("Prediction fields must be numeric")
            values = tuple(float(value) for value in row)
            if not all(math.isfinite(value) for value in values):
                raise ValueError("Nonfinite prediction")
            original = values[:4]
            box = clip_prediction(original, width, height)
            if box is None:
                dropped += 1
                continue
            clipped += box != original
            ordered.append((-values[4], image_path, index, box))
    ordered.sort(key=lambda item: (item[0], item[1], item[2]))

    matched = {path: set() for path in truth}
    outcomes: list[str] = []
    for _, path, _, prediction in ordered:
        valid = truth[path]["valid"]
        best_iou = 0.0
        best_index = -1
        for index, target in enumerate(valid):
            overlap = iou(prediction, target)
            if overlap > best_iou:
                best_iou = overlap
                best_index = index
        if best_iou > IOU_THRESHOLD:
            if best_index in matched[path]:
                outcomes.append("fp")
            else:
                matched[path].add(best_index)
                outcomes.append("tp")
        elif any(iou(prediction, target) > IOU_THRESHOLD for target in truth[path]["ignored"]):
            outcomes.append("neutral")
        else:
            outcomes.append("fp")
    ap, recall = ap_all_points(outcomes, total_gt)
    return {
        "images": len(truth),
        "valid_gt": total_gt,
        "prediction_rows": len(ordered) + dropped,
        "predictions_evaluated": len(ordered),
        "predictions_dropped_empty_box": dropped,
        "predictions_clipped": clipped,
        "images_with_no_predictions": empty_images,
        "tp": outcomes.count("tp"),
        "fp": outcomes.count("fp"),
        "neutral": outcomes.count("neutral"),
        "ap_iou_gt_0_5_project": ap,
        "max_recall": recall,
    }


def read_image_sizes(
    image_zip: zipfile.ZipFile, truth: GroundTruth
) -> tuple[dict[str, tuple[int, int]], int]:
    import cv2
    import numpy as np

    image_names = [name for name in image_zip.namelist() if name.lower().endswith(".jpg")]
    if len(image_names) != len(set(image_names)) or len(image_names) != len(truth):
        raise ValueError("Image ZIP count or path duplication differs from annotation manifest")
    expected_names = {IMAGE_PREFIX + relative for relative in truth}
    if set(image_names) != expected_names:
        raise ValueError("Image ZIP paths differ from annotation manifest")
    sizes: dict[str, tuple[int, int]] = {}
    outside = 0
    for relative in sorted(truth):
        image = cv2.imdecode(
            np.frombuffer(image_zip.read(IMAGE_PREFIX + relative), dtype=np.uint8),
            cv2.IMREAD_COLOR,
        )
        if image is None:
            raise ValueError("Cannot decode validation image")
        height, width = image.shape[:2]
        sizes[relative] = (width, height)
        for box in truth[relative]["valid"] + truth[relative]["ignored"]:
            outside += box[0] < 0 or box[1] < 0 or box[2] > width or box[3] > height
    return sizes, outside


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--predictions", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    if not args.preflight_only and (args.predictions is None or args.output is None):
        parser.error("--predictions and --output are required for scoring")

    source_hashes = {"images": sha256(args.images), "annotations": sha256(args.annotations)}
    if source_hashes != {
        "images": EXPECTED_IMAGES_SHA256,
        "annotations": EXPECTED_ANNOTATIONS_SHA256,
    }:
        raise ValueError("WIDER FACE source hash differs from audited data gate")
    with checked_zip(args.annotations) as annotation_zip:
        truth, counts = parse_annotations(
            annotation_zip.read(ANNOTATION_NAME).decode("utf-8")
        )
    if counts["images"] != EXPECTED_IMAGE_COUNT or counts["box_rows"] != EXPECTED_BOX_ROWS:
        raise ValueError("WIDER FACE annotation count differs from audited data gate")
    with checked_zip(args.images) as image_zip:
        sizes, outside = read_image_sizes(image_zip, truth)
    if outside:
        raise ValueError(
            f"{outside} GT boxes extend beyond image bounds; review protocol before scoring"
        )
    if args.preflight_only:
        print(json.dumps({
            "scope": "E1 GT/image preflight only; no detector scores",
            "source_sha256": source_hashes,
            "annotation_counts": counts,
            "gt_outside_image": outside,
        }, ensure_ascii=False))
        return

    payload: Any = json.loads(args.predictions.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("protocol_version") != PROTOCOL_VERSION:
        raise ValueError("Prediction protocol version mismatch")
    if payload.get("source_sha256") != source_hashes:
        raise ValueError("Prediction source hashes differ from evaluator inputs")
    candidate = payload.get("candidate")
    if not isinstance(candidate, dict) or not all(
        isinstance(candidate.get(key), str) and candidate[key]
        for key in ("name", "weight_sha256", "configuration_id")
    ):
        raise ValueError("Prediction candidate is missing pinned metadata")
    if not isinstance(payload.get("predictions"), dict):
        raise ValueError("Prediction map is missing")
    metrics = evaluate(truth, payload["predictions"], sizes)
    summary = {
        "scope": "T-011 E1 project AP on WIDER FACE validation TXT; not official Easy/Medium/Hard",
        "protocol_version": PROTOCOL_VERSION,
        "source_sha256": source_hashes,
        "candidate": candidate,
        "annotation_counts": counts,
        "gt_outside_image": outside,
        "metrics": metrics,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"candidate": candidate["name"], "metrics": metrics}, ensure_ascii=False))


if __name__ == "__main__":
    main()
