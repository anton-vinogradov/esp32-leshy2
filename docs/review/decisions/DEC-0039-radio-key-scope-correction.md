# DEC-0039 — radio/key mission scope correction

- Статус: **Принято владельцем; проведено ревью распространения**
- Дата: 2026-08-17
- Ответ владельца: **generic HS USB host и FIDO убрать; BadUSB оставить без hardware burden**
- Evidence: [`AUD-0011`](../audits/AUD-0011-radio-key-product-scope.md)
- Контракт: [`REQ-SCOPE-0001`](../requirements/REQ-SCOPE-0001-radio-key-product-boundary.md)

## Решение

1. Product mission is radio/wireless communication, observation, diagnostics
   and authorized research, including wireless/contact credential tools and
   only the infrastructure needed to operate/measure/secure/recover them.
2. `W-EXTRA-16` generic dual-role/High-Speed USB accessory host is rejected.
   No final architecture must contain native HS host, source generic host VBUS
   or select ESP32-P4/another HS owner for this removed result.
3. `DEC-0034/REQ-EXT-0001` retain an implementation-neutral high-throughput
   class only when a concrete accepted RF/SDR/external-analysis profile derives
   it. Connector, transport, host/device role and power remain downstream.
4. Personal FIDO2/U2F authenticator is removed from the target. `DEC-0035` is
   superseded for current product scope; `REQ-FIDO-0001` remains historical
   reviewed evidence and imposes no architecture/release requirement.
5. BadUSB/DuckyScript is retained as a single explicit non-core exception:
   release-optional Controlled-Zone software over an existing USB device/service
   path, with no incremental base hardware and no right to shape architecture or
   delay radio/key core.
6. “No hardware burden” does not mean zero cost: BadUSB still needs isolated
   runtime behavior, authorization, parser/USB security review and HIL before
   that optional profile ships.
7. Product USB service/export and independent programming/recovery of Leshy2's
   own selected chips remain enabling infrastructure, not a generic programmer
   or peripheral-computer promise.

## Consequences

- `W-EXTRA-12` closes as `removed-by-owner-scope`;
- `W-EXTRA-16` closes as `rejected-generic`; `IMP-0033/A` is not accepted;
- FIDO target prose and firmware contract are removed from both repositories;
- BadUSB requirements become `defer-release/software-only-exception`;
- M5 live attachment denominator excludes generic host as well as rejected
  haptic and keyboard profiles;
- current competitor delta proceeds to the remaining radio question
  `W-EXTRA-17` 6 GHz/Wi-Fi 6E.
