import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from src.generator.calculator import calculate_invoice_data
from src.generator.xml_builder import build_en16931_xml

BASE_DIR = Path(__file__).resolve().parent.parent

class TestXmlBuilder(unittest.TestCase):
    def test_xml_structure_2026_mbs_001(self):
        inv_path = BASE_DIR / "data" / "invoices" / "2026-MBS-001.yaml"
        data = calculate_invoice_data(inv_path, BASE_DIR)
        xml_str = build_en16931_xml(data)

        root = ET.fromstring(xml_str)
        self.assertTrue(root.tag.endswith("CrossIndustryInvoice"))
        self.assertIn("urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100", root.tag)

        # Check ID
        doc_id = root.find(".//{*}ExchangedDocument/{*}ID")
        self.assertEqual(doc_id.text, "RE-MBS-2026-001")

        # Check Seller
        seller_name = root.find(".//{*}SellerTradeParty/{*}Name")
        self.assertEqual(seller_name.text, "Kevin Sommler")

        # Check Buyer
        buyer_name = root.find(".//{*}BuyerTradeParty/{*}Name")
        self.assertEqual(buyer_name.text, "MYBOTSHOP GmbH")

        # Check Grand Total
        grand_total = root.find(".//{*}SpecifiedTradeSettlementHeaderMonetarySummation/{*}GrandTotalAmount")
        self.assertEqual(grand_total.text, "1285.20")

        # Check VAT Breakdown (BT-118, BT-119, BT-116, BT-117)
        tax_category = root.find(".//{*}ApplicableHeaderTradeSettlement/{*}ApplicableTradeTax/{*}CategoryCode")
        self.assertIsNotNone(tax_category)
        self.assertEqual(tax_category.text, "S")

        tax_rate = root.find(".//{*}ApplicableHeaderTradeSettlement/{*}ApplicableTradeTax/{*}RateApplicablePercent")
        self.assertIsNotNone(tax_rate)
        self.assertEqual(tax_rate.text, "19.00")

        tax_basis = root.find(".//{*}ApplicableHeaderTradeSettlement/{*}ApplicableTradeTax/{*}BasisAmount")
        self.assertEqual(tax_basis.text, "1080.00")

        tax_amount = root.find(".//{*}ApplicableHeaderTradeSettlement/{*}ApplicableTradeTax/{*}CalculatedAmount")
        self.assertEqual(tax_amount.text, "205.20")

        # Check Buyer Electronic Address (BT-49)
        buyer_uri = root.find(".//{*}BuyerTradeParty/{*}URIUniversalCommunication/{*}URIID")
        self.assertIsNotNone(buyer_uri)
        self.assertEqual(buyer_uri.text, "info@mybotshop.de")
        self.assertEqual(buyer_uri.attrib.get("schemeID"), "EM")

        # Check Billing Specified Period (BG-14)
        period_start = root.find(".//{*}BillingSpecifiedPeriod/{*}StartDateTime/{*}DateTimeString")
        period_end = root.find(".//{*}BillingSpecifiedPeriod/{*}EndDateTime/{*}DateTimeString")
        self.assertIsNotNone(period_start)
        self.assertIsNotNone(period_end)
        self.assertEqual(period_start.text, "20260915")
        self.assertEqual(period_end.text, "20260917")

if __name__ == "__main__":
    unittest.main()
