# IMP-0005 — заменить NFC ceiling через PN7160

- Статус: **⚠️ Предложение как замена опционального NFC-модуля**
- Связано: `OUT-06`, `C-NFC-*`
- Зона: main RX/обычная запись и `LAB-I` для security/emulation
- Обнаружено: 2026-08-15

## Legacy-ограничение

Опциональный WS1850S ограничен ISO14443A reader/writer и не поддерживает card emulation, ISO15693 или FeliCa. Legacy ошибочно поднял ceiling выбранного модуля до потолка всего продукта.

## Обход

NXP PN7160 поддерживает reader/writer для ISO/IEC A/B, FeliCa, MIFARE и ISO15693, а также NFC Forum card emulation type 3/4 и I2C/SPI host interface. Рассмотреть собственный опциональный модуль PN7160 вместо M5 RFID2/WS1850S.

## Границы обхода

- 125 kHz LF требует отдельного hardware;
- PN7160 не предназначен для EMVCo compliance;
- card emulation не означает автоматическое клонирование защищённых credentials;
- тяжёлые crypto-атаки требуют отдельной оценки compute/time/licence.

## Цена и риски

Собственная NFC-плата и антенна, RF matching, firmware NCI, больше BOM/потребление и менее готовая Grove-интеграция. Security/emulation функции — только «Лаборатория» и авторизованные credentials.

## Источники

- [NXP PN7160 product page](https://www.nxp.com/products/PN7160)
- [PN7160/PN7161 datasheet](https://www.nxp.com/docs/en/data-sheet/PN7160_PN7161.pdf)
