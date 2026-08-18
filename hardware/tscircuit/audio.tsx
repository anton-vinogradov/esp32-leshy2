// Leshy2 — Sheet 4: Audio  (FAB-READY draft, engine-pulled footprints by LCSC number)
//
// METHOD: every real IC/module uses footprint="jlcpcb:C<number>". The parts engine supplies
// the REAL pads AND the REAL pad NAMES from the LCSC/EasyEDA database, so no pin numbers are
// typed by hand for those. Traces reference the engine pad names (verified via
// `tsci export -f readable-netlist`, WITHOUT --disable-parts-engine).
// Placeholder (3.5 mm jack J30) keeps explicit pinLabels — same convention as BT1 (Sheet 1) /
// nRF24 (Sheet 3) — and the electret mic (MK1) / speaker (LS1) stay 2-pin resistor proxies.
//
// Pad-name sources of truth (engine probe of each footprint):
//   U30  Si4732-A10-GSR  16-SOIC  -> jlcpcb:C2155558
//        Engine pads: 4 GPO1, 5 NC, 6 FMI, 7 RFGND, 8 AMI, 9 RST, 10 SENB, 11 SCLK, 12 SDIO,
//        13 RCLK, 14 VDD, 15 GND. Pads 1,2,3,16 are engine-UNNAMED -> referenced by .pin#.
//        Per the Si4732-A10 datasheet 16-SOIC pinout: pin1 LOUT/DFS, pin2 GPO3/DCLK,
//        pin3 GPO2/INTB, pin16 ROUT/DOUT (single VDD, no separate VA). Only pins 1 and 16
//        are analog audio outputs in this design. They feed identical 10 k summing resistors,
//        so L/R interchange is electrically a no-op after the deliberate mono sum.
//        Added vs base logic (datasheet typical app): RFGND(pin7)->GND (RF ground, mandatory);
//        Cvdd30b 100nF HF decoupling at VDD (base only had 1uF bulk).
//   U31  SA868-U UHF walkie module  20-pad  -> jlcpcb:C3001507   (REAL module land, not a header)
//        Engine pads: 1 AudioON, 2 NC1, 3 AF_OUT, 4 NC2, 5 PTT, 6 PD, 7 (H/L, engine-unnamed),
//        8 VBAT, 9 GND1, 10 GND2, 11 NC3, 12 ANT, 13 NC4, 14 NC5, 15 NC6, 16 RXD, 17 TXD,
//        18 MIC_IN, 19 EP2, 20 EP1.  (NiceRF SA868 datasheet.)
//        DESIGN CORRECTION (found by realizing against the real module): the SA868-U is a
//        SINGLE-SUPPLY module (one VBAT pin, 3.3-5.5 V) — it does NOT have the separate
//        VIN(+5V)/VCC3V3(+3V3) pins the base sheet assumed. VBAT -> +5V (PA burst, rail sized on
//        the power sheet). The base's U31.VCC3V3 -> +3V3 connection has no real pad and is dropped.
//        AudioON(pin1) is active-LOW enable of the module's internal audio amp -> tied to GND
//        (RX audio at AF_OUT always available while PD keeps the module awake). H/L(pin7) is the
//        TX power select: "open = high; low level = low power" per datasheet. DEC-0003 requires
//        a conservative hardware default, so H/L is grounded in this prerequisite-stage draft.
//        A future controllable high-power release path requires stage-3 pin/safety proof.
//   U32  PAM8302AASCR  8-pin MSOP  -> jlcpcb:C113367
//        Engine pads: 1 SD, 2 IN_NEG, 3 IN_POS, 4 (NC, engine-unnamed), 5 VO_POS, 6 VDD,
//        7 GND, 8 VO_NEG.  DESIGN NOTE: the real PAM8302A is 8-pin MSOP, not SOT-23-6 as the
//        base sheet guessed. Inputs are internally biased to VDD/2 -> AC-couple BOTH:
//        MUX_OUT -> Rin32 -> Cinp(0.1uF) -> IN_POS ; IN_NEG -> Cinn(0.1uF) -> GND.
//   U33  SN74LVC1G3157DBVR  SOT-23-6  -> jlcpcb:C10426   (2:1 analog switch)
//        Engine pads: 1 B2, 2 GND, 3 B1, 4 A(common), 5 VCC, 6 S(select).
//        Map: A=COM->MUX_OUT, B1->SI_AUDIO (Si4732), B2->SA_AF (SA868), S->MUX_SEL.
//   Y1   32.768 kHz crystal  NDK NX3215SA  -> jlcpcb:C280830   (engine pads OSC1/OSC2, clean)
//
// Placeholder (footprint geometric, NOT engine):
//   J30  3.5 mm stereo jack + detect -> pinrow4 placeholder + pinLabels L/R/SLEEVE/DET.
//        No clean LCSC land maps 1:1 to our 4 signals; swap for the real jack land (and verify
//        the switch/detect terminal order) before fab.
//   MK1  electret mic  -> res0603 proxy (2-pin).   LS1  speaker 4-8 ohm -> res1210 proxy (2-pin).
//
// Net names are unchanged from the base sheet. Antenna ends (ANT_HF_CB, ANT_FM via Si4732;
// ANT_UHF via SA868) stay single-ended off-sheet (external whip/SMA, matched by hand) — expected,
// not a wiring defect. V3V3 keeps only U33.VCC on this sheet (U31 dropped its 3V3 pin, above).
export default () => (
  <board width="80mm" height="60mm">
    {/* ===================== Si4732-A10-GSR receiver (U30, all on +3V3A) ===================== */}
    <chip name="U30" footprint="jlcpcb:C2155558" />
    {/* dedicated 32.768 kHz watch crystal + load caps (NOT from MCU) */}
    <chip name="Y1" footprint="jlcpcb:C280830" />
    <capacitor name="CL1" capacitance="12pF" footprint="0402" />
    <capacitor name="CL2" capacitance="12pF" footprint="0402" />
    <capacitor name="Cvdd30" capacitance="1uF" footprint="0402" />
    <capacitor name="Cvdd30b" capacitance="100nF" footprint="0402" /> {/* added: VDD HF decap */}
    <resistor name="Rpu_jack" resistance="10k" footprint="0402" /> {/* JACK_DET pull-up (PCA9555 input has no internal pull-up) */}
    <trace from=".Rpu_jack > .pin1" to="net.JACK_DET" /><trace from=".Rpu_jack > .pin2" to="net.V3V3" />
    {/* L+R -> mono summing resistor pair */}
    <resistor name="RsumL" resistance="10k" footprint="0402" />
    <resistor name="RsumR" resistance="10k" footprint="0402" />

    {/* ===================== SA868-U UHF voice walkie (U31, single-supply module) ===================== */}
    <chip name="U31" footprint="jlcpcb:C3001507" />
    {/* local bulk on VBAT for the 2 W PA burst */}
    <capacitor name="Cbulk31" capacitance="330uF" footprint="1210" />
    <capacitor name="Cbyp31" capacitance="100nF" footprint="0402" />
    {/* Hardware safe defaults independent of PCA9555 configuration/firmware. */}
    <resistor name="Rsa_ptt_safe" resistance="10k" footprint="0402" /> {/* PTT=1 -> RX */}
    <resistor name="Rsa_pd_safe" resistance="10k" footprint="0402" />  {/* PD=0 -> power-down */}
    <resistor name="Rsa_hl_safe" resistance="0.01" footprint="0402" /> {/* H/L=0 -> low power */}
    {/* electret mic + bias -> 1 uF coupling into SA868 MIC (1uF, not 10uF!) */}
    <resistor name="MK1" resistance="2.2k" footprint="0603" /> {/* electret mic proxy */}
    <resistor name="Rbias" resistance="4.7k" footprint="0402" />
    <capacitor name="Cmic" capacitance="1uF" footprint="0402" />

    {/* ===================== 2:1 analog mux 74LVC1G3157 (U33) ===================== */}
    <chip name="U33" footprint="jlcpcb:C10426" />

    {/* ===================== PAM8302A class-D amp (U32) ===================== */}
    <chip name="U32" footprint="jlcpcb:C113367" />
    <resistor name="Rin32" resistance="10k" footprint="0402" /> {/* input series R */}
    <capacitor name="Cinp" capacitance="0.1uF" footprint="0402" /> {/* AC-couple IN+ (PAM8302 biases inputs to VDD/2) */}
    <capacitor name="Cinn" capacitance="0.1uF" footprint="0402" /> {/* matching AC-couple on IN- to GND */}
    <capacitor name="Cvcc32" capacitance="10uF" footprint="0805" />
    <capacitor name="Cd33" capacitance="100nF" footprint="0402" /><trace from=".Cd33 > .pin1" to="net.V3V3" /><trace from=".Cd33 > .pin2" to="net.GND" /> {/* mux U33 VCC bypass (was missing) */}

    {/* speaker (BTL, no ground reference) */}
    <resistor name="LS1" resistance="4" footprint="1210" /> {/* 4-8 ohm speaker proxy */}

    {/* 3.5mm headphone jack — AC-couple BOTH legs (amp is BTL), mute on insert */}
    <chip name="J30" footprint="pinrow4" pinLabels={{
      pin1: "L", pin2: "R", pin3: "SLEEVE", pin4: "DET",
    }} />
    <capacitor name="Cjk1" capacitance="220uF" footprint="1210" /> {/* AC-couple SPK_P -> L */}
    <capacitor name="Cjk2" capacitance="220uF" footprint="1210" /> {/* AC-couple SPK_M -> R */}

    {/* ============================== NETS ============================== */}
    {/* --- Si4732 supply + I2C + control --- */}
    <trace from=".U30 > .VDD" to="net.V3V3A" />
    <trace from=".U30 > .GND" to="net.GND" />
    <trace from=".U30 > .RFGND" to="net.GND" />      {/* added: RF ground pad */}
    <trace from=".Cvdd30 > .pin1" to="net.V3V3A" />
    <trace from=".Cvdd30 > .pin2" to="net.GND" />
    <trace from=".Cvdd30b > .pin1" to="net.V3V3A" /> {/* added: VDD HF decap */}
    <trace from=".Cvdd30b > .pin2" to="net.GND" />
    <trace from=".U30 > .SDIO" to="net.I2C_SDA" />
    <trace from=".U30 > .SCLK" to="net.I2C_SCL" />
    <trace from=".U30 > .SENB" to="net.GND" />        {/* SENB->GND = addr 0x11 */}
    <trace from=".U30 > .RST" to="net.Si4732_RST" />  {/* PCA #1 P0.3 */}

    {/* --- Si4732 RCLK from dedicated 32.768 kHz crystal (OSC2 grounded; both load caps RCLK->GND) --- */}
    <trace from=".U30 > .RCLK" to=".Y1 > .OSC1" />
    <trace from=".Y1 > .OSC2" to="net.GND" />
    <trace from=".CL1 > .pin1" to=".U30 > .RCLK" />
    <trace from=".CL1 > .pin2" to="net.GND" />
    <trace from=".CL2 > .pin1" to=".U30 > .RCLK" />
    <trace from=".CL2 > .pin2" to="net.GND" />

    {/* --- Si4732 antennas (off-sheet nets) --- */}
    <trace from=".U30 > .AMI" to="net.ANT_HF_CB" />
    <trace from=".U30 > .FMI" to="net.ANT_FM" />

    {/* --- Si4732 line-out -> summing pair -> mux B1 (pin1=LOUT, pin16=ROUT) --- */}
    <trace from=".U30 > .pin1" to=".RsumL > .pin1" />
    <trace from=".U30 > .pin16" to=".RsumR > .pin1" />
    <trace from=".RsumL > .pin2" to="net.SI_AUDIO" />
    <trace from=".RsumR > .pin2" to="net.SI_AUDIO" />
    <trace from=".U33 > .B1" to="net.SI_AUDIO" />

    {/* --- SA868 power + logic + UART1 + control (single VBAT rail) --- */}
    <trace from=".U31 > .VBAT" to="net.V5" />
    <trace from=".U31 > .GND1" to="net.GND" />
    <trace from=".U31 > .GND2" to="net.GND" />
    <trace from=".U31 > .EP1" to="net.GND" />
    <trace from=".U31 > .EP2" to="net.GND" />
    <trace from=".U31 > .AudioON" to="net.GND" />       {/* active-low -> internal audio amp ON */}
    <trace from=".Cbulk31 > .pin1" to="net.V5" />
    <trace from=".Cbulk31 > .pin2" to="net.GND" />
    <trace from=".Cbyp31 > .pin1" to="net.V5" />
    <trace from=".Cbyp31 > .pin2" to="net.GND" />
    <trace from=".U31 > .RXD" to="net.SA868_UART_TX" />  {/* S3 TX GPIO16 -> U31.RXD */}
    <trace from=".U31 > .TXD" to="net.SA868_UART_RX" />  {/* U31.TXD -> S3 RX GPIO17 */}
    <trace from=".U31 > .PTT" to="net.SA868_PTT" />      {/* PCA #1 P0.1 */}
    <trace from=".U31 > .PD" to="net.SA868_PD" />        {/* PCA #1 P0.2 */}
    <trace from=".Rsa_ptt_safe > .pin1" to="net.SA868_PTT" />
    <trace from=".Rsa_ptt_safe > .pin2" to="net.V3V3" />
    <trace from=".Rsa_pd_safe > .pin1" to="net.SA868_PD" />
    <trace from=".Rsa_pd_safe > .pin2" to="net.GND" />
    <trace from=".U31 > .pin7" to=".Rsa_hl_safe > .pin1" />
    <trace from=".Rsa_hl_safe > .pin2" to="net.GND" />
    <trace from=".U31 > .ANT" to="net.ANT_UHF" />
    {/* High power is intentionally unavailable until a fail-safe controllable H/L path is accepted. */}

    {/* --- SA868 RX audio -> mux B2 --- */}
    <trace from=".U31 > .AF_OUT" to="net.SA_AF" />
    <trace from=".U33 > .B2" to="net.SA_AF" />

    {/* --- Mic -> 1 uF -> SA868 MIC --- */}
    <trace from=".MK1 > .pin1" to="net.MIC_HOT" />
    <trace from=".MK1 > .pin2" to="net.GND" />
    <trace from=".Rbias > .pin1" to="net.V3V3A" />
    <trace from=".Rbias > .pin2" to="net.MIC_HOT" />
    <trace from=".Cmic > .pin1" to="net.MIC_HOT" />
    <trace from=".Cmic > .pin2" to=".U31 > .MIC_IN" />

    {/* --- Mux control + supply (A=COM, B1=Si4732, B2=SA868, S=select) --- */}
    <trace from=".U33 > .S" to="net.MUX_SEL" />       {/* PCA #1 P0.7 */}
    <trace from=".U33 > .VCC" to="net.V3V3" />
    <trace from=".U33 > .GND" to="net.GND" />
    <trace from=".U33 > .A" to="net.MUX_OUT" />

    {/* --- Amp: mux out -> Rin -> AC-couple -> PAM8302 IN_POS; IN_NEG AC-coupled to GND.
        PAM8302 biases both inputs internally to VDD/2 via 10k, so a series cap on each input
        is required — hard-grounding IN- (or DC-coupling IN+) breaks the bias and rails the output. */}
    <trace from=".Rin32 > .pin1" to="net.MUX_OUT" />
    <trace from=".Rin32 > .pin2" to=".Cinp > .pin1" />
    <trace from=".Cinp > .pin2" to=".U32 > .IN_POS" />
    <trace from=".U32 > .IN_NEG" to=".Cinn > .pin1" />
    <trace from=".Cinn > .pin2" to="net.GND" />
    <trace from=".U32 > .SD" to="net.PAM_SD" />      {/* PCA #1 P1.3 */}
    <trace from=".U32 > .VDD" to="net.V5" />
    <trace from=".U32 > .GND" to="net.GND" />
    <trace from=".Cvcc32 > .pin1" to="net.V5" />
    <trace from=".Cvcc32 > .pin2" to="net.GND" />
    {/* U32 pin4 = NC, left open */}

    {/* --- Speaker (BTL, floating) --- */}
    <trace from=".U32 > .VO_POS" to="net.SPK_P" />
    <trace from=".U32 > .VO_NEG" to="net.SPK_M" />
    <trace from=".LS1 > .pin1" to="net.SPK_P" />
    <trace from=".LS1 > .pin2" to="net.SPK_M" />

    {/* --- Headphone jack: AC-couple both BTL legs, jack-detect --- */}
    <trace from=".Cjk1 > .pin1" to="net.SPK_P" />
    <trace from=".Cjk1 > .pin2" to=".J30 > .L" />
    <trace from=".Cjk2 > .pin1" to="net.SPK_M" />
    <trace from=".Cjk2 > .pin2" to=".J30 > .R" />
    <trace from=".J30 > .SLEEVE" to="net.GND" />
    <trace from=".J30 > .DET" to="net.JACK_DET" />  {/* PCA #2 (0x21) P0.3 */}
  </board>
)
