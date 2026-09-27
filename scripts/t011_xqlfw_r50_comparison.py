"""T-011 paired MBF/R50 XQLFW run with bounded worker memory; aggregate output only."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort
import sklearn
from insightface import __version__ as insightface_version
from insightface import model_zoo
from insightface.app import FaceAnalysis
from sklearn.metrics import roc_auc_score, roc_curve

from t011_xqlfw_baseline import EXPECTED, checked_zip, counts, digest, load_pairs, prepare_pack, select_threshold, wilson

R50_ZIP_SHA256 = "80ffe37d8a5940d59a7384c201a2a38d4741f2f3c51eef46ebb28218a7b0ca2f"
R50_ONNX_SHA256 = "4c06341c33c2ca1f86781dab0e829f88ad5b64be9fba56e56bc9ebdefc619e43"


def unit(feature: np.ndarray) -> np.ndarray:
    vector = np.asarray(feature, dtype=np.float64).ravel()
    norm = np.linalg.norm(vector)
    if vector.size != 512 or not np.isfinite(vector).all() or norm == 0:
        raise ValueError("Unexpected embedding output")
    return vector / norm


def prepare_r50(archive, cache: Path) -> Path:
    matches = [name for name in archive.namelist() if Path(name).name == "w600k_r50.onnx"]
    if len(matches) != 1:
        raise ValueError("R50 ONNX is missing or ambiguous")
    destination = cache / "models" / "t011_r50" / "w600k_r50.onnx"
    destination.parent.mkdir(parents=True, exist_ok=True)
    content = archive.read(matches[0])
    if hashlib.sha256(content).hexdigest() != R50_ONNX_SHA256:
        raise ValueError("R50 ONNX hash mismatch")
    if not destination.exists() or digest(destination) != R50_ONNX_SHA256:
        destination.write_bytes(content)
    return destination


def extract_chunk(names: list[str], image_path: str, model_root: str, r50_path: str) -> tuple[dict, list, tuple]:
    archive = checked_zip(Path(image_path))
    app = FaceAnalysis(
        name="buffalo_sc",
        root=model_root,
        allowed_modules=["detection", "recognition"],
        providers=["CPUExecutionProvider"],
    )
    app.prepare(ctx_id=-1, det_size=(640, 640), det_thresh=0.5)
    r50 = model_zoo.get_model(r50_path, providers=["CPUExecutionProvider"])
    r50.prepare(ctx_id=-1)
    if tuple(r50.input_size) != (112, 112):
        raise ValueError("Unexpected R50 input size")
    outcomes = Counter()
    extracted = []
    for name in names:
        image = cv2.imdecode(np.frombuffer(archive.read(name), dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            outcomes["decode_error"] += 1
            continue
        faces = app.get(image)
        if len(faces) != 1:
            outcomes["zero_faces" if len(faces) == 0 else "multiple_faces"] += 1
            continue
        face = faces[0]
        mbf = unit(face.embedding)
        r50_embedding = unit(r50.get(image, face))
        extracted.append((name, mbf, r50_embedding))
        outcomes["one_face"] += 1
    archive.close()
    return dict(outcomes), extracted, (float(r50.input_mean), float(r50.input_std))


def evaluate(scores: np.ndarray, labels: np.ndarray, folds: np.ndarray) -> dict:
    results = []
    totals = {"genuine": 0, "impostor": 0, "false_reject": 0, "false_accept": 0}
    for fold in range(10):
        dev, held_out = folds != fold, folds == fold
        threshold = select_threshold(scores[dev], labels[dev])
        result = counts(scores[held_out], labels[held_out], threshold)
        if result["genuine"] == 0 or result["impostor"] == 0:
            raise ValueError("A held-out fold lost a pair class")
        for key in totals:
            totals[key] += result[key]
        results.append({"fold": fold + 1, "threshold": threshold, **result})
    fpr, tpr, _ = roc_curve(labels, scores)
    eer_index = int(np.argmin(np.abs(fpr - (1 - tpr))))
    return {
        "folds": results,
        "aggregate": {
            **totals,
            "fmr": totals["false_accept"] / totals["impostor"],
            "fnmr": totals["false_reject"] / totals["genuine"],
            "fmr_wilson95_naive": wilson(totals["false_accept"], totals["impostor"]),
            "fnmr_wilson95_naive": wilson(totals["false_reject"], totals["genuine"]),
            "roc_auc_descriptive": float(roc_auc_score(labels, scores)),
            "eer_grid_descriptive": float((fpr[eer_index] + (1 - tpr[eer_index])) / 2),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--pairs", type=Path, required=True)
    parser.add_argument("--sc-model", type=Path, required=True)
    parser.add_argument("--r50-model", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--chunk-size", type=int, default=100)
    parser.add_argument("--checkpoint-dir", type=Path, required=True)
    parser.add_argument("--smoke-images", type=int, default=0)
    args = parser.parse_args()
    if args.smoke_images < 0:
        raise ValueError("Smoke image count must be nonnegative")
    if args.chunk_size < 1:
        raise ValueError("Chunk size must be positive")

    actual = {
        "images": digest(args.images),
        "pairs": digest(args.pairs),
        "sc_model": digest(args.sc_model),
        "r50_model": digest(args.r50_model),
    }
    if actual != {"images": EXPECTED["images"], "pairs": EXPECTED["pairs"], "sc_model": EXPECTED["model"], "r50_model": R50_ZIP_SHA256}:
        raise ValueError("Input hash mismatch")
    image_zip = checked_zip(args.images)
    sc_zip = checked_zip(args.sc_model)
    r50_zip = checked_zip(args.r50_model)
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
    if args.smoke_images:
        requested = requested[:args.smoke_images]
    root, sc_hashes = prepare_pack(sc_zip, args.cache)
    r50_path = prepare_r50(r50_zip, args.cache)
    image_zip.close()
    sc_zip.close()
    r50_zip.close()

    features = {"mbf": {}, "r50": {}}
    image_outcomes = Counter()
    input_normalization = None
    args.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(max_workers=1, max_tasks_per_child=1) as pool:
        for start in range(0, len(requested), args.chunk_size):
            chunk = requested[start : start + args.chunk_size]
            checkpoint = args.checkpoint_dir / f"chunk-{start:05d}.npz"
            metadata = json.dumps({"source_sha256": actual, "start": start, "names": chunk}, sort_keys=True)
            if checkpoint.exists():
                with np.load(checkpoint, allow_pickle=False) as saved:
                    if str(saved["metadata"].item()) != metadata:
                        raise ValueError("Checkpoint does not match current inputs/chunk")
                    outcome = json.loads(str(saved["outcomes"].item()))
                    normalization = tuple(saved["normalization"].tolist())
                    extracted = list(zip(saved["names"].tolist(), saved["mbf"], saved["r50"]))
                source = "cached"
            else:
                outcome, extracted, normalization = pool.submit(
                    extract_chunk, chunk, str(args.images), str(root), str(r50_path)
                ).result()
                temporary = checkpoint.with_suffix(".tmp")
                with temporary.open("wb") as stream:
                    np.savez_compressed(
                        stream,
                        metadata=metadata,
                        outcomes=json.dumps(outcome),
                        normalization=np.asarray(normalization, dtype=np.float64),
                        names=np.asarray([entry[0] for entry in extracted]),
                        mbf=np.vstack([entry[1] for entry in extracted]) if extracted else np.empty((0, 512)),
                        r50=np.vstack([entry[2] for entry in extracted]) if extracted else np.empty((0, 512)),
                    )
                temporary.replace(checkpoint)
                source = "new"
            if input_normalization is None:
                input_normalization = normalization
            elif input_normalization != normalization:
                raise ValueError("R50 normalization changed between chunks")
            image_outcomes.update(outcome)
            for name, mbf, r50 in extracted:
                features["mbf"][name] = mbf
                features["r50"][name] = r50
            print(f"processed {min(start + len(chunk), len(requested))}/{len(requested)} images ({source})", flush=True)
    if args.smoke_images:
        if image_outcomes["one_face"] == 0:
            raise ValueError("Smoke sample did not produce an embedding")
        print(json.dumps({"smoke_images": len(requested), "image_outcomes": dict(image_outcomes)}))
        return
    if dict(image_outcomes) != {"one_face": 6064, "zero_faces": 291, "multiple_faces": 908}:
        raise ValueError("Image coverage changed from the original run")

    scores = {"mbf": [], "r50": []}
    labels, folds = [], []
    for left, right, same, fold in pairs:
        if left not in features["mbf"] or right not in features["mbf"]:
            continue
        for model in scores:
            scores[model].append(float(np.dot(features[model][left], features[model][right])))
        labels.append(same)
        folds.append(fold)
    labels = np.asarray(labels, dtype=bool)
    folds = np.asarray(folds, dtype=int)
    if len(labels) != 4215:
        raise ValueError("Pair coverage changed from the original run")
    results = {model: evaluate(np.asarray(values), labels, folds) for model, values in scores.items()}
    summary = {
        "scope": "exploratory XQLFW pair-fold comparison on identical usable pairs; not exam-room or identity-disjoint",
        "source_sha256": actual,
        "onnx_sha256": {**sc_hashes, "w600k_r50.onnx": R50_ONNX_SHA256},
        "preprocessing": "same SCRFD-500MF faces/landmarks, InsightFace norm_crop 112x112 per encoder, L2, cosine",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "logical_cpus": os.cpu_count(),
            "opencv": cv2.__version__,
            "onnxruntime": ort.__version__,
            "insightface": insightface_version,
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "provider": "CPUExecutionProvider",
            "detector_input": [640, 640],
            "detector_threshold": 0.5,
            "chunk_size": args.chunk_size,
        },
        "r50_input_mean_std": input_normalization,
        "image_outcomes": dict(image_outcomes),
        "valid_pairs": len(labels),
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"valid_pairs": len(labels), "mbf": results["mbf"]["aggregate"], "r50": results["r50"]["aggregate"]}))


if __name__ == "__main__":
    main()

