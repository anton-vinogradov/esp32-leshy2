# DEC-0099 — exact three-domain service and recovery boundary

Статус: **принято; проведено ревью в paper electrical scope**.

## Решение

1. Сохранить три независимых USB data paths: существующий protected product
   USB для S3 и два data-only `USB4105-GF-A` для C5/RP.
2. В каждом data-only порту установить connector-side
   `TPD2EUSB30ADRTR`, board-powered `FSUSB42MUX`, exact CC Rd, VBUS bleeder и
   MCU-side 22-Ω/27-Ω series; service VBUS не соединять с питанием платы.
3. Сохранить три постоянно установленных keyed
   `FTSH-105-01-L-DV-K-P-TR` DBG10 и шесть отдельных
   `SKQGADE010` RESET/BOOT controls.
4. Защитить RESET, BOOT, DBG0 и DBG1 каждого header отдельным
   `TPD4E05U06DQAR`; fixture начинает high-Z и проверяет `VTREF`/passive ID.
5. Закрепить ID `00=S3`, `01=C5`, `10=RP`, `11=invalid`.
6. Заменить конфликтный push-pull reset fan-out на
   `SN74LVC1G06DCKR` и 2×`2N7002DW-7-F` с passive target pull-ups.
7. Сделать C5 GPIO27 exact fixed-high/read-only и вывести реальные контакты
   GPIO28, RP `QSPI_SS_USB_BOOT`, SWD, RUN и USB в machine map.
8. Не разрешать service/recovery обходить STOP, подпитывать устройство или
   восстанавливать прежний TX lease.

## Следствия

- I7 получает **«Проведено ревью»** в paper electrical scope; I8 становится
  следующим dependency step.
- GPIO budgets не меняются; все уже принятые controls и radio paths сохранены.
- Исправлены три старых артефакта: reset contention, D-line backfeed при
  выключенной плате и недоступный prototype switch MPN.
- Первая qty-100 оценка service/recovery material составляет USD 10.5…11.5;
  основной cost-down target I8 — DBG10 family, но только без потери независимого
  доступа, keying, автоматической установки и retention.
- Physical mechanics, USB SI, ESD/backfeed и independent recovery HIL могут
  переоткрыть part/placement, но не могут молча убрать owner service guarantee.

