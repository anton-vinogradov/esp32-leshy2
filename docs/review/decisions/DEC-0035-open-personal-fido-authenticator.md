# DEC-0035 — open personal FIDO authenticator

- Статус: **Принято владельцем; проведено ревью распространения**
- Дата: 2026-08-16
- Ответ владельца: **да варианту A**
- Предложение: [`IMP-0029`](../improvements/IMP-0029-open-personal-fido-authenticator.md)
- Evidence: [`AUD-0006`](../audits/AUD-0006-fido-authenticator-security-boundary.md)
- Нормативный контракт: [`REQ-FIDO-0001`](../requirements/REQ-FIDO-0001-open-personal-authenticator.md)

## Решение

1. Leshy2 получает функцию открытого personal roaming authenticator в Основном
   режиме.
2. Reviewed protocol baseline — FIDO2/CTAP 2.3 over USB HID с CTAP1/U2F для
   обратной совместимости. Более новый Working Draft не принимается молча.
3. Authenticator запускается как отдельный минимальный CTAPHID-only режим через
   clean transition/reboot. Lab, Controlled Zone, radios, scripts, shared
   removable storage и прочие USB classes в нём недоступны.
4. Каждая завершённая registration/assertion, заявляющая user presence,
   требует нового локального действия. PIN/UV не заменяет physical presence.
5. Credentials являются device-bound и non-exportable, не входят в общий
   backup Leshy2. Recovery выполняется вторым заранее зарегистрированным
   authenticator или account recovery method.
6. Privacy default — none/self attestation. Без отдельного proof запрещены
   claims `FIDO Certified`, hardware-backed и tamper-resistant.
7. Исходники, owner-controlled signing/recovery и developer firmware остаются
   открытыми. Custom/debug state честно снижает assurance и не наследует
   production claims.

## Что не принято

- export/restore или синхронизация credentials;
- shared batch attestation keys в исходниках или backup;
- certified/enterprise SKU;
- обязательный secure element или locked base device;
- BLE/NFC/hybrid FIDO transport;
- использование authenticator keys другими Leshy2 applications.

Любой из этих пунктов требует отдельного review и решения.

## Последствия

- `W-EXTRA-12` закрыт вариантом A;
- G3 обязан определить понятный вход, confirmation, RP/user display, exit и
  destructive reset UX;
- G4/G7 должны доказать изолируемый trust domain и USB owner, не выбирая их из
  legacy layout;
- релиз блокируется до protocol/interoperability/fuzz/fault/update/reset and
  cross-interface isolation evidence.

