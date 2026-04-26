#!/usr/bin/env bash
# ================================================
#  🔥 stress-test-v2.sh — Saturação de Alta Performance
# ================================================

API_URL="http://localhost:5000"
NODES_FILE="nodes_data.json"

# Pega dois endereços reais para evitar falhas de validação
SENDER=$(jq -r '.Alice.address' $NODES_FILE)
RECEIVER=$(jq -r '.Bob.address' $NODES_FILE)
CONTRACT=$(jq -r '.contracts | keys[0]' blockchain_data.json 2>/dev/null || echo "98c5886478cf32c1d185f93551a42ba2860d1df5")

step() { echo -e "\e[36m[STRESS]\e[0m $1"; }

# Payload de transação pura
TX_PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$RECEIVER" '{sender: $s, receiver: $r, amount: 0.0001, signature: "stress_test_sig"}')

# Payload de chamada de contrato
CALL_PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$CONTRACT" '{sender: $s, receiver: $r, amount: 0, type: "call", data: {key: "load", val: "heavy"}, signature: "stress_sig"}')

step "Iniciando inundação da API..."

# Dispara 200 transações em lotes de 20 simultâneas usando xargs
seq 200 | xargs -I % -P 20 curl -s -X POST "$API_URL/api/add-transaction" \
    -H "Content-Type: application/json" \
    -d "$TX_PAYLOAD" > /dev/null &

# Dispara 50 chamadas de contrato simultâneas
seq 50 | xargs -I % -P 10 curl -s -X POST "$API_URL/api/add-transaction" \
    -H "Content-Type: application/json" \
    -d "$CALL_PAYLOAD" > /dev/null &

wait
step "Rajada concluída com sucesso."
