#!/usr/bin/env bash
# ================================================
#  🪨 find-out.sh — blockchain search tool
#  Find transactions by name, amount, or TXID
# ================================================

set -euo pipefail

PORT=5000
API_URL="http://localhost:$PORT"
NODES_FILE="nodes_data.json"

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
  echo -e "  $0 [options]"
  echo ""
  echo -e "${BOLD}Options:${RESET}"
  echo -e "  --name <val>     : Search by name/alias or address (sender OR receiver)"
  echo -e "  --sender <val>   : Search by sender name or address"
  echo -e "  --receiver <val> : Search by receiver name or address"
  echo -e "  --min <amount>   : Minimum BTC amount"
  echo -e "  --max <amount>   : Maximum BTC amount"
  echo -e "  --txid <hash>    : Search for specific transaction hash"
  echo -e "  --pending        : Search only in pending transactions"
  echo -e "  --balance        : Show wallet balances (can be filtered by --name, --min, --max)"
  echo ""
  echo -e "${CYAN}Example:${RESET}"
  echo -e "  $0 --name Alice --min 10"
  echo -e "  $0 --balance --min 50"
  echo -e "  $0 --txid 5e88489..."
  exit 1
}

# Defaults
NAME_FILTER=""
SENDER_FILTER=""
RECEIVER_FILTER=""
MIN_AMT=0
MAX_AMT=999999999
TXID_FILTER=""
SEARCH_PENDING=false
SHOW_BALANCE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --name)     NAME_FILTER="$2"; shift 2 ;;
    --sender)   SENDER_FILTER="$2"; shift 2 ;;
    --receiver) RECEIVER_FILTER="$2"; shift 2 ;;
    --min)      MIN_AMT="$2"; shift 2 ;;
    --max)      MAX_AMT="$2"; shift 2 ;;
    --txid)     TXID_FILTER="$2"; shift 2 ;;
    --pending)  SEARCH_PENDING=true; shift ;;
    --balance)  SHOW_BALANCE=true; shift ;;
    *) usage ;;
  esac
done

# Resolve address helper
resolve() {
  [[ -z "$1" ]] && echo "" && return
  local addr=$(jq -r ".\"$1\".address // \"null\"" "$NODES_FILE")
  [[ "$addr" != "null" ]] && echo "$addr" || echo "$1"
}

# Check dependencies
command -v jq >/dev/null 2>&1 || die "jq required."
[[ ! -f "$NODES_FILE" ]] && die "$NODES_FILE not found."

# Resolve filters
R_NAME=$(resolve "$NAME_FILTER")
R_SENDER=$(resolve "$SENDER_FILTER")
R_RECEIVER=$(resolve "$RECEIVER_FILTER")

# Build reverse lookup for names
REVERSE_LOOKUP=$(jq -r 'to_entries | map("\(.value.address) \(.key)") | .[]' "$NODES_FILE")

get_name() {
  local addr="$1"
  local name=$(echo "$REVERSE_LOOKUP" | grep "^$addr" | cut -d' ' -f2- || echo "")
  [[ -n "$name" ]] && echo "$name" || echo "${addr:0:8}..."
}

# Check for --balance mode
if [[ "$SHOW_BALANCE" == "true" ]]; then
  step "Fetching wallet balances..."
  BAL_DATA=$(curl -s "$API_URL/api/balances")
  
  step "Filtering balances..."
  # Convert object to array of {address, balance}, filter
  RESULTS=$(echo "$BAL_DATA" | jq -c "
    to_entries | map({address: .key, balance: .value}) | .[] |
    select(
      (.balance >= ($MIN_AMT|tonumber)) and
      (.balance <= ($MAX_AMT|tonumber)) and
      (if \"$R_NAME\" != \"\" then .address == \"$R_NAME\" else true end)
    )
  ")

  COUNT=$(echo "$RESULTS" | grep -c . || echo 0)
  if [[ "$COUNT" -eq 0 ]]; then
    warn "No balances found matching criteria."
    exit 0
  fi

  echo "────────────────────────────────────────────"
  printf "${BOLD}%-25s | %s${RESET}\n" "Nome/Endereço" "Saldo (BTC)"
  echo "────────────────────────────────────────────"
  while read -r entry; do
    ADDR=$(echo "$entry" | jq -r '.address')
    BAL=$(echo "$entry" | jq -r '.balance')
    NAME=$(get_name "$ADDR")
    
    LC_NUMERIC=C printf "${CYAN}%-25s${RESET} | ${GREEN}%14.4f BTC${RESET}\n" "$NAME" "$BAL"
  done <<< "$RESULTS"
  echo "────────────────────────────────────────────"
  ok "Total: $COUNT wallet(s) listed."
  exit 0
fi

# Fetch data
if [[ "$SEARCH_PENDING" == "true" ]]; then
  step "Fetching pending transactions..."
  RAW_DATA=$(curl -s "$API_URL/api/pending-transactions")
else
  step "Fetching confirmed blocks..."
  # Flatten all transactions from all blocks
  RAW_DATA=$(curl -s "$API_URL/api/blocks" | jq '[.[].transactions[]]')
fi

# Apply Filters with JQ
step "Filtering results..."
RESULTS=$(echo "$RAW_DATA" | jq -c "
  .[] | select(
    (.amount >= ($MIN_AMT|tonumber)) and 
    (.amount <= ($MAX_AMT|tonumber)) and
    (if \"$TXID_FILTER\" != \"\" then .tx_hash | contains(\"$TXID_FILTER\") else true end) and
    (if \"$R_SENDER\" != \"\" then .sender == \"$R_SENDER\" else true end) and
    (if \"$R_RECEIVER\" != \"\" then .receiver == \"$R_RECEIVER\" else true end) and
    (if \"$R_NAME\" != \"\" then (.sender == \"$R_NAME\" or .receiver == \"$R_NAME\" or .payout.address == \"$R_NAME\") else true end)
  )")

# Display Results
COUNT=$(echo "$RESULTS" | grep -c . || echo 0)
if [[ "$COUNT" -eq 0 ]]; then
  warn "No transactions found matching criteria."
  exit 0
fi

echo "────────────────────────────────────────────"
while read -r tx; do
  TXID=$(echo "$tx" | jq -r '.tx_hash // "N/A"')
  S_ADDR=$(echo "$tx" | jq -r '.sender')
  R_ADDR=$(echo "$tx" | jq -r '.receiver')
  AMT=$(echo "$tx" | jq -r '.amount')
  FEE=$(echo "$tx" | jq -r '.fee // 0')
  
  S_NAME=$(get_name "$S_ADDR")
  R_NAME=$(get_name "$R_ADDR")
  
  # Check for Payout (Smart Contract rewards)
  PAYOUT_STR=""
  PAYOUT_AMT=$(echo "$tx" | jq -r '.payout.amount // 0')
  if (( $(echo "$PAYOUT_AMT > 0" | bc -l) )); then
    P_ADDR=$(echo "$tx" | jq -r '.payout.address')
    P_NAME=$(get_name "$P_ADDR")
    PAYOUT_STR=" $(echo -e "${YELLOW}[PAYOUT]${RESET} -> ${BOLD}$P_NAME${RESET} ${GREEN}+$PAYOUT_AMT BTC${RESET}")"
  fi

  LC_NUMERIC=C printf "${CYAN}[TX]${RESET} %-16s | ${BOLD}%-10s${RESET} -> ${BOLD}%-10s${RESET} | ${GREEN}%10.4f BTC${RESET} (fee: %.4f)%s\n" \
    "${TXID:0:16}" "$S_NAME" "$R_NAME" "$AMT" "$FEE" "$PAYOUT_STR"
done <<< "$RESULTS"
echo "────────────────────────────────────────────"
ok "Total: $COUNT transaction(s) found."
