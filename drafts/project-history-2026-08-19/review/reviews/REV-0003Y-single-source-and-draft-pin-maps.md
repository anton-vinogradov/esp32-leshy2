# REV-0003Y — single-source generator and first draft pin maps

- Статус: **Проведено ревью generator foundation и structural scope; complete architecture review не проведено**
- Дата: 2026-08-17
- Decision: [`DEC-0042`](../decisions/DEC-0042-single-source-architecture-data.md)
- Finding: [`FND-0050`](../findings/FND-0050-legacy-radio-lifecycle-risk.md)
- Artifact: [`G2F-pin-ledger`](../architecture/generated/G2F-pin-ledger.md)

## Проверенный scope

| Проверка | Результат |
|---|---|
| exact compute boundary | S3/C5 считаются по WROOM-1U variants, RP — по bare QFN60; module-internal C5 GPIO15 отвергается |
| actual peripheral contacts | U214, E01 reference, CC1101RGPR, TCA9535PWR и SN74HC595PWR имеют exact physical contact rows |
| two comparable maps | `G2F-2R` и `G2F-3D` используют один semantic scope и один device inventory |
| GPIO collision/accounting | validator подтверждает used/reserved/free equality для каждого programmable instance |
| straps | каждый allocated S3/C5 strap имеет reset proof; остальные явно reserved |
| recovery/diagnostics | обязательные EN/BOOT/USB либо RUN/SWD/USB/BOOTSEL contacts проверены по exact device |
| peer identity | exact peers существуют; programmable inter-domain links reciprocal; неизвестные parts помечены `abstract:` |
| drift prevention | `--check` сверяет generated ledger; CI и семь regression tests проходят |
| target architecture selected | нет |
| KiCad/physical placement authorized | нет |

## Исправления primary-source self-review

| Draft value до проверки | Проверенный результат | Исправление |
|---|---|---|
| S3-WROOM-1U `18×19.2×3.1 mm` | datasheet v1.8: `18×19.2×3.2 mm` | `devices.json` исправлен |
| C5-WROOM-1U `18×24.4×3.2 mm` | datasheet v1.2: `18×21.2×3.3 mm` | `devices.json` исправлен до physical-layout use |
| TCA9535 `SCPS201J`, SN74HC595 `SCLS041O` | current TI documents `SCPS201E`, `SCLS041J` | source versions исправлены |
| CC1101 ошибочно обобщён как NRND вместе с nRF24 | TI order page: `CC1101RGPR ACTIVE`; Nordic: nRF24 NRND | lifecycle data и `FND-0050` исправлены; gap оставлен только nRF |
| `G2F-2R` ставил PTT на strap `S3 GPIO3`, оставляя `GPIO9` free | PTT не требует strap и должен оставаться доступным во время reset | PTT перенесён на `GPIO9`, `GPIO3` reserved; лишняя isolation cost/risk удалена |

## Self-review двух карт

`G2F-2R` использует два compute domains. S3 имеет `32 used + 4 reserved + 0
free`, C5 — `17 + 4 + 0`. Shift register сохраняет отдельные `CE/CSN` трёх
nRF и `CSn` CC1101, а агрегированный IRQ требует отдельного safe logic proof.
Карта дешевле и проще по images, но не доказала worst-case FIFO/IRQ latency
одного C5 одновременно с native radio и IR.

`G2F-3D` использует RP2354A для 3×nRF, CC1101 и voice deadlines. S3 имеет
`33 + 3 + 0`, C5 — `11 + 5 + 5`, RP — `30 + 0 + 0`. Отдельные nRF IRQ
сохраняют source identity и C5 получает запас, но S3/RP не имеют ни одной
general-purpose ноги, а третий image, power/clock/service и physical burden
ещё не посчитаны совместно.

## Не получает статус «Проведено ревью»

Ни одна карта пока не является complete owner/pin architecture. Открыты exact
nRF production choice, CC RF network, display/touch, microSD socket, codec,
voice, IR, Unit protection/mux, hard STOP implementation, controller concurrency,
memory/traffic/power и HIL. Generated ledger честно выводит эти gaps.

Следующий шаг — закрыть exact devices, которые меняют electrical/pin/power/RF
feasibility, затем провести одинаковые controller/timing/power проверки обеих
карт. Только после этого возможна рекомендация одной рабочей карты владельцу.
