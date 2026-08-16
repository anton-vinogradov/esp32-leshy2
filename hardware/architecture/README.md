# Machine-checked architecture data

This directory is the single source for **candidate** device contacts and
logical pin maps. It is deliberately upstream of KiCad: passing these checks
does not select a target architecture or authorize schematic/PCB work.

## Files

- `devices.json` records exact device/module variants, exposed physical
  contacts, straps, recovery contacts, lifecycle and primary-source identity;
- `candidates/*.json` maps semantic nets to those exposed contacts;
- `generate.py` validates the data and renders the human-readable ledger in
  `docs/review/architecture/generated/G2F-pin-ledger.md`;
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

`--check` fails when the generated ledger is stale, a pin is not exposed by
the exact device, a GPIO is double-booked/unaccounted, a strap lacks an
explicit reset proof, a service path is missing, or an exact peer endpoint is
unknown. Provisional external contracts remain visible qualification gaps; the
generator never silently promotes them to verified parts.

The inventory also contains verified reference boundaries that are not yet
instantiated in either map. `DSP-0001` currently covers three display/touch
devices and one microSD socket. `DEC-0043` accepts the task/dirty-region
performance contract, but their presence still proves real contacts only. An
exact MPN/interface/optics choice and HIL must close before a display can
replace the abstract endpoint in a candidate.
