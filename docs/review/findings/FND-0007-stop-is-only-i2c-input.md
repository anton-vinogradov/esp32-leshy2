# FND-0007 — текущий STOP является только входом I²C-экспандера

- Статус: **Открыто; safety-решение требуется**
- Серьёзность: критичный safety prerequisite для всех TX-функций
- Затрагивает: `C-X-01`, `DEC-0003`, hardware, firmware и HIL
- Обнаружено: 2026-08-16

## Наблюдение

В текущем `hardware/tscircuit/integration.tsx` кнопка `SW_STOP` подключена только к `U14.IO0_7` и подтянута к `+3V3`. От неё нет прямого аппаратного пути к:

- `S3_EN`/`CHIP_PU`;
- `C5_EN`/`CHIP_PU`;
- `SA868_PTT` или `SA868_PD`;
- rail/power enable дискретных RF-трактов и внешнего `EXT-RF14`;
- общему аппаратному `TX_INHIBIT`.

Поэтому обработка STOP требует исправных S3, I²C, общего `PCA9555_INT`, `U14` и high-priority firmware handler. При зависании S3, I²C либо expander этот путь не может гарантировать прекращение передачи.

## Почему reset одного MCU недостаточен

ESP32-S3 и ESP32-C5 имеют аппаратный `CHIP_PU`: low выключает/сбрасывает соответствующий SoC. Но отдельные RF-компоненты не обязаны сбрасываться вместе с host MCU. В частности, CC1101 возвращается в `IDLE` через собственный power-on reset либо команду `SRES`; один только reset S3 не является reset CC1101. Следовательно, универсальный STOP должен управлять не только firmware/MCU reset, но и аппаратным inhibit/power состоянием каждого TX-path.

## Пересечение с принятыми решениями

`DEC-0003` требует, чтобы STOP и аварийное выключение имели приоритет над UI и прикладными задачами, но прямо оставляет достижимость аппаратного STOP следующим этапам. Текущий артефакт этого ещё не доказывает. `DEC-0005` запрещает экономить удалением физического STOP или recovery-path.

## Требуемый контракт

До принятия любой TX-возможности требуется определить аппаратный STOP, который:

1. не зависит от S3, C5, I²C и прикладной firmware;
2. асинхронно переводит каждый onboard и внешний TX-path в физически нетранслирующее состояние;
3. после отпускания не восстанавливает TX, а запускает систему только в safe-off/`DISARMED`;
4. допускает измеримый worst-case kill time и fault-injection test;
5. сохраняет независимую фактическую TX-индикацию.

Рекомендуемый вариант и его цена для pin-map описаны в `IMP-0010`.

## Первичные источники

- [ESP32-S3 datasheet: `CHIP_PU` low disables the chip](https://documentation.espressif.com/esp32-s3_datasheet_en.pdf)
- [ESP32-C5 datasheet: power-up and reset through `CHIP_PU`](https://documentation.espressif.com/esp32-c5_datasheet_en.html)
- [TI CC1101 datasheet: power-on reset and `SRES` return the chip to `IDLE`](https://www.ti.com/lit/ds/symlink/cc1101.pdf)
