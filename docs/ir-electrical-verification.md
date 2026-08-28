# IR electrical verification

[Русский](ir-electrical-verification.ru.md) · [Home](../README.md) · [Schematics](schematics.md) · [Virtual verification](virtual-verification.md)

H3.3.3 checks the complete C5 IR chain: robust demodulated receive, raw carrier learning, bounded transmit and independent physical-light evidence. The paper result does not replace final range and optical-safety measurements through the enclosure.

## Dual receive

`Vishay TSOP75238TT` provides the robust active-low 38-kHz AGC2 envelope while `Vishay TSMP95000TT` independently returns 30-to-60-kHz carrier cycles for learning. Both are powered only in IR RX/LEARN and remain within `2.991340…3.285658 V. C5 discards the first `20` ms after enable and waits `5` ms after disable before declaring `IR_QUIET`. Short formats rejected by AGC2 remain available through the raw path.

## Transmit

`FH RS-06K47R0FT` replaces 33 ohm. It guarantees at least the characterized `20 mA / 15 mW·sr⁻¹` point while the hot instantaneous corner is `50.513 mA`, not the 70-mA absolute maximum. Production permits carrier duty no higher than `1/3`, marks no longer than `20 ms`, and emitter-on time no higher than `0.25` in rolling 100-ms and 1-s windows; IR TX is inhibited at `75 C` local temperature. The independent safety controller kills continuous optical evidence longer than 20 ms.

## Physical-light evidence

VEMD1060X01 views the emitter inside a light-tight tunnel. Full resistor/offset corners retain `60.984` mV minimum dark false-assert margin and `29.224` mV guaranteed-clear margin. HIL must achieve the bounded `2.271`-uA TIA assertion target; this remains measured because the photodiode irradiance table is specified at 5-V reverse bias while this circuit operates near 0.3 V. Evidence confirms physical light and never authorizes TX.

The corrections add only `-0.0088 USD` per unit at quantity 100. **H3.3.3 is reviewed; the exact current marker is `H3.6.1`.**

[Machine H3-VRF33 package](../hardware/verification/generated/H3-VRF33-ir.json).
