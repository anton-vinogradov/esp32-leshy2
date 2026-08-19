# REQ-IBTN-0001 — external iButton/1-Wire contact-tool contract

- Статус: **Проведено ревью capability; electrical implementation ждёт G3–G11**
- Дата: 2026-08-16
- Source: `AUD-0004/W-EXTRA-11`
- Decision: [`DEC-0033`](../decisions/DEC-0033-external-m5-ibutton-profile.md)

## Scope boundary

The base device has no mandatory integrated iButton contact pad. A protected
M5-style Port-B profile plus passive replaceable contact adapter carries the
function. Accessory presence makes the function reachable, not authorized.

| ID | Result | Status | Level and mandatory boundary |
|---|---|---|---|
| `REQ-IBTN-01` | exact accessory/profile recognition | `include` | System: unknown/wrong profile remains unpowered; passive identity or explicit selection is required before a profile-specific probe |
| `REQ-IBTN-02` | generic owned 1-Wire discovery/read | `conditional` | Main only for non-credential devices and exact supported families; CRC/family/ROM are reported without claiming identity ownership |
| `REQ-IBTN-03` | access-key read/identify/save | `conditional` | Lab: passive contact, explicit capture action, protocol/confidence/electrical state visible; no automatic emulation |
| `REQ-IBTN-04` | reader-side emulation | `conditional` | Controlled Zone `AUTHORIZED_TARGET`: exact supported protocol/fixture, per-action target preview, bounded lease and no unattended replay |
| `REQ-IBTN-05` | rewritable-key write | `conditional` | Controlled Zone `AUTHORIZED_TARGET`: exact writable family, pre-read/backup where possible, irreversible warning, verify-after-write and explicit failure state |
| `REQ-IBTN-06` | Dallas/Maxim 1-Wire baseline | `conditional` | Exact family/voltage/timing/pull-up/current and CRC corpus; generic GPIO or a software OneWire API is not sufficient qualification |
| `REQ-IBTN-07` | Cyfral/Metakom and other contact protocols | `defer-profile` | separate electrical/timing/corpus acceptance; never inferred from Dallas support |
| `REQ-IBTN-08` | sensitive record vault | `include` | encrypted at rest, typed provenance, redacted UI/export by default, explicit delete and factory-reset erasure |
| `REQ-IBTN-09` | safe detach/reset/STOP | `include` | detach, short, profile loss, lock, timeout, reset, update, brownout or STOP terminates drive/emulation and clears target/lease |

## Electrical/mechanical prerequisites

- open-drain/bidirectional timing path with selectable qualified pull-up/level;
- no direct 5 V exposure to a non-5-V-tolerant future MCU pin;
- short, ESD, back-power, reversed/wrong adapter and contaminated-contact tests;
- contact debounce and stable-presence evidence before a transaction;
- replaceable corrosion/wear surface and strain relief;
- no operation on attach alone.

## Acceptance evidence

- public/owner-created corpus per exact supported family for read, emulate and
  write treated as three independent matrices;
- good/bad CRC, marginal contact, bounce, short, disconnect and power-cycle
  traces;
- reader-fixture interoperability evidence without a universal compatibility
  claim;
- vault export/delete/factory-reset tests;
- Controlled-Zone route/authorization/timeout/STOP tests;
- HIL proof that release/reconnect never restores the previous key or emulation.

## Explicit non-claims

- no official M5 iButton Unit is claimed;
- no universal Dallas/Cyfral/Metakom compatibility;
- no credential authenticity, access right or ownership inferred from a code;
- no safe rewrite promise for unknown keys;
- no integrated base contact pad.

## Source evidence

- [M5 HY2.0 Port B permits GPIO/special single-wire profiles](https://docs.m5stack.com/en/learn/interface/grove)
- [M5 software OneWire driver and required 4.7 kΩ pull-up example](https://docs.m5stack.com/en/mpy/official/machine)
- [Flipper Zero iButton user-result reference](https://docs.flipper.net/zero/ibutton)
