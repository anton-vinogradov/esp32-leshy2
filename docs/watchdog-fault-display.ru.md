# Watchdog и понятная причина отключения

[English](watchdog-fault-display.md) · [На главную](../README.ru.md) · [Итог H3.2](power-transition-result.ru.md)

Независимый TPS3435 имеет exact window `1,44–1,76 с`; firmware обслуживает его с номинальным периодом `500 мс`. WDO напрямую входит в аппаратную fault-plane, поэтому зависание S3 или самого safety-controller не может программно отменить отключение. Возврат WDO high не запускает устройство: защёлке всё равно нужен KILL→RUN.

Safety-controller сохраняет причину в двухслотовом CRC-журнале собственной flash. Экран fault-only показывает причину, зону, значение/порог, уже выполненное действие, event ID и инструкцию перевести RUN в KILL. Он не имеет права включать C5, RP, TX/IR, voice PTT, external 5 V или очищать latch.

При UI overtemperature экран сознательно не сохраняется: важнее выключить опасную зону; остаются amber FAULT LED и последующий service readout. При полном исчезновении AON последняя запись может физически не завершиться, поэтому следующий запуск честно показывает «питание исчезло до сохранения диагностики».

**Статус:** `H3.2.4` проверено; 6/6 fault-сценариев проходят. [Machine evidence](../hardware/verification/generated/H3-VRF24-watchdog-fault-display.json).
