// Leshy2 — Sheet 3: RF chains  (transcribed from hardware/rf/rf.md)
// NOTE: modules/ICs are generic <chip> with our logical pinout; real
// footprints/part numbers get assigned before PCB. 2-pin passives (xtal load,
// per-band match inductors) are proxies for capture. All logic on +3V3.
export default () => (
  <board width="120mm" height="90mm">
    {/* ===================== 3x nRF24L01+PA/LNA modules ===================== */}
    {/* 8-pin header module: onboard SMA, own antenna */}
    <chip name="U20" footprint="soic8" pinLabels={{
      pin1: "GND", pin2: "VCC", pin3: "CE", pin4: "CSN",
      pin5: "SCK", pin6: "MOSI", pin7: "MISO", pin8: "IRQ",
    }} />
    <chip name="U21" footprint="soic8" pinLabels={{
      pin1: "GND", pin2: "VCC", pin3: "CE", pin4: "CSN",
      pin5: "SCK", pin6: "MOSI", pin7: "MISO", pin8: "IRQ",
    }} />
    <chip name="U22" footprint="soic8" pinLabels={{
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

    {/* ===================== nRF24 IRQ combiner (74AHC 3-input gate) ===================== */}
    {/* push-pull IRQs cannot wire-OR; gate -> single idle-LOW line to GPIO46 */}
    <chip name="U28" footprint="sot23-6" pinLabels={{
      pin1: "IN1", pin2: "IN2", pin3: "IN3", pin4: "OUT", pin5: "VCC", pin6: "GND",
    }} />

    {/* ===================== CC1101 bare IC + 26MHz xtal + balun ===================== */}
    <chip name="U23" footprint="soic16" pinLabels={{
      pin1: "VDD", pin2: "GND", pin3: "CSN", pin4: "SCLK",
      pin5: "SI", pin6: "SO", pin7: "GDO0", pin8: "GDO2",
      pin9: "RFP", pin10: "RFN", pin11: "XOSC1", pin12: "XOSC2",
    }} />
    <crystal name="Y1" frequency="26MHz" loadCapacitance="10pF" footprint="cd3215" />
    <capacitor name="Cx1" capacitance="10pF" footprint="0402" />
    <capacitor name="Cx2" capacitance="10pF" footprint="0402" />
    {/* RF balun: balanced RFP/RFN -> single-ended CC1101_RF */}
    <chip name="BL1" footprint="soic8" pinLabels={{
      pin1: "RFP", pin2: "RFN", pin3: "RFSE", pin4: "GND",
    }} />
    {/* CC1101 local bulk */}
    <capacitor name="Cb23" capacitance="100uF" footprint="1210" />
    <capacitor name="Cd23" capacitance="100nF" footprint="0402" />

    {/* ===================== SP4T PE42440 + 4x band matches ===================== */}
    <chip name="U24" footprint="soic16" pinLabels={{
      pin1: "RFC", pin2: "RF1", pin3: "RF2", pin4: "RF3", pin5: "RF4",
      pin6: "V1", pin7: "V2", pin8: "VDD", pin9: "GND",
    }} />
    {/* per-band matched networks (proxy: one inductor each) */}
    <inductor name="Lm315" inductance="1nH" footprint="0402" />
    <inductor name="Lm433" inductance="1nH" footprint="0402" />
    <inductor name="Lm868" inductance="1nH" footprint="0402" />
    <inductor name="Lm915" inductance="1nH" footprint="0402" />

    {/* ===================== SX1262 / E22-900M22S module ===================== */}
    <chip name="U25" footprint="soic16" pinLabels={{
      pin1: "VCC", pin2: "GND", pin3: "NSS", pin4: "SCK",
      pin5: "MOSI", pin6: "MISO", pin7: "BUSY", pin8: "DIO1",
      pin9: "NRESET", pin10: "RXEN", pin11: "TXEN", pin12: "ANT",
    }} />
    <capacitor name="Cb25" capacitance="100uF" footprint="1210" />
    <capacitor name="Cd25" capacitance="100nF" footprint="0402" />
    {/* 74LVC1G04 inverter: complementary RXEN from TXEN(LoRa_TR) */}
    <chip name="U27" footprint="sot23-5" pinLabels={{
      pin1: "IN", pin2: "OUT", pin3: "VCC", pin4: "GND",
    }} />

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

    {/* --- IRQ combiner --- */}
    <trace from=".U28 > .IN1" to="net.nRF24_1_IRQ" />
    <trace from=".U28 > .IN2" to="net.nRF24_2_IRQ" />
    <trace from=".U28 > .IN3" to="net.nRF24_3_IRQ" />
    <trace from=".U28 > .OUT" to="net.nRF24_IRQ" />
    <trace from=".U28 > .VCC" to="net.V3V3" />
    <trace from=".U28 > .GND" to="net.GND" />

    {/* --- CC1101 --- */}
    <trace from=".U23 > .VDD" to="net.V3V3" />
    <trace from=".U23 > .GND" to="net.GND" />
    <trace from=".U23 > .CSN" to="net.CC1101_CS" />
    <trace from=".U23 > .SCLK" to="net.SPI_SCK" />
    <trace from=".U23 > .SI" to="net.SPI_MOSI" />
    <trace from=".U23 > .SO" to="net.SPI_MISO" />
    <trace from=".U23 > .GDO0" to="net.CC1101_GDO0" />
    <trace from=".U23 > .GDO2" to="net.CC1101_GDO2" />
    <trace from=".U23 > .RFP" to=".BL1 > .RFP" />
    <trace from=".U23 > .RFN" to=".BL1 > .RFN" />
    <trace from=".U23 > .XOSC1" to=".Y1 > .pin1" />
    <trace from=".U23 > .XOSC2" to=".Y1 > .pin2" />
    <trace from=".Cx1 > .pin1" to=".Y1 > .pin1" />
    <trace from=".Cx1 > .pin2" to="net.GND" />
    <trace from=".Cx2 > .pin1" to=".Y1 > .pin2" />
    <trace from=".Cx2 > .pin2" to="net.GND" />
    <trace from=".BL1 > .GND" to="net.GND" />
    <trace from=".BL1 > .RFSE" to="net.CC1101_RF" />
    <trace from=".Cb23 > .pin1" to="net.V3V3" />
    <trace from=".Cb23 > .pin2" to="net.GND" />
    <trace from=".Cd23 > .pin1" to="net.V3V3" />
    <trace from=".Cd23 > .pin2" to="net.GND" />

    {/* --- SP4T band switch: one antenna, four matches --- */}
    <trace from=".U24 > .RFC" to="net.CC1101_RF" />
    <trace from=".U24 > .V1" to="net.RFSW_A" />
    <trace from=".U24 > .V2" to="net.RFSW_B" />
    <trace from=".U24 > .VDD" to="net.V3V3" />
    <trace from=".U24 > .GND" to="net.GND" />
    <trace from=".U24 > .RF1" to=".Lm315 > .pin1" />
    <trace from=".Lm315 > .pin2" to="net.ANT_CC1101" />
    <trace from=".U24 > .RF2" to=".Lm433 > .pin1" />
    <trace from=".Lm433 > .pin2" to="net.ANT_CC1101" />
    <trace from=".U24 > .RF3" to=".Lm868 > .pin1" />
    <trace from=".Lm868 > .pin2" to="net.ANT_CC1101" />
    <trace from=".U24 > .RF4" to=".Lm915 > .pin1" />
    <trace from=".Lm915 > .pin2" to="net.ANT_CC1101" />

    {/* --- SX1262 / E22 --- */}
    <trace from=".U25 > .VCC" to="net.V3V3" />
    <trace from=".U25 > .GND" to="net.GND" />
    <trace from=".U25 > .NSS" to="net.LoRa_NSS" />
    <trace from=".U25 > .SCK" to="net.SPI_SCK" />
    <trace from=".U25 > .MOSI" to="net.SPI_MOSI" />
    <trace from=".U25 > .MISO" to="net.SPI_MISO" />
    <trace from=".U25 > .BUSY" to="net.LoRa_BUSY" />
    <trace from=".U25 > .DIO1" to="net.LoRa_DIO1" />
    <trace from=".U25 > .NRESET" to="net.LoRa_NRESET" />
    <trace from=".U25 > .TXEN" to="net.LoRa_TR" />
    <trace from=".U25 > .RXEN" to="net.LoRa_RXEN" />
    <trace from=".U25 > .ANT" to="net.ANT_LoRa" />
    <trace from=".Cb25 > .pin1" to="net.V3V3" />
    <trace from=".Cb25 > .pin2" to="net.GND" />
    <trace from=".Cd25 > .pin1" to="net.V3V3" />
    <trace from=".Cd25 > .pin2" to="net.GND" />
    {/* inverter: RXEN = NOT LoRa_TR */}
    <trace from=".U27 > .IN" to="net.LoRa_TR" />
    <trace from=".U27 > .OUT" to="net.LoRa_RXEN" />
    <trace from=".U27 > .VCC" to="net.V3V3" />
    <trace from=".U27 > .GND" to="net.GND" />
  </board>
)
