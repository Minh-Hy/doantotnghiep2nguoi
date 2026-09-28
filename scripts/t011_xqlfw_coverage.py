"""T-011 detector coverage diagnosis; writes aggregate counts only."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import cv2
import numpy as np
from insightface.app import FaceAnalysis

from t011_xqlfw_baseline import EXPECTED, checked_zip, digest, load_pairs, prepare_pack


def bucket(value: float, edges: tuple[float, ...]) -> str:
    for edge in edges:
        if value < edge:
            return f"<{edge:g}"
    return f">={edges[-1]:g}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--pairs", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    actual = {"images": digest(args.images), "pairs": digest(args.pairs), "model": digest(args.model)}
    if actual != EXPECTED:
        raise ValueError("Inputs differ from the original T-011 run")
    image_zip = checked_zip(args.images)
    model_zip = checked_zip(args.model)
    image_lookup = {}
    for name in image_zip.namelist():
        if name.lower().endswith(".jpg"):
            parts = name.split("/")
            key = (parts[-2], parts[-1])
            if key in image_lookup:
                raise ValueError("Duplicate image key")
            image_lookup[key] = name
    pairs = load_pairs(args.pairs, image_lookup)
    requested = sorted({name for left, right, _, _ in pairs for name in (left, right)})
    model_root, onnx_hashes = prepare_pack(model_zip, args.cache)
    app = FaceAnalysis(name="buffalo_sc", root=str(model_root), allowed_modules=["detection"], providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=-1, det_size=(640, 640), det_thresh=0.5)

    outcomes: dict[str, str] = {}
    image_counts = Counter()
    face_count_hist = Counter()
    secondary_score_hist = Counter()
    secondary_area_ratio_hist = Counter()
    dominant_area_hist = Counter()
    multi_small_secondary = 0
    for number, name in enumerate(requested, 1):
        image = cv2.imdecode(np.frombuffer(image_zip.read(name), dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            kind = "decode_error"
        else:
            faces = app.get(image)
            face_count_hist[str(min(len(faces), 5)) + ("+" if len(faces) >= 5 else "")] += 1
            if len(faces) == 0:
                kind = "zero_faces"
            elif len(faces) == 1:
                kind = "one_face"
            else:
                kind = "multiple_faces"
                # Geometry and scores are weak proxies, not ground-truth face labels.
                areas = np.array([max(0.0, f.bbox[2] - f.bbox[0]) * max(0.0, f.bbox[3] - f.bbox[1]) for f in faces])
                order = np.argsort(-areas)
                dominant = float(areas[order[0]])
                secondary = float(areas[order[1]])
                ratio = secondary / dominant if dominant > 0 else 1.0
                dominant_area_hist[bucket(dominant / (image.shape[0] * image.shape[1]), (0.05, 0.2, 0.5))] += 1
                secondary_area_ratio_hist[bucket(ratio, (0.05, 0.1, 0.25, 0.5, 0.75))] += 1
                secondary_score_hist[bucket(float(faces[order[1]].det_score), (0.6, 0.7, 0.8, 0.9))] += 1
                if ratio < 0.1:
                    multi_small_secondary += 1
        outcomes[name] = kind
        image_counts[kind] += 1
        if number % 500 == 0:
            print(f"diagnosed {number}/{len(requested)} images", flush=True)

    pair_exclusion = Counter()
    for left, right, same, _fold in pairs:
        left_kind, right_kind = outcomes[left], outcomes[right]
        if left_kind == right_kind == "one_face":
            pair_exclusion["valid_genuine" if same else "valid_impostor"] += 1
        else:
            reasons = sorted({kind for kind in (left_kind, right_kind) if kind != "one_face"})
            pair_exclusion[("genuine_" if same else "impostor_") + "+".join(reasons)] += 1
    summary = {
        "scope": "detector-only descriptive coverage diagnosis; no label-based detector error attribution",
        "source_sha256": actual,
        "onnx_sha256": onnx_hashes,
        "detector_input": [640, 640],
        "detector_threshold": 0.5,
        "image_count": len(requested),
        "image_outcomes": dict(image_counts),
        "face_count_histogram_5plus": dict(face_count_hist),
        "multiple_face_geometry": {
            "dominant_bbox_area_over_image": dict(dominant_area_hist),
            "second_bbox_area_over_dominant": dict(secondary_area_ratio_hist),
            "second_by_area_detection_score": dict(secondary_score_hist),
            "secondary_area_below_10pct_of_dominant": multi_small_secondary,
        },
        "pair_outcomes": dict(pair_exclusion),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"image_outcomes": summary["image_outcomes"], "pair_outcomes": summary["pair_outcomes"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
