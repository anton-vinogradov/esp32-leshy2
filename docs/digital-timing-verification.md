# Digital bandwidth, latency and timing

`H3.4.2` is reviewed with `40` machine checks and no open analytical finding. The exact current marker is `H3.6.1`.

## Closed paper budgets

| Path | Reviewed result |
|---|---|
| Display + storage | 40-MHz quad display gives 20 MB/s and a full RGB565 frame in `15.360 ms`; each display quantum is 20 kB/1 ms. A qualified 50-MHz SD profile leaves exactly 4.0 MB/s after 1.25 MB/s protocol/card reserve and 1.0 MB/s display allowance. A 512-KiB ring covers `349.525 ms` at 1.5 MB/s. |
| Audio | 48-kHz, stereo, 24-bit samples in 32-bit slots: 3.072-MHz BCLK, 288 kB/s payload per direction and `21.333 ms` across four DMA buffers. |
| Three nRF24 | Each dedicated 10-Mbit/s SPI drains 32 bytes in `26.400 us`; even a serialized three-radio upper bound is `79.200 us` against a >`457.500-us` three-level FIFO guard. |
| CC1101 | 32-byte watermark fills in `426.667 us` at 600 kbit/s and drains in `26.400 us` at 10 Mbit/s. |
| S3↔RP | 1.5-MB/s payload floor exceeds the three-nRF-plus-CC theoretical payload (`0.825 MB/s`) by `0.675 MB/s`. |
| S3↔C5 | 20-MHz one-bit SDIO provides 2.5 MB/s raw; 70% admitted occupancy leaves 1.5 MB/s payload plus 0.25 MB/s framing. This carries admitted waterfall/metadata/events, not every raw Wi-Fi frame or RF sample. |
| SYS_I2C | A deliberately large 32-byte transaction takes `0.812 ms`; an eleven-client sweep takes `8.938 ms`, well below the 100-ms ordinary UI deadline. |

The storage 50-MHz mode is conditional on card identity and CMD6 high-speed admission. A fallback card may work at 25 MHz but may not claim the 4-MB/s profile. Radio FIFOs never share a controller, PIO state machine or persistent DMA channel with display/storage.

Seven physical timing gates remain explicit for H8, including logic-analyzer traces, real media stalls, USB/IPC load and audio underrun/overrun stress.

Machine evidence: [`H3-VRF42-digital-timing.json`](../hardware/verification/generated/H3-VRF42-digital-timing.json).
