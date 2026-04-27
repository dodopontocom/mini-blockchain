#!/bin/bash

# Cores para o terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'

API_URL="http://localhost:5000"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SMART_OPS="$SCRIPT_DIR/smart-ops-v2.sh"

function header() {
    clear
    echo -e "${BLUE}${BOLD}=============================================================="
    echo -e "      SIMULAÇÃO EDUCACIONAL: SMART CONTRACT HERANÇA (V1)"
    echo -e "==============================================================${NC}"
    echo ""
}

function msg() {
    echo -e "${YELLOW}>>${NC} $1"
}

function step() {
    echo -e "\n${GREEN}${BOLD}[PASSO $1]${NC} ${BOLD}$2${NC}"
    echo -e "${BLUE}--------------------------------------------------------------${NC}"
}

header
msg "Bem-vindo! Vamos simular um 'Dead Man's Switch' (Herança)."
msg "Conceito: Alice quer garantir que seu segredo seja revelado a Bob"
msg "apenas se ela ficar inativa por mais de 10 segundos."
echo ""
read -p "Pressione [ENTER] para começar..."

# 1. Deploy
step "1" "Alice faz o deploy do contrato"
echo -e "Parâmetros:\n  - Herdeiro: Bob\n  - Segredo: 'Ouro está no jardim'\n  - Tempo: 10 segundos"
echo ""

# Executa deploy e captura o endereço do contrato
DEPLOY_OUT=$($SMART_OPS deploy-heritage --from Alice --heir Bob --secret "Ouro está no jardim" --timeout 10)
CONTRACT_ADDR=$(echo "$DEPLOY_OUT" | grep -oE '[0-9a-f]{64}' | tail -n 1)

if [ -z "$CONTRACT_ADDR" ]; then
    echo -e "${RED}Erro: Não foi possível obter o endereço do contrato.${NC}"
    echo "$DEPLOY_OUT"
    exit 1
fi

msg "Contrato publicado em: ${BOLD}$CONTRACT_ADDR${NC}"
sleep 2

# 2. Ping (Alice está viva)
step "2" "Alice envia um 'Ping' para mostrar que está ativa"
msg "Isso reseta o cronômetro do contrato."
$SMART_OPS ping --from Alice --to "$CONTRACT_ADDR"
sleep 3

# 3. Bob tenta recuperar antes da hora
step "3" "Bob tenta recuperar o segredo precocemente"
msg "O contrato deve negar, pois Alice acabou de dar um ping."
$SMART_OPS recover --from Bob --to "$CONTRACT_ADDR"
sleep 4

# 4. Alice desaparece
step "4" "Alice fica inativa (Aguardando 12 segundos...)"
for i in {12..1}; do
    echo -ne "\r${RED}Tempo restante para expiração: ${i}s  ${NC}"
    sleep 1
done
echo -e "\r${RED}STATUS: Alice está oficialmente 'desaparecida'!          ${NC}"
sleep 1

# 5. Bob recupera o segredo
step "5" "Bob tenta recuperar o segredo novamente"
msg "Agora o contrato deve permitir e revelar o conteúdo."
RECOVER_OUT=$($SMART_OPS recover --from Bob --to "$CONTRACT_ADDR")
echo -e "${GREEN}${BOLD}RESULTADO:${NC}"
echo "$RECOVER_OUT" | jq .

echo -e "\n${BLUE}${BOLD}=============================================================="
echo -e "      SIMULAÇÃO CONCLUÍDA COM SUCESSO!"
echo -e "==============================================================${NC}"
msg "Você viu como a lógica on-chain protege e automatiza a herança."
msg "Ninguém (nem o administrador) precisou intervir para Bob receber o segredo."
echo ""
