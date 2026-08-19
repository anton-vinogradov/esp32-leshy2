# REV-0005AU — I5 audio and receiver propagation

- Status: **Проведено ревью**
- Decision: [`DEC-0090`](../decisions/DEC-0090-i5-exact-audio-and-receiver-paper-closure.md)
- Finding: [`FND-0095`](../findings/FND-0095-i5-abstract-audio-hidden-power-domain-failures.md)

## Propagation matrix

| Consumer | Result |
|---|---|
| exact device registry | pass: codec/receiver/voice power and isolation ICs, microphone, speaker, jack, ESD, crystal, beads, capacitors and resistors have exact MPN/contact records |
| machine instances | pass: each physical IC and each physical passive body is an independent instance; parallel headphone capacitors and four I2S buffers are not collapsed |
| exposed contacts | pass: every contact of 31 core I5 devices is present in at least one fixed route; NC and fixture-only contacts are explicit |
| slow-I/O budget | pass: P00 capture source, P01 speaker enable, P02 headphone absence; `21 used / 0 reserved / 3 free`; no control removal |
| codec power/interfaces | pass: reset-off QOD switch, 3.08-V/200-ms supervisor, local I2C pulls, dual I2C isolation and four directional I2S isolation devices |
| receiver power/interfaces | pass: independent reset-off/QOD branch, supervisor-held RST, isolated I2C and open-drain IRQ, exact crystal/load and two-address specimen probe |
| voice safety | pass: STOP-qualified rail threshold/delay, fail-RX PTT, sleeping UART low, low-or-open H/L, isolated AFOUT/MIC_IN, fixture-only UPDATE and standard VOXEN no-connect |
| analog paths | pass: receiver bypass, receiver/microphone capture, codec playback, ordinary electret TX and armed codec TX injection all terminate through exact parts/values |
| acoustic endpoints | pass: exact microphone, 4-Ohm speaker and switched 3.5-mm jack with protection, coupling and insertion sensing |
| quiet-state policy | pass: unused domains discharge or isolate; speaker and codec selections reset off; PTT authority remains separate |
| runtime/firmware | pass: exact addresses, sequencing, modes, defaults and fault behavior are propagated into the firmware architecture |
| power/cost | pass: main-rail envelope remains valid; additions are low-cost isolation/passive closure and do not materially expand functionality or budget |
| target product pages | pass: both vertical diagrams name exact MPN and role in separate boxes; review-ledger IDs remain absent from target landing pages |
| downstream boundary | pass: RF feeds/matching/protection and conducted/OTA evidence remain I6; external accessories remain I7 |
| CAD/mockup | pass: no KiCad authorization, atomic freeze or integrated-mockup restart is inferred |

## Self-review corrections

| Observed mismatch | Correction made |
|---|---|
| logical buses could back-power switched endpoints | added independent supervisors, discharged switches and physical per-direction isolation |
| SA518 H/L looked like an ordinary GPIO | inserted exact open-drain driver; direct slow-I/O-to-module route is forbidden by regression test |
| PTT crossed directly into the module | inserted a separately powered tri-state stage plus module-side RX pull-up; AON gate remains the sole request source |
| capture source was undefined | added P00 selector and complete microphone/RX common-mode path |
| speaker/mic/headphone were abstract labels | selected exact parts and instantiated contacts, coupling, output EMI and ESD |
| Si4732 public strap/address information is ambiguous | first population is SENB-low but firmware probes both `0x11` and `0x63`; HIL, not prose, freezes identity |
| old status still assigned exact audio/passive closure to I5 | machine and stage text now mark paper closure complete and I6 active while preserving HIL residue |

## Verification result

- architecture source JSON parses without duplicate keys;
- generated pin ledger and principled design reproduce from the machine source;
- 53 architecture regression tests pass, including the new all-contact I5
  endpoint audit;
- both target landing pages pass the vertical/exact-MPN/role and no-review-ID
  checks;
- firmware documentation tests pass after propagation.

I5 therefore has **«Проведено ревью»**. I6 is active. No unresolved question
or function-changing proposal remains in this block.
