# H2-R2.1.3 · native-схемы R2 в KiCad

**Пройдено 31 августа 2026 года.** Текущая архитектура R2 теперь существует
как два native-проекта схем KiCad 10, сгенерированных из точных authority
компонентов, контактов, экземпляров и nets. Сохранённые single-RP проекты R1
генератор не читает.

| Результат | Значение |
|---|---:|
| Native-проекты / sheets в графе проектов | 2 / 22 |
| Заполненные логические sheets | 18 |
| Устанавливаемые symbol instances | 1 183 |
| Контролируемые физические symbol pins | 4 243 |
| Подключённые / явные no-connect pins | 4 006 / 237 |
| Канонические nets | 816 |
| Ошибки / предупреждения KiCad ERC | 0 / 0 |
| PCB, placement или routing-файлы | 0 |

Проекты:

- [`LESHY2-UI-R2`](../hardware/ecad/kicad/LESHY2-UI-R2/) — UI/display S3,
  C5, Hub RP, три полных nRF24-острова, storage и передняя safety-часть;
- [`LESHY2-RF-R2`](../hardware/ecad/kicad/LESHY2-RF-R2/) — RF RP, питание,
  CC1101, VHF/UHF, broadcast/Airband, audio, expansion и TX evidence.

Точный 50-контактный шлейф дисплея входит прямо в
`FH34SRJ-50S-0.5SH(50)` на `LESHY2-UI-R2`; отдельного проекта переходника нет.

## Airband в принципиальной схеме

Receive-only тракт 118–137 МГц больше не является заглушкой на блок-схеме. Он
содержит точные складские детали nominal-state H2, полную LC tuning-сеть,
`PGA-103+`, `LT5560EDD#TRPBF`, официальные трансформаторы `WBC1-1TLC` /
`WBC16-1TLC` и `SI5351A-B-GTR`. Парные `HMC544AETR` изолируют оба конца
преобразующего тракта, поэтому выключенная ветвь не нагружает обычный FM/SW.
LO использует отдельный PIO-I²C на GPIO28/29 RF RP с подтяжками от
`3V3_AIR_SWITCHED`, что устраняет off-domain back-power. Reset-state остаётся
fail-off и fail-direct.

Точные LC-номиналы — nominal fitted-state H2, а не production-freeze фильтра.
Обновлённый tolerance/Q sweep даёт 3,10 дБ номинальной худшей потери, но
4,67 дБ в stress и недостаточное stress-подавление на 155 и 180 МГц. H3 должен
перенастроить и доказать эту сеть до routed extraction в H6.

## Что разрешает результат

Checkpoint разрешает только native-логические схемы. Он не создаёт PCB,
placement, routing, fabrication output или заказ. Cross-sheet-сверка прошла в
[результате H2-R2.1.5](h2-acceptance.ru.md); теперь H3 фиксирует ту же
machine-readable границу железа и прошивки.

[Сгенерированный manifest проектов](../hardware/ecad/generated/H2-R2-native-kicad-projects.json) ·
[native net-ledger](h2-r2-net-ledger.ru.md) ·
[роадмап](roadmap.ru.md)
