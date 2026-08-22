# Current ECAD status

There is **no current Leshy2 schematic or PCB layout in this directory yet**.
The previous tscircuit sheets and their partial KiCad exports were moved to
[`drafts/legacy-2026-08-22/tscircuit-pre-g2f3i`](../../drafts/legacy-2026-08-22/tscircuit-pre-g2f3i/)
because they describe a superseded device: 80-mm boards, a 4-inch ST7796
display, discrete D-pad buttons, STOP, onboard LoRa, SA868 and the old
controller/resource assignment.

Those files are retained only as historical implementation material. They must
not be built, reviewed as the current circuit or sent to a PCB manufacturer.

The current electrical source is the machine-reviewed `G2F-3I` architecture in
[`hardware/architecture`](../architecture/). A new reviewable schematic is the
next ECAD artifact and must be generated from that source. KiCad PCB placement
and routing remain unauthorized until the current schematic, ERC, power/fault
simulation and joined mechanical/electrical/firmware review pass.
