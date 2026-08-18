# REV-0005AR — exact control switch/protection propagation

- Status: **Проведено ревью**
- Decision: [`DEC-0087`](../decisions/DEC-0087-exact-control-switch-and-protection-endpoint.md)
- Finding: [`FND-0092`](../findings/FND-0092-control-switch-current-and-esd-were-abstract.md)

## Propagation matrix

| Consumer | Result |
|---|---|
| complete control inventory | pass: D-pad/OK, BACK, OPT, F1, F2, encoder push, PTT, STOP and RE-ARM all remain present |
| direct/slow ownership | pass: PTT remains RP GPIO21; encoder A/B remain direct S3 PCNT0; ordinary buttons alone use the matrix |
| safety truth table | pass: STOP remains COM+NC fail-open; RE-ARM remains NO/fresh-edge; neither depends on an MCU or I2C |
| contact-current range | pass: Y78B23214FP ULC covers matrix/PTT/RE-ARM; AEQ10410 covers nominal 0.33 mA at 3.3 V |
| protection | pass on paper: P0…P7, encoder/PTT and STOP/RE-ARM each have exact ESD channels; safety return is separate |
| machine contacts | pass: every selected device contact exists in the registry and every route names an exact exposed land/terminal |
| root product diagrams | pass: vertical diagrams name exact MPN and role, and no square combines different devices |
| cost/function | pass: no capability or pin is removed; formerly mandatory abstract controls become costable BOM positions |
| firmware | pass: runtime identities and direct/matrix/AON boundaries remain compatible; exact debounce/filter constants are propagated |
| CAD boundary | pass: physical actuator, guard, harness, placement, sealing and HIL remain open; no KiCad authorization is inferred |

## Self-review correction

The first screened STOP candidate, `D2F-01`, would have operated below its
datasheet minimum applicable load. The review rejected it before acceptance
and selected `AEQ10410`, whose low-level range contains the existing circuit.
No AON voltage, GPIO, function or user-visible behavior changed.
