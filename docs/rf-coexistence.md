# RF coexistence model

`H3.5.3` is reviewed with `30` machine checks and no open analytical finding. The exact current marker is `H3.6.1`.

| Active group | Active members | Foreign RF/IR quiet contracts |
|---|---|---:|
| SG-N24 | nrf0, nrf1, nrf2 | 9 |
| SG-S3-24 | s3 Wi-Fi, s3 BLE, ESP-NOW | 9 |
| SG-C5-NATIVE | c5 Wi-Fi 2.4/5, c5 IEEE 802.15.4 | 9 |
| SG-CC | cc | 9 |
| SG-VOICE | voice | 8 |
| SG-BROADCAST | receiver, audio support | 9 |
| SG-U214 | stock U214 receive and GNSS, evidence-aware LoRa Cap RX/TX | 9 |
| SG-IR | c5 IR | 9 |
| SG-EXT-* | one exact accessory profile | 9 |

Runtime admits at most one top-level signal group. Display/UI, safety, telemetry and explicitly profile-declared audio/storage/service work are support planes, not a second radio group; their clocks and rails remain bounded or quiet. Cross-group interference injection exists only in the contained Laboratory test layer.

`SG-N24` is the deliberate internal exception. All three radios stay active with independent SPI/PIO/DMA, digital isolation and antenna corridors. The matrix covers four role mixes, eight radio-identity permutations and both idle/worst support loads. Paper review does **not** claim same/near-channel isolation: production acceptance still requires the T1 target plus independent observer and the within-3-dB peer-receive rule, with no hidden standby or RX gap.

Machine evidence: [`H3-VRF53-rf-coexistence.json`](../hardware/verification/generated/H3-VRF53-rf-coexistence.json).
