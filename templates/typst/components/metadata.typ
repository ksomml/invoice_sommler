// Typst Metadata Block Component for Invoices

#let metadata-block(inv, client, format-date, accent-color) = [
  #align(right)[
    #block(width: 88mm)[
      #set text(size: 8.5pt)
      #let meta-rows = (
        [*Rechnungsnummer:*], [#text(weight: "bold", fill: rgb("#0F172A"))[#inv.number]],
        [*Rechnungsdatum:*], [#format-date(inv.date)],
      )
      #if "delivery_period" in inv and inv.delivery_period != none [
        #meta-rows.push([*Leistungszeitraum:*])
        #meta-rows.push([#format-date(inv.delivery_period.start) -- #format-date(inv.delivery_period.end)])
      ] else if "delivery_date" in inv and inv.delivery_date != none and inv.delivery_date != "" [
        #meta-rows.push([*Leistungsdatum:*])
        #meta-rows.push([#format-date(inv.delivery_date)])
      ]
      #if "due_date" in inv and inv.due_date != none and inv.due_date != "" [
        #meta-rows.push([*Zahlbar bis:*])
        #meta-rows.push([#format-date(inv.due_date)])
      ]
      #if "buyer_reference" in client and client.buyer_reference != "" [
        #meta-rows.push([*Ihre Referenz:*])
        #meta-rows.push([#client.buyer_reference])
      ]
      #if "order_reference" in client and client.order_reference != "" [
        #meta-rows.push([*Bestell-Nr.:*])
        #meta-rows.push([#client.order_reference])
      ]
      #grid(
        columns: (auto, 1fr),
        row-gutter: 4.5pt,
        column-gutter: 10pt,
        align: (left, right),
        ..meta-rows
      )
    ]
  ]
]
