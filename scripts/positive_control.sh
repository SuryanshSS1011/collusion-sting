#!/usr/bin/env bash
# Positive control (upstream harness, unmodified): three LLM sellers of the target model with the
# public seller chat on, no planted seller. Shows whether this model coordinates prices in this
# market at all. Run from the repo root. Add --boss_pressure if the plain version stays competitive,
# and report whichever you used.
#
#   scripts/positive_control.sh openai/gpt-4.1-mini            # 3 seeds, ~270 calls
#   scripts/positive_control.sh google/gemini-2.5-flash --boss_pressure
set -euo pipefail
MODEL="${1:?usage: scripts/positive_control.sh <openrouter model id> [extra simulation flags]}"
shift || true
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SLUG="${MODEL//\//__}"
cd "$ROOT/third_party/collusion_hackathon/llm-agent-collusion"
uv run --project "$ROOT" python -m src.continuous_double_auction.simulation \
  --seller_models "$MODEL" --buyer_models openai/gpt-4.1-mini \
  --seller_comms_enabled --seeds 0 1 2 --tag "posctrl-$SLUG" \
  --log_dir "$ROOT/results/positive_control" -y "$@"
