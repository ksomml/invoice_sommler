import unittest
from decimal import Decimal
from pathlib import Path
from src.generator.calculator import calculate_invoice_data, round_money

BASE_DIR = Path(__file__).resolve().parent.parent

class TestCalculator(unittest.TestCase):
    def test_round_money(self):
        self.assertEqual(round_money(Decimal("15.685")), Decimal("15.69"))
        self.assertEqual(round_money(Decimal("15.684")), Decimal("15.68"))
        self.assertEqual(round_money(Decimal("0.00")), Decimal("0.00"))

    def test_calculate_2026_001(self):
        inv_path = BASE_DIR / "data" / "invoices" / "2026-001.yaml"
        data = calculate_invoice_data(inv_path, BASE_DIR)
        
        self.assertIn("seller", data)
        self.assertIn("client", data)
        self.assertIn("invoice", data)
        self.assertIn("totals", data)
        
        totals = data["totals"]
        # Pos 1: 32 * 125 = 4000.00
        # Pos 2: 18 * 125 = 2250.00
        # Pos 3: 1 * 450 = 450.00
        # Line total = 6700.00
        # Tax (19%) = 1273.00
        # Grand total = 7973.00
        self.assertEqual(totals["line_total_net"], 6700.00)
        self.assertEqual(totals["tax_total"], 1273.00)
        self.assertEqual(totals["grand_total"], 7973.00)
        self.assertEqual(totals["due_payable"], 7973.00)

    def test_calculate_100(self):
        inv_path = BASE_DIR / "data" / "invoices" / "100.yaml"
        data = calculate_invoice_data(inv_path, BASE_DIR)
        
        totals = data["totals"]
        # Net: 15.69, Tax 19%: 2.98, Grand: 18.67
        self.assertEqual(totals["line_total_net"], 15.69)
        self.assertEqual(totals["tax_total"], 2.98)
        self.assertEqual(totals["grand_total"], 18.67)

if __name__ == "__main__":
    unittest.main()
