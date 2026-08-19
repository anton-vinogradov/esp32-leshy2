# Hardware architecture sources

This directory is the machine-readable source for the Leshy2 device map.

- `devices.json` contains physical devices, exact/current MPNs and contact data.
- `candidates/G2F-3I.json` assigns devices, nets and controller resources in the
  consolidated target architecture.
- `antenna-kit.json` is the dated 12-item full-field antenna manifest, including
  exact first targets, connector polarity, availability and remaining gates.
- `am-lw-pod.json` defines the passive controlled AM/LW pod assembly, its exact
  constituent first targets and the measurements still required before release.
- `generate.py` validates the sources and emits the exact pad/net atlas, pin
  ledger and BOM into `generated/`.
- `tests/` checks contact accounting, GPIO availability, safety defaults,
  resource exclusivity and generated output freshness.

Generate or verify the artifacts with:

```sh
python3 hardware/architecture/generate.py --write
python3 hardware/architecture/generate.py --check
python3 -m unittest discover -s hardware/architecture/tests
```

The public product description is in [`docs/hardware.md`](../../docs/hardware.md).
