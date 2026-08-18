# FND-0104 — monolithic receiver/audio quiet contract was contradictory

- Статус: **Исправлено; проведено ревью**
- Scope: `DEC-0046` quiet-state projection into consolidated I6
- Correction: [`QST-0001`](../architecture/QST-0001-unused-interface-quiet-states.md), [`COX-0001`](../architecture/COX-0001-consolidated-i6-qualification-matrix.md)

## Несоответствие

The machine contract `RECEIVER_AUDIO_QUIET` grouped three independently used
domains:

- the Si4732 receiver;
- ES8311/I²S/speaker audio support;
- SA518 UART/PTT/AFOUT/MIC_IN/H-L interfaces.

That state cannot be applied consistently. `SG-BROADCAST` needs Si4732 active,
`SG-VOICE` needs SA518 interfaces active, and either group may explicitly add
audio capture/decode/playback as a support member. A single all-off contract
would demand both active and inactive state from the same named block.

## Исправление

The machine source now has three independent contracts:

| Contract | Independent boundary |
|---|---|
| `RECEIVER_QUIET` | Si4732 rail, reset, I²C and passive audio outputs |
| `CODEC_AUDIO_QUIET` | codec rail, I²C/I²S isolation, selectors and PAM8302A |
| `VOICE_INTERFACE_QUIET` | SA518 PTT/UART/AFOUT/MIC_IN/H-L interface boundary |

The group manifest can therefore activate only its actual members and optional
support planes while every foreign portion reaches a measurable quiet state.
The split changes no route, GPIO, component, rail or product behavior; it makes
the already accepted behavior testable.

