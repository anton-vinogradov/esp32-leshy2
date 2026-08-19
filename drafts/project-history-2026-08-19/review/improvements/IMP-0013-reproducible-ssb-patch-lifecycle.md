# IMP-0013 — воспроизводимый и открытый lifecycle SSB-патча Si4732

- Статус: **Принято владельцем как вариант A; см. `DEC-0015`**
- Этап решения: 2 — capability scope; реализация и HIL — этапы 7–10
- Связано: `FND-0010`, `REQ-RX-0001`, `DEC-0013`, `C-RX-03`
- Обнаружено: 2026-08-16

## Контекст

FM/RDS и обычная AM входят в штатный Si4732-A10 command set. SSB/CW в используемой экосистеме PU2CLR требует внешнего volatile patch: он не сохраняется после выключения питания и не является частью MIT-кода библиотеки. Legacy уже предполагал user-supplied blob, но не определял источник, права распространения, совместимость, integrity check, размер, ошибки загрузки или связь с подписанными обновлениями.

Одновременно legacy приписывает тому же пути synchronous-AM, для которой в проверенных Skyworks/PU2CLR API не найдено доказанного режима.

## Вариант A — рекомендуемый: открытый generic loader, blob импортирует владелец

1. FM 64–108 MHz, RDS/RBDS и обычные LW/MW/SW режимы остаются встроенным baseline квалифицированной Si4732-A10.
2. Firmware содержит открытый generic patch loader и schema, но не включает сторонний SSB blob, пока не доказаны его источник и права распространения.
3. Владелец импортирует blob локально с SD/USB. Перед сохранением показываются source/license acknowledgement и manifest:
   - целевая part/revision/component и известная совместимость;
   - patch ID/version, размер и криптографический hash;
   - заявленный источник и license/provenance note;
   - дата импорта и версия loader.
4. Loader проверяет manifest, hash, size bound и совместимость до отправки команд приёмнику. Ошибка оставляет radio в обычном AM/FM state без частично загруженного режима.
5. UI различает `не установлен`, `несовместим`, `ошибка`, `загружен в текущей сессии`; reset/power-loss немедленно сбрасывает `loaded`.
6. SSB UI появляется только после успешной загрузки. CW означает приём через SSB/BFO, а не отдельный недоказанный demodulator.
7. Подписанное обновление приложения по `DEC-0013` не подписывает и не легализует пользовательский blob автоматически. Импортированный объект имеет отдельные provenance/hash records; владелец может удалить или заменить его без закрытия устройства.
8. Synchronous-AM остаётся отдельным `defer` до primary-source/on-target proof и не показывается как псевдоним обычной AM или SSB.

Преимущества: сохраняет SSB/CW без дополнительного BOM, не превращает устройство в закрытое и не заставляет проект распространять недоказанный blob. Цена: пользовательский импорт, дополнительный parser/loader/UI и qualification matrix; zero-click SSB отсутствует, пока redistribution не разрешено.

## Вариант B — только документированный baseline

Оставить FM/RDS и обычную AM, исключить SSB/CW и synchronous-AM. Это минимизирует firmware/legal/supply-chain работу, но теряет заметную часть принятого all-in-one профиля и не является экономией без потерь.

## Вариант C — сменить backend ради встроенного SSB/synchronous-AM

Выбрать другой receiver/SDR с native либо явно redistributable demodulation stack. Это может дать zero-click SSB и потенциально synchronous-AM, но требует нового RF/frontend/audio/power/BOM и повторной квалификации; пока нет требования, оправдывающего замену уже установленного Si4732.

## Сравнение

| Вариант | Дополнительный BOM | Firmware/HIL | Пользовательский результат |
|---|---:|---:|---|
| A — generic loader | нет | средний | FM/AM всегда; SSB/CW после локального импорта; sync-AM честно deferred |
| B — baseline only | нет | низкий | теряются SSB/CW и sync-AM |
| C — другой backend | средний/высокий | высокий | максимум зависит от выбранного компонента и лицензии |

## Рекомендация

Принять вариант A. Он сохраняет максимум технически доступного результата без роста BOM и без закрытия firmware, но не делает универсальных юридических выводов: право получить и использовать конкретный blob зависит от его источника, лицензии и применимой юрисдикции.

## Решение владельца

Вариант A принят 2026-08-16. Канонический контракт — `DEC-0015`: открытый bounded loader входит в target, blob остаётся локально импортируемым объектом владельца, а synchronous-AM — отдельным deferred candidate.

## Обязательные proof после принятия A

- positive test на каждой поддерживаемой Si4732 product/revision и зафиксированной library/loader version;
- absent/corrupt/truncated/oversized/wrong-target blob rejection без зависания I²C и без ложного `loaded`;
- power-cycle, brownout, watchdog и переходы FM/AM/SSB с корректным сбросом state;
- SSB USB/LSB/BFO/filter acceptance на signal-generator fixtures;
- manifest/hash audit и удаление пользовательского blob без влияния на signed base firmware;
- отдельный proof до любого появления synchronous-AM в целевом интерфейсе.

## Первичные источники

- [Skyworks AN332 — штатный command API Si4732-A10](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/application-notes/AN332.pdf)
- [Skyworks Si4732-A10 data short](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-shorts/Si4732-A10-short.pdf)
- [PU2CLR SI4735 library: поддержка Si4732-A10 и условия SSB patch](https://github.com/pu2clr/SI4735)
