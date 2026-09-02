# Thermal, single-fault and extended-operation result · H3-R2.6

[Русский](thermal-fault-electrical-verification.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

`H3-R2.6` is reviewed: **25 checks**, `56` thermal profiles and `30` single-fault cases pass with no open analytical finding. H3-R2.7, global H4-R2 and global H5-R1 are also reviewed; the current marker is `H6.0.1-R1`.

## Thermal envelope

Only the `SUPPORT_IDLE` support load is eligible for sustained thermal qualification and external 5 V is capped at 1.00 A. The worst continuous calculation profile is `VOICE/PTT_TX_MAX/SUPPORT_IDLE`: a conservative `7.418 W` inside the enclosure. At 35 °C H6 must achieve no worse than `4.044 K/W` before the 65 °C warning. That TX case remains a bounded session pending H8, not permission for unattended TX. The absolute electrical corner `VOICE/PTT_TX_MAX/SUPPORT_WORST` reaches `16.596 W` but is not a sustained permission. Three NTCs, warning/kill/rearm thresholds and charger `TREG=60 °C`, `TSHUT=85 °C` remain independent protections. This is a parameterized upper bound, not a finished-enclosure temperature claim.

## Single faults

All 30 cases have detection, primary and independent/fail-safe containment, a safe result and physical recovery. The maximum paper detection deadline is 1760 ms for the independent watchdog. Automatic or software re-arm is forbidden; the fault plane is proved at every physical `KILL to RUN`.

## Extended operation

Long operation uses a qualified USB-PD source. `24/48 hours` are non-destructive H8 soak durations and full-proof intervals, not an autonomy promise. The setting is local-only and defaults to 48 hours. Expiry first revokes TX leases, then stops the session and requires physical re-arm. It cannot change watchdog or temperature limits.

## Physical-only residuals

- H6: solve the routed copper, vias, component spreading and enclosure thermal network; meet every admitted profile's 35-C resistance ceiling
- H6: keep RUN_PERMIT and FAULT_ASSERT_N routes, pads, returns and endpoint buffers physically independent
- H8: map POWER, RF/VOICE, UI/display, both cells, charger and external surfaces at each admitted sustained profile
- H8: inject SF-R2-01 through SF-R2-30 with current-limited fixtures/emulators and verify safe output, retained cause and physical-only re-arm
- H8: calibrate all thermal/evidence thresholds and measure watchdog, eFuse, reset, QOD and residual-energy timing
- H8: run ordinary non-destructive 24/48-hour qualified-USB soak plus battery-to-protected-cutoff measurement without converting it into an uptime promise
- H8: interrupt each journal boundary and verify last-valid-slot or explicit AON-loss fallback

This result does not authorize placement/routing, purchasing, fabrication or final thermal/safety claims.

[Machine evidence](../hardware/verification/generated/H3-R2-thermal-fault.json).
