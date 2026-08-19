# DEC-0036 — no product haptic or motor profile

- Статус: **Принято владельцем; проведено ревью распространения**
- Дата: 2026-08-16
- Ответ владельца: **вариант C**
- Предложение: [`IMP-0030`](../improvements/IMP-0030-haptic-feedback-placement.md)
- Evidence: [`AUD-0007`](../audits/AUD-0007-haptic-product-mechanical-cost.md)

## Решение

1. Haptic feedback, vibration motor, специальный U059 profile и enclosure mount
   не входят в target Leshy2.
2. Причина — функция не добавляет целевой результат приёма, передачи, анализа,
   прошивки, эмуляции, диагностики или восстановления; display/audio/LED уже
   обеспечивают обычную обратную связь.
3. Универсальный M5 Port-B electrical profile остаётся способен передать GPIO/
   PWM совместимому owner-built accessory, но product не обещает, не
   квалифицирует и не тестирует haptic result.
4. Haptic не резервирует base BOM, power, GPIO, mechanics, UI patterns или HIL.
5. Исправление `FND-0044` остаётся в evidence: U059 не считается on-device
   haptic без mechanical coupling, даже вне target scope.

## Reopen condition

Только новый конкретный целевой сценарий, который нельзя разумно закрыть
display/audio/LED и который оправдывает BOM либо external-profile NRE. Простое
наличие motor Unit в каталоге не является основанием.

