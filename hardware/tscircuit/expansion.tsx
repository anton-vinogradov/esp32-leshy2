// Leshy2 — Sheet 5: Expansion + GPS  (transcribed from hardware/expansion/expansion.md)
// NOTE: ICs/connectors are generic <chip> with our logical pinout; real
// footprints/part numbers get assigned before PCB. 2-pin passive-ish parts
// (Schottky, supercap) are modeled as resistor proxies for capture.
export default () => (
  <board width="80mm" height="60mm">
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
  </board>
)
