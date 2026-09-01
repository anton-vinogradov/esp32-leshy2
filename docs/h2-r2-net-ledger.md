# H2-R2 native net reconciliation

[Русский](h2-r2-net-ledger.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)

**The `H2-R2.1.3` net checkpoint passed on 30 August 2026.** Every logical
contact of every fitted R2 instance now has one reviewed physical disposition:
one native net or an explicit board no-connect. This checkpoint reconciles the
input for native schematics; it does not authorize placement, routing,
fabrication or ordering.

## Result

| Item | Checked result |
|---|---:|
| Current fitted-instance contacts | 4,239 |
| Contacts assigned to native nets | 4,002 |
| Explicit board no-connects | 237 |
| Unresolved or hidden external contacts | 0 |
| Canonical native nets | 816 |
| Net-name aliases collapsed at a common physical node | 46 |
| Reconciliation errors | 0 |

The current H0/H1 sources own both RP GPIO maps, the S3 map, C5 SDIO/service
mux, all 80 M1 contacts on both boards, the direct 50-contact display ZIF and the powered-off
Pack/Safety boundary. Both package-visible stacked-flash buses are explicit
board no-connects. Functional names that meet on one physical pin are collapsed
to one canonical copper net; for example `AON_EFUSE_EN` is the same node as
`AON_RAW_3V3`, not a second trace.

Migration of unchanged support circuits used 3,162 same-endpoint route hints
from the retained G2F R1 contract, plus 4 identical-device/same-pin hints from
the retained R1 KiCad files. Another 143 historical rows only preserve explicit
NC, reserved/free or non-product-controller allocation intent. Every such
source remains explicitly non-authoritative: it is accepted only after the
current instance, exact device and contact match, and cannot supply R2
ownership, S3/dual-RP GPIO, M1, C5 SDIO, display or Pack/Safety topology. The
generated checked ledger is the new R2 schematic input.

## Machine evidence

- [Net reconciliation contract](../hardware/ecad/h2-r2-net-ledger-contract.json)
- [Generated 4,239-endpoint ledger](../hardware/ecad/generated/H2-R2-native-net-ledger.json)
- [Generator](../hardware/ecad/h2_r2_net_ledger.py)
- [Machine tests](../hardware/architecture/tests/test_h2_r2_net_ledger.py)

The two [native KiCad projects](h2-r2-native-kicad.md) now materialize this
ledger and pass zero-finding ERC. Cross-sheet and HW↔FW reconciliation also
passed in [H2-R2.1.5](h2-acceptance.md). H3 now freezes those inputs;
placement, routing, fabrication and ordering remain blocked.
