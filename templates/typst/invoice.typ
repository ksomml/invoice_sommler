// Typst Invoice Template for Freelance Engineering (Kevin Sommler)
// Modular Architecture with EN16931 & GiroCode Integration
// Accent Color: #c18f39 with DIN 5008 fold/punch marks

#import "components/header.typ": header-block
#import "components/metadata.typ": metadata-block
#import "components/table.typ": items-table, totals-block
#import "components/payment.typ": payment-block
#import "components/footer.typ": footer-block

#let accent-color = rgb("#c18f39")

#let fold-marks() = {
  let mark-stroke = 0.35pt + rgb("#94A3B8")
  // Page is A4: 210mm x 297mm
  // Fold mark 1 at 99mm (left and right)
  place(top + left, dx: 0mm, dy: 99mm, line(length: 5mm, stroke: mark-stroke))
  place(top + left, dx: 205mm, dy: 99mm, line(length: 5mm, stroke: mark-stroke))
  
  // Center punch mark at 148.5mm (left)
  place(top + left, dx: 0mm, dy: 148.5mm, line(length: 7mm, stroke: mark-stroke))
  
  // Fold mark 2 at 198mm (left and right)
  place(top + left, dx: 0mm, dy: 198mm, line(length: 5mm, stroke: mark-stroke))
  place(top + left, dx: 205mm, dy: 198mm, line(length: 5mm, stroke: mark-stroke))
}

#let format-euro(amount) = {
  if amount == none { return "0,00 €" }
  let str-val = str(calc.round(amount, digits: 2))
  let parts = str-val.split(".")
  let int-part = parts.at(0)
  let dec-part = if parts.len() > 1 { parts.at(1) } else { "00" }
  while dec-part.len() < 2 { dec-part = dec-part + "0" }
  
  // Format thousands with dot
  let formatted-int = ""
  let count = 0
  let is-neg = int-part.starts-with("-")
  let digits = if is-neg { int-part.slice(1) } else { int-part }
  
  for i in range(digits.len() - 1, -1, step: -1) {
    if count > 0 and calc.rem(count, 3) == 0 {
      formatted-int = "." + formatted-int
    }
    formatted-int = digits.at(i) + formatted-int
    count += 1
  }
  if is-neg { formatted-int = "-" + formatted-int }
  
  formatted-int + "," + dec-part + " €"
}

#let format-qty(qty) = {
  if qty == none { return "0" }
  let str-val = str(calc.round(qty, digits: 2))
  let parts = str-val.split(".")
  let int-part = parts.at(0)
  let dec-part = if parts.len() > 1 { parts.at(1) } else { "" }
  if dec-part == "0" or dec-part == "" {
    int-part
  } else {
    int-part + "," + dec-part
  }
}

#let format-date(d) = {
  if d == none or d == "" { return "" }
  let parts = str(d).split("-")
  if parts.len() == 3 {
    parts.at(2) + "." + parts.at(1) + "." + parts.at(0)
  } else {
    str(d)
  }
}

#let invoice-doc(data) = [
  #let seller = data.seller
  #let client = data.client
  #let inv = data.invoice
  #let totals = data.totals
  #let logo-path = data.at("logo_path", default: "/assets/logo.png")
  #let girocode-path = data.at("girocode_path", default: none)

  #set document(
    title: "Rechnung " + inv.number + " - " + seller.name,
    author: seller.name,
  )

  #set page(
    paper: "a4",
    margin: (top: 18mm, bottom: 42mm, left: 20mm, right: 20mm),
    background: fold-marks(),
    footer: footer-block(seller, inv, accent-color)
  )

  #set text(
    font: ("Arial", "Liberation Sans", "Segoe UI", "Segoe UI Symbol"),
    size: 8.8pt,
    fill: rgb("#1A202C"),
    lang: "de",
  )

  // 1. Header (Sender, Recipient, Logo)
  #header-block(seller, client, logo-path)

  #v(1.5mm)

  // 2. Metadata Block (Right aligned)
  #metadata-block(inv, client, format-date, accent-color)

  #v(2mm)
  #line(length: 100%, stroke: 1.2pt + accent-color)
  #v(1.2mm)

  // 3. Subject / Heading
  #text(size: 12.5pt, weight: "bold", fill: rgb("#0F172A"))[
    #if "subject" in inv and inv.subject != "" [
      #inv.subject
    ] else [
      RECHNUNG #inv.number
    ]
  ]
  #v(0.3mm)

  // 4. Intro Text
  #if "intro_text" in inv and inv.intro_text != "" and inv.intro_text != none [
    #text(size: 8.2pt, fill: rgb("#334155"))[#inv.intro_text]
    #v(1.5mm)
  ]

  // 5. Items Table
  #items-table(inv.items, format-qty, format-euro, accent-color)

  #v(1.2mm)

  // 6. Totals Breakdown
  #totals-block(totals, format-euro, accent-color)

  #v(2mm)

  // 7. Payment Terms & optional GiroCode
  #payment-block(inv, totals, girocode-path, format-euro, format-date, accent-color)
]

// Dynamic data loader
#let raw-data = if sys.inputs.keys().contains("data_file") {
  json(sys.inputs.data_file)
} else {
  (
    seller: (
      name: "Kevin Sommler",
      profession: "Freiberuflicher Ingenieur",
      specialization: "Humanoide Robotik & Embedded Systems",
      address: (street: "Friedrich-Ebert-Straße 12", zip: "15344", city: "Strausberg", country: "Deutschland"),
      contact: (email: "sommler@live.de", phone: "01784440117"),
      tax: (vat_id: "DE463781564", tax_number: "064/275/03524", tax_office: "Finanzamt Strausberg"),
      bank: (name: "Revolut Bank UAB", iban: "DE32100101783678168888", bic: "REVODEB2", holder: "Kevin Sommler")
    ),
    client: (
      name: "Robotics Innovations GmbH",
      trade_name: "Robotics Innovations Lab",
      address: (street: "Technologiepark 4", additional: "Gebäude B, 3. OG", zip: "10115", city: "Berlin", country: "Deutschland"),
      contact: (person: "Dr. Anna Weber"),
      buyer_reference: "ROB-2026-PO-9912",
      order_reference: "PO-2026-081"
    ),
    invoice: (
      number: "RE-2026-001",
      date: "2026-09-02",
      delivery_period: (start: "2026-08-01", end: "2026-08-31"),
      due_date: "2026-09-16",
      subject: "Rechnung RE-2026-001: Entwicklungsleistungen Humanoide Robotik",
      intro_text: "Vielen Dank für die angenehme Zusammenarbeit. Für die erbrachten Ingenieur- und Entwicklungsleistungen im Projekt 'Humanoide Kinematik & Embedded ROS2 Steuerung' erlaube ich mir, folgende Positionen in Rechnung zu stellen:",
      outro_text: "",
      items: (
        (id: 1, name: "Entwicklung ROS2 Controller für Humanoide Kinematik", description: "Inverse Kinematik und Trajektorienplanung", quantity: 32.0, unit_name: "Std.", unit_price_net: 125.00, total_net: 4000.00, vat_rate: 19.0),
        (id: 2, name: "Firmware-Entwicklung BLDC Motorcontroller", description: "Echtzeit FOC Regelung auf STM32H7", quantity: 18.0, unit_name: "Std.", unit_price_net: 125.00, total_net: 2250.00, vat_rate: 19.0),
        (id: 3, name: "Elektronik-Prototyping & Prüfstandsaufbau", description: "Inbetriebnahme Teststand", quantity: 1.0, unit_name: "Pauschale", unit_price_net: 450.00, total_net: 450.00, vat_rate: 19.0),
      )
    ),
    totals: (
      line_total_net: 6700.00,
      tax_basis_total: 6700.00,
      tax_total: 1273.00,
      grand_total: 7973.00,
      due_payable: 7973.00,
      tax_breakdown: (
        (rate: 19.0, basis: 6700.00, amount: 1273.00, category: "S"),
      )
    ),
    logo_path: "/assets/logo.png",
    girocode_path: none
  )
}

#invoice-doc(raw-data)
