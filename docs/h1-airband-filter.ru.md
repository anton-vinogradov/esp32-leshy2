# H3-R2.3 · входной фильтр Airband

Большой покупной `BPF-A127+` заменён точной фабрично устанавливаемой LC-сетью без ослабления принятой маски.

![Airband filter verification](images/h1-airband-filter.svg)

## Результат

- Все `1024` предельные комбинации эффективных допусков проходят; минимальный расчётный запас — `0.187 дБ`.
- Фильтр содержит `18` деталей и `10` точных MPN; все доступны JLCPCB как SMT для Standard PCBA с MOQ 1 на 2026-08-31.
- Материалы фильтра для одного устройства стоят `$1.6736` вместо дорогого готового фильтра.
- Это ещё не production freeze: малый запас требует повторить ту же маску в H6 с паразитиками реальной разводки, а H8 подтверждает результат VNA.

## Точная устанавливаемая группа

| Exact MPN | JLCPCB | Quantity | Role |
|---|---|---:|---|
| `LQW2BASR22G00L` | `C527968` | 2 | S1/S3 220-nH series arms |
| `LQW2BAS47NG00L` | `C162657` | 2 | S1/S3 47-nH series arms |
| `LQW2BAS22NG00L` | `C2042201` | 4 | P1/P2 equal 22-nH parallel pairs |
| `LQW2UASR56F00L` | `C907989` | 1 | S2 560-nH arm |
| `GJM1555C1H5R7WB01D` | `C2220921` | 1 | S1 5.7-pF arm |
| `GCM1555C1H121FA16D` | `C126496` | 2 | P1/P2 120-pF branches |
| `GCM1555C1H200FA16D` | `C437436` | 2 | P1/P2 20-pF branches |
| `GJM1555C1H1R4WB01D` | `C2181496` | 2 | P1/P2 1.4-pF fine branches |
| `CC0402BRNPO9BN2R8` | `C1853353` | 1 | S2 2.8-pF arm |
| `GJM1555C1H5R8WB01D` | `C2177031` | 1 | S3 5.8-pF arm |

## Следующий gate

H6 uses the reserved compact tuning island and fitted/DNP trim footprints, extracts routed pads, traces, vias, coupling, shield and enclosure parasitics, and reruns the same mask before the exact-one order. H8 VNA measurement confirms or retunes the fitted/DNP state on the assembled prototype.
