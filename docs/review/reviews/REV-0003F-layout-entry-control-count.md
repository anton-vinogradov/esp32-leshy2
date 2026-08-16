# REV-0003F — повторное ревью control count перед layouts
> **Историческая запись ревью.** `DEC-0027` архивировал её stage-3 architecture outputs; этот документ не является активным пререквизитом zero-based synthesis.


- Статус: **Проведено ревью**
- Дата: 2026-08-16
- Вход: legacy control names, `DEC-0024`, `DM-UI-02`, `DM-SAFE-01`, `IMP-0010`
- Выход: `FND-0031`, corrected `DM-0001`

## Проверки

| Проверка | Результат |
|---|---|
| Ordinary controls | D-pad 5 + BACK + OPTIONS + F1 + F2 = 9 |
| Safety control | STOP отдельно, не matrix/expander-only |
| Total physical controls | 10, как в исходном product control set |
| Scope delta | отсутствует; исправлен только двойной счёт |
| Layout effect | matrix candidate требует 3×3/6 lines, а не ложную 10-key matrix |

## Вывод

`DM-0001` повторно получает статус **«Проведено ревью»** с исправленным UI count. `LAY-S3`, `LAY-C5` и `LAY-BAL` используют девять ordinary controls плюс независимый STOP.

