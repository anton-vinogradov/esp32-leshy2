"""No unreviewed repack or copper loss may hide inside a library refresh."""
from pathlib import Path
from collections import Counter
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "hardware/layout"))
try:
    import pcbnew
except ImportError:
    pcbnew = None

if pcbnew is not None:
    import h6_r2_stage_placement_update as updater


@unittest.skipIf(pcbnew is None, "KiCad Python required for guarded placement staging")
class GuardedPlacementUpdateTests(unittest.TestCase):
    def test_unchanged_population_does_not_require_blanket_approval(self):
        self.assertEqual([], updater.verify_changed_references({"R1":"old"}, {"R1":"old"}, []))

    def test_explicitly_reviewed_change_is_admitted(self):
        self.assertEqual(["R1"], updater.verify_changed_references({"R1":"old", "R2":"same"}, {"R1":"new", "R2":"same"}, ["R1"]))

    def test_unknown_duplicate_or_nonlist_allowance_is_rejected(self):
        for allowed in (["R2"], ["R1", "R1"], "R1", [None]):
            with self.subTest(allowed=allowed), self.assertRaises(ValueError):
                updater.verify_changed_references({"R1":"same"}, {"R1":"same"}, allowed)

    def test_unreviewed_change_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unreviewed footprint changes"):
            updater.verify_changed_references({"R1":"old", "R2":"same"}, {"R1":"new", "R2":"moved"}, ["R1"])

    def test_added_or_missing_footprint_fails_closed(self):
        for after in ({}, {"R1":"old", "R2":"new"}):
            with self.subTest(after=after), self.assertRaisesRegex(ValueError, "population changed"):
                updater.verify_changed_references({"R1":"old"}, after, ["R1","R2"])

    def test_balanced_parser_retains_copper_and_ignores_quoted_parentheses(self):
        source = '(kicad_pcb (gr_text "literal (not a form)\\\"" (at 1 2)) (segment (net "n")) (via (at 1 2)) (zone (keepout (tracks not_allowed))) (zone (net "g")))'
        self.assertEqual(["gr_text","segment","via","zone","zone"], [h for h,_ in updater.forms(source)])
        self.assertEqual(['(segment (net "n"))','(via (at 1 2))','(zone (net "g"))'], updater.copper_forms(source))

    def test_uuid_normalization_does_not_remove_geometry(self):
        self.assertEqual('(pad (at 1 2) (uuid "<uuid>"))', updater.canonical('(pad (at 1 2) (uuid "abc-123"))'))

    def test_interform_cleanup_preserves_every_object_byte_and_order(self):
        first = '(gr_text "literal (parentheses)\n  " (at 1 2))'
        copper = '(segment\n  \n (start 1 2) (end 3 4) (net "GND"))'
        source = '(kicad_pcb\n\t\n\t' + first + '\n\t\n\t\n' + copper + '\n)\n'
        result = updater.normalize_interform_whitespace(source)
        self.assertEqual(list(updater.forms(source)), list(updater.forms(result)))
        self.assertEqual([copper], updater.copper_forms(result))
        self.assertIn(first, result)
        self.assertNotIn('\n\t\n', result)
        self.assertEqual(result, updater.normalize_interform_whitespace(result))

    def test_raw_duplicate_uuid_is_rejected_before_native_load(self):
        value = '00000000-0000-4000-8000-000000000001'
        text = f'(kicad_pcb (footprint (uuid "{value}")) (segment (uuid "{value}")))'
        with self.assertRaisesRegex(ValueError, "duplicate native"):
            updater.require_unique_uuids(text)

    def test_malformed_native_uuid_is_not_skipped(self):
        with self.assertRaises(ValueError):
            updater.require_unique_uuids('(kicad_pcb (footprint (uuid "not-a-uuid")))')

    def test_spliced_uuid_collision_is_fixed_without_changing_other_fields(self):
        value = '00000000-0000-4000-8000-000000000001'
        unchanged = f'(segment (uuid "{value}") (start 1 2) (end 3 4))'
        changed = f'(footprint "part" (uuid "{value}") (path "/{value}") (pad "1" (at 1 2) (net 1 "GND") (uuid "00000000-0000-4000-8000-000000000002")))'
        occupied = {value}
        result = updater.fresh_object_uuids(changed, "reviewed U1", occupied)
        self.assertEqual(updater.canonical(changed), updater.canonical(result))
        self.assertIn(f'(path "/{value}")', result)
        self.assertNotIn(value, updater.native_uuids(result))
        updater.require_unique_uuids('(kicad_pcb ' + unchanged + result + ')')
        self.assertEqual(result, updater.fresh_object_uuids(changed, "reviewed U1", {value}))

    def test_new_uuid_generation_checks_existing_generated_values_too(self):
        form = '(footprint (uuid "00000000-0000-4000-8000-000000000001"))'
        first = updater.fresh_object_uuids(form, "U1", set())
        second = updater.fresh_object_uuids(form, "U1", set(updater.native_uuids(first)))
        self.assertNotEqual(updater.native_uuids(first), updater.native_uuids(second))

    def test_nested_group_is_not_silently_reidentified(self):
        form = '(footprint (group "group" (uuid "00000000-0000-4000-8000-000000000001") (members "00000000-0000-4000-8000-000000000002")))'
        with self.assertRaisesRegex(ValueError, "membership migration"):
            updater.fresh_object_uuids(form, "U1", set())

    def test_repeated_nc_pin_removal_requires_exact_multiplicity(self):
        before, after = Counter({("MP", ""): 2}), Counter()
        with self.assertRaisesRegex(ValueError, "multiplicity"):
            updater.verify_pad_nets("U1", before, after, ["MP"])
        updater.verify_pad_nets("U1", before, after, ["MP", "MP"])
        updater.verify_pad_nets("U1", before, after, {"MP": 2})
        with self.assertRaisesRegex(ValueError, "multiplicity"):
            updater.verify_pad_nets("U1", before, before, {"MP": 2})

    def test_connected_duplicate_or_unidentified_pad_cannot_disappear(self):
        for before, after, allowance in [
            (Counter({("1", "GND"): 2}), Counter({("1", "GND"): 1}), {"1": 1}),
            (Counter({("", "GND"): 1}), Counter(), []),
            (Counter({("", ""): 1}), Counter(), []),
        ]:
            with self.subTest(before=before), self.assertRaisesRegex(ValueError, "connected pad removal"):
                updater.verify_pad_nets("U1", before, after, allowance)

    def test_net_reassignment_and_addition_are_not_a_removal_allowance(self):
        before = Counter({("1", "OLD"): 1})
        for after in (Counter({("1", "NEW"): 1}), Counter({("1", "OLD"): 2})):
            with self.subTest(after=after), self.assertRaisesRegex(ValueError, "added or reassigned"):
                updater.verify_pad_nets("U1", before, after, [])

    def test_only_npth_is_mechanical_not_unnumbered_copper(self):
        fp = pcbnew.FOOTPRINT(None)
        for attr in (pcbnew.PAD_ATTRIB_NPTH, pcbnew.PAD_ATTRIB_SMD):
            pad = pcbnew.PAD(fp)
            pad.SetAttribute(attr)
            fp.Add(pad)
        self.assertEqual(Counter({("", ""): 1}), updater.pad_nets(fp))

    def test_duplicate_references_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            updater.footprints('(kicad_pcb (footprint "x" (property "Reference" "R1")) (footprint "x" (property "Reference" "R1")))')

    def test_label_allow_list_cannot_touch_other_text_or_wrong_side(self):
        form = '(gr_text "USB" (at 1 2) (layer "F.Silkscreen"))'
        source = '(kicad_pcb '+form+' (gr_text "PTT" (layer "F.Silkscreen")))'
        self.assertEqual([("USB",form)], updater.reviewed_label_forms(source, {"USB"}))
        native_short = source.replace('"F.Silkscreen"', '"F.SilkS"')
        self.assertEqual([("USB", form.replace('"F.Silkscreen"', '"F.SilkS"'))],
                         updater.reviewed_label_forms(native_short, {"USB"}))
        with self.assertRaises(ValueError):
            updater.reviewed_label_forms(native_short.replace('"F.SilkS"', '"B.SilkS"'), {"USB"})
        with self.assertRaisesRegex(ValueError, "only touch outward"):
            updater.reviewed_label_forms(source.replace('"F.Silkscreen"','"B.Silkscreen"'), {"USB"})


@unittest.skipIf(pcbnew is None, "KiCad Python required for guarded placement staging")
class GuardedPlacementStageIntegrationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.project = "LESHY2-UI-R2"
        self.source = self.root / f"hardware/ecad/kicad/{self.project}/{self.project}.kicad_pcb"
        self.source.parent.mkdir(parents=True)
        self.contract = self.root / "contract.json"
        self.contract.write_text("{}")
        board = pcbnew.BOARD()
        net = pcbnew.NETINFO_ITEM(board, "GND")
        board.Add(net)
        fp = pcbnew.FOOTPRINT(board)
        fp.SetReference("R1")
        fp.SetValue("TEST")
        board.Add(fp)
        pad = pcbnew.PAD(fp)
        pad.SetNumber("1")
        pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        pad.SetSize(pcbnew.VECTOR2I(1000000, 1000000))
        layers = pcbnew.LSET()
        layers.AddLayer(pcbnew.F_Cu)
        pad.SetLayerSet(layers)
        pad.SetNet(net)
        fp.Add(pad)
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(pcbnew.VECTOR2I(0, 0))
        track.SetEnd(pcbnew.VECTOR2I(1000000, 0))
        track.SetWidth(200000)
        track.SetLayer(pcbnew.F_Cu)
        track.SetNet(net)
        board.Add(track)
        pcbnew.SaveBoard(str(self.source), board)
        self.original = self.source.read_bytes()
        seed = pcbnew.LoadBoard(str(self.source))
        for item in list(seed.GetTracks()):
            seed.Remove(item)
        next(iter(seed.GetFootprints())).SetPosition(pcbnew.VECTOR2I(2000000, 3000000))
        seed_file = self.root / "seed.kicad_pcb"
        pcbnew.SaveBoard(str(seed_file), seed)
        self.seed = seed_file.read_bytes()
        self.directory = self.root / "candidate"
        self.plan = {"project": self.project, "baseline_board_sha256": updater.sha(self.original), "allowed_references": ["R1"]}
        self.audit = {"boards": [{"project": self.project, "hard_conflicts": [], "placement_failures": [],
                                   "net_or_footprint_errors": [], "locality": {"status": "pass"},
                                   "critical_pad_pairs": {"status": "pass"}}]}
        self.patches = [patch.object(updater, "ROOT", self.root),
                        patch.object(updater.placement, "CONTRACT_PATH", self.contract),
                        patch.object(updater, "input_snapshot", side_effect=self.snapshot)]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)

    def snapshot(self, _source):
        return {str(path.resolve()): updater.sha(path.read_bytes()) for path in (self.source, self.contract)}

    def build(self):
        return {self.source: self.seed}, self.audit

    def test_real_roundtrip_keeps_original_copper_and_publishes_only_checked_candidate(self):
        with patch.object(updater.placement, "build", side_effect=self.build):
            result = updater.stage(self.plan, self.directory)
        candidate = self.directory / self.source.name
        self.assertEqual(self.original, self.source.read_bytes())
        self.assertEqual(["R1"], result["changed_references"])
        self.assertEqual("pass", result["native_uuid_uniqueness"])
        self.assertEqual(1, result["copper_forms_preserved_exact"])
        self.assertEqual(updater.copper_forms(self.original.decode()), updater.copper_forms(candidate.read_text()))
        updater.require_unique_uuids(candidate.read_text())
        self.assertEqual(result, json.loads((self.directory / "stage-review.json").read_text()))

    def test_changed_contract_during_build_is_rejected_before_any_candidate(self):
        def mutate():
            self.contract.write_text('{"changed": true}')
            return self.build()
        with patch.object(updater.placement, "build", side_effect=mutate):
            with self.assertRaisesRegex(ValueError, "inputs changed"):
                updater.stage(self.plan, self.directory)
        self.assertFalse(self.directory.exists())
        self.assertEqual(self.original, self.source.read_bytes())

    def test_changed_inputs_during_native_verification_are_not_published(self):
        real = updater.placement.placement_signature_bytes
        calls = 0
        def mutate(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 3:
                self.contract.write_text('{"changed": true}')
            return real(*args, **kwargs)
        with patch.object(updater.placement, "build", side_effect=self.build), patch.object(updater.placement, "placement_signature_bytes", side_effect=mutate):
            with self.assertRaisesRegex(ValueError, "inputs changed"):
                updater.stage(self.plan, self.directory)
        self.assertFalse(self.directory.exists())

    def test_projection_failure_leaves_no_candidate_or_receipt(self):
        self.plan["allowed_references"] = []
        with patch.object(updater.placement, "build", side_effect=self.build):
            with self.assertRaisesRegex(ValueError, "unreviewed footprint changes"):
                updater.stage(self.plan, self.directory)
        self.assertFalse(self.directory.exists())

    def test_existing_stage_receipt_cannot_be_overwritten(self):
        self.directory.mkdir()
        receipt = self.directory / "stage-review.json"
        receipt.write_text("keep")
        with self.assertRaisesRegex(ValueError, "new scratch"):
            updater.stage(self.plan, self.directory)
        self.assertEqual("keep", receipt.read_text())


if __name__ == "__main__":
    unittest.main()
