# FND-0099 — SA518 RF feed and actual-TX evidence were not electrically closed

- Статус: **Исправлено на бумажном уровне; проведено ревью finding**
- Область: `I6 / SG-VOICE`
- Исправление: [`VRF-0001`](../architecture/VRF-0001-exact-sa518-broadband-rf-endpoint.md), [`DEC-0094`](../decisions/DEC-0094-exact-sa518-broadband-rf-endpoint.md)

## Что было не так

После I5 точный `SA518` уже имел питание, UART, PTT, H/L, RX/TX audio и service
contacts, но `ANT` contact 7 уходил в абстрактный `VOICE-V-U-external-SMA-path`.
Отдельная абстракция `VOICE-qualified-RF-tap` не фиксировала место отбора,
нагрузку основного тракта, защиту или поведение evidence при исчезновении 4 В.

Старый `LTC5507ES6#TRMPBF` был лишь ранним кандидатом. Его наличие в safety
diagram не доказывало физический путь от финальной антенной линии. Кроме того,
перенос 7-В `SESD0402X1UN-0020-090` с маломощного CC1101 был бы ошибкой:
31 dBm в 50 Ω — это около 7,93 В RMS и 11,22 В peak, то есть выше допустимого
stand-off такого TVS.

## Исправление

- `SA518 ANT` идёт одной короткой controlled-50-Ω линией к отдельному
  standard-SMA; MPN разъёма остаётся входом mechanics.
- На внешней границе стоит шунтирующий `PESD24VY1BSF`: 24 В, 0,17 пФ typical,
  bidirectional, production. Его stand-off выше нормального 31-dBm peak и
  first-order 2:1-VSWR antinode около 14,96 В.
- Actual-TX sample использует прямо рекомендованный AD8314 способ series
  attenuation: `RC0402FR-075K1L` 5,1 кΩ и `RC0402FR-0752R3L` 52,3 Ω у RFIN.
  Номинально это около 40 dB, −14…−9 dBm на detector при 26…31 dBm и лишь
  около 0,04 dB mainline loading.
- `det_voice` теперь отдельный `AD8314ACPZ-RL7` с exact filter, bypass и
  diode/10-kΩ/1-uF enable hold. Inbound RF может только задержать quiet;
  evidence никогда не создаёт PTT или TX lease.
- Внешние VHF/UHF filters не добавлены без measured failure. Если conducted
  spurious/harmonic/return-loss/sensitivity HIL не проходит, subblock
  переоткрывается; свободный P05 заранее не расходуется.

## Источники

- [NiceRF SA518 specification v1.1](https://www.nicerf.com/pdf/sa518-1w-uv-dual-frequency-walkie-talkie-module-v1.1.pdf)
- [Analog Devices AD8314 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/ad8314.pdf)
- [Nexperia PESD24VY1BSF product page](https://www.nexperia.com/product/PESD24VY1BSF)
- [Littelfuse SESD family datasheet](https://www.littelfuse.com/assetdocs/littelfuse-tvs-diode-array-sesd-ultra-low-capacitance-discrete-tvs-datasheet?assetguid=645e7b6b-8305-497f-b62b-24df676c444e)
- [Yageo RC0402FR-075K1L product specification](https://www.yageogroup.com/component-documentation/download/specsheet/RC0402FR-075K1L)

