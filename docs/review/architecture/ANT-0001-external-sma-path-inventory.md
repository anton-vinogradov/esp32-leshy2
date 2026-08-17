# ANT-0001 — external-SMA path and frontend inventory

- Статус: **Проведено ревью фактов; exact count ожидает решение IMP-0041**
- Дата: 2026-08-17
- Основание: [`DEC-0048`](../decisions/DEC-0048-external-sma-antenna-bank.md)
- Legacy geometry: [`AUD-0013`](../audits/AUD-0013-legacy-layout-generator-reuse.md)
- Finding: [`FND-0055`](../findings/FND-0055-si4732-two-antenna-input-domains.md)
- Proposal: [`IMP-0041`](../improvements/IMP-0041-exact-external-sma-count.md)

## Проверенная граница

`SMA` здесь означает доступный снаружи механический antenna endpoint. Это не
означает, что все девять портов электрически взаимозаменяемы или имеют одну
полосу, импеданс, допустимую мощность и antenna type. Каждый порт получает
постоянный path/band label, а TX-capable ports дополнительно требуют exact
antenna/load manifest до keying.

| Logical path | Реальный RF-контакт | External endpoint consequence | Статус |
|---|---|---|---|
| S3 native 2.4 GHz | `ESP32-S3-WROOM-1U` external-antenna variant | один dedicated SMA через короткий qualified coax | один endpoint подтверждён |
| C5 native 2.4/5 GHz | standard `ESP32-C5-WROOM-1U` использует module `ANT1`; `ANT2` отключён | один dual-band dedicated SMA; второй C5 SMA не возникает | один endpoint подтверждён |
| nRF0/nRF1/nRF2 | три `E01-ML01IPX` reference connectors | три independent short-pigtail SMA; switch/shared radiator запрещены `DEC-0048` | три endpoints подтверждены |
| CC1101 | differential `RF_P/RF_N` плюс band-specific balun/matching/filter | один SMA возможен только после exact switched multiband frontend proof; external antenna/profile меняется по полосе | один endpoint — рабочая гипотеза, frontend blocking |
| SA518 | physical module pin 7 `ANT`, manufacturer требует 50-ohm antenna | один VHF/UHF SMA с exact dual-band antenna/filter/HIL | один endpoint подтверждён для SA518 reference |
| Si4732 FM/SW | physical pin 1 `FMI`, block diagram прямо маркирует `FM/SW ANT` | собственный external whip/SMA frontend | отдельный input domain подтверждён |
| Si4732 AM/LW | physical pin 3 `AMI`, block diagram прямо маркирует `AM/LW ANT` | собственный external loop/pod SMA frontend; не generic 50-ohm coax port | отдельный input domain подтверждён |

Итого для полного on-board scope: **девять external endpoints**, если оба
Si4732 input domains имеют собственный порт; **восемь**, если их объединить
через дополнительно квалифицируемый switch/frontend и потребовать смену
external antenna profile.

## Почему Si4732 нельзя считать одним generic SMA

Официальный short datasheet `Si4732-A10` показывает две физические ноги и две
разные LNA/AGC ветви: `FMI` для `64–108 MHz FM` и `2.3–26.1 MHz SW`, `AMI` для
`153–279 kHz LW` и `520–1710 kHz AM`. Это не два одновременно работающих
receiver: mode выбирается внутренним mux, поэтому два connector не создают
новую concurrency obligation. Они сохраняют разные antenna/frontend
требования одного receiver.

Skyworks `AN383` отдельно предупреждает для перечисленных там Si473x AMI
frontends, что tuning зависит от полной паразитной ёмкости. Для 300 uH ferrite
loop в приведённом примере total allowable capacitance составляет около 29 pF,
включая 8 pF input capacitance. Таблица AN383 не называет Si4732-A10 явно,
поэтому число 29 pF является риск-ориентиром, а не перенесённой exact
specification. Оно доказывает, что прямой длинный 50-ohm SMA coax к
high-impedance ferrite loop нельзя принять без измерений. При внешней AM/LW
antenna допустимы только проверенные варианты, например direct plug-in
loop/pod с минимальной связью либо external air-loop transformer/buffer
profile; длина/ёмкость кабеля входят в manifest.

## CC1101: что сохраняется, а что отвергается

TI даёт разные balun/filter component sets для `315/433` и `868/915 MHz` и
рекомендует exact reference layouts. Один generic wideband balun плюс четыре
условных индуктора из legacy drawing не является доказанным multiband
frontend. Один внешний SMA всё же остаётся правдоподобной целью, потому что
CC1101 работает в одной полосе за раз и band-specific 50-ohm branches можно
свести qualified switch topology. Но до schematic/VNA/conducted proof это
ровно один **candidate endpoint**, а не закрытая RF реализация.

## Сверка со старым макетом

Legacy generator рисовал девять SMA:

- main/front: S3, CC1101, voice, onboard LoRa, один Si4732;
- rear/C5: C5 и три nRF.

После удаления onboard LoRa механически освобождается один slot. Полный
Si4732 требует второй antenna domain, поэтому девятипортовый envelope можно
сохранить без добавления десятого отверстия: бывший `LoRa` slot становится
`RX-AM/LW`, а прежний `Si4732` уточняется как `RX-FM/SW`.

## Внешние аксессуары и неантенные интерфейсы

U214/другой LoRa Cap, external GNSS и U216 NFC владеют своими antennas и не
увеличивают base SMA bank. IR — оптический TX/RX, а iButton — контактный
интерфейс; они не считаются SMA.

## Следующие gates

1. Решить `IMP-0041`: 9 dedicated endpoints либо 8 с shared Si4732 port.
2. После решения записать exact port identities в machine source и
   адаптированный generator.
3. Отдельно синтезировать CC1101 switched frontend по exact TI references;
   legacy proxy topology не переносить.
4. Квалифицировать Si4732 antenna pods, cable capacitance, ESD, noise pickup и
   sensitivity для каждого принятого mode.
5. Затем выбрать SMA gender/mounting, cable assemblies и физическую раскладку.

## Первичные источники

- [Skyworks Si4732-A10 short datasheet](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-shorts/Si4732-A10-short.pdf)
- [Skyworks AN383 antenna/layout guide](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/application-notes/AN383.pdf)
- [TI CC1101 datasheet](https://www.ti.com/lit/ds/symlink/cc1101.pdf)
- [TI DN017 868/915 MHz matching note](https://www.ti.com/lit/an/swra168a/swra168a.pdf)
- [NiceRF SA518 rev 1.1](https://www.nicerf.com/pdf/sa518-1w-uv-dual-frequency-walkie-talkie-module-v1.1.pdf)
