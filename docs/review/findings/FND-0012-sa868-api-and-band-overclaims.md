# FND-0012 — legacy приписывает UHF SA868 режимы и диапазоны, которых его API не доказывает

- Статус: **Открыто; требуется решение `IMP-0014` по voice-radio backend**
- Серьёзность: нельзя переносить `C-VHF-01`–`C-VHF-06` как готовый единый контракт
- Затрагивает: `REQ-VHF-0001`, BOM/RF/antenna, APRS/AX.25, scan UI и firmware/HIL
- Обнаружено: 2026-08-16

## Несоответствие идентичности и диапазона

Текущий схемный артефакт и legacy называют `SA868-U`/`C3001507` и подразумевают UHF 400–480 MHz. Актуальный официальный документ NiceRF называется SA868S и прямо говорит, что UHF 400–480 и VHF 134–174 — **два опциональных исполнения**, не одновременный dual-band одного установленного модуля.

Внутри того же datasheet есть ещё одна граница: RF specification указывает UHF до 480 MHz, но публичный `AT+DMOSETGROUP` разрешает TX/RX только 400–470 MHz. Поэтому 470–480 MHz нельзя обещать как управляемый product range без точного manufacturer/part/revision proof и положительного теста.

Текущая PCB содержит UHF-вариант. Следовательно, распространённые VHF/2 m сценарии нельзя получить настройкой UART; legacy сам отмечал, что обычный VHF APRS profile этим backend не покрывается.

## Несоответствие scan API

Штатный SA868S UART предоставляет:

- `S+<frequency>` → только `signal present / no signal`;
- `AT+RSSI?` → vendor-relative число без опубликованного преобразования в dBm;
- установку CTCSS/CDCSS для TX/RX, но не API определения неизвестного принятого tone/code.

Поэтому «carrier/RSSI» возможны с честной семантикой, а CTCSS/DCS tone scan не является штатной функцией модуля. Возможный обход — host decode через `AF_OUT`→ES8311 при доказанной передаче sub-audio и отключении мешающих фильтров; это conditional HIL, не UART capability.

## Влияние

- Для сохранения текущего SA868S baseline безопасная безусловная граница — квалифицированный UHF 400–470 MHz profile.
- 470–480 MHz, tone scan и числовая dBm-калибровка условны on-target proof.
- VHF voice и обычные 2 m modem scenarios требуют другого backend.
- Новый NiceRF SA518 создаёт реальный dual-band обход без второго radio IC, но меняет footprint, power, antenna/filter qualification и peak power; варианты вынесены в `IMP-0014`.

## Условия закрытия

1. Владелец выбирает voice-radio direction из `IMP-0014`.
2. Exact installed module/variant/revision и protocol profile фиксируются в BOM и production manifest.
3. Requirement/UI отделяют vendor-relative RSSI, binary carrier scan и conditional host tone decode.
4. Любой заявленный край диапазона проходит conducted RF/HIL и applicable regional profile.

## Первичные источники

- [NiceRF SA868S datasheet rev. 1.7](https://www.nicerf.com/upload/20250730/550a4fb20f0ddcdaf5c265201a056c73.pdf)
- [NiceRF SA518 dual-band product page](https://www.nicerf.com/walkie-talkie-module/sa518-uv-dual-frequency-walkie-talkie-module.html)
- [NiceRF SA518 datasheet rev. 1.1](https://www.nicerf.com/pdf/sa518-1w-uv-dual-frequency-walkie-talkie-module-v1.1.pdf)
