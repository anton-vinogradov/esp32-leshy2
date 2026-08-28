# Thermal model · historical R1

`H3.6.1` is reviewed with `21` passing checks and one zero-cost safety correction. The exact marker is `H3.6.2`.

The model enumerates every H3.1 power state and separates electrical capacity from thermal permission. The electrical anti-hidden-load corner is `VOICE/RX/SUPPORT_WORST` at `13.802 W` of conservative base heat; it is **not** a continuous operating claim. The hottest `SUPPORT_IDLE` group is `VOICE` at `5.509 W`; quiet idle is `1.795 W`. External accessory output is excluded only after its converter/eFuse and base support heat have been retained.

The accepted engineering target is `0 to 35 C`, not a published product guarantee. Machine evidence also retains required base-to-ambient resistance at 25, 35 and 40 C against the existing 65-C warning and 75-C hard-kill classes. H6 must solve the actual copper/enclosure network and H8 must correlate temperatures and time constants before establishing the final range or admitting a sustained profile.

BQ25798 is corrected from hot reset defaults to protected/read-back `TREG=60 C`, `TSHUT=85 C`; this changes no BOM and removes no function.

Machine evidence: [`H3-VRF61-thermal-model.json`](../hardware/verification/generated/H3-VRF61-thermal-model.json).
