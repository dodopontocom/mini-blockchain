#!/usr/bin/env bash
# ================================================
#  🪨 smart-ops-v2.sh — advanced smart contracts
#  Contratos com Lógica de Negócio (Votação e Vault)
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

resolve() {
  jq -r ".\"$1\".address" "$NODES_FILE"
}

usage() {
  echo -e "${BOLD}Uso:${RESET}"
  echo "  $0 deploy-vote --from Alice --options '[\"Python\", \"JavaScript\"]'"
  echo "  $0 vote --from Bob --to <addr> --option \"Python\""
  echo ""
  echo "  $0 deploy-vault --from Charlie"
  echo "  $0 deposit --from David --to <addr> --amount 50"
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
    
    # Lógica do contrato (Python)
    # Note que usamos as aspas triplas para facilitar o código multi-linha
    CODE="
if 'results' not in storage:
    storage['results'] = {opt: 0 for opt in $OPTS}
    storage['voters'] = []
    result = 'Votacao Inicializada'
else:
    opt = msg['params'].get('opt')
    if msg['sender'] in storage['voters']:
        result = 'ERRO: Voce ja votou!'
    elif opt not in storage['results']:
        result = 'ERRO: Opcao invalida!'
    else:
        storage['results'][opt] += 1
        storage['voters'].append(msg['sender'])
        result = f'Voto computado para {opt}'
"
    step "Fazendo deploy do contrato de Votação..."
    SENDER=$(resolve "$FROM")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg c "$CODE" --arg sig "$SIGNATURE" '{sender: $s, receiver: "contract_deploy", amount: 0, type: "deploy", data: $c, signature: $sig}')
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
    step "Enviando voto de $FROM para $OPT..."
    SENDER=$(resolve "$FROM")
    # No call, enviamos o parâmetro 'opt' que o código acima espera
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$TO" --arg o "$OPT" --arg sig "$SIGNATURE" '{sender: $s, receiver: $r, amount: 0, type: "call", data: {opt: $o}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  deploy-vault)
    # Lógica: Acumula saldo por endereço
    CODE="
if 'balances' not in storage: storage['balances'] = {}
sender = msg['sender']
if msg['amount'] > 0:
    storage['balances'][sender] = storage['balances'].get(sender, 0) + msg['amount']
    result = f'Deposito recebido! Novo saldo: {storage[\"balances\"][sender]}'
else:
    result = f'Seu saldo atual: {storage[\"balances\"].get(sender, 0)}'
"
    step "Fazendo deploy do contrato de Vault (Banco)..."
    SENDER=$(resolve "$2")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg c "$CODE" --arg sig "$SIGNATURE" '{sender: $s, receiver: "contract_deploy", amount: 0, type: "deploy", data: $c, signature: $sig}')
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
    step "Depositando $AMT BTC no Vault..."
    SENDER=$(resolve "$FROM")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$TO" --argjson a "$AMT" --arg sig "$SIGNATURE" '{sender: $s, receiver: $r, amount: $a, type: "call", data: {}, signature: $sig}')
    curl -s -X POST "$API_URL/api/add-transaction" -H "Content-Type: application/json" -d "$PAYLOAD" | jq .
    ;;

  *) usage ;;
esac
