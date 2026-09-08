"""Seven current inward microphone poses, not audio/acoustic qualification."""
from collections import Counter
import copy
import hashlib
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]
PROJECT = 'LESHY2-RF-R2'
REVIEW_PATH = 'hardware/layout/h6-r2-microphone-bottom-candidate.json'
IDENTITIES = {
    'MK1': ('microphone', 'same_sky_cmej_0413_42_smt_tr', 'Same Sky CMEJ-0413-42-SMT-TR', 'Leshy2:CMEJ-0413-42-SMT-TR'),
    'R206': ('microphone_bias_res', 'uniroyal_0402wgf2201tce', 'UNI-ROYAL 0402WGF2201TCE', 'Resistor_SMD:R_0402_1005Metric'),
    'C232': ('microphone_bias_filter_cap', 'murata_grm188r60j106me47d', 'Murata GRM188R60J106ME47D', 'Capacitor_SMD:C_0603_1608Metric'),
    'R205': ('microphone_bias_filter_res', 'yageo_rc0402fr_07220rl', 'Yageo RC0402FR-07220RL', 'Resistor_SMD:R_0402_1005Metric'),
    'U85': ('headset_mic_selector', 'ti_ts5a63157_dckr', 'Texas Instruments TS5A63157DCKR', 'Package_TO_SOT_SMD:SOT-363_SC-70-6'),
    'C229': ('headset_mic_selector_bypass', 'yageo_cc0402krx7r9bb104', 'Yageo CC0402KRX7R9BB104', 'Capacitor_SMD:C_0402_1005Metric'),
    'R202': ('headset_mic_select_pullup', 'yageo_rc0402fr_07100kl', 'Yageo RC0402FR-07100KL', 'Resistor_SMD:R_0402_1005Metric'),
}
POSES = {
    'MK1': (0, [47, 147.4]), 'R206': (180, [47, 144]),
    'C232': (90, [49.25, 143.3]), 'R205': (270, [49.25, 140.65]),
    'U85': (90, [16.5, 113.75]), 'C229': (90, [18.55, 113.75]),
    'R202': (90, [14.7, 113.25]),
}
# Exact logical physical-pin allocation, independent of the reviewed poses.
NETS = {
    'MK1': {'1': 'MIC_RAW', '2': 'AUDIO_GROUND'},
    'R206': {'1': 'MIC_BIAS_FILTERED', '2': 'MIC_RAW'},
    'C232': {'1': 'MIC_BIAS_FILTERED', '2': 'AUDIO_GROUND'},
    'R205': {'1': '3V3_MAIN', '2': 'MIC_BIAS_FILTERED'},
    'U85': {'1': 'MIC_RAW', '2': 'AUDIO_GROUND', '3': 'HEADSET_MIC_RAW',
            '4': 'MIC_SELECTED_RAW', '5': '3V3_MAIN', '6': 'HEADSET_INTERNAL_MIC_SEL'},
    'C229': {'1': '3V3_MAIN', '2': 'AUDIO_GROUND'},
    'R202': {'1': '3V3_MAIN', '2': 'HEADSET_INTERNAL_MIC_SEL'},
}


def angle(value):
    assert type(value) in (int, float) and math.isfinite(value)
    return value % 360


def validate(review, contract, instances, net_rows):
    assert review['project'] == PROJECT
    assert review['feature_id'] == 'RF-INNER-BOTTOM-MICROPHONE-001'
    assert review['status'] == 'reviewed_placement_candidate_not_audio_qualified'
    assert set(review['authority']) == {'production_written', 'audio_qualified', 'fabrication_ready'}
    assert all(value is False for value in review['authority'].values())
    rows = review['placement_rows']
    assert len(rows) == 7 and {r['reference'] for r in rows} == set(IDENTITIES)
    index = [r for r in instances if r['project'] == PROJECT and r['reference'] in IDENTITIES]
    assert len(index) == 7 and {r['reference'] for r in index} == set(IDENTITIES)
    index = {r['reference']: r for r in index}
    for row in rows:
        ref = row['reference']
        keys = ('instance', 'device_id', 'mpn', 'footprint')
        assert tuple(row[key] for key in keys) == IDENTITIES[ref]
        assert tuple(index[ref][key] for key in keys) == IDENTITIES[ref]
        expected_angle, expected_at = POSES[ref]
        assert row['after']['side'] == 'B.Cu'
        assert row['after']['anchor_mm'] == expected_at
        assert angle(row['after']['angle']) == expected_angle
        target = contract['placement_overrides'][row['instance']]
        assert target['project'] == PROJECT and target['frame'] == 'rear-inner'
        assert target['anchor_mm'] == expected_at and angle(target['rotation_deg']) == expected_angle
        assert target['mechanical_locked'] is True and 'centre_mm' not in target
        assert target['evidence'] == REVIEW_PATH
        endpoints = [r for r in net_rows if r['project'] == PROJECT and r['reference'] == ref]
        assert len(endpoints) == len(NETS[ref])
        assert {r['physical']: r['net'] for r in endpoints} == NETS[ref]
        assert all(r['instance'] == row['instance'] and r['device_id'] == row['device_id']
                   and r['disposition'] == 'connected' for r in endpoints)
    datum = review['source_datum']
    assert datum['frame'] == 'rear-inner'
    assert datum['native_anchor_mm'] == [47, 147.4]
    assert datum['world_anchor_mm'] == [33, 147.4]
    assert datum['capsule_port_direction'] == (
        'toward the 11-mm interboard gap / opposing UI, not toward either in-plane +/-Y direction (+Y is the bottom edge)')
    assert 'internal-FET' in datum['internal_fet_and_load']
    assert '2.2-kohm' in datum['internal_fet_and_load']
    assert 'no additional active buffer' in datum['internal_fet_and_load']
    assert review['bounds']['couplings_retained'] == ['C197', 'C231']
    assert review['bounds']['other_moved_neighbours'] == 0
    assert review['bounds']['strategic_ports_changed'] == ['MK1']
    assert 'The geometric choice does not qualify acoustic response, assembly or the enclosure bottom opening.' in review['limits']
    assert 'MIC_RAW and headset/selected branches still require quiet analog routing and review.' in review['limits']


class MicrophoneBottomCandidateTests(unittest.TestCase):
    def setUp(self):
        self.review = json.loads((ROOT / REVIEW_PATH).read_text())
        self.contract = json.loads((ROOT / 'hardware/layout/h6-r2-placement-contract.json').read_text())
        self.instances = json.loads((ROOT / 'hardware/ecad/generated/H2-R2-native-instance-ledger.json').read_text())['rows']
        self.nets = json.loads((ROOT / 'hardware/ecad/generated/H2-R2-native-net-ledger.json').read_text())['rows']

    def check(self):
        validate(self.review, self.contract, self.instances, self.nets)

    def test_current_exact_seven_poses_identity_and_electrical_scope(self):
        self.check()

    def test_angles_accept_only_equivalent_modulo_turns(self):
        for row in self.review['placement_rows']:
            row['after']['angle'] -= 360
            self.contract['placement_overrides'][row['instance']]['rotation_deg'] += 360
        self.check()

    def test_missing_duplicate_extra_review_rows_rejected(self):
        for mutation in ('missing', 'duplicate', 'extra'):
            review = copy.deepcopy(self.review)
            if mutation == 'missing': review['placement_rows'].pop()
            elif mutation == 'duplicate': review['placement_rows'][-1] = copy.deepcopy(review['placement_rows'][0])
            else: review['placement_rows'].append(copy.deepcopy(review['placement_rows'][0]))
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                validate(review, self.contract, self.instances, self.nets)

    def test_old_outward_mk1_cannot_be_restored_in_both_sources(self):
        row = next(r for r in self.review['placement_rows'] if r['reference'] == 'MK1')
        row['after'].update(side='F.Cu', angle=180, anchor_mm=[8, 112])
        self.contract['placement_overrides']['microphone'].update(frame='rear-outer', rotation_deg=180, anchor_mm=[8, 112])
        with self.assertRaises(AssertionError): self.check()

    def test_wrong_pose_side_or_unlocked_override_rejected(self):
        for field, value in [('anchor_mm', [18.55, 114]), ('frame', 'rear-outer'),
                             ('rotation_deg', 0), ('mechanical_locked', False),
                             ('rotation_deg', True), ('rotation_deg', float('nan'))]:
            contract = copy.deepcopy(self.contract)
            contract['placement_overrides']['headset_mic_selector_bypass'][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(AssertionError):
                validate(self.review, contract, self.instances, self.nets)

    def test_review_and_ledger_cannot_jointly_substitute_same_package_part(self):
        for key in ('instance', 'device_id', 'mpn', 'footprint'):
            review, instances = copy.deepcopy(self.review), copy.deepcopy(self.instances)
            next(r for r in review['placement_rows'] if r['reference'] == 'U85')[key] = 'substitute'
            next(r for r in instances if r['project'] == PROJECT and r['reference'] == 'U85')[key] = 'substitute'
            with self.subTest(key=key), self.assertRaises(AssertionError):
                validate(review, self.contract, instances, self.nets)

    def test_missing_duplicate_net_or_selector_pin_swap_rejected(self):
        for mutation in ('missing', 'duplicate', 'swap'):
            nets = copy.deepcopy(self.nets)
            selected = next(r for r in nets if r['project'] == PROJECT and r['reference'] == 'U85' and r['physical'] == '1')
            if mutation == 'missing': nets.remove(selected)
            elif mutation == 'duplicate': nets.append(copy.deepcopy(selected))
            else: selected['net'] = 'HEADSET_MIC_RAW'
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                validate(self.review, self.contract, self.instances, nets)

    def test_power_ground_cannot_replace_audio_return(self):
        next(r for r in self.nets if r['project'] == PROJECT and r['reference'] == 'C232' and r['physical'] == '2')['net'] = 'POWER_GROUND'
        with self.assertRaises(AssertionError): self.check()

    def test_authority_missing_zero_or_true_is_not_false(self):
        for mutation in ('missing', 'zero', 'true'):
            review = copy.deepcopy(self.review)
            if mutation == 'missing': del review['authority']['audio_qualified']
            else: review['authority']['audio_qualified'] = 0 if mutation == 'zero' else True
            with self.subTest(mutation=mutation), self.assertRaises(AssertionError):
                validate(review, self.contract, self.instances, self.nets)

    def test_acoustic_direction_not_down_or_fabrication_qualification(self):
        self.review['source_datum']['capsule_port_direction'] = 'downward +Y, acoustically qualified'
        with self.assertRaises(AssertionError): self.check()


try:
    import pcbnew
except ImportError:
    pcbnew = None


@unittest.skipUnless(pcbnew, 'Native KiCad Python required; no CLI or board saves')
class NativeMicrophoneBottomCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = ROOT / f'hardware/ecad/kicad/{PROJECT}/{PROJECT}.kicad_pcb'
        cls.before_sha = hashlib.sha256(cls.path.read_bytes()).hexdigest()
        cls.board = pcbnew.LoadBoard(str(cls.path))
        cls.fps = {fp.GetReference(): fp for fp in cls.board.GetFootprints()}
        cls.bindings = json.loads((ROOT / 'hardware/layout/generated/H6-R2-kicad-net-bindings.json').read_text())['projects'][PROJECT]['canonical_to_kicad']

    @classmethod
    def tearDownClass(cls):
        assert hashlib.sha256(cls.path.read_bytes()).hexdigest() == cls.before_sha

    def assert_pose(self, ref):
        fp = self.fps[ref]
        rotation, at = POSES[ref]
        self.assertTrue(fp.IsFlipped(), ref)
        self.assertEqual(rotation, angle(fp.GetOrientationDegrees()), ref)
        self.assertEqual([round(v * 1_000_000) for v in at], [fp.GetPosition().x, fp.GetPosition().y], ref)

    def test_all_current_native_poses_match_seven_inward_requirements(self):
        for ref in IDENTITIES:
            with self.subTest(ref=ref): self.assert_pose(ref)

    def test_all_native_pad_net_multisets_include_both_mk1_pad1_occurrences(self):
        for ref, (_, _, mpn, footprint) in IDENTITIES.items():
            fp = self.fps[ref]
            expected = Counter((pad, self.bindings[net]) for pad, net in NETS[ref].items())
            if ref == 'MK1': expected[('1', self.bindings['MIC_RAW'])] += 1
            with self.subTest(ref=ref):
                self.assertEqual(mpn, fp.GetValue())
                self.assertEqual(footprint, fp.GetFPIDAsString())
                self.assertEqual(expected, Counter((p.GetNumber(), p.GetNetname()) for p in fp.Pads()))

    def test_old_native_anchor_is_rejected_without_saving(self):
        fp = self.fps['MK1']
        saved = fp.GetPosition()
        try:
            fp.SetPosition(pcbnew.VECTOR2I(8_000_000, 112_000_000))
            with self.assertRaises(AssertionError): self.assert_pose('MK1')
        finally:
            fp.SetPosition(saved)


if __name__ == '__main__':
    unittest.main()
