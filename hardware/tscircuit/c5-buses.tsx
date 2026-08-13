// Leshy2 — Sheet 2: MCU + buses  (FAB-READY draft, engine-pulled footprints by LCSC number)
//
// METHOD: every module/IC uses footprint="jlcpcb:C<number>". The parts engine supplies
// the REAL pads AND the REAL pad NAMES from the LCSC/EasyEDA database, so no pin numbers
// are typed by hand. Traces reference those engine pad names (verified via
// `tsci export -f readable-netlist`, WITHOUT --disable-parts-engine).
//
// Pad-name sources of truth (engine probe of each footprint):
//   U10  ESP32-S3-WROOM-1U-N8R2  -> jlcpcb:C3013944
//        Module pads: GND1, 3V3, EN, IO0..IO21, IO35..IO42, IO45..IO48, TXD0(=GPIO43),
//        RXD0(=GPIO44), GND2, GND3..GND11 (EP thermal copies).
//   U20  ESP32-C5-WROOM-1U-N8R4  -> jlcpcb:C49308183  (alt: C48533540 "…-1U", same pads)
//        Module pads: GND1, 3V3, EN, IO0..IO10, IO13, IO14, IO23..IO28, TX0(=GPIO11 U0TXD),
//        RX0(=GPIO12 U0RXD), NC1/NC2, ANT2 (u.FL feed), GND2/3/12/13, GND4..GND11 (EP copies).
//   U11  SN74HC138PWR TSSOP-16   -> jlcpcb:C157527
//        Pads: A,B,C,#G2A(pin4),#G2B(pin5),G1,Y0..Y7,GND,VCC.  (#G2A/#G2B referenced by pin#.)
//   U12/U13 PCA9555PW,118 TSSOP-24 -> jlcpcb:C128392
//        Pads: INT,A0,A1,A2,SCL,SDA,VDD,VSS, IO0_0..IO0_7 (=P00..P07), IO1_0..IO1_7 (=P10..P17).
//
// GPIO->pad mapping rule: every S3/C5 signal sits on the module pad matching ITS GPIO number
// (net names unchanged; only the physical pad changes). Datasheet-confirmed:
//   S3 TXD0=GPIO43=U0TXD, RXD0=GPIO44=U0RXD.  C5 U0TXD=GPIO11 (pad TX0), U0RXD=GPIO12 (pad RX0).
//
// DESIGN CORRECTION (found by realizing against the real module): the ESP32-S3-WROOM-1U does NOT
//    bond out GPIO33 or GPIO34 (module pin table jumps IO21 -> IO35), so the base plan of
//    C5_EN=GPIO33 / C5_BOOT=GPIO34 is invalid — those pads do not exist (independent of PSRAM;
//    "quad frees 33-37" holds only for 35-37). Every other freed pad (IO35..IO48) is already used.
//    RESOLVED: C5_EN and C5_BOOT are driven from PCA9555 #2 (U13.P05/P06) instead — both are slow,
//    set-once lines, and the existing pull-ups (R_C5EN/R_C5BOOT) hold safe defaults at C5 power-on.
export default () => (
  <board width="120mm" height="90mm">
    {/* ===================== U10 — ESP32-S3-WROOM-1U-N8R2 (main brain) ===================== */}
    <chip name="U10" footprint="jlcpcb:C3013944" />

    {/* ===================== U20 — ESP32-C5-WROOM-1U (co-processor) ===================== */}
    <chip name="U20" footprint="jlcpcb:C49308183" />

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
    <resistor name="R_PCA_INT" resistance="10k" footprint="0402" /> {/* pull-up for the wired-OR open-drain PCA9555 INT (3 expanders -> GPIO48) */}
    <trace from=".R_PCA_INT > .pin1" to="net.PCA9555_INT" /><trace from=".R_PCA_INT > .pin2" to="net.V3V3" />
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
    <trace from=".U20 > .IO23" to="net.C5LINK_SCK" />   {/* C5 GPIO23 LINK_SCK */}
    <trace from=".U20 > .IO24" to="net.C5LINK_MOSI" />  {/* C5 GPIO24 LINK_MOSI */}
    <trace from=".U20 > .IO6" to="net.C5LINK_MISO" />   {/* C5 GPIO6 LINK_MISO */}
    <trace from=".U20 > .IO8" to="net.C5LINK_CS" />     {/* C5 GPIO8 LINK_CS */}
    <trace from=".U20 > .IO9" to="net.C5LINK_DRDY" />   {/* C5 GPIO9 DRDY */}
    <trace from=".U20 > .EN" to="net.C5_EN" />          {/* C5 EN pad */}
    <trace from=".R_C5EN > .pin1" to="net.C5_EN" />
    <trace from=".R_C5EN > .pin2" to="net.V3V3" />
    <trace from=".C_C5EN > .pin1" to="net.C5_EN" />
    <trace from=".C_C5EN > .pin2" to="net.GND" />
    <trace from=".U20 > .IO26" to="net.C5_BOOT" />      {/* C5 GPIO26 (download strap) */}
    <trace from=".U20 > .IO28" to="net.C5_BOOT" />      {/* C5 GPIO28 (tied to 26) */}
    <trace from=".R_C5BOOT > .pin1" to="net.C5_BOOT" />
    <trace from=".R_C5BOOT > .pin2" to="net.V3V3" />
    <trace from=".U20 > .IO27" to=".R_C5S27 > .pin1" /> {/* C5 GPIO27 strap pull-high */}
    <trace from=".R_C5S27 > .pin2" to="net.V3V3" />

    {/* --- S3 <-> C5 flash bridge UART0 --- */}
    <trace from=".U10 > .TXD0" to="net.C5_FLASH_TX" />
    <trace from=".U20 > .RX0" to="net.C5_FLASH_TX" />   {/* C5 U0RXD (GPIO12) */}
    <trace from=".U10 > .RXD0" to="net.C5_FLASH_RX" />
    <trace from=".U20 > .TX0" to="net.C5_FLASH_RX" />   {/* C5 U0TXD (GPIO11) */}

    {/* --- C5 own USB-C (data-only, Sheet 1) --- */}
    <trace from=".U20 > .IO13" to="net.USB_DM_C5" />    {/* C5 GPIO13 */}
    <trace from=".U20 > .IO14" to="net.USB_DP_C5" />    {/* C5 GPIO14 */}
    <trace from=".U20 > .3V3" to="net.V3V3" />
    {/* all C5 module GND pads + EP thermal copies -> GND */}
    <trace from=".U20 > .GND1" to="net.GND" />
    <trace from=".U20 > .GND2" to="net.GND" />
    <trace from=".U20 > .GND3" to="net.GND" />
    <trace from=".U20 > .GND4" to="net.GND" />
    <trace from=".U20 > .GND5" to="net.GND" />
    <trace from=".U20 > .GND6" to="net.GND" />
    <trace from=".U20 > .GND7" to="net.GND" />
    <trace from=".U20 > .GND8" to="net.GND" />
    <trace from=".U20 > .GND9" to="net.GND" />
    <trace from=".U20 > .GND10" to="net.GND" />
    <trace from=".U20 > .GND11" to="net.GND" />
    <trace from=".U20 > .GND12" to="net.GND" />
    <trace from=".U20 > .GND13" to="net.GND" />
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
  </board>
)
