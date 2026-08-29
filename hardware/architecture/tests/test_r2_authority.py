import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "hardware/architecture/r2_authority.py"
SPEC = importlib.util.spec_from_file_location("r2_authority", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class R2AuthorityTest(unittest.TestCase):
    def current_candidate(self):
        policy = copy.deepcopy(MODULE.load(MODULE.POLICY))
        h0 = copy.deepcopy(MODULE.load(MODULE.H0))
        h2 = copy.deepcopy(MODULE.load(MODULE.H2))
        h2_m1 = copy.deepcopy(MODULE.load(MODULE.H2_M1))
        pins = copy.deepcopy(MODULE.load(MODULE.PIN_AUTHORITY))
        c5_mux = copy.deepcopy(MODULE.load(MODULE.C5_MUX))
        g2f = copy.deepcopy(MODULE.load(MODULE.G2F))
        retained_maps = MODULE.retained_controller_pin_maps(g2f, c5_mux)
        physical_h1 = copy.deepcopy(MODULE.load(MODULE.PHYSICAL_H1))
        pins["authority_chain"]["remaining_h2_gates"] = []
        physical_h1["status"] = "reviewed"
        physical_h1["current_h1_blockers"] = []
        physical_h1["pre_r2_h2_gates"] = []
        policy["current_r2_h2_export"] = True
        policy["exact_c5_mux_status"] = "electrical and production contract closed"
        domains = []
        for row in h0["compute_domains"]:
            domain = {"id": row["id"], "instance": row["id"], "mpn": row["mpn"]}
            if row["id"] == "s3":
                domain["pin_map"] = copy.deepcopy(h0["s3"]["pin_map"])
            elif row["id"] in {"c5", "pack", "safety"}:
                domain["pin_map"] = copy.deepcopy(retained_maps[row["id"]])
            elif row["id"] in {"hub_rp", "rf_rp"}:
                domain["pin_map"] = copy.deepcopy(pins[row["id"]]["pin_map"])
            domains.append(domain)
        h2["bsp"]["domains"] = domains
        h2["integration_contract"]["controllers"] = copy.deepcopy(domains)
        hashes = {
            str(MODULE.H0.relative_to(MODULE.REPO)): MODULE.digest(MODULE.H0),
            str(MODULE.PIN_AUTHORITY.relative_to(MODULE.REPO)): MODULE.digest(MODULE.PIN_AUTHORITY),
            str(MODULE.C5_MUX.relative_to(MODULE.REPO)): MODULE.digest(MODULE.C5_MUX),
            str(MODULE.G2F.relative_to(MODULE.REPO)): MODULE.digest(MODULE.G2F),
            str(MODULE.U219_CONTRACT.relative_to(MODULE.REPO)): MODULE.digest(MODULE.U219_CONTRACT),
            str(MODULE.PHYSICAL_H1.relative_to(MODULE.REPO)): MODULE.digest(MODULE.PHYSICAL_H1),
        }
        h2["source_sha256"].update(hashes)
        h2["r2_reconciliation"] = {
            "hardware_marker": pins["marker"],
            "hardware_sources": hashes,
            "domain_contracts": MODULE.expected_domain_contracts(
                h0["compute_domains"], h0, pins, c5_mux, g2f
            ),
            "hub_pin_map": copy.deepcopy(pins["hub_rp"]["pin_map"]),
            "rear_pin_map": copy.deepcopy(pins["rf_rp"]["pin_map"]),
            "c5_sdio_service_mux": c5_mux,
            "interboard": MODULE.expected_m1(h0),
            "pre_h2_gates": [],
            "physical_h1": {
                "source": str(MODULE.PHYSICAL_H1.relative_to(MODULE.REPO)),
                "sha256": MODULE.digest(MODULE.PHYSICAL_H1),
                "marker": physical_h1["marker"],
                "pin_authority_marker": physical_h1["pin_authority_marker"],
                "status": physical_h1["status"],
                "current_h1_blockers": [],
                "pre_r2_h2_gates": [],
            },
        }
        h2_m1["contacts"] = [
            {"contact": row["contact"], "net": row["net"]}
            for row in h0["interboard_rebaseline"]["pin_map"]
        ]
        return policy, h0, h2, h2_m1, pins, c5_mux, physical_h1

    def test_current_h0_has_six_domains_two_rps_and_exact_m1(self):
        result = MODULE.build()
        self.assertEqual([], result["errors"])
        self.assertEqual(6, result["current_h0"]["domain_count"])
        self.assertEqual({"hub_rp", "rf_rp"}, set(result["current_h0"]["rp_domain_ids"]))
        self.assertEqual(80, result["current_h0"]["m1_contacts"])
        self.assertEqual(16, result["current_h0"]["m1_reserve_contacts"])
        self.assertEqual(
            ("H1-R2.31", 48, 48, 5),
            (
                result["current_h1_pin_authority"]["marker"],
                result["current_h1_pin_authority"]["hub_gpio_rows"],
                result["current_h1_pin_authority"]["rf_gpio_rows"],
                result["current_h1_pin_authority"]["m1_signal_bindings"],
            ),
        )
        self.assertIn("open", result["exact_c5_mux_status"])

    def test_historical_h2_is_single_rp_old_m1_and_not_current(self):
        result = MODULE.build()
        historical = result["historical_r1_h2"]
        self.assertEqual("historical_only_not_r2", historical["authority"])
        self.assertEqual(5, historical["domain_count"])
        self.assertEqual(["rp"], historical["rp_instances"])
        self.assertEqual(51, historical["m1_unique_nets"])
        self.assertEqual(0, historical["m1_reserve_contacts"])
        self.assertFalse(result["r2_h2_authoritative"])
        self.assertFalse(result["r2_kicad_started"])

    def test_false_current_r2_claim_fails_closed(self):
        policy = copy.deepcopy(MODULE.load(MODULE.POLICY))
        policy["current_r2_h2_export"] = True
        result = MODULE.build(policy=policy)
        self.assertIn(
            "current-R2 H2 claim is forbidden until domains, exact RP maps, C5 mux/source hashes, M1, reviewed physical H1 and every pre-H2 gate reconcile",
            result["errors"],
        )

    def test_future_h2_opens_only_after_exact_reconciliation_and_zero_gates(self):
        policy, h0, h2, h2_m1, pins, c5_mux, physical_h1 = self.current_candidate()
        result = MODULE.build(policy, h0, h2, h2_m1, pins, c5_mux, physical_h1)
        self.assertEqual([], result["errors"])
        self.assertTrue(result["r2_h2_authoritative"])
        self.assertTrue(all(result["r2_h2_compatibility"].values()))

    def test_future_h2_rejects_any_exact_boundary_drift(self):
        mutations = {
            "hub map": lambda h2, h2_m1, pins: h2["bsp"]["domains"][3]["pin_map"].pop(),
            "S3 map": lambda h2, h2_m1, pins: h2["bsp"]["domains"][0]["pin_map"].pop(),
            "Pack MPN": lambda h2, h2_m1, pins: h2["bsp"]["domains"][4].update(mpn="WRONG"),
            "C5 retained IR map": lambda h2, h2_m1, pins: h2["bsp"]["domains"][1]["pin_map"].pop(0),
            "C5 composed SDIO USB row": lambda h2, h2_m1, pins: next(
                row for row in h2["bsp"]["domains"][1]["pin_map"]
                if row["contact"] == "GPIO13"
            ).update(net="STALE_USB_ONLY"),
            "Pack retained map": lambda h2, h2_m1, pins: h2["bsp"]["domains"][4]["pin_map"].pop(),
            "Safety retained map": lambda h2, h2_m1, pins: h2["bsp"]["domains"][5]["pin_map"].pop(),
            "Pack current mailbox bus": lambda h2, h2_m1, pins: next(
                row for row in h2["bsp"]["domains"][4]["pin_map"]
                if row["contact"] == "PA0"
            ).update(net="STALE_SYS_I2C_SDA"),
            "Safety current mailbox bus": lambda h2, h2_m1, pins: next(
                row for row in h2["integration_contract"]["controllers"][5]["pin_map"]
                if row["contact"] == "PA11"
            ).update(net="STALE_SYS_I2C_SCL"),
            "integration C5 map": lambda h2, h2_m1, pins: h2["integration_contract"]["controllers"][1]["pin_map"].pop(),
            "C5 mux": lambda h2, h2_m1, pins: h2["r2_reconciliation"]["c5_sdio_service_mux"].clear(),
            "source hash": lambda h2, h2_m1, pins: h2["source_sha256"].update({
                str(MODULE.PIN_AUTHORITY.relative_to(MODULE.REPO)): "0" * 64
            }),
            "M1 export": lambda h2, h2_m1, pins: h2_m1["contacts"].pop(),
            "open gate": lambda h2, h2_m1, pins: pins["authority_chain"]["remaining_h2_gates"].append("open"),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                policy, h0, h2, h2_m1, pins, c5_mux, physical_h1 = self.current_candidate()
                mutate(h2, h2_m1, pins)
                result = MODULE.build(policy, h0, h2, h2_m1, pins, c5_mux, physical_h1)
                self.assertFalse(result["r2_h2_authoritative"])
                self.assertTrue(result["errors"])

    def test_future_h2_rejects_unreviewed_or_blocked_physical_h1(self):
        for label, mutate in {
            "in progress": lambda physical: physical.update(status="in_progress"),
            "open blocker": lambda physical: physical["current_h1_blockers"].append("mock-up acceptance open"),
            "open production gate": lambda physical: physical["pre_r2_h2_gates"].append("factory route open"),
        }.items():
            with self.subTest(label=label):
                policy, h0, h2, h2_m1, pins, c5_mux, physical_h1 = self.current_candidate()
                mutate(physical_h1)
                result = MODULE.build(policy, h0, h2, h2_m1, pins, c5_mux, physical_h1)
                self.assertFalse(result["r2_h2_authoritative"])
                self.assertTrue(result["errors"])

    def test_r2_kicad_start_also_fails_closed(self):
        policy = copy.deepcopy(MODULE.load(MODULE.POLICY))
        policy["r2_kicad_started"] = True
        result = MODULE.build(policy=policy)
        self.assertIn(
            "R2 KiCad cannot start before the generated H2 export matches H0-R2 and physical H1 is reviewed",
            result["errors"],
        )

    def test_h1_and_h5_use_two_rps_per_device_and_ten_for_evt5(self):
        import json

        placement = json.loads(
            (ROOT / "hardware/product-design/h1-r2-placement.json").read_text(encoding="utf-8")
        )
        factory = next(row for row in placement["factory_evidence"] if row["mpn"] == "SC1512-A4")
        self.assertEqual(("C39843328", 2, 10), (
            factory["jlcpcb_part"], factory["quantity_per_device"], factory["evt5_quantity"]
        ))

        from hardware.verification import h5_pcba_platform

        overlay = h5_pcba_platform.build()["r2_quantity_overlay"]
        self.assertEqual(("J0", "C39843328", 2, 10), (
            overlay["route"], overlay["jlcpcb_part"],
            overlay["quantity_per_device"], overlay["evt5_quantity"]
        ))

    def test_c5_map_composes_current_sdio_usb_mux_with_retained_functions(self):
        rows = MODULE.composed_c5_pin_map(MODULE.load(MODULE.G2F), MODULE.load(MODULE.C5_MUX))
        by_contact = {row["contact"]: row for row in rows}
        self.assertEqual("IR_RX_DEMOD", by_contact["GPIO0"]["net"])
        self.assertEqual("C5_UART_SERVICE_TX", by_contact["GPIO11"]["net"])
        self.assertEqual("C5_RF_TX_EVIDENCE_N", by_contact["GPIO23"]["net"])
        self.assertEqual("C5_SDIO_D1", by_contact["GPIO7"]["net"])
        self.assertEqual("C5_SDIO_D3_USB_DM", by_contact["GPIO13"]["net"])
        self.assertEqual("C5_SDIO_D2_USB_DP", by_contact["GPIO14"]["net"])
        self.assertTrue(by_contact["GPIO13"]["muxed_with_usb"])
        self.assertEqual(13, by_contact["GPIO13"]["module_pad"])

    def test_pack_and_safety_maps_use_current_hub_mailbox_bus(self):
        maps = MODULE.retained_controller_pin_maps(
            MODULE.load(MODULE.G2F), MODULE.load(MODULE.C5_MUX)
        )
        for domain in ("pack", "safety"):
            by_contact = {row["contact"]: row for row in maps[domain]}
            self.assertEqual("HUB_SAFE_I2C_SDA", by_contact["PA0"]["net"])
            self.assertEqual(["hub_rp.GPIO42", "M1.32"], by_contact["PA0"]["peers"])
            self.assertEqual("HUB_SAFE_I2C_SCL", by_contact["PA11"]["net"])
            self.assertEqual(["hub_rp.GPIO43", "M1.33"], by_contact["PA11"]["peers"])


if __name__ == "__main__":
    unittest.main()
