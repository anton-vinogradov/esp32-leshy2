// Leshy2 — MERGED board: all 6 sheets in ONE <board>.
// Cross-sheet stitching is by shared net.NAME. Colliding refdes renamed:
//   c5-buses U20 (ESP32-C5) -> m_U20 ; rf U20 (nRF24 #1) -> rf_U20
//   rf Y1 (26MHz xtal) -> rf_Y1 ; audio Y1 (32.768kHz proxy) -> a_Y1
export default () => (
  <board width="240mm" height="180mm">
    {/* ===================================================== */}
    {/* ================ SHEET: power ================ */}
    {/* ===================================================== */}
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
  
    {/* ===================================================== */}
    {/* ================ SHEET: c5-buses ================ */}
    {/* ===================================================== */}
    {/* ===================== U10 — ESP32-S3-WROOM-1U-N8R2 (main brain) ===================== */}
    <chip name="U10" footprint="qfn48" pinLabels={{
      pin1: "S3_BOOT",     // GPIO0  strap, recovery button
      pin2: "WS2812",      // GPIO1  RMT
      pin3: "IR_TX",       // GPIO2
      pin4: "LoRa_DIO1",   // GPIO3  strap, SX1262 IRQ
      pin5: "I2C_SDA",     // GPIO4
      pin6: "I2C_SCL",     // GPIO5
      pin7: "nRF24_CE",    // GPIO6
      pin8: "CC1101_GDO0", // GPIO7
      pin9: "HC138_A",     // GPIO8
      pin10: "HC138_B",    // GPIO9
      pin11: "HC138_C",    // GPIO10
      pin12: "SPI_MOSI",   // GPIO11 FSPID
      pin13: "SPI_SCK",    // GPIO12 FSPICLK
      pin14: "SPI_MISO",   // GPIO13 FSPIQ
      pin15: "LCD_DC",     // GPIO14
      pin16: "LoRa_BUSY",  // GPIO15
      pin17: "SA868_TX",   // GPIO16 UART1
      pin18: "SA868_RX",   // GPIO17 UART1
      pin19: "GPS_RX",     // GPIO18 UART2
      pin20: "USB_DM_S3",  // GPIO19
      pin21: "USB_DP_S3",  // GPIO20
      pin22: "LCD_TE",     // GPIO21
      pin23: "C5_EN",      // GPIO33
      pin24: "C5_BOOT",    // GPIO34
      pin25: "C5LINK_SCK", // GPIO35 SPI3
      pin26: "C5LINK_MOSI",// GPIO36 SPI3
      pin27: "C5LINK_MISO",// GPIO37 SPI3
      pin28: "C5LINK_CS",  // GPIO38
      pin29: "C5LINK_DRDY",// GPIO39
      pin30: "ENC_A",      // GPIO40
      pin31: "ENC_B",      // GPIO41
      pin32: "IR_RX",      // GPIO42
      pin33: "C5_FLASH_TX",// GPIO43 U0TXD
      pin34: "C5_FLASH_RX",// GPIO44 U0RXD
      pin35: "CC1101_GDO2",// GPIO45 strap (eFuse-freed)
      pin36: "nRF24_IRQ",  // GPIO46 strap (gate idle-low)
      pin37: "GPS_TX",     // GPIO47 UART2 optional
      pin38: "PCA9555_INT",// GPIO48 expander INT
      pin39: "V3V3",       // supply (Sheet 1)
      pin40: "GND",
    }} />

    {/* ===================== U20 — ESP32-C5-WROOM-1U (co-processor) ===================== */}
    <chip name="m_U20" footprint="soic16" pinLabels={{
      pin1: "C5_EN",       // EN pin  ← S3 GPIO33
      pin2: "C5_BOOT_26",  // GPIO26  ← S3 GPIO34 (download strap)
      pin3: "C5_BOOT_28",  // GPIO28  ← S3 GPIO34 (tied to 26)
      pin4: "STRAP27",     // GPIO27  pull-high for valid boot
      pin5: "LINK_SCK",    // GPIO23  ← S3
      pin6: "LINK_MOSI",   // GPIO24  ← S3
      pin7: "LINK_MISO",   // GPIO6   → S3
      pin8: "LINK_CS",     // GPIO8   ← S3
      pin9: "LINK_DRDY",   // GPIO9   → S3
      pin10: "U0TXD",      // GPIO11  → S3 (flash path)
      pin11: "U0RXD",      // GPIO12  ← S3 (flash path)
      pin12: "USB_DM_C5",  // GPIO13
      pin13: "USB_DP_C5",  // GPIO14
      pin14: "V3V3",       // supply
      pin15: "GND",
    }} />

    {/* ===================== U11 — 74HC138 3→8 chip-select decoder ===================== */}
    <chip name="U11" footprint="soic16" pinLabels={{
      pin1: "A", pin2: "B", pin3: "C",
      pin4: "G2A", pin5: "G2B", pin6: "G1",
      pin7: "Y7", pin8: "GND",
      pin9: "Y6", pin10: "Y5", pin11: "Y4", pin12: "Y3",
      pin13: "Y2", pin14: "Y1", pin15: "Y0", pin16: "VCC",
    }} />

    {/* ===================== U12 — PCA9555 #1 (0x20) radio/display control ===================== */}
    <chip name="U12" footprint="ssop24" pinLabels={{
      pin1: "P00", pin2: "P01", pin3: "P02", pin4: "P03",
      pin5: "P04", pin6: "P05", pin7: "P06", pin8: "P07",
      pin9: "GND", pin10: "P10", pin11: "P11", pin12: "P12",
      pin13: "P13", pin14: "P14", pin15: "P15", pin16: "P16",
      pin17: "P17", pin18: "INT", pin19: "SCL", pin20: "SDA",
      pin21: "A0", pin22: "A1", pin23: "A2", pin24: "VCC",
    }} />

    {/* ===================== U13 — PCA9555 #2 (0x21) user I/O + power gating + SP4T ===================== */}
    <chip name="U13" footprint="ssop24" pinLabels={{
      pin1: "P00", pin2: "P01", pin3: "P02", pin4: "P03",
      pin5: "P04", pin6: "P05", pin7: "P06", pin8: "P07",
      pin9: "GND", pin10: "P10", pin11: "P11", pin12: "P12",
      pin13: "P13", pin14: "P14", pin15: "P15", pin16: "P16",
      pin17: "P17", pin18: "INT", pin19: "SCL", pin20: "SDA",
      pin21: "A0", pin22: "A1", pin23: "A2", pin24: "VCC",
    }} />

    {/* I2C pull-ups (4.7k, Sheet-2 side of the shared bus) */}
    <resistor name="R_SDA" resistance="4.7k" footprint="0402" />
    <resistor name="R_SCL" resistance="4.7k" footprint="0402" />
    {/* C5 boot strap pull-up (26+28 high = normal boot while S3 GPIO34 is Hi-Z) */}
    <resistor name="R_C5BOOT" resistance="10k" footprint="0402" />
    {/* C5 GPIO27 pull-high for valid boot */}
    <resistor name="R_C5S27" resistance="10k" footprint="0402" />
    {/* 74HC138 G2A boot-gate default-disabled pull-up (to +3V3) */}
    <resistor name="R_HC138EN" resistance="10k" footprint="0402" />

    {/* ============================== NETS ============================== */}
    {/* --- S3 direct GPIO → bus/rail labels --- */}
    <trace from=".U10 > .S3_BOOT" to="net.S3_BOOT" />
    <trace from=".U10 > .WS2812" to="net.WS2812" />
    <trace from=".U10 > .IR_TX" to="net.IR_TX" />
    <trace from=".U10 > .LoRa_DIO1" to="net.LoRa_DIO1" />
    <trace from=".U10 > .I2C_SDA" to="net.I2C_SDA" />
    <trace from=".U10 > .I2C_SCL" to="net.I2C_SCL" />
    <trace from=".U10 > .nRF24_CE" to="net.nRF24_CE" />
    <trace from=".U10 > .CC1101_GDO0" to="net.CC1101_GDO0" />
    <trace from=".U10 > .SPI_MOSI" to="net.SPI_MOSI" />
    <trace from=".U10 > .SPI_SCK" to="net.SPI_SCK" />
    <trace from=".U10 > .SPI_MISO" to="net.SPI_MISO" />
    <trace from=".U10 > .LCD_DC" to="net.LCD_DC" />
    <trace from=".U10 > .LoRa_BUSY" to="net.LoRa_BUSY" />
    <trace from=".U10 > .SA868_TX" to="net.SA868_UART_TX" />
    <trace from=".U10 > .SA868_RX" to="net.SA868_UART_RX" />
    <trace from=".U10 > .GPS_RX" to="net.GPS_UART_RX" />
    <trace from=".U10 > .GPS_TX" to="net.GPS_UART_TX" />
    <trace from=".U10 > .USB_DM_S3" to="net.USB_DM_S3" />
    <trace from=".U10 > .USB_DP_S3" to="net.USB_DP_S3" />
    <trace from=".U10 > .LCD_TE" to="net.LCD_TE" />
    <trace from=".U10 > .ENC_A" to="net.ENC_A" />
    <trace from=".U10 > .ENC_B" to="net.ENC_B" />
    <trace from=".U10 > .IR_RX" to="net.IR_RX" />
    <trace from=".U10 > .CC1101_GDO2" to="net.CC1101_GDO2" />
    <trace from=".U10 > .nRF24_IRQ" to="net.nRF24_IRQ" />
    <trace from=".U10 > .V3V3" to="net.V3V3" />
    <trace from=".U10 > .GND" to="net.GND" />

    {/* --- S3 ↔ C5 dedicated SPI3 link (via nets) --- */}
    <trace from=".U10 > .C5LINK_SCK" to="net.C5LINK_SCK" />
    <trace from=".m_U20 > .LINK_SCK" to="net.C5LINK_SCK" />
    <trace from=".U10 > .C5LINK_MOSI" to="net.C5LINK_MOSI" />
    <trace from=".m_U20 > .LINK_MOSI" to="net.C5LINK_MOSI" />
    <trace from=".U10 > .C5LINK_MISO" to="net.C5LINK_MISO" />
    <trace from=".m_U20 > .LINK_MISO" to="net.C5LINK_MISO" />
    <trace from=".U10 > .C5LINK_CS" to="net.C5LINK_CS" />
    <trace from=".m_U20 > .LINK_CS" to="net.C5LINK_CS" />
    <trace from=".U10 > .C5LINK_DRDY" to="net.C5LINK_DRDY" />
    <trace from=".m_U20 > .LINK_DRDY" to="net.C5LINK_DRDY" />
    <trace from=".U10 > .C5_EN" to="net.C5_EN" />
    <trace from=".m_U20 > .C5_EN" to="net.C5_EN" />
    <trace from=".U10 > .C5_BOOT" to="net.C5_BOOT" />
    <trace from=".m_U20 > .C5_BOOT_26" to="net.C5_BOOT" />
    <trace from=".m_U20 > .C5_BOOT_28" to="net.C5_BOOT" />
    <trace from=".R_C5BOOT > .pin1" to="net.C5_BOOT" />
    <trace from=".R_C5BOOT > .pin2" to="net.V3V3" />
    <trace from=".m_U20 > .STRAP27" to=".R_C5S27 > .pin1" />
    <trace from=".R_C5S27 > .pin2" to="net.V3V3" />

    {/* --- S3 ↔ C5 flash bridge UART0 --- */}
    <trace from=".U10 > .C5_FLASH_TX" to="net.C5_FLASH_TX" />
    <trace from=".m_U20 > .U0RXD" to="net.C5_FLASH_TX" />
    <trace from=".U10 > .C5_FLASH_RX" to="net.C5_FLASH_RX" />
    <trace from=".m_U20 > .U0TXD" to="net.C5_FLASH_RX" />

    {/* --- C5 own USB-C (data-only, Sheet 1) --- */}
    <trace from=".m_U20 > .USB_DM_C5" to="net.USB_DM_C5" />
    <trace from=".m_U20 > .USB_DP_C5" to="net.USB_DP_C5" />
    <trace from=".m_U20 > .V3V3" to="net.V3V3" />
    <trace from=".m_U20 > .GND" to="net.GND" />

    {/* --- I2C pull-ups --- */}
    <trace from=".R_SDA > .pin1" to="net.I2C_SDA" />
    <trace from=".R_SDA > .pin2" to="net.V3V3" />
    <trace from=".R_SCL > .pin1" to="net.I2C_SCL" />
    <trace from=".R_SCL > .pin2" to="net.V3V3" />

    {/* --- 74HC138 decoder --- */}
    <trace from=".U11 > .A" to="net.HC138_A" />
    <trace from=".U11 > .B" to="net.HC138_B" />
    <trace from=".U11 > .C" to="net.HC138_C" />
    <trace from=".U10 > .HC138_A" to="net.HC138_A" />
    <trace from=".U10 > .HC138_B" to="net.HC138_B" />
    <trace from=".U10 > .HC138_C" to="net.HC138_C" />
    <trace from=".U11 > .G1" to="net.V3V3" />
    <trace from=".U11 > .G2B" to="net.GND" />
    <trace from=".U11 > .G2A" to="net.HC138_EN" />
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
    {/* HC138 boot-gate default-disabled pull-up */}
    <trace from=".R_HC138EN > .pin1" to="net.HC138_EN" />
    <trace from=".R_HC138EN > .pin2" to="net.V3V3" />

    {/* --- PCA9555 #1 (0x20) --- */}
    <trace from=".U12 > .SDA" to="net.I2C_SDA" />
    <trace from=".U12 > .SCL" to="net.I2C_SCL" />
    <trace from=".U12 > .INT" to="net.PCA9555_INT" />
    <trace from=".U12 > .VCC" to="net.V3V3" />
    <trace from=".U12 > .GND" to="net.GND" />
    <trace from=".U12 > .A0" to="net.GND" />
    <trace from=".U12 > .A1" to="net.GND" />
    <trace from=".U12 > .A2" to="net.GND" />
    <trace from=".U12 > .P00" to="net.ENC_SW" />
    <trace from=".U12 > .P01" to="net.SA868_PTT" />
    <trace from=".U12 > .P02" to="net.SA868_PD" />
    <trace from=".U12 > .P03" to="net.Si4732_RST" />
    <trace from=".U12 > .P04" to="net.LoRa_NRESET" />
    <trace from=".U12 > .P05" to="net.BUZZER" />
    <trace from=".U12 > .P06" to="net.LCD_RESX" />
    <trace from=".U12 > .P07" to="net.MUX_SEL" />
    <trace from=".U12 > .P10" to="net.BQ_INT" />
    <trace from=".U12 > .P11" to="net.BQ_CD" />
    <trace from=".U12 > .P12" to="net.LoRa_TR" />
    <trace from=".U12 > .P13" to="net.PAM_SD" />
    <trace from=".U12 > .P14" to="net.LCD_BL_EN" />
    <trace from=".U12 > .P15" to="net.RFSW_A" />
    <trace from=".U12 > .P16" to="net.HC138_EN" />
    <trace from=".U12 > .P17" to="net.SD_CD" />

    {/* --- PCA9555 #2 (0x21) --- */}
    <trace from=".U13 > .SDA" to="net.I2C_SDA" />
    <trace from=".U13 > .SCL" to="net.I2C_SCL" />
    <trace from=".U13 > .INT" to="net.PCA9555_INT" />
    <trace from=".U13 > .VCC" to="net.V3V3" />
    <trace from=".U13 > .GND" to="net.GND" />
    <trace from=".U13 > .A0" to="net.V3V3" />
    <trace from=".U13 > .A1" to="net.GND" />
    <trace from=".U13 > .A2" to="net.GND" />
    <trace from=".U13 > .P00" to="net.PTT_BTN" />
    <trace from=".U13 > .P01" to="net.RAIL_EN_5V" />
    <trace from=".U13 > .P02" to="net.RAIL_EN_3V3A" />
    <trace from=".U13 > .P03" to="net.JACK_DET" />
    <trace from=".U13 > .P04" to="net.RFSW_B" />
    {/* P05..P17 spare */}

    {/* --- S3 expander INT input --- */}
    <trace from=".U10 > .PCA9555_INT" to="net.PCA9555_INT" />
  
    {/* ===================================================== */}
    {/* ================ SHEET: rf ================ */}
    {/* ===================================================== */}
    {/* ===================== 3x nRF24L01+PA/LNA modules ===================== */}
    {/* 8-pin header module: onboard SMA, own antenna */}
    <chip name="rf_U20" footprint="soic8" pinLabels={{
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
    <crystal name="rf_Y1" frequency="26MHz" loadCapacitance="10pF" footprint="cd3215" />
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
    <trace from=".U23 > .XOSC1" to=".rf_Y1 > .pin1" />
    <trace from=".U23 > .XOSC2" to=".rf_Y1 > .pin2" />
    <trace from=".Cx1 > .pin1" to=".rf_Y1 > .pin1" />
    <trace from=".Cx1 > .pin2" to="net.GND" />
    <trace from=".Cx2 > .pin1" to=".rf_Y1 > .pin2" />
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
  
    {/* ===================================================== */}
    {/* ================ SHEET: audio ================ */}
    {/* ===================================================== */}
    {/* ===================== Si4732-A10 receiver (U30, all on +3V3A) ===================== */}
    <chip name="U30" footprint="soic16" pinLabels={{
      pin1: "VDD", pin2: "GND", pin3: "SDA", pin4: "SCL",
      pin5: "SEN", pin6: "RST", pin7: "RCLK", pin8: "AMI",
      pin9: "FMI", pin10: "LOUT", pin11: "ROUT",
    }} />
    {/* dedicated 32.768 kHz watch oscillator + load caps (NOT from MCU) */}
    <resistor name="a_Y1" resistance="0.001" footprint="0402" /> {/* 32.768kHz xtal proxy */}
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
    <trace from=".U30 > .RST" to="net.Si4732_RST" />     {/* PCA #1 P0.3 */}

    {/* --- Si4732 RCLK from dedicated 32.768 kHz oscillator --- */}
    <trace from=".U30 > .RCLK" to=".a_Y1 > .pin1" />
    <trace from=".a_Y1 > .pin2" to="net.GND" />
    <trace from=".CL1 > .pin1" to=".U30 > .RCLK" />
    <trace from=".CL1 > .pin2" to="net.GND" />
    <trace from=".CL2 > .pin1" to=".a_Y1 > .pin2" />
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
    <trace from=".U31 > .RXD" to="net.SA868_UART_TX" />   {/* S3 TX GPIO16 -> U31.RXD */}
    <trace from=".U31 > .TXD" to="net.SA868_UART_RX" />   {/* U31.TXD -> S3 RX GPIO17 */}
    <trace from=".U31 > .PTT" to="net.SA868_PTT" />   {/* PCA #1 P0.1 */}
    <trace from=".U31 > .PD" to="net.SA868_PD" />     {/* PCA #1 P0.2 */}
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
  
    {/* ===================================================== */}
    {/* ================ SHEET: expansion ================ */}
    {/* ===================================================== */}
    {/* ===================== u-blox SAM-M8Q GPS (onboard, UART2) ===================== */}
    <chip name="U40" footprint="soic8" pinLabels={{
      pin1: "VCC", pin2: "GND", pin3: "TXD", pin4: "RXD",
      pin5: "V_BCKP", pin6: "TIMEPULSE",
    }} />
    {/* GPS backup: supercap + Schottky on V_BCKP (both modeled as 2-pin proxies) */}
    <resistor name="D40s" resistance="0.01" footprint="0603" /> {/* Schottky proxy: +3V3 -> V_BCKP */}
    <capacitor name="BT40" capacitance="100000uF" footprint="1210" /> {/* supercap proxy */}

    {/* ===================== I2C bus pull-ups ===================== */}
    <resistor name="R40" resistance="4.7k" footprint="0402" /> {/* SDA pull-up -> +3V3 */}
    <resistor name="R41" resistance="4.7k" footprint="0402" /> {/* SCL pull-up -> +3V3 */}

    {/* ===================== Grove HY2.0-4P I2C ports x2 ===================== */}
    <chip name="J40" footprint="soic8" pinLabels={{ pin1: "V", pin2: "GND", pin3: "SDA", pin4: "SCL" }} />
    <chip name="J41" footprint="soic8" pinLabels={{ pin1: "V", pin2: "GND", pin3: "SDA", pin4: "SCL" }} />
    {/* ESD arrays protecting each Grove connector (SDA/SCL clamps to GND) */}
    <chip name="D41" footprint="sot23-3" pinLabels={{ pin1: "IO1", pin2: "IO2", pin3: "GND" }} />
    <chip name="D42" footprint="sot23-3" pinLabels={{ pin1: "IO1", pin2: "IO2", pin3: "GND" }} />

    {/* ===================== RFID2 Unit (WS1850S) — example Grove I2C unit @0x28 ===================== */}
    <chip name="U44" footprint="soic8" pinLabels={{ pin1: "V", pin2: "GND", pin3: "SDA", pin4: "SCL" }} />

    {/* ============================== NETS ============================== */}
    {/* --- GPS UART2 + power --- */}
    <trace from=".U40 > .VCC" to="net.V3V3" />
    <trace from=".U40 > .GND" to="net.GND" />
    <trace from=".U40 > .TXD" to="net.GPS_UART_RX" /> {/* S3 GPIO18 <- U40.TXD */}
    <trace from=".U40 > .RXD" to="net.GPS_UART_TX" /> {/* S3 GPIO47 -> U40.RXD */}
    {/* V_BCKP: +3V3 through Schottky, held by supercap */}
    <trace from=".D40s > .pin1" to="net.V3V3" />
    <trace from=".D40s > .pin2" to="net.V_BCKP" />
    <trace from=".U40 > .V_BCKP" to="net.V_BCKP" />
    <trace from=".BT40 > .pin1" to="net.V_BCKP" />
    <trace from=".BT40 > .pin2" to="net.GND" />
    {/* TIMEPULSE (1PPS) left unconnected — no spare pin */}

    {/* --- I2C bus pull-ups to +3V3 --- */}
    <trace from=".R40 > .pin1" to="net.V3V3" />
    <trace from=".R40 > .pin2" to="net.I2C_SDA" />
    <trace from=".R41 > .pin1" to="net.V3V3" />
    <trace from=".R41 > .pin2" to="net.I2C_SCL" />

    {/* --- Grove port J40 --- */}
    <trace from=".J40 > .V" to="net.V3V3" />
    <trace from=".J40 > .GND" to="net.GND" />
    <trace from=".J40 > .SDA" to="net.I2C_SDA" />
    <trace from=".J40 > .SCL" to="net.I2C_SCL" />
    <trace from=".D41 > .IO1" to="net.I2C_SDA" />
    <trace from=".D41 > .IO2" to="net.I2C_SCL" />
    <trace from=".D41 > .GND" to="net.GND" />

    {/* --- Grove port J41 --- */}
    <trace from=".J41 > .V" to="net.V3V3" />
    <trace from=".J41 > .GND" to="net.GND" />
    <trace from=".J41 > .SDA" to="net.I2C_SDA" />
    <trace from=".J41 > .SCL" to="net.I2C_SCL" />
    <trace from=".D42 > .IO1" to="net.I2C_SDA" />
    <trace from=".D42 > .IO2" to="net.I2C_SCL" />
    <trace from=".D42 > .GND" to="net.GND" />

    {/* --- RFID2 example unit @0x28 on I2C --- */}
    <trace from=".U44 > .V" to="net.V3V3" />
    <trace from=".U44 > .GND" to="net.GND" />
    <trace from=".U44 > .SDA" to="net.I2C_SDA" />
    <trace from=".U44 > .SCL" to="net.I2C_SCL" />
  
    {/* ===================================================== */}
    {/* ================ SHEET: indicators ================ */}
    {/* ===================================================== */}
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
    <trace from=".J50 > .MOSI" to="net.SPI_MOSI" />
    <trace from=".J50 > .MISO" to="net.SPI_MISO" />
    <trace from=".J50 > .SCK" to="net.SPI_SCK" />
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
    <trace from=".SW12 > .pin1" to="net.S3_BOOT" />
    <trace from=".SW12 > .pin2" to="net.GND" />
    <trace from=".SW13 > .pin1" to="net.PTT_BTN" />
    <trace from=".SW13 > .pin2" to="net.GND" />
  
  </board>
)
