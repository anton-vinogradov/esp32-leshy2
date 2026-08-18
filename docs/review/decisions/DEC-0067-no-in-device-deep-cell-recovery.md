# DEC-0067 — no in-device deep-cell recovery

- Статус: **Принято владельцем; распространено**
- Дата: 2026-08-18
- Owner choice: [`IMP-0056/A`](../improvements/IMP-0056-deep-cell-recovery-boundary.md)
- Circuit review: [`PWR-0007`](../architecture/PWR-0007-max17320-2s-surrounding-circuit.md)
- Propagation review: [`REV-0005X`](../reviews/REV-0005X-deep-cell-policy-propagation.md)

## Decision

1. The base product does not recover deeply discharged loose cells. A cell
   below the qualified admission floor is refused; `3.0 V` relaxed/no-load per
   cell remains only the conservative paper starting point until the exact
   approved-cell profile and error budget freeze the production threshold.
2. `MAX17320` zero-volt charging is physically unused (`ZVC` open) and linear
   prequalification is disabled in the protected NVM image. Neither S3 nor a
   product menu can override this boundary.
3. Any characterization or attempted recovery is external to the handheld and
   belongs only to a separately powered, isolated Controlled-Zone fixture with
   the already accepted authorization, recurring warning and containment
   rules.
4. The exact fully-switching protection pair is one active-production
   `CSD87313DMST`: dual 30-V N-channel, common drain, 17-A package limit and
   5.5-mOhm maximum source-to-source resistance at 4.5-V gate drive. FET1
   source is the cell-stack/`IN` side and FET2 source is the protected
   pack/`PCKP` side, matching the `MAX17320` gate references.
5. Two `0451005.MRL` fuses, one per physical cell slot,
   `WSL25125L000FEA` 5-mOhm shunt and two `B57332V5103F360` NTCs are accepted
   as exact first targets.
6. The reset-default hold and admission supply use exact packages
   `2N7002DW-7-F`, `BAV70LT1G` and `BAT54-7-F`. Exact resistor/capacitor values
   and source-handover current remain schematic/HIL outputs.
7. The original PA24/PA25 evidence assignment is superseded by
   `DEC-0074/FND-0078`: `PA25/A2` measures the protected 2S midpoint and
   `PA26/A1` the protected full stack. The admission-controller budget remains
   `12 used / 3 permanent service / 3 free`.

## Lifecycle correction made during acceptance

The earlier paper candidate `FDMC8030` is rejected because onsemi now marks it
`Last Shipments`. A first replacement search found a common-source part, but
the exact `MAX17320` gate references prove that the required integrated pair is
common-drain. `CSD87313DMST` is both electrically correct and listed by TI as
active production; authorized-channel stock was visible when selected.

This correction is intentionally recorded before schematic work so neither a
stale MPN nor a topologically wrong package can leak into the BOM.

## Remaining gates

- reproduce the ADI 2S sense/balance network and freeze every passive value;
- qualify the accepted exact bounded diagnostic pulse, ADC thresholds and
  cooldown from `PWR-0013/DEC-0074` in HIL;
- prove holder polarity/reverse-insertion behavior and repeatable NTC coupling;
- calculate hot losses and validate source handover, removal/bounce, short and
  fault behavior in HIL;
- close the accepted `DEC-0068/PWR-0008` rail tree with exact passive values,
  loss/thermal calculations and HIL.

This is a reviewed working-design decision, not authorization to begin KiCad.
