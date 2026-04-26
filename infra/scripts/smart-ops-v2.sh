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
    CODE="
storage['results'] = storage.get('results', {opt: 0 for opt in $OPTS})
storage['voters'] = storage.get('voters', [])
opt = msg['params'].get('opt')
if opt:
    if msg['sender'] in storage['voters']:
        result = 'ERRO: Ja votou'
    elif opt not in storage['results']:
        result = 'ERRO: Opcao invalida'
    else:
        storage['results'][opt] += 1
        storage['voters'].append(msg['sender'])
        result = f'Voto computado para {opt}'
else:
    result = 'Votacao Ativa'
"
    step "Deploying Voting..."
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
    CODE="
storage['balances'] = storage.get('balances', {})
sender = msg['sender']
if msg['amount'] > 0:
    storage['balances'][sender] = storage['balances'].get(sender, 0) + msg['amount']
    result = f'Operacao de Deposito: {msg[\"amount\"]}'
elif msg['params'].get('action') == 'withdraw':
    amt = msg['params'].get('amount', 0)
    if storage['balances'].get(sender, 0) >= amt:
        storage['balances'][sender] -= amt
        result = f'Saque de {amt} realizado.'
    else:
        result = 'ERRO: Saldo insuficiente no Vault'
else:
    result = 'Vault Ready'
"
    step "Deploying Vault..."
    SENDER=$(resolve "$FROM")
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
    CODE="
storage['owner'] = storage.get('owner', msg['sender'])
storage['heir'] = storage.get('heir', '$HEIR_ADDR')
storage['secret'] = storage.get('secret', '$SECRET')
storage['timeout'] = storage.get('timeout', $TIMEOUT)
storage['last_seen'] = storage.get('last_seen', msg['timestamp'])
storage['status'] = storage.get('status', 'ATIVO')

action = msg['params'].get('action')
if action == 'ping' and msg['sender'] == storage['owner']:
    storage['last_seen'] = msg['timestamp']
    result = 'Sinal de vida recebido'
elif action == 'recover' and msg['sender'] == storage['heir']:
    if msg['timestamp'] - storage['last_seen'] > storage['timeout']:
        storage['status'] = 'REVELADO'
        result = f'Segredo: {storage[\"secret\"]}'
    else:
        result = 'Ainda nao expirou'
"
    step "Deploying Heritage..."
    SENDER=$(resolve "$FROM")
    PAYLOAD=$(jq -n --arg s "$SENDER" --arg c "$CODE" --arg sig "$SIGNATURE" '{sender: $s, receiver: "contract_deploy", amount: 0, type: "deploy", data: $c, signature: $sig}')
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
