# Digital levels, defaults и no-back-power

`H3.4.1` проверено: `73` машинных checks охватывают все `130` controller allocations, `13` групп digital interfaces, `13` quiet-state contracts и все шесть no-back-power invariants. Незакрытых аналитических findings и замен компонентов нет. Точный текущий маркер — `H3.5.1`.

## Гарантированные статические запасы

| Граница | Худший проверенный результат |
|---|---|
| Буферизованные LVC-тракты 3,3 В | `VOH-VIH >= 0.200 В`; `VIL-VOL >= 0.250 В` в гораздо более тяжёлом datasheet point 24 мА; фактическая нагрузка pull 10 кОм <=`0.329 мА` |
| Прямой common-rail CMOS | одна мгновенная шина; conservative high margin `0.155 В`, low margin `0.466 В` при минимальном проверенном rail |
| Open-drain SYS_I2C | pull-up 2,2 кОм требует <=`1.545 мА`; гарантированный low margin `0.400 В`; push-pull high не пересекает AON/main boundary |
| Service USB | проходят exact FSUSB42MUX power-off isolation и sense-only VBUS; USB differential SI ограничен в H3.4.3 и физически проверяется в H8, а не маскируется CMOS-расчётом |

У каждого switched domain есть off-safe enable, локальное состояние каждой линии и одно из точных доказательств: `Ioff`, разомкнутый powered-main switch, powered-off-high-Z I2C isolation либо same-rail/no-partial-power. Три nRF24 остаются независимыми, у каждого изолированы все шесть сигналов в обоих направлениях.

## Чего бумажное ревью не закрывает

Пять измерений остаются явными gates H8: powered-off leakage, осциллограммы reset/brownout, одновременное подключение service hosts, reverse current при неверном аксессуаре и уровни на дальнем конце M1 под нагрузкой. Бумажными passes они не названы.

Машинное evidence: [`H3-VRF41-digital-levels.json`](../hardware/verification/generated/H3-VRF41-digital-levels.json).
