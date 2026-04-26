#!/usr/bin/env bash
# ================================================
#  🪨 smart-ops.sh — smart contract tool
#  Deploy and Call contracts on the blockchain
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
  echo -e "  $0 deploy --from <name> --code 'python_code'"
  echo -e "  $0 deploy --from <name> --file <filename_in_src_contracts>"
  echo -e "  $0 call --from <name> --to <contract_addr> --params '{\"key\":\"val\"}'"
  echo -e "  $0 state"
  echo ""
  echo -e "${CYAN}Example (Deploy KV Store):${RESET}"
  echo -e "  $0 deploy --from Alice --code 'storage[msg[\"params\"][\"key\"]] = msg[\"params\"][\"val\"]; result=\"Saved\"'"
  echo -e "  $0 deploy --from Alice --file voting"
  exit 1
}

# Path to contracts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTRACTS_DIR="$SCRIPT_DIR/../../src/contracts"

# Resolve address helper
resolve() {
  local addr=$(jq -r ".\"$1\".address // \"null\"" "$NODES_FILE")
  [[ "$addr" != "null" ]] && echo "$addr" || echo "$1"
}

[[ $# -lt 1 ]] && usage

CMD="$1"; shift

case "$CMD" in
  deploy)
    FROM=""
    CODE=""
    FILE=""
    while [[ $# -gt 0 ]]; do
      case $1 in
        --from) FROM="$2"; shift 2 ;;
        --code) CODE="$2"; shift 2 ;;
        --file) FILE="$2"; shift 2 ;;
        *) usage ;;
      esac
    done
    
    if [[ -n "$FILE" ]]; then
      CODE=$(cat "$CONTRACTS_DIR/$FILE.py" 2>/dev/null || die "Arquivo $CONTRACTS_DIR/$FILE.py não encontrado.")
    fi
    
    [[ -z "$FROM" || -z "$CODE" ]] && usage
    
    SENDER_ADDR=$(resolve "$FROM")
    step "Deploying contract from $FROM..."
    
    PAYLOAD=$(jq -n \
      --arg s "$SENDER_ADDR" \
      --arg code "$CODE" \
      --arg sig "$SIGNATURE" \
      '{sender: $s, receiver: "contract_deploy", amount: 0, type: "deploy", data: $code, signature: $sig}')
    
    RESP=$(curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD")
    if echo "$RESP" | grep -q "sucesso"; then
      TXID=$(echo "$RESP" | jq -r '.transaction.tx_hash')
      ok "Deploy transaction sent! TXID: $TXID"
      warn "Contract address will be generated after mining."
    else
      die "Deploy failed: $RESP"
    fi
    ;;

  call)
    FROM=""
    TO=""
    PARAMS="{}"
    while [[ $# -gt 0 ]]; do
      case $1 in
        --from) FROM="$2"; shift 2 ;;
        --to)   TO="$2"; shift 2 ;;
        --params) PARAMS="$2"; shift 2 ;;
        *) usage ;;
      esac
    done
    [[ -z "$FROM" || -z "$TO" ]] && usage
    
    SENDER_ADDR=$(resolve "$FROM")
    step "Calling contract $TO from $FROM..."
    
    PAYLOAD=$(jq -n \
      --arg s "$SENDER_ADDR" \
      --arg r "$TO" \
      --argjson p "$PARAMS" \
      --arg sig "$SIGNATURE" \
      '{sender: $s, receiver: $r, amount: 0, type: "call", data: $p, signature: $sig}')
    
    RESP=$(curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD")
    if echo "$RESP" | grep -q "sucesso"; then
      ok "Call transaction sent! TXID: $(echo "$RESP" | jq -r '.transaction.tx_hash')"
    else
      die "Call failed: $RESP"
    fi
    ;;

  state)
    step "Current Global State:"
    curl -s "$API_URL/api/state" | jq .
    ;;

  *) usage ;;
esac
