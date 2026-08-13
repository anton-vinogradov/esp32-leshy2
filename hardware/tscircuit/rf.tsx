// Leshy2 — Sheet 3: RF chains  (FAB-READY draft, engine-pulled footprints by LCSC number)
//
// METHOD: every real IC/module uses footprint="jlcpcb:C<number>". The parts engine supplies
// the REAL pads AND the REAL pad NAMES from the LCSC/EasyEDA database, so no pin numbers are
// typed by hand for those. Traces reference the engine pad names (verified via
// `tsci export -f readable-netlist`, WITHOUT --disable-parts-engine).
// Placeholders (nRF24 modules, balun) keep explicit pinLabels — same convention as
// BT1 in Sheet 1 — because JLC does not stock a drop-in engine footprint for them.
//
// Pad-name sources of truth (engine probe of each footprint):
//   U23  CC1101RGPR  QFN-20-EP(4x4)   -> jlcpcb:C29953
//        Pads: 1 SCLK, 2 (SO/GDO1, unnamed -> .pin2), 3 GDO2, 4 DVDD, 5 DCOUPL, 6 (GDO0,
//        unnamed -> .pin6), 7 CSn, 8 XOSC_Q1, 9 AVDD1, 10 XOSC_Q2, 11 AVDD2, 12 RF_P,
//        13 RF_N, 14 AVDD3, 15 AVDD4, 16 GND1, 17 RBIAS, 18 DGUARD, 19 GND2, 20 SI, 21 EP.
//        (SWRS061 ref design: all AVDDx+DVDD -> VDD; DCOUPL = 100nF to GND (1.8V reg out,
//        no external load); RBIAS = 56k 1% to GND; DGUARD = digital supply (VDD); EP -> GND.)
//   U25  E22-900M22S (SX1262)  22-pad SMD  -> jlcpcb:C411293
//        Pads: 1-5 GND1-5, 6 RXEN, 7 TXEN, 8 DIO2, 9 VCC, 10-12 GND6-8, 13 DIO1, 14 BUSY,
//        15 NRST, 16 MISO, 17 MOSI, 18 SCK, 19 NSS, 20 GND9, 21 ANT, 22 GND10.
//        (Real module footprint resolves -> used instead of a header placeholder. DIO2 is a
//        module-internal T/R line we do not use here — base drives RXEN/TXEN externally.)
//   U27  SN74LVC1G04DBVR  SOT-23-5  -> jlcpcb:C7827   (inverter: RXEN = NOT LoRa_TR)
//        Pads: 1 (NC, unnamed), 2 A(in), 3 GND, 4 Y(out), 5 VCC.
//   U28  SN74LVC1G10DCKR  SC70-6  -> jlcpcb:C485078   (single 3-input NAND, nRF24 IRQ combiner)
//        Pads: 1 A, 2 GND, 3 B, 4 Y, 5 VCC, 6 C.
//        LOGIC: IRQs are active-LOW push-pull; NAND gives OUT = NOT(A&B&C): all idle-high ->
//        OUT LOW (satisfies GPIO46 POR strap), any radio asserts low -> OUT HIGH (interrupt).
//        (Base said "74AHC 3-input gate"; the idle-LOW spec forces a NAND, not a NOR.)
//
// Placeholders (footprint is geometric, NOT engine — every pad is connected so DRC stays clean):
//   U20/U21/U22  nRF24L01+PA/LNA module  -> pinrow8_p2.54_doublerow (2x4 2.54mm header posadka).
//        No SMD JLC part exists for the shielded PA/LNA module (own antenna/SMA). Header pads
//        pin1..pin8 mapped to the module's 2x4 order: 1 GND,2 VCC,3 CE,4 CSN,5 SCK,6 MOSI,
//        7 MISO,8 IRQ.  ** placeholder footprint — swap for the real module land before fab **
//   U24  SP4T RF switch SKY13414-485LF (315/433/868/915 band fold) -> jlcpcb:C255353 (in stock).
//        Chosen over PE42440 (not stocked at JLC). 3-line control V1/V2/V3 = RFSW_A/RFSW_B/RFSW_C;
//        RFSW_C is added on PCA9555 #2 P07 (Sheet 2). Common pad ANT -> CC1101 radio; RF1..RF4 ->
//        per-band matches -> the shared CC1101 antenna. EP paddle = RF ground; the 5 unnamed
//        pads are N/C (datasheet) and left open.
//   BL1  CC1101 RF balun (RF_P/RF_N -> single-ended)  -> soic6 placeholder + pinLabels.
//        Real part is a discrete LC balun/match tuned on a VNA; modelled as a 4-net proxy.
//
// Net names are unchanged from the base sheet. Antenna ends (ANT_CC1101 via SP4T, ANT_LoRa)
// stay single-ended (external SMA/u.FL, tuned by hand) — expected, not a wiring defect.
export default () => (
  <board width="120mm" height="90mm">
    {/* ===================== 3x nRF24L01+PA/LNA modules (2x4 header placeholder) ===================== */}
    <chip name="U20" footprint="pinrow8_p2.54_doublerow" pinLabels={{
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
    <crystal name="Y1" frequency="26MHz" loadCapacitance="10pF" footprint="crystal_3215_2" />
    <capacitor name="Cx1" capacitance="10pF" footprint="0402" />
    <capacitor name="Cx2" capacitance="10pF" footprint="0402" />
    <capacitor name="Cdc" capacitance="100nF" footprint="0402" /> {/* DCOUPL: 1.8V reg bypass to GND */}
    <resistor name="Rbias" resistance="56k" footprint="0402" />   {/* RBIAS: 56k 1% to GND */}
    {/* RF balun proxy: balanced RF_P/RF_N -> single-ended CC1101_RF */}
    <chip name="BL1" footprint="soic6" pinLabels={{
      pin1: "RFP", pin2: "RFN", pin3: "RFSE", pin4: "GND1", pin5: "GND2", pin6: "GND3",
    }} />
    {/* CC1101 local bulk */}
    <capacitor name="Cb23" capacitance="100uF" footprint="1210" />
    <capacitor name="Cd23" capacitance="100nF" footprint="0402" />
    {/* CC1101 per-supply-pin 100nF (SWRS061: one close to each of AVDD1-4 / DVDD / DGUARD) + logic-gate bypass (U27/U28) */}
    <capacitor name="Cd23b" capacitance="100nF" footprint="0402" /><trace from=".Cd23b > .pin1" to="net.V3V3" /><trace from=".Cd23b > .pin2" to="net.GND" />
    <capacitor name="Cd23c" capacitance="100nF" footprint="0402" /><trace from=".Cd23c > .pin1" to="net.V3V3" /><trace from=".Cd23c > .pin2" to="net.GND" />
    <capacitor name="Cd23d" capacitance="100nF" footprint="0402" /><trace from=".Cd23d > .pin1" to="net.V3V3" /><trace from=".Cd23d > .pin2" to="net.GND" />
    <capacitor name="Cd27" capacitance="100nF" footprint="0402" /><trace from=".Cd27 > .pin1" to="net.V3V3" /><trace from=".Cd27 > .pin2" to="net.GND" />
    <capacitor name="Cd28" capacitance="100nF" footprint="0402" /><trace from=".Cd28 > .pin1" to="net.V3V3" /><trace from=".Cd28 > .pin2" to="net.GND" />

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
    {/* --- nRF24 U20 --- */}
    <trace from=".U20 > .GND" to="net.GND" />
    <trace from=".U20 > .VCC" to="net.V3V3" />
    <trace from=".U20 > .CE" to="net.nRF24_CE" />
    <trace from=".U20 > .CSN" to="net.nRF24_1_CSN" />
    <trace from=".U20 > .SCK" to="net.SPI_SCK" />
    <trace from=".U20 > .MOSI" to="net.SPI_MOSI" />
    <trace from=".U20 > .MISO" to="net.SPI_MISO" />
    <trace from=".U20 > .IRQ" to="net.nRF24_1_IRQ" />
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
    <trace from=".U23 > .XOSC_Q1" to=".Y1 > .pin1" />
    <trace from=".U23 > .XOSC_Q2" to=".Y1 > .pin2" />
    <trace from=".Cx1 > .pin1" to=".Y1 > .pin1" />
    <trace from=".Cx1 > .pin2" to="net.GND" />
    <trace from=".Cx2 > .pin1" to=".Y1 > .pin2" />
    <trace from=".Cx2 > .pin2" to="net.GND" />
    <trace from=".U23 > .DCOUPL" to=".Cdc > .pin1" />  {/* 1.8V reg bypass, cap to GND */}
    <trace from=".Cdc > .pin2" to="net.GND" />
    <trace from=".U23 > .RBIAS" to=".Rbias > .pin1" />
    <trace from=".Rbias > .pin2" to="net.GND" />
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
  </board>
)
