# Machine-checked architecture data

This directory is the single source for **candidate** device contacts, logical
pin maps, complete non-MCU contact accounting and interface-resource
contracts. It is deliberately upstream of KiCad: passing these checks does not
select a target architecture or authorize schematic/PCB work.

## Files

- `devices.json` records exact device/module variants, exposed physical
  contacts, straps, recovery contacts, lifecycle and primary-source identity;
- `candidates/*.json` maps semantic nets to those exposed contacts;
- `generate.py` validates the data and renders the human-readable ledger in
  `docs/review/architecture/generated/G2F-pin-ledger.md` plus the focused
  `docs/review/architecture/generated/G2F-3I-principled-pinout.md` atlas;
- `tests/test_generator.py` protects the main failure modes.

## Commands

From the repository root:

```sh
python3 hardware/architecture/generate.py --check
python3 -m unittest discover -s hardware/architecture/tests -v
```

After an intentional source-data change:

```sh
python3 hardware/architecture/generate.py --write
```

`--check` fails when the generated ledger is stale, JSON repeats a key, a pin
is not exposed by the exact device, a GPIO or declared expander contact is
double-booked/unaccounted, a strap lacks an explicit reset proof, no complete
service alternative exists, an exact peer endpoint is unknown, or a scheduled
resource lacks its arbitration contract. For the leading B-package map it also
rejects a PIO pin outside the selected real GPIO-base window, fixed-mux contact
drift and controller/DMA overbooking. Provisional external contracts remain
visible qualification gaps; the generator never silently promotes them to
verified parts.

`G2F-3I` is the leading reviewed **paper** map selected by `DEC-0044/NIF-0001`.
Its digital non-interference/resource contracts pass these checks; physical RF,
electrical/HIL and complete target-architecture acceptance remain upstream
gates.

Its I3 power source now also records the `DEC-0067` no-deep-recovery boundary
and exact active CSD87313DMST/fuse/shunt/NTC/hold/source-isolation packages,
plus `DEC-0070`'s two exact `MMBT3904-7-F` switched-rail PG qualifiers,
`DEC-0072`'s 24 exact converter energy/configuration/feedback passives and the
`DEC-0080`-amended ten exact EN/PG/POR/fault resistor positions. DEC-0080 also
replaces the abstract source sequencer with `AON_PG_N → TPS3808.MR_N` and
delayed `POR_N → main EN`. `DEC-0081/PWR-0020` now add exact independent
`TPS25961DRVR` AON and two `TPS25974LRPWR` main/voice post-buck boundaries,
all setting passives and protected-side PG; raw converter PG is diagnostic
only. `DEC-0074/PWR-0013` first added
the bounded diagnostic and PA25/PA26 ADC frontends; `DEC-0078/PWR-0017` now
correct the TPUL WQFN contact map, cascade its second channel into a `>=350 ms`
hardware refractory lockout and use two parallel
`CRM2512-FX-20R0ELF` 20-Ohm/2-W load branches. The effective 10-Ohm load and
25-50-ms pulse are preserved, while dense faulty firmware retries can no
longer create near-continuous heating. Regression checks prevent both the
invalid battery-derived PA24 assignment and the TPUL pin swap from returning.
`DEC-0077/PWR-0016` instantiate exact polarized `Keystone Electronics 1048P`,
four functional slot contacts and the three insulated compliant NTC roles.
`DEC-0079/PWR-0018` then replace both generic cell nodes with separate exact
`XTAR 18650 4000mAh` protected button-top instances, freeze `28.8 Wh` nominal
pair energy and a 2-A charge ceiling. This is still a principle-level circuit
contract: assembly certification, received fit, exact-cell droop thresholds,
thermal-stack material and specimen HIL remain open.

`DEC-0082/PWR-0021` now mark the complete I3 paper electrical input reviewed
without promoting any physical result. The machine-readable
`paper_closure_status` records that maturity, while every `remaining_i3`
entry is explicitly classified as procurement/I8 or prototype/controlled
HIL. I4 paper work may consume the exact rail and fault contracts; any measured
functional or derating conflict reopens I3 before propagation.

The inventory also contains verified reference boundaries. `DSP-0001` covers
three display/touch devices and one microSD socket; `DSP-0005` additionally
instantiates the exact disclosed `HMX035CTFT-001` assembly in `G2F-3I` and
checks its 40-contact QSPI/touch fit. This remains a paper candidate: exact
FPC mechanics/connector, standalone orderability/lifecycle, backlight,
protection, optics and HIL must close before production acceptance.

`AUDIO-0001/REV-0005B` additionally instantiate the exact Everest
Semiconductor `ES8311` QFN-20 contact map. I2C/I2S fit consumes no new GPIO;
`CE` is address strap `0x19`, while slow P10 is external `CODEC_PWR_EN`.
Power switching and differential analog routing remain explicit blockers in
`FND-0065/IMP-0046`.
