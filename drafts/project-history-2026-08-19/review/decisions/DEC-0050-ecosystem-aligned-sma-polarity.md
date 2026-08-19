# DEC-0050 — ecosystem-aligned external SMA polarity

- Статус: **Принято**
- Дата: 2026-08-17
- Основание: владелец принял рекомендованный вариант B командой «го»
- Proposal: [`IMP-0042`](../improvements/IMP-0042-external-sma-gender-and-feed-policy.md), вариант B
- Evidence: [`RFH-0002`](../architecture/RFH-0002-antenna-connector-ecosystem-review.md)

## Решение

1. Внешний банк сохраняет девять permanent path identities из `DEC-0049`, но
   использует две осмысленные connector families:
   - `S3-2G4`, `C5-2G4/5`: device-side **RP-SMA jack с centre pin**;
     detachable antenna — **RP-SMA plug с centre socket**;
   - `N24-0`, `N24-1`, `N24-2`, `CC-SUB`, `VOICE-V/U`, `RX-FM/SW`,
     `RX-AM/LW`: device-side **standard SMA jack с centre socket**;
     detachable antenna/pod — **standard SMA plug с centre pin**.
2. Native Wi-Fi отделён по consumer ecosystem, а три nRF остаются в
   manufacturer Ebyte/E01 standard-SMA convention. Все 2.4/5 GHz ports не
   переводятся в RP-SMA только по признаку частоты.
3. Polarity не считается band keying или safety interlock. Обязательны
   permanent path/band label, цветной collar/cap, antenna-profile manifest и
   TX interlock; неподтверждённая antenna/load оставляет TX запрещённым.
4. До freezing production BOM каждая antenna group должна иметь минимум два
   реально закупаемых qualified MPN с проверкой band, VSWR, gain/regulatory
   bounds, mechanics и собранного RF path.
5. Для S3/C5 standard SMA остаётся zero-capability-loss fallback: если
   RP-SMA shortlist не даёт реального преимущества по gain, стоимости и
   доступности, native-Wi-Fi ports возвращаются к uniform standard SMA новым
   зафиксированным результатом qualification gate, а не молчаливой заменой.
6. Panel mounting, exact pigtail length, gasket/IP, anti-rotation, placement и
   cable routing остаются G3 physical co-design outputs.

## Последствия

- `DEC-0049` сохраняет count и identities, но его ранняя формулировка о девяти
  механически одинаковых interfaces уточнена этим решением: внешне используются
  две polarity families;
- machine source и validator фиксируют connector/mate map, qualification gate
  и identification controls для всех трёх G2F candidates;
- firmware сохраняет девять logical path identities, а polarity становится
  assembly/diagnostic metadata, не доказательством correct antenna;
- exact antenna shortlist является следующим RF-mechanical prerequisite.
