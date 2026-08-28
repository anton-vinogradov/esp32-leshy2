# USB ↔ аккумуляторы и brownout · historical R1

[English](power-handover.md) · [На главную](../README.ru.md) · [Итог H3.2](power-transition-result.ru.md)

Проверены семь переходов: подключение и отключение USB, DPM, USB без pack, KILL при USB, AON brownout и внешнее обратное питание. BQ25798 сначала уменьшает заряд, затем допускает supplement от pack; обычный handover не требует OTG/backup mode.

Переход источника не может включить радиотракт: при потере AON `POR_N` очищает permit, а ни SYS, ни USB, ни BATFET не соединены с clock защёлки. Без исправного pack исчезновение единственного USB является ожидаемым безопасным выключением, а не обещанием hold-up.

Абсолютная величина SYS-droop внутри закрытого control loop BQ25798 не выдумывается из datasheet. Она закреплена как обязательная H8-осциллограмма на worst-case профилях H3.1.

**Статус:** `H3.2.2` проверено; 7/7 переходов проходят. [Machine evidence](../hardware/verification/generated/H3-VRF22-handover-brownout.json).
