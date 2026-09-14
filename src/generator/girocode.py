"""
EPC-QR-Code (GiroCode) Generator for SEPA Credit Transfers (EPC069-12).
Generates official, standard-compliant QR Code SVGs for instant mobile banking scan.
"""

from decimal import Decimal
from pathlib import Path
from typing import Dict, Any, Optional
import qrcode
import qrcode.image.svg


def build_epc_payload(
    iban: str,
    bic: str,
    recipient: str,
    amount: float,
    reference: str = "",
    unstructured_text: str = ""
) -> str:
    """
    Constructs an EPC069-12 conformant GiroCode payload string.
    Lines:
    1: Service Tag: BCD
    2: Version: 002
    3: Character Set: 1 (UTF-8)
    4: Identification: SCT (SEPA Credit Transfer)
    5: BIC (optional in v002 for EEA, but recommended)
    6: Beneficiary Name (max 70 chars)
    7: IBAN (uppercase, no spaces)
    8: Amount in EUR (e.g. EUR123.45)
    9: Purpose Code (optional 4 chars)
    10: Structured Reference (RF... or ISO 11649)
    11: Unstructured Remittance Info (max 140 chars)
    12: Beneficiary to Originator Info (optional)
    """
    clean_iban = str(iban).replace(" ", "").upper()
    clean_bic = str(bic).replace(" ", "").upper() if bic else ""
    amt_str = f"EUR{amount:.2f}"
    clean_recipient = str(recipient).replace("\r", " ").replace("\n", " ").strip()[:70]
    
    # Determine remittance info (Structured RF... or Unstructured, max 140 chars)
    struct_ref = str(reference).replace("\r", "").replace("\n", "").strip()[:35] if (reference and str(reference).strip().upper().startswith("RF")) else ""
    unstruct_ref = str(unstructured_text).replace("\r", " ").replace("\n", " ").strip()[:140] if not struct_ref else ""
    if not struct_ref and not unstruct_ref and reference:
        unstruct_ref = str(reference).replace("\r", " ").replace("\n", " ").strip()[:140]

    lines = [
        "BCD",
        "002",
        "1",
        "SCT",
        clean_bic,
        clean_recipient,
        clean_iban,
        amt_str,
        "",          # Line 9: Purpose code (optional)
        struct_ref,  # Line 10: Structured Reference (optional)
        unstruct_ref,# Line 11: Unstructured Remittance text (optional)
        ""           # Line 12: Beneficiary to Originator Info (optional)
    ]
    
    # EPC069-12 specification rule:
    # "The last populated element must not be followed by any character or element separator."
    while lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines)


def generate_girocode_svg(
    data: Dict[str, Any],
    output_path: Path
) -> Optional[Path]:
    """
    Generates a GiroCode SVG file if seller bank and amount are valid.
    Returns the Path to the generated SVG or None if not applicable.
    """
    seller = data.get("seller", {})
    bank = seller.get("bank", {})
    inv = data.get("invoice", {})
    totals = data.get("totals", {})

    iban = bank.get("iban")
    if not iban:
        return None

    # Check payment means code (58 = SEPA credit transfer, or default)
    pay_code = str(inv.get("payment_means_code", "58"))
    if pay_code == "97": # Clearing / Marketplace internal payment
        return None

    bic = bank.get("bic", "")
    recipient = bank.get("holder") or seller.get("name", "")
    amount = float(totals.get("due_payable", totals.get("grand_total", 0.0)))
    if amount <= 0:
        return None

    ref = str(inv.get("payment_reference", inv.get("number", ""))).strip()
    if ref.upper().startswith("RF") and len(ref) <= 35:
        struct_ref = ref.upper()
        unstruct_text = ""
    else:
        struct_ref = ""
        unstruct_text = f"Rechnung {ref}" if not ref.lower().startswith("rechnung") else ref

    payload = build_epc_payload(
        iban=iban,
        bic=bic,
        recipient=recipient,
        amount=amount,
        reference=struct_ref,
        unstructured_text=unstruct_text
    )

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
        image_factory=qrcode.image.svg.SvgPathImage
    )
    qr.add_data(payload)
    qr.make(fit=True)

    img = qr.make_image()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        img.save(f)

    return output_path
