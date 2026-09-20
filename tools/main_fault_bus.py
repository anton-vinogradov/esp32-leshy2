"""Exact conditional POWER_FAULT_N current requirements, not a driver model.

Positive total signed current draws from the bus: Vbus = MAIN - R * I.
The common current interval is sufficient for a voltage-independent bound;
it is not necessary for correlated, voltage-dependent physical leakage.
"""
from copy import deepcopy
from fractions import Fraction as F
import hashlib
from itertools import product
import json
from pathlib import Path
import re

import main_auxiliary_scope as auxiliary
import main_candidate_topology as topology

current, require, ROOT = auxiliary.current, auxiliary.require, auxiliary.ROOT
ROWS_PATH = ROOT / 'hardware/verification/h6-power-fault-receiver-sources.json'
REVIEWED_SHA256 = '9a4657ddb6e24c730eb6a1edd1c1de09a73ffdcbeb7c46e83de2ec4d080b7f2d'
PROJECT, BUS = 'LESHY2-RF-R2', 'POWER_FAULT_N'
RECEIVERS = {
    'main_slow_io_p07': ('slow_io', 'U106', 'P07', '8', 'tca6424argjr', 'TCA6424ARGJR'),
    'aon_safety_pa30': ('safety_controller', 'U127', 'PA30', '3',
                       'ti_mspm0c1106_sdgs20r', 'Texas Instruments MSPM0C1106SDGS20R'),
}
# Literal retained native members; collector pins remain reviewed passive pins.
OTHER_NATIVE = {
    'ext_efuse.FLT': ('U17', '4', 'open_collector', 'ti_tps259470l_rpwr', 'Texas Instruments TPS259470LRPWR'),
    'unit_efuse.FLT': ('U100', '4', 'open_collector', 'ti_tps259470l_rpwr', 'Texas Instruments TPS259470LRPWR'),
    'ext_pg_qualifier.C': ('Q4', '3', 'passive', 'diodes_mmbt3904_7_f', 'Diodes Incorporated MMBT3904-7-F'),
    'voice_pg_qualifier.C': ('Q5', '3', 'passive', 'diodes_mmbt3904_7_f', 'Diodes Incorporated MMBT3904-7-F'),
}


def source_paths():
    return sorted({Path(__file__), ROWS_PATH, *topology.source_paths(), *current.source_paths()})


def load_reviewed():
    require(ROWS_PATH.is_file() and not ROWS_PATH.is_symlink(), 'missing or symlinked receiver fixture')
    raw = ROWS_PATH.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == REVIEWED_SHA256, 'receiver fixture changed; review required')
    record = json.loads(raw)
    require(type(record['schema_version']) is int and record['schema_version'] == 1 and
            record['scope'] == 'conditional receiver admissibility, not loaded voltage proof' and
            record['qualified'] is False, 'receiver source authority differs')
    rows = record['receivers']
    require(len(rows) == 2 and {r['id'] for r in rows} == set(RECEIVERS), 'missing/duplicate receiver source')
    for row in rows:
        require(tuple(row[k] for k in ('instance', 'reference', 'contact', 'physical', 'device_id', 'mpn')) ==
                RECEIVERS[row['id']] and row['project'] == PROJECT and row['net'] == BUS,
                'literal reviewed receiver identity differs')
        require(row['gpio_mode_proven'] is False and row['off_state_proven'] is False and
                row['input_limits']['vih_factor'] == '0.7' and row['input_limits']['vil_factor'] == '0.3' and
                all(r['minimum'] is None and r['typical'] is None and r['unit'] == 'A' and
                    r['signed_interval_proven'] is False and r['full_input_voltage_range_proven'] is False
                    for r in row['leakage_rows']), 'receiver source conditions or unknown bounds differ')
    tca, msp = ({r['id']: r for r in rows}[name] for name in RECEIVERS)
    require(tca['pin_function']['kind'] == 'configurable_push_pull_gpio' and
            msp['pin_function']['kind'] == 'SDIO' and msp['pin_function']['analog_input_mux_present'] is False and
            tca['input_limits']['input_high_max'] == {'law': 'fixed', 'v': '5.5'} and
            msp['input_limits']['input_high_max'] == {'law': 'supply_plus', 'supply_contact': 'VDD', 'offset_v': '0.3'} and
            [r['maximum'] for r in tca['leakage_rows']] == ['0.000001', '0.000001'] and
            [r['maximum'] for r in msp['leakage_rows']] == ['0.00000005'], 'reviewed input type/law/leakage differs')
    return record


def _bounds(values):
    require(type(values) is list and len(values) == 2 and all(type(v) is str and
            re.fullmatch(r'[+-]?(?:\d+/\d+|(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)', v)
            for v in values), 'two strict finite exact interval strings required')
    try:
        return auxiliary.bounds(values)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError('invalid exact interval') from exc


def screen(*, main_v, aon_v, resistance_ohm, temperature_c, fixture=None):
    reviewed = load_reviewed()
    require(fixture is None or fixture == reviewed, 'unreviewed receiver fixture override')
    main, aon, resistance, temperature = map(_bounds, (main_v, aon_v, resistance_ohm, temperature_c))
    require(main[0] >= 0 and aon[0] >= 0 and resistance[0] > 0 and temperature[0] >= F('-273.15'),
            'negative supply, nonpositive resistance or impossible temperature')
    applicability = []
    for receiver in reviewed['receivers']:
        supply = main if receiver['id'] == 'main_slow_io_p07' else aon
        checks = {p['contact']: F(p['operating_v'][0]) <= supply[0] <= supply[1] <= F(p['operating_v'][1])
                  for p in receiver['supplies']}
        temp = receiver['operating_temperature']['range']
        checks['ta_c'] = F(temp[0]) <= temperature[0] <= temperature[1] <= F(temp[1])
        applicability.append({'receiver': receiver['id'], 'source_id': receiver['source_id'],
            'numeric_domains_covered': all(checks.values()), 'checks': checks,
            'uncovered_axes': [k for k, v in checks.items() if not v],
            'gpio_mode_proven': False, 'off_state_proven': False, 'leakage_interval_admitted': False,
            'maximum_junction_temperature_c': receiver.get('maximum_junction_temperature_c'),
            'junction_temperature_proven': False})
    corners = []
    endpoints = [list(dict.fromkeys(v)) for v in (main, aon, resistance)]
    for (mi, mv), (ai, av), (ri, rv) in product(*(list(enumerate(v)) for v in endpoints)):
        high, upper, low = F('.7') * max(mv, av), min(F('5.5'), av + F('.3')), F('.3') * min(mv, av)
        minimum, maximum = (mv - upper) / rv, (mv - high) / rv
        violations = (['below_vih'] if mv < high else []) + (['above_input_max'] if mv > upper else [])
        corners.append({'id': f'm{mi}_a{ai}_r{ri}', 'main_v_exact': str(mv), 'aon_v_exact': str(av),
            'resistance_ohm_exact': str(rv), 'vih_min_v_exact': str(high), 'input_max_v_exact': str(upper),
            'vil_max_v_exact': str(low), 'input_lower_min_v_exact': '-3/10',
            'allowed_total_signed_current_a': {'minimum_a_exact': str(minimum), 'maximum_a_exact': str(maximum),
                                               'empty': minimum > maximum},
            'pullup_sink_current_at_vil_a_exact': str((mv - low) / rv),
            'zero_current': {'bus_v_exact': str(mv), 'high_compatible': not violations, 'violations': violations}})
    lower = max(F(c['allowed_total_signed_current_a']['minimum_a_exact']) for c in corners)
    upper = min(F(c['allowed_total_signed_current_a']['maximum_a_exact']) for c in corners)
    result = {'status': 'conditional_fault_bus_screen', 'qualified': False,
        'thresholds_admitted': all(r['numeric_domains_covered'] for r in applicability),
        'source_applicability': applicability, 'full_source_applicability': False,
        'gpio_mode_proven': False, 'off_state_proven': False, 'loaded_voltage_proven': False,
        'actual_total_signed_current_a': None, 'source_sha256': {str(ROWS_PATH.relative_to(ROOT)): REVIEWED_SHA256},
        'stimulus': deepcopy({'main_v': main_v, 'aon_v': aon_v, 'resistance_ohm': resistance_ohm,
                              'temperature_c': temperature_c}),
        'current_sign': 'positive draws from bus; Vbus = MAIN - R * I',
        'corners': corners,
        'uniform_current_interval': {'minimum_a_exact': str(lower), 'maximum_a_exact': str(upper),
            'empty': lower > upper, 'sufficient_not_necessary': True,
            'minimum_witnesses': [c['id'] for c in corners if F(c['allowed_total_signed_current_a']['minimum_a_exact']) == lower],
            'maximum_witnesses': [c['id'] for c in corners if F(c['allowed_total_signed_current_a']['maximum_a_exact']) == upper]},
        'zero_current_diagnostic': {'assumed_total_signed_current_a': '0', 'actual_current_assumed': False,
            'all_corners_high_compatible': all(c['zero_current']['high_compatible'] for c in corners),
            'violating_corner_ids': [c['id'] for c in corners if not c['zero_current']['high_compatible']]},
        'limits': ['Common interval is sufficient for a uniform signed-current bound, not necessary for voltage-correlated leakage',
                   'Out-of-source supply/temperature corners retain diagnostic arithmetic, not admitted threshold guarantees',
                   'Threshold admission covers source supply/TA domains only; GPIO mode and actual junction temperature remain unproved',
                   'No actual leakage bound follows from rail-endpoint-only source current rows; no implicit zero current',
                   'Low-state value is pullup current at VIL, not proof that any driver can sink it or establish VOL',
                   'No transient, powered-off, driver, ground-offset, input-slew or complete bus qualification']}
    require(load_reviewed() == reviewed, 'receiver source changed during screen')
    return result


def assess_candidate(candidate, *, main_v, aon_v, resistance_ohm, temperature_c):
    """Bind the conditional screen to the checked full candidate, not loose pins."""
    before = current.snapshot(source_paths())
    reviewed, aux = load_reviewed(), auxiliary.load_reviewed()
    require(type(candidate) is dict and candidate.get('status') == 'nonproduction_candidate' and
            all(candidate.get(k) is False for k in ('qualified', 'native_cad', 'production_mpn_selected',
                                                   'physical_compatibility_proven')), 'unqualified full candidate required')
    original_digest = topology.digest(candidate)
    receipt = candidate.get('validation', {})
    body_digest = topology.digest({k: v for k, v in candidate.items() if k != 'validation'})
    require(receipt.get('checked') is True and receipt.get('qualified') is False and
            receipt.get('candidate_sha256') == body_digest and receipt.get('fault_endpoint_count') == 9,
            'missing/stale candidate topology validation')
    hashes = candidate.get('source_sha256')
    required_paths = {str(p.relative_to(ROOT)) for p in current.source_paths()}
    require(type(hashes) is dict and required_paths <= set(hashes) and
            current.snapshot([ROOT / p for p in hashes]) == hashes, 'candidate source provenance missing/stale')
    instances = topology.row_index(candidate['instances'], 'instance')
    topology.row_index(candidate['instances'], 'reference')
    pins = topology.row_index(candidate['pins'], 'endpoint')
    scoped_instances = {r['instance'] for r in reviewed['receivers']} | {
        e.split('.')[0] for e in OTHER_NATIVE} | {'main_efuse', 'exp_main_monitor', 'power_fault_pullup'}
    physical_keys = [(r['instance'], p) for r in candidate['pins'] if r['project'] == PROJECT and
                     r['instance'] in scoped_instances for p in r['pads']]
    require(len(set(physical_keys)) == len(physical_keys), 'duplicate candidate physical pin')

    def check(instance, contact, physical, net, kind, reference, device, mpn, pads=None):
        component = instances.get((PROJECT, instance))
        row = pins.get((PROJECT, instance + '.' + contact))
        require(component is not None and row is not None, 'missing fault participant/contact')
        require(component['reference'] == reference and component['device_id'] == device and component['mpn'] == mpn and
                row['instance'] == instance and row['contact'] == contact and row['reference'] == reference and
                row['device_id'] == device and row['mpn'] == mpn and row['physical'] == physical and
                row['pads'] == (pads or [physical]) and row['net'] == net and row['type'] == kind and
                row['disposition'] == ('no_connect' if net is None else 'connected'), 'fault binding identity/pin/type/net differs')

    bus_endpoints = set()
    for receiver in reviewed['receivers']:
        identity = (receiver['reference'], receiver['device_id'], receiver['mpn'])
        check(receiver['instance'], receiver['contact'], receiver['physical'], BUS, 'bidirectional', *identity)
        bus_endpoints.add(receiver['instance'] + '.' + receiver['contact'])
        expected_power = {r['contact'] for r in receiver['supplies']} | {
            r['contact'] for r in receiver['ground_contacts'] if r['contact'] != 'EPAD'}
        actual_power = {r['contact'] for r in candidate['pins'] if r['project'] == PROJECT and
                        r['instance'] == receiver['instance'] and r['type'] == 'power_in'}
        require(actual_power == expected_power, 'missing/extra receiver supply or ground contact')
        for supply in receiver['supplies']:
            check(receiver['instance'], supply['contact'], supply['physical'], supply['net'], 'power_in', *identity)
        for ground in receiver['ground_contacts']:
            check(receiver['instance'], ground['contact'], ground['physical'], ground['net'],
                  'passive' if ground['contact'] == 'EPAD' else 'power_in', *identity, pads=ground['pads'])
    for endpoint, (reference, physical, kind, device, mpn) in OTHER_NATIVE.items():
        instance, contact = endpoint.split('.')
        check(instance, contact, physical, BUS, kind, reference, device, mpn)
        bus_endpoints.add(endpoint)
    for name, reference, kind, source in (
            ('main_efuse', 'U21', 'efuse', aux['replacement_interface']['candidate_mpn']),
            ('exp_main_monitor', 'EXP_U_MAIN_MON', 'voltage_monitor', aux['monitor_interface']['mpn'])):
        component = instances.get((PROJECT, name), {})
        require(component.get('generic_candidate') == {'kind': kind, 'mpn_hypothesis': source} and
                all(component.get(k) is None for k in ('mpn', 'symbol_id', 'footprint')) and
                component.get('allocation_origin') == topology.ORIGIN and component.get('bom_excluded') is True,
                'generic candidate IC identity differs')
        if name == 'main_efuse':
            connections = {p['name']: (p['physical'], None if p['name'] == 'FLT' else
                           current.power.PINS['main_efuse'][1][p['name']][1], auxiliary.PIN_TYPES[p['type']])
                           for p in aux['replacement_interface']['pins']}
            bus_endpoints.add('main_efuse.PG')
        else:
            supply = candidate['parameters']['monitor_supply_node']
            require(supply in topology.SUPPLY_NODES, 'monitor supply differs')
            nets = {'SENSE': topology.SENSE_NET, 'VDD': supply, 'CT': None, 'RESET': BUS, 'GND': 'POWER_GROUND', 'MR': None}
            connections = {contact: (pin, nets[contact], topology.MONITOR_TYPES[contact])
                           for contact, pin in aux['monitor_interface']['pins'].items()}
            bus_endpoints.add('exp_main_monitor.RESET')
        require(len([r for r in candidate['pins'] if r['project'] == PROJECT and r['instance'] == name]) == len(connections),
                'candidate IC has missing/extra contacts')
        for contact, (physical, net, pin_kind) in connections.items():
            check(name, contact, physical, net, pin_kind, reference, 'generic_candidate_' + name, None)
    pullup = aux['native_fault_pullup']
    pull_component = instances.get((PROJECT, pullup['instance']), {})
    require('generic_candidate' not in pull_component and
            len([r for r in candidate['pins'] if r['project'] == PROJECT and r['instance'] == pullup['instance']]) == 2,
            'R266 replaced or missing/extra contacts')
    for contact, physical, net in (('END_1', pullup['supply_physical'], pullup['supply_node']),
                                   ('END_2', pullup['signal_physical'], pullup['signal_node'])):
        check(pullup['instance'], contact, physical, net, 'passive', pullup['reference'], pullup['device_id'],
              'Yageo RC0402FR-0710KL')
    bus_endpoints.add(pullup['instance'] + '.END_2')
    actual_bus = {r['endpoint'] for r in candidate['pins'] if r['project'] == PROJECT and r['net'] == BUS}
    require(len(bus_endpoints) == 9 and actual_bus == bus_endpoints, 'missing/extra/changed fault-bus participant')
    rlo, rhi = _bounds(resistance_ohm)
    nominal, tolerance = F(pullup['nominal_ohm']), F(pullup['initial_tolerance_fraction'])
    require(rlo <= nominal * (1 - tolerance) and rhi >= nominal * (1 + tolerance),
            'resistance interval does not cover native R266 initial tolerance')
    result = screen(main_v=main_v, aon_v=aon_v, resistance_ohm=resistance_ohm,
                    temperature_c=temperature_c, fixture=reviewed)
    result['binding'] = {'checked': True, 'qualified': False, 'candidate_sha256': body_digest,
        'project': PROJECT, 'net': BUS, 'endpoint_count': len(actual_bus), 'endpoints': sorted(actual_bus),
        'native_pullup': deepcopy(pullup), 'resistance_spread_qualified': False,
        'resistance_scope': 'Covers initial tolerance; wider caller interval is not a source-qualified TCR/lifetime bound',
        'generic_ic_mpn_adoption': False, 'driver_current_bounds_proven': False}
    require(topology.digest(candidate) == original_digest, 'candidate mutated during fault screen')
    require(current.snapshot(source_paths()) == before, 'sources changed during fault screen')
    return result
