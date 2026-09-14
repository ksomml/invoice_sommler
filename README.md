# Rechnungs-Workspace (Typst & EN16931 E-Rechnung)

Eleganter, audit-sicherer und automatisierter Rechnungs-Workspace für freiberufliche Ingenieurdienstleistungen (**Humanoide Robotik** & **Embedded Systems**).

Das System erzeugt aus einer gemeinsamen Datenquelle (**Single Source of Truth** via YAML):
1. **Druckfertige PDF-Rechnungen** über [Typst](https://typst.app/) mit modernem Engineering-Design, `logo.png` und automatischem **EPC-QR-Code (GiroCode)**.
2. **Gesetzeskonforme E-Rechnungen (.xml)** nach dem europäischen Standard **EN16931 (CrossIndustryInvoice / XRechnung 3.0)**.
3. **Hybride E-Rechnungen (Factur-X / ZUGFeRD)** mit direkt im PDF eingebettetem EN16931-XML (`--hybrid`).

---

## 📁 Verzeichnisstruktur

```plaintext
invoice_sommler/
├── build.ps1                  # 1-Klick Build-Skript für PowerShell (Windows)
├── build.bat                  # 1-Klick Build-Skript für CMD / Batch (Windows)
├── build.sh                   # 1-Klick Build-Skript für Linux / macOS
├── AGENTS.md                  # KI-Kontext & Rollenprompts
├── plan.md                    # Detaillierter Architektur- & Implementierungsplan
├── README.md                  # Projekt-Dokumentation & Schnellanleitung
├── assets/                    # Statische Dateien & Grafiken (logo.png)
├── config/                    # Eigene Stammdaten (seller.yaml)
├── data/                      # Datenbasis (SSOT)
│   ├── clients/               # Kundenstammdaten (z.B. robotics_innovations.yaml)
│   └── invoices/              # Rechnungsentwürfe (z.B. 2026-001.yaml)
├── templates/                 # Vorlagen
│   └── typst/                 # Modulare Typst-Templates (invoice.typ & components/)
├── src/                       # Python CLI, XML-Generator, GiroCode & Validatoren
├── tests/                     # Automatisierte Unittests
├── output/                    # Fertige PDFs und XMLs (nach Jahr sortiert)
└── examples/                  # Ursprüngliche Referenzdateien
```

---

## 🚀 1-Klick-Build (Schnellstart)

### Unter Windows (PowerShell oder CMD):
```powershell
# Baut standardmäßig die Rechnung 2026-001
.\build.ps1

# Oder eine bestimmte Rechnung:
.\build.ps1 2026-001

# Oder alle Rechnungen:
.\build.ps1 all
```
*Alternativ in der Eingabeaufforderung / per Doppelklick:*
```cmd
build.bat 2026-001
```

### Unter Linux / macOS:
```bash
# Ausführbar machen (einmalig):
chmod +x build.sh

# Rechnung kompilieren:
./build.sh 2026-001

# Oder alle Rechnungen:
./build.sh all
```

---

## 🛠️ Erweiterte CLI-Befehle

### 1. Alle Rechnungen auflisten
```powershell
py -m src.cli list
```

### 2. Neue Rechnung anlegen
Erstellt einen neuen Rechnungsentwurf unter `data/invoices/<ID>.yaml`:
```powershell
py -m src.cli new 2026-002
```

### 3. Rechnung validieren
Prüft Pflichtfelder, Steuersätze, Pflicht-Adressen und mathematische Konsistenz nach EN16931 (BR-01 bis BR-65):
```powershell
py -m src.cli validate 2026-001
```

### 4. Live-Vorschau während des Bearbeitens (`watch`)
Startet die Typst Live-Kompilierung bei jeder Dateiänderung:
```powershell
py -m src.cli watch 2026-001
```

### 5. Automatisierte Tests ausführen
Führt die Unittests für Berechnungen, XML-Konformität, GiroCode und Validierung aus:
```powershell
py -m src.cli test
```

---

## ⚙️ Voraussetzungen

- **Python 3.10+** (`PyYAML`, `PyPDF2`, `Pillow`)
- **Typst** (Version 0.12+)
