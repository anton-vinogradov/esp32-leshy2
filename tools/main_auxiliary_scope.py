"""Pinned replacement-interface and auxiliary-source scope, not a DC solver.

Reuse the verified native ledger and selected static corners. Unknown branch
ownership/current is retained, not interpreted as zero or an EDG default.
"""
from copy import deepcopy
from decimal import Decimal
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re

import compare_main_current_limit as current
from h6_power_corner_math import Interval

ROOT = current.ROOT
require = current.require
ROWS_PATH = ROOT/'hardware/verification/h6-main-auxiliary-sources.json'
REVIEWED_SHA256 = '4477fc5c57b8cfeabbd5f6a7cbb5dad121ebab945fa2b68597f15b5111881b6a'
NODES = {'MAIN_RAW_3V3': 'main_converter_output_bypass', '3V3_MAIN': 'main_protected_output',
         'AON_SAFE_3V3': 'aon_output', 'NVDC_SYS': 'converter_input'}
PIN_TYPES = {'analog_input': 'input', 'open_drain_output': 'open_collector',
             'power_input': 'power_in', 'power_output': 'power_out',
             'analog_output': 'output', 'ground': 'power_in'}
BRANCHES = {'monitor_vdd': ('candidate_monitor', 'supply_current'),
            'monitor_reset_pullup': ('candidate_reset_pullup', 'pullup_current'),
            'replacement_efuse_iq': ('replacement_efuse', 'supply_current'),
            'other_new_auxiliaries': (None, 'unresolved_inventory')}
ROW_IDS = {'tps259814_iq_on', 'tps3703_idd', 'tps3703_reset_leakage'}


def source_paths():
    return [Path(__file__), ROWS_PATH]


def bounds(values):
    require(type(values) is list and len(values) == 2 and all(type(v) is str for v in values),
            'two explicit exact interval strings required')
    result = tuple(F(v) for v in values)
    require(result[0] <= result[1], 'reversed interval')
    return result


def validate_source_row(row):
    require(type(row) is dict and set(row) == {'id', 'mpn', 'parameter', 'unit', 'minimum',
            'typical', 'maximum', 'source_id', 'page', 'supply_pin', 'return_pin',
            'numeric_domains', 'header_conditions', 'limitation'}, 'invalid source row schema')
    require(all(type(row[k]) is str and row[k].strip() for k in
            ('id', 'mpn', 'parameter', 'source_id', 'supply_pin', 'return_pin', 'limitation'))
            and row['unit'] == 'A' and type(row['page']) is int and row['page'] > 0,
            'source identity/unit missing')
    for key in ('minimum', 'typical', 'maximum'):
        require(row[key] is None or type(row[key]) is str, 'bound is neither explicit nor unknown')
        if row[key] is not None:
            F(row[key])
    require(row['maximum'] is not None and F(row['maximum']) > 0, 'explicit positive maximum required')
    present = [F(row[k]) for k in ('minimum', 'typical', 'maximum') if row[k] is not None]
    require(present == sorted(present), 'source bound columns reversed')
    require(type(row['numeric_domains']) is dict and row['numeric_domains'], 'missing numeric source domains')
    for axis, domain in row['numeric_domains'].items():
        require(type(axis) is str and axis, 'unnamed source axis')
        bounds(domain)
        Interval(*domain)  # Existing finite Decimal / interval validator; source rows are decimals.
    conditions = row['header_conditions']
    require(type(conditions) is dict and conditions and all(type(k) is str and k and
            type(v) is str and v for k, v in conditions.items()), 'missing explicit source conditions')


def load_reviewed():
    require(ROWS_PATH.is_file() and not ROWS_PATH.is_symlink(), 'missing or symlinked auxiliary fixture')
    raw = ROWS_PATH.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == REVIEWED_SHA256, 'auxiliary fixture changed; review required')
    record = json.loads(raw)
    require(set(record) == {'schema_version', 'scope', 'sources', 'replacement_interface',
            'monitor_interface', 'rows', 'exact_supply_nodes', 'reference_ground',
            'native_fault_pullup', 'limits'} and type(record['schema_version']) is int and
            record['schema_version'] == 1, 'invalid auxiliary fixture schema')
    require(record['exact_supply_nodes'] == NODES and record['reference_ground'] == 'POWER_GROUND',
            'exact supply/return node authority differs')
    for source in record['sources'].values():
        require(set(source) == {'url', 'revision', 'pdf_sha256', 'reviewed_pages', 'reviewed_on'}
                and source['url'].startswith('https://www.ti.com/lit/') and source['revision']
                and re.fullmatch('[0-9a-f]{64}', source['pdf_sha256']) is not None
                and re.fullmatch(r'\d{4}-\d{2}-\d{2}', source['reviewed_on']) is not None
                and source['reviewed_pages'] and all(type(p) is int and p > 0 for p in source['reviewed_pages']),
                'incomplete primary source authority')
    require(type(record['rows']) is list and len(record['rows']) == len(ROW_IDS)
            and {r['id'] for r in record['rows']} == ROW_IDS, 'missing/duplicate source rows')
    for row in record['rows']:
        validate_source_row(row)
        require(row['source_id'] in record['sources'] and
                row['page'] in record['sources'][row['source_id']]['reviewed_pages'], 'unreviewed source/page')
    monitor = record['monitor_interface']
    require(monitor['pins'] == {'SENSE': '1', 'VDD': '2', 'CT': '3', 'RESET': '4', 'GND': '5', 'MR': '6'},
            'incomplete monitor physical pin interface')
    return record


def evaluate_source(row, *, mpn, axes, conditions):
    """Admit only this one-sided parameter maximum, never a whole circuit.

    Application conditions are explicit caller assertions, not inferred from
    matching numeric domains. A missing minimum remains unknown, not zero.
    """
    validate_source_row(row)
    require(mpn == row['mpn'], 'exact source MPN differs')
    require(type(axes) is dict and set(axes) <= set(row['numeric_domains']), 'unknown application axis')
    require(type(conditions) is dict and set(conditions) <= set(row['header_conditions']) and
            all(v is None or type(v) is str for v in conditions.values()), 'unknown/invalid application condition')
    missing, outside = [], []
    for axis, source_domain in row['numeric_domains'].items():
        if axes.get(axis) is None:
            missing.append(axis)
        else:
            low, high = bounds(axes[axis])
            source_low, source_high = bounds(source_domain)
            if not source_low <= low <= high <= source_high:
                outside.append(axis)
    unreviewed = [name for name in row['header_conditions'] if conditions.get(name) is None]
    mismatch = [name for name, expected in row['header_conditions'].items()
                if conditions.get(name) is not None and conditions[name] != expected]
    numeric = not missing and not outside
    admitted = numeric and not unreviewed and not mismatch
    return {'source_row': row['id'], 'mpn': mpn, 'parameter': row['parameter'], 'qualified': False,
            'numeric_domains_covered': numeric, 'missing_axes': missing, 'uncovered_axes': outside,
            'unreviewed_conditions': unreviewed, 'mismatched_conditions': mismatch,
            'parameter_maximum_admitted': admitted, 'actual_current_max_a': row['maximum'] if admitted else None,
            'actual_current_min_a': row['minimum'] if admitted else None,
            'source_maximum_a': row['maximum'], 'application_axes': deepcopy(axes),
            'application_conditions': deepcopy(conditions), 'source_id': row['source_id'],
            'source_page': row['page'], 'source_conditions': deepcopy(row['header_conditions']),
            'limitation': row['limitation']}


def classify_branch(supply_node, return_node):
    require(supply_node is None or type(supply_node) is str and supply_node in NODES, 'unknown/wrong supply node')
    require(return_node is None or return_node == 'POWER_GROUND', 'unknown/wrong return node')
    return {'supply_node': supply_node, 'return_node': return_node,
            'accounting_lane': NODES.get(supply_node) if return_node == 'POWER_GROUND' else None,
            'ownership_known': supply_node is not None and return_node == 'POWER_GROUND'}


def validate_branches(records):
    require(type(records) is list and len(records) == len(BRANCHES) and
            {r.get('id') for r in records} == set(BRANCHES), 'missing, duplicate or orphan auxiliary branch')
    for row in records:
        require(set(row) == {'id', 'owner', 'kind', 'supply_node', 'return_node',
                'current_max_a', 'bound_established', 'diagnostic_budget_a'}, 'invalid branch schema')
        owner, kind = BRANCHES[row['id']]
        require(row['owner'] == owner and row['kind'] == kind, 'wrong branch owner/type')
        classify_branch(row['supply_node'], row['return_node'])
        require(row['current_max_a'] is None and row['bound_established'] is False,
                'unreviewed actual auxiliary current must remain unknown')
        if row['diagnostic_budget_a'] is not None:
            require(type(row['diagnostic_budget_a']) is str and F(row['diagnostic_budget_a']) >= 0,
                    'invalid explicit diagnostic budget')
        if row['id'] == 'replacement_efuse_iq':
            require(row['supply_node'] == 'MAIN_RAW_3V3' and row['return_node'] == 'POWER_GROUND',
                    'replacement eFuse IQ belongs upstream, not protected/AON')
        if row['id'] == 'other_new_auxiliaries':
            require(row['supply_node'] is None and row['return_node'] is None and row['diagnostic_budget_a'] is None,
                    'unresolved inventory cannot be silently closed')
    return [{**deepcopy(row), **classify_branch(row['supply_node'], row['return_node'])} for row in records]


def validate_candidate_interface(interface, native):
    require(interface == load_reviewed()['replacement_interface'], 'candidate pin roles differ from reviewed source')
    require(interface['native_instance'] == 'main_efuse' and
            interface['native_mpn'] == 'Texas Instruments TPS25974LRPWR' and
            interface['candidate_mpn'] == 'Texas Instruments TPS259814LRPWR', 'replacement identity differs')
    pins = interface['pins']
    require(type(pins) is list and len(pins) == 10 and
            {p['physical'] for p in pins} == {str(n) for n in range(1, 11)}, 'complete unique candidate 10-pin interface required')
    require(len(native) == 10 and {str(r['physical']) for r in native} == {str(n) for n in range(1, 11)},
            'complete unique native 10-pin interface required')
    expected_device, expected = current.power.PINS['main_efuse']
    require(len(expected) == 10, 'native physical authority differs')
    native_by_pin = {str(r['physical']): r for r in native}
    for name, (physical, net) in expected.items():
        row = native_by_pin[physical]
        require(row['contact'] == name and row['net'] == net and row['device_id'] == expected_device and
                row['mpn'] == interface['native_mpn'] and row['instance'] == 'main_efuse',
                'native pin identity/function/net differs')
    differences = []
    for candidate in pins:
        require(set(candidate) == {'physical', 'name', 'type'} and candidate['type'] in PIN_TYPES,
                'invalid candidate pin role/type')
        old = native_by_pin[candidate['physical']]
        changed = candidate['name'] != old['contact'] or PIN_TYPES[candidate['type']] != old['type']
        differences.append({'physical': candidate['physical'], 'native_function': old['contact'],
                            'native_type': old['type'], 'native_net': old['net'],
                            'candidate_function': candidate['name'], 'candidate_type': candidate['type'],
                            'role_or_type_changed': changed, 'functional_equivalence_proven': False})
    require(next(r for r in differences if r['physical'] == '4')['role_or_type_changed'],
            'source-reviewed FLT versus PGTH mismatch disappeared')
    return {'drop_in_allowed': False, 'candidate_wiring_declared': False, 'qualified': False,
            'pins': differences, 'semantic_limits': deepcopy(interface['semantic_limits']),
            'unresolved': ['Pin 4 FLT output cannot reuse old PGTH divider by pin position',
                           'Pin 3 PG gate-on meaning is not the old PGTH-monitored rail guarantee',
                           'Candidate and external monitor wiring, control currents and unused-pin dispositions are not declared']}


def load_context(source_hashes):
    """Read only sources already validated by the existing current/DC loader."""
    require(type(source_hashes) is dict, 'validated current-loader source hashes required')
    before = current.snapshot(current.source_paths())
    require(set(before) <= set(source_hashes) and all(source_hashes[k] == v for k, v in before.items()),
            'current source inventory/provenance changed')
    crossings = current.crossings
    data = {key: crossings.load(ROOT/crossings.INPUTS[key]) for key in ('nets', 'instances', 'material', 'devices')}
    reviews = crossings.semantics.reviewed_maps([crossings.load(p) for p in crossings.semantics.MAPS],
                                               data['material']['groups'])
    _, by_instance = crossings.indexes(data, reviews)
    result = {'devices': data['devices']['devices']}
    h3 = json.loads((ROOT/current.power.INPUTS['h3']).read_text(), parse_float=Decimal)
    aon = h3['rails']['AON_SAFE_3V3']
    result['required_aon_v'] = [str(aon['load_min_v']), str(aon['load_max_v'])]
    require(bounds(result['required_aon_v'])[0] > 0, 'physical required AON voltage interval missing')
    for instance in ('main_efuse', 'power_fault_pullup'):
        matches = [rows for (project, name), rows in by_instance.items() if name == instance]
        require(len(matches) == 1, 'missing/ambiguous native branch instance')
        result[instance] = matches[0]
    require(current.snapshot(current.source_paths()) == before, 'native sources changed during scope read')
    return result


def assess_current(dc_result, *, source_hashes=None):
    """Attach a closed, explicitly incomplete source/interface scope to DC result."""
    own_before = current.snapshot(source_paths())
    fixture = load_reviewed()
    hashes = source_hashes if source_hashes is not None else dc_result.get('source_sha256')
    context = load_context(hashes)
    require(dc_result['qualified'] is False and dc_result['source_applicability'] is False and
            dc_result['status'] == 'not_qualified' and dc_result['full_dc_cell_proven'] is False,
            'upstream must retain unqualified scope')
    original = dc_result['unresolved_branches']
    expected_unresolved = [{'id': name, 'supply_node': 'raw_converter_output' if name == 'replacement_efuse_iq' else None,
                           'current_max_a': None, 'bound_established': False} for name in BRANCHES]
    require(original == expected_unresolved,
            'missing or falsely resolved upstream auxiliary branches')
    records = [{'id': name, 'owner': owner, 'kind': kind,
                'supply_node': 'MAIN_RAW_3V3' if name == 'replacement_efuse_iq' else None,
                'return_node': None if name == 'other_new_auxiliaries' else 'POWER_GROUND',
                'current_max_a': None, 'bound_established': False, 'diagnostic_budget_a': None}
               for name, (owner, kind) in BRANCHES.items()]
    branches = validate_branches(records)
    interface = validate_candidate_interface(fixture['replacement_interface'], context['main_efuse'])
    pullup = fixture['native_fault_pullup']
    resistance, tolerance = current.power.resistance(context['devices'][pullup['device_id']])
    require(F(str(resistance)) == F(pullup['nominal_ohm']) and
            F(str(tolerance)) == F(pullup['initial_tolerance_fraction']), 'native R266 declared value/tolerance differs')
    contacts = context['power_fault_pullup']
    require(len(contacts) == 2 and {str(r['physical']) for r in contacts} == {'1', '2'} and
            all(r['reference'] == pullup['reference'] and r['device_id'] == pullup['device_id']
                and r['type'] == 'passive' for r in contacts), 'native R266 identity/types differ')
    contact_map = {str(r['physical']): r for r in contacts}
    require(contact_map[pullup['supply_physical']]['net'] == pullup['supply_node'] and
            contact_map[pullup['signal_physical']]['net'] == pullup['signal_node'] and
            contact_map['1']['contact'] == 'END_1' and contact_map['2']['contact'] == 'END_2',
            'native R266 supply/signal physical contacts differ')
    rows = {r['id']: r for r in fixture['rows']}
    evaluate = lambda row, axes: evaluate_source(row, mpn=row['mpn'], axes=axes, conditions={})
    groups = []
    require(dc_result['groups'], 'selected static pairs missing')
    for group in dc_result['groups']:
        require(group['monitor'] == 'tps3703a7330', 'monitor source identity does not match selected pair')
        selected = group['selected_static_pair']
        loaded = selected['loaded_diagnostic']
        require(loaded['status'] == 'conditional_static_pass' and loaded['qualified'] is False and
                loaded['source_applicability'] is False and loaded['checked_load_cases'] == 58 and
                len(loaded['cases']) == 58, 'selected loaded static coverage missing')
        raw = loaded['raw_v_exact']
        bounds(raw)
        local_bounds = [bounds(case['bounds_exact']['local_v']) for case in loaded['cases']]
        local = [str(min(v[0] for v in local_bounds)), str(max(v[1] for v in local_bounds))]
        hypotheses = {'MAIN_RAW_3V3': raw, '3V3_MAIN': local, 'AON_SAFE_3V3': context['required_aon_v']}
        monitor_scopes, leakage_scopes = [], []
        for node, voltage in hypotheses.items():
            monitor_scopes.append({'supply_node_hypothesis': node, **evaluate(rows['tps3703_idd'],
                                   {'vdd_v': voltage, 'ta_c': ['-40', '125']})})
            leakage_scopes.append({'supply_node_hypothesis': node, **evaluate(rows['tps3703_reset_leakage'],
                                   {'vdd_v': voltage, 'reset_v': local, 'ta_c': ['-40', '125']})})
        for key, row in (('monitor', rows['tps3703_idd']), ('reset_leakage', rows['tps3703_reset_leakage'])):
            axes = {'vdd_v': ['0', '0'], 'ta_c': ['-40', '125']}
            if key == 'reset_leakage':
                axes['reset_v'] = ['0', context['required_aon_v'][1]]
            target = monitor_scopes if key == 'monitor' else leakage_scopes
            target.append({'supply_node_hypothesis': 'commanded_off_zero_voltage_diagnostic', **evaluate(row, axes)})
        # VOL=0 is only a conservative resistor diagnostic, not an IC sink proof.
        pullup_max = F(local[1]) / (F(pullup['nominal_ohm'])*(1-F(pullup['initial_tolerance_fraction'])))
        groups.append({'divider_class': group['divider_class'], 'monitor': group['monitor'],
                       'raw_voltage_v_exact': deepcopy(raw), 'protected_voltage_v_exact': local,
                       'monitor_supply_scopes': monitor_scopes, 'reset_leakage_scopes': leakage_scopes,
                       'efuse_iq_scope': evaluate(rows['tps259814_iq_on'], {'vin_v': raw, 'tj_c': ['-40', '125']}),
                       'native_pullup_low_output_diagnostic_max_a': str(pullup_max),
                       'native_pullup_added_again': False, 'qualified': False})
    final_native = current.snapshot(current.source_paths())
    require(current.snapshot(source_paths()) == own_before and all(hashes.get(p) == digest for p, digest in final_native.items()),
            'sources changed during auxiliary assessment')
    return {'schema_version': 1, 'status': 'not_qualified', 'qualified': False, 'source_applicability': False,
            'full_inventory_known': False, 'actual_auxiliary_total_a': None,
            'model_decisions_inside_command': 0, 'source_sha256': own_before,
            'source_mode': 'Current guarded native ledgers; no new native CAD export',
            'sources': deepcopy(fixture['sources']), 'replacement_interface': interface,
            'monitor_interface': deepcopy(fixture['monitor_interface']), 'branches': branches,
            'native_fault_pullup': {**deepcopy(pullup), 'counted_again': False, 'actual_current_max_a': None,
                                   'native_budget_coverage_proven': False,
                                   'diagnostic_only': '10k +/-1% initial only, VOL=0; no TCR/lifetime/sink proof'},
            'groups': groups, 'live_aon_hypothesis_v': deepcopy(context['required_aon_v']),
            'temperature_hypothesis_c': ['-40', '125'],
            'limits': deepcopy(fixture['limits']) + ['Live AON and TA/TJ intervals are explicit requirements/hypotheses, not measured supply/temperature proof',
                'Off-state zero-voltage case is diagnostic; commanded off is not measured zero',
                'Retained R266 is not an added replacement load; its presence does not prove native aggregate load allowance includes it',
                'No auxiliary currents added to existing demands; unknown inventory/conditions forbid a full DC-cell claim']}
