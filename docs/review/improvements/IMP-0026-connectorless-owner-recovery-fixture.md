# ⚠️ IMP-0026 — connectorless owner recovery fixture

- Статус: **Открыто; требуется решение владельца**
- Дата: 2026-08-16
- Основание: `C-006/C-007`, `REC-0001`, accepted independent recovery and zero-loss cost policy
- Затрагивает: base BOM, enclosure openings, owner recovery UX, factory fixture, attack/failure surface

## Current state

S3, C5 and RP2354A need recovery that works with erased/corrupt application
images and without a working peer. Only S3 also needs the ordinary product USB
port. Adding permanent external connectors for the other domains improves
casual access but adds connector/ESD/CC parts, board-edge area and enclosure
openings. Sharing one connector through a mux reduces openings but creates a
common failure dependency and contradicts the already accepted independent
recovery boundary.

## A — recommended: one product USB plus three passive service footprints

- retain one external product USB-C directly on S3;
- place one separate keyed `TC2050-IDC-NL` no-legs 10-pad footprint per compute
  domain under a removable owner-service cover;
- S3 footprint exposes GPIO0/EN and UART0; its normal USB stays direct;
- C5 footprint exposes native USB D−/D+, GPIO28/CHIP_PU and UART0;
- RP footprint exposes native USB D−/D+, USB_BOOT/RUN and SWDIO/SWCLK;
- each footprint has local ground and voltage-reference sense, but no fixture
  VBUS-to-board power path;
- publish the exact pinout and an open adapter design in the repositories;
- use no MCU-controlled mux, expander or software in any recovery path.

Consequences: zero connector BOM per board for C5/RP, no extra external USB
holes, low common-failure risk and owner recovery remains documented. Tradeoff:
the owner needs the inexpensive reusable spring-pin adapter and must open the
service cover. The external Tag-Connect cable/adapter is a tool, not a bundled
component on every board.

## B — three permanent owner connectors

Keep S3 product USB-C and add independently routed C5 USB-C plus RP USB-C and a
separate SWD header/connector.

Consequences: easiest bench use and no special pogo adapter. It has the highest
base BOM/edge/ESD/CC/mechanical cost, at least two additional enclosure
openings, more debris/liquid ingress paths and more externally reachable debug
surfaces. SWD still needs its own access or a combined custom connector.

## C — one external connector through a selector/mux

Route one USB-C to S3/C5/RP using an analog mux or mechanical selector and keep
separate boot/reset controls.

Consequences: fewer openings than B, but the shared connector, selector and
route become common recovery failure points; an active mux also needs safe
power/default logic. This fails the accepted meaning of physically independent
recovery and is not recommended.

## Recommendation

Choose **A**. It preserves independent, owner-accessible, open recovery while
removing two permanent connector assemblies from the base device. It also gives
factory test one repeatable reusable fixture format without allowing any
firmware domain to disable access.

## Decision question

Принять вариант **A**, либо выбрать **B** или **C**?
