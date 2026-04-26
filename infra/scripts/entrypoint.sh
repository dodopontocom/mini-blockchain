#!/usr/bin/env bash
set -e
step() { echo -e "\e[36m▶\e[0m $1"; }

# 1. Inicia a Blockchain
step "Iniciando infraestrutura..."
./infra/scripts/run.sh &
RUN_PID=$!

# 2. Aguarda API estar 100% pronta
step "Aguardando estabilização da API..."
sleep 10 # Tempo extra para o Flask e o Minerador acordarem

# 3. WARM-UP: Garante que existem contratos
./infra/scripts/smart-ops-v2.sh deploy-vault --from User1 > /dev/null
sleep 5

# 4. ESTRESSE: Agora sim, inundação pesada e aleatória
LEVEL=${STRESS_LEVEL:-1}
BG_VAL=$(( LEVEL * 10 ))
SIM_VAL=$(( LEVEL * 100 ))

step "Executando Stress Test Engine (Nível: $LEVEL | BG: $BG_VAL | SIM: $SIM_VAL)..."
chmod +x infra/scripts/stress-test.sh

# Executa o estresse em background para permitir monitoramento
./infra/scripts/stress-test.sh --random --bg "$BG_VAL" --sim "$SIM_VAL" &
STRESS_PID=$!

# 5. Atividade residual contínua
./infra/scripts/post-send-values.sh --random --bg 2 --sim 9999 --sleep 1 &

step "Monitorando simulação..."
wait $RUN_PID
