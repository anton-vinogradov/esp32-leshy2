# AUD-0011 — radio, communication and credential-tool product scope

- Статус: **Проведено ревью; scope correction принят `DEC-0039`**
- Дата: 2026-08-17
- Основание: уточнение владельца «связь/радио, включая перепрошивку ключей»
- Решение: [`DEC-0039`](../decisions/DEC-0039-radio-key-scope-correction.md)
- Контракт: [`REQ-SCOPE-0001`](../requirements/REQ-SCOPE-0001-radio-key-product-boundary.md)

## Проверяемая миссия

Leshy2 is an autonomous field instrument for radio/wireless communication,
observation, diagnostics and authorized research, plus wireless/contact
credential tools. A feature is in scope when it produces one of those results
or is necessary to operate, measure, secure, update, recover or document them.

## Активный target после классификации

| Class | Examples | Disposition |
|---|---|---|
| RF/wireless core | Wi-Fi 2.4/5, BLE, 802.15.4, 3×nRF24, Sub-GHz, LoRa, broadcast receiver, analog/digital voice, GNSS | target/deferred profiles remain as already reviewed |
| wireless/contact credentials | HF/LF RFID/NFC, iButton/1-Wire, authorized read/emulate/write, relay/recovery research | in scope under Main/Lab/Controlled-Zone gates |
| adjacent communication | consumer IR learn/transmit, remote-ID reception | in scope; optical is not RF but is a communication/control instrument |
| radio signal support | audio codec/bypass, storage/capture, external indexed IMU metadata, antennas, time/location | enabling instrument infrastructure only |
| product infrastructure | display/controls, phone text, battery, STOP, signed update, self-recovery/diagnostics, USB service/export | retained only to operate and maintain Leshy2 |
| M5/other expansion | exact radio, credential or measurement accessories | transport/profile, never blanket catalog scope |
| external compute | RF/credential capture analysis and recovery | bounded accepted workload; not general-purpose Linux promise |

## Найденные scope leaks

### Generic High-Speed USB host

`AUD-0010` proved HS host useful for a broad peripheral computer, but the owner
does not want that product result. `W-EXTRA-16` is rejected. A concrete future
SDR/radio profile may still derive a high-throughput transport requirement;
that transport is not automatically USB, host, dual-role or base hardware.

### Personal FIDO authenticator

`DEC-0035` was an explicit earlier choice, not an accidental implementation.
The refined mission now supersedes it: personal account authentication is not
radio communication or credential read/emulate/write. Removing it eliminates
CTAP conformance, credential vault and exclusive authenticator lifecycle from
the target without changing owner-controlled signed firmware.

### BadUSB/DuckyScript

This is also outside the core mission, but the owner explicitly retains it.
It is therefore a named exception, not evidence that generic USB security tools
belong in scope. It may ship only as a release-optional Controlled-Zone software
profile over the already-required USB device/service path:

- no extra base component, connector, pin, host power or architecture score;
- mutually exclusive HID execution mode; no permanent composite-endpoint promise;
- no autorun; authorized target, fresh local arm/confirmation and STOP behavior;
- firmware/security/fuzz/HIL cost remains real and is scheduled after radio/key core;
- failure or omission cannot block the base release or reduce radio capability.

## Other suspected non-radio hardware

- haptic and permanent keyboard are already rejected;
- IMU is external and accepted only as RF measurement-pose metadata;
- ambient auto-brightness has no accepted base sensor and remains conditional;
- Ethernet, HDMI, power-bank output, motors, cameras and arbitrary M5 sensors
  are not target capabilities;
- no exact active compute/board/pin architecture exists after `DEC-0032`, so no
  non-radio device is currently locked into the target hardware.

## Gate

- [x] core mission separated from enabling infrastructure;
- [x] radio/contact-key edge cases classified;
- [x] generic USB host and personal FIDO removed;
- [x] BadUSB retained as one explicit software-only exception with real test cost;
- [x] high-throughput RF transport kept implementation-neutral;
- [x] no active hardware owner/pin/component inherited from removed functions.
