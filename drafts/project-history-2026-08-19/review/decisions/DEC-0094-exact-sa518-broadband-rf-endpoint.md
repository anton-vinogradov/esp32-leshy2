# DEC-0094 — exact SA518 broadband RF endpoint

- Статус: **Принято автоматически в пределах no-loss/cost полномочий; paper subblock проведён ревью**
- Дата: 2026-08-18
- Входы: [`FND-0099`](../findings/FND-0099-sa518-rf-feed-and-evidence-were-not-electrically-closed.md), [`VRF-0001`](../architecture/VRF-0001-exact-sa518-broadband-rf-endpoint.md)

## Решение

1. Сохранить `NiceRF SA518` как отдельный полнофункциональный `SG-VOICE` owner
   на RP, с уже принятыми direct PTT, UART, H/L, audio и recovery paths.
2. Соединить физический `ANT` contact 7 одной короткой controlled-50-Ω линией
   с отдельной standard-SMA границей без switch/coupler/external matching.
3. Выбрать `PESD24VY1BSF` как exact шунтирующую external-RF защиту: 24-В
   stand-off не режет 11,22-В peak при 31 dBm и имеет 0,17-пФ typical C.
4. Заменить legacy voice `LTC5507` на отдельный физический
   `AD8314ACPZ-RL7`, уже используемый в BOM других RF evidence paths.
5. Реализовать approximately-40-dB resistive sample exact
   `RC0402FR-075K1L` + `RC0402FR-0752R3L`, следуя series-attenuation topology
   AD8314; ожидаемая mainline loading около 0,04 dB.
6. Использовать exact AON filter/bypass и diode/10-kΩ/1-uF enable hold.
   Evidence подтверждает только уже разрешённый PTT; inbound RF не авторизует.
7. Не добавлять external VHF/UHF filter bank и не расходовать P05, пока
   conducted HIL не покажет failure. При failure subblock переоткрывается.
8. Final SMA MPN выбрать после physical placement; VHF и UHF используют
   отдельные маркированные antenna profiles с fail-closed interlock.

## Последствия

- voice feed получает первый complete physical paper endpoint без добавленного
  RF-switch loss и без драматического BOM expansion;
- old 7-V CC ESD part не переносится на 1-W path;
- один detector SKU удаляется, дорогой low-frequency directional coupler не
  нужен, slow-I/O budget остаётся `23/0/1` с P05 free;
- exact electrical paper endpoint закрыт, но KiCad/BOM freeze не разрешены:
  VNA, emissions, detector, legal/EIRP, antenna and coexistence HIL обязательны.

