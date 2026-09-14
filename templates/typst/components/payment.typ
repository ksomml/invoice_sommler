// Typst Payment Terms & Optional GiroCode Component

#let payment-block(inv, totals, girocode-path, format-euro, format-date, accent-color) = [
  #block(
    fill: rgb("#FDFBF7"),
    stroke: 0.8pt + accent-color,
    inset: 8pt,
    radius: 4pt,
    width: 100%,
  )[
    #if girocode-path != none and girocode-path != "" [
      #grid(
        columns: (1fr, auto),
        gutter: 15pt,
        align: (left + horizon, right + horizon),
        [
          #text(weight: "bold", size: 8.5pt, fill: rgb("#0F172A"))[Zahlungskonditionen:]\
          #v(1pt)
          #text(size: 8pt, fill: rgb("#334155"))[
            Bitte überweisen Sie den Rechnungsbetrag von *#format-euro(totals.due_payable)*
            #if "due_date" in inv and inv.due_date != none and inv.due_date != "" [
              bis zum *#format-date(inv.due_date)*
            ]
            auf das unten angegebene Bankkonto oder nutzen Sie bequem den nebenstehenden QR-Code zur Überweisung.
            #v(1.5mm)
            *Verwendungszweck:* #inv.number
          ]
          #if "outro_text" in inv and inv.outro_text != "" and inv.outro_text != none and not inv.outro_text.contains("überweisen") [
            #v(2pt)
            #text(size: 7.5pt, style: "italic", fill: rgb("#64748B"))[#inv.outro_text]
          ]
        ],
        [
          #align(center)[
            #image(girocode-path, width: 22mm)
            #v(-2pt)
            #text(size: 6pt, fill: rgb("#64748B"))[GiroCode / EPC-QR]
          ]
        ]
      )
    ] else [
      #text(weight: "bold", size: 8.5pt, fill: rgb("#0F172A"))[Zahlungskonditionen:]\
      #v(1pt)
      #text(size: 8pt, fill: rgb("#334155"))[
        Bitte überweisen Sie den Rechnungsbetrag von *#format-euro(totals.due_payable)*
        #if "due_date" in inv and inv.due_date != none and inv.due_date != "" [
          bis zum *#format-date(inv.due_date)*
        ]
        auf das unten angegebene Bankkonto.
        #v(1.5mm)
        *Verwendungszweck:* #inv.number
      ]
      #if "outro_text" in inv and inv.outro_text != "" and inv.outro_text != none and not inv.outro_text.contains("überweisen") [
        #v(2pt)
        #text(size: 7.5pt, style: "italic", fill: rgb("#64748B"))[#inv.outro_text]
      ]
    ]
  ]
]
