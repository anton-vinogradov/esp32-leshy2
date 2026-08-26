# RF verification result

`H3.5` is reviewed: three leaf packages contribute `128` passing checks and this consolidation adds `22` cross-domain checks. No analytical finding remains open. The exact current marker is `H3.6.1`.

The closed paper contract contains ten source-to-port paths, eight TX-capable paths, five removable microcoaxes, nine runtime signal groups and thirteen quiet-state contracts. VHF and UHF are independent physical feeds but one runtime group with hardware one-hot selection. Ordinary RF mainlines have feed/loss, corridor, plane and return rules; `RX-AM/LW` retains its separate high-impedance `19.500-pF` external-capacitance contract. Full 3×nRF24 remains mandatory in all four role mixes and all eight identity permutations.

This is a pre-layout result, not final RF performance. `18` physical-only items are explicitly assigned to H5 received evidence, H6 field-solved/coupon-correlated routing and H8 VNA/spectrum/OTA/coexistence qualification. It does not authorize purchase, KiCad placement/routing or fabrication.

Machine evidence: [`H3-VRF54-rf-consolidation.json`](../hardware/verification/generated/H3-VRF54-rf-consolidation.json).
