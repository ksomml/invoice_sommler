// Typst Header Component for Invoices
// Handles DIN 5008 Sender Line, Recipient Block, and Top-Right Logo

#let header-block(seller, client, logo-path) = [
  #grid(
    columns: (1fr, auto),
    gutter: 15pt,
    align: (left + top, right + top),
    [
      // Small sender line above recipient (DIN 5008)
      #let seller-country = if "country" in seller.address and seller.address.country != "" [ · #seller.address.country] else []
      #text(size: 7.5pt, fill: rgb("#718096"))[
        #seller.name · #seller.address.street · #seller.address.zip #seller.address.city#seller-country
      ]
      #v(3mm)

      // Recipient Address Block
      #block(width: 85mm)[
        #if "trade_name" in client and client.trade_name != "" and client.trade_name != client.name [
          *#client.trade_name*\
          #client.name\
        ] else [
          *#client.name*\
        ]
        #if "contact" in client and "person" in client.contact and client.contact.person != "" [
          z. Hdn. #client.contact.person\
        ]
        #client.address.street\
        #if "additional" in client.address and client.address.additional != "" [
          #client.address.additional\
        ]
        #client.address.zip #client.address.city\
        #if "country" in client.address and client.address.country != "" and client.address.country != none [
          #client.address.country\
        ]
        #if "tax" in client and "vat_id" in client.tax and client.tax.vat_id != "" and client.tax.vat_id != none [
          USt-IdNr. #client.tax.vat_id\
        ]
      ]
    ],
    [
      // Top-Right Logo Block
      #if logo-path != none and logo-path != "" [
        #image(logo-path, width: 34mm)
      ]
    ]
  )
]
