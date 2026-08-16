# REQ-IMU-0001 — external measurement-pose IMU contract

- Статус: **Проведено ревью требований; implementation proof открыт**
- Дата: 2026-08-16
- Решение: [`DEC-0037`](../decisions/DEC-0037-optional-external-imu-measurement-pose.md)
- Evidence: [`AUD-0008`](../audits/AUD-0008-imu-instrument-value-and-placement.md)
- Режим: **Основной / optional passive instrument accessory**

## Capability contract

| ID | Requirement | Acceptance boundary |
|---|---|---|
| `REQ-IMU-01` | Optional external IMU adds motion/pose provenance to selected scan/hunt/log records. | Raw RF functions remain complete without the accessory; attachment never auto-starts capture or transmit. |
| `REQ-IMU-02` | Device-pose data requires a rigid keyed/indexed mechanical relation. | Every record names mount ID and versioned sensor→enclosure→antenna transform; dangling/free module data is labelled module-only and cannot annotate device pose. |
| `REQ-IMU-03` | Accepted 6-axis result is bounded. | Raw accel/gyro, pitch/roll, short-term relative rotation and stability/motion flags only; dynamic acceleration and gyro drift lower or invalidate quality. |
| `REQ-IMU-04` | Pose and RF time domains are explicit. | Monotonic sensor timestamp, host receipt time, associated RF window, sample age, interpolation rule, ODR and lost/late sample counters are recorded. |
| `REQ-IMU-05` | Calibration and quality are visible. | Sensor identity/revision, range/ODR, bias/calibration state, axis transform, temperature if used and validity envelope accompany derived fields. No stale last-known pose is shown as live. |
| `REQ-IMU-06` | No heading or RF inference is overclaimed. | Six-axis data is never called absolute yaw/compass heading; pose metadata is never called RF bearing/azimuth, distance, RSSI/dBm, AoA or VSWR. |
| `REQ-IMU-07` | Fault/removal degrades only contextual metadata. | Missing, removed, stale, corrupt or bus-faulted accessory marks pose unavailable/invalid; it does not discard raw RF data, weaken STOP or change TX authorization. |
| `REQ-IMU-08` | Passive sensing remains passive and privacy-visible. | Capture/export visibly indicates inclusion of motion metadata and supports bounded retention/removal; no silent person tracking or remote telemetry follows from attachment. |
| `REQ-IMU-09` | IMU cannot make security/destructive decisions. | No transmit, Controlled-Zone entry, secret erase/unlock, FIDO presence, tamper or fall decision is triggered solely by IMU data. |
| `REQ-IMU-10` | Accessory implementation remains replaceable. | U095 is the first catalog/prototype baseline, not a permanent MPU6886 lock; replacement preserves the same truthful result and passes identity, driver, calibration, electrical and HIL gates. |
| `REQ-IMU-11` | Expansion electrical contract remains authoritative. | I²C address sharing, power, protection, attach/detach and wrong-profile behavior follow `REQ-EXT-0001`; U095 polling is not advertised as a hardware-timestamp interrupt path. |
| `REQ-IMU-12` | Absolute heading is a separate capability. | Magnetometer/GNSS/other heading source is absent until separately approved with hard-/soft-iron, placement, current/magnet/accessory interference and calibration evidence. |

## Architecture and release gates

- G3: indexed mount, use posture, axis markings, antenna-frame relation and
  collision with Unit/Cap/high-speed surfaces.
- G4/G7: exact accessory/profile, power/I²C/address topology, polling/timing,
  transform storage and lifecycle-qualified replacement.
- G9: record schema, fusion/quality algorithm, privacy/export behavior and
  deterministic invalidation rules.
- G11: static/dynamic calibration corpus, known-angle fixture, motion windows,
  time alignment, cable/mount error, attach/removal/bus faults and negative
  heading/RF-bearing UI/export tests.

Receiving valid I²C samples is not device-pose or RF-direction evidence.
