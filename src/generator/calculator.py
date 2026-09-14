from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import yaml
from typing import Dict, Any, List

def round_money(val: Decimal) -> Decimal:
    return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Datei nicht gefunden: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def calculate_invoice_data(
    invoice_path: Path,
    base_dir: Path
) -> Dict[str, Any]:
    invoice_data = load_yaml(invoice_path)
    inv = invoice_data.get("invoice", {})
    
    # Load seller
    seller_path = base_dir / "config" / "seller.yaml"
    seller_data = load_yaml(seller_path).get("seller", {})
    
    # Load client (either reference or inline)
    client_ref = inv.get("client")
    if isinstance(client_ref, str):
        client_file = base_dir / "data" / "clients" / f"{client_ref}.yaml"
        client_data = load_yaml(client_file)
    elif isinstance(client_ref, dict):
        client_data = client_ref
    else:
        client_data = {}

    # Calculate line items
    items: List[Dict[str, Any]] = []
    line_total_net = Decimal("0.00")
    
    tax_buckets: Dict[str, Dict[str, Any]] = {}
    
    for idx, item in enumerate(inv.get("items", []), start=1):
        qty = Decimal(str(item.get("quantity", 1)))
        
        # Determine net unit price
        if "unit_price_net" in item:
            unit_price_net = Decimal(str(item["unit_price_net"]))
        elif "unit_price_gross" in item:
            vat_rate = Decimal(str(item.get("vat_rate", 19.0)))
            gross = Decimal(str(item["unit_price_gross"]))
            unit_price_net = round_money(gross / (Decimal("1.00") + (vat_rate / Decimal("100.00"))))
        else:
            unit_price_net = Decimal("0.00")
            
        line_net = round_money(qty * unit_price_net)
        line_total_net += line_net
        
        vat_rate = Decimal(str(item.get("vat_rate", 19.0)))
        vat_cat = item.get("vat_category", "S") # 'S' for Standard
        
        bucket_key = f"{vat_cat}_{vat_rate}"
        if bucket_key not in tax_buckets:
            tax_buckets[bucket_key] = {
                "category": vat_cat,
                "rate": float(vat_rate),
                "basis": Decimal("0.00"),
                "amount": Decimal("0.00")
            }
        tax_buckets[bucket_key]["basis"] += line_net
        
        items.append({
            "id": item.get("id", idx),
            "seller_assigned_id": item.get("seller_assigned_id"),
            "name": item.get("name", f"Position {idx}"),
            "description": item.get("description", ""),
            "quantity": float(qty),
            "unit": item.get("unit", "C62"),
            "unit_name": item.get("unit_name", "Stk."),
            "unit_price_net": float(unit_price_net),
            "total_net": float(line_net),
            "vat_rate": float(vat_rate),
            "vat_category": vat_cat
        })
        
    tax_total = Decimal("0.00")
    tax_breakdown = []
    for bucket in tax_buckets.values():
        basis = bucket["basis"]
        rate = Decimal(str(bucket["rate"]))
        calculated_tax = round_money(basis * (rate / Decimal("100.00")))
        tax_total += calculated_tax
        tax_breakdown.append({
            "category": bucket["category"],
            "rate": bucket["rate"],
            "basis": float(basis),
            "amount": float(calculated_tax)
        })
        
    grand_total = line_total_net + tax_total
    due_payable = grand_total
    
    totals = {
        "line_total_net": float(line_total_net),
        "tax_basis_total": float(line_total_net),
        "tax_total": float(tax_total),
        "grand_total": float(grand_total),
        "due_payable": float(due_payable),
        "tax_breakdown": tax_breakdown
    }
    
    # Clean invoice dict
    invoice_dict = dict(inv)
    invoice_dict["items"] = items
    
    logo_path = seller_data.get("logo", "/assets/logo.png")
    if not logo_path.startswith("/"):
        logo_path = "/" + logo_path.lstrip("/")

    return {
        "seller": seller_data,
        "client": client_data,
        "invoice": invoice_dict,
        "totals": totals,
        "logo_path": logo_path
    }
