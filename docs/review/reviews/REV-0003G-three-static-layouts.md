# REV-0003G — review of three static full-layout maps
> **Историческая запись ревью.** `DEC-0027` архивировал её stage-3 architecture outputs; этот документ не является активным пререквизитом zero-based synthesis.


- Статус: **Проведено ревью подшага; layouts являются входами единого package (`DEC-0026`)**
- Дата: 2026-08-16
- Inputs: completed `DM-0001/BUD-0001`, `PIN-0001`, `SC-0001`, frozen wishlist
- Outputs: `LAY-S3-0001`, `LAY-C5-0001`, `LAY-BAL-0001`, `CMP-0001`, corrected `IMP-0021`

## Review checks

| Check | Result |
|---|---|
| Same demand | all three retain identical base/conditional functions and numerical boundaries |
| Exact MCU variants | each map names S3/C5 memory variant and unavailable pins |
| Full GPIO maps | no duplicate assignment found; straps/recovery restrictions are explicit |
| Controllers | no variant double-books the sole C5 GP-SPI; 4-bit SDIO is rejected where USB recovery is required |
| 3×nRF | one owner per layout; independent logical CS/CE/IRQ identification retained |
| IR/audio/external | C5 dual IR, S3 four-wire I²S, U214/GNSS/U216 profiles remain allocated |
| STOP/actual-TX | topology reserved in each map; implementation/HIL not falsely claimed |
| Memory/power | exact architecture classes fit; N8R2 and third-controller margins remain measured gates |
| Recovery | each processor has a path not relying on its own working application image |
| Cost | structural additions compared; no unquoted currency score invented |
| Controls | `FND-0031` fixes nine ordinary controls + separate STOP; matrix/U14 remains an orthogonal decision |

## Self-review finding

No candidate may receive a weighted `SC-0001` score yet: required scenario measurements, exact nRF module, RF coexistence and comparable BOM quotes do not exist. Assigning narrative points would violate the scorecard. Static review is nevertheless complete as an input to integrated synthesis because it establishes realizability, kill gates and fallback order without deleting demand.

## Conclusion

The substep receives **«Проведено ревью»**. `LAY-S3` is the first synthesis candidate due to the smallest structural BOM/reroute and absence of raw nRF IPC; `LAY-C5` and `LAY-BAL` remain explicit fallbacks. `DEC-0026` forbids promoting the nRF owner separately: only the complete converged stage-3 package may become a decision.
