"""Validate WIDER FACE E1 inputs and emit only aggregate annotation counts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np

from t011_xqlfw_baseline import checked_zip, digest

EXPECTED = {
    "images": "f9efbd09f28c5d2d884be8c0eaef3967158c866a593fc36ab0413e4b2a58a17a",
    "annotations": "c7561e4f5e7a118c249e0a5c5c902b0de90bbf120d7da9fa28d99041f68a8a5c",
}
ANNOTATION = "wider_face_split/wider_face_val_bbx_gt.txt"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images", type=Path, required=True)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    actual = {"images": digest(args.images), "annotations": digest(args.annotations)}
    if actual != EXPECTED:
        raise ValueError("WIDER FACE input hash mismatch")
    image_zip = checked_zip(args.images)
    annotation_zip = checked_zip(args.annotations)
    if image_zip.testzip() is not None or annotation_zip.testzip() is not None:
        raise ValueError("ZIP CRC failure")
    image_names = {name for name in image_zip.namelist() if name.lower().endswith(".jpg")}
    lines = annotation_zip.read(ANNOTATION).decode("utf-8").splitlines()
    position = 0
    seen = set()
    count = {"images": 0, "zip_jpg": len(image_names), "boxes": 0, "invalid_flag": 0, "nonpositive_bbox": 0, "decode_errors": 0, "zero_face_images": 0}
    while position < len(lines):
        relative = lines[position].strip()
        number = int(lines[position + 1])
        position += 2
        if relative in seen or number < 0:
            raise ValueError("Duplicate image or negative box count")
        seen.add(relative)
        name = "WIDER_val/images/" + relative
        if name not in image_names:
            raise ValueError("Annotation references missing JPG")
        image = cv2.imdecode(np.frombuffer(image_zip.read(name), dtype=np.uint8), cv2.IMREAD_COLOR)
        count["decode_errors"] += image is None
        count["images"] += 1
        count["zero_face_images"] += number == 0
        count["boxes"] += number
        for _ in range(number):
            fields = lines[position].split()
            position += 1
            if len(fields) != 10:
                raise ValueError("Unexpected bbox field count")
            values = list(map(int, fields))
            count["invalid_flag"] += values[7] == 1
            count["nonpositive_bbox"] += values[2] <= 0 or values[3] <= 0
    if position != len(lines) or count["images"] != len(image_names):
        raise ValueError("Unmatched annotation/image count")
    summary = {"scope": "WIDER FACE validation file/label gate, not detector benchmark", "source_sha256": actual, **count}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
