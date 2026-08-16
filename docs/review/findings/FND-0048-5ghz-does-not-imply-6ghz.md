# FND-0048 — accepted 5 GHz does not imply 6 GHz/Wi-Fi 6E

- Статус: **Открыто до решения владельца**
- Дата: 2026-08-17
- Обнаружено: [`AUD-0012`](../audits/AUD-0012-6ghz-wifi6e-product-scope.md)
- Затрагивает: `W-EXTRA-17`, G2–G7, RF/regulatory/HIL

## Несоответствие

The accepted target requires autonomous 2.4/5 GHz Wi-Fi. A future architecture
could incorrectly label a dual-band Wi-Fi 6 device such as ESP32-C5 “Wi-Fi 6E”
or assume that antenna coverage alone enables 6 GHz. Current ESP32-C5 RF is
specified only through 5885 MHz. Real 6E examples add a different radio plus
SDIO/PCIe host, RF/antenna, driver, power and regulatory-device-class burden.

## Required correction

- never use “Wi-Fi 6” and “Wi-Fi 6E” interchangeably;
- trace 6 GHz to an explicit owner disposition, not spare bandwidth or a broad
  antenna label;
- if retained, qualify exact passive/STA/AP/security-workflow results and
  regional TX behavior independently;
- do not let deferred/rejected 6 GHz weaken accepted 2.4/5 GHz;
- select no host, connector, radio or antenna until the whole-device option is
  accepted and compared at G3–G7.

## Exit criteria

- [x] fact/prerequisite review complete;
- [ ] owner selects `IMP-0034/A`, `B` or `C`;
- [ ] selected disposition propagated to target, requirements and architecture gates.
