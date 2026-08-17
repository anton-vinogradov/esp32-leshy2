# PD-0001 — reviewed G3 physical-product inputs

- Статус: **Проведено ревью входов**
- Дата: 2026-08-17
- Gate: `FLOW-0001/G3`
- Capability closure: [`REV-0002AS`](../reviews/REV-0002AS-stage-2-delta-rereview.md)
- Visual candidates: [`LAY-0001`](LAY-0001-form-factor-candidates.md)

## Product boundary

G3 defines the object a person holds, sees, connects, services and carries. It
does not select compute ownership, buses, GPIO, components or PCB routing.
Every candidate below must support the same reviewed capability target; size or
control-surface alternatives cannot delete a radio/key result.

## Mandatory external/user surfaces

| Surface | G3 invariant |
|---|---|
| display | readable field status, level, armed/actual-TX, errors and local confirmation; `DEC-0053` fixes a 3.5-inch portrait `320×480` IPS direct-QSPI capacitive-touch class, while exact production MPN, brightness/cover lens and mechanics remain variables |
| local navigation | complete core, safety, pairing/revoke, update/recovery operation without phone; permanent text keyboard absent |
| safety controls | direct protected hard STOP, deliberate recessed/recess-protected RE-ARM, side hold-to-talk PTT; distinguishable by touch |
| audio | speaker, microphone path where selected voice profile requires it, and serviceable headphone/line route without blocking grip |
| storage/service | accessible removable storage and product USB device/service; neither implies generic USB host |
| repair access | a labeled service hatch/area large enough for independent direct programming, recovery and diagnostics of every later-selected programmable chip |
| M5 Cap | full Cardputer-compatible 14-pin U214 dock; 84×24×15.2 mm Cap, RP-SMA/cable bend and downstream Port-A remain physically usable |
| M5 Unit | at least the important `U214 + downstream Port A + another Unit` configuration; cable strain relief and replaceable mount for 24/32/48/72/84 mm Units |
| field mechanics | lanyard/tether point, glove operation, protected connectors, replaceable retention, no reliance on magnets for indexed IMU |

## RF and antenna zoning inputs

- three nRF24 antenna identities need stable, marked enclosure-frame geometry
  and maximum practical mutual isolation because every simultaneous PTX/PRX
  role mix is required without automatic peer standby or hidden RX gaps
  for simultaneous RPD comparison; one switched antenna is not equivalent;
- 2.4/5 GHz Wi-Fi/BLE/802.15.4, Sub-GHz, analog voice and broadcast/HF receive
  need honest separate/shared-path candidates and body-shadowing evidence;
- every external/onboard TX must remain clear of the U214/GNSS sky-view and
  external Unit cable/antenna envelope;
- physical STOP/actual-TX indication and RF-safe power domains cannot depend on
  a touchscreen, phone or removable accessory;
- G3 reserves zones and user access, not antenna count/connector type or RF
  topology. Later [`DEC-0048`](../decisions/DEC-0048-external-sma-antenna-bank.md)
  fixes one of those formerly open axes: every onboard RF antenna endpoint is
  external SMA, and the three nRF paths have three dedicated SMA. Exact
  non-nRF count, connector implementation and feed topology remain G4–G7 work.

## Power, thermal and service inputs

- autonomous battery operation, charging and visible power state are required;
- the future envelope must tolerate the accepted voice-radio transient class,
  display/audio/storage activity and qualified accessory load without hidden
  brownout or unsafe TX restart;
- replaceable battery is desirable but not assumed free: sealing, thickness,
  certification and connector wear are scored explicitly;
- service access may sit behind a screwed hatch, but no selected chip may need
  another chip/firmware to enter recovery;
- prototype access is permanent. A production cover may protect it, not delete
  it or make it destructive to reach.

## Explicit zero-burden exclusions

No candidate gains size, connector, compute, RF, secure-store or test budget
for an integrated keyboard, haptic motor, personal FIDO, generic USB host,
6 GHz/Wi-Fi 6E, onboard GNSS, onboard LoRa or onboard HF NFC frontend.
BadUSB remains software-only over the existing USB-device path.

## Working-envelope semantics

Dimensions in `LAY-0001` are feasibility envelopes, not industrial-design
commitments. They include grip/body, protective walls and service clearances,
but not every antenna protrusion or attached Unit. G4 must replace each range
with exact component/board/antenna/battery evidence before scoring fit.

## Gate result

- [x] reviewed capabilities translated to physical surfaces;
- [x] exclusions cannot survive as hidden product volume;
- [x] U214/Unit and RF/service drivers included;
- [x] electronics, pins and components remain unselected;
- [x] three same-scope visual candidates may be generated.
