# DEC-0009 — бортовой ES8311 с аппаратным analog bypass

- Статус: **Принято владельцем проекта**
- Этап: 2 — scope; pin, electrical и firmware proof — этапы 3–8
- Дата принятия: 2026-08-16
- Принимает: `IMP-0009`, вариант A из `FND-0003`
- Затрагивает: `C-RX-07`, `C-VHF-04`–`C-VHF-07`, hardware, firmware, BOM и тесты

## Контекст

Legacy firmware заявляет запись и цифровую обработку RX-звука, генерацию TX-аудио и кросс-бэнд Si4732 → SA868, но legacy hardware оставляет MCU вне audio-path. Сравнительное ревью `REV-0002E` показало, что самый узкий вариант, восстанавливающий все перечисленные mono-пререквизиты без незапрошенного stereo, — ES8311 с аппаратно безопасными analog bypass-путями.

## Решение

- на основную PCB добавляется mono ADC+DAC codec **ES8311**;
- существующий `U33` выбирает RX-источник `SI_AUDIO` или `SA_AF`, а его выход одновременно доступен ADC кодека;
- перед PAM8302 добавляется 2:1 analog selector, аппаратный default которого — прямой analog RX → speaker; digital branch проходит exact differential-to-single-ended topology из `IMP-0046`;
- между electret mic и `MIC_IN` SA868 добавляется второй 2:1 analog selector, аппаратный default которого — прямой mic → SA868;
- qualified DAC branch попадает на speaker или `MIC_IN` только после явного выбора соответствующего selector;
- PTT остаётся независимым TX-гейтом и не активируется самим codec или переключением audio selector;
- reset/crash S3 и выключенный либо неисправный codec не должны лишать устройство обычного прослушивания и голосовой связи;
- codec использует четыре I²S-сигнала без выделенного MCLK, с BCLK как кандидатом внутреннего clock source ES8311; I²C уже существует;
- предварительные GPIO2/6/42/46 были рассчитаны на исторический перенос 3×nRF24 и IR на C5 и больше не являются предпочтительной pin map. Четыре I²S-сигнала остаются обязательным demand; их размещает общий этап-3 budget после `DEC-0023`;
- три медленных управляющих сигнала codec/selectors должны войти в общую pin/safety-map. Последующий аудит обнаружил конфликт исходного размещения на `U13.P10..P17` с UI matrix (`FND-0006`). Current `G2F-3I` closes the control count as `P10=CODEC_PWR_EN`, `P11/P12=selectors`. `FND-0065` corrects the old wording: ES8311 `CE` is an I2C-address strap, not enable/reset; `P10` controls an external codec power switch.

## Firmware-контракт

Архитектура предоставляет один двунаправленный mono audio backend со следующими режимами:

- `ANALOG_BYPASS`: обычный RX и mic voice работают без codec;
- `CAPTURE_SI` и `CAPTURE_SA`: выбранный через `U33` источник поступает в ADC;
- `PLAY_LOCAL`: DAC явно выбран на speaker;
- `INJECT_SA`: DAC явно выбран на `MIC_IN`, но не выдаёт PTT;
- `RELAY_SI_TO_SA`: ограниченный buffer/DSP path; только разрешённый профиль «Лаборатории».

Сам SA868 остаётся half-duplex. Архитектурный пререквизит не означает автоматического включения всех legacy-функций: каждая из них всё ещё проходит отдельное решение `include` / `conditional` / `defer` / `exclude-proven`, acceptance test и, для TX, гейты `DEC-0002`/`DEC-0003`.

## Статус связанных возможностей

`C-RX-07` и `C-VHF-04`–`C-VHF-07` больше не заблокированы отсутствием выбранной audio-архитектуры. Их статус — **conditional**: решение `DEC-0009` принято, но электрическая реализация, firmware и тесты ещё не доказаны. Cross-band relay дополнительно остаётся выключенным по умолчанию и относится в «Лабораторию» до сценарной и правовой проверки.

## Обязательные доказательства

1. Pin audit подтверждает четыре пригодных прямых GPIO S3 для I²S и отдельные safe control lines в принятой полной компоновке независимо от nRF24 owner.
2. ES8311 стабильно работает от BCLK без отдельного MCLK в одновременном ADC+DAC режиме на зафиксированной версии ESP-IDF/`esp_codec_dev`.
3. Hardware defaults обоих selectors измерением подтверждают analog RX и electret mic при reset, watchdog и power-off codec.
4. Измерены min/nominal/max уровни Si4732, SA868 `AF_OUT` и `MIC_IN`; исключены clipping, недопустимая нагрузка и опасная инжекция.
5. Проверены gain/noise/SNR, pop/click, latency, EMI и одновременная работа Wi-Fi, display, SD, PA SA868 и codec clocks.
6. WAV, decoder fixtures, DTMF, AFSK/AX.25, parrot и разрешённый relay проходят установленные критерии без overrun.
7. Ни codec, DMA, SD, selector, watchdog, ни reset не могут самостоятельно поднять или удержать PTT.
8. Полная BOM/PCBA-дельта проверена на `1/10/100/1000`, включая пассивы, площадь, assembly и test time.

До выполнения этих доказательств нельзя объявлять `FND-0003` полностью закрытой на уровне реализации или обещать связанные возможности как готовые.

## Стоимостная граница

Снимок `IMP-0009` давал ориентир для ES8311 и двух selectors около `$0.70` по low-volume unit prices и `$0.43` на tier 100. `FND-0065` показал, что эта оценка не включает exact differential-output conditioning; до выбора `IMP-0046` и нового BOM она историческая и не является текущей PCBA-оценкой.

## Exact-contact amendment 2026-08-17

[`AUDIO-0001`](../architecture/AUDIO-0001-es8311-exact-electrical-fit.md) and
[`REV-0005B`](../reviews/REV-0005B-es8311-digital-fit-and-analog-gap.md) verify
the exact QFN-20 digital contact fit without changing GPIO budget. The scope
decision for onboard ES8311 and hardware analog bypass remains accepted.
`IMP-0046` is a narrower open implementation decision: how to preserve the
fully differential `OUTP/OUTN` signal when both legacy consumers are
single-ended.
