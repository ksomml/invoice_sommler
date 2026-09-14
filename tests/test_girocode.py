import unittest
from pathlib import Path

from src.generator.girocode import build_epc_payload, generate_girocode_svg

BASE_DIR = Path(__file__).resolve().parent.parent

class TestGirocode(unittest.TestCase):
    def test_epc_payload_format(self):
        payload = build_epc_payload(
            iban="DE32100101783678168888",
            bic="REVODEB2",
            recipient="Kevin Sommler",
            amount=7973.00,
            reference="",
            unstructured_text="Rechnung RE-2026-001"
        )
        lines = payload.split("\n")
        self.assertEqual(lines[0], "BCD")
        self.assertEqual(lines[1], "002")
        self.assertEqual(lines[2], "1")
        self.assertEqual(lines[3], "SCT")
        self.assertEqual(lines[4], "REVODEB2")
        self.assertEqual(lines[5], "Kevin Sommler")
        self.assertEqual(lines[6], "DE32100101783678168888")
        self.assertEqual(lines[7], "EUR7973.00")
        self.assertIn("Rechnung RE-2026-001", lines[10])

    def test_svg_generation(self):
        dummy_data = {
            "seller": {"name": "Kevin Sommler", "bank": {"iban": "DE32100101783678168888", "bic": "REVODEB2", "holder": "Kevin Sommler"}},
            "invoice": {"number": "RE-2026-001", "payment_means_code": "58"},
            "totals": {"due_payable": 7973.00}
        }
        test_out = BASE_DIR / "output" / ".tmp" / "test_giro_out.svg"
        generated = generate_girocode_svg(dummy_data, test_out)
        self.assertIsNotNone(generated)
        self.assertTrue(test_out.exists())
        content = test_out.read_text(encoding="utf-8")
        self.assertIn("<svg", content)
        if test_out.exists():
            test_out.unlink()

if __name__ == "__main__":
    unittest.main()
