# M5Stack Cap inquiry — sent 2026-09-07

Status: **sent; technical clarification pending**. Gmail displayed the explicit
confirmation “Сообщение отправлено.” The recipient was verified against
[M5Stack's official Tech Support contact](https://shop.m5stack.com/pages/contact-us):
**support@m5stack.com**. This is not an order, purchase, or approval of any
candidate contact map. Sending an inquiry does not close the electrical or
mechanical gate.

The public copy below omits personal sender/signature and private message
identifiers. The existing file path is retained for stable review links.

## Message

Subject: U214 / U219 Cap — physical mating-contact orientation and mounting datums

Hello M5Stack team,

We are designing a custom carrier for one U214 Cap LoRa-1262 or U219 Cap CC1101 + NFC, using a 2 x 7, 2.54 mm female socket. We have two questions before finalizing the PCB:

1. Could you provide an annotated view looking directly at the Cap's underside male contacts, identifying the SMA end and NRST side, and marking 5VIN and GND (or all 14 contacts)? Please clarify whether the GPIO.EXT diagram is this mating-side view or a view through the front label, and confirm that U214 and U219 use the same physical contact positions. We cannot resolve the row orientation from the published photographs: the U214 and U219 GPIO.EXT callouts put the supply row on opposite sides. The U219 callout also appears to interchange CC_CS and NFC_CS compared with its schematic.

2. Could you provide the X/Y position of the center of the 2 x 7 contact grid and the retention-feature centers, referenced to the 84 x 24 mm housing edges, with tolerances? The published U214 structure file contains the housing but not the metal contacts, so we cannot establish the precise header-to-housing datum.

An annotated drawing or PCB assembly drawing is sufficient; a STEP model is not required. This is a technical design inquiry only, not an order or purchase request.

Reference documents:

- [U214 documentation and GPIO.EXT photograph](https://docs.m5stack.com/en/cap/Cap_LoRa-1262)
- [U219 documentation and GPIO.EXT photograph](https://docs.m5stack.com/en/cap/Cap_CC1101)
- [U214 official housing CAD](https://github.com/m5stack/M5_Hardware/tree/master/Products/U214_Cap_LoRa-1262/Structures)

Thank you!

## Internal tracking — not part of the message

Evidence: `hardware/layout/h6-r2-cap-mating-review.json`. No proposed contact
map is accepted; review an actual technical response before changing the PCB.
