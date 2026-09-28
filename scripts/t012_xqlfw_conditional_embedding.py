"""X-012-I: compare B0 and detection-first embedding on the same XQLFW images."""

from __future__ import annotations

import argparse
import json
import os
import platform
import time
from collections import Counter, defaultdict
from pathlib import Path


def conditional_get(image, detector, recognizer, face_type):
    """Keep A0 unresolved for zero/multiple detections before recognition."""
    boxes, landmarks = detector.detect(image, max_num=0, metric="default")
    count = boxes.shape[0]
    if count != 1:
        return count, None
    face = face_type(
        bbox=boxes[0, :4],
        kps=None if landmarks is None else landmarks[0],
        det_score=boxes[0, 4],
    )
    recognizer.get(image, face)
    return count, face


def timing(values):
    import numpy as np

    data = np.asarray(values, dtype=np.float64)
    if not len(data):
        return {"n": 0}
    return {
        "n": int(len(data)),
        "median_ms": float(np.median(data) * 1000),
        "p95_ms": float(np.percentile(data, 95) * 1000),
        "total_s": float(data.sum()),
    }


def main():
    import cv2
    import numpy as np
    import onnxruntime as ort
    from insightface import __version__ as insightface_version
    from insightface.app import FaceAnalysis
    from insightface.app.common import Face

    from t011_xqlfw_baseline import EXPECTED, checked_zip, digest, load_pairs, prepare_pack
    from t011_xqlfw_r50_comparison import evaluate, unit

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", required=True, type=Path)
    parser.add_argument("--pairs", required=True, type=Path)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    actual = {"images": digest(args.images), "pairs": digest(args.pairs), "model": digest(args.model)}
    if actual != EXPECTED:
        raise ValueError("Inputs differ from B0 E2")
    with checked_zip(args.model) as model_zip:
        root, onnx_hashes = prepare_pack(model_zip, args.cache)
    app = FaceAnalysis(
        name="buffalo_sc", root=str(root),
        allowed_modules=["detection", "recognition"],
        providers=["CPUExecutionProvider"],
    )
    app.prepare(ctx_id=-1, det_size=(640, 640), det_thresh=0.5)
    detector = app.det_model
    recognizer = app.models["recognition"]
    if tuple(recognizer.input_size) != (112, 112):
        raise ValueError("Unexpected recognizer input size")

    features = {}
    outcomes = Counter()
    durations = defaultdict(list)
    order_durations = defaultdict(list)
    baseline_recognition_calls = 0
    with checked_zip(args.images) as archive:
        lookup = {}
        for name in archive.namelist():
            if name.lower().endswith(".jpg"):
                parts = name.split("/")
                key = (parts[-2], parts[-1])
                if key in lookup:
                    raise ValueError("Duplicate image key")
                lookup[key] = name
        pairs = load_pairs(args.pairs, lookup)
        requested = sorted({name for left, right, _, _ in pairs for name in (left, right)})
        if len(requested) != 7263 or len(pairs) != 6000:
            raise ValueError("Image/pair manifest differs from B0")

        for name in requested[:3]:
            image = cv2.imdecode(np.frombuffer(archive.read(name), dtype=np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("Warm-up image did not decode")
            app.get(image)
            conditional_get(image, detector, recognizer, Face)

        for position, name in enumerate(requested):
            image = cv2.imdecode(np.frombuffer(archive.read(name), dtype=np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("Image did not decode")

            def baseline():
                start = time.perf_counter()
                result = app.get(image)
                return result, time.perf_counter() - start

            def intervention():
                start = time.perf_counter()
                result = conditional_get(image, detector, recognizer, Face)
                return result, time.perf_counter() - start

            if position % 2 == 0:
                (base_faces, base_s), ((count, new_face), new_s) = baseline(), intervention()
                order = "baseline_first"
            else:
                (count, new_face), new_s = intervention()
                base_faces, base_s = baseline()
                order = "intervention_first"
            if count != len(base_faces):
                raise AssertionError("Detection count changed")
            baseline_recognition_calls += count
            group = "one_face" if count == 1 else "zero_faces" if count == 0 else "multiple_faces"
            outcomes[group] += 1
            durations[(group, "baseline")].append(base_s)
            durations[(group, "intervention")].append(new_s)
            order_durations[(order, "baseline")].append(base_s)
            order_durations[(order, "intervention")].append(new_s)
            if count == 1:
                old = base_faces[0]
                if new_face is None:
                    raise AssertionError("One detected face was discarded")
                for field in ("bbox", "kps"):
                    if not np.allclose(getattr(old, field), getattr(new_face, field), rtol=1e-6, atol=1e-6):
                        raise AssertionError(f"Detection {field} changed")
                if not np.allclose(old.embedding, new_face.embedding, rtol=1e-6, atol=1e-6):
                    raise AssertionError("Embedding changed")
                features[name] = unit(old.embedding)
            elif new_face is not None:
                raise AssertionError("Intervention embedded an unresolved image")
            if (position + 1) % 500 == 0:
                print(f"processed {position + 1}/{len(requested)} images", flush=True)

    if dict(outcomes) != {"one_face": 6064, "zero_faces": 291, "multiple_faces": 908}:
        raise ValueError("B0 coverage did not reproduce")
    scores, labels, folds = [], [], []
    excluded = Counter()
    for left, right, same, fold in pairs:
        if left not in features or right not in features:
            excluded["genuine" if same else "impostor"] += 1
            continue
        scores.append(float(np.dot(features[left], features[right])))
        labels.append(same)
        folds.append(fold)
    if len(scores) != 4215 or dict(excluded) != {"genuine": 954, "impostor": 831}:
        raise ValueError("B0 pair coverage did not reproduce")
    result = evaluate(np.asarray(scores), np.asarray(labels, dtype=bool), np.asarray(folds))
    aggregate = result["aggregate"]
    if (aggregate["false_accept"], aggregate["false_reject"]) != (133, 125):
        raise ValueError("B0 verification did not reproduce")

    by_group = {
        group: {branch: timing(durations[(group, branch)]) for branch in ("baseline", "intervention")}
        for group in ("zero_faces", "one_face", "multiple_faces")
    }
    all_times = {
        branch: timing(sum((durations[(group, branch)] for group in ("zero_faces", "one_face", "multiple_faces")), []))
        for branch in ("baseline", "intervention")
    }
    summary = {
        "protocol": "T-012-X-012-I-v1",
        "commit": os.environ.get("GITHUB_SHA", "local-unpinned"),
        "input_sha256": actual,
        "onnx_sha256": onnx_hashes,
        "environment": {
            "platform": platform.platform(), "python": platform.python_version(),
            "logical_cpus": os.cpu_count(), "opencv": cv2.__version__,
            "onnxruntime": ort.__version__, "insightface": insightface_version,
            "provider": "CPUExecutionProvider", "det_size": [640, 640], "det_thresh": 0.5,
        },
        "outcomes": dict(outcomes), "valid_pairs": len(scores),
        "excluded_pairs": dict(excluded), "verification": aggregate,
        "baseline_recognition_calls": baseline_recognition_calls,
        "intervention_recognition_calls": outcomes["one_face"],
        "inference_timing": {"all_images": all_times, "by_group": by_group},
        "order_timing": {
            order: {branch: timing(order_durations[(order, branch)]) for branch in ("baseline", "intervention")}
            for order in ("baseline_first", "intervention_first")
        },
        "scope": "exploratory paired inference timing on XQLFW JPGs, not check-in latency",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
