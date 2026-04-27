#!/usr/bin/env bash
# ================================================
#  🏦 vault.sh — Vault (Banco)
# ================================================

source "$(dirname "${BASH_SOURCE[0]}")/commons.sh"

usage() {
  echo -e "${BOLD}Uso:${RESET}"
  echo "  $0 deploy --from <name> [--pool <addr>]"
  echo "  $0 deposit --from <name> --to <addr> --amount <val>"
  echo "  $0 withdraw --from <name> --to <addr> --amount <val>"
  echo "  $0 set-pool --from <owner_name> --to <vault_addr> --pool <new_pool_addr>"
  echo -e "\n${BOLD}Opcional:${RESET}"
  echo "  --pool <addr>  Endereço ou nome da Stake Pool alvo."
  exit 1
}

[[ $# -lt 1 ]] && usage
CMD="$1"; shift

case "$CMD" in
  set-pool)
    FROM=""; TO=""; POOL=""
    while [[ $# -gt 0 ]]; do
      case $1 in
        --from) FROM="$2"; shift 2 ;;
        --to) TO="$2"; shift 2 ;;
        --pool) POOL="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    [[ -z "$FROM" ]] && fail "Faltando --from <owner_name>"
    [[ -z "$TO" ]] && fail "Faltando --to <vault_addr>"
    [[ -z "$POOL" ]] && fail "Faltando --pool <new_pool_addr>"

    SENDER=$(resolve "$FROM")
    RECEIVER=$(resolve "$TO")
    NEW_POOL_ADDR=$(resolve "$POOL")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$RECEIVER" --arg p "$NEW_POOL_ADDR" --arg sig "$SIGNATURE" \
      '{sender: $s, receiver: $r, amount: 0, type: "call", data: {action: "set_pool", pool: $p}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  deploy)
    FROM=""; POOL=""
    while [[ $# -gt 0 ]]; do
      case $1 in
        --from) FROM="$2"; shift 2 ;;
        --pool) POOL="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    [[ -z "$FROM" ]] && fail "Faltando --from <name>"

    # Resolve endereço da pool se um nome for passado
    POOL_ADDR=""
    [[ -n "$POOL" ]] && POOL_ADDR=$(resolve "$POOL")

    CODE=$(read_contract "vault")
    step "Deploying Vault..."
    SENDER=$(resolve "$FROM")
    # Agora passamos target_pool via data_params para o contrato
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg c "$CODE" --arg sig "$SIGNATURE" --arg p "$POOL_ADDR" \
      '{sender: $s, receiver: "contract_deploy", amount: 0, type: "deploy", data: $c, data_params: {target_pool: $p}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  deposit)
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
    RECEIVER=$(resolve "$TO")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$RECEIVER" --argjson a "$AMT" --arg sig "$SIGNATURE" '{sender: $s, receiver: $r, amount: $a, type: "call", data: {action: "deposit"}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  withdraw)
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
    RECEIVER=$(resolve "$TO")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$RECEIVER" --argjson a "$AMT" --arg sig "$SIGNATURE" '{sender: $s, receiver: $r, amount: 0, type: "call", data: {action: "withdraw", amount: $a}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  *) usage ;;
esac
