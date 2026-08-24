# RF feed constraints

`H3.5.1` is reviewed: `72` machine checks cover all nine external antenna ports and leave no analytical finding open. The exact current marker is `H3.5.2`.

## Per-path contract

| Port | Electrical boundary | Pre-layout acceptance target |
|---|---|---|
| S3-2G4 | 50-ohm module -> 30-mm UMCC -> U.FL -> dual-band coupler -> RP-SMA | complete feed <=1.5 dB, return loss >=10 dB |
| C5-2G4/5 | same, through 5.885 GHz | <=1.5 dB at 2.4 GHz, <=2.0 dB at 5 GHz, return loss >=10 dB |
| N24-0/1/2 | three independent 50-ohm module -> UMCC/U.FL -> 10-dB coupler -> SMA feeds | each <=1.5 dB and >=10-dB return loss through 2525 MHz |
| CC-SUB | CC1101 differential match -> balun -> dual-ended selected branch -> SMA | tuned complete path <=3 dB and >=10-dB return loss at 315/433/868/915 MHz |
| VOICE-V/U | native 50-ohm SA518 ANT -> short protected trace -> SMA | <=0.75 dB and >=10-dB return loss at both 136-174 and 400-470 MHz |
| RX-FM/SW | 50-ohm SMA corridor only up to the first 56-nH body, then receiver-specific match | complete-fixture sensitivity degradation <=1.5 dB; FM and SW qualify separately |
| RX-AM/LW | **not a 50-ohm feed**; SMA is only the serial mechanical boundary for a short loop/pod | external capacitance <=`19.500 pF` including connector, PCB, ESD and pod |

The AM/LW bound uses the pod's 300-uH +5% corner and the 1710-kHz high edge: total resonance capacitance is `27.500 pF`. The Si4732 input consumes 8 pF and the worst registered ESD consumes up to 0.25 pF, leaving `19.250 pF` for SMA, PCB and pod parasitics. Generic long coax is therefore forbidden on this port.

Known component loss is not mistaken for complete-feed loss. For example, the CC 868/915 path already has a `1.840-dB` paper maximum from the balun and two switches before matching passives, launches and trace; all four branches remain conducted/VNA gates.

Machine evidence: [`H3-VRF51-rf-feed-constraints.json`](../hardware/verification/generated/H3-VRF51-rf-feed-constraints.json).
