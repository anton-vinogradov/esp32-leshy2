# DEC-0095 — exact dual-receiver, TX and optical-evidence IR endpoint

- Статус: **Принято автоматически в пределах no-loss/cost полномочий; paper subblock проведён ревью**
- Дата: 2026-08-18
- Входы: [`FND-0100`](../findings/FND-0100-ir-endpoint-was-abstract-and-not-production-shaped.md), [`IRF-0001`](../architecture/IRF-0001-exact-dual-receiver-transmit-and-optical-evidence-endpoint.md)

## Решение

1. Preserve two simultaneous, semantically distinct C5 receive paths.
   `TSOP95238TT` owns robust 38-kHz demodulation; `TSMP95000TT` alone owns
   measured carrier learning in 30–60 kHz.
2. Use the same top-view SMD Heimdall mechanical family for both receivers,
   while retaining two separate physical devices and signal paths.
3. Power only the receive pair from an exact QOD `TPS22919DCKR` branch and
   isolate both returns through `74LVC2G126DC,125`; host inputs remain idle-high
   and cannot back-power an off frontend.
4. Replace preliminary through-hole `TSAL6200` with exact side-view reflowable
   `VSMY14940`, 33-Ohm 1206 current limit and `DMN2056U-7` low-side switch.
   The existing AON safe gate and 10-kOhm gate pull-down remain dominant.
5. Keep receive/learn and TX as mutually exclusive SG-IR phases; no C5 pin or
   slow-I/O contact changes.
6. Complete actual-optical evidence with shielded `VEMD1060X01` and AON
   `TLV9061IDBVR` 47-kOhm/1-nF TIA. LED current or gate state is never accepted
   as emitted-light proof.
7. Missing evidence revokes TX. Extra light may only delay quiet; evidence can
   never authorize TX.
8. Keep exact duty, enclosure-temperature derating, range, threshold and
   IEC 62471 as measured production gates. Paper arithmetic does not replace
   those tests.

## Последствия

- old candidate names become an explicitly superseded requirement history;
- all real receiver contacts, power-off boundaries, TX components and optical
  analog contacts now exist in the generated physical map;
- the direct C5 budget and main slow-I/O budget are unchanged;
- `TSOP95238TT` factory lead time is visible before procurement freeze;
- every separate I6 RF/IR paper endpoint is now reviewed, while consolidated
  coexistence and physical/HIL evidence remain open and KiCad is not authorized.
