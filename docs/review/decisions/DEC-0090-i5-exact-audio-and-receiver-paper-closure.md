# DEC-0090 — I5 exact audio and receiver paper closure

- Status: **accepted under delegated no-material-function/cost rule; Проведено ревью paper electrical block**
- Finding: [`FND-0095`](../findings/FND-0095-i5-abstract-audio-hidden-power-domain-failures.md)
- Architecture: [`AUDIO-0003`](../architecture/AUDIO-0003-exact-audio-and-receiver-endpoint.md)
- Propagation review: [`REV-0005AU`](../reviews/REV-0005AU-i5-audio-receiver-propagation.md)

## Decision

1. Replace the abstract I5 endpoint with the exact codec, receiver, voice,
   capture, playback, transmit, microphone, speaker and switched-headphone
   circuits recorded in AUDIO-0003 and the machine source.
2. Use independent discharged power branches and supervisor-controlled
   physical interface isolation for ES8311 and Si4732. Use four separate I2S
   buffers so no diagram box or logical device hides multiple physical ICs.
3. Admit SA518 interfaces only after STOP-permitted 4-V qualification. Keep
   PTT fail-RX, hold UART RX low while asleep, drive H/L low or open only,
   leave standard VOXEN disconnected and expose UPDATE only to a service
   fixture.
4. Assign main slow P00 to receiver/microphone capture selection, P01 to
   reset-off speaker enable and P02 to headphone-absence detection. Leave
   P03…P05 free and retain every existing PTT, STOP, RE-ARM, D-pad, F1, F2 and
   encoder path unchanged.
5. Accept host-side microphone recording/authorized VOX analysis as a useful
   zero-loss capability. It never implies PTT and does not enable the custom
   SA518 VOX variant.
6. Keep the reviewed main-rail envelope: the approximately 0.5-A paper speaker
   branch does not materially change cost or reopen I3.
7. Mark I5 **«Проведено ревью»** at paper electrical level and advance the
   dependency chain to I6. Retain every named specimen, RF, acoustic, EMI and
   concurrent-load HIL gate.

## Consequences

- Receive audio retains a hardware bypass and is not made dependent on codec
  boot or continuous S3 service.
- Recording can capture either the selected receiver or local microphone.
- Speaker, codec playback and codec TX injection are reset-off; TX injection
  additionally needs direct S3 AUDIO_ARM. Audio routing cannot bypass AON PTT
  and STOP authority.
- Powered-down endpoints are physically disconnected instead of relying only
  on firmware pin states.
- No requested user control, radio or interface is removed. Slow-I/O reserve
  becomes three contacts.
- Exact passive values are first-target paper values, not authority to freeze
  PCB footprints before HIL and procurement gates.
- This decision does not authorize KiCad, final atomic architecture or the
  paused integrated mockup.
