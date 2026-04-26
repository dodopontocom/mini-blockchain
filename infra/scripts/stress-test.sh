#!/usr/bin/env bash
# ================================================
#  🔥 stress-test.sh — V3 Inundação Agressiva
# ================================================

API_URL="http://localhost:5000"
NODES_FILE="nodes_data.json"

# Fallback de endereços caso o jq falhe no startup
SENDER="8e04b460bc4ea34d036809c79786a4c3073d28046fa37983b6e375a798a29fe7cfd2f843afd443aa76bcaa231930b9580529e781563140032ef8c168091b3851"
RECEIVER="8e03de2a914796a7742c7e43969ebcc11db47e0a58ba4ad7bac3ed95ca66f188fb06c04ddfd1384c34f87da386a0572c2609cc561befbcf9e1d4f11b1efe7546"

TX_PAYLOAD=$(jq -n --arg s "$SENDER" --arg r "$RECEIVER" '{sender: $s, receiver: $r, amount: 0.0001, signature: "stress_sig_v3"}')

# Lançar 15 threads de envio rápido
for t in {1..15}; do
  (
    for i in {1..100}; do
      curl -s -X POST "$API_URL/api/add-transaction" \
           -H "Content-Type: application/json" \
           -d "$TX_PAYLOAD" > /dev/null
    done
  ) &
done

wait
echo "[STRESS] Lote de 1500 transações enviado."
