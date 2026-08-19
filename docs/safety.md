# Leshy2 safety model

[Home](../README.md) · [Русский](safety.ru.md) · [Hardware architecture](hardware.md)

## Three functional levels

| Level | Purpose | Entry conditions |
|---|---|---|
| Normal mode | Receive, diagnostics, maintenance, navigation and ordinary lawful communications | Normal UI and regional profile |
| Laboratory | Passive, defensive and constrained research tools | Explicit section entry and visible consequences |
| Controlled Zone | Active or disruptive functions | Fresh banner on every entry, separate arming, authorized target or isolated environment |

Initial setup requires acceptance of a non-aggression agreement. It records the
intent to use the device lawfully and with permission, but never grants a
technical transmit capability or replaces national law, spectrum licensing,
privacy requirements or the target owner's consent.

## Transmit control

- Every transmit path starts off after reset, update, recovery, profile change
  or fault.
- Permission is bound to one path, band, power, time and selected target.
  Signal presence or an attached antenna cannot arm transmit.
- The UI previews mode, consequences and limits. Dangerous actions require a
  separate confirmation and a held dead-man action.
- Independent RF or optical evidence verifies actual transmission. A mismatch
  between command and evidence immediately revokes permission.
- Unused RF and digital interfaces are powered down, isolated and discharged
  into a measurable quiet state.

## RUN/KILL, watchdog and fault reporting

The side `C&K JS102011SCQN` is the only physical `RUN/KILL` control. `KILL`
removes the hardware transmit permit and asks the pack controller to shut the
device down; `RUN` supplies the only physical re-arm edge. There are no
separate STOP or RE-ARM buttons. Firmware, reset, USB and the service headers
cannot create that edge or clear a latched fault.

An AON `MSPM0C1104SDGS20R` supervises system heartbeats, short-lived per-group
transmit leases, physical TX evidence, rail faults and three independent board
temperature zones. An external `TPS3435CAKAGDDFR` timeout watchdog directly
latches `FAULT_KILL` if the safety controller stops making valid 1.6-second
deadline service. The device never restarts automatically: recovery requires a
physical `KILL → RUN` cycle after the cause is safe.

For a non-UI fault, C5 and RP remain in reset while S3 may run only the signed,
bounded fault screen. It states the primary cause, affected zone or signal
group, measured value and limit when known, action already taken, event ID and
restart instruction. If the UI/display zone itself overheats or its rail is
unsafe, hardware protection turns the screen off; the independent amber FAULT
LED and retained AON record remain available.

## Power and cells

- Main, voice and accessory rails have independent hardware cutoffs. A fault
  in one branch cannot turn software control of another into a bypass.
- Charging begins only after a valid USB-PD contract and pack admission, is
  capped at 2 A and uses independent cell-temperature sensing.
- Only two qualified protected button-top `XTAR 18650 4000mAh` cells in a
  `Keystone 1048P` are supported. Raw flat-top cells and one-cell operation are
  not supported.
- A deeply discharged or inconsistent pair is rejected. There is no onboard
  zero-volt recovery; such research belongs on a separate isolated fixture.

## Update and recovery

- Each controller accepts only an image for its target and verifies its
  signature. The package carries a compatible manifest for the complete image
  set.
- A new image is written to an inactive slot first. Failed startup causes
  rollback rather than loss of the working image.
- Owners can use their own build keys and install their own firmware.
  Irreversible key lockdown is not enabled by default, preserving device
  openness.
- S3, C5, RP2354B and both MSPM0 controllers have independent physical
  recovery paths. Every recovery boot starts TX-off; RUN/KILL, the watchdog
  and the hardware FAULT_KILL latch remain effective.

An update can be substituted through a compromised server, mirror, download
path or removable medium. Signatures defeat that substitution by verifying the
author and integrity locally before execution. They neither hide the source nor
prevent an owner from signing a custom build.
