# REV-0005AT — consolidated I4 propagation

- Status: **Проведено ревью**
- Decision: [`DEC-0089`](../decisions/DEC-0089-consolidated-i4-electrical-closure.md)
- Finding: [`FND-0094`](../findings/FND-0094-consolidated-i4-audit-found-hidden-interface-gaps.md)

## Propagation matrix

| Consumer | Result |
|---|---|
| exact device registry | pass: `TCA6424ARGJR` qualification, orderable source, all 32 contacts, exposed pad and electrical contract are recorded |
| machine instances | pass: independent VCCI/VCCP bypass, bulk, reset pull-up, two AON isolators with bypass/pull-up and STOP LED resistor are physical instances |
| fixed routes | pass: TCA supplies/grounds/ADDR/RESET/SCL/SDA/INT and all new passive/buffer endpoints terminate on real exposed contacts or explicit planes/test points |
| partial power | pass: direct AON-high routes to P22/P23 are absent; open-drain transfer preserves polarity and cannot positively inject an off main domain |
| bus addresses | pass: exact `0x20`, `0x22`, `0x2A`, `0x38` and candidate `0x3F` are visible; ES8311/Si4732 remain assigned to I5 rather than guessed |
| microSD | pass: DAT0/MISO route terminates at real S3 GPIO4; sharing and performance contract are unchanged |
| USB/FPC boundary | pass: shell uses direct local power/ESD-ground bond; internal no-live-insertion FPC policy is explicit and reopenable by mechanics |
| controls | pass: full D-pad, PTT, STOP, F1, F2 and encoder remain; UI P7 is a protected reserve, not an omitted control |
| STOP indication | pass: exact 2.2-kOhm physical resistor replaces the abstract element; indication remains independent of firmware |
| product diagrams | pass: both vertical target diagrams name every new exact MPN and role in separate boxes |
| firmware | pass: runtime consumes `0x22`, `0x2A`, reset/power-cycle recovery, shared-source discovery and isolated P22/P23 semantics |
| budgets | pass: S3 `33/3/0`, C5 `14/6/1`, RP `48/0/0`, main slow `18/0/6`, UI `7/1/0`; no ownership changes |
| downstream boundary | pass: I5/I6/I7 endpoint abstractions stay visible; I4 closure does not promote them |
| CAD/mockup | pass: no KiCad authorization, atomic freeze or integrated-mockup restart is inferred |

## Self-review corrections

The audit corrected four misleading residues in addition to the slow-I/O core:
the stale no-reserve claim, textual microSD GPIO endpoint, abstract STOP LED
resistor and unproved USB chassis node. It also fixed the pack target address
before that omission could appear as a hardware-bus collision during I5.

Every unresolved I4 item now names a prototype, layout or procurement proof.
No generic paper electrical endpoint remains in the I4-owned scope.
