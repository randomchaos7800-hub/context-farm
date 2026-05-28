#!/usr/bin/env python3
"""Evaluate Context Farm extraction predictions against a labeled gold set.

Scoring philosophy:
- type and review_priority are categorical, so they are scored by exact match.
- title and canonical_statement are generated free text, so exact-string matching
  unfairly punishes correct-but-paraphrased extractions. They are scored by graded
  token overlap. Strict variants are still reported so nothing is hidden.

Token overlap uses light normalization (lowercase, drop punctuation, strip a single
trailing plural 's', drop a small stopword set). It does NOT stem aggressively, so
families like require/requirement/requires are treated as distinct tokens. That is a
known limitation, kept deliberately to avoid a stemmer inventing its own mismatches.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

# Thresholds are explicit so the scoreboard is transparent and easy to argue with.
TITLE_OVERLAP_PASS = 0.5       # predicted title covers >= half of the gold title's content tokens
NEEDLE_RECALL_PASS = 0.6       # a single expected phrase counts as covered at >= 60% token recall
STATEMENT_PASS = 0.6           # statement passes if >= 60% of its expected phrases are covered

STOPWORDS = {
    "the", "a", "an", "of", "to", "for", "and", "or", "in", "on", "is", "are",
    "be", "that", "this", "with", "by", "at", "as", "it", "its", "will", "can",
    "may", "if", "from", "into",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def content_tokens(text: str) -> set[str]:
    """Lowercase word tokens, plural-normalized, with stopwords removed."""
    raw = []
    for chunk in normalize(text).replace("/", " ").split():
        token = "".join(ch for ch in chunk if ch.isalnum())
        if not token:
            continue
        if token.endswith("s") and len(token) > 3:
            token = token[:-1]
        raw.append(token)
    return {t for t in raw if t not in STOPWORDS}


def contains_all_needles(haystack: str, needles: list[str]) -> bool:
    """Strict legacy check: every expected phrase appears verbatim as a substring."""
    hay = normalize(haystack)
    return all(normalize(needle) in hay for needle in needles)


def needle_recall(statement_tokens: set[str], needle: str) -> float:
    needle_tokens = content_tokens(needle)
    if not needle_tokens:
        return 1.0
    return len(statement_tokens & needle_tokens) / len(needle_tokens)


def statement_graded_score(statement: str, needles: list[str]) -> float:
    """Mean fraction of each expected phrase's content tokens present in the statement."""
    if not needles:
        return 1.0
    statement_tokens = content_tokens(statement)
    return sum(needle_recall(statement_tokens, n) for n in needles) / len(needles)


def title_overlap_score(predicted: str, expected: str) -> float:
    """Fraction of the gold title's content tokens covered by the predicted title."""
    gold_tokens = content_tokens(expected)
    if not gold_tokens:
        return 1.0 if not content_tokens(predicted) else 0.0
    return len(content_tokens(predicted) & gold_tokens) / len(gold_tokens)


def score_item(gold: dict, pred: dict | None) -> dict:
    if pred is None:
        return {
            "id": gold["id"],
            "present": False,
            "type_match": False,
            "priority_match": False,
            "title_exact": False,
            "title_overlap": 0.0,
            "title_match": False,
            "statement_strict": False,
            "statement_score": 0.0,
            "statement_match": False,
        }

    needles = gold.get("expected_statement_contains", [])
    predicted_statement = pred.get("predicted_statement", "")
    predicted_title = pred.get("predicted_title", "")
    expected_title = gold.get("expected_title", "")

    title_overlap = title_overlap_score(predicted_title, expected_title)
    statement_score = statement_graded_score(predicted_statement, needles)

    return {
        "id": gold["id"],
        "present": True,
        "type_match": pred.get("predicted_type") == gold["expected_type"],
        "priority_match": pred.get("predicted_review_priority") == gold["expected_review_priority"],
        "title_exact": normalize(predicted_title) == normalize(expected_title),
        "title_overlap": round(title_overlap, 3),
        "title_match": title_overlap >= TITLE_OVERLAP_PASS,
        "statement_strict": contains_all_needles(predicted_statement, needles),
        "statement_score": round(statement_score, 3),
        "statement_match": statement_score >= STATEMENT_PASS,
    }


def pct(numerator: float, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100.0, 1)


def mean(values: list[float]) -> float:
    return round(sum(values) / len(values), 3) if values else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--gold",
        default="examples/service-dispatch-extraction-gold.json",
        help="Path to labeled gold dataset JSON",
    )
    parser.add_argument("--predictions", required=True, help="Path to prediction JSON file")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = parser.parse_args()

    gold = load_json(Path(args.gold))
    predictions = load_json(Path(args.predictions))

    gold_items = gold["items"]
    pred_map = {item["id"]: item for item in predictions.get("predictions", [])}
    scored = [score_item(item, pred_map.get(item["id"])) for item in gold_items]
    n = len(gold_items)

    totals = {
        "gold_items": n,
        "predictions_present": sum(1 for row in scored if row["present"]),
        "type_match": sum(1 for row in scored if row["type_match"]),
        "priority_match": sum(1 for row in scored if row["priority_match"]),
        "title_exact": sum(1 for row in scored if row["title_exact"]),
        "title_graded": sum(1 for row in scored if row["title_match"]),
        "statement_strict": sum(1 for row in scored if row["statement_strict"]),
        "statement_graded": sum(1 for row in scored if row["statement_match"]),
    }
    totals["coverage_pct"] = pct(totals["predictions_present"], n)
    totals["type_accuracy_pct"] = pct(totals["type_match"], n)
    totals["priority_accuracy_pct"] = pct(totals["priority_match"], n)
    totals["title_exact_pct"] = pct(totals["title_exact"], n)
    totals["title_graded_pct"] = pct(totals["title_graded"], n)
    totals["statement_strict_pct"] = pct(totals["statement_strict"], n)
    totals["statement_graded_pct"] = pct(totals["statement_graded"], n)
    totals["title_overlap_mean"] = mean([row["title_overlap"] for row in scored if row["present"]])
    totals["statement_score_mean"] = mean([row["statement_score"] for row in scored if row["present"]])

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
    print(f"Gold items:              {n}")
    print(f"Predictions present:     {totals['predictions_present']} ({totals['coverage_pct']}%)")
    print(f"Type accuracy:           {totals['type_match']} / {n} ({totals['type_accuracy_pct']}%)")
    print(f"Priority accuracy:       {totals['priority_match']} / {n} ({totals['priority_accuracy_pct']}%)")
    print()
    print("Title (categorical labels are generated, so graded is the fair metric):")
    print(f"  exact:                 {totals['title_exact']} / {n} ({totals['title_exact_pct']}%)")
    print(f"  graded (overlap>={TITLE_OVERLAP_PASS}):  {totals['title_graded']} / {n} ({totals['title_graded_pct']}%)  mean overlap {totals['title_overlap_mean']}")
    print()
    print("Statement coverage:")
    print(f"  strict (verbatim):     {totals['statement_strict']} / {n} ({totals['statement_strict_pct']}%)")
    print(f"  graded (recall>={STATEMENT_PASS}):   {totals['statement_graded']} / {n} ({totals['statement_graded_pct']}%)  mean recall {totals['statement_score_mean']}")
    if missing:
        print()
        print("Missing predictions:")
        for item_id in missing:
            print(f"- {item_id}")
    if mismatches:
        print()
        print("Mismatch ids (type/statement/priority):")
        for item_id in mismatches:
            print(f"- {item_id}")


if __name__ == "__main__":
    main()
