# FND-0037 — C5 USB download strap was misidentified

- Статус: **Закрыто исправлением source contract; проведено ревью**
- Дата: 2026-08-16
- Затрагивает: `PIN-0002`, `BOM-0002/C-006`, C5 recovery fixture

## Несоответствие

`PIN-0002` называл `GPIO26` физическим BOOT-входом C5 и утверждал, что
`GPIO26=0` выбирает USB-capable Joint Download Boot. Это неверно для
ESP32-C5:

- normal SPI boot требует `GPIO28=1`;
- USB/UART-capable Joint Download Boot 0 требует `GPIO28=0` и `GPIO27=1`;
- `GPIO26` в обоих этих режимах может иметь любое значение;
- reset выполняется отдельным входом `CHIP_PU`, а не GPIO.

Кнопка или fixture, тянущие только GPIO26, оставили бы GPIO28 высоким и не
гарантировали бы ROM recovery при повреждённой прошивке или пустой flash.

## Applied correction

1. Physical C5 recovery теперь означает отдельные `GPIO28/BOOT` и
   `CHIP_PU/RESET`.
2. `GPIO27` сохраняет pull-up; `GPIO28` имеет normal-boot pull-up и только
   intentional service control тянет его low.
3. `GPIO26` не связывается с `GPIO28` и не называется USB BOOT.
4. В варианте с runtime-функцией на GPIO28 соответствующий accessory domain
   обязан быть off/high-Z во время strap sampling.
5. Empty-flash и corrupted-application recovery остаются обязательными HIL,
   поэтому исправление source ещё не выдаёт `C-006` статус Q.

## Primary evidence

- [ESP32-C5 schematic checklist: boot-mode table](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c5/schematic-checklist.html#strapping-pins)
- [ESP32-C5 download guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c5/download-guidelines.html)

Это factual correction принятого продукта; capability, compute owner и
inter-domain transport не меняются.
