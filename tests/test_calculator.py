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

    def test_calculate_2026_mbs_001(self):
        inv_path = BASE_DIR / "data" / "invoices" / "2026-MBS-001.yaml"
        data = calculate_invoice_data(inv_path, BASE_DIR)

        self.assertIn("seller", data)
        self.assertIn("client", data)
        self.assertIn("invoice", data)
        self.assertIn("totals", data)

        totals = data["totals"]
        self.assertEqual(totals["line_total_net"], 1080.00)
        self.assertEqual(totals["tax_total"], 205.20)
        self.assertEqual(totals["grand_total"], 1285.20)
        self.assertEqual(totals["due_payable"], 1285.20)
        self.assertEqual(data["client"]["name"], "MYBOTSHOP GmbH")
        self.assertEqual(data["invoice"]["number"], "RE-MBS-2026-001")

if __name__ == "__main__":
    unittest.main()
