# DEC-0092 — exact S3/C5 native RF endpoints

- Status: **accepted under delegated non-dramatic cost/no function-loss rule; Проведено ревью subblock**
- Finding: [`FND-0097`](../findings/FND-0097-native-rf-evidence-stopped-before-the-real-feed.md)
- Architecture: [`NAT-0001`](../architecture/NAT-0001-exact-s3-c5-native-rf-evidence-endpoints.md)
- Propagation: [`REV-0005AW`](../reviews/REV-0005AW-i6-native-rf-propagation.md)

## Decision

1. Keep independent external RF paths for exact modules
   `ESP32-S3-WROOM-1U-N16R2` and `ESP32-C5-WROOM-1U-N8R8`.
2. Use one `Hirose U.FL-R-SMT-1(10)` PCB receptacle and one
   `KYOCERA AVX CP0603Q5425ENTR` directional coupler per path. Components may
   share MPNs; RF paths may not share bodies.
3. Orient coupler `IN` toward the module and `OUT` toward the dedicated RP-SMA.
   Terminate its named `50 OHM` land with exact `RC0402FR-0749R9L`.
4. Complete each `LTC5532ES6#TRMPBF` with exact 39-pF input DC block, matched
   10-kOhm gain-two network, grounded VOS, 33-pF output load and 100-nF bypass.
5. Keep C5 `ANT2` default-disabled/no-connect. It is an exposed RF pad, not a
   free second baseline antenna.
6. Select the exact double-ended U.FL cable length and final RP-SMA MPN only
   after physical placement, then qualify the complete feed. No guessed jumper
   part number enters the target BOM.
7. Mark only the S3/C5 native RF paper subblock reviewed. I6 remains active for
   CC1101, SA518, Si4732 and IR frontends plus consolidated coexistence.

## Consequences

- No GPIO, bus or radio function changes.
- S3 and C5 actual-TX evidence is now sourced after a real exposed module
  contact through a directional sample rather than an abstract tap.
- The shared coupler SKU covers all stated 2.4/5-GHz native bands and avoids a
  separate 5-GHz detector branch.
- Paper cost increases by roughly USD 2.98 at quantity 100 before jumper and
  ordinary passives; no new detector SKU is added.
- No KiCad authorization, atomic freeze or integrated-mockup restart follows.

