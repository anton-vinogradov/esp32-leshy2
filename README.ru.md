# Аппаратная часть Leshy2

> **Целевой документ продукта.** Страница описывает проверенное поведение и
> границы готового продукта, а не выбранную электронную архитектуру или текущую
> реализацию. Состояние проработки — в [current state](docs/status/current-state.ru.md).

- [English version](README.md)
- [Целевой firmware-продукт](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/README.ru.md)
- [Канонический журнал ревью](docs/review/README.md)

## Образ готового продукта

Leshy2 — открытый автономный портативный all-in-one инструмент для наблюдения,
диагностики, связи, навигации, обслуживания и разрешённых экспериментов в
нескольких радиоэкосистемах. Это должен быть собираемый, ремонтопригодный и
измеримый продукт, а не набор maximum-capability demos.

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

- Три независимых полнофункциональных nRF24 сохраняют native PTX/PRX,
  одновременный приём и честные packet/drop/timestamp evidence. Их будущий
  owner и wiring открыты.
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
  low-rate expansion tier. Для raw SDR, внешнего compute и general host
  сохраняется отдельный high-throughput class; base не обещает native 30-pin
  M5-Bus. Число/расположение портов и high-speed connector выбираются позже.
- Локальные display/storage/controls, PTT, hard STOP и explicit re-arm остаются
  автономными; обычная эксплуатация не требует телефона.
- Каждый в итоге выбранный programmable chip получает постоянные независимые
  пути прошивки, восстановления и диагностики для prototype bring-up и owner
  repair. Точные connectors и pins пока открыты.
- Owner-controlled signed updates сохраняют target validation, rollback,
  offline keys/tools и intentional physical recovery. Необратимый lockdown —
  отдельный optional decision, а не default.
- Основной режим включает открытый personal FIDO2/CTAP USB authenticator с U2F
  compatibility. Он работает в exclusive minimal mode, требует нового local
  consent и не включает device-bound credentials в обычный backup. Claims
  FIDO Certified, hardware-backed и tamper-resistant запрещены без отдельного
  proof; owner-controlled open firmware сохраняется.

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

Прежние 125 capability leaves проверены; сейчас G2 точечно переоткрыт для
актуального competitor delta, а target physical/product design ведётся как
research. Whole-device alternatives, optimality, conceptual placement и новое
atomic architecture decision обязаны предшествовать компонентам и KiCad.
Нормативный порядок — [`FLOW-0001`](docs/review/architecture/FLOW-0001-product-to-cad-gates.md).
