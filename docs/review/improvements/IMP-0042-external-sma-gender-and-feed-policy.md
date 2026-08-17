# IMP-0042 — external SMA gender/polarity and feed-class policy

- Статус: **Ожидает решения владельца**
- Дата: 2026-08-17
- Decisions: [`DEC-0048`](../decisions/DEC-0048-external-sma-antenna-bank.md),
  [`DEC-0049`](../decisions/DEC-0049-nine-dedicated-external-sma-paths.md)
- Evidence: [`RFH-0001`](../architecture/RFH-0001-module-to-external-sma-interface-review.md),
  [`RFH-0002`](../architecture/RFH-0002-antenna-connector-ecosystem-review.md)
- Finding: [`FND-0057`](../findings/FND-0057-ebyte-ipx-mating-family-unproven.md)

## Контекст решения

Внешний класс `SMA` и число 9 уже приняты, но `SMA` не определяет polarity и
gender. Без этого нельзя задать antenna/accessory manifests, общий внешний
mechanical envelope и qualification references. Mounting/length пока выбирать
рано: они зависят от G3 physical layout.

`RFH-0002` отдельно проверяет предложение выбирать наиболее распространённый
вариант под каждую radio ecosystem. Результат не совпадает с простым делением
по частоте: native Wi-Fi и nRF работают на 2.4 GHz, но принадлежат разным
рынкам готовых antennas.

## Вариант A — standard SMA jack на устройстве для всех 9

Снаружи каждый path имеет standard 50-ohm SMA **jack/female centre contact**;
съёмные antennas/pods — standard SMA plug/male centre contact. Одинаковая
механика снижает число connector families, стоимость, запасные части и
количество переходников.

Ошибка antenna не предотвращается геометрией: девять диапазонов всё равно
невозможно закодировать только SMA/RP-SMA. Поэтому остаются permanent path/band
label, цветные collars/caps, antenna-profile manifest и TX interlock.
`RX-AM/LW` использует ту же механику только как defined product interface, но не
объявляется generic 50-ohm long-coax port.

Внутри это не один feed SKU:

- S3/C5 — доказанный MHF I/U.FL/AMC-compatible plug class;
- nRF — тот же class только после `FND-0057` specimen gate;
- PCB RF paths — direct/short-coax launch выбирается в co-design;
- exact lengths, lock/IP rating и mount остаются G3 output.

## Вариант B — ecosystem-aligned `2 RP-SMA + 7 standard SMA` (рекомендуется)

Только `S3-2G4` и `C5-2G4/5` получают device-side RP-SMA jack и detachable
RP-SMA plug antennas: это соответствует знакомой consumer-Wi-Fi ecosystem.
Остальные семь ports получают standard SMA jack/plug:

- три nRF остаются в standard-SMA Ebyte/E01 convention;
- `CC-SUB` и `VOICE-V/U` используют industrial/reference convention до exact
  antenna shortlist;
- `RX-FM/SW` и специальный `RX-AM/LW` pod остаются standard SMA product
  accessories.

Цена по сравнению с A — второй panel/harness/antenna SKU, дополнительный
assembly check и риск перепутать внешне похожие connectors. RP-SMA не является
keying: резьба позволяет начать соединение, а centre contacts могут дать
socket-to-socket open или pin-to-pin collision. Поэтому marking/profile/TX
interlock остаются такими же обязательными, как в A.

Плюс — готовые замены для native Wi-Fi ищутся в привычном RP-SMA сегменте, а
nRF/sub-GHz/measurement accessories не заставляются переходить на Wi-Fi
polarity. Это ограничивает смешение ровно двумя осмысленными families.

## Вариант C — RP-SMA для всех пяти 2.4/5 GHz ports

S3, C5 и три nRF получают RP-SMA. Вариант проще объяснить как frequency group,
но он ошибочно приравнивает nRF к Wi-Fi ecosystem, расходится с официальной
Ebyte SMA-K/SMA-J convention и всё равно не различает пять ports. Не
рекомендуется.

## Вариант D — external SMA plug на устройстве

Технически возможен, но выступающий male centre contact у девяти device ports
хуже защищён при транспортировке и менее согласуется с готовыми
bulkhead-jack harness references. Не рекомендуется.

## Рекомендация

Принять **B: два native-Wi-Fi RP-SMA jack и семь standard SMA jack**, не
выбирая сейчас panel mounting и cable length. Это не разрешение покупать любую
router antenna: до freezing BOM каждая группа должна получить минимум два
orderable qualified antenna MPN с проверкой band/VSWR/gain/mechanics. Если для
S3/C5 такой RP-SMA shortlist не проходит gain/cost/availability gate, uniform
standard SMA вариант A остаётся fallback без изменения capability.

Одновременно остаются обязательными `FND-0057` sample gate и запрет считать
все девять paths одним электрическим feed/BOM item.

## Вопрос владельцу

Принимаем вариант **B: RP-SMA jack только для `S3-2G4` и `C5-2G4/5`, standard
SMA jack для остальных семи ports, с обязательным two-source antenna
qualification gate и fallback к uniform standard SMA, если RP-SMA не даёт
реального преимущества по gain/cost/availability**?
