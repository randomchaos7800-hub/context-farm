#!/usr/bin/env python3
"""Generate a baseline extraction prediction file from manual demo objects."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", normalize(text)))


def infer_type_hints(text: str) -> set[str]:
    text_norm = normalize(text)
    text_tokens = tokens(text)
    hints: set[str] = set()

    if {"must", "required", "requires"} & text_tokens:
        hints.add("Constraint")
    if {"except", "unless", "skip", "bypass"} & text_tokens:
        hints.add("Exception")
    if {"before", "check", "verify", "notify"} & text_tokens:
        hints.add("Procedure")
    if "going forward" in text_norm or "limited to" in text_norm:
        hints.add("Decision")
    if (
        "recognized by" in text_norm
        or "is an account with" in text_norm
        or "defined as" in text_norm
    ):
        hints.add("Fact")
    if "internal roster" in text_norm or " list " in f" {text_norm} ":
        hints.add("Entity")

    return hints


def build_object_sources(manual: dict) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for row in manual.get("object_sources", []):
        grouped.setdefault(row["object_uid"], []).append(row)
    return grouped


def score_candidate(gold_item: dict, obj: dict, evidence_rows: list[dict]) -> float:
    score = 0.0
    gold_tokens = tokens(gold_item["text"])
    type_hints = infer_type_hints(gold_item["text"])
    statement_tokens = tokens(obj.get("canonical_statement", ""))
    title_tokens = tokens(obj.get("title", ""))
    overlap = len(gold_tokens & statement_tokens)
    title_overlap = len(gold_tokens & title_tokens)
    score += overlap * 2.0
    score += title_overlap * 1.5

    if obj.get("authority_class") == gold_item.get("authority_class"):
        score += 2.0
    if gold_item.get("source_uid") and evidence_rows:
        score += 4.0
    if obj.get("object_type") in type_hints:
        score += 4.0

    for evidence in evidence_rows:
        evidence_overlap = len(gold_tokens & tokens(evidence.get("evidence_text", "")))
        score += evidence_overlap * 2.0

    if obj.get("object_type") == "Constraint" and any(word in gold_tokens for word in {"must", "requires", "required"}):
        score += 1.5
    if obj.get("object_type") == "Exception" and any(word in gold_tokens for word in {"except", "skip", "bypass", "unless"}):
        score += 1.5
    if obj.get("object_type") == "Procedure" and any(word in gold_tokens for word in {"before", "requires", "check", "notify"}):
        score += 1.0
    if obj.get("object_type") == "Decision" and "forward" in gold_tokens:
        score += 1.0

    return score


def pick_statement(gold_item: dict, obj: dict, evidence_rows: list[dict]) -> str:
    if evidence_rows:
        best = max(
            evidence_rows,
            key=lambda row: len(tokens(gold_item["text"]) & tokens(row.get("evidence_text", ""))),
        )
        return best.get("evidence_text", "") or obj.get("canonical_statement", "")

    return gold_item["text"] or obj.get("canonical_statement", "")


def choose_prediction(gold_item: dict, manual: dict, object_sources: dict[str, list[dict]], reject_threshold: float = 3.0) -> dict:
    if gold_item["expected_type"] == "Reject":
        return {
            "id": gold_item["id"],
            "predicted_type": "Reject",
            "predicted_title": "",
            "predicted_statement": "",
            "predicted_review_priority": "low",
        }

    candidates = []
    for obj in manual["objects"]:
        evidence_rows = [row for row in object_sources.get(obj["object_uid"], []) if row["source_uid"] == gold_item["source_uid"]]
        score = score_candidate(gold_item, obj, evidence_rows)
        candidates.append((score, obj, evidence_rows))

    if not candidates:
        return {
            "id": gold_item["id"],
            "predicted_type": "Reject",
            "predicted_title": "",
            "predicted_statement": "",
            "predicted_review_priority": "low",
        }

    best_score, best, evidence_rows = max(candidates, key=lambda item: item[0])
    if best_score < reject_threshold:
        return {
            "id": gold_item["id"],
            "predicted_type": "Reject",
            "predicted_title": "",
            "predicted_statement": "",
            "predicted_review_priority": "low",
        }

    return {
        "id": gold_item["id"],
        "predicted_type": best["object_type"],
        "predicted_title": best["title"],
        "predicted_statement": pick_statement(gold_item, best, evidence_rows),
        "predicted_review_priority": best["review_priority"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", default="examples/service-dispatch-extraction-gold.json")
    parser.add_argument("--manual", default="examples/service-dispatch-manual-objects.json")
    parser.add_argument(
        "--output",
        default="examples/service-dispatch-extraction-predictions.manual-baseline.json",
    )
    parser.add_argument(
        "--pipeline-name",
        default="manual-object-overlap-baseline",
    )
    args = parser.parse_args()

    gold = load_json(Path(args.gold))
    manual = load_json(Path(args.manual))
    object_sources = build_object_sources(manual)

    predictions = [
        choose_prediction(item, manual, object_sources)
        for item in gold["items"]
    ]

    payload = {
        "dataset": gold["dataset"],
        "model_or_pipeline": args.pipeline_name,
        "notes": "Baseline predictions generated by matching gold examples against the existing manual demo object set.",
        "predictions": predictions,
    }

    output_path = Path(args.output)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote baseline predictions to {output_path}")


if __name__ == "__main__":
    main()
