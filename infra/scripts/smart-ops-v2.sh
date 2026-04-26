#!/usr/bin/env bash
# ================================================
#  🪨 smart-ops-v2.sh — advanced smart contracts
#  Voting, Vault and Heritage (Dead Man's Switch)
# ================================================

set -euo pipefail

PORT=5000
API_URL="http://localhost:$PORT"
NODES_FILE="nodes_data.json"
SIGNATURE="assinatura_mockada"

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
BOLD='\033[1m'
RESET='\033[0m'

step() { echo -e "${CYAN}▶${RESET} $1" >&2; }
ok()   { echo -e "${GREEN}✓${RESET} $1" >&2; }

# Path to contracts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTRACTS_DIR="$SCRIPT_DIR/../../src/contracts"

read_contract() {
  cat "$CONTRACTS_DIR/$1.py"
}

resolve() {
  jq -r ".\"$1\".address" "$NODES_FILE"
}

usage() {
  echo -e "${BOLD}Uso:${RESET}"
  echo "--- VOTING ---"
  echo "  $0 deploy-vote --from <name> --options '[\"Sim\", \"Nao\"]'"
  echo "  $0 vote --from <name> --to <addr> --option \"Sim\""
  echo ""
  echo "--- VAULT (BANCO) ---"
  echo "  $0 deploy-vault --from <name>"
  echo "  $0 deposit --from <name> --to <addr> --amount <val>"
  echo "  $0 withdraw --from <name> --to <addr> --amount <val>"
  echo ""
  echo "--- HERANÇA (DEAD MAN'S SWITCH) ---"
  echo "  $0 deploy-heritage --from <name> --heir <name_or_addr> --secret \"Senha123\" --timeout 60"
  echo "  $0 ping --from <name> --to <addr>"
  echo "  $0 recover --from <heir_name> --to <addr>"
  exit 1
}

[[ $# -lt 1 ]] && usage
CMD="$1"; shift

case "$CMD" in
  deploy-vote)
    FROM=""; OPTS=""
    while [[ $# -gt 0 ]]; do
      case $1 in
        --from) FROM="$2"; shift 2 ;;
        --options) OPTS="$2"; shift 2 ;;
      esac
    done
    CODE=$(read_contract "voting")
    step "Deploying Voting..."
    SENDER=$(resolve "$FROM")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg c "$CODE" --argjson o "$OPTS" --arg sig "$SIGNATURE" \
      '{sender: $s, receiver: "contract_deploy", amount: 0, type: "deploy", data: $c, data_params: {options: $o}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  vote)
    FROM=""; TO=""; OPT=""
    while [[ $# -gt 0 ]]; do
      case $1 in
        --from) FROM="$2"; shift 2 ;;
        --to) TO="$2"; shift 2 ;;
        --option) OPT="$2"; shift 2 ;;
      esac
    done
    SENDER=$(resolve "$FROM")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$TO" --arg o "$OPT" --arg sig "$SIGNATURE" '{sender: $s, receiver: $r, amount: 0, type: "call", data: {opt: $o}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  deploy-vault)
    FROM=""
    while [[ $# -gt 0 ]]; do
      case $1 in
        --from) FROM="$2"; shift 2 ;;
      esac
    done
    CODE=$(read_contract "vault")
    step "Deploying Vault..."
    SENDER=$(resolve "$FROM")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg c "$CODE" --arg sig "$SIGNATURE" \
      '{sender: $s, receiver: "contract_deploy", amount: 0, type: "deploy", data: $c, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  deposit)
    FROM=""; TO=""; AMT=0
    while [[ $# -gt 0 ]]; do
      case $1 in
        --from) FROM="$2"; shift 2 ;;
        --to) TO="$2"; shift 2 ;;
        --amount) AMT="$2"; shift 2 ;;
      esac
    done
    SENDER=$(resolve "$FROM")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$TO" --argjson a "$AMT" --arg sig "$SIGNATURE" '{sender: $s, receiver: $r, amount: $a, type: "call", data: {action: "deposit"}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  withdraw)
    FROM=""; TO=""; AMT=0
    while [[ $# -gt 0 ]]; do
      case $1 in
        --from) FROM="$2"; shift 2 ;;
        --to) TO="$2"; shift 2 ;;
        --amount) AMT="$2"; shift 2 ;;
      esac
    done
    SENDER=$(resolve "$FROM")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$TO" --argjson a "$AMT" --arg sig "$SIGNATURE" '{sender: $s, receiver: $r, amount: 0, type: "call", data: {action: "withdraw", amount: $a}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  deploy-heritage)
    FROM=""; HEIR=""; SECRET=""; TIMEOUT=0
    while [[ $# -gt 0 ]]; do
      case $1 in
        --from) FROM="$2"; shift 2 ;;
        --heir) HEIR="$2"; shift 2 ;;
        --secret) SECRET="$2"; shift 2 ;;
        --timeout) TIMEOUT="$2"; shift 2 ;;
      esac
    done
    HEIR_ADDR=$(resolve "$HEIR")
    CODE=$(read_contract "heritage")
    step "Deploying Heritage..."
    SENDER=$(resolve "$FROM")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg c "$CODE" --arg h "$HEIR_ADDR" --arg sec "$SECRET" --argjson t "$TIMEOUT" --arg sig "$SIGNATURE" \
      '{sender: $s, receiver: "contract_deploy", amount: 0, type: "deploy", data: $c, data_params: {heir: $h, secret: $sec, timeout: $t}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  ping)
    FROM=""; TO=""
    while [[ $# -gt 0 ]]; do
      case $1 in
        --from) FROM="$2"; shift 2 ;;
        --to) TO="$2"; shift 2 ;;
      esac
    done
    SENDER=$(resolve "$FROM")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$TO" --arg sig "$SIGNATURE" '{sender: $s, receiver: $r, amount: 0, type: "call", data: {action: "ping"}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  recover)
    FROM=""; TO=""
    while [[ $# -gt 0 ]]; do
      case $1 in
        --from) FROM="$2"; shift 2 ;;
        --to) TO="$2"; shift 2 ;;
      esac
    done
    SENDER=$(resolve "$FROM")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$TO" --arg sig "$SIGNATURE" '{sender: $s, receiver: $r, amount: 0, type: "call", data: {action: "recover"}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  *) usage ;;
esac
