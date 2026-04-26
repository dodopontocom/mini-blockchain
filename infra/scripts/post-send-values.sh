#!/usr/bin/env bash
# ================================================
#  🪨 post-send-values.sh — parallelism edition
#  Supports concurrent background workers
# ================================================

set -euo pipefail

PORT=5000
API_URL="http://localhost:$PORT"
NODES_FILE="nodes_data.json"
SIGNATURE="assinatura_mockada"

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
RESET='\033[0m'

step() { echo -e "${CYAN}▶${RESET} $1" >&2; }
ok()   { echo -e "${GREEN}✓${RESET} $1" >&2; }
warn() { echo -e "${YELLOW}⚠${RESET}  $1" >&2; }
die()  { echo -e "${RED}✗ ERROR: $1${RESET}" >&2; exit 1; }

usage() {
  echo -e "${BOLD}Usage:${RESET}"
  echo -e "  $0 --amount <val> [--sim <n>] [--sleep <sec>] [--from <name|addr>] [--dest <name|addr>] [--bg <n>]"
  echo -e "  $0 --random [--sim <n>] [--sleep <sec>] [--bg <n>]"
  echo ""
  echo -e "${BOLD}Options:${RESET}"
  echo -e "  --amount : Value to send"
  echo -e "  --random : Auto-select everything"
  echo -e "  --bg     : Parallel workers (default: 1)"
  echo -e "  --sim    : Total transactions (default: 1)"
  echo -e "  --sleep  : Seconds between bursts (default: 0)"
  echo ""
  echo -e "${CYAN}Example:${RESET}"
  echo -e "  $0 --bg 3 --sim 9 --sleep 2  # 3 bursts of 3 transactions"
  exit 1
}

# Defaults
AMOUNT=""
SIM=1
SLEEP_TIME=0
FROM_VAL="Eve"
DEST_VAL=""
RANDOM_MODE=false
BG_LIMIT=1

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --amount) AMOUNT="$2"; shift 2 ;;
    --sim)    SIM="$2"; shift 2 ;;
    --sleep)  SLEEP_TIME="$2"; shift 2 ;;
    --from)   FROM_VAL="$2"; shift 2 ;;
    --dest)   DEST_VAL="$2"; shift 2 ;;
    --random) RANDOM_MODE=true; shift ;;
    --bg)     BG_LIMIT="$2"; shift 2 ;;
    *) usage ;;
  esac
done

# Auto-random if --bg is used without amount
[[ -z "$AMOUNT" && "$RANDOM_MODE" == "false" && "$BG_LIMIT" -gt 1 ]] && RANDOM_MODE=true
[[ -z "$AMOUNT" && "$RANDOM_MODE" == "false" ]] && usage

# Helper: Resolve address
resolve_address() {
  local val="$1"
  local addr=$(jq -r ".\"$val\".address // \"null\"" "$NODES_FILE")
  if [[ "$addr" != "null" ]]; then echo "$addr"; return 0; fi
  local exists=$(jq -r ".[] | select(.address == \"$val\") | .address" "$NODES_FILE" | head -n 1)
  [[ -n "$exists" ]] && { echo "$val"; return 0; }
  die "Invalid address: '$val'"
}

# Pre-checks
command -v jq >/dev/null 2>&1 || die "jq required."
[[ ! -f "$NODES_FILE" ]] && die "$NODES_FILE not found."
if ! curl -s --max-time 2 "$API_URL/api/blocks" >/dev/null; then die "API offline."; fi

# Static sender resolve
SENDER_ADDR=""
[[ "$RANDOM_MODE" == "false" ]] && SENDER_ADDR=$(resolve_address "$FROM_VAL")

MODO_STR="MANUAL"
[[ "$RANDOM_MODE" == "true" ]] && MODO_STR="RANDOM"
step "Starting: $MODO_STR MODE | $SIM total | $BG_LIMIT concurrent"

# ---------------------------------------------------------
# TRANSACTION WORKER FUNCTION
# ---------------------------------------------------------
run_tx() {
  local id="$1"
  local prefix="${BOLD}[Job $id]${RESET}"

  # 1. Determine participants
  local cur_from_name="$FROM_VAL"
  local cur_from_addr="$SENDER_ADDR"
  if [[ "$RANDOM_MODE" == "true" ]]; then
    local nodes_list=$(jq -c "to_entries" "$NODES_FILE")
    local count=$(echo "$nodes_list" | jq '. | length')
    local idx=$(( RANDOM % count ))
    cur_from_name=$(echo "$nodes_list" | jq -r ".[$idx].key")
    cur_from_addr=$(echo "$nodes_list" | jq -r ".[$idx].value.address")
  fi

  local cur_dest_name="$DEST_VAL"
  local cur_dest_addr=""
  if [[ -z "$DEST_VAL" || "$RANDOM_MODE" == "true" ]]; then
    local rec_json=$(jq -c "to_entries | map(select(.value.address != \"$cur_from_addr\"))" "$NODES_FILE")
    local count=$(echo "$rec_json" | jq '. | length')
    local idx=$(( RANDOM % count ))
    cur_dest_name=$(echo "$rec_json" | jq -r ".[$idx].key")
    cur_dest_addr=$(echo "$rec_json" | jq -r ".[$idx].value.address")
  else
    cur_dest_addr=$(resolve_address "$DEST_VAL")
  fi

  # 2. Balance & Amount
  local balances=$(curl -s "$API_URL/api/balances")
  local cur_bal=$(echo "$balances" | jq -r ".\"$cur_from_addr\" // 100.0")
  local cur_amt="$AMOUNT"
  [[ -z "$cur_amt" ]] && cur_amt=$(python3 -c "import random; b=float($cur_bal); print(round(random.uniform(0.1, max(0.2, b * 0.05)), 4))")

  # 3. Fee & Cost
  local fee=$(python3 -c "import json; d={'sender':'$cur_from_addr','receiver':'$cur_dest_addr','amount':$cur_amt}; print(max(0.15 + 0.01 * len(json.dumps(d)), 0.1))")
  local total=$(python3 -c "print(round($cur_amt + $fee, 4))")

  # 4. Check & Send
  if (( $(python3 -c "print(1 if float($total) <= float($cur_bal) else 0)") )); then
    local payload=$(jq -n --arg s "$cur_from_addr" --arg r "$cur_dest_addr" --arg n "$cur_amt" --arg sig "$SIGNATURE" \
      '{sender: $s, receiver: $r, amount: ($n|tonumber), signature: $sig}')
    
    local resp=$(curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$payload")
    
    if echo "$resp" | grep -q "sucesso"; then
      local txid=$(echo "$resp" | jq -r '.transaction.tx_hash // "N/A"')
      echo -e "$prefix ${GREEN}✓${RESET} $cur_from_name -> $cur_dest_name ($cur_amt BTC) | TXID: ${txid:0:16}..." >&2
    else
      echo -e "$prefix ${RED}✗${RESET} Failed: $resp" >&2
    fi
  else
    echo -e "$prefix ${YELLOW}⚠${RESET} Insufficient balance ($cur_from_name: $cur_bal)" >&2
  fi
}

# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------
for (( i=1; i<=SIM; i++ )); do
  run_tx "$i" &

  # Batch control
  if (( i % BG_LIMIT == 0 )); then
    wait
    if [[ $i -lt $SIM && $(python3 -c "print(1 if $SLEEP_TIME > 0 else 0)") -eq 1 ]]; then
      step "Burst of $BG_LIMIT finished. Resting ${SLEEP_TIME}s..."
      sleep "$SLEEP_TIME"
    fi
  fi
done

wait
echo ""
ok "Daring session complete."
