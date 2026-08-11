// Leshy2 — Sheet 6: Indicators & I/O  (FAB-READY draft, engine-pulled footprints by LCSC number)
//
// METHOD: every real IC/connector/switch uses footprint="jlcpcb:C<number>". The parts engine
// supplies the REAL pads AND the REAL pad NAMES from the LCSC/EasyEDA database, so no pin numbers
// are typed by hand for those. Traces reference the engine pad names (verified via
// `tsci export -f readable-netlist`, WITHOUT --disable-parts-engine).
// Kept geometric (no LCSC), same convention as power.tsx / audio.tsx:
//   - LEDs D50..D57 stay <led footprint="0603"> (pin1 anode / pin2 cathode). Amber colour + Vf
//     are a BOM detail; the land is a plain 0603 two-pad — pick the real amber part at BOM time.
//   - Passives Rd50..56 / Rir / Ren / Cen / Cir / Csd1 / Csd2 stay value+typesize.
//   - LS2 (active buzzer) and SW11/12/13 (RESET/BOOT/PTT buttons) stay 2-pin resistor proxies —
//     no clean LCSC land maps 1:1 to their footprint; swap for the real parts before fab.
//
// Pad-name sources of truth (engine probe of each footprint):
//   Q50..Q58  MMBT3904 NPN  SOT-23  -> jlcpcb:C20526
//        Engine pads: pin1 B, pin2 E, pin3 C  (== the base sheet's manual pinLabels, so the
//        transistor traces are unchanged). Cascade logic kept: base <- driver/detector net,
//        collector <- LED cathode, emitter -> GND.
//   DS1  WS2812B-B addressable RGB  SOT-23-like 4-pad  -> jlcpcb:C2761795
//        Engine pads: pin1 VDD, pin2 DOUT, pin3 VSS, pin4 DIN.
//        NOTE: the ground pad is named **VSS** (base sheet called it GND) -> DS1.VSS -> GND.
//   U51  SN74AHCT1G125DBVR  single 3-state buffer  SOT-23-5  -> jlcpcb:C7484
//        Engine pads: pin1 OE, pin2 A, pin3 GND, pin4 Y, pin5 VCC.
//        DESIGN CORRECTION (found by realizing against the real DBV part): the base sheet's
//        pinLabels (A/Y/OE/VCC/GND) did NOT match the real SOT-23-5 pinout. Real order is
//        1 OE, 2 A(in), 3 GND, 4 Y(out), 5 VCC. Mapping: A->WS2812, Y->DS1.DIN, OE->GND
//        (active-low enable, tied low = always on), VCC->+5V, GND->GND.
//        AHCT (not AHC) is required: at VCC=5V the WS2812 logic-high is ~3.5V, above the S3's
//        3.3V; AHCT's TTL input threshold recognises 3.3V as high, plain AHC (C7468, identical
//        land) would not — do NOT substitute the AHC variant.
//   U50  TSOP38238 IR receiver  SIP-3 (2.54mm)  -> jlcpcb:C141632
//        Engine pads: pin1 OUT, pin2 GND, pin3 VS  (== base labels). 100nF (Cir) at VS.
//   J50  microSD socket (push-pull)  Hanbo TF-013  -> jlcpcb:C961683
//        Engine pads: pin1 DAT2, pin2 (UNNAMED = card DAT3/CD = SPI **CS** -> .pin2), pin3 CMD,
//        pin4 VDD, pin5 CLK, pin6 VSS, pin7 DAT0, pin8 DAT1, pin9 DETECT1, pin10 DETECT2,
//        pin11 GND1, pin12 GND2.
//        SPI-mode map: CS=.pin2, MOSI=CMD, MISO=DAT0, SCK=CLK, VDD=+3V3, GND=VSS+GND1+GND2.
//        Card-detect switch: DETECT1->SD_CD, DETECT2->GND (card-in shorts SD_CD to GND, pulled
//        up on the PCA9555 side). DAT1/DAT2 unused in SPI -> left open.
//        ** verify the detect-switch terminals (DETECT1/DETECT2 polarity) on the real land before
//        fab — same caution as the audio jack. **
//   SW10  EC11 rotary encoder + push  ALPS EC11E1834403  -> jlcpcb:C361165
//        Engine pads: pin1 A, pin2 C, pin3 B, pin4 E, pin5 D, pin6 F, pin7 G.
//        Map: A->ENC_A, B->ENC_B, C(encoder common)->GND, push switch D->ENC_SW / E->GND,
//        mounting tabs F/G -> GND (mechanical, shield).
//
// Added support (vs base): Cds1 (WS2812 VDD HF decap) and Cu51 (74AHCT1G125 VCC decap) — both
// datasheet-standard 100nF, base sheet had none.
//
// Net names are UNCHANGED from the base sheet. TXDET_C5/NRF1/NRF2/NRF3/CC1101/SA868/LORA and
// WS2812_DOUT are single-ended off-sheet (analog detector taps / next-LED daisy-chain) — expected,
// not wiring defects. Slow control lines (WS2812, BUZZER, IR_*, SD_*, ENC_*, S3_BOOT, PTT_BTN,
// SPI_*) leave this sheet single-ended to their owner on Sheets 1/2.
export default () => (
  <board width="90mm" height="70mm">
    {/* ===================== TX-live LEDs x7 (analog, 0 GPIO) ===================== */}
    {/* Each transmit chain: amber LED lit by real RF envelope, never firmware. */}
    {/* D5x anode -> Rdimx -> +3V3 ; D5x cathode -> Q5x.C ; Q5x.E -> GND ; Q5x.B <- net.TXDET_x */}
    {/* chain 50 = C5 Wi-Fi/BLE */}
    <led name="D50" footprint="0603" />
    <chip name="Q50" footprint="jlcpcb:C20526" />
    <resistor name="Rd50" resistance="4.7k" footprint="0402" />
    {/* chain 51 = nRF24 #1 */}
    <led name="D51" footprint="0603" />
    <chip name="Q51" footprint="jlcpcb:C20526" />
    <resistor name="Rd51" resistance="4.7k" footprint="0402" />
    {/* chain 52 = nRF24 #2 */}
    <led name="D52" footprint="0603" />
    <chip name="Q52" footprint="jlcpcb:C20526" />
    <resistor name="Rd52" resistance="4.7k" footprint="0402" />
    {/* chain 53 = nRF24 #3 */}
    <led name="D53" footprint="0603" />
    <chip name="Q53" footprint="jlcpcb:C20526" />
    <resistor name="Rd53" resistance="4.7k" footprint="0402" />
    {/* chain 54 = CC1101 */}
    <led name="D54" footprint="0603" />
    <chip name="Q54" footprint="jlcpcb:C20526" />
    <resistor name="Rd54" resistance="4.7k" footprint="0402" />
    {/* chain 55 = SA868 */}
    <led name="D55" footprint="0603" />
    <chip name="Q55" footprint="jlcpcb:C20526" />
    <resistor name="Rd55" resistance="4.7k" footprint="0402" />
    {/* chain 56 = SX1262 (LoRa) */}
    <led name="D56" footprint="0603" />
    <chip name="Q56" footprint="jlcpcb:C20526" />
    <resistor name="Rd56" resistance="4.7k" footprint="0402" />

    {/* ===================== WS2812 status LED + level shift ===================== */}
    {/* DS1 on S3 GPIO1 (RMT), +5V, DIN via 74AHCT1G125 (U51) 3V3->5V TTL buffer */}
    <chip name="DS1" footprint="jlcpcb:C2761795" />
    <chip name="U51" footprint="jlcpcb:C7484" />
    <capacitor name="Cds1" capacitance="100nF" footprint="0402" /> {/* added: WS2812 VDD decap */}
    <capacitor name="Cu51" capacitance="100nF" footprint="0402" /> {/* added: 74AHCT VCC decap */}

    {/* ===================== Buzzer ===================== */}
    {/* LS2 active buzzer via Q57, on +5V, gated by net.BUZZER (PCA9555 #1 P0.5) */}
    <resistor name="LS2" resistance="0.01" footprint="1210" /> {/* active buzzer proxy */}
    <chip name="Q57" footprint="jlcpcb:C20526" />

    {/* ===================== IR ===================== */}
    {/* TX: D57 IR LED driven by Q58 from GPIO2 (38kHz), +5V */}
    <led name="D57" footprint="0603" />
    <chip name="Q58" footprint="jlcpcb:C20526" />
    <resistor name="Rir" resistance="47" footprint="0603" />
    {/* RX: U50 TSOP38238 into GPIO42 (RMT), +3V3 */}
    <chip name="U50" footprint="jlcpcb:C141632" />
    <capacitor name="Cir" capacitance="100nF" footprint="0402" />

    {/* ===================== microSD (SPI mode) ===================== */}
    {/* J50 on shared SPI2, CS from 74HC138 Y0, CD on PCA9555 #1 P1.7, 3V3 native */}
    <chip name="J50" footprint="jlcpcb:C961683" />
    <capacitor name="Csd1" capacitance="10uF" footprint="0805" />
    <capacitor name="Csd2" capacitance="100nF" footprint="0402" />

    {/* ===================== Rotary encoder ===================== */}
    {/* SW10 quadrature A/B (GPIO40/41) + push (PCA9555 #1 P0.0) */}
    <chip name="SW10" footprint="jlcpcb:C361165" />

    {/* ===================== Physical buttons ===================== */}
    {/* SW11 RESET across S3 EN-GND (10k pull-up + 1uF RC) */}
    <resistor name="SW11" resistance="0.01" footprint="1210" /> {/* RESET button proxy */}
    <resistor name="Ren" resistance="10k" footprint="0402" />
    <capacitor name="Cen" capacitance="1uF" footprint="0402" />
    {/* SW12 BOOT: S3 GPIO0 -> GND */}
    <resistor name="SW12" resistance="0.01" footprint="1210" /> {/* BOOT button proxy */}
    {/* SW13 PTT: -> GND on PCA9555 #2 P0.0 */}
    <resistor name="SW13" resistance="0.01" footprint="1210" /> {/* PTT button proxy */}

    {/* ============================== NETS ============================== */}
    {/* --- TX-live LED chains (analog, no GPIO) --- */}
    <trace from=".D50 > .pin1" to=".Rd50 > .pin1" />
    <trace from=".Rd50 > .pin2" to="net.V3V3" />
    <trace from=".D50 > .pin2" to=".Q50 > .C" />
    <trace from=".Q50 > .E" to="net.GND" />
    <trace from=".Q50 > .B" to="net.TXDET_C5" />

    <trace from=".D51 > .pin1" to=".Rd51 > .pin1" />
    <trace from=".Rd51 > .pin2" to="net.V3V3" />
    <trace from=".D51 > .pin2" to=".Q51 > .C" />
    <trace from=".Q51 > .E" to="net.GND" />
    <trace from=".Q51 > .B" to="net.TXDET_NRF1" />

    <trace from=".D52 > .pin1" to=".Rd52 > .pin1" />
    <trace from=".Rd52 > .pin2" to="net.V3V3" />
    <trace from=".D52 > .pin2" to=".Q52 > .C" />
    <trace from=".Q52 > .E" to="net.GND" />
    <trace from=".Q52 > .B" to="net.TXDET_NRF2" />

    <trace from=".D53 > .pin1" to=".Rd53 > .pin1" />
    <trace from=".Rd53 > .pin2" to="net.V3V3" />
    <trace from=".D53 > .pin2" to=".Q53 > .C" />
    <trace from=".Q53 > .E" to="net.GND" />
    <trace from=".Q53 > .B" to="net.TXDET_NRF3" />

    <trace from=".D54 > .pin1" to=".Rd54 > .pin1" />
    <trace from=".Rd54 > .pin2" to="net.V3V3" />
    <trace from=".D54 > .pin2" to=".Q54 > .C" />
    <trace from=".Q54 > .E" to="net.GND" />
    <trace from=".Q54 > .B" to="net.TXDET_CC1101" />

    <trace from=".D55 > .pin1" to=".Rd55 > .pin1" />
    <trace from=".Rd55 > .pin2" to="net.V3V3" />
    <trace from=".D55 > .pin2" to=".Q55 > .C" />
    <trace from=".Q55 > .E" to="net.GND" />
    <trace from=".Q55 > .B" to="net.TXDET_SA868" />

    <trace from=".D56 > .pin1" to=".Rd56 > .pin1" />
    <trace from=".Rd56 > .pin2" to="net.V3V3" />
    <trace from=".D56 > .pin2" to=".Q56 > .C" />
    <trace from=".Q56 > .E" to="net.GND" />
    <trace from=".Q56 > .B" to="net.TXDET_LORA" />

    {/* --- WS2812 + 74AHCT1G125 shift (engine pads: U51 OE/A/GND/Y/VCC, DS1 VDD/DOUT/VSS/DIN) --- */}
    <trace from=".U51 > .A" to="net.WS2812" />
    <trace from=".U51 > .OE" to="net.GND" />       {/* active-low enable tied low = always on */}
    <trace from=".U51 > .VCC" to="net.V5" />
    <trace from=".U51 > .GND" to="net.GND" />
    <trace from=".U51 > .Y" to=".DS1 > .DIN" />
    <trace from=".DS1 > .VDD" to="net.V5" />
    <trace from=".DS1 > .VSS" to="net.GND" />       {/* engine pad is VSS (was GND in base) */}
    <trace from=".DS1 > .DOUT" to="net.WS2812_DOUT" />
    <trace from=".Cds1 > .pin1" to="net.V5" />
    <trace from=".Cds1 > .pin2" to="net.GND" />
    <trace from=".Cu51 > .pin1" to="net.V5" />
    <trace from=".Cu51 > .pin2" to="net.GND" />

    {/* --- Buzzer --- */}
    <trace from=".LS2 > .pin1" to="net.V5" />
    <trace from=".LS2 > .pin2" to=".Q57 > .C" />
    <trace from=".Q57 > .E" to="net.GND" />
    <trace from=".Q57 > .B" to="net.BUZZER" />

    {/* --- IR TX --- */}
    <trace from=".D57 > .pin1" to=".Rir > .pin1" />
    <trace from=".Rir > .pin2" to="net.V5" />
    <trace from=".D57 > .pin2" to=".Q58 > .C" />
    <trace from=".Q58 > .E" to="net.GND" />
    <trace from=".Q58 > .B" to="net.IR_TX" />

    {/* --- IR RX (TSOP38238 engine pads OUT/GND/VS) --- */}
    <trace from=".U50 > .OUT" to="net.IR_RX" />
    <trace from=".U50 > .VS" to="net.V3V3" />
    <trace from=".U50 > .GND" to="net.GND" />
    <trace from=".Cir > .pin1" to="net.V3V3" />
    <trace from=".Cir > .pin2" to="net.GND" />

    {/* --- microSD (CS = engine-unnamed .pin2 = card DAT3) --- */}
    <trace from=".J50 > .pin2" to="net.SD_CS" />
    <trace from=".J50 > .CMD" to="net.SPI_MOSI" />
    <trace from=".J50 > .DAT0" to="net.SPI_MISO" />
    <trace from=".J50 > .CLK" to="net.SPI_SCK" />
    <trace from=".J50 > .VDD" to="net.V3V3" />
    <trace from=".J50 > .VSS" to="net.GND" />
    <trace from=".J50 > .GND1" to="net.GND" />
    <trace from=".J50 > .GND2" to="net.GND" />
    <trace from=".J50 > .DETECT1" to="net.SD_CD" />
    <trace from=".J50 > .DETECT2" to="net.GND" />
    <trace from=".Csd1 > .pin1" to="net.V3V3" />
    <trace from=".Csd1 > .pin2" to="net.GND" />
    <trace from=".Csd2 > .pin1" to="net.V3V3" />
    <trace from=".Csd2 > .pin2" to="net.GND" />

    {/* --- Rotary encoder (engine pads A/B/C + switch D/E + tabs F/G) --- */}
    <trace from=".SW10 > .A" to="net.ENC_A" />
    <trace from=".SW10 > .B" to="net.ENC_B" />
    <trace from=".SW10 > .C" to="net.GND" />       {/* encoder common */}
    <trace from=".SW10 > .D" to="net.ENC_SW" />    {/* push switch terminal 1 */}
    <trace from=".SW10 > .E" to="net.GND" />       {/* push switch terminal 2 */}
    <trace from=".SW10 > .F" to="net.GND" />       {/* mounting tab */}
    <trace from=".SW10 > .G" to="net.GND" />       {/* mounting tab */}

    {/* --- Physical buttons --- */}
    <trace from=".SW11 > .pin1" to="net.S3_EN" />
    <trace from=".SW11 > .pin2" to="net.GND" />
    <trace from=".Ren > .pin1" to="net.V3V3" />
    <trace from=".Ren > .pin2" to="net.S3_EN" />
    <trace from=".Cen > .pin1" to="net.S3_EN" />
    <trace from=".Cen > .pin2" to="net.GND" />
    <trace from=".SW12 > .pin1" to="net.S3_BOOT" />
    <trace from=".SW12 > .pin2" to="net.GND" />
    <trace from=".SW13 > .pin1" to="net.PTT_BTN" />
    <trace from=".SW13 > .pin2" to="net.GND" />
  </board>
)
