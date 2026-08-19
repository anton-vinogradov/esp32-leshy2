# REV-0004N — unused-interface quiet-state input review

- Статус: **Проведено ревью требования и paper controls; electrical/HIL открыты**
- Дата: 2026-08-17
- Decision: [`DEC-0046`](../decisions/DEC-0046-unused-interface-quiet-by-default.md)
- Artifact: [`QST-0001`](../architecture/QST-0001-unused-interface-quiet-states.md)
- Machine source: [`G2F-3I.json`](../../../hardware/architecture/candidates/G2F-3I.json)

## Проверки

| Проверка | Результат |
|---|---|
| reset/boot/fault/STOP default is TX-off | да; `NONE`, hard TX inhibit and no automatic re-arm remain normative |
| non-member RF protocols can remain in background | нет; scans/advertising/beacons/polling forbidden outside manifest |
| all three nRF accidentally power-cycle when one transmits | нет; they share one active `SG-N24`, so the common rail stays on for every PTX/PRX mix |
| inactive nRF/CC/IR have paper hardware power controls | да; RP GPIO15, RP GPIO23 and C5 GPIO4 are real exposed GPIO in the exact selected package/module chain |
| digital buses are quiet when unused | да as requirement; controller clock/DMA/polling stop and pins park before rail removal |
| power-off can back-feed through I/O | not accepted; exact switch/isolation/series implementation and HIL remain blocking |
| always-on S3/RP/system planes are falsely called off | нет; they remain explicit and receive active-receiver EMI limits |
| paper pin budget still closes | да; generator validates S3 `29U+3R+4F`, C5 `14U+6R+1F`, RP `48U+0R+0F` |
| quiet-state policy can silently lose a required domain | нет; source lists ten required contracts and tests reject missing coverage |
| physical non-interference is proven | нет; exact power parts, layout and conducted/OTA HIL remain open |

## Саморевью изменения

Три новые direct controls — не бесплатные «ещё три GPIO»: RP direct reserve
теперь исчерпан. Это явно внесено в target/current-state и generated ledger;
будущий direct RP endpoint обязан вызвать remap/review. Один common nRF gate
корректен только потому, что `SG-N24` всегда использует все три radio. Он не
заменяет независимые CE/CSN/IRQ и не сокращает full-mix requirement.

Review закрывает полноту requirement/paper-map propagation. Оно не принимает
load-switch MPN, power tree, I/O isolation, discharge timing, residual EMI или
physical measurements of the `DEC-0047/N24H-0001` mixed-nRF RF envelope.
