#!/usr/bin/env bash
set -e
step() { echo -e "\e[36m▶\e[0m $1"; }

# 1. Inicia a Blockchain
step "Iniciando infraestrutura..."
./run.sh &
RUN_PID=$!

# 2. Aguarda API
step "Aguardando API..."
until curl -s http://localhost:5000/api/blocks > /dev/null; do sleep 2; done

# 3. WARM-UP: Prepara contratos para o estresse
step "Warm-up: Criando contratos para monitoramento..."
./smart-ops-v2.sh deploy-vault --from User1 > /dev/null
./smart-ops-v2.sh deploy-vote --from User2 --options '["Lento", "Rapido"]' > /dev/null

# 4. ESTRESSE: Agora que os contratos existem, vamos inundar
step "Executando Stress Test Concorrente..."
chmod +x stress-test.sh
./stress-test.sh

# 5. Atividade residual
./post-send-values.sh --random --bg --sim --sleep 1 &

step "Simulação em andamento..."
wait $RUN_PID
