"""Complete nonproduction MAIN ledger overlays; no native CAD or new solver.

Only six declared native instances and two additions may differ. Generic
values never retain a formerly fitted exact MPN. Validation checks the exact
allowed delta and external membership, not a replay of the builder.
"""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path

import main_auxiliary_scope as auxiliary
from hardware.verification import h6_r2_c5_isolation_candidate as overlay

current = auxiliary.current
crossings = current.crossings
ROOT = current.ROOT
require = current.require
digest, row_index = overlay.digest, overlay.row_index
PROJECT = 'LESHY2-RF-R2'
SHEET = 'RF_03_MAIN_RAILS_DOMAIN_GATES'
ORIGIN = 'experimental_main_topology_overlay_not_production'
SENSE_NET = 'EXP_MAIN_SENSE'
SUPPLY_NODES = ('MAIN_RAW_3V3', '3V3_MAIN', 'AON_SAFE_3V3')
CHANGED_INSTANCES = ('main_efuse', 'main_efuse_pg_bottom', 'main_efuse_pg_top',
                     'main_efuse_rilm', 'main_fb_bottom', 'main_fb_top')
ADDED_INSTANCES = ('exp_main_monitor', 'exp_main_monitor_bypass')
REFERENCES = dict(zip(CHANGED_INSTANCES + ADDED_INSTANCES,
                     ('U21', 'R65', 'R66', 'R67', 'R69', 'R70', 'EXP_U_MAIN_MON', 'EXP_C_MAIN_MON')))
MONITOR_TYPES = {'SENSE': 'input', 'VDD': 'power_in', 'CT': 'input',
                 'RESET': 'open_collector', 'GND': 'power_in', 'MR': 'input'}
RESISTOR_CONNECTIONS = {
    'main_efuse_pg_bottom': {'END_1': ('1', SENSE_NET), 'END_2': ('2', 'POWER_GROUND')},
    'main_efuse_pg_top': {'END_1': ('1', '3V3_MAIN'), 'END_2': ('2', SENSE_NET)},
    'main_efuse_rilm': {'END_1': ('1', 'MAIN_EFUSE_ILM'), 'END_2': ('2', 'POWER_GROUND')},
    'main_fb_bottom': {'END_1': ('1', 'MAIN_3V3_FB'), 'END_2': ('2', 'POWER_GROUND')},
    'main_fb_top': {'END_1': ('1', 'MAIN_RAW_3V3'), 'END_2': ('2', 'MAIN_3V3_FB')},
}
IDENTITY_FIELDS = ('project', 'instance', 'reference', 'device_id', 'mpn', 'symbol_id', 'footprint')
INSTANCE_DELTA_FIELDS = {'device_id', 'mpn', 'symbol_id', 'footprint', 'allocation_origin',
                         'bom_excluded', 'source_instance', 'generic_candidate'}
PIN_DELTA_FIELDS = {'device_id', 'mpn', 'origin', 'source_endpoint', 'contact', 'endpoint',
                   'physical', 'pads', 'type', 'net', 'disposition'}


def source_paths():
    return sorted({Path(__file__), Path(overlay.__file__), *auxiliary.source_paths()})


def load_baseline(source_hashes):
    """Use current-loader provenance and native typed indexes; no new export."""
    require(type(source_hashes) is dict and source_hashes, 'validated source hashes required')
    paths = sorted({*(ROOT/p for p in source_hashes), *current.source_paths(), *source_paths()})
    before = current.snapshot(paths)
    native_paths = {str(p.relative_to(ROOT)) for p in current.source_paths()}
    require(native_paths <= set(source_hashes) and all(before.get(k) == v for k, v in source_hashes.items()),
            'sources changed or stale/incomplete current-loader provenance')
    auxiliary.load_reviewed()
    data = {key: crossings.load(ROOT/crossings.INPUTS[key]) for key in ('nets', 'instances', 'material', 'devices')}
    contracts = {key: crossings.load(ROOT/path) for key, path in crossings.LEDGER_CONTRACTS.items()}
    crossings.validate_provenance(data, contracts, before)
    reviews = crossings.semantics.reviewed_maps([crossings.load(p) for p in crossings.semantics.MAPS],
                                               data['material']['groups'])
    _, indexed = crossings.indexes(data, reviews)
    by_endpoint = row_index([p for rows in indexed.values() for p in rows], 'endpoint')
    # Retain native order while adding only source-reviewed MPN/pads/types.
    rows = {'instances': deepcopy(data['instances']['rows']),
            'pins': [deepcopy(by_endpoint[r['project'], r['endpoint']]) for r in data['nets']['rows']]}
    require(current.snapshot(paths) == before, 'sources changed during baseline load')
    return {**rows, 'source_sha256': before, 'baseline_digest': digest(rows)}


def _baseline_indexes(baseline):
    require(set(baseline) == {'instances', 'pins', 'source_sha256', 'baseline_digest'} and
            baseline['baseline_digest'] == digest({k: baseline[k] for k in ('instances', 'pins')}),
            'baseline rows/digest differ')
    instances, pins = row_index(baseline['instances'], 'instance'), row_index(baseline['pins'], 'endpoint')
    row_index(baseline['instances'], 'reference')
    require(current.snapshot([ROOT/p for p in baseline['source_sha256']]) == baseline['source_sha256'],
            'baseline source hashes changed')
    for name in CHANGED_INSTANCES:
        row = instances.get((PROJECT, name))
        require(row is not None and row['reference'] == REFERENCES[name] and row['sheet'] == SHEET,
                'native MAIN instance/reference/sheet differs')
    require(not any((PROJECT, name) in instances for name in ADDED_INSTANCES) and
            not any(r['project'] == PROJECT and r['reference'] in (REFERENCES[n] for n in ADDED_INSTANCES)
                    for r in baseline['instances']) and
            not any(r['project'] == PROJECT and r['net'] == SENSE_NET for r in baseline['pins']),
            'experimental instance/reference/net collision')
    return instances, pins


def _design(group, threshold, supply_node):
    """Bound the overlay to an upstream unqualified selected result, not solve it."""
    require(supply_node in SUPPLY_NODES, 'unsupported monitor supply node')
    require(group['qualified'] is False and group['monitor'] == 'tps3703a7330' and
            group['divider_class'] in ('0.1pct_10ppm', '0.05pct_10ppm'), 'unqualified selected monitor/divider group required')
    selected = group['selected_static_pair']
    loaded = selected['loaded_diagnostic']
    require(selected['qualified'] is False and selected['resistor_class'] == group['divider_class'] and
            selected['status'] == 'conditional_joint_candidate' and loaded['qualified'] is False and
            loaded['source_applicability'] is False and loaded['status'] == 'conditional_static_pass' and
            loaded['checked_load_cases'] == len(loaded['cases']) == 58, 'complete conditional loaded pair required')
    require(threshold in group['rilm_portfolios'] and threshold['qualified'] is False and
            threshold['source_applicability'] is False and threshold['status'] == 'conditional_known_divider_candidate' and
            threshold['requirements'] == group['requirements'] and threshold['rilm_class'] in
            ('1pct_100ppm', '0.1pct_10ppm', '0.05pct_10ppm'), 'threshold does not belong to selected unqualified group')
    spec = threshold['spec']
    require(F(spec['equation_constant_a_ohm']) == 6585 and F(spec['gain_tolerance_fraction']) == F('.1') and
            F(spec['configured_accuracy_domain_min_a_exclusive']) == 5, 'candidate law differs from TPS259814 hypothesis')
    nominal = threshold['selected_nominal_ohm']
    require(type(nominal) is str and F(nominal) > 0 and
            len([r for r in threshold['candidates'] if r['nominal_ohm'] == nominal]) == 1, 'selected RILM nominal missing/duplicate')
    chosen = next(r for r in threshold['candidates'] if r['nominal_ohm'] == nominal)
    require(chosen['qualified'] is False and F(chosen['minimum_margin_a_exact']) >= 0 and
            chosen['minimum_margin_a_exact'] == threshold['minimum_margin_a_exact'] and
            [r['budget'] for r in chosen['checks']] == list(current.BUDGETS) and
            all(F(r['nominal_ohm']) == F(nominal) for r in chosen['checks']) and
            all(r['numerical_constraints_met'] is True and F(r['configured_min_a_exact']) > 5 for r in chosen['checks']),
            'selected RILM lacks conditional forward checks')
    fixture = auxiliary.load_reviewed()
    properties = {'main_efuse': {'kind': 'efuse', 'mpn_hypothesis': fixture['replacement_interface']['candidate_mpn']},
                  'exp_main_monitor': {'kind': 'voltage_monitor', 'mpn_hypothesis': fixture['monitor_interface']['mpn']},
                  'exp_main_monitor_bypass': {'kind': 'capacitor', 'value_f_exact': '1/10000000', 'nominal_only': True}}
    for name, section, leg in (('main_efuse_pg_bottom', 'monitor_pair', 'bottom'),
                               ('main_efuse_pg_top', 'monitor_pair', 'top'),
                               ('main_fb_bottom', 'feedback', 'bottom'), ('main_fb_top', 'feedback', 'top')):
        value = selected[section]['selected_nominal_ohm_exact'][leg]
        require(type(value) is str and F(value) > 0, 'positive exact selected resistor nominal required')
        properties[name] = {'kind': 'resistor', 'value_ohm_exact': value,
                            'resistor_class': group['divider_class'], 'spread_scope': 'initial_plus_tcr_only'}
    properties['main_efuse_rilm'] = {'kind': 'resistor', 'value_ohm_exact': nominal,
                                    'resistor_class': threshold['rilm_class'], 'spread_scope': 'both_declared_RILM_diagnostic_budgets'}
    connections = {name: {contact: (physical, net, 'passive') for contact, (physical, net) in rows.items()}
                   for name, rows in RESISTOR_CONNECTIONS.items()}
    native = current.power.PINS['main_efuse'][1]
    connections['main_efuse'] = {p['name']: (p['physical'], None if p['name'] == 'FLT' else native[p['name']][1],
                                            auxiliary.PIN_TYPES[p['type']]) for p in fixture['replacement_interface']['pins']}
    monitor_nets = {'SENSE': SENSE_NET, 'VDD': supply_node, 'CT': None, 'RESET': 'POWER_FAULT_N',
                    'GND': 'POWER_GROUND', 'MR': None}
    connections['exp_main_monitor'] = {name: (physical, monitor_nets[name], MONITOR_TYPES[name])
                                       for name, physical in fixture['monitor_interface']['pins'].items()}
    connections['exp_main_monitor_bypass'] = {'END_1': ('1', supply_node, 'passive'),
                                              'END_2': ('2', 'POWER_GROUND', 'passive')}
    return fixture, properties, connections


def _metadata(baseline, group, threshold, supply_node, fixture):
    return {'schema_version': 1, 'status': 'nonproduction_candidate', 'qualified': False,
            'native_cad': False, 'production_mpn_selected': False, 'physical_compatibility_proven': False,
            'scope': 'Complete in-memory experimental ledger overlay; source-loaded, not fresh native CAD',
            'origin': ORIGIN, 'baseline_digest': baseline['baseline_digest'],
            'source_sha256': deepcopy(baseline['source_sha256']),
            'parameters': {'divider_class': group['divider_class'], 'rilm_class': threshold['rilm_class'],
                           'monitor_supply_node': supply_node, 'selected_window_index': group['selected_window_index']},
            'source_facts': {'sources': deepcopy(fixture['sources']),
                'efuse': {'source_id': 'tps25981', 'pages': [4, 27],
                          'fact': 'PG retained for FET-on indication; FLT explicitly unused, not a PGTH input nor complete UV/OV indication'},
                'monitor': {'source_id': 'tps3703', 'pages': [4, 27],
                            'fact': '100 nF nominal VDD bypass hypothesis within recommended 0.1..1 uF; no tolerance/MPN/physical qualification'}},
            'limits': ['No source-current, RON, leakage, control/timing, startup or physical bound is promoted',
                       'R266 and other native fault endpoints retained; no proof of live pullup or aggregate current coverage',
                       'Generic resistors/capacitor and IC hypotheses are not native exact-part identities or assembly choices']}


def _identity(name, spec, original=None):
    return {'device_id': 'generic_candidate_'+name, 'mpn': None, 'symbol_id': None, 'footprint': None,
            'allocation_origin': ORIGIN, 'bom_excluded': True,
            'source_instance': {k: deepcopy(original[k]) for k in IDENTITY_FIELDS} if original else None,
            'generic_candidate': deepcopy(spec)}


def _pin_fields(name, contact, definition, source_endpoint=None):
    physical, net, kind = definition
    return {'device_id': 'generic_candidate_'+name, 'mpn': None, 'origin': ORIGIN,
            'source_endpoint': source_endpoint, 'contact': contact, 'endpoint': name+'.'+contact,
            'physical': physical, 'pads': [physical], 'type': kind, 'net': net,
            'disposition': 'no_connect' if net is None else 'connected'}


def build_candidate(baseline, group, threshold, supply_node):
    old_instances, _ = _baseline_indexes(baseline)
    fixture, specs, connections = _design(group, threshold, supply_node)
    result = {**_metadata(baseline, group, threshold, supply_node, fixture),
              'instances': deepcopy(baseline['instances']), 'pins': deepcopy(baseline['pins'])}
    for row in result['instances']:
        if row['project'] == PROJECT and row['instance'] in CHANGED_INSTANCES:
            row.update(_identity(row['instance'], specs[row['instance']], old_instances[PROJECT, row['instance']]))
    for row in result['pins']:
        name = row['instance']
        if row['project'] == PROJECT and name in CHANGED_INSTANCES:
            contact = 'FLT' if name == 'main_efuse' and row['contact'] == 'PGTH' else row['contact']
            row.update(_pin_fields(name, contact, connections[name][contact], row['endpoint']))
    for name in ADDED_INSTANCES:
        result['instances'].append({'instance_uid': PROJECT+':'+name, 'instance': name, 'project': PROJECT,
            'sheet': SHEET, 'reference': REFERENCES[name], 'reference_prefix': 'U' if name == 'exp_main_monitor' else 'C',
            'historical_topology_authority': False, **_identity(name, specs[name])})
        for contact, definition in connections[name].items():
            result['pins'].append({'project': PROJECT, 'sheet': SHEET, 'reference': REFERENCES[name], 'instance': name,
                'role': 'power' if definition[2] == 'power_in' else 'signal', 'historical_topology_authority': False,
                **_pin_fields(name, contact, definition)})
    result['validation'] = validate_candidate(baseline, result, group, threshold, supply_node)
    return result


def validate_candidate(baseline, candidate, group, threshold, supply_node):
    """Check explicit field deltas and physical/contact membership, not build replay."""
    old_instances, old_pins = _baseline_indexes(baseline)
    fixture, specs, connections = _design(group, threshold, supply_node)
    metadata = _metadata(baseline, group, threshold, supply_node, fixture)
    require({k: v for k, v in candidate.items() if k not in ('instances', 'pins', 'validation')} == metadata,
            'candidate source/authority/selection metadata differs')
    instances, pins = row_index(candidate['instances'], 'instance'), row_index(candidate['pins'], 'endpoint')
    row_index(candidate['instances'], 'reference')
    added_keys = {(PROJECT, name) for name in ADDED_INSTANCES}
    require(set(instances) == set(old_instances) | added_keys, 'candidate instance membership differs')
    removed = {(PROJECT, 'main_efuse.PGTH')}
    added = {(PROJECT, 'main_efuse.FLT')} | {(PROJECT, name+'.'+contact)
                                           for name in ADDED_INSTANCES for contact in connections[name]}
    require(set(pins) == (set(old_pins)-removed) | added, 'candidate contact membership differs')
    require([(r['project'], r['instance']) for r in candidate['instances']] ==
            [(r['project'], r['instance']) for r in baseline['instances']] + [(PROJECT, n) for n in ADDED_INSTANCES],
            'candidate instance order differs')
    touched_pin_count = 0
    for key, original in old_instances.items():
        row = instances[key]
        if key[0] != PROJECT or key[1] not in CHANGED_INSTANCES:
            require(row == original, 'unrelated native instance changed: '+str(key))
        else:
            require({k: v for k, v in row.items() if k not in INSTANCE_DELTA_FIELDS} ==
                    {k: v for k, v in original.items() if k not in INSTANCE_DELTA_FIELDS} and
                    {k: row.get(k) for k in INSTANCE_DELTA_FIELDS} == _identity(key[1], specs[key[1]], original),
                    'candidate instance identity/value/source differs: '+str(key))
    expected_pin_order = []
    for key, original in old_pins.items():
        name, contact = original['instance'], original['contact']
        if key[0] != PROJECT or name not in CHANGED_INSTANCES:
            require(pins[key] == original, 'unrelated native endpoint changed: '+str(key))
            expected_pin_order.append(key)
            continue
        touched_pin_count += 1
        if name == 'main_efuse' and contact == 'PGTH':
            contact = 'FLT'
        new_key = (PROJECT, name+'.'+contact)
        expected_pin_order.append(new_key)
        row = pins[new_key]
        require({k: v for k, v in row.items() if k not in PIN_DELTA_FIELDS} ==
                {k: v for k, v in original.items() if k not in PIN_DELTA_FIELDS} and
                {k: row.get(k) for k in PIN_DELTA_FIELDS} == _pin_fields(name, contact, connections[name][contact], original['endpoint']),
                'candidate physical pin/type/net/source differs: '+str(new_key))
    for name in ADDED_INSTANCES:
        row = instances[PROJECT, name]
        require(row == {'instance_uid': PROJECT+':'+name, 'instance': name, 'project': PROJECT,
                'sheet': SHEET, 'reference': REFERENCES[name], 'reference_prefix': 'U' if name == 'exp_main_monitor' else 'C',
                'historical_topology_authority': False, **_identity(name, specs[name])}, 'added generic instance differs')
        for contact, definition in connections[name].items():
            key = (PROJECT, name+'.'+contact)
            expected_pin_order.append(key)
            require(pins[key] == {'project': PROJECT, 'sheet': SHEET, 'reference': REFERENCES[name], 'instance': name,
                    'role': 'power' if definition[2] == 'power_in' else 'signal', 'historical_topology_authority': False,
                    **_pin_fields(name, contact, definition)}, 'added monitor/bypass contact differs')
    require([(r['project'], r['endpoint']) for r in candidate['pins']] == expected_pin_order, 'candidate endpoint order differs')
    for name in CHANGED_INSTANCES+ADDED_INSTANCES:
        rows = [r for r in candidate['pins'] if r['project'] == PROJECT and r['instance'] == name]
        require(len(rows) == len(connections[name]) and {r['contact'] for r in rows} == set(connections[name]) and
                len({r['physical'] for r in rows}) == len(rows) and all(r['pads'] == [r['physical']] for r in rows),
                'candidate physical contact coverage/uniqueness differs')
    native_fault = {key for key, row in old_pins.items() if key[0] == PROJECT and row['net'] == 'POWER_FAULT_N'}
    candidate_fault = {key for key, row in pins.items() if key[0] == PROJECT and row['net'] == 'POWER_FAULT_N'}
    require(len(native_fault) == 8 and candidate_fault == native_fault | {(PROJECT, 'exp_main_monitor.RESET')},
            'shared fault-net membership differs')
    require(not any(row['project'] == PROJECT and row['net'] == 'MAIN_EFUSE_PGTH' for row in candidate['pins']),
            'obsolete PGTH connection retained')
    receipt = {'qualified': False, 'checked': True, 'changed_instances': list(CHANGED_INSTANCES),
               'added_instances': list(ADDED_INSTANCES), 'preserved_instances': len(old_instances)-len(CHANGED_INSTANCES),
               'preserved_pins': len(old_pins)-touched_pin_count, 'changed_pin_records': touched_pin_count,
               'added_pin_records': sum(len(connections[n]) for n in ADDED_INSTANCES),
               'fault_endpoint_count': len(candidate_fault),
               'candidate_sha256': digest({k: v for k, v in candidate.items() if k != 'validation'})}
    require('validation' not in candidate or candidate['validation'] == receipt, 'stale or altered validation receipt')
    return receipt
