# REQ-SCOPE-0001 — radio/key product boundary

- Статус: **Проведено ревью требований**
- Дата: 2026-08-17
- Решение: [`DEC-0039`](../decisions/DEC-0039-radio-key-scope-correction.md)
- Evidence: [`AUD-0011`](../audits/AUD-0011-radio-key-product-scope.md)

## Contract

| ID | Requirement | Acceptance boundary |
|---|---|---|
| `REQ-SCOPE-01` | Every target user capability maps to radio/wireless communication, RF observation/diagnostics/research, or wireless/contact credential work. | Any exception is named by an owner decision; catalog availability, spare MCU resources or easy firmware is insufficient. |
| `REQ-SCOPE-02` | UI, storage, audio, power, time/location, phone input, update, diagnostics and recovery are enabling infrastructure. | They preserve an accepted mission result and do not become unrelated general-purpose product promises. |
| `REQ-SCOPE-03` | Expansion is profile/result driven. | M5/generic connectors expose no catalog feature automatically; every target accessory produces an accepted radio, credential or measurement result. |
| `REQ-SCOPE-04` | High-throughput transport is derived, not a standalone feature. | No generic USB host/HS/DRP requirement. A concrete accepted RF/SDR/analysis profile states payload, latency, role and power before any architecture reserves a path. |
| `REQ-SCOPE-05` | Personal FIDO authenticator is absent. | No CTAP/U2F mode, credential vault, attestation/conformance claim or FIDO-driven hardware/resource/release gate. |
| `REQ-SCOPE-06` | BadUSB/DuckyScript is the explicit non-core exception. | Release-optional software-only Controlled-Zone profile; existing USB device path only, mutually exclusive mode, no added base hardware/architecture scoring, never blocks radio/key release. |
| `REQ-SCOPE-07` | Easy software is not free. | Optional exceptions still publish firmware size, parser/USB attack surface, authorization, test/HIL and maintenance cost before release. |
| `REQ-SCOPE-08` | Service interfaces serve Leshy2. | Console/export/update and independent chip recovery remain; they do not promise a generic external programmer, host computer or arbitrary peripheral support. |
| `REQ-SCOPE-09` | Removed features cannot survive as hidden resources. | G3–G9 trace every component, connector, pin, endpoint, secure store and power rail to a live requirement; removed FIDO/host resources score zero benefit. |

## Review gates

- G2: every wishlist row classified as core, enabling, named exception, deferred
  core profile or rejected;
- G3/G4: no enclosure/connector/compute burden justified only by removed scope;
- G7/G9: resource and firmware manifests trace to live requirement IDs;
- G11: optional BadUSB evidence is separate from the base radio/key release gate.
