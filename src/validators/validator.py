from typing import Dict, Any, List, Tuple
from decimal import Decimal

def validate_invoice_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    
    seller = data.get("seller", {})
    client = data.get("client", {})
    inv = data.get("invoice", {})
    totals = data.get("totals", {})

    # 1. Seller Checks (EN16931 BR-01 .. BR-08)
    if not seller.get("name"):
        errors.append("[BR-02] Verkäufername (seller.name) fehlt.")
    s_addr = seller.get("address", {})
    if not s_addr.get("street") or not s_addr.get("zip") or not s_addr.get("city") or not s_addr.get("country_code"):
        errors.append("[BR-08] Vollständige Verkäuferadresse (street, zip, city, country_code) erforderlich.")
    
    s_tax = seller.get("tax", {})
    if not s_tax.get("vat_id") and not s_tax.get("tax_number"):
        errors.append("[BR-CO-09] Mindestens USt-IdNr. oder Steuernummer des Verkäufers erforderlich.")

    s_bank = seller.get("bank", {})
    if not s_bank.get("iban"):
        errors.append("[BR-49] IBAN des Verkäufers (seller.bank.iban) fehlt.")

    # 2. Buyer Checks
    if not client.get("name"):
        errors.append("[BR-07] Käufername (client.name) fehlt.")
    b_addr = client.get("address", {})
    if not b_addr.get("street") or not b_addr.get("zip") or not b_addr.get("city") or not b_addr.get("country_code"):
        errors.append("[BR-11] Vollständige Käuferadresse (street, zip, city, country_code) erforderlich.")

    # 3. Invoice Header Checks
    if not inv.get("number") and not inv.get("id"):
        errors.append("[BR-01] Rechnungsnummer (invoice.number) fehlt.")
    if not inv.get("date"):
        errors.append("[BR-03] Rechnungsdatum (invoice.date) fehlt.")
    if not inv.get("currency"):
        errors.append("[BR-05] Währungscode (invoice.currency) fehlt.")

    # 4. Line Items Checks
    items = inv.get("items", [])
    if not items:
        errors.append("[BR-16] Rechnung muss mindestens eine Position enthalten.")

    for idx, item in enumerate(items, start=1):
        if not item.get("name"):
            errors.append(f"[BR-25] Position {idx}: Artikel-/Leistungsname fehlt.")
        if item.get("quantity", 0) <= 0:
            errors.append(f"[BR-22] Position {idx}: Menge muss größer als 0 sein.")
        if item.get("unit_price_net") is None:
            errors.append(f"[BR-27] Position {idx}: Nettopreis fehlt.")

    # 5. Mathematical Check
    if totals:
        calc_grand = Decimal(str(totals.get("line_total_net", 0))) + Decimal(str(totals.get("tax_total", 0)))
        declared_grand = Decimal(str(totals.get("grand_total", 0)))
        if abs(calc_grand - declared_grand) > Decimal("0.01"):
            errors.append(f"[BR-CO-15] Rechenfehler: Nettobetrag + Steuer ({calc_grand}) != Bruttobetrag ({declared_grand})")

    return (len(errors) == 0, errors)
