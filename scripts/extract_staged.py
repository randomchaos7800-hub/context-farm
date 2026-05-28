#!/usr/bin/env python3
"""Staged LLM extraction pass for Context Farm.

This is the first *real* extraction baseline. Unlike the manual-overlap baseline,
it never looks at the manual object set or the gold expected_* labels. It reads
each source span cold and predicts a typed object directly from the text.

Stages (per EXTRACTION_DESIGN_V0.md):
  1. source classification   -> from declared source metadata (passed through)
  2. candidate span          -> the gold set is pre-segmented; one span per item
  3. object typing           -> LLM classifies into the 7 types or Reject
  4. canonicalization        -> LLM emits a short title + canonical statement
  5. review routing          -> application-side priority, NOT the model

Run:
  python3 scripts/extract_staged.py \
    --output examples/service-dispatch-extraction-predictions.llm-staged.json
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

VALID_TYPES = {"Fact", "Procedure", "Constraint", "Exception", "Decision", "Entity", "Reject"}

# Stage 5: application-side review routing. The model does not get a vote here.
# Defaults follow STRUCTURED_OBJECT_SCHEMA_V0.md / EXTRACTION_DESIGN_V0.md.
PRIORITY_BY_TYPE = {
    "Constraint": "high",
    "Exception": "high",
    "Decision": "high",
    "Procedure": "medium",
    "Fact": "low",
    "Entity": "low",
    "Reject": "low",
}

SYSTEM_PROMPT = (
    "You are an operational-knowledge extractor for a service business. "
    "You read one short span of source text and classify it into exactly one type, "
    "then write a concise label and a faithful restatement. "
    "You must answer only with a single JSON object and nothing else."
)

# The type definitions and signals come verbatim from EXTRACTION_DESIGN_V0.md so the
# prompt is grounded in the same contract the rest of the system is designed around.
TYPE_GUIDE = """Types:
- Constraint: a rule, threshold, minimum/maximum, requirement, required approval, or prohibition that governs action. Signals: must, cannot, requires approval, minimum/maximum, always/never.
- Exception: a rule that narrows, overrides, or bypasses another rule under defined conditions. Signals: unless, except, emergency override, special case, may bypass, may skip, may waive.
- Procedure: a multi-step operational flow or action sequence. Signals: step order, if X then Y, handoff between roles, intake/verify/check/notify/record/closeout style language.
- Decision: a chosen policy, threshold, or operational path with continuing effect. Signals: decided, approved going forward, effective immediately, limited to.
- Fact: a durable operational truth that does not fit better elsewhere. Signals: recurring schedule, known account rule, role ownership, durable classification or definition.
- Entity: a durable named object other knowledge refers to (an account, client class, role, queue, list, roster, job type).
- Reject: the span is chit-chat, narration, or carries no durable operational knowledge."""

DISAMBIGUATION = """Disambiguation rules (apply before choosing a type):
- Decide the type from the PRIMARY action of the span, not from isolated keywords.
- Constraint vs Exception: if the span's main statement is a requirement, threshold, or prohibition, it is a Constraint even when it contains "unless"/"except" as a secondary carve-out. Classify as Exception ONLY when the span's primary purpose is to waive, skip, bypass, or override another rule under stated conditions.
- Procedure vs Constraint: if the span tells an operator what steps to perform or check (verify, classify, confirm, notify, record, check, availability check), it is a Procedure even if it uses "requires" or "should".
- The mere appearance of the word "exception" in a span does not make it an Exception."""

INSTRUCTIONS = """Classify the SPAN into exactly one type from the list.
If it is a real operational rule/flow/fact, also produce:
- "title": a short noun-phrase label, at most 6 words, no trailing punctuation
- "canonical_statement": a faithful one-sentence restatement of the operational content of the span

If the type is "Reject", set "title" and "canonical_statement" to empty strings.

Respond with ONLY this JSON object:
{"type": "<one type>", "title": "<short label or empty>", "canonical_statement": "<restatement or empty>"}"""


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def call_model(base_url: str, model: str, span: str, source_type: str, authority_class: str, timeout: float) -> str:
    user_prompt = (
        f"{TYPE_GUIDE}\n\n"
        f"{DISAMBIGUATION}\n\n"
        f"{INSTRUCTIONS}\n\n"
        f"SOURCE TYPE: {source_type}\n"
        f"AUTHORITY CLASS: {authority_class}\n"
        f"SPAN: {span}"
    )
    body = {
        "model": model,
        "temperature": 0.0,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    }
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Bearer local"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return payload["choices"][0]["message"]["content"]


def parse_model_json(raw: str) -> dict:
    """Pull the first JSON object out of the model response, tolerating stray prose."""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object in model output: {raw[:200]!r}")
    return json.loads(match.group(0))


def predict_item(item: dict, base_url: str, model: str, timeout: float) -> dict:
    raw = call_model(
        base_url,
        model,
        item["text"],
        item.get("source_type", "unknown"),
        item.get("authority_class", "unknown"),
        timeout,
    )
    parsed = parse_model_json(raw)

    predicted_type = parsed.get("type", "").strip()
    if predicted_type not in VALID_TYPES:
        predicted_type = "Reject"  # fail safe: unknown type is not a confident extraction

    if predicted_type == "Reject":
        title = ""
        statement = ""
    else:
        title = (parsed.get("title") or "").strip()
        statement = (parsed.get("canonical_statement") or "").strip()

    return {
        "id": item["id"],
        "predicted_type": predicted_type,
        "predicted_title": title,
        "predicted_statement": statement,
        "predicted_review_priority": PRIORITY_BY_TYPE[predicted_type],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", default="examples/service-dispatch-extraction-gold.json")
    parser.add_argument(
        "--output",
        default="examples/service-dispatch-extraction-predictions.llm-staged.json",
    )
    parser.add_argument("--base-url", default="http://100.120.50.35:8010/v1", help="OpenAI-compatible base URL")
    parser.add_argument("--model", default="local")
    parser.add_argument("--pipeline-name", default="llm-staged-extractor-v0")
    parser.add_argument("--timeout", type=float, default=120.0)
    args = parser.parse_args()

    gold = load_json(Path(args.gold))

    predictions = []
    for item in gold["items"]:
        pred = predict_item(item, args.base_url, args.model, args.timeout)
        predictions.append(pred)
        print(f"{pred['id']}: {pred['predicted_type']:<10} | {pred['predicted_title']}")

    payload = {
        "dataset": gold["dataset"],
        "model_or_pipeline": args.pipeline_name,
        "notes": (
            "Staged LLM extraction directly from each source span. Consumes only the "
            "span text and declared source metadata; never the manual object set or "
            "expected_* labels. Review priority is assigned application-side by type."
        ),
        "predictions": predictions,
    }

    output_path = Path(args.output)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {len(predictions)} predictions to {output_path}")


if __name__ == "__main__":
    main()
