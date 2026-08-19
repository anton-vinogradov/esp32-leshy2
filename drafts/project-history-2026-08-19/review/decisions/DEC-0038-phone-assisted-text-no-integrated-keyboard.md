# DEC-0038 — phone-assisted text without an integrated product keyboard

- Статус: **Принято владельцем; проведено ревью распространения**
- Дата: 2026-08-17
- Ответ владельца: **вариант C с phone companion для text-dependent scenarios**
- Предложение: [`IMP-0032`](../improvements/IMP-0032-keyboard-whole-product-comparison.md)
- Evidence: [`AUD-0009`](../audits/AUD-0009-physical-keyboard-product-archetype.md)

## Решение

1. Permanent integrated physical text keyboard исключается из target base
   product и больше не является обязательным G3/G4 candidate archetype.
2. Редкий, длинный или произвольный text input может выполняться с явно
   сопряжённого owner phone через qualified companion-input session.
3. Leshy2 остаётся автономным для core field operation, reception/scan,
   navigation, STOP/PTT, disarm/re-arm, pairing/revoke, service/recovery and
   truthful fault display. Text-dependent optional workflow может честно
   требовать phone; отсутствие phone не маскируется как готовность workflow.
4. Phone supplies characters, not authority. Remote input cannot accept the
   non-aggression pledge, enter Controlled Zone, arm/confirm TX or destructive
   actions, change firmware trust, clear secrets or
   authorize recovery. These decisions remain local and fresh.
5. Переданный текст полностью показывается на Leshy2 before use. Any value that
   affects target, identity, frequency, power, credentials or external action
   receives local review/confirmation under its own gate.
6. Pairing is locally initiated/accepted, peer identity and connection are
   visible, and local disconnect/revoke is always available. Input transport
   uses authenticated encryption; secret fields are not logged or echoed.
7. CardKB2/U215 is evidence only and receives no target product profile. A
   wired physical keyboard may return only through a new explicit proposal.
8. Exact display, D-pad/encoder/touch/action controls remain G3 variables, but
   none needs to provide comfortable long-form text authoring.

## Product boundary

This is a narrow exception to the former blanket “no phone for any text” rule,
not a conversion of Leshy2 into a phone-controlled peripheral. If a workflow
can affect safety, authorization or recovery, it remains possible to reject,
stop and recover locally even when the phone or companion link fails.

## Consequences

- `W-EXTRA-15` closes as `rejected-integrated / accepted-phone-assisted`;
- G3 compares display-first field-control surfaces without a mandatory keyboard
  candidate;
- G7/G9 choose and specify the exact companion transport and state machine;
- G11 verifies wrong-peer, replay, disconnect, stale text, hidden-field,
  lock/reset/update and local-authority negative cases.
