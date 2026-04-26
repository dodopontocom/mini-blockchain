#!/usr/bin/env bash
# ================================================
#  🔥 stress-test.sh — Real-time Stress Engine
#  Simulates heavy, randomized traffic
# ================================================

set -euo pipefail

PORT=5000
API_URL="http://localhost:$PORT"
NODES_FILE="nodes_data.json"
SIGNATURE="stress_sig_v3"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

step() { echo -e "${CYAN}▶${RESET} $1" >&2; }
die()  { echo -e "${RED}✗ ERROR: $1${RESET}" >&2; exit 1; }

usage() {
  echo -e "${BOLD}Usage:${RESET}"
  echo -e "  $0 --random --bg <workers> --sim <total_tx> [--sleep <sec>]"
  echo ""
  echo -e "${BOLD}Options:${RESET}"
  echo -e "  --random : Randomized sender/receiver/amount"
  echo -e "  --bg     : Parallel workers (concurrency)"
  echo -e "  --sim    : Total transactions to send"
  echo -e "  --sleep  : Sleep between bursts (default: 0)"
  exit 1
}

# Defaults
RANDOM_MODE=false
BG_LIMIT=5
SIM=100
SLEEP_TIME=0

while [[ $# -gt 0 ]]; do
  case $1 in
    --random) RANDOM_MODE=true; shift ;;
    --bg)     BG_LIMIT="$2"; shift 2 ;;
    --sim)    SIM="$2"; shift 2 ;;
    --sleep)  SLEEP_TIME="$2"; shift 2 ;;
    *) usage ;;
  esac
done

[[ "$RANDOM_MODE" == "false" ]] && step "Warning: Not in random mode. Using static fallback."

# Pre-checks
[[ ! -f "$NODES_FILE" ]] && die "$NODES_FILE not found."

# Cache nodes for performance
NODES_JSON=$(cat "$NODES_FILE")
NODE_KEYS=($(echo "$NODES_JSON" | jq -r 'keys[]'))
NODE_COUNT=${#NODE_KEYS[@]}

run_tx() {
  local id="$1"
  
  # Pick random sender/receiver
  local s_idx=$(( RANDOM % NODE_COUNT ))
  local r_idx=$(( RANDOM % NODE_COUNT ))
  while [[ $s_idx -eq $r_idx ]]; do r_idx=$(( RANDOM % NODE_COUNT )); done
  
  local s_name=${NODE_KEYS[$s_idx]}
  local r_name=${NODE_KEYS[$r_idx]}
  local s_addr=$(echo "$NODES_JSON" | jq -r ".\"$s_name\".address")
  local r_addr=$(echo "$NODES_JSON" | jq -r ".\"$r_name\".address")
  
  local amt=$(python3 -c "import random; print(round(random.uniform(0.0001, 0.01), 6))")
  
  local payload=$(jq -n --arg s "$s_addr" --arg r "$r_addr" --arg n "$amt" --arg sig "$SIGNATURE" \
    '{sender: $s, receiver: $r, amount: ($n|tonumber), signature: $sig}')

  curl -s -X POST "$API_URL/api/add-transaction" \
       -H "Content-Type: application/json" \
       -d "$payload" > /dev/null &
}

step "Launching Stress: $SIM tx | $BG_LIMIT concurrency | Random: $RANDOM_MODE"

for (( i=1; i<=SIM; i++ )); do
  run_tx "$i"
  
  if (( i % BG_LIMIT == 0 )); then
    wait
    [[ $SLEEP_TIME != "0" ]] && sleep "$SLEEP_TIME"
  fi
done

wait
echo -e "${GREEN}✓${RESET} Stress batch of $SIM transactions completed."
