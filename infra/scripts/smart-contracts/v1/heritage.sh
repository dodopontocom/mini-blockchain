#!/usr/bin/env bash
# ================================================
#  ⚰️ heritage.sh — Heritage (Dead Man's Switch)
# ================================================

source "$(dirname "${BASH_SOURCE[0]}")/commons.sh"

usage() {
  echo -e "${BOLD}Uso:${RESET}"
  echo "  $0 deploy --from <name> --heir <name_or_addr> --secret \"Senha123\" --timeout 60"
  echo "  $0 ping --from <name> --to <addr>"
  echo "  $0 recover --from <heir_name> --to <addr>"
  exit 1
}

[[ $# -lt 1 ]] && usage
CMD="$1"; shift

case "$CMD" in
  deploy)
    FROM=""; HEIR=""; SECRET=""; TIMEOUT=0; AMT=0
    while [[ $# -gt 0 ]]; do
      case $1 in
        --from) FROM="$2"; shift 2 ;;
        --heir) HEIR="$2"; shift 2 ;;
        --secret) SECRET="$2"; shift 2 ;;
        --timeout) TIMEOUT="$2"; shift 2 ;;
        --amount) AMT="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    [[ -z "$FROM" ]] && fail "Faltando --from <name>"
    [[ -z "$HEIR" ]] && fail "Faltando --heir <name_or_addr>"
    [[ -z "$SECRET" ]] && fail "Faltando --secret <string>"
    [[ "$TIMEOUT" -le 0 ]] && fail "Faltando --timeout <sec> (deve ser > 0)"
    [[ "$AMT" -le 0 ]] && fail "Faltando --amount <val> (deve ser > 0)"

    HEIR_ADDR=$(resolve "$HEIR")
    CODE=$(read_contract "heritage")
    step "Deploying Heritage with amount $AMT..."
    SENDER=$(resolve "$FROM")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg c "$CODE" --arg h "$HEIR_ADDR" --arg sec "$SECRET" \
      --argjson t "$TIMEOUT" --argjson a "$AMT" --arg sig "$SIGNATURE" \
      '{sender: $s, receiver: "contract_deploy", amount: $a, type: "deploy", data: $c, data_params: {heir: $h, secret: $sec, timeout: $t}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  ping)
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
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$TO" --arg sig "$SIGNATURE" '{sender: $s, receiver: $r, amount: 0, type: "call", data: {action: "ping"}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  recover)
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
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$TO" --arg sig "$SIGNATURE" '{sender: $s, receiver: $r, amount: 0, type: "call", data: {action: "recover"}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  *) usage ;;
esac
