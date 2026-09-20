"""Fixed current C5/IR EV load inventory, not a whole-network electrical model.

Reuses native/source guards and reviewed contacts. Nominal resistor values are
checked against exact current device identities; no source I-V model is invented.
"""

import copy
from pathlib import Path

from hardware.verification import h6_r2_power_domain_crossings as crossings

RF, UI = "LESHY2-RF-R2", "LESHY2-UI-R2"
AON, GND, ANY = "AON_SAFE_3V3", "POWER_GROUND", "ANY_TX_AON_N"
RESISTORS = {
    "10000": ("yageo_rc0402fr_0710kl", "Yageo RC0402FR-0710KL", "10kohm_1pct_0402_main_feedback_bottom_resistor"),
    "12000": ("yageo_rc0402fr_0712kl", "Yageo RC0402FR-0712KL", "12kohm_1pct_0402_voice_feedback_bottom_resistor"),
    "100000": ("yageo_rc0402fr_07100kl", "Yageo RC0402FR-07100KL", "100kohm_1pct_0402_charger_ilim_bottom_resistor"),
    "1000000": ("yageo_rc0402fr_071ml", "Yageo RC0402FR-071ML", "1megohm_1pct_0402_service_vbus_bleeder"),
    "2200": ("uniroyal_0402wgf2201tce", "UNI-ROYAL 0402WGF2201TCE", "2_2kohm_1pct_0402_i2c_pullup_resistor"),
}
DEVICES = {
    "comparator": ("ti_tlv1824_pwr", "TLV1824PWR"),
    "led": ("liteon_ltst_c190krkt", "LTST-C190KRKT"),
    "diode": ("onsemi_bat54alt1g", "BAT54ALT1G"),
    "tca": ("ti_tca9535_pwr", "TCA9535PWR"),
    "c5": ("esp32_c5_wroom_1u_n8r8", "ESP32-C5-WROOM-1U-N8R8"),
    "safety": ("ti_mspm0c1106_sdgs20r", "Texas Instruments MSPM0C1106SDGS20R"),
    "aggregate_buffer": ("ti_sn74lvc1g07_dckr", "SN74LVC1G07DCKR"),
    "m1_rf": ("hirose_fx8c_80s_sv5_92", "Hirose FX8C-80S-SV5(92)"),
    "m1_ui": ("hirose_fx8c_80p_sv1_92", "Hirose FX8C-80P-SV1(92)"),
}
CHANNELS = (
    {"id": "c5", "net": "EV_N1_C5", "m1": "42", "tca": ("P01", "5"), "diode": "0",
     "led_ref": "D1", "series_ref": "R26", "pullup_ref": "R88", "hysteresis_ref": "R86",
     "top_ref": "R208", "bottom_ref": "R89", "bottom_ohm": "10000", "threshold": "EV_THRESH_1_C5",
     "detector": "C5_DETECT_V", "out": ("OUT2", "1"), "in_p": ("IN2_P", "7"), "in_n": ("IN2_N", "6"),
     "gpio": ("GPIO23", "21")},
    {"id": "ir", "net": "EV_N7_IR", "m1": "46", "tca": ("P07", "11"), "diode": "3",
     "led_ref": "D5", "series_ref": "R33", "pullup_ref": "R124", "hysteresis_ref": "R122",
     "top_ref": "R211", "bottom_ref": "R210", "bottom_ohm": "12000", "threshold": "EV_THRESH_7_IR",
     "detector": "IR_DETECT_V", "out": ("OUT3", "14"), "in_p": ("IN3_P", "9"), "in_n": ("IN3_N", "8"),
     "gpio": ("GPIO24", "23")},
)
OTHER_DIODE_NETS = ("EV_N0_S3", "EV_N1_C5", "EV_N2_NRF0", "EV_N3_NRF1", "EV_N4_NRF2",
                    "EV_N5_CC", "EV_N6_VOICE", "EV_N7_IR", "EV_N8_LORA_EXT", "EV_N9_U219_NFC")


def source_paths():
    return [Path(__file__)]


def extract(data, reviews):
    """Return decimal-string nominal values and a checked, baseline-only frontier.

    The caller owns snapshot-before/after guarding across any subsequent solver.
    This extractor validates current ledger provenance and does not mutate inputs.
    """
    require = crossings.require
    require(data["nets"].get("artifact") == "H2-R2-native-net-ledger"
            and all("sources" in data[name] for name in crossings.AUTHORITY_KEYS), "baseline native provenance required")
    contracts = {key: crossings.load(crossings.ROOT / path) for key, path in crossings.LEDGER_CONTRACTS.items()}
    crossings.validate_provenance(data, contracts, crossings.snapshot())
    native, by_instance = crossings.indexes(data, reviews)
    parts, pins = {}, {}
    for key, rows in by_instance.items():
        for row in rows:
            pins[row["project"], row["endpoint"]] = row

    def part(project, instance, reference, identity):
        device_id, mpn = identity[:2]
        row = native.get((project, instance), {})
        device = data["devices"]["devices"][device_id]
        require(row.get("reference") == reference and row.get("device_id") == device_id
                and row.get("mpn") == device.get("mpn") == mpn, "EV exact component identity differs: " + instance)
        if len(identity) == 3:
            require(device.get("kind") == identity[2], "EV nominal resistor value/tolerance differs: " + instance)
        else:
            require(device_id == DEVICES["led"][0] or reviews.get(device_id, {}).get("mpn") == mpn,
                    "EV reviewed MPN differs: " + instance)
        source = device.get("source", {})
        require(all(source.get(field) for field in ("url", "version", "checked")), "EV component source metadata missing")
        parts[project + ":" + instance] = {"project": project, "instance": instance, "reference": reference,
            "device_id": device_id, "mpn": mpn, "source": source}

    def pin(project, instance, contact, physical, net, pin_type, pads=None):
        endpoint = instance + "." + contact
        row = pins.get((project, endpoint), {})
        require(row.get("physical") == physical and row.get("pads") == (pads or [physical])
                and row.get("net") == net and row.get("type") == pin_type
                and row.get("disposition") == ("no_connect" if net is None else "connected"),
                "EV exact contact/net/type differs: " + endpoint)
        return (project, endpoint)

    def members(net, expected):
        actual = {(row["project"], row["endpoint"]) for row in pins.values() if row["net"] == net}
        require(actual == set(expected), "EV load membership differs: " + net)
        return [crossings.pin_summary(pins[key]) for key in sorted(actual)]

    def resistor(project, instance, reference, ohm, first, second):
        part(project, instance, reference, RESISTORS[ohm])
        # The current reviewed pin map covers these Yageo parts, not the
        # UNI-ROYAL series resistor; preserve that distinction in the fixture.
        pin_type = "unreviewed" if ohm == "2200" else "passive"
        return (pin(project, instance, "END_1", "1", first, pin_type),
                pin(project, instance, "END_2", "2", second, pin_type))

    for project, instance, reference, device in ((RF, "m1_rf_receptacle", "J12", "m1_rf"),
            (UI, "m1_ui_plug", "J18", "m1_ui"), (RF, "evidence_mask", "U111", "tca"),
            (RF, "safety_controller", "U127", "safety"), (RF, "slow_io_s3_evidence_iso", "U132", "aggregate_buffer"),
            (UI, "evidence_cmp_a", "U53", "comparator"), (UI, "c5", "U14", "c5")):
        part(project, instance, reference, DEVICES[device])
    for project, instance, positive, negative in ((RF, "evidence_mask", ("VCC", "24"), ("GND", "12")),
            (RF, "safety_controller", ("VDD", "6"), ("VSS", "7")),
            (RF, "slow_io_s3_evidence_iso", ("VCC", "5"), ("GND", "3")),
            (UI, "evidence_cmp_a", ("VPLUS", "3"), ("VMINUS", "12"))):
        pin(project, instance, *positive, AON, "power_in")
        pin(project, instance, *negative, GND, "power_in")
    pin(UI, "c5", "3V3", "2", "3V3_MAIN", "power_in")
    pin(UI, "c5", "GND", "1/28/29/30/32", GND, "power_in", ["1", "28", "29", "30", "32"])
    pin(RF, "slow_io_s3_evidence_iso", "NC", "1", None, "no_connect")
    pin(RF, "slow_io_s3_evidence_iso", "Y", "4", "RF_ANY_TX_N", "open_collector")

    any_members = [resistor(RF, "any_tx_aon_pullup", "R249", "10000", AON, ANY)[1],
                   pin(RF, "safety_controller", "PA22", "17", ANY, "bidirectional"),
                   pin(RF, "slow_io_s3_evidence_iso", "A", "2", ANY, "input")]
    diode_frontier = []
    for index in range(5):
        instance = "evidence_or_" + str(index)
        part(RF, instance, "U" + str(112 + index), DEVICES["diode"])
        any_members.append(pin(RF, instance, "A_COMMON", "3", ANY, "passive"))
        for offset, contact in enumerate(("K1", "K2")):
            key = pin(RF, instance, contact, str(offset + 1), OTHER_DIODE_NETS[index * 2 + offset], "passive")
            diode_frontier.append(crossings.pin_summary(pins[key]))

    channels = []
    for channel in CHANNELS:
        name, net, threshold = channel["id"], channel["net"], channel["threshold"]
        m1 = [row for row in data["h0"]["interboard_rebaseline"]["pin_map"] if str(row["contact"]) == channel["m1"]]
        require(len(m1) == 1 and m1[0]["net"] == net and m1[0]["class"] == "tx_evidence", "EV H0 M1 assignment differs")
        expected = [pin(RF, "m1_rf_receptacle", "P" + channel["m1"], channel["m1"], net, "passive"),
                    pin(UI, "m1_ui_plug", "P" + channel["m1"], channel["m1"], net, "passive"),
                    pin(RF, "evidence_mask", *channel["tca"], net, "bidirectional"),
                    pin(RF, "evidence_or_" + channel["diode"], "K2", "2", net, "passive"),
                    pin(UI, "evidence_cmp_a", *channel["out"], net, "open_collector"),
                    pin(UI, "c5", *channel["gpio"], net, "bidirectional")]
        pin(UI, "evidence_cmp_a", *channel["in_n"], channel["detector"], "input")
        threshold_members = [pin(UI, "evidence_cmp_a", *channel["in_p"], threshold, "input")]
        led, anode = name + "_tx_led", name.upper() + "_TX_LED_A"
        part(UI, led, channel["led_ref"], DEVICES["led"])
        expected.append(pin(UI, led, "K", "cathode land", net, "unreviewed", ["1"]))
        led_anode = pin(UI, led, "A", "anode land", anode, "unreviewed", ["2"])
        series = resistor(UI, led + "_series", channel["series_ref"], "2200", AON, anode)
        expected.append(resistor(UI, name + "_evidence_output_pullup", channel["pullup_ref"], "10000", AON, net)[1])
        hysteresis = resistor(UI, name + "_evidence_hysteresis", channel["hysteresis_ref"], "1000000", net, threshold)
        expected.append(hysteresis[0])
        threshold_members += [hysteresis[1],
            resistor(UI, name + "_evidence_threshold_top", channel["top_ref"], "100000", AON, threshold)[1],
            resistor(UI, name + "_evidence_threshold_bottom", channel["bottom_ref"], channel["bottom_ohm"], threshold, GND)[0]]
        channels.append({"id": name, "net": net, "pullup_ohm": "10000", "led_series_ohm": "2200",
            "hysteresis_ohm": "1000000", "threshold_top_ohm": "100000", "threshold_bottom_ohm": channel["bottom_ohm"],
            "diode_or_pullup_ohm": "10000", "m1_contact": channel["m1"],
            "ev_members": members(net, expected), "threshold_members": members(threshold, threshold_members),
            "led_anode_members": members(anode, [led_anode, series[1]])})

    return copy.deepcopy({"status": "fixed_baseline_inventory_verified", "baseline_only": True, "qualified": False,
        "full_EV_qualified": False, "input_provenance_verified": True, "channels": channels,
        "nominal_value_basis": "Exact current device-register MPN/kind fixtures; source links are provenance, not fresh numerical datasheet review",
        "resistor_initial_tolerance_fraction": "0.01", "tolerance_scope": "Initial nominal-value diagnostic only; temperature, voltage and life drift unqualified",
        "components": parts, "shared_any_node": {"net": ANY, "pullup_ohm": "10000", "members": members(ANY, any_members),
            "diode_cathode_frontier": diode_frontier, "other_ev_loads_traversed": False},
        "unresolved": ["TCA and Safety configurable-pin modes, drive contention and input leakage remain unproven",
            "Other diode-OR branches, Schottky I-V/reverse leakage and aggregate-node loads are outside this fixture's electrical model",
            "LED forward-voltage/leakage/brightness models are not established; a shorted-LED stress case is not an exact LED model",
            "Comparator loaded VOL, output leakage, thresholds, shared package conditions and power sequences need source-conditioned checks",
            "C5 input loading/off-state tolerance and delivered rail/ground/temperature conditions are not qualified"]})
