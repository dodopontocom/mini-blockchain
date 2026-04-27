#!/usr/bin/env bash
# ================================================
#  🥩 stake-pool.sh — Stake Pool Contract
# ================================================

source "$(dirname "${BASH_SOURCE[0]}")/commons.sh"

usage() {
  echo -e "${BOLD}Uso:${RESET}"
  echo "  $0 deploy --from <name>"
  echo "  $0 stake --from <name> --to <addr> --amount <val>"
  echo "  $0 request-unstake --from <name> --to <addr> --amount <val>"
  echo "  $0 withdraw-stake --from <name> --to <addr>"
  echo "  $0 claim-reward --from <name> --to <addr>"
  echo "  $0 fund --from <name> --to <addr> --amount <val>"
  exit 1
}

[[ $# -lt 1 ]] && usage
CMD="$1"; shift

case "$CMD" in
  deploy)
    FROM=""
    while [[ $# -gt 0 ]]; do
      case $1 in
        --from) FROM="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    [[ -z "$FROM" ]] && fail "Faltando --from <name>"

    CODE=$(read_contract "stake_pool")
    step "Deploying Stake Pool..."
    SENDER=$(resolve "$FROM")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg c "$CODE" --arg sig "$SIGNATURE" \
      '{sender: $s, receiver: "contract_deploy", amount: 0, type: "deploy", data: $c, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  stake)
    FROM=""; TO=""; AMT=0
    while [[ $# -gt 0 ]]; do
      case $1 in
        --from) FROM="$2"; shift 2 ;;
        --to) TO="$2"; shift 2 ;;
        --amount) AMT="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    [[ -z "$FROM" ]] && fail "Faltando --from <name>"
    [[ -z "$TO" ]] && fail "Faltando --to <addr>"
    [[ "$AMT" -le 0 ]] && fail "Faltando --amount <val> (deve ser > 0)"

    SENDER=$(resolve "$FROM")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$TO" --argjson a "$AMT" --arg sig "$SIGNATURE" \
      '{sender: $s, receiver: $r, amount: $a, type: "call", data: {action: "stake"}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  request-unstake)
    FROM=""; TO=""; AMT=0
    while [[ $# -gt 0 ]]; do
      case $1 in
        --from) FROM="$2"; shift 2 ;;
        --to) TO="$2"; shift 2 ;;
        --amount) AMT="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    [[ -z "$FROM" ]] && fail "Faltando --from <name>"
    [[ -z "$TO" ]] && fail "Faltando --to <addr>"
    [[ "$AMT" -le 0 ]] && fail "Faltando --amount <val> (deve ser > 0)"

    SENDER=$(resolve "$FROM")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$TO" --argjson a "$AMT" --arg sig "$SIGNATURE" \
      '{sender: $s, receiver: $r, amount: 0, type: "call", data: {action: "request_unstake", amount: $a}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  withdraw-stake)
    FROM=""; TO=""
    while [[ $# -gt 0 ]]; do
      case $1 in
        --from) FROM="$2"; shift 2 ;;
        --to) TO="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    [[ -z "$FROM" ]] && fail "Faltando --from <name>"
    [[ -z "$TO" ]] && fail "Faltando --to <addr>"

    SENDER=$(resolve "$FROM")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$TO" --arg sig "$SIGNATURE" \
      '{sender: $s, receiver: $r, amount: 0, type: "call", data: {action: "withdraw_stake"}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  claim-reward)
    FROM=""; TO=""
    while [[ $# -gt 0 ]]; do
      case $1 in
        --from) FROM="$2"; shift 2 ;;
        --to) TO="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    [[ -z "$FROM" ]] && fail "Faltando --from <name>"
    [[ -z "$TO" ]] && fail "Faltando --to <addr>"

    SENDER=$(resolve "$FROM")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$TO" --arg sig "$SIGNATURE" \
      '{sender: $s, receiver: $r, amount: 0, type: "call", data: {action: "claim_reward"}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  fund)
    FROM=""; TO=""; AMT=0
    while [[ $# -gt 0 ]]; do
      case $1 in
        --from) FROM="$2"; shift 2 ;;
        --to) TO="$2"; shift 2 ;;
        --amount) AMT="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    [[ -z "$FROM" ]] && fail "Faltando --from <name>"
    [[ -z "$TO" ]] && fail "Faltando --to <addr>"
    [[ "$AMT" -le 0 ]] && fail "Faltando --amount <val> (deve ser > 0)"

    SENDER=$(resolve "$FROM")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$TO" --argjson a "$AMT" --arg sig "$SIGNATURE" \
      '{sender: $s, receiver: $r, amount: $a, type: "call", data: {action: "fund"}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  *) usage ;;
esac
