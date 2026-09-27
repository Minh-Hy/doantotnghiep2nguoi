"""Audit whether XQLFW pairs permit a custom identity-disjoint E2 split.

Only aggregate counts are printed. No identity, image path, score, or embedding is
stored in the output. This does not replace the author's official pair protocol.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

EXPECTED_PAIRS_SHA256 = "636852f90b886f3f56c73b13c9775f7ffcd37662dbb189c694f6a0a605b63b84"
ASSIGNMENT_SALT = "T-011-XQLFW-identity-disjoint-v1"


def group_for(identity: str) -> int:
    digest = hashlib.sha256((ASSIGNMENT_SALT + "\0" + identity).encode("utf-8")).digest()
    return digest[0] & 1


def parse_pairs(path: Path) -> list[tuple[str, str, bool, int]]:
    if hashlib.sha256(path.read_bytes()).hexdigest() != EXPECTED_PAIRS_SHA256:
        raise ValueError("XQLFW pairs file hash differs from T-011")
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) != 6001 or lines[0].split() != ["10", "300"]:
        raise ValueError("Unexpected XQLFW pair protocol")
    pairs = []
    for index, line in enumerate(lines[1:]):
        fields = line.split()
        if len(fields) == 3:
            pairs.append((fields[0], fields[0], True, index // 600))
        elif len(fields) == 4:
            pairs.append((fields[0], fields[2], False, index // 600))
        else:
            raise ValueError("Unexpected pair row")
    for fold in range(10):
        block = pairs[fold * 600 : (fold + 1) * 600]
        if len(block) != 600 or sum(same for _, _, same, _ in block) != 300:
            raise ValueError("Original pair fold class counts changed")
    return pairs


def audit(pairs: list[tuple[str, str, bool, int]]) -> dict[str, object]:
    identities = {identity for left, right, _, _ in pairs for identity in (left, right)}
    membership = {identity: group_for(identity) for identity in identities}
    grouped = {0: Counter(), 1: Counter()}
    grouped_identities = {0: set(), 1: set()}
    excluded = Counter()
    original_overlap = []
    for left, right, same, _ in pairs:
        left_group = membership[left]
        right_group = membership[right]
        label = "genuine" if same else "impostor"
        if left_group == right_group:
            grouped[left_group][label] += 1
            grouped_identities[left_group].update((left, right))
        else:
            excluded[label] += 1
    for fold in range(10):
        test_people = {
            identity
            for left, right, _, row_fold in pairs if row_fold == fold
            for identity in (left, right)
        }
        dev_people = {
            identity
            for left, right, _, row_fold in pairs if row_fold != fold
            for identity in (left, right)
        }
        original_overlap.append(len(test_people & dev_people))
    for group in (0, 1):
        if not grouped[group]["genuine"] or not grouped[group]["impostor"]:
            raise ValueError("Identity group lacks a pair class")
    if grouped_identities[0] & grouped_identities[1]:
        raise AssertionError("Identity groups overlap")
    return {
        "scope": "custom pair-list feasibility audit, before face detection or scoring",
        "pairs_sha256": EXPECTED_PAIRS_SHA256,
        "assignment": "SHA-256 of fixed salt and identity; first-byte parity; no score used",
        "identity_count": len(identities),
        "original_pair_fold_identity_overlap": original_overlap,
        "groups": [
            {
                "group": group,
                "identities": sum(value == group for value in membership.values()),
                "genuine_pairs": grouped[group]["genuine"],
                "impostor_pairs": grouped[group]["impostor"],
                "pair_total": sum(grouped[group].values()),
            }
            for group in (0, 1)
        ],
        "excluded_cross_group_impostor_pairs": excluded["impostor"],
        "excluded_cross_group_genuine_pairs": excluded["genuine"],
        "retained_pair_total": sum(sum(count.values()) for count in grouped.values()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(parse_pairs(args.pairs)), indent=2))


if __name__ == "__main__":
    main()
