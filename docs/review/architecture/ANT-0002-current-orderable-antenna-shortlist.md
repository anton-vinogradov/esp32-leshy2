# ANT-0002 — current-orderable antenna shortlist

- Статус: **Проведено ревью фактов и shortlist; production qualification не закрыта**
- Дата проверки: 2026-08-17; availability перепроверена перед IMP-0043
- Prerequisite: [`DEC-0050`](../decisions/DEC-0050-ecosystem-aligned-sma-polarity.md)
- Finding: [`FND-0058`](../findings/FND-0058-antenna-sourcing-and-qualification-gate-open.md)
- Proposal: [`IMP-0043`](../improvements/IMP-0043-profiled-antenna-kit.md)

## Цель и граница доказательства

Проверка ищет не абстрактную «антенну нужной частоты», а exact MPN с
правильным mating contact, рабочей полосой, gain/VSWR evidence и актуальным
commercial path. Дата и остаток дистрибьютора доказывают только возможность
заказать specimen; они не заменяют VNA, sensitivity/EIRP, coexistence,
enclosure и regulatory HIL на собранном Leshy2.

`DEC-0050` задаёт device-side интерфейс:

- `S3-2G4` и `C5-2G4/5`: RP-SMA jack с centre pin; antenna RP-SMA plug с
  centre socket;
- остальные семь endpoints: standard SMA jack с centre socket; antenna/pod
  standard SMA plug с centre pin.

Все указанные далее antennas внешние. M5 accessories продолжают использовать
собственные antennas и в этот shortlist не входят.

## Результат по группам

| Endpoint/profile | Primary specimen | Alternate | Paper result | Что остаётся до production |
|---|---|---|---|---|
| `S3-2G4`, `C5-2G4/5` | TE `001-0012`, RP-SMA, 2.4/5 GHz, 2 dBi, IP67; DigiKey showed 1,188 stocked units at recheck | TE `MAF94051`, RP-SMA, 2.4/5 GHz, 2.1/до 3.4 dBi; lifecycle Active but TE says not currently available | один stocked MPN можно купить в количестве 2 для обоих native-Wi-Fi paths; two-source production sourcing **не** закрыт | second independently stocked source, assembled cable/enclosure VNA, coexistence, certification profile and lot control |
| `N24-0/1/2` | Ebyte `TX2400-JW-5`, standard SMA, 2.4 GHz, 2 dBi, angled | Ebyte `TX2400-JZ-5`, standard SMA, 2.4–2.5 GHz, straight; JLC listing exists | один MPN покупается в количестве 3; две manufacturer-current геометрии найдены | independent current stock for both MPN, page/datasheet gain mismatch, exact nRF lot and three-path VNA/HIL |
| `CC-SUB/315` | TE `ANT-315-CW-HW-SMA`, 304–325 MHz, 0 dBi | TE `ANT-315-CW-HWR-SMA`, 305–325 MHz, tilt | две stocked exact standard-SMA позиции | assembled switch/filter/path loss, EIRP and HIL |
| `CC-SUB/433` | TE `ANT-433-CW-QW-SMA`, 433 MHz, 3.3 dBi | Ebyte `TX433-JK-11`, 423–443 MHz, 2.5 dBi | stocked primary и current manufacturer alternate | полная intended channel mask, gain/EIRP and second stocked source |
| `CC-SUB/868+915` | Taoglas `TI.08.C.0112`, 860–928 MHz, standard SMA, right-angle | band-specific Ebyte `TX868-JK-11` + `TX915-JK-11B` | один реально stocked MPN покрывает обе common-band profiles; это удаляет одну antenna SKU без удаления диапазона | target ground-plane VNA/efficiency/HIL; stocked qualified alternate for the combined profile |
| `VOICE-V` | Hytera `AN0155H13`, 136–174 MHz, SMA male | Hytera `AN0155H10`, 136–174 MHz, SMA male | две current commercial full-band позиции | SA518 assembled receive/TX/EIRP and mechanical qualification |
| `VOICE-U` | Hytera `AN0435H25`, 400–470 MHz, SMA male | Hytera `AN0435W12`, 400–470 MHz, SMA male | две current commercial full-band позиции | SA518 assembled receive/TX/EIRP and mechanical qualification |
| `RX-FM/SW` | Comet `SMA-W100RX2`, receive-only telescopic standard SMA, published 25–1300 MHz | exact alternate не закрыт | годится как закупаемый mechanical/HIL specimen; Si4732 reference отдельно подтверждает telescopic whip для FM/SW | operation below 25 MHz, exact length/matching, second-source MPN and sensitivity HIL |
| `RX-AM/LW` | custom short loop/pod согласно Si4732 AMI topology | qualified buffered pod остаётся candidate class | generic 50-ohm whip неприменим; готовая dual AM/LW exact MPN pair не найдена | pod schematic/matching/protection/mechanics, two-source BOM and AM/LW sensitivity HIL |

## Почему это не одна universal antenna на каждый RF IC

### Native Wi-Fi и три nRF

Обе native-Wi-Fi линии могут использовать один общий dual-band MPN, а три
nRF — другой общий 2.4 GHz MPN. Это сокращает запасные части без объединения
пяти независимых RF paths и без превышения рекомендованного S3 antenna gain.

TE `001-0012` с published `2 dBi` помещается в Espressif bounds для обоих
native paths. `MAF94051` также помещается: `2.1 dBi` на 2.4 GHz ниже
`2.33 dBi` S3 и `3.86 dBi` C5, а максимум `3.4 dBi` на 5 GHz ниже `3.65 dBi`
C5. Но manufacturer `Active` не равен текущему stock: обе official TE pages
сейчас говорят `not currently available`, тогда как DigiKey показывает stock
для `001-0012`. Поэтому MAF остаётся electrical alternate, не доказанным
закупочным alternate. Более мощная случайная router antenna не считается
заменой.

### `CC-SUB`

Один compact no-loss radiator на 315, 433, 868 и 915 MHz не найден. Частотное
отношение почти 3:1, а реальные короткие multi-band candidates показывают
компромисс эффективности. Поэтому `CC-SUB` остаётся одним physical SMA port,
но использует сменные profile antennas.

Taoglas `TI.08.C.0112` — полезное исключение внутри близких диапазонов: его
официальная полоса 860–928 MHz закрывает common 868/915 profiles. Он заменяет
две отдельные 868/915 antennas одной SKU только после target ground-plane HIL.
TE `ANT-8/9-IPW1-SMA` не выбран: orderability есть, но published efficiency
около 19% на 868 MHz и VSWR около 3.2 на 915 MHz нарушают no-loss intent.
TE `L001095-01` также не primary: верхняя published boundary 920 MHz не
закрывает полный 902–928 MHz profile.

### `VOICE-V/U`

SA518 имеет один physical ANT pin, но его hardware profiles охватывают два
далёких диапазона. Найдены full-range 136–174 и 400–470 MHz antennas, но не
доказан один compact standard-SMA MPN с эквивалентными характеристиками на
обоих диапазонах. Поэтому VHF и UHF — две сменные antennas одного порта.

### `RX-FM/SW` и `RX-AM/LW`

Skyworks `AN383` для exact Si473x topology разделяет FM/SW telescopic whip и
AM/LW ferrite loop. Он также показывает, что одна механическая whip требует
разных matching paths для FM и SW. Comet MPN годится для первого specimen, но
его marketing boundary начинается с 25 MHz, поэтому работа 2.3–25 MHz не
объявляется до измерения. `RX-AM/LW` остаётся специальным внешним loop/pod,
а не generic coax antenna.

## Runtime и безопасность

SMA не сообщает firmware, какая antenna действительно установлена. До
появления отдельного идентификатора действует следующий честный contract:

1. смена `CC-SUB` или `VOICE` profile немедленно сбрасывает TX arm;
2. пользователь явно выбирает exact antenna profile/MPN и подтверждает
   физическую установку;
3. UI показывает port, band, antenna ID, allowed power/region и qualification
   state; QR/цвет/надпись на antenna и порту помогают, но не считаются
   electrical detection;
4. unknown, mismatched, expired или unqualified profile оставляет TX disabled;
5. maximum power остаётся отдельным явным выбором после проверки profile.

## Закрытые и открытые gates

- **Проведено ревью:** реальный рынок exact antennas, connector mating,
  диапазоны, dated first-source stock и возможность безопасно унифицировать
  S3/C5, три nRF и common 868/915.
- **Не закрыто:** `DEC-0050` two-source production gate для каждой profile
  group, exact harness/mount, target ground plane, VNA, sensitivity, EIRP,
  coexistence, regulatory and environmental HIL.
- **Решение владельца требуется:** принимать ли profiled kit из `IMP-0043` как
  architecture input. До решения shortlist не является target BOM.

## Первичные и procurement sources

Проверено 2026-08-17; stock/price являются датированным evidence, не гарантией
будущей поставки.

- [TE 001-0012 product page](https://www.te.com/en/product-001-0012.html),
  [DigiKey 001-0012 listing](https://www.digikey.com/en/products/detail/te-connectivity/001-0012/4732757)
- [TE MAF94051 product page](https://www.te.com/en/product-MAF94051.html),
  [Mouser MAF94051 listing](https://www.mouser.com/ProductDetail/TE-Connectivity/MAF94051?qs=fnpEE5GccuPEMqYYFSm2vg%3D%3D)
- [Ebyte TX2400-JW-5](https://www.ebyte.com/product/495.html),
  [Ebyte TX2400-JZ-5](https://www.ebyte.com/product/494.html),
  [JLC TX2400-JZ-5 listing](https://jlcpcb.com/partdetail/ZIISOR-TX2400_JZ5/C468320)
- [TE ANT-315-CW-HW-SMA](https://www.te.com/en/product-ANT-315-CW-HW-SMA.html),
  [DigiKey stocked listing](https://www.digikey.com/en/products/detail/te-connectivity-linx/ANT-315-CW-HW-SMA/5592330),
  [DigiKey ANT-315-CW-HWR-SMA](https://www.digikey.com/en/products/detail/te-connectivity-linx/ANT-315-CW-HWR-SMA/1139576)
- [TE ANT-433-CW-QW-SMA](https://www.te.com/en/product-ANT-433-CW-QW-SMA.html),
  [Mouser stocked listing](https://www.mouser.com/en/ProductDetail/TE-Connectivity-Linx-Technologies/ANT-433-CW-QW-SMA?qs=XYAu1o%252BHdOKINRzlq1JrLQ%3D%3D),
  [Ebyte TX433-JK-11](https://www.ebyte.com/product/340.html)
- [Taoglas TI.08.C.0112](https://www.taoglas.com/product/ti-08-c-868-915mhz-terminal-antenna-smamra/),
  [Mouser stocked listing](https://www.mouser.com/en/ProductDetail/Taoglas/TI.08.C.0112?qs=QpZVHcK7GhTaAVV8G5mM4Q%3D%3D),
  [Ebyte TX868-JK-11 current catalogue](https://www.ebyte.com/product/2117.html),
  [Ebyte TX915-JK-11B](https://www.ebyte.com/product/346.html)
- [TE ANT-8/9-IPW1-SMA](https://www.te.com/en/product-L9000132-01.html),
  [TE ANT-8/9 datasheet](https://www.mouser.com/datasheet/2/238/ENG_DS_ant_8_9_ipw1_sma_ds_A-3226270.pdf),
  [TE L001095-01](https://www.te.com/en/product-L001095-01.html)
- [Hytera AN0155H13](https://www.hytera.com/en/product-new/accessories/radio-antennas/an0155h13.html),
  [Hytera AN0155H10](https://www.hytera.com/en/product-new/accessories/radio-antennas/an0155h10.html),
  [Hytera AN0435H25](https://www.hytera.com/eu/products/radio-antennas/an0435h25),
  [Hytera AN0435W12](https://www.hytera.com/th/product-new/accessories/radio-antennas/an0435w12.html),
  [AN0155H13 commercial listing](https://www.radiotrader.ie/products/hytera-an0155h13-vhf-gps-long-antenna),
  [AN0155H10 commercial listing](https://radiokomunikasi.com/product/hytera-an0155h10),
  [AN0435H25 commercial listing](https://airacomsystems.com/hp705-handset-accessories/hytera-an0435h25-uhf-gps-antenna-400-470mhz-co-07-001-0013/),
  [AN0435W12 commercial listing](https://www.funkhandel.com/Hytera-AN0435W12-UHF-GPS-Antenne-400-470-MHz)
- [Comet SMA-W100RX2](https://www.comet-ant.co.jp/product/638/),
  [official manual](https://www.comet-ant.co.jp/wp-content/uploads/2019/10/SMA-W100RX2_ver1.pdf),
  [current commercial listing](https://www.k-po.com/product/comet-sma-w100rx2)
- [Skyworks AN383 — Si47xx antenna, schematic and layout guidance](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/application-notes/AN383.pdf)
