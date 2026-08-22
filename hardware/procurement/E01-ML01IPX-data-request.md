# No-order technical data request — Ebyte E01-ML01IPX

Recipient: `ebyteiot@cdebyte.com`  
Target product: Leshy2 handheld radio instrument  
Current request: optional current-lot connector, revision and lifecycle
confirmation only; H1 no longer waits for a reply, and no quotation, sample or
purchase order is authorized

## Message

Subject: E01-ML01IPX current-lot RF connector and controlled mechanical data

Hello,

We are evaluating three `E01-ML01IPX` modules for simultaneous full-function
nRF24 radio paths. Public manufacturer evidence identifies the matching class
as generation 1, so the paper design now uses exact TE `2118651-2` jumpers and
Hirose `U.FL-R-SMT-1(10)` board mates. Before any quotation or purchase, please
confirm the exact current production configuration:

1. Name the manufacturer and exact series/MPN of the miniature RF receptacle.
   Your current manual identifies `IPX/IPEX`, recommends a generation-1 antenna
   family and publishes the module PcbLib; please confirm explicitly whether
   the fitted receptacle accepts U.FL / MHF1 / UMCC Gen1 plugs.
2. Confirm whether TE `2118651-2`, a 30-mm UMCC Gen1-to-Gen1 cable assembly, is
   an approved mate. If not, name an exact controlled mating cable.
3. Provide the current controlled module drawing, connector axis/tolerance,
   recommended land pattern, paste/reflow profile, maximum body/connector
   height and RF keepout.
4. Confirm genuine Nordic `nRF24L01P` and support for 250 kbps, 1 Mbps and
   2 Mbps, six RX pipes, auto acknowledgement/retransmit, ACK payload and
   dynamic payload.
5. State the current hardware revision, lot marking scheme, lifecycle status,
   PCN/EOL policy and whether RF IC, crystal, matching-network or receptacle
   substitution is allowed without PCN.

Commercial quantities, prices and received-sample qualification are
intentionally deferred until this technical identity is controlled.

Public references:

- [manufacturer product page](https://www.ebyte.com/product/47.html);
- [current product specification](https://www.ebyte.com/Uploadfiles/Files/2025-1-16/2025116152734216.pdf);
- [official Altium PcbLib download](https://www.ebyte.com/pdf-down/2947.html);
- [TE 2118651-2](https://www.te.com/en/product-2118651-2.html).
