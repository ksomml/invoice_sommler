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

Der Workspace wird wie folgt organisiert:

```plaintext
invoice_sommler/
├── AGENTS.md                  # Projektkontext und KI-Richtlinien (dieses Dokument)
├── plan.md                    # Detaillierter Implementierungsplan und Roadmap
├── assets/                    # Statische Assets (Logos, Schriftarten, Icons)
│   └── logo.svg               # Logo für Briefkopf (oben rechts)
├── config/                    # Eigene Stammdaten & globale Einstellungen
│   └── seller.yaml            # Kontaktdaten, Steuernummern, Bankverbindung (Kevin Sommler)
├── data/                      # Datenbasis (SSOT)
│   ├── clients/               # Kundenstammdaten (z.B. client_a.yaml, client_b.yaml)
│   └── invoices/              # Rechnungsdefinitionen (z.B. 2026-001.yaml, 2026-002.yaml)
├── templates/                 # Vorlagen
│   ├── typst/                 # Typst-Templates für PDF-Erstellung
│   │   ├── invoice.typ        # Haupttemplate für Rechnungen
│   │   └── components/        # Modulare Typst-Bausteine (Header, Table, Footer)
│   └── xml/                   # Templates / Generatoren für EN16931 CII XML
├── src/                       # Python-basiertes CLI & Generator-Tooling
│   ├── generator/             # Logik für Datenvalidierung, Summenberechnung, Typst- & XML-Rendering
│   ├── validators/            # Validierung der Rechnungsdaten und XML gegen EN16931
│   └── cli.py                 # Command-Line-Interface (z.B. 'py -m src.cli build 2026-001')
├── output/                    # Generierte Artefakte (PDFs, XMLs, Kombinations-PDFs)
│   └── 2026/
└── examples/                  # Referenzbeispiele (Archivierte Originaldateien)
    ├── example-invoice.pdf
    └── example-e-invoice.xml
```

---

## 4. Rechnungs- und E-Rechnungsstandards

### Gesetzliche & Fachliche Anforderungen (Deutschland / EU)
- **Pflichtangaben nach § 14 UStG**:
  - Vollständiger Name und Anschrift von Leistendem und Leistungsempfänger
  - Steuernummer und/oder USt-IdNr.
  - Ausstellungsdatum, fortlaufende Rechnungsnummer
  - Zeitpunkt / Zeitraum der Leistung
  - Menge und Art der gelieferten Gegenstände bzw. Umfang und Art der sonstigen Leistung
  - Nettoentgelt, Steuersatz (z.B. 19%), Steuerbetrag, Bruttobetrag
- **EN16931 / XRechnung Spezifikation (CII - Cross Industry Invoice)**:
  - Syntax: `urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100`
  - Profil: `urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0`
  - Maßeinheiten nach UN/ECE Rec 20: `HUR` (Stunden / Hours), `DAY` (Tage), `C62` (Stück / Pieces)
  - Zahlungsziel und Zahlungsarten nach UNTDED 4461 (z.B. Code `58` SEPA Credit Transfer oder `97` Clearing)

---

## 5. Workflow für KI & Entwickler

1. **Neue Rechnung anlegen**: Eine YAML-Datei unter `data/invoices/<JAHR>-<NUMMER>.yaml` anlegen.
2. **Kunden referenzieren**: Entweder aus `data/clients/<KUNDE>.yaml` oder inline definieren.
3. **Bauen & Validieren**:
   ```powershell
   py -m src.cli build 2026-001
   ```
4. **Ergebnis**:
   - `output/<JAHR>/RE-<NUMMER>.pdf` (Typst gerendert mit Vektor-Logo)
   - `output/<JAHR>/RE-<NUMMER>.xml` (Validierte EN16931 / XRechnung 3.0 Datei)
   - Optional: `output/<JAHR>/RE-<NUMMER>_factur-x.pdf` (Hybrid-Rechnung ZUGFeRD / Factur-X)
