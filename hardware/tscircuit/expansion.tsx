// Leshy2 — Sheet 5: Expansion + GPS  (LEGACY implementation draft; NOT FAB-READY)
//
// METHOD: every real IC/module/connector uses footprint="jlcpcb:C<number>". The parts engine
// supplies the REAL pads AND the REAL pad NAMES from the LCSC/EasyEDA database, so no pin numbers
// are typed by hand for those. Traces reference the engine pad names (verified via
// `tsci export -f readable-netlist`, WITHOUT --disable-parts-engine).
// Placeholder (external RFID2 unit U44) keeps explicit pinLabels — same convention as BT1 (Sheet 1)
// / nRF24 (Sheet 3) / J30 (Sheet 4). Passives (R40/R41 pull-ups, GPS decoupling caps) stay
// primitive resistor/capacitor footprints.
//
// Pad-name sources of truth (engine probe of each footprint):
//   U40  u-blox SAM-M8Q-0 GNSS (own patch antenna)  -> jlcpcb:C5447387  (alt C2894838, same pads)
//        Engine pads (20-pin LCC): 1 GND1, 2 VCC_IO, 3 V_BCKP, 4 GND2, 5 GND3, 6 GND4,
//        7 TIMEPULSE, 8 SAFEBOOT_N, 9 SDA, 10 GND5, 11 GND6, 12 SCL, 13 TxD, 14 RxD,
//        15 GND7, 16 GND8, 17 VCC, 18 RESET_N, 19 EXTINT0, 20 GND9.  (u-blox SAM-M8Q datasheet.)
//        DESIGN NOTES (realized against the real module):
//        - VCC_IO(pin2) is a SEPARATE I/O supply pad the base soic8 model did not have; the
//          datasheet requires it powered -> tied to V3V3 (single-supply 3.3 V design).
//        - Antenna is integrated (patch + SAW + LNA on-module) -> no external RF pad, as expected.
//        - GPS is UART-only by design (keeps NMEA off the shared I2C bus). Per the datasheet the
//          DDC pins may be left open when unused -> SDA(pin9)/SCL(pin12) left NOT_CONNECTED (NOT
//          wired to the I2C bus on purpose).
//        - SAFEBOOT_N, RESET_N, EXTINT0, TIMEPULSE have internal pull-ups / are optional -> left
//          open (RESET_N and SAFEBOOT_N must NOT be grounded in normal operation).
//        - Added vs base (datasheet-typical): 100nF+10uF at VCC, 100nF at VCC_IO (base had none).
//   J40/J41  Grove HY2.0-4P (I2C) SMD w/ locating pins, CAX HY2.0-4P-WT  -> jlcpcb:C722729
//        Engine pads are UNNAMED -> referenced by .pin#. Footprint geometry (probed from kicad_pcb):
//        pads 1..4 = the four 2.0 mm signal contacts in a row (x = -3/-1/+1/+3 mm); pads 5,6 =
//        the two large locating/anchor pads (mechanical). M5Stack Grove PORT.A physical order is
//        pin1 GND, pin2 5V, pin3 SDA, pin4 SCL -> here pin2 (the "5V" position) carries +3V3
//        (3.3 V ports by default; the S3 is not 5 V-tolerant). See ⚠ on pad-1 orientation below.
//   D40/D41  PESD5V0S2UAT double ESD diode, common cathode, SOT-23  -> jlcpcb:C552572
//        Engine pads: 1 A1, 2 A2, 3 C. Unidirectional COMMON-CATHODE array: A1/A2 = the two
//        protected lines (anodes), C = shared cathode. For a positive 0..3.3 V rail-referenced
//        signal the common cathode MUST go to the supply (+3V3), NOT to GND — with C on GND every
//        I2C logic-high forward-biases the diode and clamps the line to ~0.6 V (whole bus dead).
//        So: A1 -> I2C_SDA, A2 -> I2C_SCL, C -> +3V3 (clamps overshoot above the rail).
//   D42  BAT54 single Schottky, SOT-23  -> jlcpcb:C466635
//        Engine pads: 1 A, 2 NC, 3 K.  Backup diode: A -> +3V3, K -> V_BCKP (charges the supercap,
//        blocks back-feed when +3V3 collapses). pin2 NC left open.
//   BT40 Supercap 0.22 F 5.5 V SMD (Ohmite LM055224A)  -> jlcpcb:C3019760
//        Engine pads unnamed (pin1/pin2, 2-terminal). pin1 -> V_BCKP, pin2 -> GND. ⚠ verify + pad.
//
// Placeholder (footprint geometric, NOT engine):
//   U44  RFID2 Unit (WS1850S) — EXTERNAL M5/Grove plug-in unit @0x28, NOT a board component.
//        Legacy topology placeholder only (soic8 + pinLabels V/GND/SDA/SCL).
//        ⚠ FND-0015: official Unit power is 5 V, while J40/J41 currently provide 3.3 V.
//        This placeholder is NOT electrically compatible and must not be built/claimed until the
//        stage-3/6 PORT.A-NFC power/profile redesign is reviewed.
//
// Net names are UNCHANGED from the base sheet (V3V3, GND, I2C_SDA/SCL, GPS_UART_RX/TX, V_BCKP).
// GPS UART orientation preserved: GPS_UART_RX = U40.TxD (S3 listens), GPS_UART_TX = U40.RxD.
export default () => (
  <board width="80mm" height="60mm">
    {/* ===================== u-blox SAM-M8Q GPS (onboard, UART, own patch antenna) ===================== */}
    <chip name="U40" footprint="jlcpcb:C5447387" />
    {/* GPS supply decoupling (datasheet-typical; base soic8 model had none) */}
    <capacitor name="Cvcc40" capacitance="100nF" footprint="0402" /> {/* VCC HF decap */}
    <capacitor name="Cbulk40" capacitance="10uF" footprint="0805" /> {/* VCC bulk */}
    <capacitor name="Cio40" capacitance="100nF" footprint="0402" />  {/* VCC_IO decap */}
    {/* GPS backup: supercap + Schottky on V_BCKP for hot-start */}
    <chip name="D42" footprint="jlcpcb:C466635" />   {/* BAT54: +3V3 -> V_BCKP */}
    <chip name="BT40" footprint="jlcpcb:C3019760" /> {/* 0.22F supercap on V_BCKP */}

    {/* ===================== I2C bus pull-ups (single pair for the whole bus) ===================== */}
    <resistor name="R40" resistance="4.7k" footprint="0402" /> {/* SDA pull-up -> +3V3 */}
    <resistor name="R41" resistance="4.7k" footprint="0402" /> {/* SCL pull-up -> +3V3 */}

    {/* ===================== Grove HY2.0-4P I2C ports x2 + per-port ESD ===================== */}
    <chip name="J40" footprint="jlcpcb:C722729" />
    <chip name="J41" footprint="jlcpcb:C722729" />
    <chip name="D40" footprint="jlcpcb:C552572" />
    <chip name="D41" footprint="jlcpcb:C552572" />

    {/* ===================== RFID2 Unit (WS1850S) — EXTERNAL Grove unit @0x28 (placeholder) ===================== */}
    <chip name="U44" footprint="soic8" pinLabels={{ pin1: "V", pin2: "GND", pin3: "SDA", pin4: "SCL" }} />

    {/* ============================== NETS ============================== */}
    {/* --- GPS supply + UART + backup --- */}
    <trace from=".U40 > .VCC" to="net.V3V3" />
    <trace from=".U40 > .VCC_IO" to="net.V3V3" />       {/* added: I/O rail required by datasheet */}
    <trace from=".Cvcc40 > .pin1" to="net.V3V3" />
    <trace from=".Cvcc40 > .pin2" to="net.GND" />
    <trace from=".Cbulk40 > .pin1" to="net.V3V3" />
    <trace from=".Cbulk40 > .pin2" to="net.GND" />
    <trace from=".Cio40 > .pin1" to="net.V3V3" />
    <trace from=".Cio40 > .pin2" to="net.GND" />
    <trace from=".U40 > .GND1" to="net.GND" />
    <trace from=".U40 > .GND2" to="net.GND" />
    <trace from=".U40 > .GND3" to="net.GND" />
    <trace from=".U40 > .GND4" to="net.GND" />
    <trace from=".U40 > .GND5" to="net.GND" />
    <trace from=".U40 > .GND6" to="net.GND" />
    <trace from=".U40 > .GND7" to="net.GND" />
    <trace from=".U40 > .GND8" to="net.GND" />
    <trace from=".U40 > .GND9" to="net.GND" />
    <trace from=".U40 > .TxD" to="net.GPS_UART_RX" /> {/* S3 GPIO18 <- U40.TxD (NMEA) */}
    <trace from=".U40 > .RxD" to="net.GPS_UART_TX" /> {/* S3 GPIO47 -> U40.RxD (config) */}
    {/* SDA/SCL (DDC) intentionally open (UART-only design); TIMEPULSE/EXTINT0/SAFEBOOT_N/RESET_N open */}
    {/* V_BCKP: +3V3 through Schottky, held by supercap */}
    <trace from=".D42 > .A" to="net.V3V3" />
    <trace from=".D42 > .K" to="net.V_BCKP" />
    <trace from=".U40 > .V_BCKP" to="net.V_BCKP" />
    <trace from=".BT40 > .pin1" to="net.V_BCKP" />
    <trace from=".BT40 > .pin2" to="net.GND" />

    {/* --- I2C bus pull-ups to +3V3 --- */}
    <trace from=".R40 > .pin1" to="net.V3V3" />
    <trace from=".R40 > .pin2" to="net.I2C_SDA" />
    <trace from=".R41 > .pin1" to="net.V3V3" />
    <trace from=".R41 > .pin2" to="net.I2C_SCL" />

    {/* --- Grove port J40 (pin1 GND, pin2 +3V3, pin3 SDA, pin4 SCL; pin5/6 mechanical -> GND) --- */}
    <trace from=".J40 > .pin1" to="net.GND" />
    <trace from=".J40 > .pin2" to="net.V3V3" />
    <trace from=".J40 > .pin3" to="net.I2C_SDA" />
    <trace from=".J40 > .pin4" to="net.I2C_SCL" />
    <trace from=".J40 > .pin5" to="net.GND" />
    <trace from=".J40 > .pin6" to="net.GND" />
    <trace from=".D40 > .A1" to="net.I2C_SDA" />
    <trace from=".D40 > .A2" to="net.I2C_SCL" />
    <trace from=".D40 > .C" to="net.V3V3" />

    {/* --- Grove port J41 --- */}
    <trace from=".J41 > .pin1" to="net.GND" />
    <trace from=".J41 > .pin2" to="net.V3V3" />
    <trace from=".J41 > .pin3" to="net.I2C_SDA" />
    <trace from=".J41 > .pin4" to="net.I2C_SCL" />
    <trace from=".J41 > .pin5" to="net.GND" />
    <trace from=".J41 > .pin6" to="net.GND" />
    <trace from=".D41 > .A1" to="net.I2C_SDA" />
    <trace from=".D41 > .A2" to="net.I2C_SCL" />
    <trace from=".D41 > .C" to="net.V3V3" />

    {/* --- RFID2 legacy topology placeholder; NOT electrically compatible until FND-0015 closes --- */}
    <trace from=".U44 > .V" to="net.V3V3" />
    <trace from=".U44 > .GND" to="net.GND" />
    <trace from=".U44 > .SDA" to="net.I2C_SDA" />
    <trace from=".U44 > .SCL" to="net.I2C_SCL" />
  </board>
)
