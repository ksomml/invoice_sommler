#!/usr/bin/env bash
# ==============================================================================
# Linux / macOS Build Script for Invoice Sommler
# Builds Typst PDF, EN16931 XML, and Factur-X Hybrid PDF
#
# Usage:
#   ./build.sh              # Builds default invoice (2026-001)
#   ./build.sh 2026-001     # Builds specific invoice
#   ./build.sh all          # Builds all invoices
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

INVOICE_ID="${1:-2026-MBS-001}"

# Detect Python
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
elif command -v py &>/dev/null; then
    PYTHON_CMD="py"
else
    echo "[FEHLER] Python 3 wurde nicht gefunden! Bitte installiere Python 3.10+." >&2
    exit 1
fi

echo "=================================================="
echo "  Building Invoice: ${INVOICE_ID} (using ${PYTHON_CMD})"
echo "=================================================="

"${PYTHON_CMD}" -m src.cli build "${INVOICE_ID}" --hybrid "${@:2}"

echo ""
echo "[ERFOLG] Build abgeschlossen! Ausgabedateien liegen unter output/"
