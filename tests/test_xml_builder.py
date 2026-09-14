import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from src.generator.calculator import calculate_invoice_data
from src.generator.xml_builder import build_en16931_xml

BASE_DIR = Path(__file__).resolve().parent.parent

class TestXmlBuilder(unittest.TestCase):
    def test_xml_structure_2026_001(self):
        inv_path = BASE_DIR / "data" / "invoices" / "2026-001.yaml"
        data = calculate_invoice_data(inv_path, BASE_DIR)
        xml_str = build_en16931_xml(data)
        
        root = ET.fromstring(xml_str)
        # Check root tag ends with CrossIndustryInvoice
        self.assertTrue(root.tag.endswith("CrossIndustryInvoice"))
        
        # Check namespaces
        self.assertIn("urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100", root.tag)
        
        # Check Guideline / XRechnung Profile ID
        guideline_elem = root.find(".//{*}GuidelineSpecifiedDocumentContextParameter/{*}ID")
        self.assertIsNotNone(guideline_elem)
        self.assertEqual(guideline_elem.text, "urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0")

        # Check Seller
        seller_name = root.find(".//{*}SellerTradeParty/{*}Name")
        self.assertEqual(seller_name.text, "Kevin Sommler")

        # Check Grand Total
        grand_total = root.find(".//{*}SpecifiedTradeSettlementHeaderMonetarySummation/{*}GrandTotalAmount")
        self.assertEqual(grand_total.text, "7973.00")

    def test_xml_structure_100(self):
        inv_path = BASE_DIR / "data" / "invoices" / "100.yaml"
        data = calculate_invoice_data(inv_path, BASE_DIR)
        xml_str = build_en16931_xml(data)
        
        root = ET.fromstring(xml_str)
        buyer_ref = root.find(".//{*}ApplicableHeaderTradeAgreement/{*}BuyerReference")
        self.assertEqual(buyer_ref.text, "rainer7966")

        tax_total = root.find(".//{*}SpecifiedTradeSettlementHeaderMonetarySummation/{*}TaxTotalAmount")
        self.assertEqual(tax_total.text, "2.98")

if __name__ == "__main__":
    unittest.main()
