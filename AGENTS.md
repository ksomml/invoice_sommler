# AGENTS.md

## 1. Projektübersicht & Kontext

Dieses Projekt ist ein spezialisierter, modularer Rechnungs-Workspace für die freiberufliche Ingenieurtätigkeit von **Kevin Sommler** mit Schwerpunkt auf:
- **Humanoide Robotik** (Software-/Hardware-Entwicklung, Regelungstechnik, ROS2, Kinematik)
- **Embedded Systems** (Firmware, Mikrocontroller, Schaltungsdesign, Echtzeitsysteme)

### Hauptziel
Ein vollautomatisches, audit-sicheres und elegantes System zur Rechnungserstellung:
1. **PDF-Generierung via Typst**: Höchste typografische Qualität, modernes Engineering-Design, Einbindung von `logo.svg` oben rechts, saubere Tabellen (Stundensätze, Festpreise, Spesen, Meilensteine).
2. **E-Rechnung (EN16931-konform)**: Automatische Erstellung von maschinenlesbarem XML nach EN16931 (CII / CrossIndustryInvoice bzw. XRechnung 3.0 / ZUGFeRD / Factur-X) gemäß den aktuellen gesetzlichen Vorgaben zur E-Rechnungspflicht in Deutschland/EU.
3. **Single Source of Truth (SSOT)**: Sämtliche Rechnungs- und Kundendaten werden in strukturierten Datendateien (YAML/JSON/TOML) gepflegt. Typst-PDF und EN16931-XML werden synchron aus derselben Datenquelle generiert.

---

## 2. Initialer KI-Rollenprompt (Agent Role Prompt)

```text
Du bist ein erfahrener Lead Software Architect, E-Invoicing-Spezialist und Typst-Experte.
Deine Aufgabe ist es, einen professionellen, wartungsarmen und hochpräzisen Workspace für Rechnungen zu entwickeln und zu pflegen.

Halte dich stets an folgende Leitprinzipien:
1. Single Source of Truth (SSOT): Keine redundante Datenerfassung. Alle Daten (Stammdaten, Kunden, Positionen) liegen in sauberen Schema-Dateien.
2. EN16931 & XRechnung Konformität: Halte alle Geschäftsregeln (Business Rules BR-01 bis BR-65) strikt ein (Rundungen, BT-Felder, USt-Codes, Steuernummern, Leitweg-ID / BuyerReference, UN/ECE Einheiten wie 'HUR' für Stunden).
3. Modernes Typst Design: Nutze moderne Typst-Praktiken (Funktionen, Templates, typografische Hierarchien, Vektorgrafiken wie logo.svg) für ästhetisch ansprechende PDF-Rechnungen.
4. Struktur & Sauberkeit: Erstelle bei Bedarf neue Ordner, verschiebe Dateien sinnvoll und halte den Workspace stets übersichtlich und modular strukturiert.
5. Verlässlichkeit: Validiere Summen, Rundungen (kaufmännisch auf 2 Nachkommastellen) und XML-Strukturen automatisiert gegen XRechnung/EN16931 Schemata.
```

---

## 3. Architektur & Verzeichnisstruktur

Der Workspace ist wie folgt organisiert:

```plaintext
invoice_sommler/
├── .gitignore                 # Git-Ausschlussregeln für Caches, Temp-Dateien & IDEs
├── AGENTS.md                  # Projektkontext und KI-Richtlinien (dieses Dokument)
├── build.bat                  # Windows CMD Build-Skript
├── build.ps1                  # PowerShell Build-Skript (Standard für Windows)
├── build.sh                   # Linux/macOS Bash Build-Skript
├── assets/                    # Statische Assets (Logos, Schriftarten, Icons)
│   └── logo.svg               # Logo für Briefkopf (oben rechts)
├── config/                    # Eigene Stammdaten & globale Einstellungen
│   └── seller.yaml            # Kontaktdaten, Steuernummern, Bankverbindung (Kevin Sommler)
├── data/                      # Datenbasis (Single Source of Truth)
│   ├── clients/               # Kundenstammdaten (z.B. mybotshop.yaml)
│   └── invoices/              # Rechnungsdefinitionen (z.B. 2026-MBS-001.yaml)
├── templates/                 # Vorlagen
│   └── typst/                 # Typst-Templates für PDF-Erstellung
│       ├── invoice.typ        # Haupttemplate für Rechnungen
│       └── components/        # Modulare Typst-Bausteine (Header, Table, Payment, Footer)
├── src/                       # Python-basiertes CLI & Generator-Tooling
│   ├── generator/             # Logik: Summenberechnung, GiroCode, XML-, PDF- & Factur-X-Builder
│   │   ├── calculator.py
│   │   ├── girocode.py
│   │   ├── hybrid_builder.py
│   │   ├── pdf_builder.py
│   │   └── xml_builder.py
│   ├── validators/            # Validierung der Rechnungsdaten und EN16931-Regeln
│   │   └── validator.py
│   └── cli.py                 # Command-Line-Interface (Build-, Test-, Watch-Commands)
├── tests/                     # Testsuite für Berechnungen, GiroCode, XML & Hybrid-PDF
└── output/                    # Generierte Artefakte (PDFs & XMLs)
    └── 2026/
        ├── RE-MBS-2026-001.pdf  # Primäre Hybrid-E-Rechnung (PDF/A-3b mit eingebetteter xrechnung.xml)
        └── RE-MBS-2026-001.xml  # Standalone EN16931 / XRechnung 3.0 Datei
```

---

## 4. Rechnungs- und E-Rechnungsstandards

### Gesetzliche & Fachliche Anforderungen (Deutschland / EU)
- **Pflichtangaben nach § 14 UStG**:
  - Vollständiger Name und Anschrift von Leistendem und Leistungsempfänger (inkl. Land)
  - Steuernummer und/oder USt-IdNr.
  - Ausstellungsdatum, fortlaufende Rechnungsnummer (Kundenbezogener Nummernkreis: `RE-<KUNDE>-<JAHR>-<NUMMER>`)
  - Leistungszeitraum / Lieferdatum (`BillingSpecifiedPeriod` BG-14)
  - Menge, Einheit und Art der gelieferten Gegenstände bzw. Dienstleistungen
  - Nettoentgelt, Steuersatz (19%), Steuerbetrag, Bruttobetrag
- **EN16931 / XRechnung Spezifikation (CII - Cross Industry Invoice)**:
  - Syntax: `urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100`
  - Profil: `urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0`
  - Maßeinheiten nach UN/ECE Rec 20: `HUR` (Stunden), `DAY` (Tage), `C62` (Stück / Pauschale)
  - Zahlungsziel und Zahlungsarten nach UNTDED 4461 (Code `58` SEPA Credit Transfer)
  - Elektronische Käuferadresse nach Peppol / BT-49: `URIUniversalCommunication` (Schema `EM` für E-Mail)
  - Steueraufschlüsselung (BG-23): `ApplicableTradeTax` mit `CategoryCode` (`S`) und `RateApplicablePercent` (`19.00`)

---

## 5. Workflow für KI & Entwickler

1. **Kunden anlegen / prüfen**: YAML unter `data/clients/<kunde>.yaml` (z.B. mit `client_code: MBS` und `contact.email`).
2. **Rechnung anlegen**: YAML-Datei unter `data/invoices/<JAHR>-<KÜRZEL>-<NUMMER>.yaml` anlegen (z.B. `2026-MBS-001.yaml`).
3. **Bauen & Validieren**:
   ```powershell
   # Schneller Build mit Standard PowerShell-Skript:
   .\build.ps1 2026-MBS-001

   # Oder via Python CLI:
   py -m src.cli build 2026-MBS-001
   
   # Tests ausführen:
   py -m src.cli test
   ```
4. **Ergebnis in `output/<JAHR>/`**:
   - `RE-<KÜRZEL>-<JAHR>-<NUMMER>.pdf` (Hybride PDF/A-3b E-Rechnung mit Vektor-Logo, EPC-QR und eingebetteter `xrechnung.xml`)
   - `RE-<KÜRZEL>-<JAHR>-<NUMMER>.xml` (100% KoSIT-validierte reine EN16931 / XRechnung 3.0 Datei)

