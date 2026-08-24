# Leshy2 consolidated ERC and NC review

[Русский](erc-review.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md) · [All NCs](no-connects.md)

H2.6 is closed on the complete four-project KiCad hierarchy, not isolated sheets.

| Check | Result |
|---|---|
| Native ERC | 4 projects · 0 errors · 0 warnings |
| Intentional NCs | 189 physical contacts · each has a pin, marker and rationale |
| Local symbols | 1100 comparisons moved from the noisy KiCad rule into an exact shared-library check |
| ERC exclusions | only `lib_symbol_mismatch`; no other ignored rules |

✅ **Reviewed:** no unexplained ERC/NC finding remains. H2.6 is complete; the current step is H2.7, end-to-end contact/net reconciliation against H1, the pin ledger, M1 and firmware F2.

[Machine evidence](../hardware/ecad/generated/H2-REV64-erc-consolidated.json).
