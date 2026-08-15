# FND-0010 — legacy смешивает доказанный Si4732 baseline, внешний SSB-патч и недоказанную синхронную AM

- Статус: **Открыто; требуется решение `IMP-0013`**
- Серьёзность: нельзя переносить `C-RX-03` как единый готовый firmware-контракт
- Затрагивает: `C-RX-01`–`C-RX-07`, `REQ-RX-0001`, supply-chain обновлений, storage/import UI, firmware/HIL
- Обнаружено: 2026-08-16

## Несоответствие

Legacy одновременно обещает `SSB (USB/LSB) + CW + synchronous-AM`, ссылается на MIT-библиотеку `pu2clr/SI4735` и отдельно пишет, что пользователь загружает SSB patch blob во время работы.

Проверка первичных источников разделила это на три разных состояния:

1. Si4732-A10 штатно поддерживает FM, AM/SW/LW, RDS, tune/seek, RSSI/SNR, AGC и связанные receive controls через документированный command API.
2. PU2CLR реализует SSB для Si4732-A10 через внешний volatile patch, который необходимо загружать заново после power-up. Репозиторий библиотеки имеет MIT-лицензию, но содержимое патча в неё не входит; README не устанавливает право проекта на распространение blob и отдельно предупреждает о коммерческом использовании patch content.
3. В актуальной Skyworks AN332 и публичном API PU2CLR не найден документированный synchronous-AM mode. Обычная AM, SSB с BFO и «синхронная AM» не взаимозаменяемы и не должны иметь одну отметку готовности.

Следовательно, MIT-лицензия driver library не доказывает право включить сторонний patch blob в образ прошивки, а наличие SSB patch path не доказывает synchronous-AM.

## Влияние на продукт

- FM/RDS и обычная AM могут остаться обязательным baseline квалифицированного Si4732-A10.
- SSB/CW технически достижимы без изменения BOM, но требуют отдельного контракта provenance, совместимости, импорта, проверки целостности и volatile reload.
- Синхронная AM остаётся недоказанной возможностью до появления воспроизводимого primary-source или on-target proof; переименование обычной AM/SSB в sync-AM не допускается.
- Firmware update и пользовательский patch import должны иметь разные trust/provenance состояния: подписанный образ не делает автоматически доверенным импортированный blob.

## Условия закрытия

1. Владелец выбирает вариант `IMP-0013`.
2. `REQ-RX-0001` разделяет baseline, conditional SSB/CW и deferred synchronous-AM.
3. Целевые страницы обещают только принятое, а current-state сохраняет открытые implementation proofs.
4. Для выбранного patch lifecycle определены отрицательные тесты: отсутствующий, повреждённый, слишком большой и несовместимый blob, а также потеря patch state после reset/power-cycle.

## Первичные источники

- [Skyworks AN332 — Si47xx programming guide](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/application-notes/AN332.pdf)
- [Skyworks Si4732-A10 data short](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-shorts/Si4732-A10-short.pdf)
- [PU2CLR SI4735 library and SSB patch notes](https://github.com/pu2clr/SI4735)
