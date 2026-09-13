"""Finite S3 UART0/Hub separation guard; no boot or link-timing qualification.

ESP32-S3-WROOM-1U datasheet v1.8 table 3-1: GPIO43/U0TXD is module
pad 37; GPIO44/U0RXD is pad 36. GPIO7/8 are module pads 7/12.
https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf
"""

from collections import Counter


PROJECT = "LESHY2-UI-R2"
NATIVE_PREFIX = "/UI_10_S3_DISPLAY_TOUCH/"
S3_DEVICE = "esp32_s3_wroom_1u_n16r8"
S3_MPN = "ESP32-S3-WROOM-1U-N16R8"
# endpoint: (reference, physical pad, exact canonical net, selected device)
PINS = {
    "s3.GPIO7": ("U1", "7", "S3_HUB_D2", S3_DEVICE),
    "s3.GPIO8": ("U1", "12", "S3_HUB_D3", S3_DEVICE),
    "s3.GPIO43": ("U1", "37", "S3_UART_SERVICE_TX", S3_DEVICE),
    "s3.GPIO44": ("U1", "36", "S3_UART_SERVICE_RX", S3_DEVICE),
    "hub_rp.GPIO2": ("U28", "79", "S3_HUB_D2", "rp2354b_a4"),
    "hub_rp.GPIO3": ("U28", "80", "S3_HUB_D3", "rp2354b_a4"),
    "s3_dbg0_series.END_1": ("R4", "1", "S3_DBG0_CONNECTOR", "yageo_rc0402fr_07470rl"),
    "s3_dbg0_series.END_2": ("R4", "2", "S3_UART_SERVICE_TX", "yageo_rc0402fr_07470rl"),
    "s3_dbg1_series.END_1": ("R5", "1", "S3_DBG1_CONNECTOR", "yageo_rc0402fr_07470rl"),
    "s3_dbg1_series.END_2": ("R5", "2", "S3_UART_SERVICE_RX", "yageo_rc0402fr_07470rl"),
    "s3_dbg_esd.D2_PLUS": ("U2", "4", "S3_DBG0_CONNECTOR", "ti_tpd4e05u06_dqar"),
    "s3_dbg_esd.D2_MINUS": ("U2", "5", "S3_DBG1_CONNECTOR", "ti_tpd4e05u06_dqar"),
    "s3_dbg_header.P5": ("J2", "5", "S3_DBG0_CONNECTOR", "samtec_ftsh_105_01_l_dv_k_p_tr"),
    "s3_dbg_header.P6": ("J2", "6", "S3_DBG1_CONNECTOR", "samtec_ftsh_105_01_l_dv_k_p_tr"),
}
NETS = frozenset(pin[2] for pin in PINS.values())


def topology_checks(rows, devices):
    """Check identities, every required leg and exact membership of six nets."""
    checks = {"identity:s3_module": devices.get(S3_DEVICE, {}).get("mpn") == S3_MPN}
    for endpoint, (reference, physical, net, device_id) in PINS.items():
        instance, contact = endpoint.split(".", 1)
        matches = [row for row in rows if row.get("endpoint") == endpoint]
        expected = {
            "project": PROJECT, "reference": reference, "physical": physical,
            "net": net, "device_id": device_id, "instance": instance,
            "contact": contact, "disposition": "connected",
        }
        definition = devices.get(device_id, {}).get("contacts", {}).get(contact, {})
        checks["pin:" + endpoint] = (
            len(matches) == 1
            and all(matches[0].get(key) == value for key, value in expected.items())
            and definition.get("physical") == physical
        )
    for net in sorted(NETS):
        expected = Counter(endpoint for endpoint, pin in PINS.items() if pin[2] == net)
        actual = Counter(row.get("endpoint") for row in rows
                         if row.get("project") == PROJECT and row.get("net") == net)
        checks["members:" + net] = actual == expected
    return checks


def native_pad_checks(pads):
    """Check read-only (reference, physical, full net name) PCB pad tuples.

    Exact full net names deliberately reject stale sheet aliases. Counter
    comparison also rejects duplicate lands and additional/shared endpoints.
    No copper completion or electrical timing is inferred from pad membership.
    """
    pads = list(pads)
    checks = {}
    for net in sorted(NETS):
        full_net = NATIVE_PREFIX + net
        expected = Counter((pin[0], pin[1]) for pin in PINS.values() if pin[2] == net)
        actual = Counter((ref, physical) for ref, physical, name in pads if name == full_net)
        checks["native_members:" + net] = actual == expected
    for endpoint, (reference, physical, net, _) in PINS.items():
        actual = [name for ref, pad, name in pads if (ref, pad) == (reference, physical)]
        checks["native_pin:" + endpoint] = actual == [NATIVE_PREFIX + net]
    return checks
