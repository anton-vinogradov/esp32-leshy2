# AUDIO-0001 — ES8311 exact electrical-fit review

- Статус: **Проведено ревью digital/contact fit; analog/power implementation открыта**
- Дата: 2026-08-17
- Scope decision: [`DEC-0009`](../decisions/DEC-0009-onboard-es8311-audio.md)
- Machine source: [`devices.json`](../../../hardware/architecture/devices.json) /
  [`G2F-3I.json`](../../../hardware/architecture/candidates/G2F-3I.json)
- Finding: [`FND-0065`](../findings/FND-0065-es8311-ce-and-differential-path.md)
- Open topology proposal: [`IMP-0046`](../improvements/IMP-0046-es8311-analog-routing-topology.md)
- Review: [`REV-0005B`](../reviews/REV-0005B-es8311-digital-fit-and-analog-gap.md)

## Результат

Exact current paper candidate — **Everest Semiconductor `ES8311`, QFN-20
3×3 mm с exposed pad**. Все реальные контакты внесены в machine source. Его
digital path полностью помещается в уже принятую карту без нового GPIO и без
изменения бюджета S3 `31/3/2`:

| ES8311 contact | Physical | G2F-3I endpoint |
|---|---:|---|
| `CCLK` | 1 | S3 `GPIO2 / SYS_I2C_SCL` |
| `MCLK` | 2 | NC; internal master clock выбирается от `SCLK/BCLK` |
| `SCLK/DMIC_SCL` | 6 | S3 `GPIO15 / I2S_BCLK` |
| `ASDOUT` | 7 | S3 `GPIO18 / I2S_DIN` |
| `LRCK` | 8 | S3 `GPIO16 / I2S_WS` |
| `DSDIN` | 9 | S3 `GPIO17 / I2S_DOUT` |
| `CDATA` | 19 | S3 `GPIO1 / SYS_I2C_SDA` |
| `CE` | 20 | `10 kΩ` high strap, documented 7-bit address `0x19` |

`MCLK` is deliberately not assigned a hidden GPIO. The ES8311 user guide
documents `MCLK_SEL`, which can derive the internal clock from SCLK/BCLK. That
configuration remains a full-duplex prototype/HIL gate on the pinned
ESP-IDF/`esp_codec_dev` version.

## Exact power, ground and reference contacts

| Function | Contacts | Paper contract |
|---|---|---|
| digital supplies | `PVDD=3`, `DVDD=4` | switched quiet digital rail, local decoupling, no I/O back-power |
| digital ground | `DGND=5` | reviewed audio/digital return boundary |
| analog supply | `AVDD=11` | filtered switched analog rail |
| analog ground | `AGND=10` | quiet analog return |
| exposed pad | `EPAD=21` | connect to audio ground as required by user guide |
| references | `DACVREF=14`, `ADCVREF=15`, `VMID=16` | local manufacturer-valid decoupling; never general rails |

The part has **no hardware enable/reset pin**. `CE` is only the I2C-address
strap. Consequently current slow contact `P10` is renamed from misleading
`CODEC_EN` to `CODEC_PWR_EN` and controls an external quiet-rail load switch/
sequencer. Exact load-switch MPN, discharge and I/O isolation are still open;
the pin/contact error itself is corrected.

## Analog boundary found during exact-contact review

The real converter boundary is fully differential:

- ADC input: `MIC1P=18`, `MIC1N=17`;
- DAC output: `OUTP=12`, `OUTN=13`.

The existing receiver mux output and legacy PAM8302 input are single-ended,
and SA518 `MIC_IN` is also represented as a single-ended module endpoint.
Therefore phrases such as «DAC → one selector» are insufficient electrical
specification. A conditioner must either convert the differential DAC signal
to single-ended, or the speaker selector must switch both legs and the TX path
must still receive a qualified single-ended signal. Neither DAC leg may be
silently grounded or discarded before the selected topology documents the
level/SNR consequence.

`G2F-3I` therefore terminates `OUTP/OUTN` and `MIC1P/MIC1N` on explicit
qualified analog blocks rather than inventing a schematic. This does not
change the two slow selector controls `P11/P12`; it opens the topology choice
in `IMP-0046`.

## Firmware contract

- Internal I2C address baseline: `0x19`; startup must verify chip readback and
  scan for collisions on the complete bus.
- Codec power is controlled through `CODEC_PWR_EN`; firmware must never treat
  `CE` as reset or enable.
- Driver starts with I2S clocks stopped, powers/initializes the codec, then
  proves BCLK-derived full-duplex ADC+DAC before any selector leaves analog
  bypass.
- Fault, watchdog or readback failure returns both selectors to hardware
  bypass and stops I2S; it never asserts PTT.
- Exact sample rates/formats and register script are implementation outputs,
  not inferred from the contact fit.

## Exact part-name register for this pass

| Role | Exact identifier | Disposition |
|---|---|---|
| mono codec | Everest Semiconductor `ES8311`, QFN-20 3×3 mm | exact paper candidate instantiated |
| existing RX mux | TI `SN74LVC1G3157DBVR`, SOT-23-6 | legacy/reference path retained |
| existing speaker amp | Diodes Inc. `PAM8302AASCR`, MSOP-8 | legacy/reference endpoint retained |
| candidate one-pole selector | TI `SN74LVC1G3157DBVR` | cheapest/common-part candidate; not yet selected for new positions |
| candidate dual selector | TI `TMUX1136DGSR` (VSSOP-10) / `TMUX1136DQAR` (USON-10) | active two-pole candidate; not yet selected |
| candidate powered-off-protected one-pole selector | TI `TS5A63157DCKR` | TX-path candidate; not yet selected |
| candidate differential receiver | TI `TLV9061IDBVR` | active 10-MHz RRIO candidate; values/noise/power/HIL open |

The selector/op-amp lines are alternatives, not a BOM freeze. Exact analog
parts can be selected only after `IMP-0046` and measured Si4732/SA518/PAM8302
levels.

## Remaining gates

1. Choose the analog topology in `IMP-0046`.
2. Calculate and review supplies, decoupling, address/pull-up network,
   differential input/output conditioning, mute/default states and protection.
3. Confirm production order code, AVL/lifecycle, footprint and assembly lot.
4. Prove `0x19`, BCLK-derived simultaneous ADC+DAC, power sequencing and no
   I2C/I2S back-power on hardware.
5. Measure gain, noise/SNR, clipping, pop/click, latency and RF desense with
   display, SD, Wi-Fi and radios at their maximum valid concurrent load.
6. Verify reset/watchdog/codec-off analog bypass and independent PTT safety.

## Primary sources

- [Everest Semiconductor ES8311 product brief, rev 17.0](https://www.everest-semi.com/pdf/ES8311%20PB.pdf)
- [ES8311 user guide, pinout/address/clock details](https://files.waveshare.com/wiki/common/ES8311.user.Guide.pdf)
- [Espressif `esp_codec_dev`](https://components.espressif.com/components/espressif/esp_codec_dev)
- [TI SN74LVC1G3157](https://www.ti.com/product/SN74LVC1G3157)
- [TI TMUX1136 datasheet/orderable addendum](https://www.ti.com/lit/ds/symlink/tmux1136.pdf)
- [TI TS5A63157](https://www.ti.com/product/TS5A63157)
- [TI TLV9061](https://www.ti.com/product/TLV9061)
