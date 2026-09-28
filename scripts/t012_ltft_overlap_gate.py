"""T-012 X-012-H: compare P1 and a fixed IoU gate on LTFT annotation boxes."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from t012_ltft_box_proxy import Box, SOURCE_SHA256, WINDOW, iou, parse


PROTOCOL_COMMIT = "7085022"
GATE_IOU = 0.3
OUTCOMES = ("correct-track", "wrong-track", "unresolved")


def select(reference: Box, candidates: list[Box], gate: float) -> Box | None:
    if not candidates:
        return None
    scores = [iou(reference, candidate) for candidate in candidates]
    best = max(scores)
    if best <= 0 or best < gate or scores.count(best) != 1:
        return None
    return candidates[scores.index(best)]


def trace(frames: list[list[Box]], start: int, target: Box, gate: float) -> tuple[str, bool]:
    chosen: Box | None = target
    ever_wrong = False
    for index in range(start + 1, start + WINDOW):
        if chosen is None:
            break
        chosen = select(chosen, frames[index], gate)
        if chosen is not None and chosen.identity != target.identity:
            ever_wrong = True
    if chosen is None:
        return "unresolved", ever_wrong
    return ("correct-track" if chosen.identity == target.identity else "wrong-track"), ever_wrong


def analyze(frames: list[list[Box]]) -> dict[str, object]:
    groups: dict[str, Counter[str]] = {
        "all": Counter(),
        "target-annotated-at-end": Counter(),
        "target-not-annotated-at-end": Counter(),
        "face-count-at-start/1": Counter(),
        "face-count-at-start/2": Counter(),
        "face-count-at-start/3+": Counter(),
    }
    transitions: Counter[str] = Counter()
    for start in range(0, len(frames) - WINDOW + 1, WINDOW):
        end = start + WINDOW - 1
        for target in frames[start]:
            p1_outcome, p1_ever_wrong = trace(frames, start, target, 0.0)
            p2_outcome, p2_ever_wrong = trace(frames, start, target, GATE_IOU)
            transitions[f"{p1_outcome}->{p2_outcome}"] += 1
            end_ids = {box.identity for box in frames[end]}
            face_count = len(frames[start])
            labels = [
                "all",
                "target-annotated-at-end"
                if target.identity in end_ids
                else "target-not-annotated-at-end",
                f"face-count-at-start/{face_count if face_count < 3 else '3+'}",
            ]
            for label in labels:
                counter = groups[label]
                counter["denominator"] += 1
                counter[f"P1/{p1_outcome}"] += 1
                counter[f"P2/{p2_outcome}"] += 1
                counter["P1/ever-wrong"] += int(p1_ever_wrong)
                counter["P2/ever-wrong"] += int(p2_ever_wrong)

    for label, counter in groups.items():
        for candidate in ("P1", "P2"):
            if sum(counter[f"{candidate}/{outcome}"] for outcome in OUTCOMES) != counter["denominator"]:
                raise AssertionError(f"{label}: {candidate} outcomes do not reconcile")
        if counter["P1/ever-wrong"] < counter["P1/wrong-track"]:
            raise AssertionError(f"{label}: P1 endpoint wrong exceeds ever-wrong")
        if counter["P2/ever-wrong"] < counter["P2/wrong-track"]:
            raise AssertionError(f"{label}: P2 endpoint wrong exceeds ever-wrong")
    if sum(transitions.values()) != groups["all"]["denominator"]:
        raise AssertionError("Transition matrix does not reconcile")
    keys = ["denominator"] + [
        f"{candidate}/{outcome}"
        for candidate in ("P1", "P2")
        for outcome in (*OUTCOMES, "ever-wrong")
    ]
    return {
        "groups": {name: {key: counter[key] for key in keys} for name, counter in groups.items()},
        "transitions": {
            f"{old}->{new}": transitions[f"{old}->{new}"]
            for old in OUTCOMES
            for new in OUTCOMES
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--choke1", type=Path, required=True)
    parser.add_argument("--choke2", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    results: dict[str, object] = {}
    for name in ("choke1", "choke2"):
        frames = parse(getattr(args, name), SOURCE_SHA256[name])
        results[name] = {"frames": len(frames), **analyze(frames)}

    expected = {
        "choke1": (495, 384, 17, 94),
        "choke2": (529, 374, 21, 134),
    }
    for name, (denominator, correct, wrong, unresolved) in expected.items():
        observed = results[name]["groups"]["all"]
        actual = (
            observed["denominator"],
            observed["P1/correct-track"],
            observed["P1/wrong-track"],
            observed["P1/unresolved"],
        )
        if actual != (denominator, correct, wrong, unresolved):
            raise AssertionError(f"{name}: P1 replay {actual} differs from preregistered baseline")

    summary = {
        "scope": "Exploratory LTFT annotation-only association with oracle initial box; not check-in",
        "protocol_commit": PROTOCOL_COMMIT,
        "source_sha256": SOURCE_SHA256,
        "window_frames": WINDOW,
        "p1_rule": "unique maximum IoU > 0 with previous chosen box",
        "p2_rule": "same P1 rule, plus IoU >= 0.3",
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
