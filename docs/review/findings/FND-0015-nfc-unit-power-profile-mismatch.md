# FND-0015 — текущие Grove I²C-порты не питают заявленные M5 NFC Unit по их профилю

- Статус: **Открыто; требование исправлено, electrical artifact ждёт этап 3/6**
- Серьёзность: заявленный внешний NFC может не запуститься либо работать нестабильно
- Затрагивает: `C-NFC-*`, `REQ-SYS-08`, `hardware/tscircuit/expansion.tsx`, power/accessory manager
- Обнаружено: 2026-08-16

## Несоответствие

Текущий `hardware/tscircuit/expansion.tsx` подаёт на силовой контакт `J40/J41` сеть `V3V3` и одновременно показывает внешний RFID2 `U44` как совместимый пример. Официальные pin map M5 для RFID2 U031-B и Unit NFC U216 задают на красном контакте PORT.A **5 V**.

Это не безразличная маркировка:

- RFID2 содержит `HT7533`: официальный schematic подаёт на его `VIN` 5 V и получает внутренние 3.3 V;
- U216 содержит отдельный 3.3 V regulator, а M5 приводит измерения питания именно при 5 V;
- питание такого Unit от 3.3 V через входной regulator не является квалифицированным 3.3 V profile и не может обещаться по диапазону, току или RF-полю;
- простой перевод всего общего Grove rail на 5 V тоже недопустим: S3 не 5 V-tolerant, а generic 3.3 V accessories нельзя считать 5 V-safe без descriptor.

## Исправленная граница

1. Ни RFID2, ни U216 не считаются работающими на текущем tsCircuit artifact.
2. NFC profile требует квалифицированный `PORT.A-NFC`: 5 V power, 3.3 V-safe SDA/SCL, ограничение/защита питания, известный current budget и power-off attach до отдельного hot-swap proof.
3. `AUD-0005/FND-0042` generalizes the correction: Unit A/B/C/custom, Cap and
   M5-Bus are separate profiles. Выбор fixed port либо управляемого per-port
   power profile выполняется только после G3 product-surface review and G4–G7
   budgets; он не должен молча ломать generic Grove profile.
4. UI показывает `power/profile mismatch` и не запускает RF polling при неизвестном либо неверном accessory profile.
5. Stage-6/9 acceptance измеряет startup, continuous polling, brownout/removal, bus stuck-low/recovery и RF range на фактическом кабеле/порту.

Немедленное безопасное исправление выполнено: с `expansion.tsx` снята ложная пометка `FAB-READY`, а `U44` явно назван электрически несовместимым legacy placeholder до закрытия находки. Сами traces не меняются вслепую: корректная схема зависит от ещё не принятой общей power/port архитектуры. Несоответствие остаётся видимым implementation gate.

## Первичные источники

- [M5Stack RFID2 U031-B documentation and 5 V pin map](https://docs.m5stack.com/en/unit/rfid2)
- [M5Stack RFID2 schematic](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/841/U031-B-Sch_Unit-RFID_v1.3.pdf)
- [M5Stack Unit NFC U216 documentation, power and pin map](https://docs.m5stack.com/en/unit/Unit_NFC)
- [M5Stack Unit NFC U216 schematic](https://m5stack-doc.oss-cn-shenzhen.aliyuncs.com/1229/SCH_Unit_NFC_V0.1_2025_11_28_12_15_35.pdf)
