#!/usr/bin/env python3
"""Evaluate Context Farm extraction predictions against a labeled gold set."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def contains_all_needles(haystack: str, needles: list[str]) -> bool:
    hay = normalize(haystack)
    return all(normalize(needle) in hay for needle in needles)


def score_item(gold: dict, pred: dict | None) -> dict:
    if pred is None:
        return {
            "id": gold["id"],
            "present": False,
            "type_match": False,
            "priority_match": False,
            "statement_match": False,
            "title_match": False,
        }

    predicted_statement = pred.get("predicted_statement", "")
    return {
        "id": gold["id"],
        "present": True,
        "type_match": pred.get("predicted_type") == gold["expected_type"],
        "priority_match": pred.get("predicted_review_priority") == gold["expected_review_priority"],
        "statement_match": contains_all_needles(predicted_statement, gold.get("expected_statement_contains", [])),
        "title_match": normalize(pred.get("predicted_title", "")) == normalize(gold.get("expected_title", "")),
    }


def pct(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100.0, 1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--gold",
        default="examples/service-dispatch-extraction-gold.json",
        help="Path to labeled gold dataset JSON",
    )
    parser.add_argument(
        "--predictions",
        required=True,
        help="Path to prediction JSON file",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = parser.parse_args()

    gold = load_json(Path(args.gold))
    predictions = load_json(Path(args.predictions))

    gold_items = gold["items"]
    pred_map = {item["id"]: item for item in predictions.get("predictions", [])}
    scored = [score_item(item, pred_map.get(item["id"])) for item in gold_items]

    totals = {
        "gold_items": len(gold_items),
        "predictions_present": sum(1 for row in scored if row["present"]),
        "type_match": sum(1 for row in scored if row["type_match"]),
        "title_match": sum(1 for row in scored if row["title_match"]),
        "statement_match": sum(1 for row in scored if row["statement_match"]),
        "priority_match": sum(1 for row in scored if row["priority_match"]),
    }
    totals["coverage_pct"] = pct(totals["predictions_present"], totals["gold_items"])
    totals["type_accuracy_pct"] = pct(totals["type_match"], totals["gold_items"])
    totals["title_accuracy_pct"] = pct(totals["title_match"], totals["gold_items"])
    totals["statement_coverage_pct"] = pct(totals["statement_match"], totals["gold_items"])
    totals["priority_accuracy_pct"] = pct(totals["priority_match"], totals["gold_items"])

    missing = [row["id"] for row in scored if not row["present"]]
    mismatches = [
        row["id"]
        for row in scored
        if row["present"] and not (row["type_match"] and row["statement_match"] and row["priority_match"])
    ]

    payload = {
        "dataset": gold["dataset"],
        "model_or_pipeline": predictions.get("model_or_pipeline", ""),
        "totals": totals,
        "missing_predictions": missing,
        "mismatch_ids": mismatches,
        "scored_items": scored,
    }

    if args.json:
        print(json.dumps(payload, indent=2))
        return

    print(f"Dataset: {gold['dataset']}")
    print(f"Pipeline: {predictions.get('model_or_pipeline', '(unspecified)')}")
    print()
    print(f"Gold items:           {totals['gold_items']}")
    print(f"Predictions present:  {totals['predictions_present']} ({totals['coverage_pct']}%)")
    print(f"Type accuracy:        {totals['type_match']} / {totals['gold_items']} ({totals['type_accuracy_pct']}%)")
    print(f"Title accuracy:       {totals['title_match']} / {totals['gold_items']} ({totals['title_accuracy_pct']}%)")
    print(f"Statement coverage:   {totals['statement_match']} / {totals['gold_items']} ({totals['statement_coverage_pct']}%)")
    print(f"Priority accuracy:    {totals['priority_match']} / {totals['gold_items']} ({totals['priority_accuracy_pct']}%)")
    if missing:
        print()
        print("Missing predictions:")
        for item_id in missing:
            print(f"- {item_id}")
    if mismatches:
        print()
        print("Mismatch ids:")
        for item_id in mismatches:
            print(f"- {item_id}")


if __name__ == "__main__":
    main()
