"""Compare YuNet/SCRFD detection-to-MBF interface on pinned XQLFW pairs."""

from __future__ import annotations

import argparse
import json
import os
import platform
from collections import Counter
from pathlib import Path

PROTOCOL_ID = "T-012-X-012-F-v1"


def valid_pair_indices(pairs: list[tuple[str, str, bool, int]], available: set[str]) -> list[int]:
    return [index for index, (left, right, _, _) in enumerate(pairs) if left in available and right in available]


def unit(feature):
    import numpy as np

    vector = np.asarray(feature, dtype=np.float64).ravel()
    norm = np.linalg.norm(vector)
    if vector.size != 512 or not np.isfinite(vector).all() or norm == 0:
        raise ValueError("Invalid 512-D embedding")
    return vector / norm


def yunet_landmarks(face_row):
    import numpy as np

    row = np.asarray(face_row, dtype=np.float32).ravel()
    if row.size != 15 or not np.isfinite(row).all():
        raise ValueError("YuNet output must be 15 finite values")
    points = row[4:14].reshape(5, 2)
    if np.linalg.norm(points[0] - points[1]) <= 0:
        raise ValueError("YuNet eyes coincide")
    return points


def pair_results(pairs, indices, features, evaluator):
    import numpy as np

    if not indices:
        raise ValueError("No valid XQLFW pairs")
    scores, labels, folds = [], [], []
    for index in indices:
        left, right, same, fold = pairs[index]
        scores.append(float(np.dot(features[left], features[right])))
        labels.append(same)
        folds.append(fold)
    labels = np.asarray(labels, dtype=bool)
    return {
        "valid_pairs": len(indices),
        "genuine": int(labels.sum()),
        "impostor": int((~labels).sum()),
        "outside_subset_genuine": 3000 - int(labels.sum()),
        "outside_subset_impostor": 3000 - int((~labels).sum()),
        "evaluation": evaluator(np.asarray(scores), labels, np.asarray(folds, dtype=int)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--pairs", type=Path, required=True)
    parser.add_argument("--sc-model", type=Path, required=True)
    parser.add_argument("--yunet", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    import cv2
    import numpy as np
    import onnxruntime as ort
    from insightface import __version__ as insightface_version
    from insightface.app import FaceAnalysis
    from insightface.utils import face_align
    from t011_widerface_predict import MODEL_SHA256
    from t011_xqlfw_baseline import EXPECTED, checked_zip, digest, load_pairs, prepare_pack
    from t011_xqlfw_r50_comparison import evaluate

    hashes = {"images": digest(args.images), "pairs": digest(args.pairs), "sc_model": digest(args.sc_model), "yunet": digest(args.yunet)}
    if hashes != {"images": EXPECTED["images"], "pairs": EXPECTED["pairs"], "sc_model": EXPECTED["model"], "yunet": MODEL_SHA256["yunet"]}:
        raise ValueError("Input source/weight hash differs from E1/E2")
    with checked_zip(args.sc_model) as model_zip:
        root, model_hashes = prepare_pack(model_zip, args.cache)
    app = FaceAnalysis(name="buffalo_sc", root=str(root), allowed_modules=["detection", "recognition"], providers=["CPUExecutionProvider"])
    app.prepare(ctx_id=-1, det_size=(640, 640), det_thresh=0.5)
    mbf = app.models["recognition"]
    if tuple(mbf.input_size) != (112, 112):
        raise ValueError("Unexpected MBF input size")
    yunet = cv2.FaceDetectorYN.create(model=str(args.yunet), config="", input_size=(320, 320), score_threshold=0.5, nms_threshold=0.3, top_k=5000)

    with checked_zip(args.images) as archive:
        lookup = {}
        for name in archive.namelist():
            if not name.lower().endswith(".jpg"):
                continue
            parts = name.split("/")
            key = (parts[-2], parts[-1])
            if key in lookup:
                raise ValueError("Duplicate image key")
            lookup[key] = name
        pairs = load_pairs(args.pairs, lookup)
        requested = sorted({name for left, right, _, _ in pairs for name in (left, right)})
        if len(pairs) != 6000 or len(requested) != 7263:
            raise ValueError("XQLFW pair/image manifest differs from E2")
        features = {"scrfd": {}, "yunet": {}}
        outcomes = {"scrfd": Counter(), "yunet": Counter()}
        for position, name in enumerate(requested, 1):
            image = cv2.imdecode(np.frombuffer(archive.read(name), dtype=np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                outcomes["scrfd"]["decode_error"] += 1
                outcomes["yunet"]["decode_error"] += 1
                continue

            faces = app.get(image)
            if len(faces) == 1:
                features["scrfd"][name] = unit(faces[0].embedding)
                outcomes["scrfd"]["one_face"] += 1
            else:
                outcomes["scrfd"]["zero_faces" if len(faces) == 0 else "multiple_faces"] += 1

            height, width = image.shape[:2]
            yunet.setInputSize((width, height))
            _, detections = yunet.detect(image)
            count = 0 if detections is None else len(detections)
            if count == 1:
                try:
                    landmarks = yunet_landmarks(detections[0])
                    aligned = face_align.norm_crop(image, landmark=landmarks, image_size=112)
                    features["yunet"][name] = unit(mbf.get_feat(aligned))
                except (ValueError, AssertionError):
                    outcomes["yunet"]["invalid_landmarks_or_embedding"] += 1
                else:
                    outcomes["yunet"]["one_face"] += 1
            else:
                outcomes["yunet"]["zero_faces" if count == 0 else "multiple_faces"] += 1
            if position % 500 == 0:
                print(f"processed {position}/{len(requested)} images", flush=True)

    if dict(outcomes["scrfd"]) != {"one_face": 6064, "zero_faces": 291, "multiple_faces": 908}:
        raise ValueError(f"SCRFD image coverage differs from E2: {dict(outcomes['scrfd'])}")
    if any(sum(counter.values()) != len(requested) for counter in outcomes.values()):
        raise AssertionError("Image outcomes do not reconcile")

    indices = {candidate: valid_pair_indices(pairs, set(candidate_features)) for candidate, candidate_features in features.items()}
    common = sorted(set(indices["scrfd"]) & set(indices["yunet"]))
    if len(indices["scrfd"]) != 4215 or len(common) > min(len(indices["scrfd"]), len(indices["yunet"])):
        raise ValueError("Pair coverage does not reconcile with E2 or intersection")
    own = {candidate: pair_results(pairs, indices[candidate], features[candidate], evaluate) for candidate in features}
    both = {candidate: pair_results(pairs, common, features[candidate], evaluate) for candidate in features}
    scrfd_aggregate = own["scrfd"]["evaluation"]["aggregate"]
    if scrfd_aggregate["false_accept"] != 133 or scrfd_aggregate["false_reject"] != 125:
        raise ValueError("SCRFD+MBF pair-fold result differs from E2")
    for group in (own, both):
        for result in group.values():
            if result["valid_pairs"] + result["outside_subset_genuine"] + result["outside_subset_impostor"] != 6000:
                raise AssertionError("Pair outcomes do not reconcile")

    summary = {
        "protocol_id": PROTOCOL_ID,
        "commit": os.environ.get("GITHUB_SHA", "local-unpinned"),
        "scope": "XQLFW pair-fold detector/landmark-to-MBF interface; strict one-face rule, not target selection or exam check-in",
        "source_sha256": hashes,
        "model_onnx_sha256": model_hashes,
        "configuration": {"scrfd": "buffalo_sc FaceAnalysis det_size=640x640 det_thresh=0.5", "yunet": "2026may dynamic original image score=0.5 nms=0.3 top_k=5000; OpenCV 5 landmark order", "encoder": "same buffalo_sc MBF, norm_crop 112x112, L2 cosine"},
        "environment": {"platform": platform.platform(), "logical_cpus": os.cpu_count(), "python": platform.python_version(), "opencv": cv2.__version__, "numpy": np.__version__, "onnxruntime": ort.__version__, "insightface": insightface_version, "provider": "CPUExecutionProvider"},
        "images_referenced": len(requested),
        "pair_count": len(pairs),
        "image_outcomes": {candidate: dict(counter) for candidate, counter in outcomes.items()},
        "own_valid": own,
        "common_valid": both,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"image_outcomes": summary["image_outcomes"], "own_valid": {candidate: {key: value for key, value in result.items() if key != "evaluation"} | {"aggregate": result["evaluation"]["aggregate"]} for candidate, result in own.items()}, "common_valid": {candidate: {key: value for key, value in result.items() if key != "evaluation"} | {"aggregate": result["evaluation"]["aggregate"]} for candidate, result in both.items()}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
