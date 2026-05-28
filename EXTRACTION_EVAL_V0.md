# Extraction Eval v0

Status: draft  
Date: 2026-05-28

## Purpose

This document defines the first concrete extraction evaluation loop for Context Farm.

The point is to stop talking about extraction quality abstractly and start measuring it against a small labeled domain set.

## Artifacts

- gold set: [examples/service-dispatch-extraction-gold.json](./examples/service-dispatch-extraction-gold.json)
- prediction template: [examples/service-dispatch-extraction-predictions.template.json](./examples/service-dispatch-extraction-predictions.template.json)
- evaluator: [scripts/eval_extraction.py](./scripts/eval_extraction.py)

## Scope

This first set is intentionally narrow:

- domain: `service-dispatch`
- labels: `Constraint`, `Exception`, `Procedure`, `Fact`, `Decision`, `Entity`, `Reject`
- examples: `12`

That is enough to evaluate:
- type classification
- title normalization
- review-priority assignment
- minimal statement coverage

## How To Use

1. Copy the prediction template.
2. Fill one prediction per gold item.
3. Run the evaluator.

Example:

```bash
cd /home/dino/context-farm-repo
cp examples/service-dispatch-extraction-predictions.template.json /tmp/preds.json
python3 scripts/eval_extraction.py --predictions /tmp/preds.json
```

## Metrics

The evaluator reports:

- prediction coverage
- type accuracy
- title accuracy
- statement coverage
- review-priority accuracy

This is intentionally simple. It is meant to be the first extraction scoreboard, not the final one.

## Why This Matters

Context Farm already has:
- a manual demo domain
- a structured object schema
- a SQLite store
- retrieval and briefing prototypes

What it does not yet have is a disciplined way to say whether the extraction loop is getting better.

This artifact is the first answer to that problem.

## Next Step

The next meaningful implementation step is to generate a first real prediction file from a staged extraction prompt and run it against this gold set. That will tell us whether the extraction design is only plausible on paper or starting to work in code.
