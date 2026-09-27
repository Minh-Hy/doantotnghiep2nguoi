"""Compare pinned E1 detectors by images with zero, one, or multiple valid faces.

This is a descriptive T-012 analysis after the full T-011 E1 run. It reuses
the exact project evaluator and never saves per-image boxes in Git.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

from t011_widerface_evaluate import (
    ANNOTATION_NAME,
    EXPECTED_ANNOTATIONS_SHA256,
    EXPECTED_BOX_ROWS,
    EXPECTED_IMAGE_COUNT,
    EXPECTED_IMAGES_SHA256,
    PROTOCOL_VERSION,
    GroundTruth,
    checked_zip,
    evaluate,
    parse_annotations,
    read_image_sizes,
    sha256,
)
from t011_widerface_predict import CONFIGURATION_ID, MODEL_SHA256
from t012_widerface_error_slices import size_bucket

GROUPS = ("zero_valid", "one_valid", "multi_valid")
ADDITIVE_METRICS = (
    "images",
    "valid_gt",
    "prediction_rows",
    "predictions_evaluated",
    "predictions_dropped_empty_box",
    "predictions_clipped",
    "images_with_no_predictions",
    "tp",
    "fp",
    "neutral",
)


def group_name(valid_count: int) -> str:
    if valid_count == 0:
        return "zero_valid"
    return "one_valid" if valid_count == 1 else "multi_valid"


def score_groups(
    truth: GroundTruth,
    predictions: dict[str, list[list[int | float]]],
    image_sizes: dict[str, tuple[int, int]],
    reference_metrics: dict[str, int | float],
) -> dict[str, dict[str, Any]]:
    """Evaluate disjoint image groups and reconcile additive counts to E1."""
    if set(truth) != set(predictions) or set(truth) != set(image_sizes):
        raise ValueError("GT, predictions and image sizes have different paths")
    grouped: dict[str, list[str]] = {name: [] for name in GROUPS}
    for path, entry in truth.items():
        grouped[group_name(len(entry["valid"]))].append(path)

    output: dict[str, dict[str, Any]] = {}
    for name, paths in grouped.items():
        subset_truth = {path: truth[path] for path in paths}
        subset_predictions = {path: predictions[path] for path in paths}
        subset_sizes = {path: image_sizes[path] for path in paths}
        metrics = evaluate(subset_truth, subset_predictions, subset_sizes)
        histogram: Counter[str] = Counter()
        for entry in subset_truth.values():
            histogram.update(size_bucket(box) for box in entry["valid"])
        output[name] = {
            "images": len(paths),
            "valid_gt": sum(len(entry["valid"]) for entry in subset_truth.values()),
            "ignored_gt": sum(len(entry["ignored"]) for entry in subset_truth.values()),
            "gt_size_distribution": dict(sorted(histogram.items())),
            "metrics": metrics,
        }
        if name == "zero_valid":
            # AP and recall have no denominator in this group.
            metrics["ap_iou_gt_0_5_project"] = None
            metrics["max_recall"] = None

    for key in ADDITIVE_METRICS:
        actual = sum(int(output[name]["metrics"][key]) for name in GROUPS)
        if actual != reference_metrics[key]:
            raise ValueError(f"Grouped {key} does not reconcile: {actual} != {reference_metrics[key]}")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--e1-summary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source_hashes = {"images": sha256(args.images), "annotations": sha256(args.annotations)}
    if source_hashes != {
        "images": EXPECTED_IMAGES_SHA256,
        "annotations": EXPECTED_ANNOTATIONS_SHA256,
    }:
        raise ValueError("WIDER sources differ from the T-011 data gate")
    with checked_zip(args.annotations) as archive:
        truth, counts = parse_annotations(archive.read(ANNOTATION_NAME).decode("utf-8"))
    if counts["images"] != EXPECTED_IMAGE_COUNT or counts["box_rows"] != EXPECTED_BOX_ROWS:
        raise ValueError("WIDER annotation counts differ from the T-011 data gate")
    with checked_zip(args.images) as archive:
        image_sizes, outside = read_image_sizes(archive, truth)
    if outside:
        raise ValueError("GT outside images; group scoring needs review")

    payload: Any = json.loads(args.predictions.read_text(encoding="utf-8"))
    reference: Any = json.loads(args.e1_summary.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("protocol_version") != PROTOCOL_VERSION:
        raise ValueError("Prediction protocol differs from E1")
    if payload.get("source_sha256") != source_hashes or not isinstance(payload.get("predictions"), dict):
        raise ValueError("Prediction sources or map differ from E1")
    candidate = payload.get("candidate")
    if not isinstance(candidate, dict) or candidate.get("name") not in CONFIGURATION_ID:
        raise ValueError("Unknown candidate")
    name = candidate["name"]
    if candidate.get("configuration_id") != CONFIGURATION_ID[name] or candidate.get(
        "weight_sha256"
    ) != MODEL_SHA256[name]:
        raise ValueError("Candidate weight/config differs from pinned E1")
    if not isinstance(reference, dict) or reference.get("candidate") != candidate:
        raise ValueError("Reference E1 candidate differs from predictions")
    if reference.get("source_sha256") != source_hashes or not isinstance(
        reference.get("metrics"), dict
    ):
        raise ValueError("Reference E1 summary differs from sources")
    ref_metrics = reference["metrics"]
    if not math.isfinite(ref_metrics.get("ap_iou_gt_0_5_project", float("nan"))):
        raise ValueError("Reference E1 AP is not finite")

    groups = score_groups(truth, payload["predictions"], image_sizes, ref_metrics)
    result = {
        "scope": "T-012 post-E1 WIDER one-vs-multi-valid-GT image analysis; not target selection",
        "analysis_revision": "T-012-S4-C1-v1; image groups defined before new group-score run",
        "source_sha256": source_hashes,
        "candidate": candidate,
        "annotation_counts": counts,
        "reference_e1_metrics": ref_metrics,
        "groups": groups,
        "group_definition": {
            "zero_valid": "0 valid GT; AP and recall undefined",
            "one_valid": "exactly 1 valid GT",
            "multi_valid": "at least 2 valid GT",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "candidate": name,
        "reference_ap": ref_metrics["ap_iou_gt_0_5_project"],
        "groups": groups,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
