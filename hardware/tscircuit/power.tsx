// Leshy2 — Sheet 1: Power  (transcribed from hardware/power/power.md)
// NOTE: ICs/connectors are generic <chip> with our logical pinout; real
// footprints/part numbers get assigned before PCB. 2-pin passive-ish parts
// (PPTC fuse, master switch, NTC) are modeled as resistor proxies for capture.
export default () => (
  <board width="90mm" height="70mm">
    {/* ===================== USB-C inputs ===================== */}
    {/* J1 -> S3 : 5 V charge + data */}
    <chip name="J1" footprint="soic8" pinLabels={{
      pin1: "VBUS", pin2: "GND", pin3: "CC1", pin4: "CC2",
      pin5: "DP", pin6: "DM", pin7: "SBU1", pin8: "SBU2",
    }} />
    <resistor name="Rcc1" resistance="5.1k" footprint="0402" />
    <resistor name="Rcc2" resistance="5.1k" footprint="0402" />
    {/* J2 -> C5 : data only, VBUS = ESD stub */}
    <chip name="J2" footprint="soic8" pinLabels={{
      pin1: "VBUS", pin2: "GND", pin3: "CC1", pin4: "CC2",
      pin5: "DP", pin6: "DM", pin7: "SBU1", pin8: "SBU2",
    }} />

    {/* ===================== BQ25887 2S boost charger ===================== */}
    <chip name="U2" footprint="soic16" pinLabels={{
      pin1: "VBUS", pin2: "SW", pin3: "BAT", pin4: "VCELL",
      pin5: "TS", pin6: "SDA", pin7: "SCL", pin8: "CD",
      pin9: "INT", pin10: "GND",
    }} />
    <inductor name="L1" inductance="2.2uH" footprint="1210" />

    {/* ===================== 2S pack + protection ===================== */}
    <chip name="BT1" footprint="soic8" pinLabels={{ pin1: "P_PLUS", pin2: "MID", pin3: "P_MINUS" }} />
    <chip name="U3" footprint="soic8" pinLabels={{ pin1: "VDD", pin2: "VC", pin3: "VM", pin4: "DO", pin5: "CO" }} />
    <chip name="Q1" footprint="soic8" pinLabels={{ pin1: "G1", pin2: "G2", pin3: "D", pin4: "S" }} />
    <resistor name="F1" resistance="0.05" footprint="1210" />  {/* PPTC fuse proxy */}
    <resistor name="SW1" resistance="0.01" footprint="1210" /> {/* master switch proxy */}
    <resistor name="RT1" resistance="10k" footprint="0603" />  {/* NTC to BQ TS */}

    {/* ===================== +5 V buck : MP2315 ===================== */}
    <chip name="U4" footprint="soic8" pinLabels={{
      pin1: "BST", pin2: "IN", pin3: "SW", pin4: "GND",
      pin5: "FB", pin6: "EN", pin7: "SS", pin8: "NC",
    }} />
    <inductor name="L2" inductance="4.7uH" footprint="1210" />
    <capacitor name="Cin5" capacitance="22uF" footprint="0805" />
    <capacitor name="Cout5" capacitance="22uF" footprint="0805" />
    <resistor name="R1" resistance="52.3k" footprint="0402" />
    <resistor name="R2" resistance="10k" footprint="0402" />

    {/* ===================== +3V3 buck : TLV62569 ===================== */}
    <chip name="U5" footprint="soic8" pinLabels={{
      pin1: "SW", pin2: "GND", pin3: "FB", pin4: "EN", pin5: "IN",
    }} />
    <inductor name="L3" inductance="2.2uH" footprint="1210" />
    <capacitor name="Cin3" capacitance="22uF" footprint="0805" />
    <capacitor name="Cout3" capacitance="22uF" footprint="0805" />
    <resistor name="R3" resistance="45.3k" footprint="0402" />
    <resistor name="R4" resistance="10k" footprint="0402" />

    {/* ===================== +3V3A LDO : TPS7A2033 (from +5V) ===================== */}
    <chip name="U6" footprint="soic8" pinLabels={{
      pin1: "IN", pin2: "GND", pin3: "EN", pin4: "OUT", pin5: "NR",
    }} />
    <capacitor name="Cin3a" capacitance="1uF" footprint="0402" />
    <capacitor name="Cout3a" capacitance="2.2uF" footprint="0402" />

    {/* ============================== NETS ============================== */}
    {/* --- USB J1 -> S3 --- */}
    <trace from=".J1 > .VBUS" to="net.VBUS_S3" />
    <trace from=".J1 > .GND" to="net.GND" />
    <trace from=".J1 > .DP" to="net.USB_DP_S3" />
    <trace from=".J1 > .DM" to="net.USB_DM_S3" />
    <trace from=".Rcc1 > .pin1" to=".J1 > .CC1" />
    <trace from=".Rcc1 > .pin2" to="net.GND" />
    <trace from=".Rcc2 > .pin1" to=".J1 > .CC2" />
    <trace from=".Rcc2 > .pin2" to="net.GND" />
    {/* --- USB J2 -> C5 (data only) --- */}
    <trace from=".J2 > .VBUS" to="net.VBUS_C5" />
    <trace from=".J2 > .GND" to="net.GND" />
    <trace from=".J2 > .DP" to="net.USB_DP_C5" />
    <trace from=".J2 > .DM" to="net.USB_DM_C5" />

    {/* --- Charger --- */}
    <trace from=".U2 > .VBUS" to="net.VBUS_S3" />
    <trace from=".U2 > .SW" to=".L1 > .pin1" />
    <trace from=".L1 > .pin2" to="net.BAT" />
    <trace from=".U2 > .BAT" to="net.BAT" />
    <trace from=".U2 > .VCELL" to="net.BATM" />
    <trace from=".U2 > .GND" to="net.GND" />
    <trace from=".U2 > .TS" to="net.TS" />
    <trace from=".U2 > .SDA" to="net.I2C_SDA" />
    <trace from=".U2 > .SCL" to="net.I2C_SCL" />
    <trace from=".U2 > .CD" to="net.BQ_CD" />
    <trace from=".U2 > .INT" to="net.BQ_INT" />
    <trace from=".RT1 > .pin1" to="net.TS" />
    <trace from=".RT1 > .pin2" to="net.GND" />

    {/* --- Pack + protection (low-side FETs) --- */}
    <trace from=".BT1 > .P_PLUS" to=".F1 > .pin1" />
    <trace from=".F1 > .pin2" to=".SW1 > .pin1" />
    <trace from=".SW1 > .pin2" to="net.BAT" />
    <trace from=".BT1 > .MID" to="net.BATM" />
    <trace from=".BT1 > .P_MINUS" to=".Q1 > .D" />
    <trace from=".Q1 > .S" to="net.GND" />
    <trace from=".U3 > .VDD" to="net.BAT" />
    <trace from=".U3 > .VC" to="net.BATM" />
    <trace from=".U3 > .VM" to=".Q1 > .D" />
    <trace from=".U3 > .DO" to=".Q1 > .G1" />
    <trace from=".U3 > .CO" to=".Q1 > .G2" />

    {/* --- +5V buck --- */}
    <trace from=".U4 > .IN" to="net.BAT" />
    <trace from=".Cin5 > .pin1" to="net.BAT" />
    <trace from=".Cin5 > .pin2" to="net.GND" />
    <trace from=".U4 > .GND" to="net.GND" />
    <trace from=".U4 > .SW" to=".L2 > .pin1" />
    <trace from=".L2 > .pin2" to="net.V5" />
    <trace from=".Cout5 > .pin1" to="net.V5" />
    <trace from=".Cout5 > .pin2" to="net.GND" />
    <trace from=".R1 > .pin1" to="net.V5" />
    <trace from=".R1 > .pin2" to=".U4 > .FB" />
    <trace from=".R2 > .pin1" to=".U4 > .FB" />
    <trace from=".R2 > .pin2" to="net.GND" />
    <trace from=".U4 > .EN" to="net.RAIL_EN_5V" />

    {/* --- +3V3 buck --- */}
    <trace from=".U5 > .IN" to="net.BAT" />
    <trace from=".Cin3 > .pin1" to="net.BAT" />
    <trace from=".Cin3 > .pin2" to="net.GND" />
    <trace from=".U5 > .GND" to="net.GND" />
    <trace from=".U5 > .SW" to=".L3 > .pin1" />
    <trace from=".L3 > .pin2" to="net.V3V3" />
    <trace from=".Cout3 > .pin1" to="net.V3V3" />
    <trace from=".Cout3 > .pin2" to="net.GND" />
    <trace from=".R3 > .pin1" to="net.V3V3" />
    <trace from=".R3 > .pin2" to=".U5 > .FB" />
    <trace from=".R4 > .pin1" to=".U5 > .FB" />
    <trace from=".R4 > .pin2" to="net.GND" />
    <trace from=".U5 > .EN" to="net.BAT" />

    {/* --- +3V3A LDO from +5V --- */}
    <trace from=".U6 > .IN" to="net.V5" />
    <trace from=".Cin3a > .pin1" to="net.V5" />
    <trace from=".Cin3a > .pin2" to="net.GND" />
    <trace from=".U6 > .GND" to="net.GND" />
    <trace from=".U6 > .OUT" to="net.V3V3A" />
    <trace from=".Cout3a > .pin1" to="net.V3V3A" />
    <trace from=".Cout3a > .pin2" to="net.GND" />
    <trace from=".U6 > .EN" to="net.RAIL_EN_3V3A" />
  </board>
)
