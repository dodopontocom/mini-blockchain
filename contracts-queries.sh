#!/usr/bin/env bash
# ================================================
#  🪨 contracts-queries.sh — contract inspector
#  Consulta o estado e código de contratos
# ================================================

set -euo pipefail

PORT=5000
API_URL="http://localhost:$PORT"

# Cores
CYAN='\033[0;36m'
GREEN='\033[0;32m'
BOLD='\033[1m'
RESET='\033[0m'

step() { echo -e "${CYAN}▶${RESET} $1"; }

usage() {
  echo -e "${BOLD}Uso:${RESET}"
  echo -e "  $0 list            # Lista todos os endereços de contratos"
  echo -e "  $0 state <addr>    # Mostra o storage de um contrato específico"
  echo -e "  $0 code <addr>     # Mostra o código-fonte de um contrato"
  echo -e "  $0 full            # Mostra o estado global completo"
  exit 1
}

[[ $# -lt 1 ]] && usage

CMD="$1"; shift

case "$CMD" in
  list)
    step "Contratos deployados no sistema:"
    if [ -f "blockchain_data.json" ]; then
        jq -r ".contracts | keys[]" blockchain_data.json 2>/dev/null || echo "Nenhum contrato encontrado."
    else
        echo "Erro: blockchain_data.json não encontrado."
    fi
    ;;

  state)
    [[ $# -lt 1 ]] && usage
    ADDR="$1"
    step "Storage do contrato $ADDR:"
    curl -s "$API_URL/api/state" | jq -r ".\"$ADDR\" // \"Endereço não encontrado ou sem storage.\""
    ;;

  code)
    [[ $# -lt 1 ]] && usage
    ADDR="$1"
    step "Código-fonte do contrato $ADDR:"
    if [ -f "blockchain_data.json" ]; then
        jq -r ".contracts.\"$ADDR\" // \"Código não encontrado.\"" blockchain_data.json
    else
        echo "Erro: blockchain_data.json não encontrado."
    fi
    ;;

  full)
    step "Estado Global Completo (Snapshot):"
    curl -s "$API_URL/api/state" | jq .
    ;;

  *) usage ;;
esac
