# RF layout constraints · historical R1

`H3.5.2` is reviewed with `23` machine checks and no open analytical finding. The historical R1 progression marker is `H3.6.1`.

The H1 lines remain topology/corridor guides, not alleged KiCad copper. Their projected lengths are carried forward only so H6 cannot silently lose or swap a path.

| Path | Board inner frame | H1 guide, mm | Maximum via-fence pitch, mm |
|---|---:|---:|---:|
| S3-2G4 | ui-inner | 14.474 | 1.25 |
| C5-2G4/5 | ui-inner | 14.474 | 1.25 |
| N24-0 | rf-inner | 45.950 | 1.25 |
| N24-1 | rf-inner | 43.812 | 1.25 |
| N24-2 | rf-inner | 36.636 | 1.25 |
| CC-SUB | rf-inner | 24.244 | 2.5 |
| VOICE-VHF | rf-inner | 45.575 | 2.5 |
| VOICE-UHF | rf-inner | 47.333 | 2.5 |
| RX-FM/SW | ui-inner | 92.346 | 2.5 |
| RX-AM/LW | ui-inner | 80.511 | capacitance-controlled |

For every ordinary RF mainline H6 must solve the released stack-up, preserve one uninterrupted reference plane, use no tee/test stub, prefer zero and allow at most one field-solved signal-layer transition, and place connector/ESD/matching return vias immediately. The common 2.4/5-GHz fence pitch is `1.25 mm`, rounded below the conservative `lambda_g/20 = 1.361 mm` value at 5.885 GHz and effective permittivity 3.5.

`RX-AM/LW` is deliberately different: its high-impedance segment gets no generic 50-ohm plane or fence. Its connector, PCB, ESD and pod capacitance must instead fit the H3.5.1 `19.500-pF` external budget.

Machine evidence: [`H3-VRF52-rf-layout-constraints.json`](../hardware/verification/generated/H3-VRF52-rf-layout-constraints.json).
