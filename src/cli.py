import argparse
import subprocess
import sys
import unittest
from pathlib import Path

# Ensure UTF-8 output in Windows terminals
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.generator.calculator import calculate_invoice_data, load_yaml
from src.generator.xml_builder import build_en16931_xml
from src.generator.pdf_builder import compile_typst_pdf
from src.generator.hybrid_builder import create_hybrid_pdf
from src.validators.validator import validate_invoice_data

BASE_DIR = Path(__file__).resolve().parent.parent

def get_invoice_path(invoice_id: str) -> Path:
    inv_id = invoice_id.removesuffix(".yaml")
    path = BASE_DIR / "data" / "invoices" / f"{inv_id}.yaml"
    if not path.exists():
        candidates = list((BASE_DIR / "data" / "invoices").glob(f"*{inv_id}*.yaml"))
        if candidates:
            return candidates[0]
        raise FileNotFoundError(f"Rechnungsdatei nicht gefunden: {path}")
    return path

def cmd_build(args):
    inv_files = []
    if args.invoice_id.lower() == "all":
        inv_files = sorted(list((BASE_DIR / "data" / "invoices").glob("*.yaml")))
    else:
        inv_files = [get_invoice_path(args.invoice_id)]

    print(f"\n==================================================")
    print(f"  Building {len(inv_files)} Invoice(s)")
    print(f"==================================================\n")

    for inv_path in inv_files:
        try:
            print(f"-> Verarbeite: {inv_path.name}")
            data = calculate_invoice_data(inv_path, BASE_DIR)
            
            # Validate
            is_valid, errors = validate_invoice_data(data)
            if not is_valid:
                print(f"   [WARNUNG] Validierungsfehler gefunden:")
                for err in errors:
                    print(f"     - {err}")
                if not args.force:
                    print("   Abbruch wegen Validierungsfehlern (nutze --force zum Erzwingen).\n")
                    continue
            else:
                print("   [OK] EN16931 & Geschäftsregeln validiert.")

            inv_obj = data["invoice"]
            year = str(inv_obj.get("date", "2026"))[:4]
            inv_num = inv_obj.get("number", inv_obj.get("id", "invoice"))
            
            out_dir = BASE_DIR / "output" / year
            out_dir.mkdir(parents=True, exist_ok=True)
            
            # 1. Generate XML
            xml_path = out_dir / f"RE-{inv_num}.xml" if not str(inv_num).startswith("RE-") else out_dir / f"{inv_num}.xml"
            xml_content = build_en16931_xml(data)
            with open(xml_path, "w", encoding="utf-8") as f:
                f.write(xml_content)
            print(f"   [XML] Erzeugt: {xml_path.relative_to(BASE_DIR)}")

            # 2. Generate PDF (Typst)
            pdf_path = out_dir / f"RE-{inv_num}.pdf" if not str(inv_num).startswith("RE-") else out_dir / f"{inv_num}.pdf"
            compile_typst_pdf(
                data=data,
                output_pdf_path=pdf_path,
                base_dir=BASE_DIR,
                xml_path=xml_path,
                create_hybrid=getattr(args, "hybrid", False)
            )
            print(f"   [PDF] Erzeugt: {pdf_path.relative_to(BASE_DIR)}")

            if getattr(args, "hybrid", False):
                hybrid_pdf_path = out_dir / f"{pdf_path.stem}_factur-x.pdf"
                print(f"   [HYBRID] Factur-X / ZUGFeRD erzeugt: {hybrid_pdf_path.relative_to(BASE_DIR)}")

            totals = data["totals"]
            print(f"   [SUMME] Netto: {totals['line_total_net']:.2f} EUR | MwSt: {totals['tax_total']:.2f} EUR | Brutto: {totals['grand_total']:.2f} EUR")
            print("   -> Erfolgreich abgeschlossen.\n")

        except Exception as e:
            print(f"   [FEHLER] {e}\n")
            if args.verbose:
                import traceback
                traceback.print_exc()

def cmd_validate(args):
    inv_path = get_invoice_path(args.invoice_id)
    print(f"\n-> Validiere: {inv_path.name}")
    try:
        data = calculate_invoice_data(inv_path, BASE_DIR)
        is_valid, errors = validate_invoice_data(data)
        if is_valid:
            print("   [ERFOLG] Alle Pflichtfelder und Berechnungen entsprechen den EN16931-Vorgaben.")
            totals = data["totals"]
            print(f"   Rechnungsnummer : {data['invoice'].get('number')}")
            print(f"   Kunde           : {data['client'].get('name')}")
            print(f"   Gesamtbetrag    : {totals['grand_total']:.2f} EUR")
        else:
            print("   [FEHLER] Gefundene Inkonsistenzen:")
            for err in errors:
                print(f"     - {err}")
    except Exception as e:
        print(f"   [FEHLER] {e}")

def cmd_list(args):
    inv_dir = BASE_DIR / "data" / "invoices"
    invoices = sorted(list(inv_dir.glob("*.yaml")))
    print(f"\n{'ID / DATEI':<20} {'DATUM':<12} {'KUNDE':<30} {'BETRAG (BRUTTO)':<16}")
    print("-" * 80)
    for inv_path in invoices:
        try:
            data = calculate_invoice_data(inv_path, BASE_DIR)
            inv = data["invoice"]
            client = data["client"]
            totals = data["totals"]
            print(f"{inv_path.stem:<20} {str(inv.get('date', '')):<12} {client.get('name', 'Unbekannt')[:28]:<30} {totals['grand_total']:>10.2f} EUR")
        except Exception as e:
            print(f"{inv_path.stem:<20} [Fehler beim Lesen: {e}]")
    print()

def cmd_new(args):
    inv_id = args.invoice_id.removesuffix(".yaml")
    out_path = BASE_DIR / "data" / "invoices" / f"{inv_id}.yaml"
    if out_path.exists() and not args.force:
        print(f"[FEHLER] Datei {out_path.name} existiert bereits. Nutze --force zum Überschreiben.")
        return

    template = f"""invoice:
  id: "{inv_id}"
  number: "RE-{inv_id}"
  type_code: "380"
  date: "2026-09-02"
  delivery_date: "2026-09-02"
  due_date: "2026-09-16"
  currency: "EUR"
  client: "robotics_innovations"
  payment_means_code: "58"
  payment_reference: "RE-{inv_id}"
  
  subject: "Rechnung RE-{inv_id}: Ingenieurdienstleistungen"
  intro_text: "Vielen Dank für Ihren Auftrag. Ich erlaube mir, folgende Leistungen in Rechnung zu stellen:"
  outro_text: ""
  
  items:
    - id: 1
      name: "Engineering Dienstleistung"
      description: "Entwicklungs- und Beratungsleistungen Humanoide Robotik / Embedded Systems"
      quantity: 10.0
      unit: "HUR"
      unit_name: "Std."
      unit_price_net: 125.00
      vat_rate: 19.00
      vat_category: "S"
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(template)
    print(f"[ERFOLG] Neue Rechnungsvorlage angelegt: {out_path.relative_to(BASE_DIR)}")

def cmd_watch(args):
    inv_path = get_invoice_path(args.invoice_id)
    print(f"\n[WATCH] Starte Typst Live-Watch für {inv_path.name}...")
    
    from src.generator.girocode import generate_girocode_svg
    import json

    # Calculate and prepare temp data
    data = calculate_invoice_data(inv_path, BASE_DIR)
    inv_obj = data["invoice"]
    year = str(inv_obj.get("date", "2026"))[:4]
    inv_num = inv_obj.get("number", inv_obj.get("id", "invoice"))
    
    out_dir = BASE_DIR / "output" / year
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / f"RE-{inv_num}.pdf" if not str(inv_num).startswith("RE-") else out_dir / f"{inv_num}.pdf"
    
    temp_dir = BASE_DIR / "output" / ".tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    data_to_render = dict(data)

    # Girocode
    giro_path = temp_dir / f"girocode_{inv_num}.svg"
    generated_giro = generate_girocode_svg(data, giro_path)
    if generated_giro and generated_giro.exists():
        data_to_render["girocode_path"] = "/" + generated_giro.relative_to(BASE_DIR).as_posix()
    else:
        data_to_render["girocode_path"] = None

    temp_data_file = temp_dir / f"data_{inv_num}.json"
    with open(temp_data_file, "w", encoding="utf-8") as f:
        json.dump(data_to_render, f, ensure_ascii=False, indent=2)
        
    root_rel_path = "/" + temp_data_file.relative_to(BASE_DIR).as_posix()
    template_path = BASE_DIR / "templates" / "typst" / "invoice.typ"
    
    cmd = [
        "typst", "watch",
        "--root", str(BASE_DIR),
        str(template_path),
        str(pdf_path),
        "--input", f"data_file={root_rel_path}"
    ]
    
    print(f"Typst beobachtet Änderungen an Templates. PDF-Ausgabe: {pdf_path.relative_to(BASE_DIR)}")
    print("Drücke Strg+C zum Beenden.\n")
    try:
        subprocess.run(cmd, cwd=str(BASE_DIR))
    except KeyboardInterrupt:
        print("\n[WATCH] Beendet.")
    finally:
        if temp_data_file.exists():
            try:
                temp_data_file.unlink()
            except Exception:
                pass
        if giro_path.exists():
            try:
                giro_path.unlink()
            except Exception:
                pass

def cmd_test(args):
    print("\n==================================================")
    print("  Führe Testsuite für Rechnungs-Workspace aus")
    print("==================================================\n")
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(BASE_DIR / "tests"), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2 if args.verbose else 1)
    result = runner.run(suite)
    if not result.wasSuccessful():
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Invoice Sommler - Typst & EN16931 E-Invoice CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # build
    p_build = subparsers.add_parser("build", help="Baut Typst PDF und EN16931 XML")
    p_build.add_argument("invoice_id", help="Rechnungs-ID (z.B. '2026-001' oder 'all')")
    p_build.add_argument("--hybrid", "--factur-x", action="store_true", help="Erzeugt hybrides ZUGFeRD / Factur-X PDF mit eingebettetem XML")
    p_build.add_argument("--force", action="store_true", help="Ignoriert Validierungswarnungen")
    p_build.add_argument("--verbose", "-v", action="store_true", help="Ausführliche Fehlerausgabe")
    p_build.set_defaults(func=cmd_build)

    # validate
    p_val = subparsers.add_parser("validate", help="Validiere Rechnungsdaten gegen EN16931 Regeln")
    p_val.add_argument("invoice_id", help="Rechnungs-ID")
    p_val.set_defaults(func=cmd_validate)

    # list
    p_list = subparsers.add_parser("list", help="Listet alle Rechnungen auf")
    p_list.set_defaults(func=cmd_list)

    # new
    p_new = subparsers.add_parser("new", help="Erstellt einen neuen Rechnungsentwurf")
    p_new.add_argument("invoice_id", help="Rechnungs-ID")
    p_new.add_argument("--force", action="store_true", help="Vorhandene Datei überschreiben")
    p_new.set_defaults(func=cmd_new)

    # watch
    p_watch = subparsers.add_parser("watch", help="Typst Live-Watch für Rechnungsansicht")
    p_watch.add_argument("invoice_id", help="Rechnungs-ID")
    p_watch.set_defaults(func=cmd_watch)

    # test
    p_test = subparsers.add_parser("test", help="Führt automatisierte Tests aus")
    p_test.add_argument("--verbose", "-v", action="store_true", help="Ausführliche Testausgabe")
    p_test.set_defaults(func=cmd_test)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
