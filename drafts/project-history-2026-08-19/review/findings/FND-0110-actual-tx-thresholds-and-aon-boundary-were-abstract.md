# FND-0110 — actual-TX thresholds and the AON-to-main evidence boundary were abstract

- Статус: **исправлено; проведено ревью в paper electrical scope**
- Scope: I8 prerequisite repair discovered during consolidated BOM qualification

> Subsequent `FND-0112/BOM-0011` removes one unrelated assembly-internal
> display-controller purchasing duplicate; its 857/187 current denominator
> does not change any threshold circuit or quantity.
- Corrected artifact: [`SAFE-0003`](../architecture/SAFE-0003-exact-actual-tx-threshold-and-isolation.md)
- Decision: [`DEC-0101`](../decisions/DEC-0101-exact-actual-tx-threshold-and-domain-isolation.md)

## Несоответствие

The accepted I2 evidence architecture already contained two exact
`TLV1824PWR`, eight active-low evidence outputs, `TCA9534APWR`, four dual
Schottky aggregate devices and a physical ANY-TX LED. The machine map still
used eight `abstract:qualified-evidence-threshold-*` endpoints, however. It
also described eight 10-kOhm output pull-ups and a 2.2-kOhm LED resistor only
in prose; neither comparator power/bypass nor evidence-mask power/address/bus
support was fully instantiated.

The same audit exposed a separate power-domain error. C5 GPIO23/GPIO24 and RP
GPIO22 were shown directly on AON evidence nodes. `AON_SAFE_3V3` may remain
present while `3V3_MAIN` and those MCU domains are absent, so the old drawing
did not prove absence of positive injection/back-power. The ANY-TX diode node
also relied on the LED branch instead of an independent logic pull-up.

## Исправление

- Every RF channel now has separate exact 100-kOhm/10-kOhm/1-MOhm/10-kOhm
  threshold, hysteresis and output-pull-up placements.
- IR uses a separate exact 12-kOhm lower leg because its TIA idles near 0.30 V.
- Each `TLV1824PWR`, the `TCA9534APWR` mask and the new domain isolator receive
  their own exact 100-nF bypass placement.
- `TCA9534APWR` power, ground, direct-low A2/A1/A0 straps, local RP I2C0 routes
  and test-only INT are explicit.
- One exact AON-powered `SN74LVC3G07DCUR` transfers C5 RF, IR and ANY-TX into
  separately pulled-up main-domain inputs without changing active-low polarity.
- ANY-TX gains independent 10-kOhm AON logic pull-up and exact 2.2-kOhm LED
  current resistor.

The repair adds no GPIO, capability or firmware polarity change. It adds 42
necessary placements and one used MPN line, taking the current machine BOM to
858 placements / 188 used lines and reducing the explicit physical-gap
families from five to four.

## Обязательная граница

The resistor values are first population, not production calibration proof.
Detector lots, coupler/feed loss, permitted output powers, temperature,
optical-tunnel coupling, ambient IR, threshold tolerance, assertion/decay and
false-positive/false-negative behavior remain HIL gates. A failed measured
channel remains unavailable for proof-mandatory TX; the paper calculation is
not substituted for that gate.
