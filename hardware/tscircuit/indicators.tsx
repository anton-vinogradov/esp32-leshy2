// Leshy2 — Sheet 6: Indicators & I/O  (transcribed from hardware/indicators/indicators.md)
// NOTE: ICs/connectors/switches are generic <chip> with our logical pinout; real
// footprints/parts get assigned before PCB. 2-pin passive-ish parts (active
// buzzer, momentary buttons) are modeled as resistor proxies for capture.
// TX-live LEDs are pure analog envelope detectors (0 GPIO): <led> + NPN + Rdim,
// base fed from a per-chain RF detector tap (net.TXDET_*).
export default () => (
  <board width="90mm" height="70mm">
    {/* ===================== TX-live LEDs ×7 (analog, 0 GPIO) ===================== */}
    {/* Each transmit chain: amber LED lit by real RF envelope, never firmware. */}
    {/* D5x anode -> Rdimx -> +3V3 ; D5x cathode -> Q5x collector ; Q5x emitter -> GND ; */}
    {/* Q5x base <- per-chain detector tap net.TXDET_x */}
    {/* chain 50 = C5 Wi-Fi/BLE */}
    <led name="D50" footprint="0603" />
    <chip name="Q50" footprint="sot23" pinLabels={{ pin1: "B", pin2: "E", pin3: "C" }} />
    <resistor name="Rd50" resistance="4.7k" footprint="0402" />
    {/* chain 51 = nRF24 #1 */}
    <led name="D51" footprint="0603" />
    <chip name="Q51" footprint="sot23" pinLabels={{ pin1: "B", pin2: "E", pin3: "C" }} />
    <resistor name="Rd51" resistance="4.7k" footprint="0402" />
    {/* chain 52 = nRF24 #2 */}
    <led name="D52" footprint="0603" />
    <chip name="Q52" footprint="sot23" pinLabels={{ pin1: "B", pin2: "E", pin3: "C" }} />
    <resistor name="Rd52" resistance="4.7k" footprint="0402" />
    {/* chain 53 = nRF24 #3 */}
    <led name="D53" footprint="0603" />
    <chip name="Q53" footprint="sot23" pinLabels={{ pin1: "B", pin2: "E", pin3: "C" }} />
    <resistor name="Rd53" resistance="4.7k" footprint="0402" />
    {/* chain 54 = CC1101 */}
    <led name="D54" footprint="0603" />
    <chip name="Q54" footprint="sot23" pinLabels={{ pin1: "B", pin2: "E", pin3: "C" }} />
    <resistor name="Rd54" resistance="4.7k" footprint="0402" />
    {/* chain 55 = SA868 */}
    <led name="D55" footprint="0603" />
    <chip name="Q55" footprint="sot23" pinLabels={{ pin1: "B", pin2: "E", pin3: "C" }} />
    <resistor name="Rd55" resistance="4.7k" footprint="0402" />
    {/* chain 56 = SX1262 (LoRa) */}
    <led name="D56" footprint="0603" />
    <chip name="Q56" footprint="sot23" pinLabels={{ pin1: "B", pin2: "E", pin3: "C" }} />
    <resistor name="Rd56" resistance="4.7k" footprint="0402" />

    {/* ===================== WS2812 status LED + level shift ===================== */}
    {/* DS1 on S3 GPIO1 (RMT), +5V, DIN via 74AHCT1G125 (U51) 3V3->5V TTL buffer */}
    <chip name="DS1" footprint="sot23-5" pinLabels={{
      pin1: "VDD", pin2: "DOUT", pin3: "GND", pin4: "DIN",
    }} />
    <chip name="U51" footprint="sot23-5" pinLabels={{
      pin1: "A", pin2: "Y", pin3: "OE", pin4: "VCC", pin5: "GND",
    }} />

    {/* ===================== Buzzer ===================== */}
    {/* LS2 active buzzer via Q57, on +5V, gated by net.BUZZER (PCA9555 #1 P0.5) */}
    <resistor name="LS2" resistance="0.01" footprint="1210" /> {/* active buzzer proxy */}
    <chip name="Q57" footprint="sot23" pinLabels={{ pin1: "B", pin2: "E", pin3: "C" }} />

    {/* ===================== IR ===================== */}
    {/* TX: D57 IR LED driven by Q58 from GPIO2 (38kHz), +5V */}
    <led name="D57" footprint="0603" />
    <chip name="Q58" footprint="sot23" pinLabels={{ pin1: "B", pin2: "E", pin3: "C" }} />
    <resistor name="Rir" resistance="47" footprint="0603" />
    {/* RX: U50 TSOP38238 into GPIO42 (RMT), +3V3 */}
    <chip name="U50" footprint="sot23" pinLabels={{ pin1: "OUT", pin2: "GND", pin3: "VS" }} />
    <capacitor name="Cir" capacitance="100nF" footprint="0402" />

    {/* ===================== microSD (SPI mode) ===================== */}
    {/* J50 on shared SPI2, CS from 74HC138 Y0, CD on PCA9555 #1 P1.7, 3V3 native */}
    <chip name="J50" footprint="soic8" pinLabels={{
      pin1: "CS", pin2: "MOSI", pin3: "MISO", pin4: "SCK",
      pin5: "VDD", pin6: "GND", pin7: "CD", pin8: "DAT1",
    }} />
    <capacitor name="Csd1" capacitance="10uF" footprint="0805" />
    <capacitor name="Csd2" capacitance="100nF" footprint="0402" />

    {/* ===================== Rotary encoder ===================== */}
    {/* SW10 quadrature A/B (GPIO40/41) + push (PCA9555 #1 P0.0) */}
    <chip name="SW10" footprint="sot23-5" pinLabels={{
      pin1: "A", pin2: "COM", pin3: "B", pin4: "SW1", pin5: "SW2",
    }} />

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

    {/* --- WS2812 + 74AHCT1G125 shift --- */}
    <trace from=".U51 > .A" to="net.WS2812" />
    <trace from=".U51 > .OE" to="net.GND" />
    <trace from=".U51 > .VCC" to="net.V5" />
    <trace from=".U51 > .GND" to="net.GND" />
    <trace from=".U51 > .Y" to=".DS1 > .DIN" />
    <trace from=".DS1 > .VDD" to="net.V5" />
    <trace from=".DS1 > .GND" to="net.GND" />
    <trace from=".DS1 > .DOUT" to="net.WS2812_DOUT" />

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

    {/* --- IR RX --- */}
    <trace from=".U50 > .OUT" to="net.IR_RX" />
    <trace from=".U50 > .VS" to="net.V3V3" />
    <trace from=".U50 > .GND" to="net.GND" />
    <trace from=".Cir > .pin1" to="net.V3V3" />
    <trace from=".Cir > .pin2" to="net.GND" />

    {/* --- microSD --- */}
    <trace from=".J50 > .CS" to="net.SD_CS" />
    <trace from=".J50 > .MOSI" to="net.SPI2_MOSI" />
    <trace from=".J50 > .MISO" to="net.SPI2_MISO" />
    <trace from=".J50 > .SCK" to="net.SPI2_SCK" />
    <trace from=".J50 > .VDD" to="net.V3V3" />
    <trace from=".J50 > .GND" to="net.GND" />
    <trace from=".J50 > .CD" to="net.SD_CD" />
    <trace from=".Csd1 > .pin1" to="net.V3V3" />
    <trace from=".Csd1 > .pin2" to="net.GND" />
    <trace from=".Csd2 > .pin1" to="net.V3V3" />
    <trace from=".Csd2 > .pin2" to="net.GND" />

    {/* --- Rotary encoder --- */}
    <trace from=".SW10 > .A" to="net.ENC_A" />
    <trace from=".SW10 > .B" to="net.ENC_B" />
    <trace from=".SW10 > .COM" to="net.GND" />
    <trace from=".SW10 > .SW1" to="net.ENC_SW" />
    <trace from=".SW10 > .SW2" to="net.GND" />

    {/* --- Physical buttons --- */}
    <trace from=".SW11 > .pin1" to="net.S3_EN" />
    <trace from=".SW11 > .pin2" to="net.GND" />
    <trace from=".Ren > .pin1" to="net.V3V3" />
    <trace from=".Ren > .pin2" to="net.S3_EN" />
    <trace from=".Cen > .pin1" to="net.S3_EN" />
    <trace from=".Cen > .pin2" to="net.GND" />
    <trace from=".SW12 > .pin1" to="net.BOOT" />
    <trace from=".SW12 > .pin2" to="net.GND" />
    <trace from=".SW13 > .pin1" to="net.PTT_BTN" />
    <trace from=".SW13 > .pin2" to="net.GND" />
  </board>
)
