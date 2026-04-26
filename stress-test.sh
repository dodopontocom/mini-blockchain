#!/usr/bin/env bash
# ================================================
#  🔥 stress-test.sh — Saturação Concorrente
#  Objetivo: Gerar carga máxima no Runner
# ================================================

PORT=5000
API_URL="http://localhost:$PORT"
CONCURRENCY=5 # Número de workers paralelos
TX_PER_WORKER=50 # Transações por worker

step() { echo -e "\e[36m[STRESS]\e[0m $1"; }

# Função worker para inundar a API
flood_worker() {
    local worker_id=$1
    for ((i=1; i<=TX_PER_WORKER; i++)); do
        # Gera transação aleatória ultra-rápida
        curl -s -X POST "$API_URL/api/enviar-transacao" \
            -d "receiver=8e03de2a914796a7742c7e43969ebcc11db47e0a58ba4ad7bac3ed95ca66f188fb06c04ddfd1384c34f87da386a0572c2609cc561befbcf9e1d4f11b1efe7546" \
            -d "amount=0.001" \
            -o /dev/null
        
        # A cada 10 transações, faz uma chamada de contrato para estressar a VM
        if (( i % 10 == 0 )); then
            curl -s -X POST "$API_URL/api/add-transaction" \
                -H "Content-Type: application/json" \
                -d '{"sender":"coinbase","receiver":"98c5886478cf32c1d185f93551a42ba2860d1df5","amount":0,"type":"call","data":{"key":"stress","val":"'$worker_id-$i'"},"signature":"sig"}' \
                -o /dev/null
        fi
    done
}

step "Iniciando estresse com $CONCURRENCY workers enviando $(($CONCURRENCY * $TX_PER_WORKER)) operações..."

for ((w=1; w<=CONCURRENCY; w++)); do
    flood_worker $w &
done

wait
step "Rajada de estresse concluída."
