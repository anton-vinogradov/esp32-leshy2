# FND-0058 — antenna sourcing and qualification gate remains open

- Статус: **Несоответствие формулировок исправлено; pre-production blocker открыт**
- Серьёзность: RF performance / TX safety / reproducible BOM blocker
- Обнаружено: 2026-08-17
- Evidence: [`ANT-0002`](../architecture/ANT-0002-current-orderable-antenna-shortlist.md)
- Kit decision: [`DEC-0055`](../decisions/DEC-0055-profiled-external-antenna-kit.md)

## Несоответствие

После `DEC-0050` current-state говорил, что следующий exact antenna shortlist
«закрывает» two-source gate. Это слишком сильное утверждение. Shortlist может
закрыть paper sourcing review, но production gate требует для каждой profile
group одновременно:

- минимум два реально закупаемых exact MPN либо документированную
  interchangeable BOM family;
- exact connector/contact, band, impedance, gain и mechanical envelope;
- qualification на собранном target harness/ground plane/enclosure;
- VNA, receive sensitivity, TX power/EIRP, coexistence и environmental HIL;
- version/lot control и повторяемый incoming test.

`ANT-0002` нашёл сильные пары для native Wi-Fi и VHF/UHF voice, stocked
candidates для части sub-GHz profiles и полезный combined 868/915 MPN. Но:

1. Native-Wi-Fi `001-0012` имеет dated DigiKey stock, но official TE pages для
   него и electrical alternate `MAF94051` одновременно пишут Active и
   `not currently available`; второго независимо stocked production source нет;
2. Ebyte nRF pages расходятся по published gain, а independent stock evidence
   обоих proposed MPN ещё неполно;
3. 433 и combined 868/915 не имеют двух полностью qualified stocked sources;
4. `RX-FM/SW` имеет только один procurement specimen и не доказан ниже 25 MHz;
5. `RX-AM/LW` требует custom loop/pod co-design, а не найденную готовую пару;
6. ни одна группа ещё не прошла assembled-device HIL.

## Исправление процесса

- current-state и stage wording заменяют «shortlist закрывает gate» на
  «shortlist формирует candidates; production gate остаётся открытым»;
- `ANT-0002` получает **«Проведено ревью»** только за факты и shortlist, не за
  product qualification;
- `DEC-0055` закрывает структуру profiled kit, но candidate MPN не попадают в
  frozen BOM до exact-MPN selection и последующих measurements;
- distributor stock сохраняется с датой и не трактуется как lifecycle promise.
- availability не опрашивается повторно на каждом architecture pass; следующая
  проверка выполняется при выборе exact MPN.

## Критерий закрытия

Для каждого runtime antenna profile есть approved primary/alternate, exact
assembly BOM, incoming-test rule и passed target HIL. Unknown/mismatched
antenna profile оставляет TX disabled. Только после этого `DEC-0050`
two-source qualification gate и эта находка могут быть закрыты.
