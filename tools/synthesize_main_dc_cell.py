#!/usr/bin/env python3
"""Known-divider-only necessary DC screen, never a complete DC cell approval.

Reuse selected static EDG pairs and the existing current inverse/forward/E192
machinery with a separate TPS259814 hypothesis. Unknown auxiliary currents,
source applicability and circuit-breaker dynamics remain unresolved.
"""
from copy import deepcopy
from fractions import Fraction as F
import json
from pathlib import Path
import signal
import tempfile
import time

import synthesize_main_static_pair as static
import compare_main_current_limit as current
import main_auxiliary_scope as auxiliary
from route_board import keep_awake

ROOT = static.ROOT
require = current.require
RILM_CLASSES = {'1pct_100ppm': ('.01', '100'), '0.1pct_10ppm': ('.001', '10'),
                '0.05pct_10ppm': ('.0005', '10')}
SOURCE_LAW = {
    'mpn_hypothesis': 'Texas Instruments TPS259814LRPWR',
    'url': 'https://www.ti.com/lit/ds/symlink/tps25981.pdf',
    'revision': 'SLVSGG6D, revised September 2026',
    'pdf_sha256': '8609249da4eb65da1d5398a4cbd5bc3ace4ca1f1f0205e41fbf3873d8e3f8e91',
    'pages': [1, 7, 8, 22], 'reviewed_on': '2026-09-20',
    'equation_constant_a_ohm': '6585', 'gain_tolerance_fraction': '0.10',
    'configured_domain': '6585/Rmax > 5 A, strict; separate from actual threshold interval',
    'header': 'TJ -40..125 C; VIN 12 V; OUT open; EN/UVLO 2 V; OVLO 0 V; RILM 611 ohm; dVdt/ITIMER/FLT/PG open',
    'unresolved': 'No actual ~3.3 V accuracy admission; printed 1102 kohm row is not corrected/interpolated; circuit-breaker threshold with ITIMER blanking is not a clamp or converter dynamic protection',
    'iq_on_row': {'minimum_a': None, 'typical_a': '.000417', 'maximum_a': '.000610',
                  'page': 7, 'conditions': 'VIN=12 V table header; not an actual ~3.3 V bound',
                  'application_bound_established': False},
    'source_applicability': False}
UNRESOLVED_BRANCHES = [
    {'id': name, 'supply_node': 'raw_converter_output' if name == 'replacement_efuse_iq' else None,
     'current_max_a': None, 'bound_established': False}
    for name in ('monitor_vdd', 'monitor_reset_pullup', 'replacement_efuse_iq', 'other_new_auxiliaries')]


def exact(value):
    require(type(value) in (str, int, F), 'exact finite rational value required')
    return F(value)


def current_requirements(native, selected):
    """FB bypasses protection; monitor current is downstream of protection."""
    demands = {name: exact(value) for name, value in native['requirements_a'].items()}
    require(set(demands) == {'h0_step_a', 'pf03_reserve_a', 'existing_inrush_a'} and
            demands['h0_step_a'] >= F('4.25') and min(demands.values()) > 0 and
            exact(native['required_lower_a']) == max(demands.values()) and exact(native['strict_upper_a']) == 6,
            'native current demands missing/weakened or upper is not 6 A continuous')
    loaded = selected['loaded_diagnostic']
    require(selected['qualified'] is False and loaded['qualified'] is False and
            loaded['source_applicability'] is False and loaded['status'] == 'conditional_static_pass' and
            loaded['checked_load_cases'] == 58 and len(loaded['cases']) == 58,
            'a complete conditional selected static pair is required')
    branch = loaded['branch_current_a_exact']
    values = {key: tuple(map(exact, branch[key]))
              for key in ('monitor_top_current_a', 'feedback_top_current_a')}
    require(all(len(bounds) == 2 and 0 <= bounds[0] <= bounds[1] for bounds in values.values()),
            'nonnegative ordered known branch bounds required')
    monitor, feedback = (values[key][1] for key in ('monitor_top_current_a', 'feedback_top_current_a'))
    protected = {'h0_step_a': demands['h0_step_a']+monitor,
                 'pf03_reserve_a': demands['pf03_reserve_a']+F('1.25')*monitor,
                 'existing_inrush_dc_proxy_a': demands['existing_inrush_a']+monitor}
    require(6-feedback > 0, 'feedback branch consumes entire converter current ceiling')
    return {'native_requirements_a': {key: str(value) for key, value in demands.items()},
            'protected_demands_a': {key: str(value) for key, value in protected.items()},
            'required_lower_a': str(max(protected.values())), 'strict_upper_a': str(6-feedback),
            'monitor_branch_max_a': str(monitor), 'feedback_branch_max_a': str(feedback),
            'scope': 'Full candidate branches added without subtracting native allowances; old inrush is a DC proxy only',
            'unknown_auxiliary_currents_included': False}


def candidate_spec(kind):
    require(kind in RILM_CLASSES, 'undeclared independent RILM class')
    tolerance, tcr = RILM_CLASSES[kind]
    return {'equation_constant_a_ohm': '6585', 'gain_tolerance_fraction': '0.10',
            'configured_accuracy_domain_min_a_exclusive': '5',
            'initial_tolerance_fraction': tolerance, 'tcr_ppm_per_c': tcr,
            'temperature_c': ['-40', '125'], 'reference_temperature_c': '25'}


def validate_candidate_spec(spec):
    require(exact(spec['equation_constant_a_ohm']) == 6585 and exact(spec['gain_tolerance_fraction']) == F('.1') and
            exact(spec['configured_accuracy_domain_min_a_exclusive']) == 5,
            'wrong candidate-specific TPS259814 law or strict accuracy domain')
    require(spec['temperature_c'] == ['-40', '125'] and spec['reference_temperature_c'] == '25',
            'resistor temperature hypothesis changed')


def threshold_portfolio(requirements, kind, table):
    """Complete existing E192 enumeration with mixed open/closed upper bounds."""
    spec = candidate_spec(kind)
    validate_candidate_spec(spec)
    require(list(current.BUDGETS) == ['initial_plus_tcr', 'additional_solder_and_load_life_diagnostic'] and
            not current.BUDGETS['initial_plus_tcr'] and
            [(b.name, F(b.fraction), F(b.absolute_ohm)) for b in current.BUDGETS['additional_solder_and_load_life_diagnostic']]
            == [('solder', F('.01'), F('.05')), ('load_life', F('.01'), F('.05'))],
            'both original ordered RILM diagnostic budgets required')
    required, ceiling = exact(requirements['required_lower_a']), exact(requirements['strict_upper_a'])
    monitor, feedback = exact(requirements['monitor_branch_max_a']), exact(requirements['feedback_branch_max_a'])
    native = {key: exact(value) for key, value in requirements['native_requirements_a'].items()}
    expected = {'h0_step_a': native['h0_step_a']+monitor,
                'pf03_reserve_a': native['pf03_reserve_a']+F('1.25')*monitor,
                'existing_inrush_dc_proxy_a': native['existing_inrush_a']+monitor}
    require(native['h0_step_a'] >= F('4.25') and min(native.values()) > 0 and monitor >= 0 and feedback >= 0 and
            required == max(expected.values()) and ceiling == 6-feedback and
            requirements['protected_demands_a'] == {key: str(value) for key, value in expected.items()},
            'weakened or inconsistent protected/raw current demands')
    windows = {name: current.inverse(required, ceiling, spec, budget) for name, budget in current.BUDGETS.items()}
    domain_high = {name: current.inverse(F(5)*F('.9'), ceiling, spec, budget).maximum_ohm
                   for name, budget in current.BUDGETS.items()}
    low = max(window.minimum_ohm for window in windows.values())
    load_high = min(window.maximum_ohm for window in windows.values())
    strict_high = min(domain_high.values())
    high = min(load_high, strict_high)
    decades, nominals = current.finite_nominals(low, high, table)
    nominals = [value for value in nominals if value < strict_high]
    candidates = []
    for nominal in nominals:
        checks = []
        for name, budget in current.BUDGETS.items():
            check = current.forward(nominal, spec, budget, required, ceiling)
            configured = F(6585)/F(check['resistance_ohm'][1])
            require(configured > 5 and check['numerical_constraints_met'], 'candidate failed exact configured/threshold forward checks')
            checks.append({'budget': name, 'configured_min_a_exact': str(configured), **check})
        score = min(F(check[key]) for check in checks for key in ('lower_margin_a_exact', 'strict_upper_margin_a_exact'))
        candidates.append({'nominal_ohm': str(nominal), 'minimum_margin_a_exact': str(score), 'checks': checks, 'qualified': False})
    best = max(candidates, key=lambda row: (F(row['minimum_margin_a_exact']), -F(row['nominal_ohm']))) if candidates else None
    return {'status': 'conditional_known_divider_candidate' if best else 'no_candidate_in_declared_finite_domain',
            'qualified': False, 'source_applicability': False, 'rilm_class': kind, 'spec': spec,
            'requirements': deepcopy(requirements), 'budgets': list(current.BUDGETS),
            'budget_windows': {name: {'load_window_ohm_exact': [str(window.minimum_ohm), str(window.maximum_ohm)],
                                      'minimum_exclusive': True, 'load_maximum_inclusive': True,
                                      'configured_maximum_ohm_exclusive': str(domain_high[name])}
                               for name, window in windows.items()},
            'domain': {'nominal_ohm_exact': [str(low), str(high)], 'minimum_exclusive': True,
                       'maximum_inclusive': load_high < strict_high, 'decade_exponents': decades,
                       'mantissa_count': len(table)},
            'candidate_count': len(candidates), 'candidates': candidates,
            'selected_nominal_ohm': best['nominal_ohm'] if best else None,
            'minimum_margin_a_exact': best['minimum_margin_a_exact'] if best else None,
            'objective': 'Maximize minimum exact lower/strict-upper threshold margin across both budgets; ties choose lower nominal'}


def combine(static_report, native, table):
    require(static_report['qualified'] is False and static_report['status'] == 'not_qualified',
            'upstream static scope must remain unqualified')
    groups = []
    for group in static_report['portfolio']['groups']:
        index = group['selected_window_index']
        if index is None:
            continue
        require(type(index) is int and 0 <= index < len(group['trials']), 'invalid selected static index')
        selected = group['trials'][index]
        requirements = current_requirements(native, selected)
        groups.append({'monitor': group['monitor'], 'divider_class': group['resistor_class'],
                       'selected_window_index': index, 'selected_static_pair': deepcopy(selected),
                       'requirements': requirements, 'qualified': False,
                       'rilm_portfolios': [threshold_portfolio(requirements, kind, table) for kind in RILM_CLASSES]})
    return {'status': 'not_qualified', 'qualified': False, 'full_dc_cell_proven': False,
            'divider_lifetime_covered': False, 'model_decisions_inside_command': 0,
            'source_applicability': False, 'startup_proven': False, 'dynamic_protection_proven': False,
            'production_mpn_selected': False, 'scope': 'Known-divider-only necessary DC screen; unknown auxiliary currents are NOT zero',
            'source_law': deepcopy(SOURCE_LAW), 'unresolved_branches': deepcopy(UNRESOLVED_BRANCHES),
            'baseline_power_review': deepcopy(native['baseline_power_review']),
            'upstream_static_report': deepcopy(static_report), 'groups': groups,
            'limitations': ['RON projected beyond its reviewed 3 A test point; voltage and current source applicability remain open',
                            'RILM classes are independent hypotheses, not divider classes or selected components',
                            'Both original RILM stress budgets retained; FB/monitor still initial+TCR only, not combined cell lifetime coverage',
                            'Threshold <6 A minus FB branch is only a steady DC necessary ceiling, not instantaneous protection',
                            'Auxiliary supply/return nodes, monitor VDD/pullup and replacement eFuse IQ bounds must be bound before full-cell claims',
                            'No simultaneous auxiliary headroom, startup, ITIMER, fast-trip, thermal, layout or physical proof']}


def validate_combination(static_report, native, table, result):
    require(json.dumps(result, sort_keys=True, allow_nan=False) ==
            json.dumps(combine(static_report, native, table), sort_keys=True, allow_nan=False),
            'DC screen membership, selection, demands, findings or unresolved authority differs from replay')


def source_paths():
    return sorted(set(current.source_paths()) | set(auxiliary.source_paths()) | {
        Path(__file__), Path(static.__file__), Path(static.compare.__file__),
        static.monitor_source.ROWS_PATH, Path(static.monitor_source.__file__),
        static.ron_source.ROWS_PATH, Path(static.ron_source.__file__),
        ROOT/'hardware/verification/h3_r2_current_scope.py'})


def run():
    started = time.monotonic()
    before = current.snapshot(source_paths())
    static_report, native = static.run(), current.load_current()
    for hashes in (static_report['source_sha256'], native['source_sha256']):
        require(set(hashes) <= set(before) and hashes == {path: before[path] for path in hashes},
                'upstream source inventory or starting hashes differ')
    table = current.load_edg_table()
    result = combine(static_report, native, table)
    validate_combination(static_report, native, table, result)
    result['auxiliary_scope'] = auxiliary.assess_current(result, source_hashes=before)
    require(current.load_edg_table() == table, 'installed EDG runtime/table changed')
    require(current.snapshot(source_paths()) == before, 'sources changed during DC screen')
    return {**result, 'schema_version': 1, 'source_sha256': before,
            'selector': {'name': 'existing pinned EDG E192 complete finite enumeration',
                         'version': static.pair.EDG_VERSION, 'source_sha256': dict(static.pair.EDG_SOURCE_SHA256)},
            'elapsed_s': round(time.monotonic()-started, 6)}


def main():
    try:
        started = time.monotonic()
        def interrupted(*_):
            raise KeyboardInterrupt('DC screen cancelled')
        signal.signal(signal.SIGTERM, interrupted)
        work = ROOT/'work'
        work.mkdir(exist_ok=True)
        require(not work.is_symlink() and work.resolve() == work, 'unsafe work directory')
        directory = Path(tempfile.mkdtemp(prefix='main-dc-cell-', dir=work))
        awake = {}
        with keep_awake(awake, directory):
            result = run()
        require(current.snapshot(source_paths()) == result['source_sha256'], 'sources changed before publication')
        static.pair._load_edg()
        result['caffeinate'] = awake
        result['command_elapsed_s'] = round(time.monotonic()-started, 6)
        path = directory/'result.json'
        with path.open('x') as stream:
            stream.write(json.dumps(result, indent=2, allow_nan=False)+'\n')
        require(json.loads(path.read_text()) == result, 'persisted report differs')
        print(json.dumps({'status': result['status'], 'qualified': False, 'report': str(path),
                          'elapsed_s': result['elapsed_s'], 'selected': [
                              [group['divider_class'], [[p['rilm_class'], p['selected_nominal_ohm']] for p in group['rilm_portfolios']]]
                              for group in result['groups']]}))
        return 1
    except (Exception, KeyboardInterrupt) as error:
        print(json.dumps({'status': 'execution_error', 'qualified': False, 'error': str(error), 'report': None}))
        return 130 if isinstance(error, KeyboardInterrupt) else 2


if __name__ == '__main__':
    raise SystemExit(main())
