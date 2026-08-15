# DEC-0015 — открытый generic loader для пользовательского SSB-патча Si4732

- Статус: **Принято владельцем**
- Дата: 2026-08-16
- Источник: `IMP-0013`, вариант A
- Закрывает на уровне требований: `FND-0010`
- Затрагивает: `REQ-RX-0001`, `DEC-0013`, storage/import UI, firmware/HIL

## Контекст

Штатный Si4732-A10 API покрывает FM/RDS и обычную AM, но SSB/CW в выбранной открытой driver ecosystem требует внешний volatile patch. MIT-лицензия библиотеки не распространяется автоматически на patch content и не доказывает право проекта включать конкретный blob в release. Тот же путь не доказывает legacy-обещание synchronous-AM.

## Решение

1. Готовый продукт включает FM/RDS и обычные квалифицированные LW/MW/SW профили как встроенный Si4732 baseline.
2. Firmware включает открытый generic patch loader и публичную manifest schema, но не включает сторонний SSB blob, пока не доказаны его provenance и право распространения.
3. Владелец локально импортирует blob с SD/USB. Manifest фиксирует target part/revision/component, patch ID/version, size, cryptographic hash, заявленный source/license note, время импорта и loader version.
4. Hash доказывает целостность и идентичность импортированного объекта, но сам по себе не доказывает авторство, безопасность или лицензию. UI сохраняет эти состояния раздельно.
5. Blob является данными для bounded Si4732 patch protocol и не исполняется как код ESP32. Loader ограничивает размер, время, target/component, допустимую последовательность и ошибки транспорта; failed import/load возвращает обычный FM/AM state.
6. UI различает `не установлен`, `несовместим`, `ошибка`, `загружен в текущей сессии`. После reset, brownout или power-cycle volatile `loaded` всегда сбрасывается.
7. USB/LSB и CW через BFO показываются только после успешной загрузки совместимого patch. Пользователь может удалить или заменить импорт без переподписания base firmware.
8. Owner-controlled подписи application images по `DEC-0013` не подписывают и не легализуют пользовательский blob автоматически. Developer lifecycle, собственные сборки и ключи владельца остаются открытыми.
9. Synchronous-AM остаётся отдельной отложенной возможностью до primary-source и on-target proof с измеримым carrier-lock contract; ordinary AM, SSB/BFO и host post-processing не переименовываются в sync-AM.

## Что решение не утверждает

- Проект не заявляет универсальное право получать, использовать или распространять любой найденный blob.
- Наличие loader не доказывает совместимость каждой Si4732 revision и каждого patch.
- SSB/CW не становятся доступными без успешного импорта и session load.
- Synchronous-AM не входит в текущий target contract.
- Driver, patch storage layout и окончательная firmware architecture не считаются реализованными до последующих стадий.

## Обязательные доказательства реализации

- positive USB/LSB/BFO/filter fixtures для каждой поддерживаемой part/revision/patch/library/loader combination;
- rejection absent/corrupt/truncated/oversized/wrong-target blob без ложного `loaded`, зависшего I²C или потери FM/AM baseline;
- reset/brownout/watchdog/power-cycle и repeated mode transitions;
- manifest/hash/provenance display, deterministic removal и отсутствие auto-upload;
- доказательство, что parser bounds и patch transport не дают blob исполняться на host MCU;
- отдельное решение до включения bundled patch либо synchronous-AM.

## Стоимость

Решение не добавляет BOM и сохраняет SSB/CW в all-in-one профиле ценой firmware/UI/HIL NRE. Отказ от loader был бы потерей функции, а смена receiver — отдельным более дорогим архитектурным вариантом.

## Первичные источники

- [Skyworks AN332 — Si47xx programming guide](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/application-notes/AN332.pdf)
- [Skyworks Si4732-A10 data short](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-shorts/Si4732-A10-short.pdf)
- [PU2CLR SI4735 library and SSB patch notes](https://github.com/pu2clr/SI4735)
