// Leshy2 — Sheet 2: MCU + buses  (transcribed from hardware/c5-buses/c5-buses.md)
// NOTE: MCUs/expanders/decoder are generic <chip> with our logical pinout from the
// GPIO maps; real footprints/part numbers get assigned before PCB. Peripherals of
// other sheets are NOT placed here — only MCUs + PCA9555 expanders + 74HC138, plus
// bus/rail labels (net.NAME). Footprints are pin-count placeholders (see issues).
export default () => (
  <board width="120mm" height="90mm">
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
      pin41: "EN",         // CHIP_PU — reset + RC from Sheet 6 (net.S3_EN)
    }} />

    {/* ===================== U20 — ESP32-C5-WROOM-1U (co-processor) ===================== */}
    <chip name="U20" footprint="soic16" pinLabels={{
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

    {/* I2C pull-ups live on Sheet 5 (single pair R40/R41 for the whole bus) */}
    {/* C5 boot strap pull-up (26+28 high = normal boot while S3 GPIO34 is Hi-Z) */}
    <resistor name="R_C5BOOT" resistance="10k" footprint="0402" />
    {/* C5 GPIO27 pull-high for valid boot */}
    <resistor name="R_C5S27" resistance="10k" footprint="0402" />
    {/* 74HC138 G2A boot-gate default-disabled pull-up (to +3V3) */}
    <resistor name="R_HC138EN" resistance="10k" footprint="0402" />
    {/* C5 EN pull-up + RC — reset well-defined regardless of S3 GPIO33 (open-drain) */}
    <resistor name="R_C5EN" resistance="10k" footprint="0402" />
    <capacitor name="C_C5EN" capacitance="1uF" footprint="0402" />

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
    <trace from=".U10 > .EN" to="net.S3_EN" />

    {/* --- S3 ↔ C5 dedicated SPI3 link (via nets) --- */}
    <trace from=".U10 > .C5LINK_SCK" to="net.C5LINK_SCK" />
    <trace from=".U20 > .LINK_SCK" to="net.C5LINK_SCK" />
    <trace from=".U10 > .C5LINK_MOSI" to="net.C5LINK_MOSI" />
    <trace from=".U20 > .LINK_MOSI" to="net.C5LINK_MOSI" />
    <trace from=".U10 > .C5LINK_MISO" to="net.C5LINK_MISO" />
    <trace from=".U20 > .LINK_MISO" to="net.C5LINK_MISO" />
    <trace from=".U10 > .C5LINK_CS" to="net.C5LINK_CS" />
    <trace from=".U20 > .LINK_CS" to="net.C5LINK_CS" />
    <trace from=".U10 > .C5LINK_DRDY" to="net.C5LINK_DRDY" />
    <trace from=".U20 > .LINK_DRDY" to="net.C5LINK_DRDY" />
    <trace from=".U10 > .C5_EN" to="net.C5_EN" />
    <trace from=".U20 > .C5_EN" to="net.C5_EN" />
    <trace from=".R_C5EN > .pin1" to="net.C5_EN" />
    <trace from=".R_C5EN > .pin2" to="net.V3V3" />
    <trace from=".C_C5EN > .pin1" to="net.C5_EN" />
    <trace from=".C_C5EN > .pin2" to="net.GND" />
    <trace from=".U10 > .C5_BOOT" to="net.C5_BOOT" />
    <trace from=".U20 > .C5_BOOT_26" to="net.C5_BOOT" />
    <trace from=".U20 > .C5_BOOT_28" to="net.C5_BOOT" />
    <trace from=".R_C5BOOT > .pin1" to="net.C5_BOOT" />
    <trace from=".R_C5BOOT > .pin2" to="net.V3V3" />
    <trace from=".U20 > .STRAP27" to=".R_C5S27 > .pin1" />
    <trace from=".R_C5S27 > .pin2" to="net.V3V3" />

    {/* --- S3 ↔ C5 flash bridge UART0 --- */}
    <trace from=".U10 > .C5_FLASH_TX" to="net.C5_FLASH_TX" />
    <trace from=".U20 > .U0RXD" to="net.C5_FLASH_TX" />
    <trace from=".U10 > .C5_FLASH_RX" to="net.C5_FLASH_RX" />
    <trace from=".U20 > .U0TXD" to="net.C5_FLASH_RX" />

    {/* --- C5 own USB-C (data-only, Sheet 1) --- */}
    <trace from=".U20 > .USB_DM_C5" to="net.USB_DM_C5" />
    <trace from=".U20 > .USB_DP_C5" to="net.USB_DP_C5" />
    <trace from=".U20 > .V3V3" to="net.V3V3" />
    <trace from=".U20 > .GND" to="net.GND" />

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
  </board>
)
