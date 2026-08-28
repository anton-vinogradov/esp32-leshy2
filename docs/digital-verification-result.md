# Consolidated digital-interface result

`H3.4` is reviewed: all three leaf packages and `171` leaf checks pass, followed by `28` cross-domain consolidation checks. No analytical finding remains open. The exact current marker is `H3.6.1`.

## Closed analytical envelope

| Boundary | Reviewed result |
|---|---|
| Levels and quiet state | 130 controller allocations, 13 interface groups, 13 reset/off contracts and all six no-back-power invariants pass |
| Display and storage | 40-MHz direct QSPI, <=1-ms work quanta, 15.36-ms full-frame payload; qualified SD keeps >=4 MB/s and 512-KiB covers 349.525 ms |
| Audio | 48-kHz stereo full-duplex, 3.072-MHz BCLK and 21.333-ms DMA ring on its own controller |
| Compatibility radios | Three simultaneous full-function nRF24 paths and CC1101 have independent SPI/DMA service; worst serialized nRF drain is 79.2 us inside a 457.5-us guard |
| IPC | Both S3-RP and S3-C5 admit >=1.5 MB/s; S3-RP retains 675 kB/s over the three-nRF-plus-CC theoretical payload |
| M1 and extensions | 80-contact/51-net M1, protected U214/native Unit branches, U214 10-MHz SPI/150-pF I2C and data-only service USB pass |
| C5 revision admission | Official MPN stays `ESP32-C5-WROOM-1U-N8R8`; production requires both incoming MD/lot identity and eFuse revision >=v1.2; v1.0 is engineering-only and v0.1/unknown fail closed |

The one-active-signal-group rule still applies at the product level. It does not serialize the three nRF24 radios: those three remain a deliberately concurrent group with independent engines, full RX/TX/mixed-role operation and bounded FIFO service.

## Physical boundary retained

All `19` residual items remain explicit H5/H8 measurements: far-end levels and eyes, reset/brownout captures, SD specimens, DMA and IPC traces, radio FIFO timing, M1/U214 mating and loading, extension misuse, and multi-host service USB. H3.4 does not relabel them as simulated passes.

One self-review correction is preserved in the evidence: the U214 I2C pF-to-ns conversion was fixed before acceptance; 150 pF now evaluates to 279.609 ns against the 300-ns limit.

Machine evidence: [`H3-VRF44-digital-consolidation.json`](../hardware/verification/generated/H3-VRF44-digital-consolidation.json).
