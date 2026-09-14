"""
Hybrid Invoice (Factur-X / ZUGFeRD) Builder.
Embeds the EN16931 XML into the Typst-generated PDF using the official factur-x library.
"""

from pathlib import Path
from typing import Optional
import facturx


def create_hybrid_pdf(
    input_pdf_path: Path,
    xml_path: Path,
    output_pdf_path: Optional[Path] = None,
    attachment_filename: str = "factur-x.xml"
) -> Path:
    """
    Embeds the EN16931 / XRechnung XML into the PDF, creating an official,
    standard-compliant Factur-X / ZUGFeRD hybrid electronic invoice (PDF/A-3).
    """
    if not input_pdf_path.exists():
        raise FileNotFoundError(f"PDF-Datei nicht gefunden: {input_pdf_path}")
    if not xml_path.exists():
        raise FileNotFoundError(f"XML-Datei nicht gefunden: {xml_path}")

    if output_pdf_path is None:
        output_pdf_path = input_pdf_path.parent / f"{input_pdf_path.stem}_factur-x.pdf"

    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

    # Use official facturx library to embed XML and generate valid PDF/A-3 catalog & XMP metadata
    facturx.generate_from_file(
        pdf_file=str(input_pdf_path),
        xml=str(xml_path),
        flavor="factur-x",
        level="en16931",
        check_xsd=False,
        output_pdf_file=str(output_pdf_path)
    )

    return output_pdf_path
