# REV-0004Y — exact fast-display shortlist review

- Статус: **Проведено ревью фактов; IMP-0045 и production MPN открыты**
- Дата: 2026-08-17
- Evidence: [`DSP-0003`](../architecture/DSP-0003-exact-fast-display-shortlist.md)
- Finding: [`FND-0062`](../findings/FND-0062-old-four-inch-display-is-not-qspi.md)
- Proposal: [`IMP-0045`](../improvements/IMP-0045-new-35in-qspi-display-class.md)

## Проверено

| Проверка | Результат |
|---|---|
| old 4-inch meets task workload | yes, as low-rate A0 control |
| old 4-inch exposes direct QSPI | no: exact ST7796S module is 1-bit SPI |
| 4-inch `SPI+RGB` means QSPI pixels | no: SPI config plus 24-bit RGB data |
| ready 4-inch host-QSPI exists | yes through BT817 EVE, but cost/width/controller burden is material |
| direct-QSPI portrait candidate exists | yes: two 3.5-inch 320×480 IPS+touch controller families |
| official firmware driver path | yes: Espressif AXS15231B and ST77922 components |
| integrated dev board equals production panel | no |
| active-area loss disclosed | yes: about 23% versus old 4-inch |
| exact target silently frozen | no: owner choice, two-source and HIL remain open |

## Результат

Фактический shortlist получает **«Проведено ревью»**. Рекомендуется новый
3.5-inch direct-QSPI class; owner decision and exact production qualification
remain open.
