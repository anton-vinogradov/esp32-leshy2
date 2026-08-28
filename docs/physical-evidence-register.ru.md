# Реестр физических evidence

H3.7.2 закрыт. В сведениях шести фаз H3 было 88 residual-строк: три являлись внутренними зависимостями H3, уже закрытыми H3.2/H3.6, а все оставшиеся `85` опубликованы ниже. `9` назначены H5 received-part evidence, `10` — H6 final placement/routing evidence, `78` — H8 qualification собранного устройства. Ни одна не названа аналитически закрытой.

Каждая машинная строка содержит точный исходный artifact, ответственный gate, обязательный artifact и pass rule. Несоответствие повторно открывает исходный результат, а не превращается в waiver разводки или теста. Реестр не разрешает закупку, layout или печать. Точный текущий маркер — `H3.7.3`.

| ID | Этап | Источник | Требуемое физическое evidence |
|---|---|---|---|
| `H3-PHY-001` | `H6` | `H3.1` | H6 copper, placement and converter-loop thermal layout |
| `H3-PHY-002` | `H8` | `H3.1` | H8 measured converter efficiency, pack current, DPM charge derating and source handover |
| `H3-PHY-003` | `H8` | `H3.1` | H8 measured rail currents with display, selected microSD, speaker, every RF group and both exposed-port profiles |
| `H3-PHY-004` | `H8` | `H3.2` | apply named worst load steps while capturing buck/eFuse current and rail minimum |
| `H3-PHY-005` | `H8` | `H3.2` | fault-inject every clear source and measure TX-off/reset/rail-discharge ordering |
| `H3-PHY-006` | `H8` | `H3.2` | inject weak/current-limited USB sources with healthy, absent and rejected packs |
| `H3-PHY-007` | `H8` | `H3.2` | measure SYS and AON droop during USB attach/detach and DPM |
| `H3-PHY-008` | `H8` | `H3.2` | measure actual RC capacitance under DC bias and temperature |
| `H3-PHY-009` | `H8` | `H3.2` | measure charger/BATFET behavior at temperature and cell-voltage corners |
| `H3-PHY-010` | `H8` | `H3.2` | measure effective MLCC capacitance under DC bias and temperature |
| `H3-PHY-011` | `H8` | `H3.2` | measure every protected-rail ramp and discharge |
| `H3-PHY-012` | `H8` | `H3.2` | measure exact watchdog window and WDO pulse on populated hardware |
| `H3-PHY-013` | `H8` | `H3.2` | measure switch bounce and break-before-make interval |
| `H3-PHY-014` | `H8` | `H3.2` | power-cut fault-inject every flash-journal write boundary |
| `H3-PHY-015` | `H8` | `H3.2` | prove the signed fault-only UI cannot enable a transmitter or external rail |
| `H3-PHY-016` | `H8` | `H3.3` | measure protected-rail ripple and connector voltage at every accepted load and temperature corner |
| `H3-PHY-017` | `H5+H8` | `H3.3` | confirm HMX035CTFT-001 tail, ST77922 identity, VDD/VDDI ramp equality and reset/readback on received specimens |
| `H3-PHY-018` | `H8` | `H3.3` | measure QSPI edges, CS-high high-Z/contention and shared-microSD throughput before raising the 40-MHz initial cap |
| `H3-PHY-019` | `H8` | `H3.3` | measure actual panel backlight current, brightness, PWM EMI, temperature and TPS2553 latch recovery |
| `H3-PHY-020` | `H8` | `H3.3` | measure microphone/headset sensitivity, codec clipping/ALC/noise, channel phase perception, crosstalk, insertion pop and RF immunity on routed hardware |
| `H3-PHY-021` | `H8` | `H3.3` | measure PAM8302A current, output EMI, speaker temperature/excursion and enclosure response; enforce the 50 C speaker-local mute rule |
| `H3-PHY-022` | `H8` | `H3.3` | calibrate SA818S-V and SA818S-U deviation downward from the bounded full-scale codec injection and repeat across both module lots, rail and temperature |
| `H3-PHY-023` | `H8` | `H3.3` | prove reset/brownout/off ordering, >=10-ms amplifier-enable delay and absence of back-power with codec, voice and main domains independently off |
| `H3-PHY-024` | `H5+H8` | `H3.3` | verify received TSOP75238TR/TSMP95000TT identity, orientation, two-channel capture, 20-ms startup guard, 5-ms QOD quiet guard and no-back-power; confirm TSOP75238TR CPL rotation and feeder presentation against the JLCPCB placement preview |
| `H3-PHY-025` | `H8` | `H3.3` | replay a representative 30-to-60-kHz protocol corpus and measure carrier/count accuracy, robust AGC behavior, range and field of view |
| `H3-PHY-026` | `H8` | `H3.3` | measure VSMY14940 current, optical range/alignment, local temperature and IEC 62471 classification through the final enclosure/window |
| `H3-PHY-027` | `H8` | `H3.3` | calibrate the VEMD1060 tunnel against the <=2.271-uA paper target and inject missing emitter, ambient leakage, RX crosstalk, stuck carrier, brownout and FAULT_KILL |
| `H3-PHY-028` | `H5+H8` | `H3.3` | program one golden MAX17320 image, verify both address spaces/checksum/readback and fault-inject blank, corrupt and exhausted-write specimens |
| `H3-PHY-029` | `H8` | `H3.3` | calibrate the two divider channels on the assembled admission domain and inject open, short, swapped, reversed, missing and imbalanced cells |
| `H3-PHY-030` | `H8` | `H3.3` | thermally ramp every cell and board NTC, measure bond response time and prove open/short/lift detection plus the 35/40/60/65/75-C policy |
| `H3-PHY-031` | `H8` | `H3.3` | verify BQ CE-default-off, TS open/short, exact warm/cold suspend and all source/load/charge-current transitions with the exact cell lot |
| `H3-PHY-032` | `H8` | `H3.3` | measure long-idle divider imbalance, MAX balancing heat and both 49.9-ohm balance-resistor temperatures |
| `H3-PHY-033` | `H8` | `H3.4` | measure powered-off leakage at every switched-domain signal while the host remains powered |
| `H3-PHY-034` | `H8` | `H3.4` | capture reset and brownout pin states for S3, C5, RP2354B, both MSPM0 controllers and TCA6424A |
| `H3-PHY-035` | `H8` | `H3.4` | inject one and three simultaneous service USB hosts and verify no product rail is sourced |
| `H3-PHY-036` | `H8` | `H3.4` | exercise U214 and Unit wrong-accessory/external-source cases and measure reverse current |
| `H3-PHY-037` | `H8` | `H3.4` | measure VIH/VIL/VOH/VOL at the far end of M1 under simultaneous worst allowed branch load |
| `H3-PHY-038` | `H5+H8` | `H3.4` | qualify SD card identity/CMD6 high-speed mode, >=4.0-MB/s storage, 1.5-MB/s record, 250-ms stalls and 512-KiB buffering |
| `H3-PHY-039` | `H8` | `H3.4` | scope shared SPI2 edges, CS-high high-Z/contention and <=1-ms display/SD arbitration under insert/remove |
| `H3-PHY-040` | `H8` | `H3.4` | capture all three nRF24 IRQ-to-drain paths and every 3PRX/PTX role mix at 10-Mbit/s SPI |
| `H3-PHY-041` | `H8` | `H3.4` | capture CC1101 GDO/FIFO service at 600-kbit/s air rate and 10-Mbit/s SPI |
| `H3-PHY-042` | `H8` | `H3.4` | run full-duplex 48-kHz audio without DMA underrun/overrun during display, storage and radio-event stress |
| `H3-PHY-043` | `H8` | `H3.4` | prove S3-RP >=1.5 MB/s with <=250-us alert-to-read and S3-C5 >=1.5 MB/s with <=2-ms control RTT |
| `H3-PHY-044` | `H8` | `H3.4` | measure 400-kHz SYS_I2C transaction/recovery/IRQ latency with every assembled address and simultaneous UI activity |
| `H3-PHY-045` | `H8` | `H3.4` | measure M1 far-end rail drop, return offset, crosstalk and USB/SPI eye/edge quality after PCB placement |
| `H3-PHY-046` | `H5+H8` | `H3.4` | verify received stock U214 male-post material/plating, current continuity, insertion/withdrawal force and repeated-cycle retention; the 4.1-A figure proves only the controlled HLE/TSM pair |
| `H3-PHY-047` | `H8` | `H3.4` | measure U214 SPI load/edges at 10 MHz and external I2C total capacitance/rise time <=150 pF/300 ns |
| `H3-PHY-048` | `H5+H8` | `H3.4` | qualify each native Unit profile, cable length and pull network through TXS0102; 1-Wire remains specimen-only |
| `H3-PHY-049` | `H8` | `H3.4` | inject dual-branch request, overload, reverse source, wrong accessory, hot plug and brownout while proving independent latch-off |
| `H3-PHY-050` | `H8` | `H3.4` | measure C5/RP service USB edges/eye and powered-off leakage with one and three hosts |
| `H3-PHY-051` | `H8` | `H3.4` | measure product USB Full-Speed through M1 plus all DBG10 UART/SWD recovery paths in the assembled sandwich |
| `H3-PHY-052` | `H8` | `H3.5` | measure S3/C5 complete-feed insertion and return loss at every channel edge, including both microcoax transitions and the selected stackup launch |
| `H3-PHY-053` | `H5+H8` | `H3.5` | measure all three E01 module-to-SMA feeds and received-lot Gen1 mating/retention independently |
| `H3-PHY-054` | `H8` | `H3.5` | VNA-tune CC1101 differential-to-single-ended match and every 315/433/868/915 branch; prove output, sensitivity, harmonics and switch loss |
| `H3-PHY-055` | `H8` | `H3.5` | measure the independent SA818S-V and SA818S-U feed insertion/return loss, output power and harmonics at both power settings; repeat UHF for SA818S-CE before enabling that alternate |
| `H3-PHY-056` | `H8` | `H3.5` | qualify Si4732 FMI FM and SW sensitivity/overload with the complete external whip and first-pass 56-nH/1-nF network |
| `H3-PHY-057` | `H5+H6+H8` | `H3.5` | measure RX-AM/LW total capacitance <=19.500 pF external to the Si4732 input with the received SMA, PCB and exact pod |
| `H3-PHY-058` | `H8` | `H3.5` | derate every allowed TX power/EIRP table by measured complete-feed loss and selected antenna gain before regional profile release |
| `H3-PHY-059` | `H6+H8` | `H3.5` | use impedance coupons and de-embedded SMA/U.FL fixtures for H6/H8 acceptance; nominal field-solver values alone cannot close a feed |
| `H3-PHY-060` | `H6` | `H3.5` | release the fabricator stack-up, field-solve every launch and 50-ohm geometry, and correlate with coupons in H6 |
| `H3-PHY-061` | `H6` | `H3.5` | prove each routed path stays inside the accepted mechanical envelope and has no DRC, return-path or plane-slot violation |
| `H3-PHY-062` | `H5+H8` | `H3.5` | measure received 2118651-2 bend/retention/strain behavior and E01 connector axes before freezing the five microcoax paths |
| `H3-PHY-063` | `H6+H8` | `H3.5` | extract AM/LW connector, pad and high-Z trace capacitance and prove the complete external budget remains <=19.500 pF |
| `H3-PHY-064` | `H8` | `H3.5` | inspect every RF via fence, connector ground, ESD return and coupled-sampler branch on the fabricated board before H8 VNA/spectrum work |
| `H3-PHY-065` | `H8` | `H3.5` | run the signed-configuration L1 isolated baseline and L2 foreign-interface quiet/desense matrix for every signal group |
| `H3-PHY-066` | `H8` | `H3.5` | run FX-I6-N24-T1 with target plus independent observer for all eight radio-identity permutations at both support loads, all admitted channels/rates/powers and antenna poses |
| `H3-PHY-067` | `H8` | `H3.5` | prove inactive rails discharge, I/O remains high-Z, native S3/C5 radios emit no background packet/scan/advertising and service clocks have no periodic activity |
| `H3-PHY-068` | `H8` | `H3.5` | capture raw IRQ/FIFO/PIO/DMA/IPC/UI/storage/audio timing while each active group faces maximum valid support-plane aggression |
| `H3-PHY-069` | `H8` | `H3.5` | inject cross-group blocking, evidence false-positive, reset/brownout/stuck-line and KILL/FAULT_KILL faults only inside the contained Laboratory fixture |
| `H3-PHY-070` | `H6` | `H3.6` | H6: solve the real board/enclosure thermal network after placement, copper, vias, wall material, vents and accessory geometry are fixed |
| `H3-PHY-071` | `H6` | `H3.6` | H6: meet or beat the applicable allowable base-to-ambient resistance from the parameter sweep; SUPPORT_WORST remains non-continuous |
| `H3-PHY-072` | `H8` | `H3.6` | H8: measure all three NTCs, converter/eFuse/charger junction proxies, both cells and external surfaces at every admitted sustained profile |
| `H3-PHY-073` | `H8` | `H3.6` | H8: correlate thermal time constants and set per-profile maximum session/duty limits before any unattended claim |
| `H3-PHY-074` | `H8` | `H3.6` | H8: verify cell-to-NTC contact, replacement spread, charger TREG/TSHUT, warning, FAULT_KILL and physical rearm in a chamber |
| `H3-PHY-075` | `H6` | `H3.6` | H6: physically separate RUN_PERMIT and FAULT_ASSERT_N routing, their local buffers and endpoint gate returns; verify no single via/pad short joins both paths |
| `H3-PHY-076` | `H8` | `H3.6` | H8: inject every SF-01..SF-30 case at accessible pads and verify rail fall, no RF/optical output, retained reason and physical-only re-arm |
| `H3-PHY-077` | `H8` | `H3.6` | H8: calibrate evidence thresholds and prove stuck-active, stuck-inactive and unreadable evidence behavior for all nine channels |
| `H3-PHY-078` | `H8` | `H3.6` | H8: measure watchdog, reset, eFuse, QOD and transmitter-energy deadlines; analytical 0/100/1760-ms classes are upper-level contracts, not measured closure |
| `H3-PHY-079` | `H8` | `H3.6` | H8: interrupt every two-slot flash-journal write boundary and verify last-valid-slot or explicit AON-loss fallback |
| `H3-PHY-080` | `H6` | `H3.6` | H6: meet the profile-specific 35-C base-to-ambient resistance target with final copper, vias, enclosure and installed accessory geometry |
| `H3-PHY-081` | `H8` | `H3.6` | H8: run 24-hour and 48-hour USB-powered endurance cases as validation tests, including the configured proof-due stop and retained display reason |
| `H3-PHY-082` | `H8` | `H3.6` | H8: run each battery profile to its real protected cutoff and publish measurements only as test results, not guaranteed autonomy |
| `H3-PHY-083` | `H8` | `H3.6` | H8: chamber-test admitted sustained profiles at 0, 25 and 35 C plus boundary/fault behavior outside the design target |
| `H3-PHY-084` | `H8` | `H3.6` | H8: verify all three self-test settings, staged activation, local-only authority, warning sequence, S3-loss behavior and physical KILL-to-RUN recovery |
| `H3-PHY-085` | `H8` | `H3.6` | H8: correlate final thermal time constants and set per-profile TX duty/session limits before release |

Машинное evidence: [`H3-VRF72-physical-residuals.json`](../hardware/verification/generated/H3-VRF72-physical-residuals.json).
