# RF electrical verification · H3-R2.5

**Current status: `review_required`.** Numerical and logical checks below are retained as provisional. Applicability to the fitted power cell is checked separately; open analytical findings are not reclassified as physical tests. This result does not authorize phase advancement, purchasing, fabrication or battery energization.

Open: `applicability:digital_inputs`; `applicability:analog_inputs`.

[Machine evidence](../hardware/verification/generated/H3-R2-rf-coexistence.json).

The ten source-to-port paths are local to the PCB that carries their antenna: `5 + 5`, with no RF crossing M1. S3 and C5 retain exact 30-mm jumpers; the three nRF paths use exact 60-mm jumpers. The conservative generated reach test leaves at least **9.388 mm** and bounds every nRF from the farthest corner of the complete module envelope rather than guessing the IPEX axis. Airband is a receive-only selectable branch behind the existing `RX-FM/SW` port.

Paper component limits are internally consistent: C5 keeps 115-MHz connector margin at 5.885 GHz, the nRF coupler is at most 0.250 dB, the known CC1101 868/915-MHz balun-plus-switch contribution is 1.840 dB before passives/trace/connector, and the AM/LW external capacitance budget remains 19.500 pF.

Runtime still admits at most one of nine top-level signal groups and preserves all thirteen quiet contracts. The deliberate `SG-N24` internal exception keeps all three radios active in 3PRX, 1PTX+2PRX, 2PTX+1PRX and 3PTX, covering eight radio-identity permutations under both support loads.

The component-limit and policy comparisons above are provisional. Current power applicability remains open alongside the seven existing physical RF residuals; this does not close the pre-layout electrical model or prove final RF performance.

Machine evidence: [`H3-R2-rf-coexistence.json`](../hardware/verification/generated/H3-R2-rf-coexistence.json).
