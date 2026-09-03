# H6.0.2-R1 · Routing policy

[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h6-r2-routing-policy.ru.md)

**Status:** ✅ all 858 physical nets across both boards are assigned to 13 classes before routing starts. An automatic helper may propose copper only for ordinary low-rate control nets; RF, USB, power, i8080, clocked buses, oscillators, safety and analogue nets remain manual.

| Class | Nets | Method | Geometry release |
| --- | ---: | --- | --- |
| `GROUND_REFERENCE` | 32 | manual plane/pour | `H6.0.3` |
| `PRIMARY_POWER` | 22 | manual | `H6.0.3` |
| `POWER_BRANCH` | 22 | manual | `H6.0.3` |
| `SWITCHING_NODE` | 15 | manual | `H6.0.3` |
| `RF_CONTROLLED` | 80 | manual | `H6.0.5` |
| `USB_DIFFERENTIAL` | 24 | manual | `H6.0.4` |
| `DISPLAY_I8080` | 10 | manual | `H6.0.4` |
| `OSCILLATOR` | 12 | manual | `H6.0.2` |
| `CLOCKED_DIGITAL` | 142 | manual | `H6.0.4` |
| `SAFETY_CONTROL` | 111 | manual | `H6.0.2` |
| `SERIAL_CONTROL` | 78 | manual | `H6.0.4` |
| `ANALOG_AUDIO_SENSE` | 143 | manual | `H6.0.2` |
| `GENERAL_CONTROL` | 167 | automatic proposal + manual review | `H6.0.2` |

## What is locked

- exact stack: `JLC06161H-3313`, six layers, 1.6 mm, two 0.55-mm cores;
- four external USB ports expand to `12` complete differential-pair segments, and exactly ten direct i8080-8 nets are detected automatically;
- RF/USB widths are not guessed: H6.0.4/H6.0.5 bind them to the current JLCPCB calculator;
- no automatic result is accepted before KiCad import, visual review and native DRC.

## Disposable helper workspace

`hardware/layout/h6_r2_routing_workspace.py` exports temporary DSNs without the protected net definitions. Pads and components remain as physical obstacles, but Freerouting can see only `GENERAL_CONTROL` nets: `61` on the UI board and `106` on the RF/power board. This explicit filter is required because Freerouting 2.3.0 parses its ignore-class option in headless mode but applies it only in the GUI loader. The generated DSNs and sessions are review inputs, never source or release artifacts.

Run the exporter with KiCad's bundled Python:

```sh
/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 hardware/layout/h6_r2_routing_workspace.py --output-dir /private/tmp/leshy2-routing
```

[Machine audit and every assignment](../hardware/layout/generated/H6-R2-routing-policy-audit.json)
