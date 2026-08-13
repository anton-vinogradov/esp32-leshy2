// Leshy2 — Sheet 1: Power  (FAB-READY, engine-pulled footprints by LCSC number)
//
// METHOD: every IC/connector uses footprint="jlcpcb:C<number>". The parts engine
// supplies the REAL pads AND the REAL pin NAMES from the LCSC/EasyEDA database, so
// no pin numbers are typed by hand. Traces below reference those engine pin names
// (verified via `tsci export -f readable-netlist`, WITHOUT --disable-parts-engine).
//
// Datasheet sources of truth:
//   BQ25887  : TI SLUSD89B. Pin Functions pp.4-5, Block Diagram p.15, Typical
//              Application Figure 69 p.68, Layout p.74.
//              BOOST charger: VBUS(5V) -> QBLK -> PMID -> L -> SW -> QHS -> SNS(out) -> BAT.
//              Cvbus>=1uF, Cpmid 10uF, Cregn 4.7uF, Cbtst 47nF (SW->BTST), Csns 44uF,
//              Cbat 10uF, Rilim 383R, Rmid 300R (MID sense), Rcbset ~10R (cell balance,
//              ICB=VCELLREG/(Rcbset+Rdson)), TS = divider REGN->TS->GND w/ 103AT NTC,
//              PSEL=LOW -> 3.0A adapter mode, thermal pad(EP)->GND.
//   S-8252A  : ABLIC Rev.4.0. Pin table p.8, Connection Example Figure 14 p.22, Table 11.
//              SOT-23-6: 1 DO,2 CO,3 VM,4 VC,5 VDD,6 VSS.
//              VDD=B+ (via R1 470R), VC=cell-mid (via R2 470R), VSS=B- (bottom of stack),
//              VM=EB-/GND (via R3 2k). C1/C2 0.1uF (VDD-VSS, VC-VSS), R1*C1=R2*C2.
//              FETs are COMMON-DRAIN (FS8205 topology): FET1 (gate=DO) source at B-/VSS,
//              FET2 (gate=CO) source at EB-/GND, drains tied together. See report.
//   MP2315   : MPS. TSOT23-8 engine names: 1 AAM,2 IN,3 SW,4 GND,5 BST,7 VCC,8 FB;
//              pin6 = EN (engine leaves it unlabeled -> referenced as .pin6).
//              VCC decouple 0.1uF, AAM resistor->GND, Cbst 100nF (BST->SW).
//   TPS7A2033: TI. SOT-23-5 engine names: 1 IN,2 GND,3 EN,4 NC,5 OUT.
//   USB-C    : 16P receptacle GT-USB-7010ASV. Engine names: VBUS1/2, GND1/2, CC1/2,
//              DP1/DP2, DN1/DN2, SBU1/2, SHELL1..SHELL4 (shield). USB2.0: DP1=DP2, DN1=DN2.
//              (C165948 TYPE-C-31-M-12 also resolves but its shell custom-pads render as
//               NaN in the engine kicad_pcb -> blocks KiCad load; C2988369 renders clean.)
//
// LCSC parts (all resolve via the parts engine):
//   J1/J2 = USB-C 16P GT-USB-7010ASV   -> jlcpcb:C2988369
//   U2    = BQ25887  (VQFN-24 4x4)    -> jlcpcb:C2761614
//   U3    = S-8252AAS-M6T1U (SOT-23-6)-> jlcpcb:C468224
//   Q1/Q2 = AO3400A N-FET (SOT-23)    -> jlcpcb:C20917
//   U4/U5 = MP2315 (TSOT23-8)         -> jlcpcb:C45889
//   U6    = TPS7A2033 (SOT-23-5)      -> jlcpcb:C2862740
//   BT1   = 2S 18650 holder           -> pinrow3 PLACEHOLDER (holder/wires, no LCSC)
export default () => (
  <board width="90mm" height="70mm">
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
    <resistor name="Rcc3" resistance="5.1k" footprint="0402" /> {/* J2 CC1 Rd -> Type-C UFP attach (C5 flash-over-USB, incl. C-to-C) */}
    <resistor name="Rcc4" resistance="5.1k" footprint="0402" /> {/* J2 CC2 Rd */}
    <trace from=".Rcc3 > .pin1" to=".J2 > .CC1" /><trace from=".Rcc3 > .pin2" to="net.GND" />
    <trace from=".Rcc4 > .pin1" to=".J2 > .CC2" /><trace from=".Rcc4 > .pin2" to="net.GND" />

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
  </board>
)
