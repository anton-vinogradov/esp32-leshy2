"""The physical 5+5 bank must report a conflict, never silently repack an SMA."""
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
KICAD_PYTHON = Path("/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3")
EXPECTED = {
    "LESHY2-UI-R2": {"nrf0_external_sma", "s3_external_rp_sma", "nrf1_external_sma", "c5_external_rp_sma", "nrf2_external_sma"},
    "LESHY2-RF-R2": {"receiver_fmsw_external_sma", "receiver_amlw_external_sma", "cc_external_sma", "voice_external_sma", "voice_v_external_sma"},
}
REVERSE_POLARITY = {"s3_external_rp_sma", "c5_external_rp_sma"}


class H6R2AntennaAnchorLockTests(unittest.TestCase):
    def test_all_ten_ports_retain_exact_connector_identity(self):
        contract = json.loads((ROOT / "hardware/layout/h6-r2-placement-contract.json").read_text())
        ledger = json.loads((ROOT / "hardware/ecad/generated/H2-R2-native-instance-ledger.json").read_text())["rows"]
        self.assertEqual(set(EXPECTED), set(contract["antenna_ports"]))
        for project, expected in EXPECTED.items():
            self.assertEqual(expected, set(contract["antenna_ports"][project]))
            rows = {row["instance"]: row for row in ledger if row["project"] == project and row["instance"] in expected}
            self.assertEqual(expected, set(rows))
            for instance, row in rows.items():
                series = "32" if instance in REVERSE_POLARITY else "31"
                self.assertEqual(f"gct_rfpc_sma{series}_fn_175_a", row["device_id"])
                self.assertEqual(f"GCT RFPC-SMA{series}-FN-175-A", row["mpn"])
                self.assertEqual(f"Leshy2:RFPC-SMA{series}-FN-175-A", row["footprint"])

    @unittest.skipUnless(KICAD_PYTHON.is_file(), "KiCad bundled pcbnew Python is unavailable")
    def test_native_placement_keeps_even_colliding_ports_locked(self):
        # Instantiate only the actual ten connector instances. This exercises
        # the native hard-placement branch without rebuilding 1,208 components
        # or saving any PCB; missing unrelated pair audits are not a pass claim.
        code = r'''
import copy
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / "hardware/layout"))
import h6_r2_placement as p
# The deliberately connector-only fixture has no buttons for the independent
# user-label renderer. No placement, occupancy or conflict logic is replaced.
import h6_r2_user_silkscreen
h6_r2_user_silkscreen.add_to_board = lambda *args: None
p.add_battery_ntc_silkscreen = lambda *args: None
contract = p.load(p.CONTRACT_PATH)
placement = p.load(p.PLACEMENT_PATH)
coordinate = p.load(p.COORDINATE_PATH)
instances = p.load(p.INSTANCE_PATH)["rows"]
nets = p.load(p.NET_PATH)["rows"]
symbols = {row["device_id"]: row for row in p.load(p.SYMBOL_PATH)["symbols"]}
bindings = p.load(p.NET_BINDING_PATH)
count = 0
for project, ports in contract["antenna_ports"].items():
    rows = [row for row in instances if row["project"] == project and row["instance"] in ports]
    assert len(rows) == 5
    for row in rows:
        target = p.target_for_instance(project, row["instance"], row["reference"], contract, {}, {})
        assert target["mechanical_locked"] is True
        assert target["rotation_locked"] is True
        assert target["anchor"] == ports[row["instance"]]
        assert p.correction_rotations(180, target) == (180,)
    for force_collision in (False, True):
        candidate = copy.deepcopy(contract)
        if force_collision:
            candidate["antenna_ports"][project] = {instance: [40.0, 0.0] for instance in ports}
        project_nets = [row for row in nets if row["project"] == project and row["instance"] in ports]
        board, audit = p.place_project(project, candidate, placement, coordinate, rows, project_nets, symbols, bindings["projects"][project]["canonical_to_kicad"], {})
        placed = {row["instance"]: row for row in audit["placements"]}
        assert set(placed) == set(ports)
        for instance, expected in candidate["antenna_ports"][project].items():
            row = placed[instance]
            assert row["footprint_anchor_mm"] == expected, (instance, row["footprint_anchor_mm"], expected)
            assert row["side"] == "F.Cu" and row["rotation_deg"] == 180, (instance, row)
        if force_collision:
            assert audit["hard_conflicts"], "Deliberately coincident SMA bodies were silently accepted"
        count += len(placed)
assert count == 20
print("20 normal/colliding native antenna placements retain exact anchors and rotation")
'''
        result = subprocess.run([str(KICAD_PYTHON), "-c", code], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=90)
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("20 normal/colliding native antenna placements", result.stdout)


if __name__ == "__main__":
    unittest.main()
