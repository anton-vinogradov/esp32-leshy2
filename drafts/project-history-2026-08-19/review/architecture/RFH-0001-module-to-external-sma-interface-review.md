# RFH-0001 — module-to-external-SMA interface review

- Статус: **Проведено ревью фактов; polarity закрыта `DEC-0050`**
- Дата: 2026-08-17
- Decisions: [`DEC-0048`](../decisions/DEC-0048-external-sma-antenna-bank.md),
  [`DEC-0049`](../decisions/DEC-0049-nine-dedicated-external-sma-paths.md)
- Finding: [`FND-0057`](../findings/FND-0057-ebyte-ipx-mating-family-unproven.md)
- Proposal: [`IMP-0042`](../improvements/IMP-0042-external-sma-gender-and-feed-policy.md)
- Decision: [`DEC-0050`](../decisions/DEC-0050-ecosystem-aligned-sma-polarity.md)

## Проверенная граница

Из девяти внешних SMA только пять начинаются на on-module micro-coax
receptacle: S3, C5 и три nRF. Остальные четыре начинаются на PCB/front-end:
CC1101, SA518, Si4732 FMI и Si4732 AMI. Поэтому один generic `IPEX→SMA
pigtail` не описывает весь банк и не может стать общим BOM item.

| Path class | Exact исходный интерфейс | Что доказано | Что ещё нельзя замораживать |
|---|---|---|---|
| `S3-2G4` | ESP32-S3-WROOM-1U first-generation receptacle | официальный v1.8 прямо перечисляет mating U.FL, MHF I и AMC; 50 Ω, 2.4 GHz | harness length, lock, bulkhead side и antenna gain/MPN |
| `C5-2G4/5` | ESP32-C5-WROOM-1U `ANT1` first-generation receptacle | официальный v1.2 перечисляет U.FL/MHF I/AMC; 50 Ω, 2.4/5 GHz; `ANT2` default-disabled | harness, dual-band antenna/filters и certification evidence |
| `N24-0/1/2` | Ebyte E01-ML01IPX, manufacturer label `IPX` | официальный 2025 PDF показывает реальный module body и примерно 50 Ω external interface | документ не называет U.FL/MHF I/AMC, generation, receptacle MPN или mating dimensions; exact plug **не доказан** |
| `CC-SUB` | bare-IC differential RF plus switched frontend | один 50 Ω external endpoint является target | switch/matching/filter/launch и conducted proof |
| `VOICE-V/U` | SA518 pin 7 `ANT`, 50 Ω | один PCB-to-external feed | launch/cable/filter/protection/HIL |
| `RX-FM/SW` | Si4732 pin 1 `FMI` | отдельный receiving path | exact whip/front-end/ESD/noise profile |
| `RX-AM/LW` | Si4732 pin 3 `AMI` | отдельный direct loop/pod identity | это не generic long-coax path; transformer/buffer, capacitance и sensitivity открыты |

## Реальные harness references

I-PEX подтверждает, что MHF I работает до 9 GHz и предлагает MHF I→SMA Jack
evaluation harnesses, включая `8-25-0046` (1.13 mm coax, 100 mm) и
`8-25-0066` (1.37 mm, 100 mm). Это полезные измерительные references, а не
автоматический production BOM: 100 mm может быть длиннее необходимого, а
обычный MHF I рассчитан на внутреннее соединение и ограниченное число mating
cycles.

Для вибрации существует MHF I LK, который mates с MHF I receptacle и добавляет
mechanical lock. Amphenol имеет active готовые MHF I LK→standard-SMA-jack
bulkhead assemblies, например 50 mm `095-902-583-050` и IP67 100 mm
`095-902-584-100`. Они доказывают реализуемость locked/panel class, но exact
length, front/rear mount и IP rating зависят от ещё не принятого корпуса.

MHF I LK нельзя автоматически назначить Ebyte: сначала specimen должен пройти
microscope/dimension/fit check с документированным plug MPN, axial engagement,
retention и VNA through/reference measurement. Силовая фиксация кабеля к
корпусу/PCB обязательна; micro-coax receptacle не несёт нагрузку внешнего SMA.
У официального Ebyte PDF также остался embedded title от `E01-2G4M27D`, хотя
видимые страницы относятся к `E01-ML01IPX`; это не отменяет показанные размеры
и pins, но дополнительно запрещает достраивать отсутствующий connector MPN по
непроверенным metadata/картинке.

## Разделение gates

Сейчас допустимо решить только внешний mating convention и обязательные
electrical/qualification rules. Следующее остаётся в physical co-design:

- panel-mount против edge-launch для каждой из четырёх PCB paths;
- front/rear mount, anti-rotation, gasket/IP rating и panel thickness;
- exact 50/100 mm harness length после координат module↔panel;
- bend radius, strain relief, fold collision и service replacement;
- measured insertion/return loss каждого экземпляра feed path.

Это предотвращает повторение прежней ошибки: electrical feasibility не
замораживает корпус до G3, но G3 уже не сможет выбрать несовместимый connector
или скрыть непроверенный Ebyte `IPX`.

## Первичные источники

- [Espressif ESP32-S3-WROOM-1/1U v1.8](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)
- [Espressif ESP32-C5-WROOM-1/1U v1.2](https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.pdf)
- [Ebyte E01-ML01IPX 2025 specification](https://www.ebyte.com/Uploadfiles/Files/2025-1-16/2025116152734216.pdf)
- [I-PEX MHF I family and sample harnesses](https://www.i-pex.com/product/mhf-I)
- [Amphenol 095-902-583-050 active 50 mm MHF I LK→SMA jack](https://www.amphenolrf.com/en-us/part/095-902-583-050/9910/)
- [Amphenol 095-902-584-100 active IP67 100 mm reference](https://www.amphenolrf.com/en-us/part/095-902-584-100/9947/)
