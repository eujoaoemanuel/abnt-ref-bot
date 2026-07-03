#!/usr/bin/env bash
# Inicializador Linux/Mac: cria venv, instala deps, pede token, roda.
set -e
cd "$(dirname "$0")"

echo "============================================"
echo "   ABNT Ref Bot - inicializador"
echo "============================================"
echo

# 1. localizar python
if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python >/dev/null 2>&1; then PY=python
else
  echo "[ERRO] Python nao encontrado. Instale o Python 3.10+."
  exit 1
fi
echo "[OK] $($PY --version)"

# 2. venv
if [ ! -x ".venv/bin/python" ]; then
  echo "[..] Criando ambiente virtual (.venv)..."
  $PY -m venv .venv
fi
VENV_PY=".venv/bin/python"

# 3. deps
echo "[..] Instalando dependencias (rapido depois da 1a vez)..."
"$VENV_PY" -m pip install --upgrade pip >/dev/null 2>&1
"$VENV_PY" -m pip install -r requirements.txt
echo "[OK] Dependencias prontas."
echo

# 4. token na primeira vez
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "============================================"
  echo "   PRIMEIRO USO: COLE SEU TOKEN"
  echo "============================================"
  echo "Abrindo o .env no editor. Cole o token depois de DISCORD_TOKEN=, salve e feche."
  "${EDITOR:-nano}" .env
fi

# 5. rodar
echo "[..] Iniciando o bot... (Ctrl+C para parar)"
echo
"$VENV_PY" bot.py
