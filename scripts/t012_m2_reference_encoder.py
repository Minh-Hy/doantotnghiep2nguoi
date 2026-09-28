"""Time MBF and R50 on identical XQLFW aligned crops; aggregate output only."""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import time
from pathlib import Path

SAMPLE_COUNT = 60
SCAN_LIMIT = 300
WARMUP_COUNT = 8
REPEATS = 3
PROTOCOL_ID = "T-012-M2-reference-encoder-v1"
CANDIDATES = ("mbf", "r50")


def percentile(values: list[float], fraction: float) -> float:
    if not values or not 0 <= fraction <= 1:
        raise ValueError("Invalid percentile input")
    ordered = sorted(values)
    at = (len(ordered) - 1) * fraction
    lower = math.floor(at)
    upper = math.ceil(at)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (at - lower)


def candidate_order(repeat: int) -> tuple[str, str]:
    return CANDIDATES[repeat % len(CANDIDATES) :] + CANDIDATES[: repeat % len(CANDIDATES)]


def checked_feature(feature: object) -> None:
    import numpy as np

    vector = np.asarray(feature).ravel()
    if vector.size != 512 or not np.isfinite(vector).all():
        raise ValueError("Encoder output is not a finite 512-D embedding")


def load_crops(image_zip, app) -> tuple[list[object], int, int, dict[str, int]]:
    import cv2
    import numpy as np
    from insightface.utils import face_align

    names = sorted(name for name in image_zip.namelist() if name.lower().endswith(".jpg"))
    if len(names) < SAMPLE_COUNT:
        raise ValueError("XQLFW ZIP has too few JPG entries for M2")
    crops = []
    counts = {"decode_error": 0, "zero_faces": 0, "multiple_faces": 0, "invalid_landmarks": 0}
    scanned = 0
    for name in names[:SCAN_LIMIT]:
        scanned += 1
        image = cv2.imdecode(np.frombuffer(image_zip.read(name), dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            counts["decode_error"] += 1
            continue
        faces = app.get(image)
        if len(faces) != 1:
            counts["zero_faces" if not faces else "multiple_faces"] += 1
            continue
        face = faces[0]
        kps = np.asarray(face.kps)
        if kps.shape != (5, 2) or not np.isfinite(kps).all():
            counts["invalid_landmarks"] += 1
            continue
        crop = face_align.norm_crop(image, landmark=kps, image_size=112)
        if crop.shape != (112, 112, 3):
            raise ValueError("Unexpected aligned crop shape")
        checked_feature(face.embedding)
        if not crops:
            expected = np.asarray(face.embedding).ravel()
            observed = np.asarray(app.models["recognition"].get_feat(crop)).ravel()
            checked_feature(observed)
            if not np.allclose(observed, expected, rtol=1e-5, atol=1e-4):
                raise ValueError("MBF crop output differs from E2 FaceAnalysis embedding")
        crops.append(crop)
        if len(crops) == SAMPLE_COUNT:
            break
    if len(crops) != SAMPLE_COUNT:
        raise ValueError(f"Only {len(crops)} one-face crops in first {SCAN_LIMIT} XQLFW images")
    return crops, len(names), scanned, counts


def benchmark(models: dict[str, object], crops: list[object]) -> dict[str, dict[str, float | int]]:
    if len(crops) != SAMPLE_COUNT or set(models) != set(CANDIDATES):
        raise ValueError("Benchmark requires fixed sample and both encoders")
    for candidate in CANDIDATES:
        for crop in crops[:WARMUP_COUNT]:
            checked_feature(models[candidate].get_feat(crop))
    elapsed = {candidate: [] for candidate in CANDIDATES}
    for repeat in range(REPEATS):
        for candidate in candidate_order(repeat):
            for crop in crops:
                started = time.perf_counter_ns()
                feature = models[candidate].get_feat(crop)
                elapsed[candidate].append((time.perf_counter_ns() - started) / 1_000_000)
                checked_feature(feature)
    expected_calls = SAMPLE_COUNT * REPEATS
    if any(len(values) != expected_calls for values in elapsed.values()):
        raise AssertionError("Encoder call count differs from protocol")
    return {
        candidate: {
            "calls": len(values),
            "median_ms": percentile(values, 0.5),
            "p95_ms": percentile(values, 0.95),
            "min_ms": min(values),
            "max_ms": max(values),
        }
        for candidate, values in elapsed.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", required=True, type=Path)
    parser.add_argument("--sc-model", required=True, type=Path)
    parser.add_argument("--r50-model", required=True, type=Path)
    parser.add_argument("--cache", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    import cv2
    import numpy as np
    import onnxruntime as ort
    from insightface import __version__ as insightface_version
    from insightface import model_zoo
    from insightface.app import FaceAnalysis
    from t011_xqlfw_baseline import EXPECTED, checked_zip, digest, prepare_pack
    from t011_xqlfw_r50_comparison import R50_ONNX_SHA256, R50_ZIP_SHA256, prepare_r50

    hashes = {
        "images": digest(args.images),
        "sc_model": digest(args.sc_model),
        "r50_model": digest(args.r50_model),
    }
    if hashes != {
        "images": EXPECTED["images"],
        "sc_model": EXPECTED["model"],
        "r50_model": R50_ZIP_SHA256,
    }:
        raise ValueError("Input hash differs from E2")
    with checked_zip(args.sc_model) as archive:
        root, sc_hashes = prepare_pack(archive, args.cache)
    with checked_zip(args.r50_model) as archive:
        r50_path = prepare_r50(archive, args.cache)
    mbf_path = root / "models" / "buffalo_sc" / "w600k_mbf.onnx"
    if digest(mbf_path) != sc_hashes["w600k_mbf.onnx"] or digest(r50_path) != R50_ONNX_SHA256:
        raise ValueError("Extracted ONNX hash changed")

    app = FaceAnalysis(
        name="buffalo_sc",
        root=str(root),
        allowed_modules=["detection", "recognition"],
        providers=["CPUExecutionProvider"],
    )
    app.prepare(ctx_id=-1, det_size=(640, 640), det_thresh=0.5)
    mbf = app.models["recognition"]
    r50 = model_zoo.get_model(str(r50_path), providers=["CPUExecutionProvider"])
    r50.prepare(ctx_id=-1)
    if tuple(mbf.input_size) != (112, 112) or tuple(r50.input_size) != (112, 112):
        raise ValueError("Unexpected encoder input size")
    with checked_zip(args.images) as archive:
        crops, manifest_count, scanned, rejected = load_crops(archive, app)
    measurements = benchmark({"mbf": mbf, "r50": r50}, crops)
    summary = {
        "protocol_id": PROTOCOL_ID,
        "commit": os.environ.get("GITHUB_SHA", "local-unpinned"),
        "scope": "get_feat on shared aligned XQLFW crops; excludes decode, detection, alignment and app flow",
        "source_sha256": hashes,
        "onnx_sha256": {"mbf": sc_hashes["w600k_mbf.onnx"], "r50": R50_ONNX_SHA256},
        "onnx_bytes": {"mbf": mbf_path.stat().st_size, "r50": r50_path.stat().st_size},
        "selection": {"rule": "first 60 valid one-face images in sorted ZIP JPG names, scan at most 300", "manifest_jpg": manifest_count, "scanned": scanned, "rejected": rejected},
        "warmup_crops_per_candidate": WARMUP_COUNT,
        "repeats": REPEATS,
        "candidate_order": [candidate_order(i) for i in range(REPEATS)],
        "environment": {
            "platform": platform.platform(), "processor": platform.processor(), "logical_cpus": os.cpu_count(),
            "python": platform.python_version(), "opencv": cv2.__version__, "numpy": np.__version__,
            "onnxruntime": ort.__version__, "insightface": insightface_version,
            "provider": "CPUExecutionProvider",
        },
        "candidates": measurements,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
