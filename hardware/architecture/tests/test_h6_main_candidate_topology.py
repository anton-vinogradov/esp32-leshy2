"""Independent native-delta and literal pin-table checks, not CAD qualification."""
from copy import deepcopy
from fractions import Fraction as F
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import main_candidate_topology as topology
import synthesize_main_dc_cell as cell


PROJECT = 'LESHY2-RF-R2'
CHANGED = {'main_efuse', 'main_fb_top', 'main_fb_bottom',
           'main_efuse_pg_top', 'main_efuse_pg_bottom', 'main_efuse_rilm'}
ADDED = {'exp_main_monitor', 'exp_main_monitor_bypass'}
SUPPLIES = ('MAIN_RAW_3V3', '3V3_MAIN', 'AON_SAFE_3V3')
# Independent transcription of the reviewed physical interfaces. Do not import
# the builder's mapping or use its reconstruction as the expected topology.
EFUSE = {
    '1': ('EN_UVLO', 'MAIN_RAW_3V3', 'input'),
    '2': ('OVLO', 'MAIN_EFUSE_OVLO', 'input'),
    '3': ('PG', 'POWER_FAULT_N', 'open_collector'),
    '4': ('FLT', None, 'open_collector'),
    '5': ('IN', 'MAIN_RAW_3V3', 'power_in'),
    '6': ('OUT', '3V3_MAIN', 'power_out'),
    '7': ('DVDT', 'MAIN_EFUSE_DVDT', 'output'),
    '8': ('GND', 'POWER_GROUND', 'power_in'),
    '9': ('ILM', 'MAIN_EFUSE_ILM', 'output'),
    '10': ('ITIMER', 'MAIN_EFUSE_ITIMER', 'output'),
}
MONITOR = {
    '1': ('SENSE', 'EXP_MAIN_SENSE', 'input'),
    '2': ('VDD', None, 'power_in'),  # Substitute the explicitly selected rail.
    '3': ('CT', None, 'input'),
    '4': ('RESET', 'POWER_FAULT_N', 'open_collector'),
    '5': ('GND', 'POWER_GROUND', 'power_in'),
    '6': ('MR', None, 'input'),
}
PF_PEERS = {('ext_efuse', '4'), ('ext_pg_qualifier', '3'),
            ('main_efuse', '3'), ('voice_pg_qualifier', '3'),
            ('unit_efuse', '4'), ('slow_io', '8'),
            ('power_fault_pullup', '2'), ('safety_controller', '3')}


@unittest.skipUnless(importlib.util.find_spec('edg'), 'prepared EDG runtime needed')
class MainCandidateTopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Never call cell.run(): its parent integration calls this builder too.
        cls.native = cell.current.load_current()
        cls.static = cell.static.run()
        cls.dc = cell.combine(cls.static, cls.native, cell.current.load_edg_table())
        cls.baseline = topology.load_baseline(cls.native['source_sha256'])
        cls.group = cls.dc['groups'][0]
        cls.threshold = cls.group['rilm_portfolios'][0]
        cls.candidates = {supply: topology.build_candidate(
            cls.baseline, cls.group, cls.threshold, supply) for supply in SUPPLIES}
        cls.dc['auxiliary_scope'] = cell.auxiliary.assess_current(
            cls.dc, source_hashes=cls.native['source_sha256'])

    def setUp(self):
        self.candidate = deepcopy(self.candidates['MAIN_RAW_3V3'])

    def pin(self, instance, physical, data=None):
        rows = (self.candidate if data is None else data)['pins']
        return next(r for r in rows if r['project'] == PROJECT and
                    r['instance'] == instance and str(r['physical']) == str(physical))

    def instance(self, name, data=None):
        rows = (self.candidate if data is None else data)['instances']
        return next(r for r in rows if r['project'] == PROJECT and r['instance'] == name)

    def validate(self):
        return topology.validate_candidate(self.baseline, self.candidate,
                                           self.group, self.threshold, 'MAIN_RAW_3V3')

    def test_literal_efuse_monitor_and_bypass_pin_maps_for_all_supply_options(self):
        for supply, candidate in self.candidates.items():
            with self.subTest(supply=supply):
                for instance, expected in (('main_efuse', EFUSE), ('exp_main_monitor', MONITOR)):
                    actual = [r for r in candidate['pins'] if r['project'] == PROJECT and r['instance'] == instance]
                    self.assertEqual(len(actual), len(expected))
                    for physical, (name, net, kind) in expected.items():
                        if instance == 'exp_main_monitor' and name == 'VDD':
                            net = supply
                        row = self.pin(instance, physical, candidate)
                        self.assertEqual((row['contact'], row['net'], row['type']), (name, net, kind))
                        self.assertEqual(row['endpoint'], instance + '.' + name)
                        self.assertEqual(row['pads'], [physical])
                        self.assertEqual(row['disposition'], 'no_connect' if net is None else 'connected')
                self.assertEqual(self.pin('exp_main_monitor_bypass', '1', candidate)['net'], supply)
                self.assertEqual(self.pin('exp_main_monitor_bypass', '2', candidate)['net'], 'POWER_GROUND')
                self.assertEqual(F(self.instance('exp_main_monitor_bypass', candidate)
                                   ['generic_candidate']['value_f_exact']), F('0.0000001'))

    def test_exact_native_delta_preserves_all_unrelated_components_and_contacts(self):
        old_instances = {(r['project'], r['instance']): r for r in self.baseline['instances']}
        new_instances = {(r['project'], r['instance']): r for r in self.candidate['instances']}
        self.assertEqual(set(new_instances) - set(old_instances), {(PROJECT, n) for n in ADDED})
        self.assertFalse(set(old_instances) - set(new_instances))
        altered = {key for key, row in old_instances.items() if row != new_instances[key]}
        self.assertEqual(altered, {(PROJECT, n) for n in CHANGED})
        old_pins = [r for r in self.baseline['pins'] if not (r['project'] == PROJECT and r['instance'] in CHANGED)]
        new_pins = [r for r in self.candidate['pins'] if not (r['project'] == PROJECT and r['instance'] in CHANGED | ADDED)]
        self.assertEqual(old_pins, new_pins)
        self.assertEqual(len(self.candidate['instances']), len(self.baseline['instances']) + 2)
        self.assertEqual(len(self.candidate['pins']), len(self.baseline['pins']) + 8)
        receipt = self.validate()
        self.assertEqual(set(receipt['changed_instances']), CHANGED)
        self.assertEqual(set(receipt['added_instances']), ADDED)
        self.assertEqual(receipt['preserved_instances'], len(self.baseline['instances']) - 6)
        self.assertEqual(receipt['preserved_pins'], len(self.baseline['pins']) - 20)

    def test_all_eight_fault_peers_retained_ninth_reset_and_r266_unchanged(self):
        peers = lambda data: {(r['instance'], str(r['physical'])) for r in data['pins']
                             if r['project'] == PROJECT and r['net'] == 'POWER_FAULT_N'}
        self.assertEqual(peers(self.baseline), PF_PEERS)
        self.assertEqual(peers(self.candidate), PF_PEERS | {('exp_main_monitor', '4')})
        self.assertEqual(self.pin('power_fault_pullup', '1')['net'], '3V3_MAIN')
        self.assertEqual(self.instance('power_fault_pullup'), self.instance('power_fault_pullup', self.baseline))

    def test_pgth_resistors_become_sense_divider_not_output_load_on_flt(self):
        expected = {('main_efuse_pg_top', '1'): '3V3_MAIN',
                    ('main_efuse_pg_top', '2'): 'EXP_MAIN_SENSE',
                    ('main_efuse_pg_bottom', '1'): 'EXP_MAIN_SENSE',
                    ('main_efuse_pg_bottom', '2'): 'POWER_GROUND'}
        for (name, pad), net in expected.items():
            self.assertEqual(self.pin(name, pad)['net'], net)
        self.assertEqual(self.instance('main_efuse_pg_top')['reference'], 'R66')
        self.assertEqual(self.instance('main_efuse_pg_bottom')['reference'], 'R65')
        self.assertFalse(any(r['net'] == 'MAIN_EFUSE_PGTH' for r in self.candidate['pins']))
        self.assertFalse(any(r['endpoint'] == 'main_efuse.PGTH' for r in self.candidate['pins']))

    def test_five_values_are_generic_and_both_selected_divider_classes_are_used(self):
        for group, threshold_index, expected_fb, expected_rilm in (
                (self.dc['groups'][0], 0, (F(442), F(101)), F(1260)),
                (self.dc['groups'][1], 1, (F(4420), F(1010)), F(1270))):
            candidate = topology.build_candidate(self.baseline, group, group['rilm_portfolios'][threshold_index], 'MAIN_RAW_3V3')
            expected = {'main_fb_top': expected_fb[0], 'main_fb_bottom': expected_fb[1],
                        'main_efuse_pg_top': F('10.5'), 'main_efuse_pg_bottom': F(10000),
                        'main_efuse_rilm': expected_rilm}
            for name, value in expected.items():
                row = self.instance(name, candidate)
                with self.subTest(group=group['divider_class'], instance=name):
                    self.assertEqual(F(row['generic_candidate']['value_ohm_exact']), value)
                    self.assertIsNone(row['mpn'])
                    self.assertIsNone(row['symbol_id'])
                    self.assertIsNone(row['footprint'])
                    self.assertEqual(row['source_instance']['mpn'], self.instance(name, self.baseline)['mpn'])
                    for pin in candidate['pins']:
                        if pin['project'] == PROJECT and pin['instance'] == name:
                            self.assertIsNone(pin['mpn'])
                            self.assertEqual(pin['device_id'], row['device_id'])

    def test_repeatable_copy_does_not_mutate_input_or_claim_native_authority(self):
        before = deepcopy((self.baseline, self.group, self.threshold))
        second = topology.build_candidate(self.baseline, self.group, self.threshold, 'MAIN_RAW_3V3')
        self.assertEqual(second, self.candidate)
        self.assertEqual(before, (self.baseline, self.group, self.threshold))
        self.assertEqual(second['status'], 'nonproduction_candidate')
        for flag in ('qualified', 'native_cad', 'production_mpn_selected'):
            self.assertIs(second[flag], False)
        self.assertNotIn('sources', second)

    def test_omitted_original_or_added_component_and_pin_rejected(self):
        for key, index in (('instances', 0), ('instances', -1), ('pins', 0), ('pins', -1)):
            with self.subTest(key=key, index=index):
                self.candidate = deepcopy(self.candidates['MAIN_RAW_3V3'])
                self.candidate[key].pop(index)
                with self.assertRaises(ValueError):
                    self.validate()

    def test_duplicate_component_reference_endpoint_or_physical_pad_rejected(self):
        for mutation in ('instance', 'reference', 'pin', 'physical'):
            self.candidate = deepcopy(self.candidates['MAIN_RAW_3V3'])
            if mutation == 'instance':
                self.candidate['instances'].append(deepcopy(self.candidate['instances'][0]))
            elif mutation == 'reference':
                self.instance('exp_main_monitor')['reference'] = 'U21'
            elif mutation == 'pin':
                self.candidate['pins'].append(deepcopy(self.candidate['pins'][0]))
            else:
                self.pin('exp_main_monitor', '4')['physical'] = '3'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.validate()

    def test_wrong_monitor_channel_type_supply_or_bypass_rail_rejected(self):
        for name, pad, field, value in (
                ('exp_main_monitor', '1', 'net', 'MAIN_RAW_3V3'),
                ('exp_main_monitor', '4', 'net', 'EXP_MAIN_SENSE'),
                ('exp_main_monitor', '4', 'type', 'output'),
                ('exp_main_monitor', '2', 'net', 'AON_SAFE_3V3'),
                ('exp_main_monitor_bypass', '1', 'net', '3V3_MAIN'),
                ('exp_main_monitor', '1', 'pads', ['4'])):
            self.candidate = deepcopy(self.candidates['MAIN_RAW_3V3'])
            self.pin(name, pad)[field] = value
            with self.subTest(name=name, pad=pad, field=field), self.assertRaises(ValueError):
                self.validate()

    def test_ct_mr_and_flt_are_explicitly_unconnected(self):
        for name, pad, net in (('exp_main_monitor', '3', 'POWER_GROUND'),
                               ('exp_main_monitor', '6', 'MAIN_RAW_3V3'),
                               ('main_efuse', '4', 'MAIN_EFUSE_PGTH')):
            self.candidate = deepcopy(self.candidates['MAIN_RAW_3V3'])
            self.pin(name, pad).update(net=net, disposition='connected')
            with self.subTest(name=name, pad=pad), self.assertRaises(ValueError):
                self.validate()

    def test_old_pgth_middle_or_swapped_sense_resistors_rejected(self):
        for name, pad, net in (('main_efuse_pg_top', '2', 'MAIN_EFUSE_PGTH'),
                               ('main_efuse_pg_bottom', '1', 'MAIN_EFUSE_PGTH'),
                               ('main_efuse_pg_top', '1', 'POWER_GROUND')):
            self.candidate = deepcopy(self.candidates['MAIN_RAW_3V3'])
            self.pin(name, pad)['net'] = net
            with self.subTest(name=name, pad=pad), self.assertRaises(ValueError):
                self.validate()

    def test_stale_production_mpn_or_footprint_cannot_describe_changed_resistor(self):
        for key in ('mpn', 'device_id', 'symbol_id', 'footprint'):
            self.candidate = deepcopy(self.candidates['MAIN_RAW_3V3'])
            self.instance('main_fb_top')[key] = self.instance('main_fb_top', self.baseline)[key]
            with self.subTest(field=key), self.assertRaises(ValueError):
                self.validate()
        self.candidate = deepcopy(self.candidates['MAIN_RAW_3V3'])
        self.pin('main_fb_top', '1')['mpn'] = self.instance('main_fb_top', self.baseline)['mpn']
        with self.assertRaises(ValueError):
            self.validate()

    def test_incorrect_resistor_or_bypass_values_rejected(self):
        for name in ('main_fb_top', 'main_fb_bottom', 'main_efuse_pg_top',
                     'main_efuse_pg_bottom', 'main_efuse_rilm', 'exp_main_monitor_bypass'):
            self.candidate = deepcopy(self.candidates['MAIN_RAW_3V3'])
            key = 'value_f_exact' if name == 'exp_main_monitor_bypass' else 'value_ohm_exact'
            self.instance(name)['generic_candidate'][key] = '1'
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.validate()

    def test_unrelated_native_wiring_or_component_and_aon_pullup_rejected(self):
        for mutation in ('wiring', 'component', 'aon_pullup'):
            self.candidate = deepcopy(self.candidates['MAIN_RAW_3V3'])
            if mutation == 'wiring':
                self.pin('safety_controller', '3')['net'] = 'UNREQUESTED'
            elif mutation == 'component':
                self.instance('power_fault_pullup')['mpn'] = 'substituted part'
            else:
                self.pin('power_fault_pullup', '1')['net'] = 'AON_SAFE_3V3'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.validate()

    def test_authority_flags_cannot_be_promoted(self):
        for key in ('qualified', 'native_cad', 'production_mpn_selected'):
            self.candidate = deepcopy(self.candidates['MAIN_RAW_3V3'])
            self.candidate[key] = True
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.validate()

    def test_stale_source_digest_or_changed_baseline_is_rejected(self):
        stale = dict(self.native['source_sha256'])
        stale[next(iter(stale))] = '0'*64
        with self.assertRaises(ValueError):
            topology.load_baseline(stale)
        baseline = deepcopy(self.baseline)
        baseline['instances'][0]['reference'] = 'TAMPERED'
        with self.assertRaises(ValueError):
            topology.build_candidate(baseline, self.group, self.threshold, 'MAIN_RAW_3V3')

    def test_undeclared_supply_and_missing_threshold_candidate_are_rejected(self):
        for supply in ('3V3', 'NVDC_SYS', None):
            with self.subTest(supply=supply), self.assertRaises(ValueError):
                topology.build_candidate(self.baseline, self.group, self.threshold, supply)
        threshold = deepcopy(self.threshold)
        threshold['selected_nominal_ohm'] = None
        with self.assertRaises(ValueError):
            topology.build_candidate(self.baseline, self.group, threshold, 'MAIN_RAW_3V3')

    def test_parent_portfolio_has_eighteen_compact_unqualified_deltas(self):
        before = deepcopy(self.dc)
        report = cell.build_topology_portfolio(self.dc, self.native['source_sha256'])
        self.assertEqual(self.dc, before)
        self.assertEqual(report['candidate_count'], 18)
        self.assertEqual(report['variants_considered'], 18)
        self.assertEqual(report['monitor_supply_nodes'], list(SUPPLIES))
        self.assertEqual(len(report['candidates']), 18)
        self.assertIs(report['qualified'], False)
        self.assertIs(report['native_cad_changed'], False)
        self.assertIs(report['production_mpn_selected'], False)
        for row in report['candidates']:
            self.assertEqual(len(row['instance_delta']), 8)
            self.assertEqual(len(row['pin_delta']), 28)
            self.assertIs(row['qualified'], False)
            self.assertIsNone(row['actual_auxiliary_total_a'])
            self.assertIsNone(row['monitor_idd_scope']['actual_current_max_a'])
            self.assertFalse(row['monitor_idd_scope']['parameter_maximum_admitted'])
            self.assertIn('reset_load_f', row['monitor_idd_scope']['unreviewed_conditions'])
            self.assertFalse(row['output_bus']['new_pullup_added'])
            self.assertFalse(row['output_bus']['loaded_logic_proven'])
        self.assertEqual(cell.current.snapshot(cell.current.source_paths()), self.native['source_sha256'])


if __name__ == '__main__':
    unittest.main()
