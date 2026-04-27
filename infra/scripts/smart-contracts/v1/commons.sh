#!/usr/bin/env bash
# ================================================
#  🛠️ commons.sh — Shared logic for smart-ops
# ================================================

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
fail() { echo -e "\033[0;31m✘ Erro:\033[0m $1" >&2; exit 1; }

# Path to contracts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../" && pwd)"
CONTRACTS_DIR="$PROJECT_ROOT/src/contracts"

read_contract() {
  local contract_file="$CONTRACTS_DIR/$1.py"
  if [[ ! -f "$contract_file" ]]; then
    fail "Arquivo de contrato não encontrado: $contract_file"
  fi
  cat "$contract_file"
}

resolve() {
  [[ -z "$1" ]] && fail "Nome do nó não fornecido."

  # Se já for um endereço hexadecimal (40 caracteres para contrato ou 128 para usuário)
  if [[ "$1" =~ ^[a-fA-F0-9]{40}$ ]] || [[ "$1" =~ ^[a-fA-F0-9]{128}$ ]]; then
    echo "$1"
    return
  fi

  # Check if nodes file exists in project root
  local nodes_path="$PROJECT_ROOT/$NODES_FILE"
  if [[ ! -f "$nodes_path" ]]; then
    fail "Arquivo $NODES_FILE não encontrado em $PROJECT_ROOT"
  fi
  local addr
  addr=$(jq -r ".\"$1\".address // empty" "$nodes_path")
  [[ -z "$addr" ]] && fail "Nó '$1' não encontrado em $nodes_path"
  echo "$addr"
}
