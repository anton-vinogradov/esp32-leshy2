# FND-0095 — abstract audio hid power-domain and endpoint failures

- Status: **исправлено; Проведено ревью paper electrical boundary**
- Scope: `I5` codec, receiver, voice and acoustic endpoints
- Architecture: [`AUDIO-0003`](../architecture/AUDIO-0003-exact-audio-and-receiver-endpoint.md)

## Finding

The earlier functional audio drawing selected useful ICs, but it was not an
electrically complete endpoint. It hid several implementation-significant
facts behind logical lines:

1. ES8311 and Si4732 could be powered off while their I2C/I2S/IRQ pins were
   still driven from the live S3 domain, creating unproved back-power paths.
2. SA518 `H/L` permits low or open operation; a normal push-pull GPIO could
   actively drive a forbidden high level. Its PTT, UART and analog ports also
   crossed between independently sequenced rails without physical isolation.
3. Codec supply filtering, reference capacitors, address strap, analog ground
   join, capture common mode and matched differential ADC feed were absent.
4. The source of recording was implicit. Receiver audio could be monitored,
   but there was no complete selection between receiver capture and a local
   microphone, so recording and host-side VOX were not implementable as drawn.
5. `speaker`, `microphone` and `headphone` were functional labels rather than
   exact physical parts with contacts, coupling, protection and reset behavior.
6. Speaker shutdown on reset/headphone insertion and voice receive as the
   reset default were policy statements rather than physical defaults.
7. SA518 `UPDATE` and `VOXEN` could be misread as normal product controls even
   though the former belongs to a service fixture and the standard module's
   latter contact has no useful VOX behavior.

These were paper-integration defects, not a reason to remove any requested
control or radio capability.

## Correction summary

| Gap | Correction | Functional result |
|---|---|---|
| codec partial power | `TPS22919DCKR`, `TPS3839K33DBZR`, dual `SN74LVC2G66DCUR` I2C switch and four separate `SN74LVC1G126DCKR` I2S buffers | codec can be physically quiet/off without loading or receiving power from S3 |
| receiver partial power | independent `TPS22919DCKR`, `TPS3839K33DBZR`, `SN74LVC2G66DCUR` I2C isolation and `SN74LVC1G07DCKR` IRQ isolation | receiver off state is independent of the shared bus |
| SA518 boundary | STOP-qualified `TPS3808G33DBVR`, discharged local I/O rail, separate PTT/UART buffers, dual analog isolation and open-drain H/L driver | PTT remains fail-RX; H/L is never actively high; asleep UART input is low |
| capture | second `TS5A63157DCKR` on slow P00, `TLV9061IDBVR` buffer and matched AC-coupled ES8311 ADC legs | receiver or exact local microphone can be recorded; host VOX never asserts PTT by implication |
| playback | reset-default `TMUX1136DGSR` receiver bypass, P01-controlled `PAM8302AASCR`, exact output EMI network | ordinary receiver audio remains available with codec off; speaker is reset-off |
| endpoints | `CMEJ-0413-42-SMT-TR`, `AS02404PO`, `SJ1-3515-SMT-TR`, exact coupling and `TPD4E05U06DQAR` | real contacts, load, insertion sensing and connector protection are represented |
| address/clock | ES8311 CE=`0x19`; Si4732 first SENB-low population, firmware probe of `0x11` and `0x63`, exact `Q13FC13500005` crystal | no guessed assembled identity is hidden; specimen HIL freezes the final receiver address |
| UI budget | P00 capture source, P01 speaker enable and P02 headphone absence; P03…P05 remain free | full D-pad, PTT, STOP, F1, F2 and encoder are unchanged |

## Remaining evidence, not paper uncertainty

HIL still has to prove actual module identity and address, clock startup, audio
gain/noise/distortion, pop/click, headphone insertion, acoustic loading,
powered-off leakage, SA518 service-pin behavior and radio desense under the
qualified concurrent loads. RF feed and matching remain I6 rather than being
silently accepted by this audio review.

No KiCad authorization, atomic-architecture freeze or integrated-mockup
restart follows from this correction.

## Primary sources

- [Everest Semiconductor ES8311 product brief](http://www.everest-semi.com/pdf/ES8311%20PB.pdf)
- [Skyworks AN383 — Si47xx antenna and crystal interface](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/application-notes/AN383.pdf)
- [TI SN74LVC2G66 product page](https://www.ti.com/product/SN74LVC2G66)
- [Same Sky CMEJ-0413-42-SMT-TR](https://www.sameskydevices.com/product/audio/microphones/electret-condenser-microphones/cmej-0413-42-smt-tr)
- [PUI Audio AS02404PO](https://puiaudio.com/product/speakers-and-receivers/as02404po)
