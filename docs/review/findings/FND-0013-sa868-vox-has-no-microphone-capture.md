# FND-0013 — host VOX не имеет microphone-capture path

- Статус: **Открыто; VOX явно `defer` в `REQ-VHF-0001` до stage-3 audio/pin решения**
- Серьёзность: blocker `C-VHF-04/VOX`, не blocker ручного PTT
- Затрагивает: `DEC-0009`, `DEC-0012`, `IMP-0010`, audio selector/control budget и firmware/HIL
- Обнаружено: 2026-08-16

## Несоответствие

Legacy пишет «VOX нужен mic feed». Принятая архитектура `DEC-0009` сохраняет electret mic аппаратным bypass в `MIC_IN` SA868 и использует единственный ADC ES8311 для выбранного RX-источника `Si4732/SA868 AF_OUT`. Она не заводит `MIC_HOT` на ADC.

SA868S rev. 1.7 не имеет документированной VOX-команды или VOX input. Следовательно, firmware не может измерить голос с микрофона и безопасно реализовать host VOX на уже принятом audio-path.

## Реалистичные обходы

1. Добавить ещё один safe-default analog selector/tap `RX_MUX ↔ MIC_HOT` перед ADC ES8311. Это минимальный IC BOM, но требует control line, pop/noise/gain proof и не должно ломать RX capture.
2. Добавить отдельный analog envelope/VOX detector. Это экономит ADC scheduling, но добавляет analog BOM, threshold drift и отдельный false-trigger proof.
3. Использовать специальную VOX-ревизию нового SA518. NiceRF предупреждает, что эта кастомизация не поддерживает собственную data-transmission функцию; совместимость и доступность неизвестны.
4. Исключить VOX, сохранив manual PTT.

Выбор нельзя делать до сводного stage-3 pin/audio budget: `DEC-0012` уже запрещает расходовать якобы свободную линию до учёта всей системы.

## Обязательная safety-семантика будущего VOX

Даже после hardware proof VOX не является глобальной настройкой. Он требует отдельной пользовательской сессии, видимого armed state, threshold/hang-time test, bounded maximum key time, silence/error release, region/profile gate и независимого STOP. Reset/watchdog/codec overrun никогда не удерживает PTT.

## Первичные источники

- [NiceRF SA868S datasheet rev. 1.7](https://www.nicerf.com/upload/20250730/550a4fb20f0ddcdaf5c265201a056c73.pdf)
- [NiceRF SA518 product page: optional VOX pin and data trade-off](https://www.nicerf.com/walkie-talkie-module/sa518-uv-dual-frequency-walkie-talkie-module.html)
