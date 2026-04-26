#!/usr/bin/env bash
# ================================================
#  🪨 post-send-values.sh — send BTC script
#  Supports aliases, named arguments, and random mode
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
  echo -e "  $0 --amount <val> [--sim <n>] [--sleep <sec>] [--from <name|addr>] [--dest <name|addr>]"
  echo -e "  $0 --random [--sim <n>] [--sleep <sec>]"
  echo ""
  echo -e "${BOLD}Options:${RESET}"
  echo -e "  --amount : Value to send (required if not --random)"
  echo -e "  --random : Auto-select sender, receiver, and realistic amount"
  echo -e "  --sim    : Number of transactions (default: 1)"
  echo -e "  --sleep  : Seconds between transactions (default: 0)"
  echo -e "  --from   : Sender alias or address (default: Eve)"
  echo -e "  --dest   : Receiver alias or address (default: random)"
  echo ""
  echo -e "${CYAN}Example:${RESET}"
  echo -e "  $0 --random --sim 10 --sleep 1"
  exit 1
}

# Defaults
AMOUNT=""
SIM=1
SLEEP_TIME=0
FROM_VAL="Eve"
DEST_VAL=""
RANDOM_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --amount) AMOUNT="$2"; shift 2 ;;
    --sim)    SIM="$2"; shift 2 ;;
    --sleep)  SLEEP_TIME="$2"; shift 2 ;;
    --from)   FROM_VAL="$2"; shift 2 ;;
    --dest)   DEST_VAL="$2"; shift 2 ;;
    --random) RANDOM_MODE=true; shift ;;
    *) usage ;;
  esac
done

[[ -z "$AMOUNT" && "$RANDOM_MODE" == "false" ]] && usage

# Resolve address helper
resolve_address() {
  local val="$1"
  local type="$2"
  local addr=$(jq -r ".\"$val\".address // \"null\"" "$NODES_FILE")
  if [[ "$addr" != "null" ]]; then
    echo "$addr"
    return 0
  fi
  local exists=$(jq -r ".[] | select(.address == \"$val\") | .address" "$NODES_FILE" | head -n 1)
  [[ -n "$exists" ]] && { echo "$val"; return 0; }
  die "Invalid $type: '$val' is not in $NODES_FILE"
}

# Checks
command -v jq >/dev/null 2>&1 || die "jq required."
command -v curl >/dev/null 2>&1 || die "curl required."
[[ ! -f "$NODES_FILE" ]] && die "$NODES_FILE not found."

# Resolve static sender if not in random mode
SENDER_ADDR=""
if [[ "$RANDOM_MODE" == "false" ]]; then
  SENDER_ADDR=$(resolve_address "$FROM_VAL" "Sender")
fi

# API Check
if ! curl -s --max-time 2 "$API_URL/api/blocks" >/dev/null; then
  die "API not responding at $API_URL"
fi

MODO_STR="MANUAL"
[[ "$RANDOM_MODE" == "true" ]] && MODO_STR="RANDOM"
step "Starting session: $MODO_STR MODE ($SIM transactions)"

for (( i=1; i<=SIM; i++ )); do
  echo "────────────────────────────────────────────"
  step "Transaction $i of $SIM"

  # 1. Determine Sender
  if [[ "$RANDOM_MODE" == "true" ]]; then
    NODES_LIST=$(jq -c "to_entries" "$NODES_FILE")
    COUNT=$(echo "$NODES_LIST" | jq '. | length')
    IDX=$(( RANDOM % COUNT ))
    CUR_FROM_NAME=$(echo "$NODES_LIST" | jq -r ".[$IDX].key")
    CUR_FROM_ADDR=$(echo "$NODES_LIST" | jq -r ".[$IDX].value.address")
  else
    CUR_FROM_NAME="$FROM_VAL"
    CUR_FROM_ADDR="$SENDER_ADDR"
  fi

  # 2. Determine Receiver
  if [[ -z "$DEST_VAL" || "$RANDOM_MODE" == "true" ]]; then
    RECIPIENTS_JSON=$(jq -c "to_entries | map(select(.value.address != \"$CUR_FROM_ADDR\"))" "$NODES_FILE")
    COUNT=$(echo "$RECIPIENTS_JSON" | jq '. | length')
    [[ "$COUNT" -eq 0 ]] && die "No other recipients found."
    IDX=$(( RANDOM % COUNT ))
    CUR_DEST_NAME=$(echo "$RECIPIENTS_JSON" | jq -r ".[$IDX].key")
    CUR_DEST_ADDR=$(echo "$RECIPIENTS_JSON" | jq -r ".[$IDX].value.address")
  else
    CUR_DEST_NAME="$DEST_VAL"
    CUR_DEST_ADDR=$(resolve_address "$DEST_VAL" "Receiver")
  fi

  # 3. Determine Amount & Balance
  BALANCES=$(curl -s "$API_URL/api/balances")
  CUR_BAL=$(echo "$BALANCES" | jq -r ".\"$CUR_FROM_ADDR\" // 100.0")
  
  CUR_AMOUNT="$AMOUNT"
  if [[ -z "$CUR_AMOUNT" ]]; then
    # Realistic: 0.1 to 5% of balance
    CUR_AMOUNT=$(python3 -c "import random; b=float($CUR_BAL); print(round(random.uniform(0.1, max(0.2, b * 0.05)), 4))")
  fi

  # 4. Fee & Cost
  FEE=$(python3 -c "import json; d={'sender':'$CUR_FROM_ADDR','receiver':'$CUR_DEST_ADDR','amount':$CUR_AMOUNT}; print(max(0.15 + 0.01 * len(json.dumps(d)), 0.1))")
  TOTAL_COST=$(python3 -c "print(round($CUR_AMOUNT + $FEE, 4))")
  
  step "From: $CUR_FROM_NAME"
  step "Target: $CUR_DEST_NAME"
  step "Balance: $CUR_BAL BTC"
  step "Cost: $CUR_AMOUNT + $FEE (fee) = $TOTAL_COST BTC"

  # 5. Validation
  IS_OK=$(python3 -c "print(1 if float($TOTAL_COST) <= float($CUR_BAL) else 0)")
  if [[ "$IS_OK" -eq 0 ]]; then
    warn "Insufficient balance! Skipping."
    continue
  fi

  # 6. Post
  PAYLOAD=$(jq -n \
    --arg s "$CUR_FROM_ADDR" \
    --arg r "$CUR_DEST_ADDR" \
    --arg n "$CUR_AMOUNT" \
    --arg sig "$SIGNATURE" \
    '{sender: $s, receiver: $r, amount: ($n|tonumber), signature: $sig}')

  RESPONSE=$(curl -s -X POST "$API_URL/api/add-transaction" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

  if echo "$RESPONSE" | grep -q "sucesso"; then
    TXID=$(echo "$RESPONSE" | jq -r '.transaction.tx_hash // "N/A"')
    ok "Success: $CUR_FROM_NAME -> $CUR_DEST_NAME"
    [[ "$TXID" != "N/A" ]] && step "TXID: $TXID"
  else
    warn "Failed: $RESPONSE"
  fi

  # Sleep
  if [[ $i -lt $SIM ]]; then
    # Use python to check if sleep > 0 and perform it
    python3 -c "import time; t=$SLEEP_TIME; t > 0 and time.sleep(t)"
    [[ $(python3 -c "print(1 if $SLEEP_TIME > 0 else 0)") -eq 1 ]] && step "Slept ${SLEEP_TIME}s"
  fi
done

echo ""
ok "Done."
