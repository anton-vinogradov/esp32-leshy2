# Сквозная сверка железа и прошивки Leshy2

[English](hwfw-reconciliation.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md)

H2.7 связывает физический H1, production ECAD и вход firmware F2 одним проверяемым контрактом.

| Граница | Проверено | Результат |
|---|---:|---|
| H1 ↔ instance ledger ↔ symbols | 1034 строк / 1032 identities | 0 MPN/contact mismatches |
| root hierarchy nets | 266 | все присутствуют в native netlists |
| M1 UI ↔ RF | 80 контактов / 51 nets | построчно идентичны |
| architecture ↔ KiCad | 130 allocations | 0 pin/net mismatches |
| H2 export ↔ firmware F2 | 125 MCU-контактов | byte-identical, временные pins запрещены |

## Исправленные несоответствия

- `H2.7.2-F01` — instance ledger называл число логических функций числом физических контактов в десяти expanded-pad/module случаях → теперь каждая строка отдельно хранит logical_contact_count и physical_pcb_contact_count, а contact_count означает реальные lands корпуса или модуля
- `H2.7.4-F01` — PACK UART назывался PACK_SERVICE_UART_TX/RX в allocations, но PACK_ADMISSION_UART_TX/RX в KiCad, fixture pads и fixed routes → allocations и firmware F2 переведены на уже установленное каноническое имя PACK_ADMISSION_UART_TX/RX

✅ **Проведено ревью:** H2.7 закрыт, сквозных несоответствий не осталось.

[Машинное evidence](../hardware/ecad/generated/H2-REV75-hwfw-consolidated.json).
