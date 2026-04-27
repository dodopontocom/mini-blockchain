#!/usr/bin/env bash
# ================================================
#  🔐 hash-secret.sh — Gera hash SHA256 do segredo
# ================================================

API_URL="http://localhost:5000"

usage() {
  echo "Uso: $0 --secret \"texto\" | --secret-file caminho/arquivo.txt"
  exit 1
}

[[ $# -lt 1 ]] && usage

SECRET=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --secret) SECRET="$2"; shift 2 ;;
    --secret-file) SECRET=$(cat "$2"); shift 2 ;;
    *) usage ;;
  esac
done

if [[ -z "$SECRET" ]]; then
  echo "Erro: Segredo vazio ou não fornecido."
  exit 1
fi

# Chama a API e extrai apenas o hash
HASH=$(curl -s -X POST "$API_URL/api/hash-secret" \
  -H "Content-Type: application/json" \
  -d "{\"secret\": \"$SECRET\"}" | jq -r '.hash')

if [[ "$HASH" == "null" ]] || [[ -z "$HASH" ]]; then
  echo "Erro ao gerar hash."
  exit 1
fi

echo -n "$HASH"
