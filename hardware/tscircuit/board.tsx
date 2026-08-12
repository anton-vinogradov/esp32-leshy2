// Leshy2 - MERGED board (all 6 REALIZED sheets in one <board>)
// Sources: power / c5-buses / rf / audio / expansion / indicators (.tsx), post self-review.
// Real engine footprints (jlcpcb:C...) + a few geometric placeholders, unchanged.
// Refdes collisions resolved so every name= is unique across the whole board:
//   c5-buses U20 (ESP32-C5)     -> m_U20
//   rf       U20 (nRF24 #1)     -> rf_U20
//   rf       Y1  (26 MHz xtal)  -> rf_Y1
//   audio    Y1  (32.768 kHz)   -> a_Y1
//   rf       Rbias (56k CC1101) -> rf_Rbias
//   audio    Rbias (4.7k mic)   -> a_Rbias
// New self-review parts (power RT2/Rbst4/Rbst5, net.SNS; audio Cinp/Cinn) are single-sheet,
// no new cross-sheet collisions. Net names (net.NAME) kept verbatim: identical names across
// sheets join = inter-sheet stitching (SPI/I2C/rails/RFSW_C/...).
export default () => (
  <board width="400mm" height="300mm">

    {/* ================= SHEET 1 - POWER ================= */}

    {/* ===================== USB-C inputs ===================== */}
    {/* J1 -> S3 : 5 V charge + data. C2988369: VBUS1/2, GND1/2, CC1/2, DP1/DP2, DN1/DN2,
        SBU1/2, SHELL1..SHELL4 (shield tabs). */}
    <chip name="J1" footprint="jlcpcb:C2988369" />
    <resistor name="Rcc1" resistance="5.1k" footprint="0402" />
    <resistor name="Rcc2" resistance="5.1k" footprint="0402" />
    {/* VBUS bulk (10uF) + TVS/ESD (D1 proxy) on the J1 5 V input */}
    <capacitor name="Cvbus" capacitance="10uF" footprint="0805" />
    <resistor name="D1" resistance="1M" footprint="0603" /> {/* TVS proxy on VBUS_S3 */}
    {/* J2 -> C5 : data only, VBUS = ESD stub */}
    <chip name="J2" footprint="jlcpcb:C2988369" />

    {/* ===================== BQ25887 2S BOOST charger ===================== */}
    <chip name="U2" footprint="jlcpcb:C2761614" />
    <inductor name="L1" inductance="2.2uH" footprint="1210" /> {/* boost inductor PMID<->SW */}
    <capacitor name="Cvbusic" capacitance="1uF" footprint="0402" /> {/* >=1uF at VBUS pin */}
    <capacitor name="Cpmid" capacitance="10uF" footprint="0805" /> {/* PMID input cap (25V) */}
    <capacitor name="Cregn" capacitance="4.7uF" footprint="0805" /> {/* REGN LDO bypass */}
    <capacitor name="Cbtst" capacitance="47nF" footprint="0402" /> {/* BTST->SW bootstrap */}
    <capacitor name="Csns" capacitance="47uF" footprint="1210" /> {/* SNS boost-output cap (ds 44uF) */}
    <capacitor name="Cbat" capacitance="10uF" footprint="0805" /> {/* BAT decoupling */}
    <resistor name="Rilim" resistance="383" footprint="0402" /> {/* input current limit set */}
    <resistor name="Rmid" resistance="300" footprint="0402" /> {/* MID cell-mid sense series */}
    <resistor name="Rcbset" resistance="10" footprint="0402" /> {/* cell-balance current limit (~9.5R) */}
    <resistor name="Rts_top" resistance="5.23k" footprint="0402" /> {/* TS divider top REGN->TS */}
    <resistor name="RT1" resistance="10k" footprint="0603" /> {/* 103AT NTC to GND (TS bottom) */}
    <resistor name="RT2" resistance="30.1k" footprint="0402" /> {/* TS: parallel to 103AT NTC (BQ25887 ref) */}

    {/* ===================== 2S pack + protection (S-8252A, low-side, common-drain) ===================== */}
    <chip name="BT1" footprint="pinrow3" pinLabels={{ pin1: "P_PLUS", pin2: "MID", pin3: "P_MINUS" }} />
    <chip name="U3" footprint="jlcpcb:C468224" />
    {/* AO3400A N-FET (engine: 1 G, 2 S, 3 D). COMMON-DRAIN per S-8252 Fig.14:
        Q1 = discharge (gate DO), source at B-/VSS.  Q2 = charge (gate CO), source at EB-/GND.
        Drains tied at PACKMID. */}
    <chip name="Q1" footprint="jlcpcb:C20917" />
    <chip name="Q2" footprint="jlcpcb:C20917" />
    <resistor name="Rvdd" resistance="470" footprint="0402" /> {/* R1: VDD series to B+ */}
    <resistor name="Rvc" resistance="470" footprint="0402" />  {/* R2: VC series to cell-mid */}
    <resistor name="Rvm" resistance="2k" footprint="0402" />   {/* R3: VM series to EB-/GND */}
    <capacitor name="Cvdd" capacitance="0.1uF" footprint="0402" /> {/* C1: VDD-VSS */}
    <capacitor name="Cvc" capacitance="0.1uF" footprint="0402" />  {/* C2: VC-VSS */}
    <resistor name="F1" resistance="0.05" footprint="1210" />  {/* PPTC fuse proxy (pack +) */}
    <chip name="SW1" footprint="jlcpcb:C496164" /> {/* master switch: SPDT ON-OFF, COM=pin2, throw=pin1, pin3 NC */}

    {/* ===================== +5 V buck : MP2315 ===================== */}
    <chip name="U4" footprint="jlcpcb:C45889" />
    <inductor name="L2" inductance="4.7uH" footprint="1210" />
    <capacitor name="Cin5" capacitance="22uF" footprint="0805" />
    <capacitor name="Cout5" capacitance="22uF" footprint="0805" />
    <capacitor name="Cbst4" capacitance="100nF" footprint="0402" /> {/* bootstrap BST->SW */}
    <resistor name="Rbst4" resistance="20" footprint="0402" /> {/* MP2315 bootstrap series R (datasheet-required) */}
    <capacitor name="Cvcc4" capacitance="0.1uF" footprint="0402" /> {/* VCC decouple */}
    <resistor name="Raam4" resistance="100k" footprint="0402" /> {/* AAM light-load set */}
    <resistor name="R1" resistance="52.3k" footprint="0402" />
    <resistor name="R2" resistance="10k" footprint="0402" />

    {/* ===================== +3V3 buck : MP2315 (wide Vin — sits on 8.4 V BAT) ===================== */}
    <chip name="U5" footprint="jlcpcb:C45889" />
    <inductor name="L3" inductance="2.2uH" footprint="1210" />
    <capacitor name="Cin3" capacitance="22uF" footprint="0805" />
    <capacitor name="Cout3" capacitance="22uF" footprint="0805" />
    <capacitor name="Cbst5" capacitance="100nF" footprint="0402" /> {/* bootstrap BST->SW */}
    <resistor name="Rbst5" resistance="20" footprint="0402" /> {/* MP2315 bootstrap series R (datasheet-required) */}
    <capacitor name="Cvcc5" capacitance="0.1uF" footprint="0402" /> {/* VCC decouple */}
    <resistor name="Raam5" resistance="100k" footprint="0402" /> {/* AAM light-load set */}
    <resistor name="R3" resistance="31.6k" footprint="0402" /> {/* FB top: 0.8*(1+31.6/10)=3.33V */}
    <resistor name="R4" resistance="10k" footprint="0402" />
    <resistor name="R_EN3H" resistance="100k" footprint="0402" /> {/* EN divider top (BAT) */}
    <resistor name="R_EN3L" resistance="47k" footprint="0402" />  {/* EN divider bottom (GND) */}

    {/* ===================== +3V3A LDO : TPS7A2033 (from +5V) ===================== */}
    <chip name="U6" footprint="jlcpcb:C2862740" />
    <capacitor name="Cin3a" capacitance="1uF" footprint="0402" />
    <capacitor name="Cout3a" capacitance="2.2uF" footprint="0402" />
    <resistor name="R_RE5" resistance="100k" footprint="0402" />  {/* RAIL_EN_5V default off */}
    <resistor name="R_RE3A" resistance="100k" footprint="0402" /> {/* RAIL_EN_3V3A default off */}

    {/* ============================== NETS ============================== */}
    {/* --- USB J1 -> S3 --- */}
    <trace from=".J1 > .VBUS1" to="net.VBUS_S3" />
    <trace from=".J1 > .VBUS2" to="net.VBUS_S3" />
    <trace from=".Cvbus > .pin1" to="net.VBUS_S3" />
    <trace from=".Cvbus > .pin2" to="net.GND" />
    <trace from=".D1 > .pin1" to="net.VBUS_S3" />
    <trace from=".D1 > .pin2" to="net.GND" />
    <trace from=".J1 > .GND1" to="net.GND" />
    <trace from=".J1 > .GND2" to="net.GND" />
    <trace from=".J1 > .SHELL1" to="net.GND" /> {/* shield tabs -> GND */}
    <trace from=".J1 > .SHELL2" to="net.GND" />
    <trace from=".J1 > .SHELL3" to="net.GND" />
    <trace from=".J1 > .SHELL4" to="net.GND" />
    <trace from=".J1 > .DP1" to="net.USB_DP_S3" />
    <trace from=".J1 > .DP2" to="net.USB_DP_S3" />
    <trace from=".J1 > .DN1" to="net.USB_DM_S3" />
    <trace from=".J1 > .DN2" to="net.USB_DM_S3" />
    <trace from=".Rcc1 > .pin1" to=".J1 > .CC1" />
    <trace from=".Rcc1 > .pin2" to="net.GND" />
    <trace from=".Rcc2 > .pin1" to=".J1 > .CC2" />
    <trace from=".Rcc2 > .pin2" to="net.GND" />
    {/* --- USB J2 -> C5 (data only) --- */}
    <trace from=".J2 > .VBUS1" to="net.VBUS_C5" />
    <trace from=".J2 > .VBUS2" to="net.VBUS_C5" />
    <trace from=".J2 > .GND1" to="net.GND" />
    <trace from=".J2 > .GND2" to="net.GND" />
    <trace from=".J2 > .SHELL1" to="net.GND" /> {/* shield tabs -> GND */}
    <trace from=".J2 > .SHELL2" to="net.GND" />
    <trace from=".J2 > .SHELL3" to="net.GND" />
    <trace from=".J2 > .SHELL4" to="net.GND" />
    <trace from=".J2 > .DP1" to="net.USB_DP_C5" />
    <trace from=".J2 > .DP2" to="net.USB_DP_C5" />
    <trace from=".J2 > .DN1" to="net.USB_DM_C5" />
    <trace from=".J2 > .DN2" to="net.USB_DM_C5" />

    {/* --- Charger BQ25887 (BOOST) --- */}
    <trace from=".U2 > .VBUS" to="net.VBUS_S3" />
    <trace from=".Cvbusic > .pin1" to="net.VBUS_S3" /> {/* >=1uF at VBUS pin */}
    <trace from=".Cvbusic > .pin2" to="net.GND" />
    {/* PMID (input rail after blocking FET) */}
    <trace from=".U2 > .PMID1" to="net.PMID" />
    <trace from=".U2 > .PMID2" to="net.PMID" />
    <trace from=".Cpmid > .pin1" to="net.PMID" />
    <trace from=".Cpmid > .pin2" to="net.GND" />
    {/* boost inductor: PMID -> L1 -> SW */}
    <trace from=".L1 > .pin1" to="net.PMID" />
    <trace from=".L1 > .pin2" to="net.SW" />
    <trace from=".U2 > .SW1" to="net.SW" />
    <trace from=".U2 > .SW2" to="net.SW" />
    <trace from=".Cbtst > .pin1" to=".U2 > .BTST" />
    <trace from=".Cbtst > .pin2" to="net.SW" /> {/* bootstrap 47nF SW->BTST */}
    {/* REGN gate-drive LDO */}
    <trace from=".Cregn > .pin1" to=".U2 > .REGN" />
    <trace from=".Cregn > .pin2" to="net.GND" />
    {/* SNS = charge-current-sense / boost-output pad: ONLY the 44uF cap to GND here.
        The SNS<->BAT shunt is INTERNAL (ICHG set over I2C); tying SNS to BAT externally
        shorts the sense element and defeats charge-current regulation — SNS is its own net. */}
    <trace from=".Csns > .pin1" to="net.SNS" />
    <trace from=".Csns > .pin2" to="net.GND" />
    <trace from=".U2 > .SNS1" to="net.SNS" />
    <trace from=".U2 > .SNS2" to="net.SNS" />
    {/* BAT power connection + decoupling */}
    <trace from=".U2 > .BAT1" to="net.BAT" />
    <trace from=".U2 > .BAT2" to="net.BAT" />
    <trace from=".Cbat > .pin1" to="net.BAT" />
    <trace from=".Cbat > .pin2" to="net.GND" />
    {/* GND pins + thermal pad */}
    <trace from=".U2 > .GND1" to="net.GND" />
    <trace from=".U2 > .GND2" to="net.GND" />
    <trace from=".U2 > .EP" to="net.GND" /> {/* exposed thermal pad -> GND (layout critical) */}
    {/* ILIM input current limit */}
    <trace from=".Rilim > .pin1" to=".U2 > .ILIM" />
    <trace from=".Rilim > .pin2" to="net.GND" />
    {/* PSEL LOW -> 3.0 A adapter mode */}
    <trace from=".U2 > .PSEL" to="net.GND" />
    {/* cell mid: MID sense (300R) + CBSET balance (10R) to BATM */}
    <trace from=".Rmid > .pin1" to=".U2 > .MID" />
    <trace from=".Rmid > .pin2" to="net.BATM" />
    <trace from=".Rcbset > .pin1" to=".U2 > .CBSET" />
    <trace from=".Rcbset > .pin2" to="net.BATM" />
    {/* TS: REGN -> Rts_top -> TS -> RT1(NTC) -> GND */}
    <trace from=".Rts_top > .pin1" to=".U2 > .REGN" />
    <trace from=".Rts_top > .pin2" to="net.TS" />
    <trace from=".U2 > .TS" to="net.TS" />
    <trace from=".RT1 > .pin1" to="net.TS" />
    <trace from=".RT1 > .pin2" to="net.GND" />
    <trace from=".RT2 > .pin1" to="net.TS" />
    <trace from=".RT2 > .pin2" to="net.GND" />
    {/* control + I2C */}
    <trace from=".U2 > .SDA" to="net.I2C_SDA" />
    <trace from=".U2 > .SCL" to="net.I2C_SCL" />
    <trace from=".U2 > .CD" to="net.BQ_CD" />
    <trace from=".U2 > .INT" to="net.BQ_INT" />
    {/* PG, STAT: open-drain indicators, unused -> left unconnected (INT carries status) */}

    {/* --- Pack + protection (S-8252A, common-drain low-side FETs) --- */}
    <trace from=".BT1 > .P_PLUS" to=".F1 > .pin1" />
    <trace from=".F1 > .pin2" to=".SW1 > .pin2" /> {/* fuse out -> SPDT COM (pin2) */}
    <trace from=".SW1 > .pin1" to="net.BAT" /> {/* SPDT throw (pin1) -> BAT rail (pin3 NC) */}
    <trace from=".BT1 > .MID" to="net.BATM" />
    <trace from=".BT1 > .P_MINUS" to="net.BMINUS" /> {/* B- (bottom of stack) */}
    {/* S-8252A: VDD=B+ via R1, VC=mid via R2, VSS=B-, VM=EB-/GND via R3 */}
    <trace from=".Rvdd > .pin1" to=".U3 > .VDD" />
    <trace from=".Rvdd > .pin2" to="net.BAT" /> {/* VDD senses B+ (BAT rail) */}
    <trace from=".Rvc > .pin1" to=".U3 > .VC" />
    <trace from=".Rvc > .pin2" to="net.BATM" />
    <trace from=".U3 > .VSS" to="net.BMINUS" /> {/* VSS = B- (battery negative) */}
    <trace from=".Rvm > .pin1" to=".U3 > .VM" />
    <trace from=".Rvm > .pin2" to="net.GND" /> {/* VM senses EB- = system GND */}
    <trace from=".Cvdd > .pin1" to=".U3 > .VDD" />
    <trace from=".Cvdd > .pin2" to=".U3 > .VSS" />
    <trace from=".Cvc > .pin1" to=".U3 > .VC" />
    <trace from=".Cvc > .pin2" to=".U3 > .VSS" />
    {/* FETs common-drain: Q1 discharge (S=B-), Q2 charge (S=GND), drains=PACKMID */}
    <trace from=".U3 > .DO" to=".Q1 > .G" />
    <trace from=".U3 > .CO" to=".Q2 > .G" />
    <trace from=".Q1 > .S" to="net.BMINUS" />
    <trace from=".Q1 > .D" to="net.PACKMID" />
    <trace from=".Q2 > .S" to="net.GND" />
    <trace from=".Q2 > .D" to="net.PACKMID" />

    {/* --- +5V buck (MP2315 U4) --- */}
    <trace from=".U4 > .IN" to="net.BAT" />
    <trace from=".Cin5 > .pin1" to="net.BAT" />
    <trace from=".Cin5 > .pin2" to="net.GND" />
    <trace from=".U4 > .GND" to="net.GND" />
    <trace from=".U4 > .SW" to=".L2 > .pin1" />
    <trace from=".Cbst4 > .pin1" to=".U4 > .BST" />
    <trace from=".Cbst4 > .pin2" to=".Rbst4 > .pin1" />
    <trace from=".Rbst4 > .pin2" to=".U4 > .SW" />
    <trace from=".L2 > .pin2" to="net.V5" />
    <trace from=".Cout5 > .pin1" to="net.V5" />
    <trace from=".Cout5 > .pin2" to="net.GND" />
    <trace from=".R1 > .pin1" to="net.V5" />
    <trace from=".R1 > .pin2" to=".U4 > .FB" />
    <trace from=".R2 > .pin1" to=".U4 > .FB" />
    <trace from=".R2 > .pin2" to="net.GND" />
    <trace from=".U4 > .pin6" to="net.RAIL_EN_5V" /> {/* pin6 = EN */}
    <trace from=".R_RE5 > .pin1" to="net.RAIL_EN_5V" />
    <trace from=".R_RE5 > .pin2" to="net.GND" />
    <trace from=".Cvcc4 > .pin1" to=".U4 > .VCC" />
    <trace from=".Cvcc4 > .pin2" to="net.GND" />
    <trace from=".Raam4 > .pin1" to=".U4 > .AAM" />
    <trace from=".Raam4 > .pin2" to="net.GND" />

    {/* --- +3V3 buck (MP2315 U5, wide Vin on BAT) --- */}
    <trace from=".U5 > .IN" to="net.BAT" />
    <trace from=".Cin3 > .pin1" to="net.BAT" />
    <trace from=".Cin3 > .pin2" to="net.GND" />
    <trace from=".U5 > .GND" to="net.GND" />
    <trace from=".U5 > .SW" to=".L3 > .pin1" />
    <trace from=".Cbst5 > .pin1" to=".U5 > .BST" />
    <trace from=".Cbst5 > .pin2" to=".Rbst5 > .pin1" />
    <trace from=".Rbst5 > .pin2" to=".U5 > .SW" />
    <trace from=".L3 > .pin2" to="net.V3V3" />
    <trace from=".Cout3 > .pin1" to="net.V3V3" />
    <trace from=".Cout3 > .pin2" to="net.GND" />
    <trace from=".R3 > .pin1" to="net.V3V3" />
    <trace from=".R3 > .pin2" to=".U5 > .FB" />
    <trace from=".R4 > .pin1" to=".U5 > .FB" />
    <trace from=".R4 > .pin2" to="net.GND" />
    {/* EN auto-on via divider from BAT (safe level, never raw 8.4 V) */}
    <trace from=".R_EN3H > .pin1" to="net.BAT" />
    <trace from=".R_EN3H > .pin2" to=".U5 > .pin6" /> {/* pin6 = EN */}
    <trace from=".R_EN3L > .pin1" to=".U5 > .pin6" />
    <trace from=".R_EN3L > .pin2" to="net.GND" />
    <trace from=".Cvcc5 > .pin1" to=".U5 > .VCC" />
    <trace from=".Cvcc5 > .pin2" to="net.GND" />
    <trace from=".Raam5 > .pin1" to=".U5 > .AAM" />
    <trace from=".Raam5 > .pin2" to="net.GND" />

    {/* --- +3V3A LDO from +5V (TPS7A2033 U6) --- */}
    <trace from=".U6 > .IN" to="net.V5" />
    <trace from=".Cin3a > .pin1" to="net.V5" />
    <trace from=".Cin3a > .pin2" to="net.GND" />
    <trace from=".U6 > .GND" to="net.GND" />
    <trace from=".U6 > .OUT" to="net.V3V3A" />
    <trace from=".Cout3a > .pin1" to="net.V3V3A" />
    <trace from=".Cout3a > .pin2" to="net.GND" />
    <trace from=".U6 > .EN" to="net.RAIL_EN_3V3A" />
    <trace from=".R_RE3A > .pin1" to="net.RAIL_EN_3V3A" />
    <trace from=".R_RE3A > .pin2" to="net.GND" />
  

    {/* ================= SHEET 2 - MCU + BUSES ================= */}

    {/* ===================== U10 — ESP32-S3-WROOM-1U-N8R2 (main brain) ===================== */}
    <chip name="U10" footprint="jlcpcb:C3013944" />

    {/* ===================== m_U20 — ESP32-C5-WROOM-1U (co-processor) ===================== */}
    <chip name="m_U20" footprint="jlcpcb:C49308183" />

    {/* ===================== U11 — 74HC138 3->8 chip-select decoder ===================== */}
    <chip name="U11" footprint="jlcpcb:C157527" />

    {/* ===================== U12 — PCA9555 #1 (0x20) radio/display control ===================== */}
    <chip name="U12" footprint="jlcpcb:C128392" />

    {/* ===================== U13 — PCA9555 #2 (0x21) user I/O + power gating + SP4T ===================== */}
    <chip name="U13" footprint="jlcpcb:C128392" />

    {/* I2C pull-ups live on Sheet 5 (single pair R40/R41 for the whole bus) */}
    <resistor name="R_C5BOOT" resistance="10k" footprint="0402" />
    <resistor name="R_C5S27" resistance="10k" footprint="0402" />
    <resistor name="R_HC138EN" resistance="10k" footprint="0402" />
    <resistor name="R_C5EN" resistance="10k" footprint="0402" />
    <capacitor name="C_C5EN" capacitance="1uF" footprint="0402" />

    {/* ============================== NETS ============================== */}
    {/* --- S3 direct GPIO -> bus/rail labels (pad = IO<gpio>) --- */}
    <trace from=".U10 > .IO0" to="net.S3_BOOT" />       {/* GPIO0 */}
    <trace from=".U10 > .IO1" to="net.WS2812" />        {/* GPIO1 */}
    <trace from=".U10 > .IO2" to="net.IR_TX" />         {/* GPIO2 */}
    <trace from=".U10 > .IO3" to="net.LoRa_DIO1" />     {/* GPIO3 */}
    <trace from=".U10 > .IO4" to="net.I2C_SDA" />       {/* GPIO4 */}
    <trace from=".U10 > .IO5" to="net.I2C_SCL" />       {/* GPIO5 */}
    <trace from=".U10 > .IO6" to="net.nRF24_CE" />      {/* GPIO6 */}
    <trace from=".U10 > .IO7" to="net.CC1101_GDO0" />   {/* GPIO7 */}
    <trace from=".U10 > .IO8" to="net.HC138_A" />       {/* GPIO8 */}
    <trace from=".U10 > .IO9" to="net.HC138_B" />       {/* GPIO9 */}
    <trace from=".U10 > .IO10" to="net.HC138_C" />      {/* GPIO10 */}
    <trace from=".U10 > .IO11" to="net.SPI_MOSI" />     {/* GPIO11 */}
    <trace from=".U10 > .IO12" to="net.SPI_SCK" />      {/* GPIO12 */}
    <trace from=".U10 > .IO13" to="net.SPI_MISO" />     {/* GPIO13 */}
    <trace from=".U10 > .IO14" to="net.LCD_DC" />       {/* GPIO14 */}
    <trace from=".U10 > .IO15" to="net.LoRa_BUSY" />    {/* GPIO15 */}
    <trace from=".U10 > .IO16" to="net.SA868_UART_TX" />{/* GPIO16 */}
    <trace from=".U10 > .IO17" to="net.SA868_UART_RX" />{/* GPIO17 */}
    <trace from=".U10 > .IO18" to="net.GPS_UART_RX" />  {/* GPIO18 */}
    <trace from=".U10 > .IO19" to="net.USB_DM_S3" />    {/* GPIO19 */}
    <trace from=".U10 > .IO20" to="net.USB_DP_S3" />    {/* GPIO20 */}
    <trace from=".U10 > .IO21" to="net.LCD_TE" />       {/* GPIO21 */}
    {/* GPIO33 C5_EN / GPIO34 C5_BOOT are NOT bonded out on the WROOM-1U module — relocated
       to PCA9555 #2 (U13.P05/P06); see the C5-control block below and the header note. */}
    <trace from=".U10 > .IO35" to="net.C5LINK_SCK" />   {/* GPIO35 */}
    <trace from=".U10 > .IO36" to="net.C5LINK_MOSI" />  {/* GPIO36 */}
    <trace from=".U10 > .IO37" to="net.C5LINK_MISO" />  {/* GPIO37 */}
    <trace from=".U10 > .IO38" to="net.C5LINK_CS" />    {/* GPIO38 */}
    <trace from=".U10 > .IO39" to="net.C5LINK_DRDY" />  {/* GPIO39 */}
    <trace from=".U10 > .IO40" to="net.ENC_A" />        {/* GPIO40 */}
    <trace from=".U10 > .IO41" to="net.ENC_B" />        {/* GPIO41 */}
    <trace from=".U10 > .IO42" to="net.IR_RX" />        {/* GPIO42 */}
    {/* TXD0(GPIO43)/RXD0(GPIO44) -> C5 flash bridge, wired in the flash-bridge block below */}
    <trace from=".U10 > .IO45" to="net.CC1101_GDO2" />  {/* GPIO45 = VDD_SPI strap; de-strapped by the eFuse `espefuse set_flash_voltage 3.3V` (production step, see power.md) so CC1101 GDO2 driving it HIGH at POR is harmless */}
    <trace from=".U10 > .IO46" to="net.nRF24_IRQ" />    {/* GPIO46 */}
    <trace from=".U10 > .IO47" to="net.GPS_UART_TX" />  {/* GPIO47 */}
    <trace from=".U10 > .IO48" to="net.PCA9555_INT" />  {/* GPIO48 */}
    <trace from=".U10 > .3V3" to="net.V3V3" />
    <trace from=".U10 > .EN" to="net.S3_EN" />
    {/* all module GND pads + EP thermal copies -> GND */}
    <trace from=".U10 > .GND1" to="net.GND" />
    <trace from=".U10 > .GND2" to="net.GND" />
    <trace from=".U10 > .GND3" to="net.GND" />
    <trace from=".U10 > .GND4" to="net.GND" />
    <trace from=".U10 > .GND5" to="net.GND" />
    <trace from=".U10 > .GND6" to="net.GND" />
    <trace from=".U10 > .GND7" to="net.GND" />
    <trace from=".U10 > .GND8" to="net.GND" />
    <trace from=".U10 > .GND9" to="net.GND" />
    <trace from=".U10 > .GND10" to="net.GND" />
    <trace from=".U10 > .GND11" to="net.GND" />

    {/* --- S3 <-> C5 dedicated SPI3 link (via nets) --- */}
    <trace from=".m_U20 > .IO23" to="net.C5LINK_SCK" />   {/* C5 GPIO23 LINK_SCK */}
    <trace from=".m_U20 > .IO24" to="net.C5LINK_MOSI" />  {/* C5 GPIO24 LINK_MOSI */}
    <trace from=".m_U20 > .IO6" to="net.C5LINK_MISO" />   {/* C5 GPIO6 LINK_MISO */}
    <trace from=".m_U20 > .IO8" to="net.C5LINK_CS" />     {/* C5 GPIO8 LINK_CS */}
    <trace from=".m_U20 > .IO9" to="net.C5LINK_DRDY" />   {/* C5 GPIO9 DRDY */}
    <trace from=".m_U20 > .EN" to="net.C5_EN" />          {/* C5 EN pad */}
    <trace from=".R_C5EN > .pin1" to="net.C5_EN" />
    <trace from=".R_C5EN > .pin2" to="net.V3V3" />
    <trace from=".C_C5EN > .pin1" to="net.C5_EN" />
    <trace from=".C_C5EN > .pin2" to="net.GND" />
    <trace from=".m_U20 > .IO26" to="net.C5_BOOT" />      {/* C5 GPIO26 (download strap) */}
    <trace from=".m_U20 > .IO28" to="net.C5_BOOT" />      {/* C5 GPIO28 (tied to 26) */}
    <trace from=".R_C5BOOT > .pin1" to="net.C5_BOOT" />
    <trace from=".R_C5BOOT > .pin2" to="net.V3V3" />
    <trace from=".m_U20 > .IO27" to=".R_C5S27 > .pin1" /> {/* C5 GPIO27 strap pull-high */}
    <trace from=".R_C5S27 > .pin2" to="net.V3V3" />

    {/* --- S3 <-> C5 flash bridge UART0 --- */}
    <trace from=".U10 > .TXD0" to="net.C5_FLASH_TX" />
    <trace from=".m_U20 > .RX0" to="net.C5_FLASH_TX" />   {/* C5 U0RXD (GPIO12) */}
    <trace from=".U10 > .RXD0" to="net.C5_FLASH_RX" />
    <trace from=".m_U20 > .TX0" to="net.C5_FLASH_RX" />   {/* C5 U0TXD (GPIO11) */}

    {/* --- C5 own USB-C (data-only, Sheet 1) --- */}
    <trace from=".m_U20 > .IO13" to="net.USB_DM_C5" />    {/* C5 GPIO13 */}
    <trace from=".m_U20 > .IO14" to="net.USB_DP_C5" />    {/* C5 GPIO14 */}
    <trace from=".m_U20 > .3V3" to="net.V3V3" />
    {/* all C5 module GND pads + EP thermal copies -> GND */}
    <trace from=".m_U20 > .GND1" to="net.GND" />
    <trace from=".m_U20 > .GND2" to="net.GND" />
    <trace from=".m_U20 > .GND3" to="net.GND" />
    <trace from=".m_U20 > .GND4" to="net.GND" />
    <trace from=".m_U20 > .GND5" to="net.GND" />
    <trace from=".m_U20 > .GND6" to="net.GND" />
    <trace from=".m_U20 > .GND7" to="net.GND" />
    <trace from=".m_U20 > .GND8" to="net.GND" />
    <trace from=".m_U20 > .GND9" to="net.GND" />
    <trace from=".m_U20 > .GND10" to="net.GND" />
    <trace from=".m_U20 > .GND11" to="net.GND" />
    <trace from=".m_U20 > .GND12" to="net.GND" />
    <trace from=".m_U20 > .GND13" to="net.GND" />
    {/* ANT2 (u.FL antenna feed) left for RF sheet; NC1/NC2 unused */}

    {/* --- 74HC138 decoder --- */}
    <trace from=".U11 > .A" to="net.HC138_A" />
    <trace from=".U11 > .B" to="net.HC138_B" />
    <trace from=".U11 > .C" to="net.HC138_C" />
    <trace from=".U11 > .G1" to="net.V3V3" />
    <trace from=".U11 > .pin5" to="net.GND" />          {/* #G2B */}
    <trace from=".U11 > .pin4" to="net.HC138_EN" />     {/* #G2A */}
    <trace from=".U11 > .VCC" to="net.V3V3" />
    <trace from=".U11 > .GND" to="net.GND" />
    <trace from=".U11 > .Y0" to="net.SD_CS" />
    <trace from=".U11 > .Y1" to="net.CC1101_CS" />
    <trace from=".U11 > .Y2" to="net.nRF24_1_CSN" />
    <trace from=".U11 > .Y3" to="net.nRF24_2_CSN" />
    <trace from=".U11 > .Y4" to="net.nRF24_3_CSN" />
    <trace from=".U11 > .Y5" to="net.LoRa_NSS" />
    <trace from=".U11 > .Y6" to="net.LCD_CS" />
    {/* Y7 = deselect-all address, no chip; left unconnected */}
    <trace from=".R_HC138EN > .pin1" to="net.HC138_EN" />
    <trace from=".R_HC138EN > .pin2" to="net.V3V3" />

    {/* --- PCA9555 #1 (0x20) --- */}
    <trace from=".U12 > .SDA" to="net.I2C_SDA" />
    <trace from=".U12 > .SCL" to="net.I2C_SCL" />
    <trace from=".U12 > .INT" to="net.PCA9555_INT" />
    <trace from=".U12 > .VDD" to="net.V3V3" />
    <trace from=".U12 > .VSS" to="net.GND" />
    <trace from=".U12 > .A0" to="net.GND" />
    <trace from=".U12 > .A1" to="net.GND" />
    <trace from=".U12 > .A2" to="net.GND" />
    <trace from=".U12 > .IO0_0" to="net.ENC_SW" />
    <trace from=".U12 > .IO0_1" to="net.SA868_PTT" />
    <trace from=".U12 > .IO0_2" to="net.SA868_PD" />
    <trace from=".U12 > .IO0_3" to="net.Si4732_RST" />
    <trace from=".U12 > .IO0_4" to="net.LoRa_NRESET" />
    <trace from=".U12 > .IO0_5" to="net.BUZZER" />
    <trace from=".U12 > .IO0_6" to="net.LCD_RESX" />
    <trace from=".U12 > .IO0_7" to="net.MUX_SEL" />
    <trace from=".U12 > .IO1_0" to="net.BQ_INT" />
    <trace from=".U12 > .IO1_1" to="net.BQ_CD" />
    <trace from=".U12 > .IO1_2" to="net.LoRa_TR" />
    <trace from=".U12 > .IO1_3" to="net.PAM_SD" />
    <trace from=".U12 > .IO1_4" to="net.LCD_BL_EN" />
    <trace from=".U12 > .IO1_5" to="net.RFSW_A" />
    <trace from=".U12 > .IO1_6" to="net.HC138_EN" />
    <trace from=".U12 > .IO1_7" to="net.SD_CD" />

    {/* --- PCA9555 #2 (0x21) --- */}
    <trace from=".U13 > .SDA" to="net.I2C_SDA" />
    <trace from=".U13 > .SCL" to="net.I2C_SCL" />
    <trace from=".U13 > .INT" to="net.PCA9555_INT" />
    <trace from=".U13 > .VDD" to="net.V3V3" />
    <trace from=".U13 > .VSS" to="net.GND" />
    <trace from=".U13 > .A0" to="net.V3V3" />
    <trace from=".U13 > .A1" to="net.GND" />
    <trace from=".U13 > .A2" to="net.GND" />
    <trace from=".U13 > .IO0_0" to="net.PTT_BTN" />
    <trace from=".U13 > .IO0_1" to="net.RAIL_EN_5V" />
    <trace from=".U13 > .IO0_2" to="net.RAIL_EN_3V3A" />
    <trace from=".U13 > .IO0_3" to="net.JACK_DET" />
    <trace from=".U13 > .IO0_4" to="net.RFSW_B" />
    {/* C5 control relocated here: GPIO33/34 are NOT bonded out on the WROOM-1U module.
        Both are slow, set-once lines; the pull-ups (R_C5EN / R_C5BOOT) hold safe
        power-on defaults regardless of the expander, so I2C-driven control is fine. */}
    <trace from=".U13 > .IO0_5" to="net.C5_EN" />   {/* P05 -> C5 reset/enable */}
    <trace from=".U13 > .IO0_6" to="net.C5_BOOT" /> {/* P06 -> C5 download strap */}
    <trace from=".U13 > .IO0_7" to="net.RFSW_C" />  {/* P07 -> SP4T 3rd select (SKY13414 V3, RF sheet) */}
    {/* P10..P17 spare */}

    {/* --- S3 expander INT input --- */}
    <trace from=".U10 > .IO48" to="net.PCA9555_INT" />
  

    {/* ================= SHEET 3 - RF CHAINS ================= */}

    {/* ===================== 3x nRF24L01+PA/LNA modules (2x4 header placeholder) ===================== */}
    <chip name="rf_U20" footprint="pinrow8_p2.54_doublerow" pinLabels={{
      pin1: "GND", pin2: "VCC", pin3: "CE", pin4: "CSN",
      pin5: "SCK", pin6: "MOSI", pin7: "MISO", pin8: "IRQ",
    }} />
    <chip name="U21" footprint="pinrow8_p2.54_doublerow" pinLabels={{
      pin1: "GND", pin2: "VCC", pin3: "CE", pin4: "CSN",
      pin5: "SCK", pin6: "MOSI", pin7: "MISO", pin8: "IRQ",
    }} />
    <chip name="U22" footprint="pinrow8_p2.54_doublerow" pinLabels={{
      pin1: "GND", pin2: "VCC", pin3: "CE", pin4: "CSN",
      pin5: "SCK", pin6: "MOSI", pin7: "MISO", pin8: "IRQ",
    }} />
    {/* brownout: 150uF bulk + 100nF right at each VCC */}
    <capacitor name="Cb20" capacitance="150uF" footprint="1210" />
    <capacitor name="Cd20" capacitance="100nF" footprint="0402" />
    <capacitor name="Cb21" capacitance="150uF" footprint="1210" />
    <capacitor name="Cd21" capacitance="100nF" footprint="0402" />
    <capacitor name="Cb22" capacitance="150uF" footprint="1210" />
    <capacitor name="Cd22" capacitance="100nF" footprint="0402" />

    {/* ===================== nRF24 IRQ combiner: SN74LVC1G10 3-input NAND ===================== */}
    <chip name="U28" footprint="jlcpcb:C485078" />

    {/* ===================== CC1101 bare IC + 26MHz xtal + balun ===================== */}
    <chip name="U23" footprint="jlcpcb:C29953" />
    <crystal name="rf_Y1" frequency="26MHz" loadCapacitance="10pF" footprint="crystal_3215_2" />
    <capacitor name="Cx1" capacitance="10pF" footprint="0402" />
    <capacitor name="Cx2" capacitance="10pF" footprint="0402" />
    <capacitor name="Cdc" capacitance="100nF" footprint="0402" /> {/* DCOUPL: 1.8V reg bypass to GND */}
    <resistor name="rf_Rbias" resistance="56k" footprint="0402" />   {/* RBIAS: 56k 1% to GND */}
    {/* RF balun proxy: balanced RF_P/RF_N -> single-ended CC1101_RF */}
    <chip name="BL1" footprint="soic6" pinLabels={{
      pin1: "RFP", pin2: "RFN", pin3: "RFSE", pin4: "GND1", pin5: "GND2", pin6: "GND3",
    }} />
    {/* CC1101 local bulk */}
    <capacitor name="Cb23" capacitance="100uF" footprint="1210" />
    <capacitor name="Cd23" capacitance="100nF" footprint="0402" />

    {/* ===================== SP4T SKY13414-485LF + 4x band matches ===================== */}
    {/* In-stock SP4T (C255353). Engine pads: ANT(common), RF1..RF4, V1/V2/V3 (3-line select),
        VDD, EP + unnamed pads = RF ground. Needs RFSW_C (3rd select) — added on PCA9555 #2 P07. */}
    <chip name="U24" footprint="jlcpcb:C255353" />
    {/* per-band matched networks (proxy: one inductor each) */}
    <inductor name="Lm315" inductance="1nH" footprint="0402" />
    <inductor name="Lm433" inductance="1nH" footprint="0402" />
    <inductor name="Lm868" inductance="1nH" footprint="0402" />
    <inductor name="Lm915" inductance="1nH" footprint="0402" />

    {/* ===================== SX1262 / E22-900M22S module (real engine footprint) ===================== */}
    <chip name="U25" footprint="jlcpcb:C411293" />
    <capacitor name="Cb25" capacitance="100uF" footprint="1210" />
    <capacitor name="Cd25" capacitance="100nF" footprint="0402" />
    {/* 74LVC1G04 inverter: complementary RXEN from TXEN(LoRa_TR) */}
    <chip name="U27" footprint="jlcpcb:C7827" />

    {/* ============================== NETS ============================== */}
    {/* --- nRF24 rf_U20 --- */}
    <trace from=".rf_U20 > .GND" to="net.GND" />
    <trace from=".rf_U20 > .VCC" to="net.V3V3" />
    <trace from=".rf_U20 > .CE" to="net.nRF24_CE" />
    <trace from=".rf_U20 > .CSN" to="net.nRF24_1_CSN" />
    <trace from=".rf_U20 > .SCK" to="net.SPI_SCK" />
    <trace from=".rf_U20 > .MOSI" to="net.SPI_MOSI" />
    <trace from=".rf_U20 > .MISO" to="net.SPI_MISO" />
    <trace from=".rf_U20 > .IRQ" to="net.nRF24_1_IRQ" />
    <trace from=".Cb20 > .pin1" to="net.V3V3" />
    <trace from=".Cb20 > .pin2" to="net.GND" />
    <trace from=".Cd20 > .pin1" to="net.V3V3" />
    <trace from=".Cd20 > .pin2" to="net.GND" />
    {/* --- nRF24 U21 --- */}
    <trace from=".U21 > .GND" to="net.GND" />
    <trace from=".U21 > .VCC" to="net.V3V3" />
    <trace from=".U21 > .CE" to="net.nRF24_CE" />
    <trace from=".U21 > .CSN" to="net.nRF24_2_CSN" />
    <trace from=".U21 > .SCK" to="net.SPI_SCK" />
    <trace from=".U21 > .MOSI" to="net.SPI_MOSI" />
    <trace from=".U21 > .MISO" to="net.SPI_MISO" />
    <trace from=".U21 > .IRQ" to="net.nRF24_2_IRQ" />
    <trace from=".Cb21 > .pin1" to="net.V3V3" />
    <trace from=".Cb21 > .pin2" to="net.GND" />
    <trace from=".Cd21 > .pin1" to="net.V3V3" />
    <trace from=".Cd21 > .pin2" to="net.GND" />
    {/* --- nRF24 U22 --- */}
    <trace from=".U22 > .GND" to="net.GND" />
    <trace from=".U22 > .VCC" to="net.V3V3" />
    <trace from=".U22 > .CE" to="net.nRF24_CE" />
    <trace from=".U22 > .CSN" to="net.nRF24_3_CSN" />
    <trace from=".U22 > .SCK" to="net.SPI_SCK" />
    <trace from=".U22 > .MOSI" to="net.SPI_MOSI" />
    <trace from=".U22 > .MISO" to="net.SPI_MISO" />
    <trace from=".U22 > .IRQ" to="net.nRF24_3_IRQ" />
    <trace from=".Cb22 > .pin1" to="net.V3V3" />
    <trace from=".Cb22 > .pin2" to="net.GND" />
    <trace from=".Cd22 > .pin1" to="net.V3V3" />
    <trace from=".Cd22 > .pin2" to="net.GND" />

    {/* --- IRQ combiner (NAND: A/B/C in, Y out) --- */}
    <trace from=".U28 > .A" to="net.nRF24_1_IRQ" />
    <trace from=".U28 > .B" to="net.nRF24_2_IRQ" />
    <trace from=".U28 > .C" to="net.nRF24_3_IRQ" />
    <trace from=".U28 > .Y" to="net.nRF24_IRQ" />
    <trace from=".U28 > .VCC" to="net.V3V3" />
    <trace from=".U28 > .GND" to="net.GND" />

    {/* --- CC1101 (QFN-20 engine pads; pin2=SO/MISO, pin6=GDO0 are engine-unnamed) --- */}
    <trace from=".U23 > .SCLK" to="net.SPI_SCK" />
    <trace from=".U23 > .pin2" to="net.SPI_MISO" />    {/* SO (GDO1) = SPI MISO */}
    <trace from=".U23 > .GDO2" to="net.CC1101_GDO2" />
    <trace from=".U23 > .DVDD" to="net.V3V3" />
    <trace from=".U23 > .pin6" to="net.CC1101_GDO0" /> {/* GDO0 */}
    <trace from=".U23 > .CSn" to="net.CC1101_CS" />
    <trace from=".U23 > .AVDD1" to="net.V3V3" />
    <trace from=".U23 > .AVDD2" to="net.V3V3" />
    <trace from=".U23 > .AVDD3" to="net.V3V3" />
    <trace from=".U23 > .AVDD4" to="net.V3V3" />
    <trace from=".U23 > .DGUARD" to="net.V3V3" />      {/* digital I/O guard supply */}
    <trace from=".U23 > .SI" to="net.SPI_MOSI" />
    <trace from=".U23 > .GND1" to="net.GND" />
    <trace from=".U23 > .GND2" to="net.GND" />
    <trace from=".U23 > .EP" to="net.GND" />
    <trace from=".U23 > .RF_P" to=".BL1 > .RFP" />
    <trace from=".U23 > .RF_N" to=".BL1 > .RFN" />
    <trace from=".U23 > .XOSC_Q1" to=".rf_Y1 > .pin1" />
    <trace from=".U23 > .XOSC_Q2" to=".rf_Y1 > .pin2" />
    <trace from=".Cx1 > .pin1" to=".rf_Y1 > .pin1" />
    <trace from=".Cx1 > .pin2" to="net.GND" />
    <trace from=".Cx2 > .pin1" to=".rf_Y1 > .pin2" />
    <trace from=".Cx2 > .pin2" to="net.GND" />
    <trace from=".U23 > .DCOUPL" to=".Cdc > .pin1" />  {/* 1.8V reg bypass, cap to GND */}
    <trace from=".Cdc > .pin2" to="net.GND" />
    <trace from=".U23 > .RBIAS" to=".rf_Rbias > .pin1" />
    <trace from=".rf_Rbias > .pin2" to="net.GND" />
    <trace from=".BL1 > .GND1" to="net.GND" />
    <trace from=".BL1 > .GND2" to="net.GND" />
    <trace from=".BL1 > .GND3" to="net.GND" />
    <trace from=".BL1 > .RFSE" to="net.CC1101_RF" />
    <trace from=".Cb23 > .pin1" to="net.V3V3" />
    <trace from=".Cb23 > .pin2" to="net.GND" />
    <trace from=".Cd23 > .pin1" to="net.V3V3" />
    <trace from=".Cd23 > .pin2" to="net.GND" />

    {/* --- SP4T band switch (SKY13414): common ANT -> CC1101 radio, 4 throws -> per-band matches --- */}
    <trace from=".U24 > .ANT" to="net.CC1101_RF" />    {/* switch common -> CC1101 RF_P/N (via balun) */}
    <trace from=".U24 > .V1" to="net.RFSW_A" />
    <trace from=".U24 > .V2" to="net.RFSW_B" />
    <trace from=".U24 > .V3" to="net.RFSW_C" />        {/* 3rd select -> PCA9555 #2 P07 (Sheet 2) */}
    <trace from=".U24 > .VDD" to="net.V3V3" />
    {/* EP + unnamed pads = RF ground (⚠ confirm ground pinout vs SKY13414 datasheet at layout) */}
    <trace from=".U24 > .EP" to="net.GND" />
    {/* pins 1/8/11/12/14 are N/C per the SKY13414 datasheet (the Skyworks EVB leaves them
        floating) — left unconnected, only the EP paddle is the RF ground. */}
    <trace from=".U24 > .RF1" to=".Lm315 > .pin1" />
    <trace from=".Lm315 > .pin2" to="net.ANT_CC1101" />
    <trace from=".U24 > .RF2" to=".Lm433 > .pin1" />
    <trace from=".Lm433 > .pin2" to="net.ANT_CC1101" />
    <trace from=".U24 > .RF3" to=".Lm868 > .pin1" />
    <trace from=".Lm868 > .pin2" to="net.ANT_CC1101" />
    <trace from=".U24 > .RF4" to=".Lm915 > .pin1" />
    <trace from=".Lm915 > .pin2" to="net.ANT_CC1101" />

    {/* --- SX1262 / E22 (real engine pads) --- */}
    <trace from=".U25 > .VCC" to="net.V3V3" />
    <trace from=".U25 > .GND1" to="net.GND" />
    <trace from=".U25 > .GND2" to="net.GND" />
    <trace from=".U25 > .GND3" to="net.GND" />
    <trace from=".U25 > .GND4" to="net.GND" />
    <trace from=".U25 > .GND5" to="net.GND" />
    <trace from=".U25 > .GND6" to="net.GND" />
    <trace from=".U25 > .GND7" to="net.GND" />
    <trace from=".U25 > .GND8" to="net.GND" />
    <trace from=".U25 > .GND9" to="net.GND" />
    <trace from=".U25 > .GND10" to="net.GND" />
    <trace from=".U25 > .NSS" to="net.LoRa_NSS" />
    <trace from=".U25 > .SCK" to="net.SPI_SCK" />
    <trace from=".U25 > .MOSI" to="net.SPI_MOSI" />
    <trace from=".U25 > .MISO" to="net.SPI_MISO" />
    <trace from=".U25 > .BUSY" to="net.LoRa_BUSY" />
    <trace from=".U25 > .DIO1" to="net.LoRa_DIO1" />
    <trace from=".U25 > .NRST" to="net.LoRa_NRESET" />
    <trace from=".U25 > .TXEN" to="net.LoRa_TR" />
    <trace from=".U25 > .RXEN" to="net.LoRa_RXEN" />
    <trace from=".U25 > .ANT" to="net.ANT_LoRa" />
    {/* DIO2 (module T/R helper) unused — RXEN/TXEN driven externally, as in base */}
    <trace from=".Cb25 > .pin1" to="net.V3V3" />
    <trace from=".Cb25 > .pin2" to="net.GND" />
    <trace from=".Cd25 > .pin1" to="net.V3V3" />
    <trace from=".Cd25 > .pin2" to="net.GND" />
    {/* inverter: RXEN = NOT LoRa_TR  (A=in, Y=out; pin1 NC) */}
    <trace from=".U27 > .A" to="net.LoRa_TR" />
    <trace from=".U27 > .Y" to="net.LoRa_RXEN" />
    <trace from=".U27 > .VCC" to="net.V3V3" />
    <trace from=".U27 > .GND" to="net.GND" />
  

    {/* ================= SHEET 4 - AUDIO ================= */}

    {/* ===================== Si4732-A10-GS receiver (U30, all on +3V3A) ===================== */}
    <chip name="U30" footprint="jlcpcb:C1526102" />
    {/* dedicated 32.768 kHz watch crystal + load caps (NOT from MCU) */}
    <chip name="a_Y1" footprint="jlcpcb:C280830" />
    <capacitor name="CL1" capacitance="12pF" footprint="0402" />
    <capacitor name="CL2" capacitance="12pF" footprint="0402" />
    <capacitor name="Cvdd30" capacitance="1uF" footprint="0402" />
    <capacitor name="Cvdd30b" capacitance="100nF" footprint="0402" /> {/* added: VDD HF decap */}
    {/* L+R -> mono summing resistor pair */}
    <resistor name="RsumL" resistance="10k" footprint="0402" />
    <resistor name="RsumR" resistance="10k" footprint="0402" />

    {/* ===================== SA868-U UHF voice walkie (U31, single-supply module) ===================== */}
    <chip name="U31" footprint="jlcpcb:C3001507" />
    {/* local bulk on VBAT for the 2 W PA burst */}
    <capacitor name="Cbulk31" capacitance="330uF" footprint="1210" />
    <capacitor name="Cbyp31" capacitance="100nF" footprint="0402" />
    {/* electret mic + bias -> 1 uF coupling into SA868 MIC (1uF, not 10uF!) */}
    <resistor name="MK1" resistance="2.2k" footprint="0603" /> {/* electret mic proxy */}
    <resistor name="a_Rbias" resistance="4.7k" footprint="0402" />
    <capacitor name="Cmic" capacitance="1uF" footprint="0402" />

    {/* ===================== 2:1 analog mux 74LVC1G3157 (U33) ===================== */}
    <chip name="U33" footprint="jlcpcb:C10426" />

    {/* ===================== PAM8302A class-D amp (U32) ===================== */}
    <chip name="U32" footprint="jlcpcb:C113367" />
    <resistor name="Rin32" resistance="10k" footprint="0402" /> {/* input series R */}
    <capacitor name="Cinp" capacitance="0.1uF" footprint="0402" /> {/* AC-couple IN+ (PAM8302 biases inputs to VDD/2) */}
    <capacitor name="Cinn" capacitance="0.1uF" footprint="0402" /> {/* matching AC-couple on IN- to GND */}
    <capacitor name="Cvcc32" capacitance="10uF" footprint="0805" />

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
    <trace from=".U30 > .RCLK" to=".a_Y1 > .OSC1" />
    <trace from=".a_Y1 > .OSC2" to="net.GND" />
    <trace from=".CL1 > .pin1" to=".U30 > .RCLK" />
    <trace from=".CL1 > .pin2" to="net.GND" />
    <trace from=".CL2 > .pin1" to=".U30 > .RCLK" />
    <trace from=".CL2 > .pin2" to="net.GND" />

    {/* --- Si4732 antennas (off-sheet nets) --- */}
    <trace from=".U30 > .AMI" to="net.ANT_HF_CB" />
    <trace from=".U30 > .FMI" to="net.ANT_FM" />

    {/* --- Si4732 line-out -> summing pair -> mux B1 (pin2=LOUT, pin1=ROUT; L/R interchangeable) --- */}
    <trace from=".U30 > .pin2" to=".RsumL > .pin1" />
    <trace from=".U30 > .pin1" to=".RsumR > .pin1" />
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
    <trace from=".U31 > .ANT" to="net.ANT_UHF" />
    {/* H/L (pin7) left open = high TX power (datasheet default); see gotchas */}

    {/* --- SA868 RX audio -> mux B2 --- */}
    <trace from=".U31 > .AF_OUT" to="net.SA_AF" />
    <trace from=".U33 > .B2" to="net.SA_AF" />

    {/* --- Mic -> 1 uF -> SA868 MIC --- */}
    <trace from=".MK1 > .pin1" to="net.MIC_HOT" />
    <trace from=".MK1 > .pin2" to="net.GND" />
    <trace from=".a_Rbias > .pin1" to="net.V3V3A" />
    <trace from=".a_Rbias > .pin2" to="net.MIC_HOT" />
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
  

    {/* ================= SHEET 5 - EXPANSION + GPS ================= */}

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

    {/* --- RFID2 example unit @0x28 on I2C (external plug-in placeholder) --- */}
    <trace from=".U44 > .V" to="net.V3V3" />
    <trace from=".U44 > .GND" to="net.GND" />
    <trace from=".U44 > .SDA" to="net.I2C_SDA" />
    <trace from=".U44 > .SCL" to="net.I2C_SCL" />
  

    {/* ================= SHEET 6 - INDICATORS & I/O ================= */}

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

    {/* ================= STAGE 1 additions (2026-08-13) ================= */}
    {/* Display FPC + antenna u.FL + full control set + 3rd PCA9555.       */}
    {/* Added to the merged board; back-port to the sheet .tsx files later. */}

    {/* --- Display FPC connector: 4.0" ST7796 320x480 SPI panel (C19273968, 24+2pin 0.5mm) --- */}
    {/* Pinout modelled on a SPI-TFT (+optional I2C touch) FPC; verify vs the chosen module datasheet. */}
    <chip name="J_LCD" footprint="jlcpcb:C19273968" />
    <trace from=".J_LCD > .pin1" to="net.GND" />
    <trace from=".J_LCD > .pin2" to="net.GND" />
    <trace from=".J_LCD > .pin3" to="net.V3V3" />
    <trace from=".J_LCD > .pin4" to="net.V3V3" />
    <trace from=".J_LCD > .pin5" to="net.LCD_CS" />
    <trace from=".J_LCD > .pin6" to="net.LCD_DC" />
    <trace from=".J_LCD > .pin7" to="net.LCD_RESX" />
    <trace from=".J_LCD > .pin8" to="net.SPI_SCK" />
    <trace from=".J_LCD > .pin9" to="net.SPI_MOSI" />
    <trace from=".J_LCD > .pin10" to="net.SPI_MISO" />
    <trace from=".J_LCD > .pin11" to="net.LCD_TE" />
    <trace from=".J_LCD > .pin12" to="net.LCD_BL_EN" />
    <trace from=".J_LCD > .pin13" to="net.GND" />
    {/* pins 14-16 = capacitive-touch INT/SDA/SCL — left NC (optional touch module) */}
    <trace from=".J_LCD > .pin17" to="net.GND" />
    <trace from=".J_LCD > .pin18" to="net.LCD_LEDK" /> {/* backlight cathode -> Stage 3 driver */}
    <trace from=".J_LCD > .pin19" to="net.LCD_LEDK" />
    <trace from=".J_LCD > .pin20" to="net.LCD_LEDA" /> {/* backlight anode -> Stage 3 driver */}
    <trace from=".J_LCD > .pin21" to="net.LCD_LEDA" />
    <trace from=".J_LCD > .pin22" to="net.LCD_LEDA" />
    <trace from=".J_LCD > .pin23" to="net.GND" />
    <trace from=".J_LCD > .pin24" to="net.GND" />
    <trace from=".J_LCD > .pin25" to="net.GND" /> {/* mounting tab */}
    <trace from=".J_LCD > .pin26" to="net.GND" /> {/* mounting tab */}

    {/* --- Antenna u.FL/IPEX connectors (C2987682): pin2 = signal (center), pin1/3/4 = GND shell --- */}
    {/* Only the bare-chip radios need a board u.FL (module radios carry their own). Pigtail -> panel SMA/RP-SMA. */}
    <chip name="J_ANT_CC" footprint="jlcpcb:C2987682" />
    <trace from=".J_ANT_CC > .pin2" to="net.ANT_CC1101" />
    <trace from=".J_ANT_CC > .pin1" to="net.GND" />
    <trace from=".J_ANT_CC > .pin3" to="net.GND" />
    <trace from=".J_ANT_CC > .pin4" to="net.GND" />
    <chip name="J_ANT_UHF" footprint="jlcpcb:C2987682" />
    <trace from=".J_ANT_UHF > .pin2" to="net.ANT_UHF" />
    <trace from=".J_ANT_UHF > .pin1" to="net.GND" />
    <trace from=".J_ANT_UHF > .pin3" to="net.GND" />
    <trace from=".J_ANT_UHF > .pin4" to="net.GND" />
    <chip name="J_ANT_SI" footprint="jlcpcb:C2987682" />
    <trace from=".J_ANT_SI > .pin2" to="net.ANT_FM" /> {/* telescopic whip on the FM input */}
    <trace from=".J_ANT_SI > .pin1" to="net.GND" />
    <trace from=".J_ANT_SI > .pin3" to="net.GND" />
    <trace from=".J_ANT_SI > .pin4" to="net.GND" />
    {/* Si4732 AM/HF (ANT_HF_CB) shares the whip via a coupling cap; value tuned in Stage 2 / on a VNA */}
    <capacitor name="Ccpl_si" capacitance="100pF" footprint="0402" />
    <trace from=".Ccpl_si > .pin1" to="net.ANT_FM" />
    <trace from=".Ccpl_si > .pin2" to="net.ANT_HF_CB" />

    {/* --- 3rd PCA9555 (U14, addr 0x22) for the UI buttons (U13 has only 8 free pins < 10 buttons) --- */}
    <chip name="U14" footprint="jlcpcb:C128392" />
    <capacitor name="Cu14" capacitance="100nF" footprint="0402" />
    <trace from=".Cu14 > .pin1" to="net.V3V3" />
    <trace from=".Cu14 > .pin2" to="net.GND" />
    <trace from=".U14 > .SDA" to="net.I2C_SDA" />
    <trace from=".U14 > .SCL" to="net.I2C_SCL" />
    <trace from=".U14 > .INT" to="net.PCA9555_INT" />
    <trace from=".U14 > .VDD" to="net.V3V3" />
    <trace from=".U14 > .VSS" to="net.GND" />
    <trace from=".U14 > .A0" to="net.GND" />  {/* A2A1A0 = 010 -> 0x22 */}
    <trace from=".U14 > .A1" to="net.V3V3" />
    <trace from=".U14 > .A2" to="net.GND" />

    {/* --- UI buttons (C318884 tactile: signal=pin1, GND=pin2; pins 3/4 are mechanical anchors) --- */}
    {/* D-pad = 5 tactiles for now (UP/DN/LF/RT/OK); swap to a single 5-way nav switch in Stage 2. */}
    <chip name="SW_UP" footprint="jlcpcb:C318884" />
    <trace from=".SW_UP > .pin1" to=".U14 > .IO0_0" />
    <trace from=".SW_UP > .pin2" to="net.GND" />
    <chip name="SW_DN" footprint="jlcpcb:C318884" />
    <trace from=".SW_DN > .pin1" to=".U14 > .IO0_1" />
    <trace from=".SW_DN > .pin2" to="net.GND" />
    <chip name="SW_LF" footprint="jlcpcb:C318884" />
    <trace from=".SW_LF > .pin1" to=".U14 > .IO0_2" />
    <trace from=".SW_LF > .pin2" to="net.GND" />
    <chip name="SW_RT" footprint="jlcpcb:C318884" />
    <trace from=".SW_RT > .pin1" to=".U14 > .IO0_3" />
    <trace from=".SW_RT > .pin2" to="net.GND" />
    <chip name="SW_OK" footprint="jlcpcb:C318884" />
    <trace from=".SW_OK > .pin1" to=".U14 > .IO0_4" />
    <trace from=".SW_OK > .pin2" to="net.GND" />
    <chip name="SW_BACK" footprint="jlcpcb:C318884" />
    <trace from=".SW_BACK > .pin1" to=".U14 > .IO0_5" />
    <trace from=".SW_BACK > .pin2" to="net.GND" />
    <chip name="SW_OPT" footprint="jlcpcb:C318884" />
    <trace from=".SW_OPT > .pin1" to=".U14 > .IO0_6" />
    <trace from=".SW_OPT > .pin2" to="net.GND" />
    <chip name="SW_STOP" footprint="jlcpcb:C318884" />
    <trace from=".SW_STOP > .pin1" to=".U14 > .IO0_7" />
    <trace from=".SW_STOP > .pin2" to="net.GND" />
    <chip name="SW_F1" footprint="jlcpcb:C318884" />
    <trace from=".SW_F1 > .pin1" to=".U14 > .IO1_0" />
    <trace from=".SW_F1 > .pin2" to="net.GND" />
    <chip name="SW_F2" footprint="jlcpcb:C318884" />
    <trace from=".SW_F2 > .pin1" to=".U14 > .IO1_1" />
    <trace from=".SW_F2 > .pin2" to="net.GND" />


  </board>
)
