#!/usr/bin/env bash
set -e
step() { echo -e "\e[36m▶\e[0m $1"; }

# 1. Inicia a Blockchain
step "Iniciando infraestrutura..."
./run.sh &
RUN_PID=$!

# 2. Aguarda API estar 100% pronta
step "Aguardando estabilização da API..."
sleep 10 # Tempo extra para o Flask e o Minerador acordarem

# 3. WARM-UP: Garante que existem contratos
./smart-ops-v2.sh deploy-vault --from User1 > /dev/null
sleep 5

# 4. ESTRESSE: Agora sim, inundação pesada em loop
LEVEL=${STRESS_LEVEL:-1}
step "Executando Stress Test V3 (Nível: $LEVEL)..."
chmod +x stress-test.sh

# Rodamos o estresse 'LEVEL' vezes em paralelo
for ((i=1; i<=LEVEL; i++)); do
   ./stress-test.sh &
done

# 5. Atividade residual
./post-send-values.sh --random --bg --sim --sleep 0.5 &

step "Monitorando simulação..."
wait $RUN_PID
