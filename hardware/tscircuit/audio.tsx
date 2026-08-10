// Leshy2 — Sheet 4: Audio  (transcribed from hardware/audio/audio.md)
// NOTE: ICs/connectors are generic <chip> with our logical pinout; real
// footprints/part numbers get assigned before PCB. 2-pin parts (electret mic,
// speaker, watch crystal) are modeled as resistor proxies for capture.
export default () => (
  <board width="80mm" height="60mm">
    {/* ===================== Si4732-A10 receiver (U30, all on +3V3A) ===================== */}
    <chip name="U30" footprint="soic16" pinLabels={{
      pin1: "VDD", pin2: "GND", pin3: "SDA", pin4: "SCL",
      pin5: "SEN", pin6: "RST", pin7: "RCLK", pin8: "AMI",
      pin9: "FMI", pin10: "LOUT", pin11: "ROUT",
    }} />
    {/* dedicated 32.768 kHz watch oscillator + load caps (NOT from MCU) */}
    <resistor name="Y1" resistance="0.001" footprint="0402" /> {/* 32.768kHz xtal proxy */}
    <capacitor name="CL1" capacitance="12pF" footprint="0402" />
    <capacitor name="CL2" capacitance="12pF" footprint="0402" />
    <capacitor name="Cvdd30" capacitance="1uF" footprint="0402" />
    {/* L+R -> mono summing resistor pair */}
    <resistor name="RsumL" resistance="10k" footprint="0402" />
    <resistor name="RsumR" resistance="10k" footprint="0402" />

    {/* ===================== SA868-U UHF voice walkie (U31) ===================== */}
    <chip name="U31" footprint="soic16" pinLabels={{
      pin1: "VIN", pin2: "VCC3V3", pin3: "GND", pin4: "RXD",
      pin5: "TXD", pin6: "PTT", pin7: "PD", pin8: "AF_OUT",
      pin9: "MIC_IN", pin10: "ANT",
    }} />
    {/* local bulk on Vin for the 2 W PA burst */}
    <capacitor name="Cbulk31" capacitance="330uF" footprint="1210" />
    <capacitor name="Cbyp31" capacitance="100nF" footprint="0402" />

    {/* electret mic + bias -> 1 uF coupling into SA868 MIC (1uF, not 10uF!) */}
    <resistor name="MK1" resistance="2.2k" footprint="0603" /> {/* electret mic proxy */}
    <resistor name="Rbias" resistance="4.7k" footprint="0402" />
    <capacitor name="Cmic" capacitance="1uF" footprint="0402" />

    {/* ===================== 2:1 analog mux 74LVC1G3157 (U33) ===================== */}
    <chip name="U33" footprint="sot23-6" pinLabels={{
      pin1: "INA", pin2: "INB", pin3: "COM", pin4: "SEL", pin5: "VCC", pin6: "GND",
    }} />

    {/* ===================== PAM8302A class-D amp (U32) ===================== */}
    <chip name="U32" footprint="sot23-6" pinLabels={{
      pin1: "IN", pin2: "SD", pin3: "VCC", pin4: "GND", pin5: "OUTP", pin6: "OUTM",
    }} />
    <resistor name="Rin32" resistance="10k" footprint="0402" /> {/* gain-set input R */}
    <capacitor name="Cvcc32" capacitance="10uF" footprint="0805" />

    {/* speaker (BTL, no ground reference) */}
    <resistor name="LS1" resistance="4" footprint="1210" /> {/* 4-8 ohm speaker proxy */}

    {/* 3.5mm headphone jack — AC-couple BOTH legs (amp is BTL), mute on insert */}
    <chip name="J30" footprint="soic8" pinLabels={{
      pin1: "L", pin2: "R", pin3: "SLEEVE", pin4: "DET",
    }} />
    <capacitor name="Cjk1" capacitance="220uF" footprint="1210" /> {/* AC-couple OUTP -> L */}
    <capacitor name="Cjk2" capacitance="220uF" footprint="1210" /> {/* AC-couple OUTM -> R */}

    {/* ============================== NETS ============================== */}
    {/* --- Si4732 supply + I2C + control --- */}
    <trace from=".U30 > .VDD" to="net.V3V3A" />
    <trace from=".U30 > .GND" to="net.GND" />
    <trace from=".Cvdd30 > .pin1" to="net.V3V3A" />
    <trace from=".Cvdd30 > .pin2" to="net.GND" />
    <trace from=".U30 > .SDA" to="net.I2C_SDA" />
    <trace from=".U30 > .SCL" to="net.I2C_SCL" />
    <trace from=".U30 > .SEN" to="net.GND" />        {/* SEN->GND = addr 0x11 */}
    <trace from=".U30 > .RST" to="net.Si4732_RST" />  {/* PCA #1 P0.3 */}

    {/* --- Si4732 RCLK from dedicated 32.768 kHz oscillator --- */}
    <trace from=".U30 > .RCLK" to=".Y1 > .pin1" />
    <trace from=".Y1 > .pin2" to="net.GND" />
    <trace from=".CL1 > .pin1" to=".U30 > .RCLK" />
    <trace from=".CL1 > .pin2" to="net.GND" />
    <trace from=".CL2 > .pin1" to=".Y1 > .pin2" />
    <trace from=".CL2 > .pin2" to="net.GND" />

    {/* --- Si4732 antennas (off-sheet nets) --- */}
    <trace from=".U30 > .AMI" to="net.ANT_HF_CB" />
    <trace from=".U30 > .FMI" to="net.ANT_FM" />

    {/* --- Si4732 line-out -> summing pair -> mux A --- */}
    <trace from=".U30 > .LOUT" to=".RsumL > .pin1" />
    <trace from=".U30 > .ROUT" to=".RsumR > .pin1" />
    <trace from=".RsumL > .pin2" to="net.SI_AUDIO" />
    <trace from=".RsumR > .pin2" to="net.SI_AUDIO" />
    <trace from=".U33 > .INA" to="net.SI_AUDIO" />

    {/* --- SA868 power + logic + UART1 + control --- */}
    <trace from=".U31 > .VIN" to="net.V5" />
    <trace from=".U31 > .VCC3V3" to="net.V3V3" />
    <trace from=".U31 > .GND" to="net.GND" />
    <trace from=".Cbulk31 > .pin1" to="net.V5" />
    <trace from=".Cbulk31 > .pin2" to="net.GND" />
    <trace from=".Cbyp31 > .pin1" to="net.V5" />
    <trace from=".Cbyp31 > .pin2" to="net.GND" />
    <trace from=".U31 > .RXD" to="net.SA868_UART_TX" />  {/* S3 TX GPIO16 -> U31.RXD */}
    <trace from=".U31 > .TXD" to="net.SA868_UART_RX" />  {/* U31.TXD -> S3 RX GPIO17 */}
    <trace from=".U31 > .PTT" to="net.SA868_PTT" />      {/* PCA #1 P0.1 */}
    <trace from=".U31 > .PD" to="net.SA868_PD" />        {/* PCA #1 P0.2 */}
    <trace from=".U31 > .ANT" to="net.ANT_UHF" />

    {/* --- SA868 RX audio -> mux B --- */}
    <trace from=".U31 > .AF_OUT" to="net.SA_AF" />
    <trace from=".U33 > .INB" to="net.SA_AF" />

    {/* --- Mic -> 1 uF -> SA868 MIC --- */}
    <trace from=".MK1 > .pin1" to="net.MIC_HOT" />
    <trace from=".MK1 > .pin2" to="net.GND" />
    <trace from=".Rbias > .pin1" to="net.V3V3A" />
    <trace from=".Rbias > .pin2" to="net.MIC_HOT" />
    <trace from=".Cmic > .pin1" to="net.MIC_HOT" />
    <trace from=".Cmic > .pin2" to=".U31 > .MIC_IN" />

    {/* --- Mux control + supply --- */}
    <trace from=".U33 > .SEL" to="net.MUX_SEL" />  {/* PCA #1 P0.7 */}
    <trace from=".U33 > .VCC" to="net.V3V3" />
    <trace from=".U33 > .GND" to="net.GND" />
    <trace from=".U33 > .COM" to="net.MUX_OUT" />

    {/* --- Amp: mux out -> Rin -> PAM8302 --- */}
    <trace from=".Rin32 > .pin1" to="net.MUX_OUT" />
    <trace from=".Rin32 > .pin2" to=".U32 > .IN" />
    <trace from=".U32 > .SD" to="net.PAM_SD" />    {/* PCA #1 P1.3 */}
    <trace from=".U32 > .VCC" to="net.V5" />
    <trace from=".U32 > .GND" to="net.GND" />
    <trace from=".Cvcc32 > .pin1" to="net.V5" />
    <trace from=".Cvcc32 > .pin2" to="net.GND" />

    {/* --- Speaker (BTL, floating) --- */}
    <trace from=".U32 > .OUTP" to="net.SPK_P" />
    <trace from=".U32 > .OUTM" to="net.SPK_M" />
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
