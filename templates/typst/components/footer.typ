// Typst Footer Component for Invoices
// Inspired by examples/example-invoice.pdf with 3-column data, colored contact icons and sub-footer

#let footer-block(seller, inv, accent-color) = [
  #set text(size: 7pt, fill: rgb("#334155"))

  // Top separator line in accent color
  #line(length: 100%, stroke: 1pt + accent-color)
  #v(0.8mm)

  // 3-Column Metadata
  #grid(
    columns: (1.1fr, 1fr, 1.2fr),
    gutter: 8pt,
    [
      *#seller.name*\
      #seller.address.street\
      #seller.address.zip #seller.address.city
    ],
    [
      #if "vat_id" in seller.tax and seller.tax.vat_id != "" [*USt-IdNr.:* #seller.tax.vat_id\ ]
      #if "tax_number" in seller.tax and seller.tax.tax_number != "" [*Steuernr.:* #seller.tax.tax_number\ ]
      #if "tax_office" in seller.tax and seller.tax.tax_office != "" [*Finanzamt:* #seller.tax.tax_office\ ]
    ],
    [
      #if "bank" in seller [
        *IBAN:* #seller.bank.iban\
        *BIC / Swift:* #seller.bank.bic\
        *Bank:* #seller.bank.name
      ]
    ]
  )

  #v(0.6mm)
  // Accent separator line (exact same thickness as top line)
  #line(length: 100%, stroke: 1pt + accent-color)

  // Contact Info Row with Accent-Colored Emojis/Icons (Brief & Telefonhörer)
  #align(center)[
    #text(size: 7.2pt, fill: rgb("#475569"))[
      #if "email" in seller.contact and seller.contact.email != "" [
        #text(fill: accent-color, size: 8.5pt)[✉] #h(1.5mm) #seller.contact.email
      ]
      #if "email" in seller.contact and "phone" in seller.contact and seller.contact.email != "" and seller.contact.phone != "" [
        #h(8mm)
      ]
      #if "phone" in seller.contact and seller.contact.phone != "" [
        #text(fill: accent-color, size: 8.5pt)[📞] #h(1.5mm) #seller.contact.phone
      ]
    ]
  ]

  #v(1.4mm)
  // Sub-footer: Rechnungsnummer & Seitenzahl
  #align(center)[
    #text(size: 6.2pt, fill: rgb("#94A3B8"))[
      Rechnungs-Nr.: #inv.number
      #if "order_reference" in inv and inv.order_reference != "" [
        #h(3mm) | #h(3mm) Bestell-Nr.: #inv.order_reference
      ]
      #h(3mm) | #h(3mm) Seite #context { counter(page).display("1 von 1", both: true) }
    ]
  ]
]
