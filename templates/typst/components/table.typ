// Typst Items Table & Totals Block Components
// Accent color: #f2d180

#let items-table(items, format-qty, format-euro, accent-color) = [
  #let table-rows = ()
  
  // Header
  #table-rows.push([*Pos.*])
  #table-rows.push([*Beschreibung & Spezifikation*])
  #table-rows.push(align(center)[*Menge*])
  #table-rows.push(align(right)[*Einzelpreis*])
  #table-rows.push(align(center)[*MwSt.*])
  #table-rows.push(align(right)[*Gesamtpreis*])

  #for item in items {
    let qty-str = format-qty(item.quantity) + " " + item.at("unit_name", default: "Stk.")
    let unit-price = format-euro(item.unit_price_net)
    let line-total = format-euro(item.total_net)
    let vat-str = str(item.vat_rate) + " %"

    table-rows.push([#item.id])
    table-rows.push([
      *#item.name*\
      #if "description" in item and item.description != "" and item.description != none [
        #text(size: 8pt, fill: rgb("#64748B"))[#item.description]
      ]
    ])
    table-rows.push(align(center)[#qty-str])
    table-rows.push(align(right)[#unit-price])
    table-rows.push(align(center)[#vat-str])
    table-rows.push(align(right)[*#line-total*])
  }

  #table(
    columns: (24pt, 1fr, 74pt, 66pt, 36pt, 68pt),
    stroke: (x, y) => if y == 0 {
      (bottom: 1.5pt + accent-color)
    } else if y < items.len() {
      (bottom: 0.4pt + rgb("#E2E8F0"))
    } else {
      none
    },
    fill: (col, row) => if row == 0 { rgb("#FCFAF3") } else if calc.even(row) { rgb("#FDFBF7") } else { none },
    inset: (x: 6pt, y: 7pt),
    align: (col, row) => (
      if col == 0 { center + top }
      else if col == 1 { left + top }
      else if col == 2 { center + top }
      else if col == 3 { right + top }
      else if col == 4 { center + top }
      else { right + top }
    ),
    ..table-rows
  )
]

#let totals-block(totals, format-euro, accent-color) = [
  #align(right)[
    #block(width: 85mm)[
      #set text(size: 9pt)
      #line(length: 100%, stroke: 1pt + accent-color)
      #v(2.5pt)
      
      #grid(
        columns: (1fr, auto),
        row-gutter: 5pt,
        align: (left + horizon, right + horizon),
        [Nettobetrag], [#format-euro(totals.line_total_net)],
        ..totals.tax_breakdown.map(tax => (
          [zzgl. #str(tax.rate) % MwSt.], [#format-euro(tax.amount)]
        )).flatten()
      )
      
      #v(2.5pt)
      #line(length: 100%, stroke: 1pt + accent-color)
      #v(2.5pt)
      
      #grid(
        columns: (1fr, auto),
        align: (left + horizon, right + horizon),
        [*Gesamtbetrag*],
        [*#text(size: 11pt, fill: rgb("#0F172A"))[#format-euro(totals.grand_total)]*]
      )
    ]
  ]
]
