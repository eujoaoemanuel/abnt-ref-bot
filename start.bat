@echo off
setlocal enabledelayedexpansion
title ABNT Ref Bot
cd /d "%~dp0"

echo ============================================
echo    ABNT Ref Bot - inicializador
echo ============================================
echo.

REM --- 1. localizar o Python ---
set "PY="
python --version >nul 2>&1 && set "PY=python"
if not defined PY (
    py --version >nul 2>&1 && set "PY=py"
)
if not defined PY (
    echo [ERRO] Python nao encontrado no sistema.
    echo.
    echo Instale o Python 3.10 ou superior em:
    echo    https://www.python.org/downloads/
    echo IMPORTANTE: marque "Add Python to PATH" durante a instalacao.
    echo.
    pause
    exit /b 1
)
echo [OK] Python encontrado:
%PY% --version
echo.

REM --- 2. criar o ambiente virtual na primeira vez ---
if not exist ".venv\Scripts\python.exe" (
    echo [..] Criando ambiente virtual ^(.venv^)...
    %PY% -m venv .venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar o ambiente virtual.
        pause
        exit /b 1
    )
)
set "VENV_PY=.venv\Scripts\python.exe"

REM --- 3. instalar/atualizar dependencias ---
echo [..] Instalando dependencias ^(rapido depois da 1a vez^)...
"%VENV_PY%" -m pip install --upgrade pip >nul 2>&1
"%VENV_PY%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar as dependencias.
    pause
    exit /b 1
)
echo [OK] Dependencias prontas.
echo.

REM --- 4. configurar o token na primeira vez ---
if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo ============================================
    echo    PRIMEIRO USO: COLE SEU TOKEN
    echo ============================================
    echo Vou abrir o arquivo .env no Bloco de Notas.
    echo Cole o token do bot depois de  DISCORD_TOKEN=
    echo Depois salve ^(Ctrl+S^) e feche o Bloco de Notas.
    echo.
    pause
    notepad .env
    echo.
)

REM --- 5. subir o bot ---
echo [..] Iniciando o bot... ^(feche esta janela ou Ctrl+C para parar^)
echo.
"%VENV_PY%" bot.py

echo.
echo Bot encerrado.
pause
