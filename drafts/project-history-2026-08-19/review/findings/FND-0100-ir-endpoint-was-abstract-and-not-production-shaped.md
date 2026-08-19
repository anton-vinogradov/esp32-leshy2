# FND-0100 — IR endpoint was abstract and not production-shaped

- Статус: **Исправлено на бумажном уровне; optical/HIL open**
- Scope: I6 consumer-IR endpoint
- Исправление: [`IRF-0001`](../architecture/IRF-0001-exact-dual-receiver-transmit-and-optical-evidence-endpoint.md), [`DEC-0095`](../decisions/DEC-0095-exact-ir-endpoint.md)

## Несоответствие

The reviewed wish list already required two independent receive paths, but the
machine map still ended at three abstractions: screened through-hole
`TSOP38238`, carrier receiver `TSMP95000`, and `TSAL6200` plus an unnamed
driver. It did not account for switched-domain output back-power, every real
receiver ground contact, TX current at a rail/forward-voltage corner, or the
analog circuit behind the accepted `VEMD1060X01` optical evidence sensor.

The old three names were therefore requirement candidates, not a complete
orderable endpoint. In particular, a LED drive waveform or current sense is
not proof that infrared light left the emitter.

## Correction

- `TSOP95238TT` replaces the old through-hole demodulator with an active,
  reflowable 38-kHz AGC2 Heimdall device; contacts 1/4 GND, 2 VS and 3 OUT are
  all represented.
- Separate `TSMP95000TT` retains 30–60-kHz carrier learning in the same
  top-view Heimdall assembly family; its recommended 100-Ohm/4.7-uF supply
  filter and 4.7-kOhm output pull-up are physical.
- `TPS22919DCKR` plus `74LVC2G126DC,125` discharge the receive rail and isolate
  both returns from live C5 pins while off.
- Side-view SMD `VSMY14940`, `RC1206FR-0733RL` and `DMN2056U-7` replace the
  through-hole emitter/abstract driver without changing function.
- `VEMD1060X01` now feeds an exact AON `TLV9061IDBVR` transimpedance circuit in
  a light-tight internal tunnel. Comparator channel 8 therefore observes
  emitted light, not the gate command or LED current.

No C5 pin or main slow-I/O contact changes. Exact optics, threshold, duty,
temperature, IEC 62471 and coexistence remain mandatory HIL gates.

## Sources

- [Vishay TSOP952/954 datasheet](https://www.vishay.com/docs/82837/tsop952.pdf)
- [Vishay TSMP95000 datasheet](https://www.vishay.com/docs/82907/tsmp95000.pdf)
- [Vishay VSMY14940 datasheet](https://www.vishay.com/docs/84209/vsmy14940.pdf)
- [Vishay VEMD1060X01 datasheet](https://www.vishay.com/docs/84295/vemd1060x01.pdf)
