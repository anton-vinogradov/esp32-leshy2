# Реестр физических evidence · H3-R2

[English](physical-evidence-register-r2.md) · [Отчёт H3](h3-r2-acceptance.ru.md) · [Роадмап](roadmap.ru.md)

После H3 остаётся `51` physical-only строк evidence: `1` затрагивают проверку полученных деталей H5, `5` — evidence разведённой платы H6, `46` — измерения единственного собранного прототипа H8. У строки может быть несколько владельцев, когда identity полученной детали и поведение в сборке являются разными gates.

Ни один пункт ниже не назван пройденным. Реестр не требует расходуемого собранного устройства, drop-test, vibration campaign или произвольного числа циклов разъёмов. Безопасные электрические faults задаются current-limited fixture или emulator; реальные банки и единственный MAX17320 остаются внутри заявленных пределов.

| ID | Владелец | Источник | Остающееся физическое evidence |
|---|---|---|---|
| `H3-R2-PHY-001` | `H8` | `H3-R2.1` | H6 must realize converter/eFuse copper and vias at least as good as the modeled published EVM/package boundary |
| `H3-R2-PHY-002` | `H8` | `H3-R2.1` | H8 must measure rail endpoints, current and temperature for each named sustained profile and reject any profile outside the generated envelope |
| `H3-R2-PHY-003` | `H8` | `H3-R2.1` | H8 may raise the 1.00-A sustained external admission only after measured 35-C margin remains at least 20 C |
| `H3-R2-PHY-004` | `H8` | `H3-R2.1` | H6 routed source/pack resistance extraction |
| `H3-R2-PHY-005` | `H8` | `H3-R2.1` | H8 measured efficiency, current and pack temperature |
| `H3-R2-PHY-006` | `H8` | `H3-R2.2` | H8 measures real switch bounce and break-before-make interval. |
| `H3-R2-PHY-007` | `H8` | `H3-R2.2` | H8 measures the populated 100-kohm/2.2-uF RC under DC bias and temperature; startup safety does not depend solely on this number. |
| `H3-R2-PHY-008` | `H8` | `H3-R2.2` | H8 captures POR assertion/release, direct C5/RF-RP reset and S3 fault-display retention at real rail corners. |
| `H3-R2-PHY-009` | `H8` | `H3-R2.2` | measure SYS, AON and downstream-rail minima during every USB attach/detach and DPM transition |
| `H3-R2-PHY-010` | `H8` | `H3-R2.2` | measure actual BATFET handover and supplement waveforms at low, nominal and full pack voltage |
| `H3-R2-PHY-011` | `H8` | `H3-R2.2` | inject weak and current-limited USB sources with healthy, absent and isolated packs |
| `H3-R2-PHY-012` | `H8` | `H3-R2.2` | repeat the worst transitions at the declared temperature corners |
| `H3-R2-PHY-013` | `H8` | `H3-R2.2` | H8 measures every protected-rail rise, minimum voltage and settling waveform at the generated worst load step |
| `H3-R2-PHY-014` | `H8` | `H3-R2.2` | H8 measures the real U214 and selected M5 Unit input capacitance/inrush before that accessory is admitted |
| `H3-R2-PHY-015` | `H8` | `H3-R2.2` | H8 injects missing and stuck watchdog service, captures WDO/FAULT_ASSERT_N/FAULT_KILL and proves that source recovery cannot restart the product |
| `H3-R2-PHY-016` | `H8` | `H3-R2.2` | H8 interrupts every fault-journal write boundary and verifies valid-slot or explicit generic-fallback selection |
| `H3-R2-PHY-017` | `H8` | `H3-R2.2` | H8 proves the fault-only UI cannot enable C5, either RP2354B, RF/IR, voice PTT or either external 5-V branch |
| `H3-R2-PHY-018` | `H8` | `H3-R2.3` | H6 preserves the 1206 series-resistor land as a controlled brightness trim point and routes the LED loop compactly |
| `H3-R2-PHY-019` | `H8` | `H3-R2.3` | H8 measures panel current, luminance, PWM noise and visible boot at the received panel Vf; the manufacturer publishes no minimum Vf, so paper analysis cannot prove minimum luminance at the simultaneous low-rail/high-Vf endpoint |
| `H3-R2-PHY-020` | `H8` | `H3-R2.3` | measure microphone/headset sensitivity, codec clipping/ALC/noise, channel phase perception, crosstalk, insertion pop and RF immunity on routed hardware |
| `H3-R2-PHY-021` | `H8` | `H3-R2.3` | measure PAM8302A current, output EMI, speaker temperature/excursion and enclosure response; enforce the 50 C speaker-local mute rule |
| `H3-R2-PHY-022` | `H8` | `H3-R2.3` | calibrate SA818S-V and SA818S-U deviation downward from the bounded full-scale codec injection and repeat across both module lots, rail and temperature |
| `H3-R2-PHY-023` | `H8` | `H3-R2.3` | prove reset/brownout/off ordering, >=10-ms amplifier-enable delay and absence of back-power with codec, voice and main domains independently off |
| `H3-R2-PHY-024` | `H5+H8` | `H3-R2.3` | verify received TSOP75238TR/TSMP95000TT identity, orientation, two-channel capture, 20-ms startup guard, 5-ms QOD quiet guard and no-back-power; confirm TSOP75238TR CPL rotation and feeder presentation against the JLCPCB placement preview |
| `H3-R2-PHY-025` | `H8` | `H3-R2.3` | replay a representative 30-to-60-kHz protocol corpus and measure carrier/count accuracy, robust AGC behavior, range and field of view |
| `H3-R2-PHY-026` | `H8` | `H3-R2.3` | measure VSMY14940 current, optical range/alignment, local temperature and IEC 62471 classification through the final enclosure/window |
| `H3-R2-PHY-027` | `H8` | `H3-R2.3` | calibrate the VEMD1060 tunnel against the <=2.271-uA paper target and inject missing emitter, ambient leakage, RX crosstalk, stuck carrier, brownout and FAULT_KILL |
| `H3-R2-PHY-028` | `H8` | `H3-R2.3` | on one received MAX17320, record blank fail-closed behavior, program a deliberately invalid but electrically safe configuration, then program the reviewed golden image and prove recovery; read both address spaces, checksum, NVError and remaining-update bitmap at each transition; inject zero-remaining and failed-copy only in the emulator or isolated fixture, never consume all seven physical updates and use no sacrificial chip |
| `H3-R2-PHY-029` | `H8` | `H3-R2.3` | calibrate the two divider channels on the assembled admission domain; inject open, short, swapped, reversed, missing and imbalanced-cell states only with a current-limited cell simulator |
| `H3-R2-PHY-030` | `H8` | `H3-R2.3` | use an NTC fixture to inject open/short/lift and the 35/40/60/65/75-C thresholds, measure sensor bonding/response within component limits, and never heat real cells beyond the exact cell MPN temperature envelope |
| `H3-R2-PHY-031` | `H8` | `H3-R2.3` | verify BQ CE-default-off, TS open/short with the NTC fixture, exact warm/cold suspend and all admitted source/load/charge-current transitions with the exact cell lot inside its MPN limits |
| `H3-R2-PHY-032` | `H8` | `H3-R2.3` | measure long-idle divider imbalance, MAX balancing heat and both 49.9-ohm balance-resistor temperatures |
| `H3-R2-PHY-033` | `H6` | `H3-R2.3` | H6 uses the reserved compact tuning island and fitted/DNP trim footprints, extracts routed pads, traces, vias, coupling, shield and enclosure parasitics, and reruns the same mask before the exact-one order. |
| `H3-R2-PHY-034` | `H8` | `H3-R2.3` | H8 VNA measurement confirms or retunes the fitted/DNP state on the assembled prototype. |
| `H3-R2-PHY-035` | `H8` | `H3-R2.3` | H8 records Si5351 startup and output-frequency calibration; the exact crystal start limits pass, while long-term aging is calibrated rather than guessed from an unpublished exact-code aging row |
| `H3-R2-PHY-036` | `H6` | `H3-R2.4` | route i8080, S3-Hub, Hub-C5 SDIO, Hub-RF SPI and USB as length/return/impedance constrained groups; prove extracted delay/skew and UI-I2C capacitance <=120 pF |
| `H3-R2-PHY-037` | `H8` | `H3-R2.4` | measure i8080 WR/data edges at the panel, USB eyes/ enumeration, SDIO/SPI far-end setup-hold and sustained qualified payload floors |
| `H3-R2-PHY-038` | `H8` | `H3-R2.5` | H5/J4-F: inspect exact received cable/receptacle mating, gentle service loop, bend radius, retention and strain routing for all five paths |
| `H3-R2-PHY-039` | `H6` | `H3-R2.5` | H6: field-solve and coupon-correlate every ordinary 50-ohm mainline, launch, reference plane, return path and via fence; extract RX-AM/LW capacitance separately |
| `H3-R2-PHY-040` | `H8` | `H3-R2.5` | H8: VNA-test insertion loss and return loss for all ten complete assembled feeds at every admitted band edge |
| `H3-R2-PHY-041` | `H8` | `H3-R2.5` | H8: calibrate every actual-TX detector and prove no false negative at minimum qualified output; inbound false positives may only delay |
| `H3-R2-PHY-042` | `H8` | `H3-R2.5` | H8: run the isolated baseline, foreign-group quiet matrix, maximum support-load aggression and ordered transition/fault suite |
| `H3-R2-PHY-043` | `H8` | `H3-R2.5` | H8: run all four 3xnRF role mixes and eight identity permutations with an independent observer; paper review does not claim same-channel isolation |
| `H3-R2-PHY-044` | `H8` | `H3-R2.5` | H8: measure final antenna gain/feed loss and bind regional power, duty, emission, exposure and thermal profiles |
| `H3-R2-PHY-045` | `H6` | `H3-R2.6` | H6: solve the routed copper, vias, component spreading and enclosure thermal network; meet every admitted profile's 35-C resistance ceiling |
| `H3-R2-PHY-046` | `H6` | `H3-R2.6` | H6: keep RUN_PERMIT and FAULT_ASSERT_N routes, pads, returns and endpoint buffers physically independent |
| `H3-R2-PHY-047` | `H8` | `H3-R2.6` | H8: map POWER, RF/VOICE, UI/display, both cells, charger and external surfaces at each admitted sustained profile |
| `H3-R2-PHY-048` | `H8` | `H3-R2.6` | H8: inject SF-R2-01 through SF-R2-30 with current-limited fixtures/emulators and verify safe output, retained cause and physical-only re-arm |
| `H3-R2-PHY-049` | `H8` | `H3-R2.6` | H8: calibrate all thermal/evidence thresholds and measure watchdog, eFuse, reset, QOD and residual-energy timing |
| `H3-R2-PHY-050` | `H8` | `H3-R2.6` | H8: run ordinary non-destructive 24/48-hour qualified-USB soak plus battery-to-protected-cutoff measurement without converting it into an uptime promise |
| `H3-R2-PHY-051` | `H8` | `H3-R2.6` | H8: interrupt each journal boundary and verify last-valid-slot or explicit AON-loss fallback |

Одно отдельное firmware-обязательство намеренно не названо физическим evidence: F5/F6 должны создать и проверить точную зафиксированную конфигурацию i8080. H4-R2 объединит его с проведённой аппаратной границей.

[Машинный реестр](../hardware/verification/generated/H3-R2-physical-residuals.json).
