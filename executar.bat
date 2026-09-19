@echo off
title Automação de Flashcards Anki
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" gui.py
) else (
    python gui.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERRO] Ocorreu um erro ao executar a aplicacao.
    pause
)
