#!/usr/bin/env bash
set -e

step() { echo -e "\e[36m▶\e[0m $1"; }

# 1. Inicia a Blockchain (API + Minerador + Simulador Interno)
step "Iniciando infraestrutura da Blockchain..."
./run.sh &
RUN_PID=$!

# 2. Aguarda a API responder
step "Aguardando API em http://localhost:5000..."
until curl -s http://localhost:5000/api/blocks > /dev/null; do
  sleep 2
done

# 3. Dispara o estresse concorrente
step "Iniciando Estresse Concorrente (stress-test.sh)..."
chmod +x stress-test.sh
./stress-test.sh

# 4. Mantém o simulador de fundo para atividade residual
./post-send-values.sh --random --bg --sim --sleep 2 &

# 4. Gera Atividade de Smart Contracts Mock
step "Gerando Smart Contracts iniciais..."
# Deploy de um Vault e uma Votação para garantir que existam dados
./smart-ops-v2.sh deploy-vault --from User1 > /dev/null
./smart-ops-v2.sh deploy-vote --from User2 --options '["Docker", "BareMetal"]' > /dev/null

step "Sistema em plena operação!"

# Mantém o script vivo enquanto o run.sh estiver rodando
wait $RUN_PID
