import unittest
from src.validators.validator import validate_invoice_data

class TestValidator(unittest.TestCase):
    def test_valid_data(self):
        valid_data = {
            "seller": {
                "name": "Kevin Sommler",
                "address": {"street": "Friedrich-Ebert-Str. 12", "zip": "15344", "city": "Strausberg", "country_code": "DE"},
                "tax": {"vat_id": "DE463781564"},
                "bank": {"iban": "DE32100101783678168888"}
            },
            "client": {
                "name": "Robotics Innovations GmbH",
                "address": {"street": "Tech Park 4", "zip": "10115", "city": "Berlin", "country_code": "DE"}
            },
            "invoice": {
                "number": "RE-2026-001",
                "date": "2026-09-02",
                "currency": "EUR",
                "items": [
                    {"id": 1, "name": "Entwicklung", "quantity": 10.0, "unit_price_net": 100.0, "total_net": 1000.0, "vat_rate": 19.0}
                ]
            },
            "totals": {
                "line_total_net": 1000.0,
                "tax_total": 190.0,
                "grand_total": 1190.0
            }
        }
        is_valid, errors = validate_invoice_data(valid_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_missing_seller_iban(self):
        invalid_data = {
            "seller": {
                "name": "Kevin Sommler",
                "address": {"street": "Friedrich-Ebert-Str. 12", "zip": "15344", "city": "Strausberg", "country_code": "DE"},
                "tax": {"vat_id": "DE463781564"},
                "bank": {}
            },
            "client": {
                "name": "Robotics Innovations GmbH",
                "address": {"street": "Tech Park 4", "zip": "10115", "city": "Berlin", "country_code": "DE"}
            },
            "invoice": {
                "number": "RE-2026-001",
                "date": "2026-09-02",
                "currency": "EUR",
                "items": [{"id": 1, "name": "Item", "quantity": 1, "unit_price_net": 100}]
            },
            "totals": {"line_total_net": 100.0, "tax_total": 19.0, "grand_total": 119.0}
        }
        is_valid, errors = validate_invoice_data(invalid_data)
        self.assertFalse(is_valid)
        self.assertTrue(any("BR-49" in e for e in errors))

    def test_calculation_mismatch(self):
        invalid_data = {
            "seller": {
                "name": "Kevin Sommler",
                "address": {"street": "Friedrich-Ebert-Str. 12", "zip": "15344", "city": "Strausberg", "country_code": "DE"},
                "tax": {"vat_id": "DE463781564"},
                "bank": {"iban": "DE32100101783678168888"}
            },
            "client": {
                "name": "Robotics Innovations GmbH",
                "address": {"street": "Tech Park 4", "zip": "10115", "city": "Berlin", "country_code": "DE"}
            },
            "invoice": {
                "number": "RE-2026-001",
                "date": "2026-09-02",
                "currency": "EUR",
                "items": [{"id": 1, "name": "Item", "quantity": 1, "unit_price_net": 100}]
            },
            "totals": {
                "line_total_net": 100.0,
                "tax_total": 19.0,
                "grand_total": 150.0 # Incorrect grand total
            }
        }
        is_valid, errors = validate_invoice_data(invalid_data)
        self.assertFalse(is_valid)
        self.assertTrue(any("BR-CO-15" in e for e in errors))

if __name__ == "__main__":
    unittest.main()
