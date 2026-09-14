<#
.SYNOPSIS
    Builds Typst PDF, EN16931 XML, and Factur-X Hybrid PDF for invoices.
.EXAMPLE
    .\build.ps1
    .\build.ps1 2026-001
    .\build.ps1 all
#>
param (
    [string]$InvoiceId = "2026-MBS-001",
    [switch]$Force,
    [switch]$NoHybrid
)

# Determine Python command
$PythonCmd = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonCmd = "py"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PythonCmd = "python3"
} else {
    Write-Error "Python wurde nicht gefunden! Bitte installiere Python 3.10+."
    exit 1
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$CliArgs = @("-m", "src.cli", "build", $InvoiceId)
if ($NoHybrid) {
    $CliArgs += "--no-hybrid"
}
if ($Force) {
    $CliArgs += "--force"
}

Write-Host "-> Starte Rechnungs-Build für '$InvoiceId' mit $PythonCmd..." -ForegroundColor Cyan
& $PythonCmd @CliArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host "[ERFOLG] Build abgeschlossen! Ausgabedateien liegen unter output/" -ForegroundColor Green
} else {
    Write-Host "[FEHLER] Build fehlgeschlagen mit Exit-Code $LASTEXITCODE" -ForegroundColor Red
}
exit $LASTEXITCODE
