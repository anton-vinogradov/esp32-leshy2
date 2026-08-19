# FND-0014 — программный PMR446 preset не делает текущую конструкцию licence-exempt PMR446

- Статус: **Закрыто на уровне требований: ложный licence-free preset запрещён в `REQ-VHF-0001`**
- Серьёзность: legal/compliance misrepresentation и риск неразрешённого TX
- Затрагивает: `C-VHF-01`–`C-VHF-04`, regional profiles, antenna, power calibration, UI/onboarding
- Обнаружено: 2026-08-16

## Несоответствие

Legacy предлагает «PMR446 preset» и связывает его с лимитом 0.5 W. Но для гармонизированного CEPT/EU PMR446 equipment profile одновременно требуются:

- hand-portable peer-to-peer use, не base/repeater;
- integral antenna, которую пользователь не заменяет внешней;
- не более 500 mW ERP;
- соответствующий channel plan и применимые transmitter time-out/VOX условия.

Leshy2 использует отдельный SA868/SA518 RF-port и внешнюю SMA-антенну, программируется за пределами PMR446 и не имеет доказанной ERP/certification configuration. Даже low-power SA868S имеет datasheet range 24–26 dBm **на RF-порту**; antenna gain/loss и production spread не превращают это автоматически в ≤500 mW ERP. Поэтому частота 446 MHz и программное значение low-power не доказывают licence-exempt device.

## Закрытие на уровне требований

1. Термин `licence-free PMR446 preset` удаляется из target contract текущей аппаратной конфигурации.
2. CEPT PMR446 channel table может существовать для RX/reference и, если применимо, для отдельно авторизованного/квалифицированного TX profile, но UI не обещает освобождение от лицензии или соответствие оборудования.
3. Любой будущий licence-exempt SKU требует отдельной integral-antenna, ERP, timeout, conformity и country-implementation qualification; обычный firmware profile этого не создаёт.
4. Для других юрисдикций применяется отдельный актуальный legal profile; CEPT-правила не выдаются за универсальные.

Это исправление не запрещает законную licensed/authorized связь в 400–470/480 MHz. Оно запрещает ложную маркировку текущего устройства как безлицензионной PMR446-рации.

## Первичные источники

- [ECC/DEC/(15)05 — harmonised PMR446 conditions](https://docdb.cept.org/download/2783)
- [ETSI EN 303 405 V1.1.1 — PMR446 equipment scope and limits](https://www.etsi.org/deliver/etsi_en/303400_303499/303405/01.01.01_30/en_303405v010101v.pdf)
- [NiceRF SA868S datasheet rev. 1.7](https://www.nicerf.com/upload/20250730/550a4fb20f0ddcdaf5c265201a056c73.pdf)
