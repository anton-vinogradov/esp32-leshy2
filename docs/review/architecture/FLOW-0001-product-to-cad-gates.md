# FLOW-0001 — corrected product-to-CAD development gates

- Статус: **Нормативно; проведено ревью метода**
- Дата: 2026-08-17
- Решение: [`DEC-0032`](../decisions/DEC-0032-reopen-product-design-before-cad.md)
- Owner sequencing: [`DEC-0058`](../decisions/DEC-0058-internals-before-integrated-mockup.md)
- Принцип: каждый downstream artifact потребляет только reviewed upstream outputs

## Gate chain

| Gate | Required inputs | Reviewed output | Explicitly forbidden output |
|---|---|---|---|
| `G0` review baseline | repository scope and working rules | evidence/decision/finding ledgers | product choice |
| `G1` product intent | vision, users, legal/safety boundaries | ranked goals and non-negotiable constraints | MCU/module/pin choice |
| `G2` capability model | `G1`, competitors, owner wishlist | complete capabilities, exclusions, concurrency and failure needs | physical implementation |
| `G2F` logical/electrical feasibility | `G2`; exact manufacturer device evidence | hardware-neutral signal demand; real-device pin provenance; ≥2 complete owner/bus/controller/GPIO candidates; owner-selected working electrical baseline | final architecture, schematic or PCB |
| `G3` target product design | `G1/G2/G2F` working baseline | form factor, interaction/control surfaces, interfaces, battery, antenna/service/environment/cost envelopes; adapted reproducible physical mockup | treating working pins or geometry as atomic target; PCB routing |
| `G4` whole-device candidates | `G2/G3` | at least two complete product architectures with no-loss disposition | mixing best fragments without re-synthesis |
| `G5` optimality decision | `G4`, weighted criteria and Pareto evidence | owner-selected candidate or explicit need for another iteration | selection by pin count or one subsystem alone |
| `G6` conceptual co-design | selected candidate | block placement, board partition, antenna/thermal/power/service feasibility and preliminary resource budgets | exact CAD as proof of fit |
| `G7` atomic architecture | `G5/G6` | owners, transports, reset/update/safety, exact resource/pin contracts and reopen gates | component substitution that changes architecture |
| `G8` components/BOM | `G7` | exact qualified components, lifecycle/supply/cost and alternates | unqualified footprint becoming normative |
| `G9` electrical/CAD | `G7/G8` | electrical specification, canonical libraries, schematic/ERC and firmware HAL contracts | PCB before schematic review |
| `G10` PCB/pre-fab | `G9` | placement/routing/DRC/SI/PI/RF/mechanical/manufacturing evidence | fabrication with an open hard gate |
| `G11` prototype | `G10` | assembly, bring-up, recovery, safety/RF/HIL measurements | release claims from paper analysis |

## Mandatory optimality dimensions

Each `G4` candidate is compared over the whole product, at minimum:

- complete capability and concurrency coverage;
- user ergonomics, accessibility and failure behavior;
- form factor, mass, board/enclosure complexity and module attachment;
- GPIO/controllers, compute/memory/throughput and firmware burden;
- RF coexistence, antenna volumes and body/enclosure influence;
- power, battery runtime, charging, thermal and brownout behavior;
- safety, independent STOP/recovery/diagnostics and owner openness;
- recurring BOM, assembly/test NRE, availability and repairability;
- qualification uncertainty and cost of a failed assumption.

Both a weighted score and a Pareto view are required. Weights are reviewed
before scores, sensitivity to reasonable weight changes is shown, and a
candidate dominated on all material axes cannot win through narrative alone.

## Iteration rule

`G2F…G6` intentionally form a loop: candidate feasibility may expose a product
envelope conflict. The loop updates an upstream artifact visibly and repeats
review; it never hides the conflict in an exact pin map or enclosure exception.

`G2F` is the explicit exception to the old assumption that logical pin
feasibility must wait for a selected enclosure. It gives physical design a
complete, checked working net/owner hypothesis, while its provisional status
allows later mechanical/RF/power evidence to reopen the map before `G7`.

## Owner-ordered internal closure before integrated mockup

`DEC-0058/INT-0001` pause the integrated G3 mockup after the bounded U214
envelope proof. The active loop deepens internal feasibility first: compute and
service, safety, power, UI/storage electrical endpoints, audio, RF/IR/voice,
expansion protection and consolidated component evidence. Integrated physical
layout resumes only after their joint paper/electrical review.

This does not silently promote candidate parts to `G8` or authorize KiCad.
Exact first targets, circuit calculations and local body/footprint/keep-out
checks are feasibility evidence until the whole-device and atomic gates pass.
Prototype/enclosure-only HIL remains downstream with explicit fixtures and pass
conditions; it is not an impossible prerequisite for drawing the later mockup.

Every counted pin passes `SoC → package → exact module/device → actual exposed
pad/header/connector`. A real dev-board is checked only when that board itself
is in the candidate; it cannot prove a custom WROOM/QFN implementation.

Feasibility probes may run early to answer bounded questions such as whether a
radio, connector or battery class exists. Their output is labelled draft and
cannot become an accepted component, footprint or target owner before its gate.

## Review status semantics

- **Проведено ревью** means the named artifact and its prerequisites were
  actually checked; it does not propagate automatically downstream.
- **Candidate/reference** preserves evidence without authorizing consumption as
  a final prerequisite.
- Any mismatch creates a finding and correction ledger entry.
- Any apparently extra capability or design element returns to the owner as an
  explicit proposal with context before removal or acceptance.
