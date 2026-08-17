import copy
import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "generate.py"
SPEC = importlib.util.spec_from_file_location("architecture_generate", MODULE_PATH)
GENERATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(GENERATOR)


class ArchitectureValidationTests(unittest.TestCase):
    def setUp(self):
        self.database, self.candidates = GENERATOR.load_sources()

    def errors_for(self, candidates=None):
        return GENERATOR.validate_sources(self.database, candidates or self.candidates)

    def test_checked_in_sources_are_valid(self):
        self.assertEqual([], self.errors_for())

    def test_rejects_duplicate_json_key_before_validation(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            GENERATOR.reject_duplicate_keys([("GPIO0", {}), ("GPIO0", {})])

    def test_rejects_module_internal_gpio(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3D")
        candidate["free_gpio"]["c5"].append("GPIO15")
        errors = self.errors_for(candidates)
        self.assertTrue(any("GPIO15" in error and "unknown GPIO" in error for error in errors), errors)

    def test_rejects_duplicate_allocation(self):
        candidates = copy.deepcopy(self.candidates)
        candidates[0]["allocations"].append(copy.deepcopy(candidates[0]["allocations"][0]))
        errors = self.errors_for(candidates)
        self.assertTrue(any("duplicate allocation" in error for error in errors), errors)

    def test_rejects_allocated_strap_without_proof(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-2R")
        row = next(a for a in candidate["allocations"] if a["instance"] == "c5" and a["contact"] == "GPIO3")
        row.pop("strap_proof")
        errors = self.errors_for(candidates)
        self.assertTrue(any("strap without strap_proof" in error for error in errors), errors)

    def test_rejects_unaccounted_gpio(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3D")
        candidate["free_gpio"]["c5"].remove("GPIO24")
        errors = self.errors_for(candidates)
        self.assertTrue(any("unaccounted GPIO" in error and "GPIO24" in error for error in errors), errors)

    def test_rejects_missing_recovery_contact(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3D")
        service = next(s for s in candidate["services"] if s["instance"] == "rp")
        service["contacts"].remove("SWDIO")
        errors = self.errors_for(candidates)
        self.assertTrue(any("missing service contacts" in error and "SWDIO" in error for error in errors), errors)

    def test_accepts_one_complete_service_alternative(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        service = next(s for s in candidate["services"] if s["instance"] == "c5")
        self.assertIn("GPIO11", service["contacts"])
        self.assertIn("GPIO12", service["contacts"])
        self.assertEqual([], self.errors_for(candidates))

    def test_rejects_partial_service_alternative(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        service = next(s for s in candidate["services"] if s["instance"] == "c5")
        service["contacts"].remove("GPIO12")
        errors = self.errors_for(candidates)
        self.assertTrue(any("missing one complete service alternative" in error for error in errors), errors)

    def test_rejects_unaccounted_slow_contact(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["contact_accounting"]["slow_io"]["reserved"].pop("P27")
        errors = self.errors_for(candidates)
        self.assertTrue(any("unaccounted allocatable contacts" in error and "P27" in error for error in errors), errors)

    def test_rejects_scheduled_resource_without_arbitration(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        resource = next(r for r in candidate["resource_contracts"] if r["sharing"] == "scheduled")
        resource.pop("arbitration")
        errors = self.errors_for(candidates)
        self.assertTrue(any("scheduled resource lacks arbitration" in error for error in errors), errors)

    def test_rejects_radio_resource_made_shared(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        resource = next(r for r in candidate["resource_contracts"] if r["id"] == "NRF1_SPI")
        resource["sharing"] = "scheduled"
        resource["arbitration"] = "invalid regression fixture"
        errors = self.errors_for(candidates)
        self.assertTrue(any("exclusive resource NRF1_SPI is not dedicated" in error for error in errors), errors)

    def test_rejects_missing_required_resource_contract(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["resource_contracts"] = [
            r for r in candidate["resource_contracts"] if r["id"] != "S3_C5_IPC"
        ]
        errors = self.errors_for(candidates)
        self.assertTrue(any("missing required resource contracts" in error and "S3_C5_IPC" in error for error in errors), errors)

    def test_rejects_controller_not_available_on_exact_device(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-2R")
        candidate["controllers"]["c5"].append("IMAGINARY_SPI9")
        candidate["allocations"][32]["controller"] = "IMAGINARY_SPI9"
        errors = self.errors_for(candidates)
        self.assertTrue(any("unavailable controllers" in error and "IMAGINARY_SPI9" in error for error in errors), errors)

    def test_rejects_pio_pin_outside_selected_b_package_window(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        row = next(
            allocation
            for allocation in candidate["allocations"]
            if allocation["instance"] == "rp" and allocation["net"] == "NRF0_MISO"
        )
        row["contact"] = "GPIO15"
        candidate["free_gpio"]["rp"].remove("GPIO15")
        candidate["free_gpio"]["rp"].append("GPIO30")
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("NRF0" not in error and "outside GPIO16..GPIO47" in error for error in errors),
            errors,
        )

    def test_rejects_missing_shared_pio_window_selection(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["controller_gpio_windows"] = [
            window
            for window in candidate["controller_gpio_windows"]
            if "PIO0_SM0_RF_SPI" not in window["controllers"]
        ]
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("PIO0_GPIO_BASE missing GPIO-window selection" in error for error in errors),
            errors,
        )

    def test_rejects_overbooked_dma_capacity(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        capacity = next(
            item for item in candidate["capacity_contracts"] if item["id"] == "RP_DMA_CHANNELS"
        )
        capacity["claims"][0]["units"] += 1
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("14 claimed + 3 reserve != 16 available" in error for error in errors),
            errors,
        )

    def test_rejects_fixed_mux_contact_drift(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        mux = next(item for item in candidate["mux_contracts"] if item["id"] == "RP_UART1_GNSS")
        mux["contacts"][1] = "GPIO42"
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("RP_UART1_GNSS" not in error and "declared contacts" in error for error in errors),
            errors,
        )

    def test_rejects_missing_required_mux_contract(self):
        candidates = copy.deepcopy(self.candidates)
        candidate = next(c for c in candidates if c["id"] == "G2F-3I")
        candidate["mux_contracts"] = [
            mux for mux in candidate["mux_contracts"] if mux["id"] != "C5_FIXED_SDIO"
        ]
        errors = self.errors_for(candidates)
        self.assertTrue(
            any("missing required mux contracts" in error and "C5_FIXED_SDIO" in error for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
