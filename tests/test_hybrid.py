import unittest
from pathlib import Path

import facturx
from pypdf import PdfWriter

from src.generator.hybrid_builder import create_hybrid_pdf

BASE_DIR = Path(__file__).resolve().parent.parent

class TestHybridBuilder(unittest.TestCase):
    def test_create_hybrid_pdf(self):
        temp_dir = BASE_DIR / "output" / ".tmp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        dummy_pdf = temp_dir / "dummy_base.pdf"
        output_pdf = temp_dir / "dummy_hybrid.pdf"

        # Write dummy PDF
        writer = PdfWriter()
        writer.add_blank_page(width=200, height=200)
        with open(dummy_pdf, "wb") as f:
            writer.write(f)

        real_xml = BASE_DIR / "output" / "2026" / "RE-MBS-2026-001.xml"
        if not real_xml.exists():
            real_xml = BASE_DIR / "examples" / "example-e-invoice.xml"

        try:
            res_path = create_hybrid_pdf(
                input_pdf_path=dummy_pdf,
                xml_path=real_xml,
                output_pdf_path=output_pdf
            )
            self.assertTrue(res_path.exists())

            # Verify attachment in generated PDF
            with open(output_pdf, "rb") as f:
                filename, xml_bytes = facturx.get_facturx_xml_from_pdf(f.read(), check_xsd=False)
                self.assertEqual(filename, "factur-x.xml")
                self.assertGreater(len(xml_bytes), 100)

        finally:
            if dummy_pdf.exists(): dummy_pdf.unlink()
            if output_pdf.exists(): output_pdf.unlink()

if __name__ == "__main__":
    unittest.main()
