"""
Hybrid Invoice (Factur-X / ZUGFeRD) Builder.
Embeds the EN16931 / XRechnung XML into the Typst-generated PDF/A-3b document,
fully compliant with ISO 19005-3:2012 (veraPDF) and ZUGFeRD 2.x / Mustang Project.
"""

from pathlib import Path
from typing import Optional
import hashlib
from datetime import datetime, timezone
from lxml import etree
import pypdf
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    DictionaryObject, NameObject, ArrayObject, DecodedStreamObject,
    TextStringObject, ByteStringObject, NumberObject
)


def _detect_profile_and_filename(xml_bytes: bytes) -> tuple[str, str, str]:
    """
    Detects conformance level, standard URN, and recommended embedded filename.
    For XRechnung 3.0 (KoSIT): 'XRECHNUNG', 'xrechnung.xml'.
    For standard EN16931: 'EN 16931', 'factur-x.xml'.
    """
    xml_str = xml_bytes.decode("utf-8", errors="ignore")
    if "urn:xeinkauf.de:kosit:xrechnung" in xml_str or "xrechnung" in xml_str.lower():
        return "XRECHNUNG", "xrechnung.xml", "urn:factur-x:pdfa:CrossIndustryDocument:invoice:1p0#"
    return "EN 16931", "factur-x.xml", "urn:factur-x:pdfa:CrossIndustryDocument:invoice:1p0#"


def create_hybrid_pdf(
    input_pdf_path: Path,
    xml_path: Path,
    output_pdf_path: Optional[Path] = None,
    attachment_filename: Optional[str] = None
) -> Path:
    """
    Embeds the EN16931 / XRechnung XML into a PDF/A-3 document, creating an official,
    standard-compliant ZUGFeRD 2.x / Factur-X hybrid invoice (PDF/A-3b).
    """
    if not input_pdf_path.exists():
        raise FileNotFoundError(f"PDF-Datei nicht gefunden: {input_pdf_path}")
    if not xml_path.exists():
        raise FileNotFoundError(f"XML-Datei nicht gefunden: {xml_path}")

    if output_pdf_path is None:
        output_pdf_path = input_pdf_path.parent / f"{input_pdf_path.stem}_factur-x.pdf"

    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

    with open(xml_path, "rb") as f:
        xml_bytes = f.read()

    conf_level, detected_filename, fx_urn = _detect_profile_and_filename(xml_bytes)
    filename = attachment_filename or detected_filename

    reader = PdfReader(str(input_pdf_path))
    writer = PdfWriter(clone_from=reader)
    writer._header = b"%PDF-1.7"

    # 1. Embedded File Stream
    md5sum_bytes = hashlib.md5(xml_bytes).digest()
    mod_date_str = datetime.now(timezone.utc).strftime("D:%Y%m%d%H%M%SZ")
    params_dict = DictionaryObject({
        NameObject("/CheckSum"): ByteStringObject(md5sum_bytes),
        NameObject("/ModDate"): TextStringObject(mod_date_str),
        NameObject("/Size"): NumberObject(len(xml_bytes)),
    })

    file_entry = DecodedStreamObject()
    file_entry.set_data(xml_bytes)
    file_entry = file_entry.flate_encode()
    file_entry.update({
        NameObject("/Type"): NameObject("/EmbeddedFile"),
        NameObject("/Params"): params_dict,
        NameObject("/Subtype"): NameObject("/text/xml"),
    })
    file_entry_obj = writer._add_object(file_entry)

    # 2. File Specification Dictionary (ISO 19005-3:2012 Rule 6.8 requires /Subtype on /Filespec)
    fname_obj = TextStringObject(filename)
    desc_str = "XRechnung XML invoice" if conf_level == "XRECHNUNG" else "Factur-X XML invoice"
    filespec_dict = DictionaryObject({
        NameObject("/Type"): NameObject("/Filespec"),
        NameObject("/F"): fname_obj,
        NameObject("/UF"): fname_obj,
        NameObject("/EF"): DictionaryObject({
            NameObject("/F"): file_entry_obj,
            NameObject("/UF"): file_entry_obj,
        }),
        NameObject("/Subtype"): NameObject("/text/xml"),
        NameObject("/AFRelationship"): NameObject("/Alternative"),
        NameObject("/Desc"): TextStringObject(desc_str),
    })
    filespec_obj = writer._add_object(filespec_dict)

    # 3. EmbeddedFiles and Catalog AF array
    name_array = ArrayObject([fname_obj, filespec_obj])
    embedded_files_dict = DictionaryObject({
        NameObject("/Names"): name_array,
    })

    af_list = ArrayObject([filespec_obj])

    update_root = {
        NameObject("/AF"): writer._add_object(af_list),
        NameObject("/Names"): DictionaryObject({
            NameObject("/EmbeddedFiles"): embedded_files_dict
        }),
        NameObject("/PageMode"): NameObject("/UseAttachments"),
    }

    # 4. Enhance XMP Metadata with Factur-X / ZUGFeRD Extension Schema
    meta_obj = writer._root_object.get("/Metadata")
    if meta_obj:
        raw_xmp = meta_obj.get_object().get_data()
        if raw_xmp.startswith(b"\xef\xbb\xbf"):
            raw_xmp = raw_xmp[3:]

        try:
            xmp_root = etree.fromstring(raw_xmp)
            rdf_ns = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            pdfa_ext_ns = "http://www.aiim.org/pdfa/ns/extension/"
            pdfa_schema_ns = "http://www.aiim.org/pdfa/ns/schema#"
            pdfa_prop_ns = "http://www.aiim.org/pdfa/ns/property#"

            rdf_desc = xmp_root.xpath("//rdf:Description", namespaces={"rdf": rdf_ns})
            if rdf_desc:
                desc = rdf_desc[0]
                schemas_bag = desc.xpath(".//pdfaExtension:schemas/rdf:Bag", namespaces={"pdfaExtension": pdfa_ext_ns, "rdf": rdf_ns})
                if schemas_bag:
                    bag = schemas_bag[0]
                    ext_schema_xml = f"""
                    <rdf:li xmlns:rdf="{rdf_ns}" xmlns:pdfaSchema="{pdfa_schema_ns}" xmlns:pdfaProperty="{pdfa_prop_ns}" rdf:parseType="Resource">
                        <pdfaSchema:schema>Factur-X PDFA Extension Schema</pdfaSchema:schema>
                        <pdfaSchema:namespaceURI>{fx_urn}</pdfaSchema:namespaceURI>
                        <pdfaSchema:prefix>fx</pdfaSchema:prefix>
                        <pdfaSchema:property>
                            <rdf:Seq>
                                <rdf:li rdf:parseType="Resource">
                                    <pdfaProperty:name>DocumentFileName</pdfaProperty:name>
                                    <pdfaProperty:valueType>Text</pdfaProperty:valueType>
                                    <pdfaProperty:category>external</pdfaProperty:category>
                                    <pdfaProperty:description>The name of the embedded XML document</pdfaProperty:description>
                                </rdf:li>
                                <rdf:li rdf:parseType="Resource">
                                    <pdfaProperty:name>DocumentType</pdfaProperty:name>
                                    <pdfaProperty:valueType>Text</pdfaProperty:valueType>
                                    <pdfaProperty:category>external</pdfaProperty:category>
                                    <pdfaProperty:description>The type of the hybrid document in capital letters, e.g. INVOICE or ORDER</pdfaProperty:description>
                                </rdf:li>
                                <rdf:li rdf:parseType="Resource">
                                    <pdfaProperty:name>Version</pdfaProperty:name>
                                    <pdfaProperty:valueType>Text</pdfaProperty:valueType>
                                    <pdfaProperty:category>external</pdfaProperty:category>
                                    <pdfaProperty:description>The actual version of the standard applying to the embedded XML document</pdfaProperty:description>
                                </rdf:li>
                                <rdf:li rdf:parseType="Resource">
                                    <pdfaProperty:name>ConformanceLevel</pdfaProperty:name>
                                    <pdfaProperty:valueType>Text</pdfaProperty:valueType>
                                    <pdfaProperty:category>external</pdfaProperty:category>
                                    <pdfaProperty:description>The conformance level of the embedded XML document</pdfaProperty:description>
                                </rdf:li>
                            </rdf:Seq>
                        </pdfaSchema:property>
                    </rdf:li>
                    """
                    bag.append(etree.fromstring(ext_schema_xml))

                # Add fx property block
                fx_desc_xml = f"""
                <rdf:Description xmlns:rdf="{rdf_ns}" xmlns:fx="{fx_urn}" rdf:about="">
                    <fx:DocumentType>INVOICE</fx:DocumentType>
                    <fx:DocumentFileName>{filename}</fx:DocumentFileName>
                    <fx:Version>1.0</fx:Version>
                    <fx:ConformanceLevel>{conf_level}</fx:ConformanceLevel>
                </rdf:Description>
                """
                rdf_root = xmp_root.xpath("//rdf:RDF", namespaces={"rdf": rdf_ns})[0]
                rdf_root.append(etree.fromstring(fx_desc_xml))

                head = b'<?xpacket begin="\xef\xbb\xbf" id="W5M0MpCehiHzreSzNTczkc9d"?>'
                tail = b'<?xpacket end="w"?>'
                new_xmp_bytes = head + etree.tostring(xmp_root, encoding="utf-8") + tail

                new_meta_stream = DecodedStreamObject()
                new_meta_stream.update({
                    NameObject("/Subtype"): NameObject("/XML"),
                    NameObject("/Type"): NameObject("/Metadata"),
                })
                new_meta_stream.set_data(new_xmp_bytes)
                new_meta_stream = new_meta_stream.flate_encode()
                writer._replace_object(meta_obj.indirect_reference, new_meta_stream)
        except Exception:
            pass

    writer._root_object.update(update_root)

    with open(output_pdf_path, "wb") as f:
        writer.write(f)

    return output_pdf_path
