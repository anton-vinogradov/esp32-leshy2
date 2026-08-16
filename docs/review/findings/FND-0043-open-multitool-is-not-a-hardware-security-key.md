# FND-0043 — an open multitool authenticator is not automatically a hardware security key

- Статус: **Закрыто исторически; capability removed from target `DEC-0039`**
- Дата: 2026-08-16
- Обнаружено: [`AUD-0006`](../audits/AUD-0006-fido-authenticator-security-boundary.md)
- Затрагивает: `W-EXTRA-12`, USB product modes, secret storage, update/recovery/debug

## Несоответствие

Первичная competitor-строка предлагала `U2F/FIDO-style USB security key` как
mostly-software capability. USB HID transport действительно mostly software,
но security-key result — нет. Общий firmware/runtime с radios, Lab tools,
storage, debug and vendor interfaces способен наблюдать или использовать те же
secrets. Это противоречит необходимой isolation boundary и создаёт ложное
ожидание hardware-backed/certified assurance.

Кроме того, U2F является compatibility protocol, а не достаточным современным
target. Current baseline — FIDO2/CTAP2.3 plus CTAP1/U2F compatibility.

## Исправление

1. Target name and claims separate protocol compatibility, certification,
   hardware backing and physical tamper resistance.
2. Software-only capability допускается только в exclusive minimal
   Authenticator Mode с локальным user presence и isolated secret lifecycle.
3. General device backup never clones single-device FIDO secrets.
4. Open/custom firmware remains allowed, but lowers assurance honestly.
5. Dedicated security hardware/certified SKU is a separate future product
   decision, not an implied property of the base.

## Exit criteria

- [x] owner historically accepted option A through [`DEC-0035`](../decisions/DEC-0035-open-personal-fido-authenticator.md);
- [x] later mission correction [`DEC-0039`](../decisions/DEC-0039-radio-key-scope-correction.md)
  removes it from target;
- [x] no CTAP/vault/USB/UX/architecture/release gate remains active.
