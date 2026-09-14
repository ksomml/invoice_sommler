import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Dict, Any

RAM = "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
RSM = "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
UDT = "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100"

def fmt_2f(val: float) -> str:
    return f"{val:.2f}"

def fmt_date_102(d: str) -> str:
    if not d:
        return ""
    return str(d).replace("-", "")

def build_en16931_xml(data: Dict[str, Any]) -> str:
    seller = data["seller"]
    client = data["client"]
    inv = data["invoice"]
    totals = data["totals"]

    # Register namespaces
    ET.register_namespace("ram", RAM)
    ET.register_namespace("rsm", RSM)
    ET.register_namespace("udt", UDT)

    root = ET.Element(f"{{{RSM}}}CrossIndustryInvoice")

    # 1. ExchangedDocumentContext
    ctx = ET.SubElement(root, f"{{{RSM}}}ExchangedDocumentContext")
    proc = ET.SubElement(ctx, f"{{{RAM}}}BusinessProcessSpecifiedDocumentContextParameter")
    ET.SubElement(proc, f"{{{RAM}}}ID").text = "urn:fdc:peppol.eu:2017:poacc:billing:01:1.0"
    
    guideline = ET.SubElement(ctx, f"{{{RAM}}}GuidelineSpecifiedDocumentContextParameter")
    ET.SubElement(guideline, f"{{{RAM}}}ID").text = "urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0"

    # 2. ExchangedDocument
    doc = ET.SubElement(root, f"{{{RSM}}}ExchangedDocument")
    ET.SubElement(doc, f"{{{RAM}}}ID").text = str(inv.get("number", inv.get("id", "")))
    ET.SubElement(doc, f"{{{RAM}}}TypeCode").text = str(inv.get("type_code", "380"))
    
    issue_dt = ET.SubElement(doc, f"{{{RAM}}}IssueDateTime")
    dt_str = ET.SubElement(issue_dt, f"{{{UDT}}}DateTimeString")
    dt_str.set("format", "102")
    dt_str.text = fmt_date_102(inv.get("date", ""))

    # 3. SupplyChainTradeTransaction
    tx = ET.SubElement(root, f"{{{RSM}}}SupplyChainTradeTransaction")

    # 3.1 Line Items
    for item in inv.get("items", []):
        line = ET.SubElement(tx, f"{{{RAM}}}IncludedSupplyChainTradeLineItem")
        
        assoc = ET.SubElement(line, f"{{{RAM}}}AssociatedDocumentLineDocument")
        ET.SubElement(assoc, f"{{{RAM}}}LineID").text = str(item.get("id", 1))

        prod = ET.SubElement(line, f"{{{RAM}}}SpecifiedTradeProduct")
        if item.get("seller_assigned_id"):
            ET.SubElement(prod, f"{{{RAM}}}SellerAssignedID").text = str(item["seller_assigned_id"])
        ET.SubElement(prod, f"{{{RAM}}}Name").text = item.get("name", "")
        if item.get("description"):
            ET.SubElement(prod, f"{{{RAM}}}Description").text = item["description"]

        agreement = ET.SubElement(line, f"{{{RAM}}}SpecifiedLineTradeAgreement")
        net_price = ET.SubElement(agreement, f"{{{RAM}}}NetPriceProductTradePrice")
        ET.SubElement(net_price, f"{{{RAM}}}ChargeAmount").text = fmt_2f(item.get("unit_price_net", 0.0))

        delivery = ET.SubElement(line, f"{{{RAM}}}SpecifiedLineTradeDelivery")
        billed_qty = ET.SubElement(delivery, f"{{{RAM}}}BilledQuantity")
        billed_qty.set("unitCode", item.get("unit", "C62"))
        billed_qty.text = str(int(item["quantity"])) if item["quantity"] == int(item["quantity"]) else str(item["quantity"])

        settlement = ET.SubElement(line, f"{{{RAM}}}SpecifiedLineTradeSettlement")
        trade_tax = ET.SubElement(settlement, f"{{{RAM}}}ApplicableTradeTax")
        ET.SubElement(trade_tax, f"{{{RAM}}}TypeCode").text = "VAT"
        ET.SubElement(trade_tax, f"{{{RAM}}}CategoryCode").text = item.get("vat_category", "S")
        ET.SubElement(trade_tax, f"{{{RAM}}}RateApplicablePercent").text = fmt_2f(item.get("vat_rate", 19.0))

        line_sum = ET.SubElement(settlement, f"{{{RAM}}}SpecifiedTradeSettlementLineMonetarySummation")
        ET.SubElement(line_sum, f"{{{RAM}}}LineTotalAmount").text = fmt_2f(item.get("total_net", 0.0))

    # 3.2 Header Trade Agreement (Seller & Buyer)
    hdr_agreement = ET.SubElement(tx, f"{{{RAM}}}ApplicableHeaderTradeAgreement")
    
    buyer_ref = client.get("buyer_reference") or inv.get("buyer_reference") or "N/A"
    ET.SubElement(hdr_agreement, f"{{{RAM}}}BuyerReference").text = str(buyer_ref)

    # Seller Trade Party
    seller_party = ET.SubElement(hdr_agreement, f"{{{RAM}}}SellerTradeParty")
    ET.SubElement(seller_party, f"{{{RAM}}}Name").text = seller.get("name", "")
    
    s_contact_data = seller.get("contact", {})
    s_contact = ET.SubElement(seller_party, f"{{{RAM}}}DefinedTradeContact")
    ET.SubElement(s_contact, f"{{{RAM}}}PersonName").text = s_contact_data.get("person", seller.get("name", ""))
    if s_contact_data.get("phone"):
        tel = ET.SubElement(s_contact, f"{{{RAM}}}TelephoneUniversalCommunication")
        ET.SubElement(tel, f"{{{RAM}}}CompleteNumber").text = s_contact_data["phone"]
    if s_contact_data.get("email"):
        em = ET.SubElement(s_contact, f"{{{RAM}}}EmailURIUniversalCommunication")
        ET.SubElement(em, f"{{{RAM}}}URIID").text = s_contact_data["email"]

    s_addr = seller.get("address", {})
    s_postal = ET.SubElement(seller_party, f"{{{RAM}}}PostalTradeAddress")
    ET.SubElement(s_postal, f"{{{RAM}}}PostcodeCode").text = str(s_addr.get("zip", ""))
    ET.SubElement(s_postal, f"{{{RAM}}}LineOne").text = s_addr.get("street", "")
    ET.SubElement(s_postal, f"{{{RAM}}}CityName").text = s_addr.get("city", "")
    ET.SubElement(s_postal, f"{{{RAM}}}CountryID").text = s_addr.get("country_code", "DE")

    if s_contact_data.get("email"):
        uri_comm = ET.SubElement(seller_party, f"{{{RAM}}}URIUniversalCommunication")
        uri_id = ET.SubElement(uri_comm, f"{{{RAM}}}URIID")
        uri_id.set("schemeID", "EM")
        uri_id.text = s_contact_data["email"]

    s_tax = seller.get("tax", {})
    if s_tax.get("vat_id"):
        tax_reg_va = ET.SubElement(seller_party, f"{{{RAM}}}SpecifiedTaxRegistration")
        vat_id_elem = ET.SubElement(tax_reg_va, f"{{{RAM}}}ID")
        vat_id_elem.set("schemeID", "VA")
        vat_id_elem.text = s_tax["vat_id"]
    if s_tax.get("tax_number"):
        tax_reg_fc = ET.SubElement(seller_party, f"{{{RAM}}}SpecifiedTaxRegistration")
        tax_no_elem = ET.SubElement(tax_reg_fc, f"{{{RAM}}}ID")
        tax_no_elem.set("schemeID", "FC")
        tax_no_elem.text = s_tax["tax_number"]

    # Buyer Trade Party
    buyer_party = ET.SubElement(hdr_agreement, f"{{{RAM}}}BuyerTradeParty")
    ET.SubElement(buyer_party, f"{{{RAM}}}Name").text = client.get("name", "")

    b_contact_data = client.get("contact", {})
    if b_contact_data:
        b_contact = ET.SubElement(buyer_party, f"{{{RAM}}}DefinedTradeContact")
        if b_contact_data.get("person"):
            ET.SubElement(b_contact, f"{{{RAM}}}PersonName").text = b_contact_data["person"]
        if b_contact_data.get("phone"):
            b_tel = ET.SubElement(b_contact, f"{{{RAM}}}TelephoneUniversalCommunication")
            ET.SubElement(b_tel, f"{{{RAM}}}CompleteNumber").text = b_contact_data["phone"]
        if b_contact_data.get("email"):
            b_em = ET.SubElement(b_contact, f"{{{RAM}}}EmailURIUniversalCommunication")
            ET.SubElement(b_em, f"{{{RAM}}}URIID").text = b_contact_data["email"]

    b_addr = client.get("address", {})
    b_postal = ET.SubElement(buyer_party, f"{{{RAM}}}PostalTradeAddress")
    ET.SubElement(b_postal, f"{{{RAM}}}PostcodeCode").text = str(b_addr.get("zip", ""))
    ET.SubElement(b_postal, f"{{{RAM}}}LineOne").text = b_addr.get("street", "")
    if b_addr.get("additional"):
        ET.SubElement(b_postal, f"{{{RAM}}}LineTwo").text = b_addr["additional"]
    ET.SubElement(b_postal, f"{{{RAM}}}CityName").text = b_addr.get("city", "")
    ET.SubElement(b_postal, f"{{{RAM}}}CountryID").text = b_addr.get("country_code", "DE")

    if b_contact_data.get("email"):
        b_uri_comm = ET.SubElement(buyer_party, f"{{{RAM}}}URIUniversalCommunication")
        b_uri_id = ET.SubElement(b_uri_comm, f"{{{RAM}}}URIID")
        b_uri_id.set("schemeID", "EM")
        b_uri_id.text = b_contact_data["email"]

    b_tax = client.get("tax", {})
    if b_tax.get("vat_id"):
        b_tax_reg = ET.SubElement(buyer_party, f"{{{RAM}}}SpecifiedTaxRegistration")
        b_vat_id_elem = ET.SubElement(b_tax_reg, f"{{{RAM}}}ID")
        b_vat_id_elem.set("schemeID", "VA")
        b_vat_id_elem.text = b_tax["vat_id"]

    order_ref = client.get("order_reference") or inv.get("order_reference")
    if order_ref:
        order_elem = ET.SubElement(hdr_agreement, f"{{{RAM}}}BuyerOrderReferencedDocument")
        ET.SubElement(order_elem, f"{{{RAM}}}IssuerAssignedID").text = str(order_ref)

    # 3.3 Delivery
    delivery = ET.SubElement(tx, f"{{{RAM}}}ApplicableHeaderTradeDelivery")
    deliv_event = ET.SubElement(delivery, f"{{{RAM}}}ActualDeliverySupplyChainEvent")
    deliv_dt = ET.SubElement(deliv_event, f"{{{RAM}}}OccurrenceDateTime")
    deliv_dt_str = ET.SubElement(deliv_dt, f"{{{UDT}}}DateTimeString")
    deliv_dt_str.set("format", "102")
    
    # Use delivery date or end of delivery period
    deliv_date_val = inv.get("delivery_date")
    if not deliv_date_val and inv.get("delivery_period"):
        deliv_date_val = inv["delivery_period"].get("end")
    if not deliv_date_val:
        deliv_date_val = inv.get("date", "")
    deliv_dt_str.text = fmt_date_102(deliv_date_val)

    # 3.4 Settlement
    settlement = ET.SubElement(tx, f"{{{RAM}}}ApplicableHeaderTradeSettlement")
    ET.SubElement(settlement, f"{{{RAM}}}PaymentReference").text = str(inv.get("payment_reference", inv.get("number", "")))
    ET.SubElement(settlement, f"{{{RAM}}}InvoiceCurrencyCode").text = inv.get("currency", "EUR")

    pay_means = ET.SubElement(settlement, f"{{{RAM}}}SpecifiedTradeSettlementPaymentMeans")
    ET.SubElement(pay_means, f"{{{RAM}}}TypeCode").text = str(inv.get("payment_means_code", "58"))
    
    bank = seller.get("bank", {})
    if bank.get("iban"):
        cred_acc = ET.SubElement(pay_means, f"{{{RAM}}}PayeePartyCreditorFinancialAccount")
        ET.SubElement(cred_acc, f"{{{RAM}}}IBANID").text = str(bank["iban"]).replace(" ", "")
    if bank.get("bic"):
        cred_inst = ET.SubElement(pay_means, f"{{{RAM}}}PayeeSpecifiedCreditorFinancialInstitution")
        ET.SubElement(cred_inst, f"{{{RAM}}}BICID").text = str(bank["bic"]).replace(" ", "")

    # ApplicableTradeTax for each tax category
    for tax in totals.get("tax_breakdown", []):
        trade_tax = ET.SubElement(settlement, f"{{{RAM}}}ApplicableTradeTax")
        ET.SubElement(trade_tax, f"{{{RAM}}}CalculatedAmount").text = fmt_2f(tax["amount"])
        ET.SubElement(trade_tax, f"{{{RAM}}}TypeCode").text = "VAT"
        ET.SubElement(trade_tax, f"{{{RAM}}}BasisAmount").text = fmt_2f(tax["basis"])
        ET.SubElement(trade_tax, f"{{{RAM}}}CategoryCode").text = tax.get("category", "S")
        ET.SubElement(trade_tax, f"{{{RAM}}}RateApplicablePercent").text = fmt_2f(tax["rate"])

    # Payment terms / due date
    if inv.get("due_date"):
        pay_terms = ET.SubElement(settlement, f"{{{RAM}}}SpecifiedTradePaymentTerms")
        due_dt = ET.SubElement(pay_terms, f"{{{RAM}}}DueDateDateTime")
        due_dt_str = ET.SubElement(due_dt, f"{{{UDT}}}DateTimeString")
        due_dt_str.set("format", "102")
        due_dt_str.text = fmt_date_102(inv["due_date"])

    # Monetary summation
    mon_sum = ET.SubElement(settlement, f"{{{RAM}}}SpecifiedTradeSettlementHeaderMonetarySummation")
    ET.SubElement(mon_sum, f"{{{RAM}}}LineTotalAmount").text = fmt_2f(totals["line_total_net"])
    ET.SubElement(mon_sum, f"{{{RAM}}}ChargeTotalAmount").text = "0.00"
    ET.SubElement(mon_sum, f"{{{RAM}}}AllowanceTotalAmount").text = "0.00"
    ET.SubElement(mon_sum, f"{{{RAM}}}TaxBasisTotalAmount").text = fmt_2f(totals["tax_basis_total"])
    
    tax_total_elem = ET.SubElement(mon_sum, f"{{{RAM}}}TaxTotalAmount")
    tax_total_elem.set("currencyID", inv.get("currency", "EUR"))
    tax_total_elem.text = fmt_2f(totals["tax_total"])

    ET.SubElement(mon_sum, f"{{{RAM}}}GrandTotalAmount").text = fmt_2f(totals["grand_total"])
    ET.SubElement(mon_sum, f"{{{RAM}}}DuePayableAmount").text = fmt_2f(totals["due_payable"])

    # Pretty-print
    rough_string = ET.tostring(root, encoding="utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")
