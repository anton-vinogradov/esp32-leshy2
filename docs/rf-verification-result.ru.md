# Сводный результат RF-проверки

`H3.5` проведён ревью: три leaf-пакета дают `125` проходящих checks, сведение добавляет `22` сквозных checks. Незакрытых аналитических findings нет. Точный текущий маркер — `H3.6.1`.

Закрытый бумажный контракт содержит девять source-to-port трактов, семь TX-capable трактов, пять съёмных microcoax, девять runtime signal groups и тринадцать quiet-state contracts. Обычные RF-mainline имеют правила feed/loss, corridor, plane и return; `RX-AM/LW` сохраняет отдельный high-impedance бюджет внешней ёмкости `19,500 пФ`. Полные 3×nRF24 остаются обязательными во всех четырёх смесях и восьми перестановках ролей.

Это pre-layout результат, а не заявление финальных RF-характеристик. `18` только физических пунктов явно назначены H5 received evidence, H6 field-solved/coupon-correlated routing и H8 VNA/spectrum/OTA/coexistence qualification. Результат не разрешает закупку, KiCad placement/routing или печать.

Машинное evidence: [`H3-VRF54-rf-consolidation.json`](../hardware/verification/generated/H3-VRF54-rf-consolidation.json).
