@echo off
setlocal enabledelayedexpansion

set INVOICE_ID=%~1
if "%INVOICE_ID%"=="" set INVOICE_ID=2026-001

echo ==================================================
echo   Building Invoice: %INVOICE_ID%
echo ==================================================

where py >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
) else (
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python
    ) else (
        where python3 >nul 2>nul
        if %errorlevel% equ 0 (
            set PYTHON_CMD=python3
        ) else (
            echo [FEHLER] Python wurde nicht im PATH gefunden!
            pause
            exit /b 1
        )
    )
)

%PYTHON_CMD% -m src.cli build %INVOICE_ID% --hybrid

if %errorlevel% equ 0 (
    echo.
    echo [ERFOLG] Build abgeschlossen!
) else (
    echo.
    echo [FEHLER] Fehler beim Bauen der Rechnung!
)

endlocal
