# AUD-0001 — повторный аудит legacy-исключений

- Статус: **В работе**
- Основание: `DEC-0004`
- Этап: 2 — возможности и исключения
- Дата начала: 2026-08-15

## Правило чтения

Это первичный triage, а не финальная матрица требований. `reopen` означает «исследовать как реальную возможность», а не «обещать функцию». Группы с разнородными функциями будут декомпозированы; у их дочерних строк могут оказаться разные статусы. Правовой вывод не переносится между странами автоматически.

## Матрица

| OUT | Legacy-исключение | Текущая техническая оценка | Правовая форма | Статус / действие |
|---|---|---|---|---|
| OUT-01 | WPA PMKID/EAPOL capture; полный 5 ГГц monitor+inject | Абсолютный потолок опровергнут частично: C5 promiscuous mode принимает management/control/data frames, а `esp_wifi_80211_tx()` передаёт management и non-QoS data; encrypted/QoS TX не поддержан | Только собственная/письменно разрешённая сеть; capture и хранение имеют privacy-гейт | `reopen`; декомпозировать: `IMP-0003` и on-target proof для EAPOL/PMKID; «полный» inject пока не обещать |
| OUT-02 | Wideband/full-band jamming | С текущими narrowband-чипами нет; возможно только с иным RF hardware | Полевой jammer не допускается как универсальная функция; отдельно рассмотреть проводной/экранированный interference-resilience test source по юрисдикции | `conditional`; не проектировать открытое вредоносное излучение |
| OUT-03 | Bluetooth Classic, BLE connection-follow sniff, BLE jam | S3 и C5 — LE-only; Nordic официально подтверждает connection-follow sniff на отдельном nRF52-class sniffer | Passive capture только на своих/разрешённых устройствах; BLE jam наследует OUT-02 | `reopen`; декомпозировать: connection sniff → `IMP-0004`, Classic требует третьего radio/controller, jam рассматривается отдельно |
| OUT-04 | nRF24 как 802.11/full-BLE receiver | Ограничение верно для nRF24 PHY, но не для продукта: Wi-Fi уже есть на S3/C5, full BLE sniff возможен отдельным radio | Зависит от конкретной capture/active функции | `reopen`; декомпозировать: nRF24-путь проверить на `exclude-proven`, продуктовую функцию оставить в рассмотрении |
| OUT-05 | HF TX, VHF airband/weather, 30–64 MHz, DRM через Si4732 | Это ceiling Si4732, не продукта; нужен другой receiver/transceiver/SDR и, для digital decode, MCU audio/IQ path | RX обычно проще; TX зависит от диапазона, лицензии и региона | `reopen`; сравнить встроенный RF-path и опциональный модуль вместе с `FND-0003` |
| OUT-06 | NFC emulation/relay, ISO15693, FeliCa, LF 125 kHz, hardnested/darkside | Готовый M5 U216/ST25R3916 даёт A/B/F/V, emulation и custom mode дешевле custom PN7160 integration; relay требует два frontend, LF отдельный, key recovery — compute/license proof | Read-only analysis в Lab; recovery/emulation/clone/relay только Controlled Zone `AUTHORIZED_TARGET` | `reopen` декомпозировано: `DEC-0017` выбирает U216; `REQ-NFC-0001` reviewed, LF/recovery/relay сохраняют отдельные gates |
| OUT-07 | SA868 full-duplex repeater и digital voice | Ceiling одного half-duplex analog SA868; технически требует второго RF-path/duplex isolation либо dedicated digital-voice hardware | Частоты, callsign, repeater и encryption зависят от лицензии/региона | `defer`; сначала определить пользовательскую ценность и RF/BOM цену |
| OUT-08 | Wideband SDR, arbitrary RF TX, onboard Linux analytics | Технически достижимо только при добавлении SDR frontend и существенно более мощного compute | RX и анализ отделить от arbitrary TX; TX гейтовать по диапазону/лицензии | `defer/architecture option`; сравнить встроенное и внешнее расширение |
| OUT-09 | Cellular/GSM | Технически достижимо сертифицированным modem module, которого нет в legacy design | Нужны операторские диапазоны, сертификация, SIM/eSIM и региональная проверка | `defer/architecture option`; определить продуктовый сценарий до BOM-анализа |

## Уже найденные обходы

### C5 inter-MCU link — за пределами списка OUT, но снимает legacy-блокер

Актуальный ESP32-C5 имеет отдельный SDIO-slave controller, а ESP32-S3 — SDMMC host с гибкими GPIO. Официальные драйвер и пример поддерживают FIFO, interrupts и DMA. Это даёт путь S3 SDMMC-host ↔ C5 SDIO-slave, оставляя единственный GP-SPI C5 локальной шине nRF24; см. `IMP-0002`.

### Источники первого прохода

- [ESP32-C5 Wi-Fi vendor features](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-guides/wifi-driver/wifi-vendor-features.html)
- [ESP32-C5 Wi-Fi driver / promiscuous frames](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-guides/wifi.html)
- [ESP32-C5-WROOM-1/1U datasheet](https://documentation.espressif.com/esp32-c5-wroom-1_wroom-1u_datasheet_en.html)
- [ESP32-C5 SDIO slave driver](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-reference/peripherals/sdio_slave.html)
- [ESP32-S3 SDMMC host driver](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/sdmmc_host.html)
- [Espressif SDIO host/slave example](https://github.com/espressif/esp-idf/blob/master/examples/peripherals/sdio/README.md)
- [Nordic nRF Sniffer for Bluetooth LE](https://www.nordicsemi.com/Products/Development-tools/nRF-Sniffer-for-Bluetooth-LE)
- [Nordic connection-follow sniffer modes](https://docs.nordicsemi.com/r/bundle/nrfutil/page/nrfutil-ble-sniffer/guides/sniffer_usage.html)
- [NXP PN7160 product page](https://www.nxp.com/products/PN7160)
- [NXP PN7160/PN7161 datasheet](https://www.nxp.com/docs/en/data-sheet/PN7160_PN7161.pdf)
- [M5Stack Unit NFC U216](https://docs.m5stack.com/en/unit/Unit_NFC)
- [M5Stack M5Unit-NFC MIT library](https://github.com/m5stack/M5Unit-NFC)
- [STMicroelectronics ST25R3916](https://www.st.com/en/nfc/st25r3916.html)
- [FCC jammer enforcement basis](https://docs.fcc.gov/public/attachments/FCC-13-106A1_Rcd.pdf)
- [Ofcom rules on jammers](https://www.ofcom.org.uk/spectrum/radio-equipment/radio-spectrum-and-the-law)
- [ETSI shielded/anechoic test environment](https://www.etsi.org/deliver/etsi_en/300001_300099/300086/02.01.01_30/en_300086v020101v.pdf)

## До завершения

- проверить каждый technical reopening по datasheet/SDK и, где нужно, минимальным прототипом;
- выбрать целевые юрисдикции и построить отдельные legal profiles;
- оценить BOM/площадь/питание вариантов OUT-03, OUT-05–OUT-09;
- не закрывать старый потолок без статуса `exclude-proven` и доказательств.
