"""Produce WIDER FACE E1 detector predictions for the preregistered project evaluator.

Raw per-image boxes are written only to a caller-chosen local JSON path. Keep that
file outside Git (for example artifacts/). This script does not choose a model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import statistics
import time
import zipfile
from pathlib import Path
from typing import Any

MODEL_SHA256 = {
    "yunet": "ebafce4e3c118d6554634be5c27ab333b4c047a9a8c3faf1d7cf93101c22f0f0",
    "blazeface": "3698b18f063835bc609069ef052228fbe86d9c9a6dc8dcb7c7c2d69aed2b181b",
    "scrfd": "5e4447f50245bbd7966bd6c0fa52938c61474a04ec7def48753668a9d8b4ea3a",
}
IMAGE_SHA256 = "f9efbd09f28c5d2d884be8c0eaef3967158c866a593fc36ab0413e4b2a58a17a"
ANNOTATION_SHA256 = "c7561e4f5e7a118c249e0a5c5c902b0de90bbf120d7da9fa28d99041f68a8a5c"
PROTOCOL_VERSION = "T-010-E1-2026-09-27"
CONFIGURATION_ID = {
    "yunet": "T-010-E1-v1-yunet-dynamic-0.01-0.3-top5000",
    "blazeface": "T-010-E1-v1-blazeface-full-0.01-0.3",
    "scrfd": "T-010-E1-v1-scrfd500-640-0.01-0.4",
}
ANNOTATION_NAME = "wider_face_split/wider_face_val_bbx_gt.txt"
IMAGE_PREFIX = "WIDER_val/images/"
EXPECTED_IMAGE_COUNT = 3226


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def xywh_to_xyxy(x: float, y: float, width: float, height: float, score: float) -> list[float]:
    values = [float(x), float(y), float(x + width), float(y + height), float(score)]
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Nonfinite detector output")
    return values


def xyxy_score(row: Any) -> list[float]:
    if len(row) < 5:
        raise ValueError("Detector output has fewer than five fields")
    values = [float(row[index]) for index in range(5)]
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Nonfinite detector output")
    return values


class YuNetAdapter:
    def __init__(self, model_path: Path):
        import cv2

        self.cv2 = cv2
        self.detector = cv2.FaceDetectorYN.create(
            model=str(model_path),
            config="",
            input_size=(320, 320),
            score_threshold=0.01,
            nms_threshold=0.3,
            top_k=5000,
        )
        self.configuration = {
            "input": "BGR original image; dynamic width and height",
            "score_threshold": 0.01,
            "nms_threshold": 0.3,
            "top_k": 5000,
            "runtime": f"OpenCV {cv2.__version__} CPU",
        }

    def detect(self, bgr: Any) -> list[list[float]]:
        height, width = bgr.shape[:2]
        self.detector.setInputSize((width, height))
        _, faces = self.detector.detect(bgr)
        if faces is None:
            return []
        if len(faces.shape) != 2 or faces.shape[1] < 15:
            raise ValueError("Unexpected YuNet face matrix")
        return [
            xywh_to_xyxy(row[0], row[1], row[2], row[3], row[-1])
            for row in faces
        ]

    def close(self) -> None:
        return None


class BlazeFaceAdapter:
    def __init__(self, model_path: Path):
        import mediapipe as mp

        self.mp = mp
        options = mp.tasks.vision.FaceDetectorOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            min_detection_confidence=0.01,
            min_suppression_threshold=0.3,
        )
        self.detector = mp.tasks.vision.FaceDetector.create_from_options(options)
        self.configuration = {
            "input": "BGR to RGB; original image supplied as MediaPipe SRGB",
            "min_detection_confidence": 0.01,
            "min_suppression_threshold": 0.3,
            "runtime": f"MediaPipe {mp.__version__} Tasks IMAGE CPU",
        }

    def detect(self, bgr: Any) -> list[list[float]]:
        import cv2
        import numpy as np

        rgb = np.ascontiguousarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        mp_image = self.mp.Image(image_format=self.mp.ImageFormat.SRGB, data=rgb)
        result = self.detector.detect(mp_image)
        rows = []
        for detection in result.detections:
            if not detection.categories:
                raise ValueError("BlazeFace detection lacks a score category")
            box = detection.bounding_box
            rows.append(
                xywh_to_xyxy(
                    box.origin_x, box.origin_y, box.width, box.height,
                    detection.categories[0].score,
                )
            )
        return rows

    def close(self) -> None:
        self.detector.close()


class SCRFDAdapter:
    def __init__(self, model_path: Path):
        import insightface
        import onnxruntime as ort
        from insightface.model_zoo import get_model

        self.detector = get_model(str(model_path), providers=["CPUExecutionProvider"])
        if self.detector is None:
            raise ValueError("InsightFace could not identify the SCRFD model")
        self.detector.prepare(
            ctx_id=-1, input_size=(640, 640), det_thresh=0.01, nms_thresh=0.4
        )
        self.configuration = {
            "input": "BGR original image; InsightFace SCRFD internal 640x640 resizing",
            "det_thresh": 0.01,
            "nms_thresh": 0.4,
            "max_num": 0,
            "runtime": f"InsightFace {insightface.__version__}; ONNX Runtime {ort.__version__} CPU",
        }

    def detect(self, bgr: Any) -> list[list[float]]:
        boxes, _ = self.detector.detect(bgr, max_num=0)
        return [xyxy_score(row) for row in boxes]

    def close(self) -> None:
        return None


def adapter_for(candidate: str, model_path: Path) -> YuNetAdapter | BlazeFaceAdapter | SCRFDAdapter:
    if candidate == "yunet":
        return YuNetAdapter(model_path)
    if candidate == "blazeface":
        return BlazeFaceAdapter(model_path)
    if candidate == "scrfd":
        return SCRFDAdapter(model_path)
    raise ValueError("Unknown candidate")


def main() -> None:
    from t011_widerface_evaluate import checked_zip, parse_annotations

    import cv2
    import numpy as np

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", choices=sorted(MODEL_SHA256), required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--preflight-only", action="store_true",
        help="Check adapter/API and coordinates on first 8 sorted images; no prediction file",
    )
    args = parser.parse_args()
    if not args.preflight_only and args.output is None:
        parser.error("--output is required for a full prediction run")

    hashes = {
        "model": sha256(args.model),
        "images": sha256(args.images),
        "annotations": sha256(args.annotations),
    }
    if hashes != {
        "model": MODEL_SHA256[args.candidate],
        "images": IMAGE_SHA256,
        "annotations": ANNOTATION_SHA256,
    }:
        raise ValueError("Input or model hash differs from pinned T-009/T-011 artifact")

    with checked_zip(args.annotations) as annotation_zip:
        truth, counts = parse_annotations(
            annotation_zip.read(ANNOTATION_NAME).decode("utf-8")
        )
    if counts["images"] != EXPECTED_IMAGE_COUNT:
        raise ValueError("Annotation manifest count differs from WIDER data gate")
    image_paths = sorted(truth)
    source_hashes = {"images": hashes["images"], "annotations": hashes["annotations"]}
    predictions: dict[str, list[list[float]]] = {}
    durations_ms = []
    adapter = adapter_for(args.candidate, args.model)
    try:
        with checked_zip(args.images) as image_zip:
            image_names = [name for name in image_zip.namelist() if name.lower().endswith(".jpg")]
            if len(image_names) != len(set(image_names)) or set(image_names) != {
                IMAGE_PREFIX + relative for relative in image_paths
            }:
                raise ValueError("Image ZIP paths differ from annotation manifest")
            selected = image_paths[:8] if args.preflight_only else image_paths
            for number, relative in enumerate(selected, 1):
                bgr = cv2.imdecode(
                    np.frombuffer(image_zip.read(IMAGE_PREFIX + relative), dtype=np.uint8),
                    cv2.IMREAD_COLOR,
                )
                if bgr is None:
                    raise ValueError("Cannot decode validation image")
                tick = time.perf_counter()
                boxes = adapter.detect(bgr)
                durations_ms.append((time.perf_counter() - tick) * 1000)
                if not isinstance(boxes, list):
                    raise ValueError("Adapter must return a list")
                for row in boxes:
                    if len(row) != 5 or not all(math.isfinite(value) for value in row):
                        raise ValueError("Invalid normalized detector row")
                predictions[relative] = boxes
                if number % 200 == 0:
                    print(f"{args.candidate}: {number}/{len(selected)} images", flush=True)
    finally:
        adapter.close()

    latency = {
        "scope": "after image decode; includes adapter preprocessing, inference and postprocessing",
        "images": len(durations_ms),
        "median_ms": statistics.median(durations_ms),
        "p95_ms": float(np.percentile(durations_ms, 95)),
        "uncontrolled_reference_run": True,
    }
    candidate_info = {
        "name": args.candidate,
        "weight_sha256": hashes["model"],
        "configuration_id": CONFIGURATION_ID[args.candidate],
        "configuration": adapter.configuration,
    }
    if args.preflight_only:
        print(json.dumps({
            "scope": "API/coordinate preflight only; no AP or model selection",
            "candidate": candidate_info,
            "images_checked": len(predictions),
            "prediction_rows": sum(len(rows) for rows in predictions.values()),
            "latency_observation": latency,
        }, ensure_ascii=False))
        return

    payload = {
        "protocol_version": PROTOCOL_VERSION,
        "source_sha256": source_hashes,
        "candidate": candidate_info,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "logical_cpus": os.cpu_count(),
            "opencv": cv2.__version__,
            "numpy": np.__version__,
        },
        "latency_observation": latency,
        "predictions": predictions,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "candidate": args.candidate,
        "images": len(predictions),
        "prediction_rows": sum(len(rows) for rows in predictions.values()),
        "output": str(args.output),
        "latency_observation": latency,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
