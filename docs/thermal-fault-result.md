# Thermal, fault and extended-operation result

H3.6 is closed: three leaf packages contribute `70` passing checks and this consolidation adds `24` cross-domain checks. All `30` single-fault cases finish contained or with no admission; no analytical finding or policy decision remains open. The exact current marker is `H3.7.1`.

The engineering ambient target is `0 to 35 °C`, not a published guarantee. Only `SUPPORT_IDLE` with one active top-level signal group may proceed toward sustained-profile qualification; `SUPPORT_WORST`, continuous or unleased TX, unknown accessories and unreadable safety sensors are excluded. H6 must meet the final thermal and route-separation constraints, and H8 must measure the product.

Long operation uses a qualified USB-PD source and carries no uptime or battery-autonomy promise. The local full-self-test setting offers 24 hours, default 48 hours and warned startup-only proof; it cannot weaken watchdog, thermal, power-fault or TX-lease behavior. Proof expiry records `FAULT_PLANE_PROOF_DUE`, revokes leases and requires physical `KILL` to `RUN` recovery.

`16` remaining items are physical-only and assigned to H5, H6 or H8. This result does not authorize purchase, KiCad placement/routing or fabrication.

Machine evidence: [`H3-VRF64-thermal-fault-consolidation.json`](../hardware/verification/generated/H3-VRF64-thermal-fault-consolidation.json).
