# DEC-0033 — iButton is external through a protected M5-style Port-B profile

- Статус: **Принято; capability contract проведён ревью**
- Дата: 2026-08-16
- Основание: владелец подтвердил, что отдельная база/встроенные контакты не
  нужны, если домофонные ключи покрываются M5 expansion path
- Предложение: [`IMP-0027`](../improvements/IMP-0027-ibutton-one-wire-profile.md)
- Requirement: [`REQ-IBTN-0001`](../requirements/REQ-IBTN-0001-ibutton-one-wire.md)

## Решение

1. Base enclosure Leshy2 не получает обязательную встроенную iButton contact
   pad и отдельный single-purpose connector.
2. Product сохраняет iButton/1-Wire result через protected M5-style Port-B
   electrical profile и replaceable passive contact adapter.
3. На дату решения официальный M5Stack catalog не содержит готового iButton
   Unit. Поэтому речь идёт о нашем M5-compatible adapter, а не о ложной
   совместимости с несуществующим SKU.
4. Adapter не добавляет programmable target. Он содержит контакты, protection,
   pull-up/level elements и passive identity where selected by later design.
5. Dallas/Maxim 1-Wire baseline, Cyfral, Metakom, key-side write and reader-side
   emulation remain separate capability profiles. Generic GPIO does not prove
   support for all of them.

## Product/safety consequence

- generic owned 1-Wire sensor/identity read may live in Main;
- access-control key read/identification is Lab;
- emulation or supported rewritable-key write is Controlled Zone
  `AUTHORIZED_TARGET`, with per-action preview and no unattended replay;
- connect/power never starts read, write or emulation automatically;
- sensitive records use encrypted storage, provenance, explicit export/delete
  and factory-reset erasure;
- removal, STOP, reset, lock or profile mismatch ends emulation and invalidates
  its lease.

## G3/G4 consequence

M5 Unit/Cap surface design must preserve a feasible timing/protection path for
the passive adapter, but exact connector count, pins, pad mechanics and rail
values remain open until product design and complete architecture comparison.
