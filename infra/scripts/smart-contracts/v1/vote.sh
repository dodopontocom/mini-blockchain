#!/usr/bin/env bash
# ================================================
#  🗳️ vote.sh — Voting
# ================================================

source "$(dirname "${BASH_SOURCE[0]}")/commons.sh"

usage() {
  echo -e "${BOLD}Uso:${RESET}"
  echo "  $0 deploy --from <name> --options '[\"Sim\", \"Nao\"]'"
  echo "  $0 vote --from <name> --to <addr> --option \"Sim\""
  exit 1
}

[[ $# -lt 1 ]] && usage
CMD="$1"; shift

case "$CMD" in
  deploy)
    FROM=""; OPTS=""
    while [[ $# -gt 0 ]]; do
      case $1 in
        --from) FROM="$2"; shift 2 ;;
        --options) OPTS="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    [[ -z "$FROM" ]] && fail "Faltando --from <name>"
    [[ -z "$OPTS" ]] && fail "Faltando --options '[\"Op1\", \"Op2\"]'"
    
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
        *) shift ;;
      esac
    done
    [[ -z "$FROM" ]] && fail "Faltando --from <name>"
    [[ -z "$TO" ]] && fail "Faltando --to <addr>"
    [[ -z "$OPT" ]] && fail "Faltando --option <value>"

    SENDER=$(resolve "$FROM")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$TO" --arg o "$OPT" --arg sig "$SIGNATURE" '{sender: $s, receiver: $r, amount: 0, type: "call", data: {opt: $o}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  *) usage ;;
esac
