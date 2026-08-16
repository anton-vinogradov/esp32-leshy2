# DEC-0032 — reopen architecture and complete product design before CAD

- Статус: **Принято; проведено ревью исправления процесса**
- Дата: 2026-08-16
- Основание: владелец выбрал вариант `A` после выявления пропущенных product-design/optimality gates
- Finding: [`FND-0039`](../findings/FND-0039-architecture-frozen-before-product-design.md)
- Нормативный workflow: [`FLOW-0001`](../architecture/FLOW-0001-product-to-cad-gates.md)

## Решение

1. Системная архитектура Leshy2 снова **не выбрана**. `SYN-3A`, `PKG-0001` и
   связанные exact pin/power/RF/runtime artifacts сохраняются только как один
   изученный candidate и источник удачных идей, рисков и измеримых gates.
2. Историческое принятие [`DEC-0028`](DEC-0028-accept-zero-based-syn-3a.md)
   superseded: оно не является разрешением продолжать BOM, schematic, firmware
   implementation or PCB.
3. Все прежние physical-owner назначения также переоткрыты, включая C5 для IR/
   dual-band Wi-Fi/802.15.4 и S3 для BLE/2.4 GHz Wi-Fi/ESP-NOW. Проверенные
   capability, concurrency, evidence and safety requirements сохраняются, а
   названные чипы остаются backend reference profiles до нового `G5…G7`.
4. `DEC-0029` остаётся условным фактом: если будущий candidate использует C5,
   production рассматривает только актуально подтверждённую revision не ниже
   найденного floor. Он не означает, что C5 уже выбран.
5. `DEC-0030` superseded as an active-work authorization. Reproducible
   C-001…005 CAD snapshot и его CI архивируются целиком и не считаются
   canonical product library.
6. Из [`DEC-0031`](DEC-0031-permanent-three-domain-development-access.md)
   сохраняется owner requirement: **каждый фактически выбранный programmable
   chip должен иметь постоянно доступные независимые пути прошивки,
   восстановления и диагностики, пригодные для prototype bring-up и owner
   repair**. Три USB-C, DBG10, exact buttons, pins and components возвращаются
   в candidate space до physical design and optimality review.
7. Accepted requirement-level capabilities and safety/legal contracts remain
   reviewed inputs. Architecture work may reveal a conflict, but cannot drop a
   capability silently; it must create a finding and owner decision.
8. The next active stage is target physical/product design, not KiCad.

## Change-control consequence

- Target READMEs describe desired finished-product behavior without claiming a
  selected compute topology.
- Firmware documents are requirements/candidate studies until a new atomic
  architecture decision passes the corrected gates.
- Feasibility research on components is allowed, but every resulting part,
  drawing or CAD asset remains a draft and cannot constrain the design.
- `Проведено ревью` now applies to this correction and retained requirement
  artifacts—not to a finished architecture.

## Preserved archives

- [`premature-compute-cad-2026-08-16`](../../../drafts/premature-compute-cad-2026-08-16/README.md)
- [`premature-service-cad-2026-08-16`](../../../drafts/premature-service-cad-2026-08-16/README.md)
- earlier legacy-derived architecture archive remains reference-only.

## Exit from the reopened state

Architecture may be accepted again only after product design, several complete
candidates, an explicit optimality comparison and conceptual placement all
receive their own review records. Exact pins/components/CAD cannot substitute
for any of those artifacts.
