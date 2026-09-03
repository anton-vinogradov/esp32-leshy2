# H6.0.2-R1 · Routing policy

[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h6-r2-routing-policy.ru.md)

**Status:** 🟡 all 823 physical nets across both boards (789 canonical) are assigned to 13 classes. The reviewed `GENERAL_CONTROL` set, all 12 crystal/oscillator nets and `SAFETY_CONTROL` are now routed completely; manual H6.0.2 work on analogue/audio/sense nets remains current. RF, USB, power, i8080 and clocked buses remain protected for their later manual releases.

| Class | Nets | Method | Geometry release |
| --- | ---: | --- | --- |
| `GROUND_REFERENCE` | 3 | manual plane/pour | `H6.0.3` |
| `PRIMARY_POWER` | 22 | manual | `H6.0.3` |
| `POWER_BRANCH` | 22 | manual | `H6.0.3` |
| `SWITCHING_NODE` | 15 | manual | `H6.0.3` |
| `RF_CONTROLLED` | 80 | manual | `H6.0.5` |
| `USB_DIFFERENTIAL` | 24 | manual | `H6.0.4` |
| `DISPLAY_I8080` | 10 | manual | `H6.0.4` |
| `OSCILLATOR` | 12 | manual | `H6.0.2` |
| `CLOCKED_DIGITAL` | 142 | manual | `H6.0.4` |
| `SAFETY_CONTROL` | 111 | manual | `H6.0.2` |
| `SERIAL_CONTROL` | 74 | manual | `H6.0.4` |
| `ANALOG_AUDIO_SENSE` | 143 | manual | `H6.0.2` |
| `GENERAL_CONTROL` | 165 | automatic proposal + manual review | `H6.0.2` |

## What is locked

- exact stack: `JLC06161H-3313`, 1.6-mm order nominal, 1.54-mm ±10% calculated finished thickness, and two 0.55-mm cores;
- four external USB ports expand to `12` complete differential-pair segments, and exactly ten direct i8080-8 nets are detected automatically;
- abstract RF, safety, ESD and power-ground anchors are physically canonicalized onto the solid `POWER_GROUND`; only `AUDIO_GROUND` remains local and joins it through explicit 0-ohm link `R172`;
- the current JLCPCB calculator sets outer 50-ohm RF CPWG to 5.31-mil width / 6-mil lateral copper gap and 90-ohm USB to 5.31-mil width / 6-mil pair gap;
- canonical `DP/DM` identities remain in the contracts, while physical KiCad net names end in `_P/_N`, allowing the native differential router to discover all 12 pairs;
- no automatic result is accepted before KiCad import, visual review and native DRC; completeness uses the full native connectivity count rather than the DRC JSON list capped at 499 rows.

## Disposable helper workspace

`hardware/layout/h6_r2_routing_workspace.py` exports temporary DSNs without the protected net definitions. Pads and components remain as physical obstacles, but Freerouting can see only `GENERAL_CONTROL` nets: `61` on the UI board and `104` on the RF/power board. This explicit filter is required because Freerouting 2.3.0 parses ignore-class and layer-active settings in headless mode but applies them only in the GUI loader. The disposable DSN therefore also declares `In1.Cu`/`In4.Cu` as non-signal layers. Generated DSNs and sessions are review inputs, never source or release artifacts. The helper may use only `F.Cu`, `In2.Cu`, `In3.Cu` and `B.Cu`; `In1.Cu`/`In4.Cu` remain uninterrupted reference planes, and the via cost is raised to `250`.

## Accepted H6.0.2 slice

The imported `GENERAL_CONTROL` and `SAFETY_CONTROL` proposals were repaired and reviewed in KiCad; oscillator branches were routed manually with short local geometry. The checked-in boards now resolve all **652/652** physical connections across all **288** allowed nets: 231 connections on UI and 421 on RF/power. They contain 5,273 track/via items, including 836 vias, use only the four permitted routing layers, touch zero protected nets and leave `In1.Cu`/`In4.Cu` untouched. Fresh KiCad 10.0.5 DRC reports contain **zero violations** and zero schematic-parity errors on both boards. The exact native unconnected totals are 996 (UI) and 1,617 (RF/power); the 499 rows shown by each JSON report are only KiCad's output cap.

The [accepted-routing audit](../hardware/layout/generated/H6-R2-general-routing-audit.json) binds those results to the exact PCB hashes and to the 1,208-position freeze. This is a slice inside H6.0.2, not completion of the phase: `ANALOG_AUDIO_SENSE` is still routed manually.

### What the real routing looks like now

Blue is front copper and red is back copper; holes and vias appear across both layers. These are direct exports from the checked-in `.kicad_pcb` files, not illustrative mockups. Each image carries the source board hash and becomes stale automatically after any PCB change.

**Front/UI board**

![Current front UI-board routing](images/h6-r2-routing-ui.svg)

**Rear RF/power board**

![Current rear RF/power-board routing](images/h6-r2-routing-rf.svg)

Run the exporter with KiCad's bundled Python:

```sh
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 hardware/layout/h6_r2_routing_workspace.py --output-dir /private/tmp/leshy2-routing
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 hardware/layout/h6_r2_general_routing.py --check
python3 hardware/layout/h6_r2_routing_render.py --write
```

[Machine audit and every assignment](../hardware/layout/generated/H6-R2-routing-policy-audit.json)
