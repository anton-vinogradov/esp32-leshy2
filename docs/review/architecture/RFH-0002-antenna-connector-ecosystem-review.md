# RFH-0002 — antenna connector ecosystem review

- Статус: **Проведено ревью фактов; вариант B принят `DEC-0050`**
- Дата: 2026-08-17
- Prerequisite: [`RFH-0001`](RFH-0001-module-to-external-sma-interface-review.md)
- Proposal: [`IMP-0042`](../improvements/IMP-0042-external-sma-gender-and-feed-policy.md)
- Decision: [`DEC-0050`](../decisions/DEC-0050-ecosystem-aligned-sma-polarity.md)

## Проверяемый вопрос

Нужно отделить три разных утверждения, которые нельзя подменять друг другом:

1. разъём широко встречается в некоторой рыночной экосистеме;
2. конкретная антенна электрически подходит данному тракту;
3. конкретная антенна сохраняет допустимые gain/EIRP/certification bounds.

Популярность polarity помогает с покупкой и заменой, но сама по себе не
доказывает ни полосу, ни согласование, ни допустимость передачи.

## Проверенные экосистемы

| Port group | Что показывают первичные источники | Вывод для Leshy2 |
|---|---|---|
| `S3-2G4`, `C5-2G4/5` | TE называет Wi-Fi routers/access points типичным применением RP-SMA; при этом текущий TE antenna catalogue предлагает одни и те же Wi-Fi families и с RP-SMA plug, и со standard SMA plug | RP-SMA имеет наиболее знакомую consumer-Wi-Fi экосистему, но standard SMA не создаёт дефицита сам по себе |
| `N24-0/1/2` | официальный Ebyte E01 guide перечисляет nRF modules с `SMA-K`, а рекомендуемые внешние 2.4 GHz antennas — с `SMA-J`; это standard-SMA convention в собственной E01 ecosystem | переносить consumer Wi-Fi RP-SMA на nRF только из-за частоты 2.4 GHz оснований нет |
| `CC-SUB` | текущий TE catalogue показывает 433/868/915 MHz families одновременно в RP-SMA и standard SMA variants | уникальной «общепринятой» polarity нет; standard SMA остаётся нормальным industrial/reference выбором |
| `VOICE-V/U` | handheld-radio aftermarket использует разные centre-contact conventions; точный SA518 antenna MPN пока не выбран | нельзя объявлять одну polarity наиболее распространённой до shortlist exact dual-band antennas |
| `RX-FM/SW` | это product receiver accessory, а не Wi-Fi ecosystem | standard SMA совместим с принятой общей RF/instrument convention; exact telescopic/whip profile всё равно требует проверки |
| `RX-AM/LW` | antenna является специальным short loop/pod или qualified buffered pod | connector выбирается как product interface; популярность generic whip неприменима |

Ebyte guide датирован 2018 годом и не является доказательством текущего склада
конкретных antenna MPN. Он используется только как manufacturer evidence того,
что E01/nRF ecosystem исторически построена вокруг standard SMA-K/SMA-J, а не
как production sourcing approval. Exact antenna BOM требует текущей
orderability и qualified alternate.

## Почему polarity не является безопасным кодированием диапазона

По TE standard SMA plug имеет male centre pin, а standard jack — female centre
socket. В RP-SMA centre contacts обращены: RP plug имеет socket, RP jack — pin;
наружная threaded coupling остаётся SMA. Поэтому несовместимые standard/RP
пары могут начать механически навинчиваться, но получить socket-to-socket без
RF contact либо pin-to-pin collision. Это не защита от неправильной антенны.

Независимо от решения обязательны permanent port label, цветной collar/cap,
antenna-profile manifest, TX interlock и запрет TX без подтверждённой нагрузки.

## Qualification gate перед заморозкой BOM

Для каждого port group нужно не искать «антенну с правильной гайкой», а
сформировать минимум два реально закупаемых reference MPN и проверить:

- покрытие полной рабочей полосы, impedance/VSWR и radiation profile;
- gain и regulatory profile; для module-certification baseline Espressif
  рекомендует не превышать `2.33 dBi` для S3 и `3.86 dBi @ 2.4 GHz` /
  `3.65 dBi @ 5 GHz` для C5;
- механический envelope, соседние antennas, hinge/swing и транспортные caps;
- conducted path loss, VNA return loss на собранном устройстве и target HIL;
- текущую orderability, стоимость и хотя бы один qualified alternate.

Следовательно, случайная «router 5 dBi» antenna не становится допустимой для
S3/C5 только потому, что имеет распространённый RP-SMA plug.

## Вывод

Есть обоснованный ecosystem-aligned кандидат: RP-SMA только для двух native
Wi-Fi ports S3/C5, standard SMA для остальных семи. Вариант «все пять
2.4/5 GHz ports RP-SMA» не следует из фактов: три nRF принадлежат Ebyte/nRF
ecosystem, а не Wi-Fi-router ecosystem.

Факт-review получает **«Проведено ревью»**. Владелец принял ограниченный mixed
candidate в `DEC-0050`; exact antenna MPN и orderability не закрыты.

## Первичные источники

- [TE RP-SMA overview and common applications](https://www.te.com/en/plp/rp-sma-rf-connectors/Y45Kw.html)
- [TE Connectivity current antenna catalogue](https://www.te.com/content/dam/te-com/documents/consumer-devices/global/te-connectivity-antenna.pdf)
- [TE RF coaxial connector gender naming](https://www.te.com/content/dam/te-com/documents/appliances/global/AN-00601%20RF%20Coaxial%20Connector%20Gender%20Naming.pdf)
- [Ebyte E01 series and antenna guidance](https://www.ebyte.com/Uploadfiles/Files/2019-4-19/201941917633515.pdf)
- [Espressif ESP32-S3-WROOM-1/1U v1.8](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf)
- [Espressif ESP32-C5-WROOM-1/1U v1.2](https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.pdf)
