# M1, expansion and service-boundary loading

`H3.4.3` is reviewed with `49` machine checks and no open analytical finding. The exact current marker is `H3.6.1`.

## M1 worst-case bounds

The exact 80-contact FX8C pair carries 51 nets. Even the deliberately over-conservative assumption that the whole accepted 2.5-A main rail crosses M1 loads each of seven contacts by only `0.357 A` against 0.4 A; maximum connector drop is `28.571 mV` and loss `71.429 mW`. AON uses `0.082 A` per contact. Every IPC and USB contact is adjacent to POWER_GROUND; every low-level audio contact is within two positions of AUDIO_GROUND. The connector's 8-Gbit/s rating is `16.667x` USB2 High-Speed.

## Expansion bounds

Each active 5-V branch is limited to 1.25 A below the 1.632-A guaranteed eFuse floor (`23.407%` margin). The 60-mOhm path envelope gives `75.000 mV` and `93.750 mW`. One active signal group keeps U214 and native Unit operationally exclusive; even a faulty dual request at both eFuse floors totals `3.264 A`, still below the 4-A converter floor.

The HLE controlled HLE/TSM pair is rated 4.1 A per pin, and the native `1125R-SMT-4P` is rated 2 A. The stock U214's undocumented male-post material/plating is still an H5 received-sample gate; the socket rating is not silently assigned to its mate.

U214 SPI is admitted at 10 MHz: a 4.7-ns buffer plus the 22-Ohm/30-pF envelope leaves `43.848 ns` inside a half-cycle. U214 I2C is admitted only at <=150 pF (`279.609 ns` with 2.2 kOhm). Native Unit profiles stay <=400-kHz I2C or <=1-Mbit/s UART; 1-Wire remains HIL-only.

Service VBUS cannot power the product. Two service ports draw only 10 uA through their bleeders; four powered-off data lines are bounded to 8 uA through exact FSUSB42 switches. Signal integrity and wrong-accessory injection remain seven explicit H5/H8 gates.

Machine evidence: [`H3-VRF43-boundary-loading.json`](../hardware/verification/generated/H3-VRF43-boundary-loading.json).
