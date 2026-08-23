# Прошивка и восстановление Leshy2

[English](service-recovery.md) · [На главную](../README.ru.md) · [Схемы](schematics.ru.md)

Устройство не превращается в «кирпич» из-за повреждённой прошивки одного контроллера. Ни один recovery-путь не даёт обходить аппаратные запреты передачи.

| Цель | Основной путь | Независимый fallback | Где |
|---|---|---|---|
| ESP32-S3 | защищённый основной USB-C, native USB Serial/JTAG | внутренний keyed DBG10 UART0 + RESET/BOOT; две утопленные боковые кнопки | UI + RF |
| ESP32-C5 | собственный data-only USB-C через FSUSB42MUX | внутренний keyed DBG10 UART0 + RESET/BOOT; две утопленные боковые кнопки | UI |
| RP2354B | собственный data-only USB-C через FSUSB42MUX | внутренний keyed DBG10 SWD + RUN/USB_BOOT; две утопленные боковые кнопки | RF |
| MSPM0 допуска аккумуляторов | внутренние current-limited VDD/GND + UART + SWD + NRST | постоянно доступны и SWD, и UART | RF |
| AON safety MSPM0 | внутренние AON-powered UART + SWD + NRST | recovery не отпускает RUN_PERMIT и не очищает аппаратный FAULT_KILL | RF |
| TPS25751D + EEPROM конфигурации | площадки SYS_I2C и прямые SDA/SCL/WP локальной шины | заранее прошитая EEPROM либо current-limited raw-VBUS fixture | RF |
| MAX17320 аккумуляторов | защищённая локальная I2C и наблюдение fault/hold | checksum образа и readback override до установки запитанных ячеек | RF |
| голосовой модуль SA518 | площадка UPDATE, постоянный UART и аппаратный PD | UPDATE запрещён до квалификации timing конкретной ревизии модуля | RF |

## Аппаратные границы

- S3, C5 и RP2354B имеют каждый свой USB и независимый keyed DBG10 fallback
- все шесть RESET/BOOT — отдельные утопленные боковые кнопки, способные только притянуть сигнал к нулю
- оба MSPM0 сохраняют UART, SWD и reset даже без рабочей прошивки S3/C5/RP
- первичное программирование PD/EEPROM больше не зависит от недокументированного контакта fixture
- service-пути не разрешают RF re-arm, не отпускают RUN_PERMIT и не очищают FAULT_KILL

## Результат H2.5.2

✅ **Проведено ревью:** 61 reset/boot/service/recovery цепей проверены по полным KiCad-netlist. Обнаруженный пробел PD/EEPROM исправлен шестью внутренними медными площадками без BOM и без изменения корпуса.

[Машинное evidence](../hardware/ecad/generated/H2-REV52-recovery-paths.json).
