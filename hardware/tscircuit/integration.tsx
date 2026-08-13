// Leshy2 — INTEGRATION sheet (board-level parts that span subsystems).
// Display FPC + antenna u.FL array + full UI control set (D-pad/BACK/OPTIONS/STOP/F1/F2) + 3rd PCA9555 (U14, 0x22).
// Real engine footprints (jlcpcb:C...). Merged into board.tsx by merge.py — do not hand-merge.
export default () => (
  <board width="400mm" height="300mm">

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

    {/* --- Pull-ups: PCA9555 has NO internal pull-ups -> every button input needs 10k to +3V3 to read high when released (active-low). --- */}
    <resistor name="Rpu_up"   resistance="10k" footprint="0402" /><trace from=".Rpu_up > .pin1"   to=".U14 > .IO0_0" /><trace from=".Rpu_up > .pin2"   to="net.V3V3" />
    <resistor name="Rpu_dn"   resistance="10k" footprint="0402" /><trace from=".Rpu_dn > .pin1"   to=".U14 > .IO0_1" /><trace from=".Rpu_dn > .pin2"   to="net.V3V3" />
    <resistor name="Rpu_lf"   resistance="10k" footprint="0402" /><trace from=".Rpu_lf > .pin1"   to=".U14 > .IO0_2" /><trace from=".Rpu_lf > .pin2"   to="net.V3V3" />
    <resistor name="Rpu_rt"   resistance="10k" footprint="0402" /><trace from=".Rpu_rt > .pin1"   to=".U14 > .IO0_3" /><trace from=".Rpu_rt > .pin2"   to="net.V3V3" />
    <resistor name="Rpu_ok"   resistance="10k" footprint="0402" /><trace from=".Rpu_ok > .pin1"   to=".U14 > .IO0_4" /><trace from=".Rpu_ok > .pin2"   to="net.V3V3" />
    <resistor name="Rpu_back" resistance="10k" footprint="0402" /><trace from=".Rpu_back > .pin1" to=".U14 > .IO0_5" /><trace from=".Rpu_back > .pin2" to="net.V3V3" />
    <resistor name="Rpu_opt"  resistance="10k" footprint="0402" /><trace from=".Rpu_opt > .pin1"  to=".U14 > .IO0_6" /><trace from=".Rpu_opt > .pin2"  to="net.V3V3" />
    <resistor name="Rpu_stop" resistance="10k" footprint="0402" /><trace from=".Rpu_stop > .pin1" to=".U14 > .IO0_7" /><trace from=".Rpu_stop > .pin2" to="net.V3V3" />
    <resistor name="Rpu_f1"   resistance="10k" footprint="0402" /><trace from=".Rpu_f1 > .pin1"   to=".U14 > .IO1_0" /><trace from=".Rpu_f1 > .pin2"   to="net.V3V3" />
    <resistor name="Rpu_f2"   resistance="10k" footprint="0402" /><trace from=".Rpu_f2 > .pin1"   to=".U14 > .IO1_1" /><trace from=".Rpu_f2 > .pin2"   to="net.V3V3" />

  </board>
)
