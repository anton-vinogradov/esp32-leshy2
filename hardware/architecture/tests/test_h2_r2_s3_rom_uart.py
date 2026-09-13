"""S3 GPIO swap guards only; no claim of sampled boot or qualified 40-MHz SPI."""

import copy
import importlib.util
import json
from pathlib import Path
import unittest

try:
    import pcbnew
except ImportError:
    pcbnew = None


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/ecad/h2_r2_s3_rom_uart.py"
# Independent physical expectation, not populated from the guard under test.
UART_TX = {("U1", "37"), ("R4", "2")}
UART_RX = {("U1", "36"), ("R5", "2")}
HUB_D2 = {("U1", "7"), ("U28", "79")}
HUB_D3 = {("U1", "12"), ("U28", "80")}
PIN_NETS = {**{pin: "S3_UART_SERVICE_TX" for pin in UART_TX},
            **{pin: "S3_UART_SERVICE_RX" for pin in UART_RX},
            **{pin: "S3_HUB_D2" for pin in HUB_D2},
            **{pin: "S3_HUB_D3" for pin in HUB_D3},
            ("R4", "1"): "S3_DBG0_CONNECTOR", ("J2", "5"): "S3_DBG0_CONNECTOR",
            ("U2", "4"): "S3_DBG0_CONNECTOR",
            ("R5", "1"): "S3_DBG1_CONNECTOR", ("J2", "6"): "S3_DBG1_CONNECTOR",
            ("U2", "5"): "S3_DBG1_CONNECTOR"}


class S3RomUartTopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("s3_rom_uart_guard", SCRIPT)
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        cls.rows = json.loads((ROOT / "hardware/ecad/generated/H2-R2-native-net-ledger.json").read_text())["rows"]
        cls.devices = json.loads((ROOT / "hardware/architecture/devices.json").read_text())["devices"]

    def checks(self, rows=None, devices=None):
        return self.module.topology_checks(self.rows if rows is None else rows,
                                           self.devices if devices is None else devices)

    def test_live_ledger_has_default_rom_uart_separate_from_hub(self):
        result = self.checks()
        self.assertEqual(21, len(result))
        self.assertTrue(all(result.values()), result)
        for pin, net in PIN_NETS.items():
            matches = [row for row in self.rows if row["project"] == "LESHY2-UI-R2"
                       and (row["reference"], row["physical"]) == pin]
            self.assertEqual([net], [row["net"] for row in matches], pin)

    def test_every_required_leg_rejects_missing_duplicate_or_misidentified_rows(self):
        for endpoint in self.module.PINS:
            for mutation in ("missing", "duplicate", "net", "disposition", "physical",
                             "reference", "project", "device_id", "instance", "contact"):
                with self.subTest(endpoint=endpoint, mutation=mutation):
                    rows = copy.deepcopy(self.rows)
                    row = next(row for row in rows if row["endpoint"] == endpoint)
                    if mutation == "missing":
                        rows.remove(row)
                    elif mutation == "duplicate":
                        rows.append(copy.deepcopy(row))
                    else:
                        row[mutation] = "WRONG"
                    self.assertFalse(self.checks(rows=rows)["pin:" + endpoint])

    def test_manufacturer_physical_mapping_cannot_follow_a_wrong_native_mapping(self):
        for endpoint in ("s3.GPIO7", "s3.GPIO8", "s3.GPIO43", "s3.GPIO44"):
            devices = copy.deepcopy(self.devices)
            contact = endpoint.split(".")[1]
            devices[self.module.S3_DEVICE]["contacts"][contact]["physical"] = "999"
            self.assertFalse(self.checks(devices=devices)["pin:" + endpoint])
        devices = copy.deepcopy(self.devices)
        devices[self.module.S3_DEVICE]["mpn"] = "DIFFERENT_MODULE"
        self.assertFalse(self.checks(devices=devices)["identity:s3_module"])

    def test_extra_uart_or_hub_endpoint_fails_exact_membership(self):
        for net in self.module.NETS:
            rows = copy.deepcopy(self.rows)
            rows.append({"endpoint": "unexpected.GPIO", "project": "LESHY2-UI-R2",
                         "disposition": "connected", "net": net})
            self.assertFalse(self.checks(rows=rows)["members:" + net])

    def test_historical_uart1_hub_uart0_swap_is_rejected(self):
        rows = copy.deepcopy(self.rows)
        old = {"s3.GPIO7": "S3_UART_SERVICE_TX", "s3.GPIO8": "S3_UART_SERVICE_RX",
               "s3.GPIO43": "S3_HUB_D2", "s3.GPIO44": "S3_HUB_D3"}
        for row in rows:
            if row["endpoint"] in old:
                row["net"] = old[row["endpoint"]]
        result = self.checks(rows=rows)
        for endpoint in old:
            self.assertFalse(result["pin:" + endpoint])

    def test_native_guard_rejects_alias_missing_duplicate_and_shared_hub_pads(self):
        pads = [(ref, pad, "/UI_10_S3_DISPLAY_TOUCH/" + net)
                for (ref, pad), net in PIN_NETS.items()]
        self.assertTrue(all(self.module.native_pad_checks(pads).values()))
        for index, (ref, pad, net) in enumerate(pads):
            for mutation in ("missing", "duplicate", "alias", "wrong_pin", "extra_hub"):
                with self.subTest(ref=ref, pad=pad, mutation=mutation):
                    changed = list(pads)
                    if mutation == "missing":
                        changed.pop(index)
                    elif mutation == "duplicate":
                        changed.append(changed[index])
                    elif mutation == "alias":
                        changed[index] = (ref, pad, net.replace("DISPLAY_TOUCH", "CORE_MEMORY_BOOT"))
                    elif mutation == "wrong_pin":
                        changed[index] = (ref, "999", net)
                    else:
                        changed.append(("U28", "1", net))
                    self.assertFalse(all(self.module.native_pad_checks(changed).values()))

    @unittest.skipUnless(pcbnew, "Requires KiCad Python; read-only native pad check")
    def test_live_native_pads_match_full_uart_and_hub_topology(self):
        board = pcbnew.LoadBoard(str(ROOT / "hardware/ecad/kicad/LESHY2-UI-R2/LESHY2-UI-R2.kicad_pcb"))
        pads = [(fp.GetReference(), pad.GetNumber(), str(pad.GetNetname()))
                for fp in board.GetFootprints() for pad in fp.Pads()]
        result = self.module.native_pad_checks(pads)
        self.assertEqual(20, len(result))
        self.assertTrue(all(result.values()), result)


if __name__ == "__main__":
    unittest.main()
