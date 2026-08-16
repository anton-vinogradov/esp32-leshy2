# DEC-0016 — conditional target SA518 dual-band с SA868S fallback

- Статус: **Принято владельцем; supply topology уточнена `DEC-0025`**
- Дата: 2026-08-16
- Источник: `IMP-0014`, вариант A
- Закрывает на уровне требований: `FND-0012`
- Затрагивает: `REQ-VHF-0001`, BOM/RF/antenna/power, APRS/AX.25, target/current документы

## Контекст

Текущий SA868S fallback является UHF-only 2 W-class модулем. Новый NiceRF SA518 в одном SMD backend одновременно поддерживает VHF 136–174 MHz и UHF 400–470 MHz, но имеет несовместимый footprint, примерно на 40% большую площадь, более низкий 1 W peak и пока недоказанные цену/AVL для производства.

## Решение

1. Предпочтительный target voice-radio backend — **NiceRF SA518-class dual-band**: half-duplex analog FM, VHF 136–174 MHz и UHF 400–470 MHz, low/high nominal profiles 0.5/1 W в пределах фактически измеренной revision и регионального допуска.
2. SA518 не становится безусловно зафиксированным BOM-компонентом до stage-4 qualification exact part/revision:
   - supplier/AVL, tier pricing и lifecycle;
   - footprint, reflow, power and thermal budget;
   - protocol identity/readback/error behavior;
   - conducted RF, harmonics/spurs, dual-band antenna/matching and enclosure desense;
   - audio gain/filter path и production test time.
3. До прохождения gate текущий SA868S-UHF остаётся fallback. Если SA518 не проходит, production profile честно становится UHF-only 400–470 MHz; 470–480 MHz остаётся conditional on-target proof. UI/manifest никогда не приписывает fallback VHF/dual-band возможности.
4. Владелец осознанно принимает обмен UHF peak 2 W-class → 1 W ради VHF+UHF в одном модуле. Это capability trade, а не экономия без потерь по `DEC-0005`.
5. Текущий tsCircuit SA868S с исправленными `PTT/PD/H-L` safe defaults не заменяется молча: новый footprint появляется только как отдельный stage-3/4 artifact после pin/power/RF review.
6. Proprietary SA518 short-data mode квалифицируется отдельно и не называется AX.25/APRS. VHF лишь создаёт технический RF/audio путь; protocol interoperability, callsign/licence и modem HIL остаются обязательными.
7. Оба backend наследуют один и тот же conservative TX contract: no-profile=RX-only, hardware low/off defaults, explicit arming, bounded PTT, independent STOP и actual-TX indication.
8. По `DEC-0025` SA518 использует отдельный BAT-fed `VVOICE` около 4.0 V; SA868S fallback имеет отдельный stuffing/supply/manifest profile и не смешивается с SA518 как один runtime-неизвестный backend.

## Что решение не исправляет автоматически

- External SMA не создаёт licence-exempt PMR446 equipment (`FND-0014`).
- VOX остаётся `defer` без mic capture или доказанной специальной module variant (`FND-0013`).
- PCA9555 не становится независимым STOP/PTT kill (`FND-0007`).
- Analog half-duplex backend не предоставляет true duplex repeater, DMR/C4FM/dPMR или vocoder.
- Price/availability нового SA518 и готовая PCB не объявлены доказанными.

## Критерий fallback

Stage-4 review фиксирует измеримый pass/fail по каждому gate. Fallback включается при отсутствии надёжной поставки/цены, несовместимом protocol, провале RF/thermal/power/audio tests или невозможности разместить dual-band path без потери уже принятых функций. Причина и потерянные VHF-возможности публикуются; fallback не называется dual-band.

## Первичные источники

- [NiceRF SA518 product page](https://www.nicerf.com/walkie-talkie-module/sa518-uv-dual-frequency-walkie-talkie-module.html)
- [NiceRF SA518 datasheet rev. 1.1](https://www.nicerf.com/pdf/sa518-1w-uv-dual-frequency-walkie-talkie-module-v1.1.pdf)
- [NiceRF SA868S datasheet rev. 1.7](https://www.nicerf.com/upload/20250730/550a4fb20f0ddcdaf5c265201a056c73.pdf)
