# DEC-0093 — exact CC1101 three-band electrical endpoint

- Статус: **Принято; paper subblock проведён ревью**
- Дата: 2026-08-18
- Входы: [`FND-0098`](../findings/FND-0098-cc1101-single-ended-band-switch-was-invalid.md), [`CCRF-0001`](../architecture/CCRF-0001-exact-cc1101-three-band-endpoint.md)

## Решение

1. Сохранить `CC1101RGPR` как отдельный полнофункциональный `SG-CC` owner на
   dedicated `RP2354B PIO0 SM3`, без ожидания nRF, U214 или display buses.
2. Пропустить SCLK/SI/CSN и SO/GDO0/GDO2 через два отдельных switched-rail
   `74LVC126APW,118`; добавить exact 22-Ом source series и host defaults.
3. Использовать exact 26-МГц `ABM8-26.000MHZ-10-D-1-G-T`, 15-пФ loads,
   56-кОм RBIAS и отдельные supply/DCOUPL decoupling bodies.
4. Использовать два `BGS13SN8E6327XTSA1` с одинаковыми V1/V2 и тремя
   двухсторонне изолируемыми ветвями: RF1=315, RF2=433, RF3=868/915 МГц.
5. Выделить slow-I/O P03/P04 под эти два truth bits; P05 остаётся свободным.
   Band code меняется только при снятом `3V3_CC_SWITCHED`; `00` всегда isolation.
6. Принять `B0310J50100AHF` и exact populated U219-derived high-Q passive
   coupon как первую измеряемую сборку, а не как уже квалифицированное matching.
7. Защитить final line exact `SESD0402X1UN-0020-090`; final standard-SMA MPN
   выбрать только после mechanics/placement, не выдумывая footprint заранее.
8. Заменить CC `LTC5507` на уже используемый `AD8314ACPZ-RL7` с 0,47-пФ
   high-impedance sample после полного тракта и AON hold. Inbound RF никогда не
   авторизует передачу; detector может только подтвердить commanded TX или
   консервативно задержать quiet-state.

## Последствия

- невыбранные band filters больше не являются односторонними stubs;
- GPIO MCU не тратятся, main slow-I/O reserve сокращается с P03…P05 до P05;
- отдельный CC detector SKU удаляется, а recurring delta остаётся порядка
  нескольких долларов, без драматического раздувания BOM;
- exact electrical paper endpoint закрыт, но KiCad/BOM freeze не разрешены:
  VNA, output/sensitivity/spurious, evidence, EIRP/legal and coexistence HIL
  остаются обязательными.

