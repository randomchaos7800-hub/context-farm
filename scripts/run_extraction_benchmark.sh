#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${OUTPUT_DIR:-$ROOT_DIR/artifacts/extraction-benchmarks/latest}"
BASE_URL="${BASE_URL:-http://100.120.50.35:8010/v1}"
MODEL="${MODEL:-local}"
PIPELINE_NAME="${PIPELINE_NAME:-llm-staged-live}"

mkdir -p "$OUTPUT_DIR"

cd "$ROOT_DIR"

python3 scripts/generate_manual_baseline_predictions.py \
  --output "$OUTPUT_DIR/manual-baseline.predictions.json"

python3 scripts/eval_extraction.py \
  --predictions "$OUTPUT_DIR/manual-baseline.predictions.json" \
  --json > "$OUTPUT_DIR/manual-baseline.eval.json"

python3 scripts/extract_staged.py \
  --base-url "$BASE_URL" \
  --model "$MODEL" \
  --pipeline-name "$PIPELINE_NAME" \
  --output "$OUTPUT_DIR/llm-staged.predictions.json"

python3 scripts/eval_extraction.py \
  --predictions "$OUTPUT_DIR/llm-staged.predictions.json" \
  --json > "$OUTPUT_DIR/llm-staged.eval.json"

printf 'Wrote benchmark artifacts to %s\n' "$OUTPUT_DIR"
