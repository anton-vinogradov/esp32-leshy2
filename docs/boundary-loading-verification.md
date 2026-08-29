# M1, expansion and service-boundary loading · current R2 architecture

`H3.4.3` is reviewed with `50` machine checks and no open analytical finding. The historical R1 progression marker is `H3.6.1`.

## M1 worst-case bounds

The exact 80-contact FX8C pair carries 44 distinct nets plus 16 explicit NC reserves. The entire accepted 3.75-A main envelope is distributed across fourteen supply and fourteen dedicated return contacts: `0.268 A` per contact against 0.4 A, `21.429 mV` maximum connector drop and `80.357 mW` total connector loss. AON uses `0.082 A` per contact. Every clocked IPC and USB contact is adjacent to POWER_GROUND; the low-rate ALERT/CS control is at most two positions away, and no audio payload crosses M1. The connector's 8-Gbit/s rating is `16.667x` USB2 High-Speed.

## Expansion bounds

Each active 5-V branch is limited to 1.25 A below the 1.632-A guaranteed eFuse floor (`23.407%` margin). The 60-mOhm path envelope gives `75.000 mV` and `93.750 mW`. One active signal group keeps U214 and native Unit operationally exclusive; even a faulty dual request at both eFuse floors totals `3.264 A`, still below the 4-A converter floor.

The HLE controlled HLE/TSM pair is rated 4.1 A per pin, and the native `1125R-SMT-4P` is rated 2 A. The stock U214's undocumented male-post material/plating is still an H5 received-sample gate; the socket rating is not silently assigned to its mate.

U214 SPI is admitted at 10 MHz: a 4.7-ns buffer plus the 22-Ohm/30-pF envelope leaves `43.848 ns` inside a half-cycle. U214 I2C is admitted only at <=150 pF (`279.609 ns` with 2.2 kOhm). Native Unit profiles stay <=400-kHz I2C or <=1-Mbit/s UART; 1-Wire remains HIL-only.

Service VBUS cannot power the product. Two service ports draw only 10 uA through their bleeders; four powered-off data lines are bounded to 8 uA through exact FSUSB42 switches. Signal integrity and wrong-accessory injection remain seven explicit H5/H8 gates.

Machine evidence: [`H3-VRF43-boundary-loading.json`](../hardware/verification/generated/H3-VRF43-boundary-loading.json).
