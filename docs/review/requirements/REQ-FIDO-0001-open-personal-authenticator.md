# REQ-FIDO-0001 — open personal FIDO authenticator contract

- Статус: **Проведено ревью требований; implementation proof открыт**
- Дата: 2026-08-16
- Решение: [`DEC-0035`](../decisions/DEC-0035-open-personal-fido-authenticator.md)
- Evidence: [`AUD-0006`](../audits/AUD-0006-fido-authenticator-security-boundary.md)
- Режим: **Основной / exclusive Authenticator Mode**

## Capability contract

| ID | Requirement | Acceptance boundary |
|---|---|---|
| `REQ-FIDO-01` | USB roaming authenticator implements reviewed CTAP 2.3 Proposed Standard and CTAP1/U2F compatibility. | Exact advertised versions/commands/extensions pass the applicable conformance and cross-platform suite; newer drafts require review. |
| `REQ-FIDO-02` | Authenticator Mode is an exclusive minimal trust domain. | Clean transition/reboot; USB exposes CTAPHID only. Lab/CZ, radios, scripts/plugins, CDC/MSC/keyboard/vendor RPC and shared removable storage are unavailable. |
| `REQ-FIDO-03` | Every completed registration/assertion with UP gets fresh local consent. | No default cached presence; display distinguishes create/sign and shows available RP/user context before the designated physical gesture. PIN alone never asserts presence. |
| `REQ-FIDO-04` | CTAP2 PIN/UV behavior is complete and independent of device unlock. | PIN/UV protocol 2, retry/lockout/reset behavior and volatile permission lifetimes follow the reviewed spec; general Leshy2 PIN is not silently reused. |
| `REQ-FIDO-05` | Modern credential functions are internally consistent. | `hmac-secret`, `credProtect`, discoverable/non-discoverable credentials and credential management are implemented together with published capacity and truthful `getInfo`. |
| `REQ-FIDO-06` | Credentials and wrapping secrets are device-bound and non-exportable. | General backup/export/restore omits keys, wrapping secret, PIN state and counters; restore cannot clone the authenticator. BE/BS remain truthful single-device semantics. |
| `REQ-FIDO-07` | Secret persistence is atomic and fail-safe. | Power loss, brownout, full storage, interrupted update and wear cannot expose or partially replace credentials/PIN/counters; corrupt state fails closed. |
| `REQ-FIDO-08` | Reset is deliberate and destructive. | On-device long physical action plus explicit confirmation wipes credentials, wrapping secret, PIN and transactions; reset never restores them from general backup. |
| `REQ-FIDO-09` | Update/rollback preserves or safely destroys the trust domain. | Only compatible owner-authorized images migrate secrets; incompatible trust-domain/debug/recovery transition wipes or makes the vault unavailable. No rollback restores old authorization or keys. |
| `REQ-FIDO-10` | Counters and metadata never overclaim. | Non-zero sign counter is monotonic across supported lifecycle or reported as zero; AAGUID, firmware version, options and certification map are truthful. |
| `REQ-FIDO-11` | Privacy-default attestation is none/self. | No shared batch/enterprise attestation key in source, logs or backup; a new attestation model needs separate approval and provisioning audit. |
| `REQ-FIDO-12` | Marketing and UI state the assurance class honestly. | No `FIDO Certified`, hardware-backed or tamper-resistant claim without evidence; open/custom/debug state remains visible and never inherits a stronger label. |
| `REQ-FIDO-13` | Authenticator secrets are single-purpose. | They are not observable/alterable or usable for signing through non-FIDO transports, apps, shell, diagnostics or vendor commands. |
| `REQ-FIDO-14` | Recovery guidance prevents account lockout. | Setup recommends a second authenticator/recovery codes and warns before destructive reset/update transitions; device backup is never presented as credential recovery. |

## Architecture and release gates

- G3: entry/exit, confirmation, RP/user display, PIN/reset/recovery UX.
- G4/G7: at least two complete implementations compare isolation, USB owner,
  persistence, update/debug boundary, cost and failure modes.
- G9: threat model, cryptographic/persistence design, exact CTAPHID state
  machine, reproducible build and dependency/SBOM review.
- G11: official/independent conformance, Windows/macOS/Linux/browser
  interoperability, fuzzing, malformed/concurrent CTAPHID, power-cut,
  update/rollback/reset/debug and cross-interface extraction tests.

Transport availability or a TinyUSB HID example is not completion evidence.

