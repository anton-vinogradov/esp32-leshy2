"""Conditional AON delivery using the existing H3 forward model, not a solver.

The native source guard and complete current profile report are replayed. All
extra AON load, actual voltage and fitted-condition RON bounds remain unknown.
"""
from copy import deepcopy
from decimal import Decimal
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

import compare_main_current_limit as current
import main_auxiliary_scope as auxiliary
import main_candidate_topology as topology
import main_fault_bus as fault_bus

ROOT, require, h3 = current.ROOT, current.require, current.source.h3
ROWS_PATH = ROOT / 'hardware/verification/h6-aon-delivery-sources.json'
REVIEWED_SHA256 = '3671acd0f486403f6d9ee971fb6b1911bdc8aaecc255e7c3baf1760892631122'
PROJECT, RAIL = 'LESHY2-RF-R2', 'AON_SAFE_3V3'
ENVELOPES = ('legacy_h3_raw_2pct', 'source_conditioned_vset_1pct')
IDENTITIES = {
    'aon_buck': ('U13', 'ti_tps629203_drlr', 'Texas Instruments TPS629203DRLR'),
    'aon_efuse': ('U14', 'ti_tps25961_drvr', 'Texas Instruments TPS25961DRVR'),
    'aon_mode_res': ('R47', 'yageo_rc0402fr_0742k2l', 'Yageo RC0402FR-0742K2L'),
    'aon_efuse_rilim': ('R46', 'yageo_rc0402fr_07240kl', 'Yageo RC0402FR-07240KL'),
    'safety_controller': ('U127', 'ti_mspm0c1106_sdgs20r', 'Texas Instruments MSPM0C1106SDGS20R'),
}


def source_paths():
    return sorted({Path(__file__), ROWS_PATH, *current.source_paths(),
                   *topology.source_paths(), *fault_bus.source_paths()})


def load_reviewed():
    require(ROWS_PATH.is_file() and not ROWS_PATH.is_symlink(), 'missing or symlinked AON fixture')
    raw = ROWS_PATH.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == REVIEWED_SHA256, 'AON fixture changed; review required')
    record = json.loads(raw)
    require(type(record['schema_version']) is int and record['schema_version'] == 1 and
            record['qualified'] is False and record['actual_raw_output_v'] is None and
            record['actual_ron_max_ohm'] is None, 'AON source authority differs')
    buck, efuse = record['buck'], record['efuse']
    for item in (buck, efuse, buck['mode_resistor'], efuse['rilim']):
        identity = item['identity']
        name = identity['instance']
        require(name in IDENTITIES and identity == dict(zip(
            ('project', 'instance', 'reference', 'device_id', 'mpn'), (PROJECT, name, *IDENTITIES[name]))),
            'AON source identity differs')
        if name in current.power.PINS:
            device, pins = current.power.PINS[name]
            require(device == identity['device_id'], 'AON physical authority device differs')
        else:
            pins = {f'END_{n}': (str(n), net) for n, net in enumerate(current.power.PASSIVES[name], 1)}
        expected = [{'contact': contact, 'physical': physical, 'net': net,
                     'disposition': 'no_connect' if net is None else 'connected'}
                    for contact, (physical, net) in pins.items()]
        normalized = [{**p, 'physical': p['physical'].split()[0]} for p in item['pins']]
        require(normalized == expected, 'AON source contact/physical/net authority differs')
    require(buck['selection']['programmed_nominal_v'] == buck['regulation']['nominal_v'] == '3.3' and
            buck['regulation']['minimum_fraction'] == '-0.01' and buck['regulation']['maximum_fraction'] == '0.01' and
            buck['selection']['configuration_hardware_proven'] is False and
            buck['regulation']['regulation_prerequisites_proven'] is False and
            buck['mode_resistor']['fitted_tcr_ppm_per_c'] is None and
            buck['mode_resistor']['tcr_source_bound'] is False and
            buck['mode_resistor']['maximum_absolute_tcr_ppm_per_c_required'] == '200',
            'conditional VSET/MODE source scope differs')
    require(buck['mode_resistor']['nominal_ohm'] == '42200' and efuse['rilim']['nominal_ohm'] == '240000' and
            buck['mode_resistor']['initial_tolerance_fraction'] == efuse['rilim']['initial_tolerance_fraction'] == '0.01' and
            efuse['rilim']['fitted_ron_maximum_admitted'] is False and
            efuse['current_limit']['guaranteed_fitted_minimum_a'] is None and
            efuse['current_limit']['guaranteed_fitted_maximum_a'] is None,
            'fitted resistor or unknown current/RON scope differs')
    return record


def _bind_native(reviewed, baseline):
    instances = topology.row_index(baseline['instances'], 'instance')
    pins = topology.row_index(baseline['pins'], 'endpoint')
    devices = json.loads((ROOT/current.power.INPUTS['devices']).read_text())['devices']
    observed = []
    for item in (reviewed['buck'], reviewed['efuse'], reviewed['buck']['mode_resistor'], reviewed['efuse']['rilim']):
        identity = item['identity']
        name = identity['instance']
        instance = instances.get((PROJECT, name))
        require(instance is not None and all(instance[k] == v for k, v in identity.items()) and
                instance['bom_excluded'] is False, 'fitted AON instance identity differs')
        native = [r for r in baseline['pins'] if r['project'] == PROJECT and r['instance'] == name]
        require(len(native) == len(item['pins']) and len({r['physical'] for r in native}) == len(native),
                'missing/extra/duplicate native AON physical contact')
        for pin in item['pins']:
            row = pins.get((PROJECT, name+'.'+pin['contact']))
            require(row is not None and all(row[k] == v for k, v in {**identity, **pin}.items()) and
                    row['pads'] == [pin['physical'].split()[0]], 'native AON pin/net/disposition differs')
        if 'nominal_ohm' in item:
            resistance, tolerance = current.power.resistance(devices[identity['device_id']])
            require(F(str(resistance)) == F(item['nominal_ohm']) and
                    F(str(tolerance)) == F(item['initial_tolerance_fraction']), 'native AON resistor value/tolerance differs')
        observed.append({'identity': deepcopy(identity), 'pins': deepcopy(item['pins'])})
    receiver = next(r for r in fault_bus.load_reviewed()['receivers'] if r['id'] == 'aon_safety_pa30')
    identity = dict(zip(('project', 'instance', 'reference', 'device_id', 'mpn'),
                        (PROJECT, 'safety_controller', *IDENTITIES['safety_controller'])))
    require(all(instances[PROJECT, 'safety_controller'][k] == v for k, v in identity.items()),
            'PA30 owner identity differs')
    for contact, physical, net, kind in [(receiver['contact'], receiver['physical'], receiver['net'], 'bidirectional'),
            *[(p['contact'], p['physical'], p['net'], 'power_in') for p in receiver['supplies']+receiver['ground_contacts']]]:
        row = pins.get((PROJECT, 'safety_controller.'+contact))
        require(row is not None and all(row[k] == v for k, v in identity.items()) and
                (row['physical'], row['pads'], row['net'], row['type'], row['disposition']) ==
                (physical, [physical], net, kind, 'connected'), 'PA30 supply/ground/signal binding differs')
    return {'checked': True, 'qualified': False, 'baseline_digest': baseline['baseline_digest'],
            'components': observed, 'receiver': deepcopy(identity),
            'same_native_project': PROJECT, 'native_cad_changed': False,
            'source_mode': 'Current guarded native ledgers, not a fresh KiCad export',
            'configuration_source_conditions_proven': False, 'native_current_inventory_qualified': False,
            'actual_aon_voltage_v': None, 'actual_ron_max_ohm': None}


def inverse_ron(*, raw_average_min_v, ripple_pp_v, distribution_drop_v,
                consumer_min_v, main_max_v, load_a):
    """Necessary DC RON ceiling for a zero-bus-current HIGH diagnostic only."""
    exact = lambda v: fault_bus._bounds([v, v])[0] if type(v) is str else current.exact(v)
    raw, ripple, distribution, minimum, main, load = map(exact, (
        raw_average_min_v, ripple_pp_v, distribution_drop_v, consumer_min_v, main_max_v, load_a))
    require(raw > 0 and min(ripple, distribution, minimum, main, load) >= 0,
            'invalid RON diagnostic axes')
    floor = max(minimum, main-F('.3'))
    headroom = raw-ripple/2-distribution-floor
    return {'required_consumer_floor_v_exact': str(floor),
            'headroom_v_exact': str(headroom),
            'load_a_exact': str(load), 'zero_load_case': load == 0,
            'required_max_ron_ohm_exact': None if load == 0 else str(headroom/load),
            'feasible_nonnegative_ron': headroom >= 0,
            'actual_ron_max_ohm': None, 'qualified': False,
            'scope': 'Consumer minimum and PA30 upper-input limit at zero bus current only; not complete HIGH/sink/startup proof'}


def _profile_rows(rail, path, profiles):
    rows = []
    for profile in profiles:
        identity = '/'.join(profile[k] for k in ('signal_group', 'group_mode', 'support_profile'))
        load = current.exact(profile['loads_ma'][RAIL])
        require(load >= 0, 'negative AON profile load')
        row = h3.rail_voltage_result(RAIL, rail, str(Decimal(load.numerator)/Decimal(load.denominator)),
                                     load_case=identity, voltage_path=path)
        # H3 emits microvolt-rounded display values. Retain this tiny exact
        # affine projection separately: reusing rounded minima could narrow a
        # later fault-screen bound. This is I*R bookkeeping, not a new solver.
        raw_low = current.exact(rail['raw_average_min_v'])-current.exact(rail['ripple_pp_v'])/2
        raw_high = current.exact(rail['raw_average_max_v'])+current.exact(rail['ripple_pp_v'])/2
        protected = raw_low-load/1000*current.exact(rail['efuse_ron_max_ohm'])
        consumer = protected-current.exact(rail['distribution_drop_v'])
        exact = dict(zip(('raw_min_v', 'raw_max_v', 'protected_local_min_v',
                          'protected_local_max_v', 'consumer_endpoint_min_v', 'consumer_endpoint_max_v'),
                         (raw_low, raw_high, protected, raw_high, consumer, raw_high)))
        require(all(abs(F(row[k])-v) <= F(1, 2000000) for k, v in exact.items()),
                'H3 forward result disagrees with exact passive projection')
        require(row['model_qualified'] is False and row['status'] == 'review_required',
                'AON diagnostic was falsely qualified')
        rows.append({**row, 'load_ma_exact': str(load),
                     'exact_bounds': {k: str(v) for k, v in exact.items()}})
    require(len(rows) == 56 and len({r['load_case'] for r in rows}) == 56,
            'missing, duplicate or changed AON profile inventory')
    return rows


def _projected_faults(envelope, rows, dc_result):
    consumer = [str(min(F(r['exact_bounds']['consumer_endpoint_min_v']) for r in rows)),
                str(max(F(r['exact_bounds']['consumer_endpoint_max_v']) for r in rows))]
    aux = dc_result['auxiliary_scope']
    pullup = aux['native_fault_pullup']
    nominal, tolerance = F(pullup['nominal_ohm']), F(pullup['initial_tolerance_fraction'])
    resistance = [str(nominal*(1-tolerance)), str(nominal*(1+tolerance))]
    result = []
    for group in aux['groups']:
        main = group['protected_voltage_v_exact']
        cases = [{'load_case': row['load_case'], **inverse_ron(
                    raw_average_min_v=envelope['raw_average_min_v'], ripple_pp_v=envelope['ripple_pp_v'],
                    distribution_drop_v=envelope['distribution_drop_v'], consumer_min_v=envelope['load_min_v'],
                    main_max_v=main[1], load_a=F(row['load_ma_exact'])/1000)} for row in rows]
        finite = [F(r['required_max_ron_ohm_exact']) for r in cases if r['required_max_ron_ohm_exact'] is not None]
        maximum = min(finite) if finite else None
        result.append({'divider_class': group['divider_class'], 'consumer_aon_hypothesis_v_exact': consumer,
            'main_protected_hypothesis_v_exact': deepcopy(main),
            'zero_added_aon_current_diagnostic': True, 'modeled_added_aon_current_a': '0',
            'actual_extra_aon_current_a': None, 'qualified': False,
            'screen': fault_bus.screen(main_v=main, aon_v=consumer, resistance_ohm=resistance,
                                      temperature_c=['-40', '85']),
            'ron_inverse_cases': cases, 'minimum_required_max_ron_ohm_exact': None if maximum is None else str(maximum),
            'witness_ids': [r['load_case'] for r in cases if r['required_max_ron_ohm_exact'] is not None and
                            F(r['required_max_ron_ohm_exact']) == maximum],
            'all_cases_allow_nonnegative_ron': all(r['feasible_nonnegative_ron'] for r in cases),
            'actual_ron_max_ohm': None, 'ron_source_condition_proven': False})
    return consumer, result


def assess_current(dc_result, source_hashes):
    """Attach two separate zero-added-load diagnostics without changing MAIN."""
    before = current.snapshot(source_paths())
    require(type(source_hashes) is dict and source_hashes, 'fresh parent source hashes required')
    native_paths = {str(p.relative_to(ROOT)) for p in current.source_paths()}
    require(native_paths <= set(source_hashes) and
            current.snapshot([ROOT/p for p in source_hashes]) == source_hashes,
            'parent current-source inventory/provenance missing or stale')
    original = topology.digest(dc_result)
    require(dc_result['status'] == 'not_qualified' and dc_result['qualified'] is False and
            dc_result['full_dc_cell_proven'] is False, 'parent DC result must retain open qualification')
    native = current.load_current()  # Replays H3 and startup reports in memory, never writes them.
    require(all(source_hashes.get(p) == value for p, value in native['source_sha256'].items()),
            'native sources changed during AON load')
    require(dc_result['auxiliary_scope'] == auxiliary.assess_current(dc_result, source_hashes=source_hashes),
            'parent auxiliary scope is missing/stale/altered')
    reviewed = load_reviewed()
    baseline = topology.load_baseline(source_hashes)
    binding = _bind_native(reviewed, baseline)
    contract = json.loads(h3.CONTRACT.read_text(), parse_float=Decimal)
    report = json.loads(h3.OUTPUT.read_text())  # Full equality to regeneration was checked by current.load_current.
    rail, path = contract['rails'][RAIL], contract['voltage_paths'][RAIL]
    require((path['raw_net'], path['protected_local_net'], path['distribution_scope'], path['qualified']) ==
            ('AON_RAW_3V3', RAIL, 'downstream_excludes_protection', False), 'AON voltage-node path differs')
    expected = {'nominal_v': '3.3', 'raw_average_min_v': '3.234', 'raw_average_max_v': '3.366',
                'ripple_pp_v': '.020', 'distribution_drop_v': '.025', 'efuse_ron_max_ohm': '.240',
                'load_min_v': '2.7', 'load_max_v': '3.6'}
    require(all(current.exact(rail[k]) == F(v) for k, v in expected.items()),
            'reviewed legacy AON requirements/diagnostic budgets changed')
    profiles = report['profiles']
    require(len(profiles) == 56, 'current AON electrical profile inventory differs')
    nominal = F(reviewed['buck']['regulation']['nominal_v'])
    conditioned = deepcopy(rail)
    conditioned['raw_average_min_v'] = current.decimal_text(nominal*(1+F(reviewed['buck']['regulation']['minimum_fraction'])))
    conditioned['raw_average_max_v'] = current.decimal_text(nominal*(1+F(reviewed['buck']['regulation']['maximum_fraction'])))
    conditioned_path = deepcopy(path)
    conditioned_path['unqualified_reasons'] += [
        'VSET regulation law is conditional; R47 TCR/startup decoding, VIN headroom, effective passives and thermal prerequisites remain unproved',
        'Zero added AON load is a diagnostic hypothesis, not a bound on the monitor or other auxiliaries']
    envelopes = {}
    for name, hypothesis, voltage_path in ((ENVELOPES[0], rail, path), (ENVELOPES[1], conditioned, conditioned_path)):
        rows = _profile_rows(hypothesis, voltage_path, profiles)
        if name == ENVELOPES[0]:
            observed = [{k: v for k, v in row.items() if k not in ('load_ma_exact', 'exact_bounds')} for row in rows]
            require(observed == [row for row in report['profile_voltage_corners'] if row['rail'] == RAIL],
                    'legacy AON projection differs from freshly validated H3 profile report')
        consumer, screens = _projected_faults(hypothesis, rows, dc_result)
        envelopes[name] = {'qualified': False, 'rail_hypothesis': {k: str(hypothesis[k]) for k in expected},
            'profiles': rows, 'consumer_envelope_v_exact': consumer, 'fault_bus_by_divider': screens,
            'raw_source': 'legacy H3 +/-2% hypothesis' if name == ENVELOPES[0] else 'conditional source VSET +/-1% law',
            'configuration_source_conditions_proven': False, 'native_current_inventory_qualified': False,
            'modeled_added_aon_current_a': '0', 'actual_extra_aon_current_a': None,
            'zero_added_load_diagnostic': True, 'actual_aon_voltage_v': None, 'actual_ron_max_ohm': None}
    portfolio = dc_result['candidate_topologies']
    require(portfolio['baseline_digest'] == baseline['baseline_digest'] and portfolio['qualified'] is False and
            portfolio['native_cad_changed'] is False, 'parent candidate/native baseline differs')
    aux = dc_result['auxiliary_scope']
    pullup = aux['native_fault_pullup']
    nominal, tolerance = F(pullup['nominal_ohm']), F(pullup['initial_tolerance_fraction'])
    resistance = [str(nominal*(1-tolerance)), str(nominal*(1+tolerance))]
    original_screens = {group['divider_class']: {
        label: fault_bus.screen(main_v=group['protected_voltage_v_exact'],
                                aon_v=aux['live_aon_hypothesis_v'],
                                resistance_ohm=resistance, temperature_c=temperature)
        for label, temperature in (
            ('common_source_temperature_hypothesis', ['-40', '85']),
            ('prior_temperature_hypothesis', aux['temperature_hypothesis_c']))}
        for group in aux['groups']}
    require(portfolio.get('fault_bus_screens') == original_screens,
            'original requirement fault screens missing or altered')
    expected_variants = {(g['divider_class'], r['rilm_class'], supply) for g in dc_result['groups']
                         for r in g['rilm_portfolios'] for supply in topology.SUPPLY_NODES}
    variants = []
    for candidate in portfolio['candidates']:
        key = tuple(candidate[k] for k in ('divider_class', 'rilm_class', 'monitor_supply_node'))
        require(key in expected_variants and candidate.get('fault_bus_screen_ref') == key[0] and
                candidate['status'] == 'nonproduction_topology_candidate' and
                candidate['qualified'] is False and candidate['validation']['checked'] is True and
                candidate['fault_bus_binding']['checked'] is True and candidate['fault_bus_binding']['candidate_sha256'] ==
                candidate['validation']['candidate_sha256'], 'missing/unbound parent topology variant')
        variants.append({k: candidate[k] for k in ('divider_class', 'rilm_class', 'monitor_supply_node')})
        variants[-1].update(candidate_sha256=candidate['validation']['candidate_sha256'],
            envelope_refs=[{'envelope': name, 'divider_class': key[0]} for name in ENVELOPES],
            monitor_on_aon=key[2] == RAIL, actual_extra_aon_current_a=None,
            modeled_added_aon_current_a='0', zero_added_load_diagnostic=True, qualified=False)
    require(len(expected_variants) == len(variants) == 18 and
            {tuple(r[k] for k in ('divider_class', 'rilm_class', 'monitor_supply_node')) for r in variants} == expected_variants,
            'missing/duplicate AON candidate variant coverage')
    result = {'schema_version': 1, 'status': 'conditional_aon_delivery_scope', 'qualified': False,
        'source_sha256': before, 'native_binding': binding, 'profile_count': len(profiles),
        'requirements': {k: str(rail[k]) for k in ('load_min_v', 'load_max_v')},
        'diagnostic_budgets': {k: str(rail[k]) for k in ('ripple_pp_v', 'efuse_ron_max_ohm', 'distribution_drop_v')},
        'envelopes': envelopes, 'candidate_variants': variants, 'sources': deepcopy(reviewed['sources']),
        'source_applicability': deepcopy(reviewed), 'actual_aon_voltage_v': None,
        'actual_extra_aon_current_a': None, 'actual_ron_max_ohm': None,
        'configuration_source_conditions_proven': False, 'native_current_inventory_qualified': False,
        'original_requirement_fault_screens_preserved': True, 'native_cad_changed': False,
        'limits': ['All 56 loads are existing H3 aggregate profiles, not a newly qualified executable sum of physical AON consumers',
            'RAW, protected-local and consumer nodes remain distinct; full 25mV consumer budget is conservative for same-RF-board U127, not a measured U14-to-U127 drop',
            'Ground offsets and return-path losses are not modeled',
            '20mVpp ripple, 0.240ohm RON and 25mV distribution are diagnostic assumptions, not fitted-condition source guarantees',
            'Fitted 240kohm RILIM has no admitted maximum RON or guaranteed current-limit interval',
            'Every projected screen assumes zero added AON current even for AON-powered monitor variants; actual auxiliary current remains unknown',
            'Inverse RON addresses the PA30 ceiling at zero fault-bus current and consumer minimum only, not complete HIGH/LOW, leakage, mode, off-state, startup or thermal qualification',
            'The original requirement-based AON fault screens are retained, not overwritten by these delivery hypotheses']}
    require(topology.digest(dc_result) == original, 'parent DC result mutated during AON assessment')
    require(current.snapshot(source_paths()) == before, 'sources changed during AON assessment')
    return result
