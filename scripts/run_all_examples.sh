#!/usr/bin/env bash
# Run all Python examples with py-sdk/.env loaded (same idea as ts-sdk/scripts/run_all_examples.sh).

set -uo pipefail

cd "$(dirname "$0")/.."

export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}$(pwd)"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

mapfile -t EXAMPLES < <(find examples -maxdepth 1 -name '*.py' -type f | sort)

if [[ ${#EXAMPLES[@]} -eq 0 ]]; then
  echo "No examples found in examples/ directory."
  exit 1
fi

FAILED=0
for EX in "${EXAMPLES[@]}"; do
  echo "=================================================="
  echo "Running example: $EX"
  echo "=================================================="
  if python3 "$EX"; then
    echo "--------------------------------------------------"
    echo "✅ SUCCESS: $EX"
    echo "--------------------------------------------------"
  else
    FAILED=$((FAILED + 1))
    echo "--------------------------------------------------"
    echo "❌ FAILED: $EX"
    echo "--------------------------------------------------"
  fi
  echo ""
done

if [[ "$FAILED" -gt 0 ]]; then
  echo "Summary: $FAILED example(s) failed (out of ${#EXAMPLES[@]})."
  exit 1
fi
echo "Summary: all ${#EXAMPLES[@]} example(s) succeeded."
