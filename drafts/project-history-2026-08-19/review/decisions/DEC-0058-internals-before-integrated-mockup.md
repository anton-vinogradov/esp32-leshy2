# DEC-0058 — finish the internal design before resuming the integrated mockup

- Статус: **Принято владельцем; проведено ревью propagation**
- Дата: 2026-08-17
- Основание: прямое указание владельца продолжать mockup только после полного
  завершения работ над начинкой
- Closure sequence: [`INT-0001`](../architecture/INT-0001-internal-design-closure-sequence.md)
- Review: [`REV-0005J`](../reviews/REV-0005J-internals-before-integrated-mockup.md)

## Решение

После уже выполненного `PHY-0001` габаритного proof для U214 цельный physical
mockup, размещение органов управления и industrial/enclosure design ставятся на
паузу. Следующая активная работа закрывает начинку в dependency order.

Для возобновления mockup все внутренние блоки `INT-0001` должны иметь
проведённое paper/electrical review:

1. owners, transports, controllers, exposed contacts, straps and pin budgets;
2. compute clocks, reset, update, recovery, diagnostics and inter-domain links;
3. non-programmable STOP, actual-TX evidence and supervisor boundaries;
4. battery, charging, power path, rails, switches, monitoring and thermal budget;
5. display/storage/control electrical endpoints;
6. audio/receiver analog paths, exact passives and safe reset states;
7. RF/IR/voice assemblies, quiet-state isolation and antenna-feed circuits;
8. M5/USB/service electrical protection and profile detection;
9. exact first-target components, sourcing/cost/alternate evidence and one
   coherent internal architecture projection.

`FND-0060` cannot remain a generic bucket: every target-critical `abstract:*`
endpoint must be replaced by an exact part contact or a documented circuit
block with voltage, reset, safe-state and test contracts.

## Не создаём невозможный цикл

«Начинка завершена» здесь означает завершённый проектный/electrical baseline,
а не уже пройденные испытания собранной платы. HIL, RF tuning, thermal soak,
drop/strain and enclosure-dependent tests, которые физически требуют prototype
или корпуса, остаются явными downstream gates и не выдаются за закрытые.

До возобновления цельного mockup разрешены только локальные feasibility checks,
нужные для честного выбора начинки: реальные выводы, footprint/body envelope,
connector mating, antenna/RF keep-out, thermal area and test access. Они не
замораживают расположение плат, кнопок, экрана или форму корпуса.

## Cross-repository boundary

Решение меняет порядок hardware-проработки, но не target behavior, firmware
protocol or runtime ownership. Firmware repository не требует изменения до
появления нового electrical/transport decision.
