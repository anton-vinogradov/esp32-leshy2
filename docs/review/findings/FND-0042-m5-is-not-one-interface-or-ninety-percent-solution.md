# FND-0042 — M5 is neither one interface nor a 90% turnkey solution

- Статус: **Закрыто на уровне product model `DEC-0034`; implementation proof открыт**
- Дата: 2026-08-16
- Обнаружено: [`AUD-0005`](../audits/AUD-0005-m5-expansion-ecosystem-coverage.md)
- Затрагивает: `C-SYS-09`, `REQ-SYS-08`, `W-EXTRA-02/04/05/06A/06B/07/08/09/10A/10B/11/13/14/15/16`, G3 external surfaces

## Несоответствие

Разговорная формулировка «поддержать M5 расширения» может быть ошибочно
прочитана как один универсальный connector и почти полное функциональное
покрытие. Официальная ecosystem использует как минимум три materially different
families: HY2.0-4P Unit, Cardputer 14-pin Cap и 30-pin M5-Bus Module. Они имеют
разные сигналы, power directions, mechanics и compatibility rules.

Отдельно, официальный текущий catalog не содержит готового iButton/1-Wire
contact tool или LF 125 kHz Unit. M5 RFID2 работает на 13.56 MHz, UHF-RFID — на
840–960 MHz. Старый M5 USB Module EOL, имеет compatibility warning и даёт только
USB full/low-speed, поэтому не закрывает high-speed host/SDR/compute.

## Измеренный разрыв

Из 18 релевантных Leshy2 external-hardware classes:

- 5 имеют сильный прямой current M5 product match;
- 3 имеют только частичный/unqualified match, включая U059 без доказанного
  mechanical coupling к основному enclosure (`FND-0044`);
- iButton становится reachable только через наш собственный passive Port-B
  adapter;
- M5-only остаётся на 50% даже при таком custom adapter, а не на 90%.

## Исправление product model

1. `M5-compatible` всегда уточняет family и exact profile.
2. Connector reachability, catalog product и product qualification считаются
   отдельно.
3. iButton получает explicit custom passive profile по `DEC-0033`, без
   фиктивного official Unit.
4. M5-Bus не добавляется в base молча; exact Module требует carrier review.
5. High-rate SDR/compute/host остаются отдельным expansion-class вопросом.
6. Every port/profile starts unpowered and fails closed on identity, power,
   protocol, firmware or safety mismatch.

## Exit criteria

- [x] owner принял вариант B через [`DEC-0034`](../decisions/DEC-0034-m5-first-two-tier-expansion.md);
- G3 compares physical Unit/Cap/high-speed surfaces and module retention;
- G4 candidates budget exact ports, signals, power and concurrent profiles;
- G7/G9 produce exact electrical/protection/STOP/update contracts;
- G11 HIL proves wrong-profile, attach/detach, backfeed, overcurrent, bus fault,
  TX safe-off and accessory recovery behavior.

The finding does not reject M5. It prevents M5 connector reachability from
being reported as already completed product capability.
