"""Close the 2x2 SCRFD/YuNet x MBF/R50 XQLFW component comparison."""

from __future__ import annotations

import argparse
import json
import os
import platform
from collections import Counter
from pathlib import Path

PROTOCOL_ID = "T-012-X-012-G-v1"
BRANCHES = ("scrfd_mbf", "scrfd_r50", "yunet_mbf", "yunet_r50")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--pairs", type=Path, required=True)
    parser.add_argument("--sc-model", type=Path, required=True)
    parser.add_argument("--r50-model", type=Path, required=True)
    parser.add_argument("--yunet", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    import cv2
    import numpy as np
    import onnxruntime as ort
    from insightface import __version__ as insightface_version
    from insightface import model_zoo
    from insightface.app import FaceAnalysis
    from insightface.utils import face_align
    from t011_widerface_predict import MODEL_SHA256
    from t011_xqlfw_baseline import EXPECTED, checked_zip, digest, load_pairs, prepare_pack
    from t011_xqlfw_r50_comparison import R50_ZIP_SHA256, evaluate, prepare_r50
    from t012_xqlfw_detector_encoder_interface import pair_results, unit, valid_pair_indices, yunet_landmarks

    hashes = {
        "images": digest(args.images),
        "pairs": digest(args.pairs),
        "sc_model": digest(args.sc_model),
        "r50_model": digest(args.r50_model),
        "yunet": digest(args.yunet),
    }
    expected = {
        "images": EXPECTED["images"],
        "pairs": EXPECTED["pairs"],
        "sc_model": EXPECTED["model"],
        "r50_model": R50_ZIP_SHA256,
        "yunet": MODEL_SHA256["yunet"],
    }
    if hashes != expected:
        raise ValueError("XQLFW, pairs or weights differ from E1/E2/X-012-F")

    with checked_zip(args.sc_model) as archive:
        root, sc_hashes = prepare_pack(archive, args.cache)
    with checked_zip(args.r50_model) as archive:
        r50_path = prepare_r50(archive, args.cache)
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
    yunet = cv2.FaceDetectorYN.create(
        model=str(args.yunet), config="", input_size=(320, 320),
        score_threshold=0.5, nms_threshold=0.3, top_k=5000,
    )

    features = {branch: {} for branch in BRANCHES}
    outcomes = {"scrfd": Counter(), "yunet": Counter()}
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

        for position, name in enumerate(requested, 1):
            image = cv2.imdecode(np.frombuffer(archive.read(name), dtype=np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                outcomes["scrfd"]["decode_error"] += 1
                outcomes["yunet"]["decode_error"] += 1
                continue

            faces = app.get(image)
            if len(faces) == 1:
                face = faces[0]
                features["scrfd_mbf"][name] = unit(face.embedding)
                features["scrfd_r50"][name] = unit(r50.get(image, face))
                outcomes["scrfd"]["one_face"] += 1
            else:
                outcomes["scrfd"]["zero_faces" if not faces else "multiple_faces"] += 1

            height, width = image.shape[:2]
            yunet.setInputSize((width, height))
            _, detections = yunet.detect(image)
            count = 0 if detections is None else len(detections)
            if count == 1:
                landmarks = yunet_landmarks(detections[0])
                aligned = face_align.norm_crop(image, landmark=landmarks, image_size=112)
                features["yunet_mbf"][name] = unit(mbf.get_feat(aligned))
                features["yunet_r50"][name] = unit(r50.get_feat(aligned))
                outcomes["yunet"]["one_face"] += 1
            else:
                outcomes["yunet"]["zero_faces" if count == 0 else "multiple_faces"] += 1
            if position % 500 == 0:
                print(f"processed {position}/{len(requested)} images", flush=True)

    if dict(outcomes["scrfd"]) != {"one_face": 6064, "zero_faces": 291, "multiple_faces": 908}:
        raise ValueError("SCRFD image outcomes differ from E2")
    if dict(outcomes["yunet"]) != {"one_face": 5943, "zero_faces": 2, "multiple_faces": 1318}:
        raise ValueError("YuNet image outcomes differ from X-012-F")
    if any(sum(counter.values()) != len(requested) for counter in outcomes.values()):
        raise AssertionError("Image outcomes do not reconcile")

    indices = {branch: valid_pair_indices(pairs, set(branch_features)) for branch, branch_features in features.items()}
    if indices["scrfd_mbf"] != indices["scrfd_r50"] or indices["yunet_mbf"] != indices["yunet_r50"]:
        raise AssertionError("Encoder changed detector coverage")
    common = sorted(set.intersection(*(set(values) for values in indices.values())))
    if len(indices["scrfd_mbf"]) != 4215 or len(indices["yunet_mbf"]) != 4055 or len(common) != 3666:
        raise ValueError("Pair coverage differs from E2/X-012-F")
    own = {branch: pair_results(pairs, indices[branch], features[branch], evaluate) for branch in BRANCHES}
    both = {branch: pair_results(pairs, common, features[branch], evaluate) for branch in BRANCHES}
    gates = {
        "scrfd_mbf": (133, 125),
        "scrfd_r50": (76, 74),
        "yunet_mbf": (183, 176),
    }
    for branch, (expected_fa, expected_fr) in gates.items():
        aggregate = own[branch]["evaluation"]["aggregate"]
        if (aggregate["false_accept"], aggregate["false_reject"]) != (expected_fa, expected_fr):
            raise ValueError(f"{branch} does not reproduce E2/X-012-F")
    for group in (own, both):
        for result in group.values():
            if result["valid_pairs"] + result["outside_subset_genuine"] + result["outside_subset_impostor"] != 6000:
                raise AssertionError("Pair outcomes do not reconcile")

    summary = {
        "protocol_id": PROTOCOL_ID,
        "commit": os.environ.get("GITHUB_SHA", "local-unpinned"),
        "scope": "XQLFW pair-fold 2x2 component comparison, not S4 target selection or exam check-in",
        "source_sha256": hashes,
        "onnx_sha256": {**sc_hashes, "w600k_r50.onnx": digest(r50_path)},
        "configuration": {
            "scrfd": "buffalo_sc FaceAnalysis det_size=640x640 det_thresh=0.5",
            "yunet": "2026may dynamic original image score=0.5 nms=0.3 top_k=5000",
            "encoders": "buffalo_sc MBF and buffalo_l R50, norm_crop 112x112, L2 cosine",
            "r50_input_mean_std": [float(r50.input_mean), float(r50.input_std)],
        },
        "environment": {
            "platform": platform.platform(), "logical_cpus": os.cpu_count(),
            "python": platform.python_version(), "opencv": cv2.__version__,
            "numpy": np.__version__, "onnxruntime": ort.__version__,
            "insightface": insightface_version, "provider": "CPUExecutionProvider",
        },
        "images_referenced": len(requested),
        "pair_count": len(pairs),
        "image_outcomes": {candidate: dict(counter) for candidate, counter in outcomes.items()},
        "own_valid": own,
        "common_valid": both,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    brief = {
        group_name: {
            branch: {key: value for key, value in result.items() if key != "evaluation"}
            | {"aggregate": result["evaluation"]["aggregate"]}
            for branch, result in group.items()
        }
        for group_name, group in (("own_valid", own), ("common_valid", both))
    }
    print(json.dumps({"image_outcomes": summary["image_outcomes"], **brief}, ensure_ascii=False))


if __name__ == "__main__":
    main()
