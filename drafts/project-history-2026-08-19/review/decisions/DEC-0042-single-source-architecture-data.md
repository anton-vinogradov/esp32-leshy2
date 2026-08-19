# DEC-0042 — single source for exact devices, logical pins and later layout

- Статус: **Принято владельцем; первый milestone проведён ревью**
- Дата: 2026-08-17
- Выбранный вариант: `IMP-0035/A`
- Основание: прямой ответ владельца «го» после предложения принять единый
  versioned data model

## Решение

Exact device identity, реально выведенные контакты и candidate logical net maps
ведутся как versioned machine-readable source. Human-readable pin ledger
генерируется из него и не редактируется отдельно. После выбора рабочей
электрической карты тот же источник будет дополнен геометрией/keepouts и станет
входом адаптированного legacy physical generator.

Первый обязательный validation contract:

1. контакт существует на exact MPN/package/module, а не только в SoC family;
2. каждый exposed GPIO programmable device ровно один раз классифицирован как
   used, reserved или free;
3. duplicate allocation и unknown peer запрещены;
4. используемый strap имеет явное reset/boot proof;
5. обязательные programming/recovery contacts реально выведены и перечислены;
6. reference-only device, constrained lifecycle и abstract peripheral остаются
   видимыми gaps и не становятся silently qualified;
7. generated artifact и source data проверяются CI.

## Реализация первого milestone

- source: `hardware/architecture/devices.json`;
- draft maps: `hardware/architecture/candidates/G2F-2R.json` и `G2F-3D.json`;
- validator/generator: `hardware/architecture/generate.py`;
- generated review ledger:
  [`G2F-pin-ledger`](../architecture/generated/G2F-pin-ledger.md);
- regression tests: `hardware/architecture/tests/test_generator.py`;
- CI: `.github/workflows/architecture-data.yml`.

Это решение принимает **способ получения артефактов**, но не принимает ни
`G2F-2R`, ни `G2F-3D`, ни конкретного владельца nRF24. Physical layout и KiCad
остаются заблокированы текущей последовательностью `DEC-0041`.

