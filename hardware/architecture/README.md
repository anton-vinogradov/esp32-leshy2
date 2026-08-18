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
plus `DEC-0070`'s two exact `MMBT3904-7-F` switched-rail PG qualifiers. This is
still a principle-level circuit contract: passive values, diagnostic load,
mechanical polarity/thermal coupling and HIL remain open.

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
