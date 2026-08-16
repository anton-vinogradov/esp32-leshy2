# AUD-0004 — current competitor capability and product-design gap

- Статус: **На ревью; `W-EXTRA-11..16` закрыты, только `W-EXTRA-17` открыт**
- Дата snapshot: 2026-08-16
- Finding: [`FND-0040`](../findings/FND-0040-current-competitor-benchmark-missing.md)
- Scope: official product/project documentation; shipping and prototype states
  are never merged

## Representative products

| Product/class | Current official facts relevant to Leshy2 | Design lesson, not copied solution |
|---|---|---|
| Flipper Zero, shipping compact multi-tool | 100×40×25 mm, 102 g, 2100 mAh, 1.4-inch sunlight-readable 128×64 LCD, D-pad/back, microSD, USB-C, CC1101, LF RFID, NFC, IR, BLE/802.15.4, iButton and GPIO; claimed battery life up to 28 days | pocket control can remain complete without touch/keyboard; field runtime/readability, lanyard and contact tools are product-level requirements |
| M5 Cardputer-Adv, shipping card terminal | 84×54×19.6 mm, 81 g, 1750 mAh, 56-key keyboard, 240×135 display, ES8311/mic/speaker/jack, IR TX, microSD, Grove and 14-pin expansion, lanyard; U214 Cap adds LoRa+GNSS | keyboard and cap mechanics are viable in a small device, but screen area and antenna/accessory volume are constrained |
| LILYGO T-Deck Plus, shipping dev platform | 100×68×11 mm, 2.8-inch 320×240, keyboard+trackball, 2000 mAh, microSD, LoRa and GNSS; no touch; Plus consumes its Grove pins for GNSS | large landscape face improves UI/text, while fixed onboard radios can remove general expansion and force bus sharing |
| LILYGO T-Embed CC1101, shipping integrated dev platform | 97.5×39×31 mm, 1.9-inch 320×170, encoder, CC1101, PN532, IR, mic/speaker, TF, 1300 mAh and two QWIIC ports | narrow one-hand/encoder shell can carry many blocks, but thickness, controls and RF/antenna honesty need explicit review |
| ESP32 Marauder, active open project | hardware variants deliberately span 2.8-inch touch, 1.44-inch 5-way compact control, SD/battery/GPS and CLI; current feature matrix includes Wi-Fi/BLE analysis, raw capture and PMKID | one firmware does not prove one optimal enclosure; control/display profiles are real product variants |
| Flipper One, **prototype not for sale** | preliminary 155×67×40 mm, 22.9 Wh, Linux RK3576 + low-power RP2350, 256×144 grayscale display, D-pad/touchpad/PTT, USB host/PD, Wi-Fi 6E 2.4/5/6, M.2 and modular antenna rail | high-speed/Linux/extensible class is physically and economically different; its provisional features are competitor direction, not a baseline fact to clone |
| HackRF One, shipping SDR peripheral | open 1 MHz–6 GHz half-duplex, 20 Msps 8-bit IQ, high-speed USB, no autonomous UI/battery | wideband SDR requires a different RF/compute/data/power class; external/deferred disposition is honest unless the whole product class changes |

## Sources

- [Flipper Zero official product/specifications](https://flipper.net/)
- [Flipper Zero iButton](https://docs.flipper.net/zero/ibutton) and
  [U2F](https://docs.flipper.net/zero/u2f) documentation
- [Flipper One preliminary technical specifications](https://docs.flipper.net/one/general/tech-specs),
  [Wi-Fi/Bluetooth](https://docs.flipper.net/one/hardware/wifi-bluetooth) and
  [module mounting](https://docs.flipper.net/one/mechanics/module-mounting-system)
- [M5Stack Cardputer-Adv](https://docs.m5stack.com/en/core/Cardputer-Adv) and
  [Cardputer Mesh Kit/U214](https://docs.m5stack.com/en/core/Cardputer_Mesh_Kit)
- [LILYGO T-Deck Plus](https://wiki.lilygo.cc/products/t-deck-series/t-deck-plus/)
- [LILYGO T-Embed CC1101](https://wiki.lilygo.cc/products/t-embed-series/t-embed-cc1101/)
- [ESP32 Marauder current hardware matrix](https://github.com/justcallmekoko/ESP32Marauder/wiki/marauder-versions)
- [Great Scott Gadgets HackRF One](https://greatscottgadgets.com/hackrf/one/)

## Coverage against the existing wishlist

| Competitor result | Existing Leshy2 disposition | Audit result |
|---|---|---|
| ordinary 2.4/5 GHz Wi-Fi, BLE and 802.15.4 | reviewed `REQ-W24/W5/BLE`; owners open | covered; 5 GHz remains a base capability |
| Sub-GHz/IR/HF NFC/audio/SD/local UI | reviewed base or qualified external contracts | covered with intentionally different backend choices |
| external GNSS and LoRa | explicit M5 Unit + U214/expansion profiles | covered; onboard duplication remains rejected by owner |
| LF 125 kHz RFID | `W-EXTRA-09`, deferred external frontend | already considered; not a new gap |
| wideband SDR/Linux analytics | `W-EXTRA-07`, external/defer-release | already considered; HackRF proves a different hardware class, not free base scope |
| cellular | `W-EXTRA-08`, external/tethered | already considered |
| Bluetooth Classic, dedicated BLE sniffer | `W-EXTRA-02/04`, optional/deferred | already considered |
| iButton/1-Wire contact-tool behavior | accepted external by `DEC-0033/REQ-IBTN-0001` | **gap closed at capability level; electrical/HIL open** |
| USB security key (U2F/FIDO family) | former acceptance `DEC-0035`, removed by mission correction `DEC-0039` | **closed outside current radio/key product scope** |
| haptic feedback | rejected by `DEC-0036`; buzzer/LED/display remain | **closed outside product scope** |
| IMU/orientation/motion | accepted external `DEC-0037/REQ-IMU-0001` | **gap closed at requirement level; indexed mechanics/electrical/HIL open** |
| physical keyboard/trackball/D-pad archetype | core local control required; text-dependent scenarios may use phone | **closed `DEC-0038`: no integrated keyboard, bounded phone-assisted text; other field controls remain G3** |
| high-speed USB host/M.2-class attachment | two-tier expansion remains result-driven; generic host rejected `DEC-0039` | **closed outside scope; concrete RF profile may derive exact transport** |
| 6 GHz Wi-Fi | accepted target stops at 5 GHz | **real scope question; not implied by “5 GHz”** |
| sunlight/gloves/lanyard/mounts/module retention | not quantified | **mandatory G3 constraints**, not radios/features |
| Ethernet/HDMI/power-bank outputs | absent and no reviewed use case | not silently added; remains out unless a user result is proposed |

## Complete delta queue

These rows are deliberately visible together so the later product design cannot
claim completeness while hiding pending choices. They are resolved one by one.

| ID | ⚠️ Candidate desire | Material consequence | Initial recommendation |
|---|---|---|---|
| `W-EXTRA-11` | iButton/1-Wire read/emulate and bounded write | **resolved `DEC-0033`**: protected M5-style Port-B profile + passive adapter; no base pad | accepted external; official M5 iButton Unit is not claimed |
| `W-EXTRA-12` | modern FIDO2/CTAP authenticator + U2F compatibility | **superseded `DEC-0039`**: former reviewed acceptance no longer matches radio/key mission | removed from target; historical security evidence retained |
| `W-EXTRA-13` | haptic feedback | **resolved `DEC-0036`**: clarified instrument scope does not need consumer tactile UX | rejected; no motor/profile/mount/base burden |
| `W-EXTRA-14` | IMU | **resolved `DEC-0037/REQ-IMU-0001`**: optional external measurement pose/motion provenance; indexed mount; 6-axis is not heading/bearing | accepted external; no base sensor or consumer gesture/fall/tamper scope |
| `W-EXTRA-15` | physical text keyboard | **resolved `DEC-0038`**: permanent keyboard excluded; rare/long text may use locally paired phone, never as safety/authorization authority | accepted phone-assisted text; no U215/base keyboard profile |
| `W-EXTRA-16` | dual-role/high-speed USB accessory host | **resolved `DEC-0039`**: generic peripheral-host result is outside mission | rejected generic; a concrete accepted RF/SDR profile may derive transport later |
| `W-EXTRA-17` | 6 GHz/Wi-Fi 6E | **facts reviewed `AUD-0012/REV-0002AQ`; owner placement open `IMP-0034`** | keep 5 GHz base; preserve qualified optional 6E profile without base burden |

## Gate result

The old 125 leaves remain reviewed; none was lost. G2 is reopened only for the
five remaining delta decisions above and physical constraints that feed G3.
`W-EXTRA-11` is closed by `DEC-0033`; `AUD-0005/DEC-0034` separately close the
general M5-first/two-tier infrastructure question. `DEC-0039` later removes the
former `AUD-0006/DEC-0035` FIDO target; `AUD-0007/DEC-0036` reject
product haptic; `AUD-0008/DEC-0037` close `W-EXTRA-14`; `AUD-0009/DEC-0038`
close `W-EXTRA-15`; `AUD-0010/DEC-0039` reject generic `W-EXTRA-16`;
`AUD-0012` reviews the final 6 GHz facts. G3 research
may proceed in parallel, but neither product design nor architecture can receive
final review while any accepted delta is missing from its demand model.
