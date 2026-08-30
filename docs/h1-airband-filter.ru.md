# H1-R2.3 · входной фильтр Airband

Проверена дешёвая и компактная замена большому `BPF-A127+`. H2 уже переносит её точный номинальный BOM в принципиальную схему, но production fitted-state ещё не заморожен.

![Airband filter feasibility](images/h1-airband-filter.svg)

## Что получилось

- Номинальный finite-Q расчёт проходит маску: худшая потеря в 118–137 МГц — `3.10 дБ` при лимите `4,5 дБ`; все именованные nominal stop-точки проходят.
- Stress sweep из `16386` наборов сохраняет passband (`4.67 дБ` при лимите `4,5 дБ`), но на 155 МГц худшее подавление — `17.85 дБ` вместо `20 дБ`. Поэтому точные складские H2 MPN приняты только как номинальный ECAD-state, а production fitted-state **не принят**.
- Сохраняется серийная LC-реализация, но её физическая ячейка увеличена до `24 × 11 мм`, получает via-fence и площадки альтернативных/DNP номиналов.
- Полоса 180–2200 МГц не доказывается lumped-моделью выше SRF: H3 использует ограниченную pre-layout-модель, H6 повторяет расчёт с извлечёнными паразитиками до заказа H7, а H8 закрывает production-state измерением VNA.

## Свидетельства фабричной реализуемости

Это проверенные складские MPN номинального H2 ECAD-state, но ещё не production BOM фильтра. H3 должен пересчитать номиналы по моделям производителя, H6 — зафиксировать предзаказный fitted/DNP-state после extraction, H8 — проверить production-state по VNA.

| Exact MPN | JLCPCB | Value | Current route |
|---|---|---|---|
| `LQW2UASR56F00L` | [`C907989`](https://jlcpcb.com/partdetail/MurataElectronics-LQW2UASR56F00L/C907989) | 560 nH +/-1%, 1008 | 155 stock / 152 available, MOQ 1, USD 0.272 at quantity 1 |
| `LQW2BASR22G00L` | [`C527968`](https://jlcpcb.com/partdetail/MurataElectronics-LQW2BASR22G00L/C527968) | 220 nH +/-2%, 0805 | 28 stock / 25 available, MOQ 1, USD 0.1324 at quantity 1 |
| `LQW2BASR33G00L` | [`C703717`](https://jlcpcb.com/partdetail/MurataElectronics-LQW2BASR33G00L/C703717) | 330 nH +/-2%, 0805 | 4573 stock / 4548 available, MOQ 1, USD 0.1158 at quantity 1 |
| `LQW15AN8N2G80D` | [`C307610`](https://jlcpcb.com/partdetail/MurataElectronics-LQW15AN8N2G80D/C307610) | 8.2 nH +/-2%, 0402 | 8484 stock / 8343 available, MOQ 1, USD 0.0975 at quantity 1 |
| `CS0805-R27J-S` | [`C108271`](https://jlcpcb.com/partdetail/ChilisinElec-CS0805R27JS/C108271) | 270 nH +/-5%, Q 48 witness, 0805 | 1972 stock, MOQ 1, USD 0.0549 at quantity 1 |

## Следующий gate

H2 переносит полную tuning-сеть в ECAD. H3 проверяет её с ограниченными pre-layout-паразитиками; H6 повторяет проверку с routed/extracted-паразитиками до заказа H7; H8 выбирает production fitted/DNP-state по VNA. При провале маски возвращаемся к точному покупному фильтру или меняем границу приёмника.

> Маркер результата: **H1-R2.3**. Текущий маркер H1 опубликован в роадмапе.
