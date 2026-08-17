# Аппаратная часть Leshy2

> **Целевой документ продукта.** Страница описывает проверенное поведение и
> границы готового продукта, а не выбранную электронную архитектуру или текущую
> реализацию. Состояние проработки — в [current state](docs/status/current-state.ru.md).

- [English version](README.md)
- [Целевой firmware-продукт](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/README.ru.md)
- [Канонический журнал ревью](docs/review/README.md)

## Образ готового продукта

Leshy2 — открытый автономный портативный all-in-one инструмент для radio/
wireless наблюдения, диагностики, связи и разрешённых исследований, включая
беспроводные и контактные credential tools. Навигация, обслуживание и compute
поддерживают эти результаты, а не превращают продукт в general-purpose
peripheral computer. Это должен быть собираемый, ремонтопригодный и измеримый
продукт, а не набор maximum-capability demos.

Форм-фактор, вычислительная topology, owners, buses, pin map, components,
разбиение плат и корпус намеренно открыты. Бывший `PKG-0001/SYN-3A` после
[`DEC-0032`](docs/review/decisions/DEC-0032-reopen-product-design-before-cad.md)
сохранён только как один candidate study.

## Три уровня функциональности

1. **Основной режим** — повседневные инструменты, приём, диагностика,
   навигация, обслуживание и законная связь.
2. **Лаборатория** — пассивные, защитные и ограниченные security-инструменты.
3. **Лаборатория → Контролируемая зона** — опасные active/disruptive функции.
   Каждый вход показывает новое неснимаемое предупреждение, а каждое действие
   отдельно требует авторизованной цели, изолированной/проводной среды или обоих.

При первичной установке отдельно принимается акт о ненападении. Ни он, ни banner
не вооружают функцию и не отменяют spectrum/licensing/privacy/third-party gates
([`DEC-0002`](docs/review/decisions/DEC-0002-project-vision.md),
[`DEC-0010`](docs/review/decisions/DEC-0010-three-functional-levels.md)).

## Проверенный целевой набор возможностей

- Три независимых полнофункциональных nRF24 сохраняют native PTX/PRX и обязаны
  поддерживать любой одновременный mix `3R/1T2R/2T1R/3T` без automatic standby
  соседей и скрытых RX gaps. Packet/drop/timestamp и exact mixed-RF profile
  evidence остаются явными. Ведущий paper candidate `G2F-3I` размещает их на
  RP2354B; atomic ownership и wiring ещё не финальны.
- Продукт даёт обычные Wi-Fi 2.4/5 ГГц, IEEE 802.15.4, native Bluetooth LE и
  Wi-Fi 2.4/ESP-NOW profiles. Точные radios и ownership выбирает только будущая
  whole-device architecture.
- Packet Sub-GHz, broadcast receiver, analog voice, калиброванное 2.4 GHz
  sector/RPD comparison, consumer IR learning/TX и digital/analog audio paths
  остаются в scope со своими проверенными safety/evidence limits.
- Бортовые GNSS, LoRa и HF NFC frontends не обязательны. Product design должен
  поддержать внешние M5-style GNSS, общепринятые LoRa bands через cap и
  expansion-module strategies где это реализуемо, а также внешний NFC.
  iButton/1-Wire реализуется заменяемым пассивным M5-style Port-B адаптером,
  без обязательных контактов на корпусе базы.
- M5 Unit A/B/C/custom и полный U214-compatible 14-pin Cap образуют основной
  low-rate expansion tier. Принятые raw SDR и external RF/credential-analysis
  profiles могут вывести отдельный high-throughput class; base не обещает
  generic host или native 30-pin M5-Bus. Число/расположение портов и high-speed
  connector выбираются позже.
- Опциональный qualified external IMU может добавлять к RF records timestamped
  motion, pitch/roll и short-term relative-rotation metadata. Device-pose claim
  требует жёсткий indexed mount и sensor-to-antenna transform. Six-axis data не
  является absolute heading или RF bearing; base IMU не требуется.
- Core field operation, display/storage controls, PTT, hard STOP, explicit
  re-arm, pairing/revoke, service и recovery остаются автономными. В base нет
  постоянной text keyboard; заявленный редкий/длинный text workflow может
  использовать локально сопряжённый owner phone. Телефон передаёт видимый текст,
  но не authority для safety, Controlled Zone, TX, destructive, trust или
  recovery actions.
- Производительность дисплея задаётся задачами продукта, а не video-like full
  frames/s: dirty/tiled updates показывают critical state и первый menu feedback
  за `≤100 ms`, waterfall остаётся preemptible при admitted radio/audio/storage
  load, а любое visual coalescing/drop явно учитывается. Exact panel и optics
  остаются решениями architecture/product design.
- Каждый в итоге выбранный programmable chip получает постоянные независимые
  пути прошивки, восстановления и диагностики для prototype bring-up и owner
  repair. Точные connectors и pins пока открыты.
- Owner-controlled signed updates сохраняют target validation, rollback,
  offline keys/tools и intentional physical recovery. Необратимый lockdown —
  отдельный optional decision, а не default.
- Generic USB host, personal FIDO/U2F authenticator и 6 GHz/Wi-Fi 6E находятся
  вне product mission. Конкретный принятый RF/SDR profile может позже вывести
  exact high-throughput transport, не превращая generic host в capability.
- BadUSB/DuckyScript — одно явное non-core исключение: release-optional
  Controlled-Zone software profile поверх существующего USB device/service
  path. Он не добавляет base hardware, не формирует architecture и не задерживает
  radio/key core, но всё равно требует authorization, parser/security review и HIL.

Названные в требованиях и candidate studies modules/IC являются first targets
или evidence, но не молча зафиксированным BOM.

## Границы безопасности и стоимости

- Каждый transmitter и Lab action стартует разоружённым после power/reset/
  update/watchdog/brownout.
- Первая TX использует консервативный профиль; максимум требует явного выбора
  для текущего сценария.
- Physical STOP доминирует над firmware и communication failures. Его отпускание
  никогда не восстанавливает прежние target, power или lease.
- Actual-TX evidence отделено от команды и UI indication.
- Стоимость уменьшается только при доказанной эквивалентности capabilities,
  performance, safety, reliability, autonomy, serviceability и testability.

## Состояние разработки

125 capability leaves и competitor delta прошли повторное ревью G2. Physical/
product inputs G3 остаются проверенными, но теперь сначала проходит G2F.
Единый machine-readable источник содержит три structurally checked карты;
`DEC-0044/NIF-0001/REV-0004L` выбрали `G2F-3I` ведущей reviewed paper map без
radio-bus contention. Physical RF, exact `SG-N24` full-mix acceptance,
quiet-state power controls неиспользуемых interfaces, peripherals, power и HIL
должны закрыться до адаптации legacy physical mockup.
Whole-device optimality, conceptual placement и новое atomic architecture
decision обязаны предшествовать компонентам и KiCad. Нормативный порядок —
[`FLOW-0001`](docs/review/architecture/FLOW-0001-product-to-cad-gates.md).
