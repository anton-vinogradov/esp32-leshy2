# DEC-0040 — reject 6 GHz/Wi-Fi 6E product scope

- Статус: **Принято владельцем; проведено ревью распространения**
- Дата: 2026-08-17
- Ответ владельца: **вариант C — полностью отказаться от 6 ГГц**
- Предложение: [`IMP-0034`](../improvements/IMP-0034-6ghz-wifi6e-placement.md)
- Evidence: [`AUD-0012`](../audits/AUD-0012-6ghz-wifi6e-product-scope.md)

## Решение

1. `W-EXTRA-17` 6 GHz/Wi-Fi 6E is rejected from the product target.
2. No base or optional Leshy2 profile promises 6 GHz Wi-Fi discovery,
   association, AP, monitor/security workflow or transmit support.
3. G3–G9 assign zero product benefit to 6E radio/host, 6 GHz RF path, antenna,
   connector, power, driver, regulatory qualification or enclosure burden.
4. Accepted autonomous 2.4/5 GHz Wi-Fi and its existing safety/regulatory
   contract remain unchanged.
5. A generic external SDR may incidentally have physical coverage near 6 GHz,
   but Leshy2 must not advertise or qualify that as a 6 GHz/Wi-Fi 6E result.
   Adding such a result later requires an explicit scope-reopen decision.

## Consequences

- option `IMP-0034/C` is selected; A and B remain historical alternatives;
- current-competitor delta `W-EXTRA-11..17` is fully disposed;
- no whole-device candidate may gain score by reserving hidden 6E resources;
- G2 may receive repeat review and hand the physical-design inputs to G3.
