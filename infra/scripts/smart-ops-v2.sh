#!/usr/bin/env bash
# ==========================================================
#  🪨 smart-ops-v2.sh — router for segregated scripts
# ==========================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
V1_DIR="$SCRIPT_DIR/smart-contracts/v1"

usage() {
  echo "Uso: $0 <modulo> <comando> [args]"
  echo "Modulos disponiveis:"
  echo "  heritage -> $V1_DIR/heritage.sh"
  echo "  vault    -> $V1_DIR/vault.sh"
  echo "  vote     -> $V1_DIR/vote.sh"
  echo ""
  echo "Exemplo: $0 heritage deploy --from Alice ..."
  exit 1
}

[[ $# -lt 2 ]] && usage

MODULE="$1"; shift

case "$MODULE" in
  heritage) "$V1_DIR/heritage.sh" "$@" ;;
  vault)    "$V1_DIR/vault.sh" "$@" ;;
  vote)     "$V1_DIR/vote.sh" "$@" ;;
  # Mapeamento de comandos antigos para manter compatibilidade retroativa
  deploy-heritage) "$V1_DIR/heritage.sh" deploy "$@" ;;
  ping)            "$V1_DIR/heritage.sh" ping "$@" ;;
  recover)         "$V1_DIR/heritage.sh" recover "$@" ;;
  deploy-vault)    "$V1_DIR/vault.sh" deploy "$@" ;;
  deposit)         "$V1_DIR/vault.sh" deposit "$@" ;;
  withdraw)        "$V1_DIR/vault.sh" withdraw "$@" ;;
  deploy-vote)     "$V1_DIR/vote.sh" deploy "$@" ;;
  vote)            "$V1_DIR/vote.sh" vote "$@" ;;
  *) usage ;;
esac
