# FND-0008 — legacy System/UI смешивает функции с неподтверждённой реализацией

- Статус: **Закрыто на уровне требований; `DEC-0013`, `REQ-SYS-0001`, `REV-0002I`**
- Серьёзность: не позволяет переносить `FW-CAP §11` как готовый контракт
- Затрагивает: `C-SYS-02`–`C-SYS-11`, `C-X-01`, hardware/firmware и recovery
- Обнаружено: 2026-08-16

## Несоответствия

| Legacy-утверждение | Почему нельзя принять буквально | Исправленная граница |
|---|---|---|
| C5 OTA выполняется именно через `SPI3` | Legacy S3↔C5 SPI topology заблокирована `FND-0001` | C5 OTA transport-neutral до этапа 3; C5 сам проверяет и применяет свой image |
| Physical STOP уже является hardware panic path | Текущий `SW_STOP` — только вход I²C-expander, `FND-0007` | Поведение обязательно, электрический proof отложен; software long-BACK не выдаётся за hardware STOP |
| Grove/M5 поддерживает hot-plug | Legacy expansion одновременно предупреждает, что порты не hot-swap | Dynamic attach только для отдельно квалифицированного powered-port profile; базовое правило — power-off |
| Все M5/Grove — один тип expansion | Принятый GPS `PORT.C` питается 5 V, U214 использует отдельный `EXT-RF14`, generic I²C имеет другие уровни/адреса | Отдельные descriptors и электрические профили; blanket compatibility запрещена |
| USB HID, CDC и MSC можно просто включить вместе | S3 USB device stack имеет общий PHY и ограниченный endpoint budget | Каждая функция включается, но их одновременный composite profile требует audit; mode switching допустим |
| OTA/SD update достаточно доставить до flash | Legacy не задаёт authenticity, key ownership, rollback и first-boot validation | Открыто `IMP-0011`; update trust становится отдельным обязательным контрактом после решения |
| RTOS task management — пользовательская функция | Произвольное убийство safety/radio tasks может нарушить инварианты и является implementation detail | В продукт входят health/self-test; task control остаётся dev/service tooling этапа 7 |

## Закрытие

`DEC-0013` принял owner-controlled signed-update baseline, а `REQ-SYS-0001` прошёл `REV-0002I`. Legacy assumptions больше не являются требованиями. Оставшиеся pin, USB descriptor, S3↔C5 transport, recovery и HIL proof явно сохранены как входы последующих этапов, а не как открытая неоднозначность scope.
