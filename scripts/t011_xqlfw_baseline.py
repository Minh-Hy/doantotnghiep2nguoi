"""T-011 exploratory XQLFW pair-fold baseline; no biometric artifacts are written."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import time
import zipfile
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort
import sklearn
from insightface import __version__ as insightface_version
from insightface.app import FaceAnalysis
from sklearn.metrics import roc_auc_score, roc_curve

EXPECTED = {
    "images": "1af459679fba23a12f4d83c82a81523eb930a4aec759eebefcbdde69a678962c",
    "pairs": "636852f90b886f3f56c73b13c9775f7ffcd37662dbb189c694f6a0a605b63b84",
    "model": "57d31b56b6ffa911c8a73cfc1707c73cab76efe7f13b675a05223bf42de47c72",
}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def checked_zip(path: Path) -> zipfile.ZipFile:
    archive = zipfile.ZipFile(path)
    for entry in archive.namelist():
        p = Path(entry.replace("\\", "/"))
        if p.is_absolute() or ".." in p.parts:
            raise ValueError("Archive contains unsafe path")
    return archive


def pair_image(person: str, index: str, image_lookup: dict[tuple[str, str], str]) -> str:
    filename = f"{person}_{int(index):04d}.jpg"
    key = (person, filename)
    if key not in image_lookup:
        raise ValueError("A protocol pair refers to a missing image")
    return image_lookup[key]


def load_pairs(path: Path, image_lookup: dict[tuple[str, str], str]) -> list[tuple[str, str, bool, int]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if lines[0].split() != ["10", "300"] or len(lines) != 6001:
        raise ValueError("Unexpected XQLFW pair protocol")
    pairs = []
    for position, line in enumerate(lines[1:]):
        fields = line.split()
        if len(fields) == 3:
            left = pair_image(fields[0], fields[1], image_lookup)
            right = pair_image(fields[0], fields[2], image_lookup)
            same = True
        elif len(fields) == 4:
            left = pair_image(fields[0], fields[1], image_lookup)
            right = pair_image(fields[2], fields[3], image_lookup)
            same = False
        else:
            raise ValueError("Unexpected protocol row")
        pairs.append((left, right, same, position // 600))
    for fold in range(10):
        block = pairs[fold * 600 : (fold + 1) * 600]
        if len(block) != 600 or sum(x[2] for x in block) != 300:
            raise ValueError("Fold does not contain 300 genuine and 300 impostor pairs")
    return pairs


def select_threshold(scores: np.ndarray, labels: np.ndarray) -> float:
    """Choose a descriptive dev balance point; higher score means match."""
    if len(scores) == 0 or not labels.any() or labels.all():
        raise ValueError("Both pair classes are needed to select a threshold")
    order = np.argsort(-scores, kind="stable")
    sorted_scores = scores[order]
    sorted_labels = labels[order].astype(bool)
    ends = np.flatnonzero(np.r_[sorted_scores[:-1] != sorted_scores[1:], True])
    true_accepted = np.cumsum(sorted_labels)[ends]
    false_accepted = np.cumsum(~sorted_labels)[ends]
    fmr = false_accepted / np.sum(~sorted_labels)
    fnmr = (np.sum(sorted_labels) - true_accepted) / np.sum(sorted_labels)
    thresholds = sorted_scores[ends]
    best = np.lexsort((-thresholds, fmr, np.abs(fmr - fnmr)))[0]
    return float(thresholds[best])


def counts(scores: np.ndarray, labels: np.ndarray, threshold: float) -> dict[str, int]:
    accepted = scores >= threshold
    genuine = labels.astype(bool)
    return {
        "genuine": int(genuine.sum()),
        "impostor": int((~genuine).sum()),
        "false_reject": int((genuine & ~accepted).sum()),
        "false_accept": int(((~genuine) & accepted).sum()),
    }


def wilson(errors: int, total: int) -> list[float] | None:
    if total == 0:
        return None
    z = 1.959963984540054
    p = errors / total
    den = 1 + z * z / total
    center = (p + z * z / (2 * total)) / den
    half = z * np.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / den
    return [float(center - half), float(center + half)]


def prepare_pack(model_zip: zipfile.ZipFile, cache: Path) -> tuple[Path, dict[str, str]]:
    destination = cache / "models" / "buffalo_sc"
    destination.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name in ("det_500m.onnx", "w600k_mbf.onnx"):
        matches = [item for item in model_zip.namelist() if Path(item).name == name]
        if len(matches) != 1:
            raise ValueError("Missing or ambiguous model file")
        target = destination / name
        content = model_zip.read(matches[0])
        file_hash = hashlib.sha256(content).hexdigest()
        if not target.exists() or digest(target) != file_hash:
            target.write_bytes(content)
        hashes[name] = file_hash
    return cache, hashes


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
        raise ValueError("Input checksum differs from the reviewed T-009/T-010 artifacts")
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
    model_root, model_hashes = prepare_pack(model_zip, args.cache)
    app = FaceAnalysis(
        name="buffalo_sc",
        root=str(model_root),
        allowed_modules=["detection", "recognition"],
        providers=["CPUExecutionProvider"],
    )
    app.prepare(ctx_id=-1, det_size=(640, 640), det_thresh=0.5)

    features: dict[str, np.ndarray] = {}
    image_outcomes = {"one_face": 0, "zero_faces": 0, "multiple_faces": 0, "decode_error": 0}
    durations = []
    start = time.monotonic()
    for number, name in enumerate(requested, 1):
        tick = time.monotonic()
        image = cv2.imdecode(np.frombuffer(image_zip.read(name), dtype=np.uint8), cv2.IMREAD_COLOR)
        if image is None:
            image_outcomes["decode_error"] += 1
        else:
            faces = app.get(image)
            if len(faces) == 0:
                image_outcomes["zero_faces"] += 1
            elif len(faces) > 1:
                image_outcomes["multiple_faces"] += 1
            else:
                feature = np.asarray(faces[0].embedding, dtype=np.float64).ravel()
                norm = np.linalg.norm(feature)
                if feature.size != 512 or not np.isfinite(feature).all() or norm == 0:
                    raise ValueError("Unexpected embedding output")
                features[name] = feature / norm
                image_outcomes["one_face"] += 1
        durations.append(time.monotonic() - tick)
        if number % 500 == 0:
            print(f"processed {number}/{len(requested)} images; usable {image_outcomes['one_face']}", flush=True)

    scores, labels, folds = [], [], []
    excluded = {"genuine": 0, "impostor": 0}
    for left, right, same, fold in pairs:
        if left not in features or right not in features:
            excluded["genuine" if same else "impostor"] += 1
            continue
        scores.append(float(np.dot(features[left], features[right])))
        labels.append(same)
        folds.append(fold)
    scores = np.asarray(scores, dtype=np.float64)
    labels = np.asarray(labels, dtype=bool)
    folds = np.asarray(folds, dtype=int)
    if len(scores) == 0:
        raise ValueError("No usable pairs")

    fold_results = []
    totals = {"genuine": 0, "impostor": 0, "false_reject": 0, "false_accept": 0}
    for fold in range(10):
        dev, held_out = folds != fold, folds == fold
        threshold = select_threshold(scores[dev], labels[dev])
        result = counts(scores[held_out], labels[held_out], threshold)
        if result["genuine"] == 0 or result["impostor"] == 0:
            raise ValueError("A held-out fold lost an entire pair class")
        for key in totals:
            totals[key] += result[key]
        result.update(
            {
                "fold": fold + 1,
                "dev_pairs": int(dev.sum()),
                "threshold": threshold,
                "fmr": result["false_accept"] / result["impostor"],
                "fnmr": result["false_reject"] / result["genuine"],
            }
        )
        fold_results.append(result)
    fpr, tpr, _ = roc_curve(labels, scores)
    descriptive_eer_index = int(np.argmin(np.abs(fpr - (1 - tpr))))
    summary = {
        "scope": "exploratory XQLFW pair-fold; not identity-disjoint or exam-room validation",
        "source_sha256": actual,
        "onnx_sha256": model_hashes,
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
            "face_rule": "exactly one detected face; otherwise pair excluded and coverage reported",
            "embedding": "InsightFace 112x112 norm_crop, L2 normalized, cosine similarity",
        },
        "image_count": len(requested),
        "image_outcomes": image_outcomes,
        "pair_count": len(pairs),
        "valid_pairs": len(scores),
        "excluded_pairs": excluded,
        "folds": fold_results,
        "aggregate": {
            **totals,
            "fmr": totals["false_accept"] / totals["impostor"],
            "fnmr": totals["false_reject"] / totals["genuine"],
            "fmr_wilson95": wilson(totals["false_accept"], totals["impostor"]),
            "fnmr_wilson95": wilson(totals["false_reject"], totals["genuine"]),
            "roc_auc_descriptive": float(roc_auc_score(labels, scores)),
            "eer_grid_descriptive": float((fpr[descriptive_eer_index] + (1 - tpr[descriptive_eer_index])) / 2),
        },
        "latency": {
            "image_decode_detect_embed_seconds_total": time.monotonic() - start,
            "per_image_median_ms": float(np.median(durations) * 1000),
            "per_image_p95_ms": float(np.percentile(durations, 95) * 1000),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"valid_pairs": len(scores), "excluded_pairs": excluded, "fmr": summary["aggregate"]["fmr"], "fnmr": summary["aggregate"]["fnmr"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
