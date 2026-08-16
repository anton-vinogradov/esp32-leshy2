# FND-0041 — owner assumptions remained in supposedly neutral inputs

- Статус: **Закрыто понижением прежних inputs; проведено ревью исправления**
- Дата: 2026-08-16
- Решение: [`DEC-0032`](../decisions/DEC-0032-reopen-product-design-before-cad.md)

## Несоответствие

После переоткрытия архитектуры четыре активных места всё ещё могли снова
протащить прежнюю раскладку:

- `INV-0002/W-OWN-11` называл C5 владельцем IR;
- `INV-0002/W-OWN-13` называл S3 владельцем native BLE;
- `CAP-0001/CI-06/07` объявлял S3/C5 domains неподвижными;
- `RES-0001` называл те же domains `RB-FIX-*`, а `CON-0001` зависел от
  загрязнённого `CAP-0001`.

Это противоречило выбранному варианту A: функции сохраняются, но compute/radio
owners должны следовать из target product design и complete whole-device
comparison, а не быть входом такого сравнения.

## Исправление

- `INV-0002` хранит dual-path IR и native BLE как желания без owner.
- `REQ-IR/W5/W24/BLE` уже выражают capability contracts и reference backends.
- Бывшие `CAP/CON/RES` понижены до historical candidate/reference artifacts.
  Их внутренние числа и failure questions можно переиспользовать только после
  независимого повторного вывода; они не являются reviewed prerequisites.
- После закрытия competitor delta и `G3` новые neutral capability/concurrency/
  demand artifacts строятся заново либо явно доказывают каждое заимствование.

Потери capability нет: переоткрыты только owners, named domains и зависимые
implementation assumptions.
