#!/usr/bin/env bash
# ================================================
#  🪨 run.sh — mini-blockchain local setup
#  Cria venv, instala deps, sobe blockc + api
# ================================================

set -euo pipefail

VENV_DIR="venv"
GITIGNORE=".gitignore"
PORT=5000

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
RESET='\033[0m'

step() { echo -e "${CYAN}▶${RESET} $1"; }
ok()   { echo -e "${GREEN}✓${RESET} $1"; }
warn() { echo -e "${YELLOW}⚠${RESET}  $1"; }
die()  { echo -e "${RED}✗${RESET} $1"; exit 1; }

echo ""
echo -e "${BOLD}🪨 mini-blockchain — setup & run${RESET}"
echo "────────────────────────────────────────────"

# ── Verifica Python ────────────────────────────
step "Verificando Python..."
PYTHON=$(command -v python3 || command -v python || true)
[ -z "$PYTHON" ] && die "Python não encontrado"
ok "$($PYTHON --version)"

# ── Cria venv ──────────────────────────────────
if [ ! -d "$VENV_DIR" ]; then
  step "Criando venv em ./$VENV_DIR..."
  $PYTHON -m venv "$VENV_DIR"
  ok "venv criado"
else
  ok "venv já existe"
fi

# ── Valida .gitignore ──────────────────────────
step "Verificando .gitignore..."
if [ ! -f "$GITIGNORE" ]; then
  warn ".gitignore não encontrado — criando..."
  echo "venv/" > "$GITIGNORE"
  ok "venv/ adicionado ao .gitignore"
elif grep -q "^venv" "$GITIGNORE" 2>/dev/null; then
  ok "venv já está no .gitignore"
else
  warn "venv não está no .gitignore — adicionando..."
  echo "venv/" >> "$GITIGNORE"
  ok "venv/ adicionado ao .gitignore"
fi

# ── Ativa venv ─────────────────────────────────
step "Ativando venv..."
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
ok "venv ativo: $(which python)"

# ── Instala dependências ───────────────────────
step "Instalando dependências..."
if [ -f "requirements.txt" ]; then
  pip install -q -r requirements.txt
  ok "requirements.txt instalado"
fi

# pacotes extras identificados pelo Trae
pip install -q flask flask-restx requests ecdsa filelock
ok "Todos os pacotes instalados"

# ── Valida arquivos principais ─────────────────
step "Validando arquivos do projeto..."
[ ! -f "blockc.py" ] && die "blockc.py não encontrado"
[ ! -f "api.py" ]    && die "api.py não encontrado"
ok "blockc.py e api.py encontrados"

# ── Sobe os processos ──────────────────────────
echo ""
echo -e "${BOLD}Subindo serviços...${RESET}"
echo -e "${YELLOW}  Ctrl+C para encerrar tudo${RESET}"
echo ""

# mata processos filhos ao sair
cleanup() {
  echo ""
  echo -e "${YELLOW}Encerrando...${RESET}"
  kill "$BLOCKC_PID" "$API_PID" 2>/dev/null || true
  deactivate 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# sobe blockc em background
step "Iniciando blockc.py (mining)..."
python blockc.py &
BLOCKC_PID=$!
sleep 2
kill -0 "$BLOCKC_PID" 2>/dev/null && ok "blockc.py rodando (PID $BLOCKC_PID)" || die "blockc.py falhou ao iniciar"

# sobe api em background
step "Iniciando api.py (porta $PORT)..."
python api.py &
API_PID=$!
sleep 2
kill -0 "$API_PID" 2>/dev/null && ok "api.py rodando (PID $API_PID)" || die "api.py falhou ao iniciar"

# ── Validação HTTP ─────────────────────────────
step "Validando porta $PORT..."
sleep 1
if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PORT" | grep -qE "^(200|301|302)"; then
  ok "http://localhost:$PORT respondendo"
else
  warn "Porta $PORT ainda não respondeu — pode precisar de mais tempo"
fi

echo ""
echo -e "${BOLD}✅ Pronto!${RESET}"
echo -e "   ${CYAN}UI:${RESET}     http://localhost:$PORT"
echo -e "   ${CYAN}Swagger:${RESET} http://localhost:$PORT/api/docs"
echo -e "   ${CYAN}Mining:${RESET}  watch o terminal do blockc.py"
echo ""

# mantém vivo até Ctrl+C
wait "$BLOCKC_PID" "$API_PID"