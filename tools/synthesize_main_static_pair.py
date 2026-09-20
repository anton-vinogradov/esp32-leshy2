#!/usr/bin/env python3
"""Conditional coupled MAIN feedback/monitor divider selection, never cell approval.

Run in the prepared EDG0.5.2 environment. Native voltage/load/ripple demands
are immutable; distribution defaults to the current source value. Changed
resistor classes, RON and monitor circuitry are explicit hypotheses, not MPN
adoption. The RON hypothesis is NOT combined with the old eFuse current law.
"""
import argparse
from copy import deepcopy
from decimal import Decimal, localcontext
from fractions import Fraction as F
from itertools import product
import json
import math
from pathlib import Path
import signal
import tempfile
import time

import synthesize_main_feedback as source
import compare_main_feedback as compare
import edg_feedback_pair as pair
import compare_main_current_limit as preferred_numbers
from h6_power_corner_math import Interval, resistor_interval, _decimal
import h6_main_monitor_window as monitor_source
import h6_ron_source_scope as ron_source
from route_board import keep_awake

ROOT = source.ROOT
RON = F('0.0084')
CLASSES = {'0.1pct_10ppm': '.001', '0.05pct_10ppm': '.0005'}
RESERVES = tuple(map(F, ('.000001', '.00001', '.00005', '.0001', '.0002', '.0005', '.001', '.002', '.003')))
SENSE_DIAGNOSTIC_A = {'tps389001': '.0000001', 'tps3703a7330': '.0000015'}
FB_IMPEDANCE_WINDOWS = ((F(5000), F(10000)), (F(500), F(1000)), (F(50), F(100)))
PORTFOLIO_POLICY = 'First passing EDG-proposed pair in fixed highest-to-lowest feedback impedance windows; no exhaustive within-window search, global optimum or MPN selection'


def decimal(value):
    value = F(value)
    with localcontext() as context:
        context.prec = 70
        return Decimal(value.numerator) / Decimal(value.denominator)


def interval(low, high):
    # Only a search request is rounded. Final acceptance uses exact Fractions.
    return Interval(decimal(low), decimal(high))


def monitor_hypotheses():
    reviewed = next(row for row in monitor_source.load_reviewed_rows() if row['id'] == 'candidate_tps389001')
    return [
        {'id': 'tps389001', 'falling': F(reviewed['falling_min_v']),
         'rising': F(reviewed['rising_max_v']), 'impedance': (F(5000), F(10000)), 'source': reviewed},
        {'id': 'tps3703a7330', 'falling': F('3.069') * F('.993'),
         'rising': F('3.069') * F('1.007') * F('1.008'),
         'ov_falling': F('3.531') * F('.993') * F('.992'),
         'impedance': (F(10), F(100)),
         'source': {'device': 'TPS3703A7330DSER hypothesis, not selected/adopted',
                    'url': 'https://www.ti.com/lit/ds/symlink/tps3703.pdf',
                    'revision': 'SBVS249B', 'pages': [3, 6, 7, 28],
                    'pdf_sha256': 'cc65714774e50c97dca9a1bf094489b17350cc70fa16068880e108e320f8a6ea',
                    'reviewed_on': '2026-09-20',
                    'derivation': '3.3 V nominal; UV=-7%, OV=+7%; threshold +/-0.7%; max hysteresis 0.8% of trip point',
                    'header_conditions': 'VDD 1.7..5.5 V; TA -40..125 C; CT/MR open; RESET 10 kohm/10 pF',
                    'input_current': '1.5 uA maximum at VSENSE=5 V only; not a bound at application ~3.1 V; zero used diagnostically',
                    'scope': 'Reviewed diagnostic transcription; VDD/SENSE loading, leakage, exact assembly supply and circuit unqualified',
                    'timing': '30 us maximum only at 5% overdrive and 10 kohm/10 pF output loading to VOL; not arbitrary sag/system response'}}]


def select_pair(reference, required, top, bottom, impedance, leakage, *, series=192):
    """Reuse stock EDG; if needed change only its target's initial decades.

    Stock equal-decade seeding cannot reach some near-unity transfers because
    adjacent nonintersecting decades are pruned. Inverse center seeding fixes
    that bounded search issue without replacing EDG's E-series enumeration.
    No-match still does not prove discrete infeasibility or global optimality.
    """
    result = pair.synthesize_pair(reference, required, top, bottom, impedance, leakage, series=series)
    if result['status'] != 'preferred_selector_found_no_candidate':
        return result
    Calculator, Series, Range, Values = pair._load_edg()
    ratio = tuple(map(F, result['required_ratio_exact']))
    z = (F(impedance.minimum), F(impedance.maximum))
    q = float((ratio[0] + min(F(1), ratio[1])) / 2)
    if not 0 < q < 1:
        return result
    center = float(sum(z) / 2)
    seed = (math.floor(math.log10(center / q)), math.floor(math.log10(center / (1-q))))
    if any(not -15 < exponent < 15 for exponent in seed):
        raise ValueError('EDG seed outside its bounded decade domain')

    class Target(Values):
        def initial_test_decades(self):
            return seed

    tolerance = F(result['common_symmetric_tolerance_fraction_exact'])
    floating = float(tolerance)
    if F(floating) < tolerance:
        floating = math.nextafter(floating, math.inf)
    calculator = Calculator(Series.SERIES[series], floating, Values)
    result['selector']['initial_decade_retry'] = list(seed)
    try:
        values = calculator.find(Target(pair._search_range(ratio, Range), pair._search_range(z, Range)))
    except Calculator.NoMatchException:
        return result
    if not isinstance(values, tuple) or len(values) != 2 or any(
            type(v) not in (int, float) or not math.isfinite(v) or v <= 0 for v in values):
        raise ValueError('EDG returned invalid resistor nominals')
    rt, rb = (F(str(value)) for value in values)
    checked = pair.verify_candidate(rt, rb, reference, required, top, bottom, impedance)
    return dict(result, status='conditional_candidate',
                selected_nominal_ohm_exact={'top': str(rt), 'bottom': str(rb)}, **checked)


def checked_corners(selection, reference, required, factors, impedance):
    """Recompute from actual nominals; do not trust a returned corner summary."""
    nominals = selection['selected_nominal_ohm_exact']
    checked = pair.verify_candidate(F(nominals['top']), F(nominals['bottom']), reference,
                                    required, factors, factors, impedance)
    if any(selection[key] != value for key, value in checked.items()):
        raise ValueError('Selected pair corner summary differs from independent recomputation')
    return tuple(map(F, checked['average_v_exact']))


def loaded_point(vref, rf_top, rf_bottom, i_fb, rm_top, rm_bottom, i_sense,
                 load, ron, raw_ripple_v=F(0)):
    """One exact DC/KCL point; positive bias flows into each IC input.

    Feedback is upstream of the eFuse; only monitor top-branch current joins
    the protected load. Ripple shifts the FB node and branch current too.
    Signed algebraic results are preserved, never clamped into physicality.
    """
    values = (vref, rf_top, rf_bottom, i_fb, rm_top, rm_bottom, i_sense, load, ron, raw_ripple_v)
    if any(not isinstance(value, F) for value in values):
        raise ValueError('Exact Fraction circuit inputs required')
    if min(vref, rf_top, rf_bottom, rm_top, rm_bottom) <= 0 or min(load, ron) < 0:
        raise ValueError('Positive reference/resistors and nonnegative load/RON required')
    raw = vref*(1+rf_top/rf_bottom) + i_fb*rf_top + raw_ripple_v
    total = rm_top+rm_bottom
    local = ((raw-ron*load)*total - ron*i_sense*rm_bottom) / (total+ron)
    sense = rm_bottom*(local-i_sense*rm_top)/total
    monitor_current = (local+i_sense*rm_bottom)/total
    feedback_current = vref/rf_bottom+i_fb+raw_ripple_v/(rf_top+rf_bottom)
    efuse_current = load+monitor_current
    return {'raw_v': raw, 'local_v': local, 'sense_v': sense,
            'feedback_top_current_a': feedback_current, 'monitor_top_current_a': monitor_current,
            'efuse_current_a': efuse_current, 'converter_current_a': efuse_current+feedback_current}


def loaded_diagnostic(data, row, monitor, fb_bias, sense_bias):
    """Post-check existing EDG nominals; never synthesize from missing bounds.

    All native load envelopes remain intact; full new branch currents are
    conservatively added. Existing member allowances may therefore be counted
    twice. This diagnostic does not prove replacement current admission.
    """
    result = {'qualified': False, 'source_applicability': False,
              'actual_source_bias_bounds_a': {'feedback': None, 'sense': None},
              'load_accounting': '58 native envelopes unchanged + full candidate branches; possible double counting, no allowance subtracted',
              'excluded_loads': 'Monitor VDD/output pull-up, converter input IQ and other replacement auxiliaries remain unknown',
              'bias_basis': 'Signed hypotheses only: FB has no reviewed input-bias row; SENSE max is one-sided at 5 V, not an application signed bound'}
    primary = monitor['source'].get('source', monitor['source'])
    result['reviewed_bias_sources'] = {
        'feedback': {'url': 'https://www.ti.com/lit/ds/symlink/tps566231.pdf', 'revision': 'SLUSDQ7B',
                     'pdf_sha256': '59b851cec004a536641b4b360b7f9fd42580cfc817639592c1d1e032fbf5ab76',
                     'pages': [5, 6], 'reviewed_on': '2026-09-20', 'input_bias_row': None,
                     'conditions': 'No FB input-bias row published; VFB table VIN=12 V, TJ=-40..125 C'},
        'sense': {**{key: primary[key] for key in ('url', 'revision', 'pdf_sha256')},
                  'page': 5 if monitor['id'] == 'tps389001' else 6, 'reviewed_on': '2026-09-20',
                  'minimum_a': None, 'typical_a': '.00000001' if monitor['id'] == 'tps389001' else '.000001',
                  'maximum_a': '.0000001' if monitor['id'] == 'tps389001' else '.0000015', 'test_vsense_v': '5',
                  'application_signed_bound_established': False}}
    if fb_bias is None or sense_bias is None:
        return dict(result, status='not_evaluated_unknown_bias')
    if not isinstance(fb_bias, Interval) or not isinstance(sense_bias, Interval):
        raise ValueError('Explicit signed bias intervals or unknown None required')
    result['hypothetical_bias_a_exact'] = {
        name: [str(F(value.minimum)), str(F(value.maximum))]
        for name, value in (('feedback', fb_bias), ('sense', sense_bias))}
    if row['status'] != 'conditional_joint_candidate':
        return dict(result, status='not_evaluated_no_selected_pair')
    demand = compare.demands(data)
    ripple = F(demand['ripple_half_v'])
    if ripple >= F(data['reference'].minimum):
        raise ValueError('Ripple outside reviewed corner-current monotonicity domain')
    factors = tuple(map(F, row['factor_interval_exact']))
    rf = [F(row['feedback']['selected_nominal_ohm_exact'][name]) for name in ('top', 'bottom')]
    rm = [F(row['monitor_pair']['selected_nominal_ohm_exact'][name]) for name in ('top', 'bottom')]
    distribution = F(row['distribution_drop_v_exact'])
    endpoints = lambda value: tuple(dict.fromkeys((F(value.minimum), F(value.maximum))))
    corners = list(product(endpoints(data['reference']), *(tuple(r*f for f in factors) for r in rf),
                           endpoints(fb_bias), *(tuple(r*f for f in factors) for r in rm),
                           endpoints(sense_bias), (-ripple, ripple)))
    cases, all_points = [], []
    for name, load in demand['cases']:
        points = [loaded_point(*corner[:7], load, RON, corner[7]) for corner in corners]
        all_points.extend(points)
        bounds = {key: [str(min(p[key] for p in points)), str(max(p[key] for p in points))]
                  for key in ('local_v', 'sense_v', 'efuse_current_a', 'converter_current_a')}
        cases.append({'name': name, 'native_load_a_exact': str(load), 'bounds_exact': bounds})
    factor_interval = interval(*factors)
    fb_voltage = source.forward(rf[0], data['reference'], interval(rf[1]*factors[0], rf[1]*factors[1]),
                                factor_interval, fb_bias)
    raw = (fb_voltage[0]-ripple, fb_voltage[1]+ripple)
    if raw != (min(p['raw_v'] for p in all_points), max(p['raw_v'] for p in all_points)):
        raise ValueError('Loaded KCL raw envelope differs from existing exact divider forward check')
    monitor_threshold = lambda v: source.forward(rm[0], interval(v, v),
        interval(rm[1]*factors[0], rm[1]*factors[1]), factor_interval, sense_bias)
    falling = monitor_threshold(monitor['falling'])[0]
    margins = {'consumer_lower': min(p['local_v'] for p in all_points)-distribution-F(demand['consumer_min_v']),
               'raw_lower': raw[0]-F(demand['raw_min_v']),
               'raw_upper': F(demand['consumer_max_v'])-raw[1],
               'monitor_falling': falling-distribution-F(demand['consumer_min_v']),
               'monitor_rising_sense': min(p['sense_v'] for p in all_points)-monitor['rising']}
    if 'ov_falling' in monitor:
        # Conservative no-load upper envelope: no guaranteed eFuse drop credit.
        margins['monitor_ov_release'] = monitor_threshold(monitor['ov_falling'])[0]-raw[1]
    physical = all(min(p[key] for key in ('raw_v', 'local_v', 'sense_v')) > 0 and
                   min(p[key] for key in ('feedback_top_current_a', 'monitor_top_current_a',
                                         'efuse_current_a', 'converter_current_a')) >= 0 for p in all_points)
    failures = [key for key, margin in margins.items() if margin <= 0]
    if not physical:
        failures.append('unsupported_reverse_current_or_nonpositive_voltage')
    return dict(result, status='conditional_static_pass' if not failures else 'conditional_static_fail',
                checked_load_cases=len(cases), corners_per_case=len(corners), cases=cases,
                physical_operating_domain=physical, failed_checks=failures,
                headroom_v_exact={key: str(value) for key, value in margins.items()},
                raw_v_exact=list(map(str, raw)),
                branch_current_a_exact={key: [str(min(p[key] for p in all_points)), str(max(p[key] for p in all_points))]
                                       for key in ('feedback_top_current_a', 'monitor_top_current_a')})


def synthesize(data, resistor_class, distribution, monitor, solver=select_pair, *,
               fb_impedance_ohm=FB_IMPEDANCE_WINDOWS[0]):
    if resistor_class not in CLASSES or not isinstance(distribution, F) or distribution < 0:
        raise ValueError('Explicit supported resistor class and nonnegative exact distribution required')
    if (type(fb_impedance_ohm) is not tuple or len(fb_impedance_ohm) != 2 or
            any(type(value) is not F for value in fb_impedance_ohm) or
            not 0 < fb_impedance_ohm[0] <= fb_impedance_ohm[1]):
        raise ValueError('Explicit positive ordered exact feedback impedance window required')
    demand = compare.demands(data)
    current = max(i for _, i in demand['cases'])
    ripple = F(demand['ripple_half_v'])
    floor = F(demand['consumer_min_v']) + distribution
    upper = F(demand['consumer_max_v']) - ripple
    factors = resistor_interval('1', CLASSES[resistor_class], '10', '-40', '125', reference_temperature_c='25')
    qlo = F(factors.minimum) / F(factors.maximum)
    qhi = 1 / qlo
    reflo, refhi = F(data['reference'].minimum), F(data['reference'].maximum)
    falling, rising = monitor['falling'], monitor['rising']
    if falling <= 0 or rising < falling:
        raise ValueError('Invalid monitor threshold bounds')
    best_feedback_low = reflo * (1 + (upper/refhi-1) * qlo/qhi)
    best_local = best_feedback_low - ripple - current * RON
    min_monitor_ratio = max(F(0), (floor/falling-1) / qlo)
    least_rising = rising * (1 + min_monitor_ratio*qhi)
    continuous_margin = best_local - least_rising
    result = {'resistor_class': resistor_class, 'monitor': monitor['id'], 'qualified': False,
              'distribution_drop_v_exact': str(distribution),
              'continuous_joint_margin_v_exact': str(continuous_margin),
              'factor_interval_exact': [str(F(factors.minimum)), str(F(factors.maximum))],
              'fb_impedance_ohm_exact': list(map(str, fb_impedance_ohm)),
              'monitor_source': monitor['source'], 'monitor_impedance_ohm_exact': list(map(str, monitor['impedance']))}
    if continuous_margin <= 0:
        return dict(result, status='continuous_joint_infeasible')
    attempts = []
    for reserve in RESERVES:
        ratio_min = max(F(0), ((floor+reserve)/falling-1) / qlo)
        required_min = max(F(demand['raw_min_v']) + ripple + reserve,
                           floor + ripple + current*RON + reserve,
                           rising*(1+ratio_min*qhi) + ripple + current*RON + reserve)
        maximum = upper - reserve
        if required_min > maximum:
            continue
        fb_required, fb_impedance = interval(required_min, maximum), interval(*fb_impedance_ohm)
        feedback = solver(data['reference'], fb_required, factors, factors, fb_impedance, interval(0, 0))
        attempt = {'reserve_v_exact': str(reserve), 'feedback_status': feedback['status']}
        attempts.append(attempt)
        if feedback['status'] != 'conditional_candidate':
            continue
        fb_low, fb_high = checked_corners(feedback, data['reference'], fb_required, factors, fb_impedance)
        local_min = fb_low - ripple - current*RON
        mon_reference, mon_required = interval(falling, rising), interval(floor+reserve, local_min-reserve)
        mon_impedance = interval(*monitor['impedance'])
        monitor_pair = solver(mon_reference, mon_required, factors, factors, mon_impedance, interval(0, 0))
        attempt['monitor_status'] = monitor_pair['status']
        if monitor_pair['status'] != 'conditional_candidate':
            continue
        fall_min, rise_max = checked_corners(monitor_pair, mon_reference, mon_required, factors, mon_impedance)
        consumer = compare.check_consumers(feedback['average_v_exact'], demand, decimal(RON), decimal(distribution))
        margins = {'consumer_lower': F(consumer['lower_margin_v_exact']),
                   'raw_upper': F(consumer['upper_raw_margin_v_exact']),
                   'raw_lower': fb_low-ripple-F(demand['raw_min_v']),
                   'monitor_falling': fall_min-floor, 'monitor_rising': local_min-rise_max}
        rt, rb = (F(monitor_pair['selected_nominal_ohm_exact'][name]) for name in ('top', 'bottom'))
        if 'ov_falling' in monitor:
            margins['monitor_ov_false_fault'] = monitor['ov_falling']*(1+rt/rb*qlo) - (fb_high+ripple)
        if any(margin < reserve or margin <= 0 for margin in margins.values()):
            raise ValueError('Selected pair failed strict exact joint headroom checks')
        divider_load = F(demand['consumer_max_v']) / ((rt+rb)*F(factors.minimum))
        return dict(result, status='conditional_joint_candidate', reserve_v_exact=str(reserve),
                    feedback=feedback, monitor_pair=monitor_pair, consumer_check=consumer,
                    protected_local_min_v_exact=str(local_min),
                    headroom_v_exact={key: str(value) for key, value in margins.items()},
                    monitor_divider_load_upper_a_exact=str(divider_load),
                    divider_load_admitted_to_current_budget=False, attempts=attempts)
    return dict(result, status='bounded_edg_search_no_pair', attempts=attempts)


def trial(data, kind, distribution, monitor, window):
    row = synthesize(data, kind, distribution, monitor, fb_impedance_ohm=window)
    sense_magnitude = Decimal(SENSE_DIAGNOSTIC_A[monitor['id']])
    row['ideal_status'] = row['status']
    row['loaded_diagnostic'] = loaded_diagnostic(
        data, row, monitor, Interval('-.000001', '.000001'), Interval(-sense_magnitude, sense_magnitude))
    row['loaded_diagnostic_status'] = row['loaded_diagnostic']['status']
    return row


def portfolio(data, monitors, distribution, baseline_rows=None):
    """Fixed finite search policy; EDG remains the only nominal selector."""
    if monitors != monitor_hypotheses():
        raise ValueError('Portfolio must use both unchanged declared monitor hypotheses')
    if baseline_rows is not None and len(baseline_rows) != len(monitors)*len(CLASSES):
        raise ValueError('Incomplete baseline portfolio rows')
    groups = []
    for monitor in monitors:
        for kind in CLASSES:
            trials = [deepcopy(baseline_rows[len(groups)]) if index == 0 and baseline_rows is not None
                      else trial(data, kind, distribution, monitor, window)
                      for index, window in enumerate(FB_IMPEDANCE_WINDOWS)]
            selected = next((index for index, row in enumerate(trials)
                             if row['loaded_diagnostic_status'] == 'conditional_static_pass'), None)
            groups.append({'monitor': monitor['id'], 'resistor_class': kind, 'qualified': False,
                           'trials': trials, 'selected_window_index': selected})
    return {'qualified': False, 'selection_policy': PORTFOLIO_POLICY,
            'windows_ohm_exact': [list(map(str, window)) for window in FB_IMPEDANCE_WINDOWS],
            'trial_count': sum(len(group['trials']) for group in groups), 'groups': groups,
            'invariant_demands': {key: str(value) for key, value in compare.demands(data).items() if key != 'cases'},
            'load_cases_a_exact': [[name, str(current)] for name, current in data['cases']],
            'reference_v_exact': [str(F(data['reference'].minimum)), str(F(data['reference'].maximum))],
            'distribution_drop_v_exact': str(distribution), 'projected_ron_ohm_exact': str(RON),
            'bias_budgets_a_exact': {'feedback': ['-1/1000000', '1/1000000'],
                                     'sense': {name: [str(-F(value)), str(F(value))]
                                               for name, value in SENSE_DIAGNOSTIC_A.items()}},
            'resistor_class_tolerance_fraction': dict(CLASSES)}


def verify_portfolio(data, monitors, distribution, result):
    """Replay is reproducibility, not a second independent selection solver.

    Every replayed candidate invokes existing independent exact forward and
    loaded KCL checks. Separately require membership in the pinned EDG E192
    table, so a physically valid continuous nominal cannot masquerade as E192.
    """
    if (result.get('windows_ohm_exact') != [list(map(str, window)) for window in FB_IMPEDANCE_WINDOWS] or
            type(result.get('trial_count')) is not int or result['trial_count'] != 12 or
            len(result.get('groups', [])) != 4 or any(len(group.get('trials', [])) != 3 for group in result['groups'])):
        raise ValueError('Incomplete or reordered fixed portfolio domain')
    table = preferred_numbers.load_edg_table()
    for group in result['groups']:
        for row in group['trials']:
            if row['ideal_status'] == 'conditional_joint_candidate':
                for divider in ('feedback', 'monitor_pair'):
                    for nominal in row[divider]['selected_nominal_ohm_exact'].values():
                        if type(nominal) is not str or F(nominal) <= 0:
                            raise ValueError('Explicit positive exact nominal string required')
                        value = F(nominal)
                        if value not in preferred_numbers.finite_nominals(value/10, value, table)[1]:
                            raise ValueError('Portfolio nominal is not a pinned E192 member')
    expected = portfolio(data, monitors, distribution)
    if json.dumps(result, sort_keys=True, allow_nan=False) != json.dumps(expected, sort_keys=True, allow_nan=False):
        raise ValueError('Portfolio differs from full replay: demands, budgets, trials or first passing selection changed')
    if preferred_numbers.load_edg_table() != table:
        raise ValueError('Pinned E192 table changed during portfolio validation')
    return {'qualified': False, 'complete_fixed_trial_count': 12, 'e192_membership_checked': True,
            'search_replayed': 'same bounded EDG search, not an independent solver or exhaustive E192 optimization',
            'arithmetic_checked': 'independent exact forward and loaded checks rerun for every replayed candidate'}


def run(distribution_override=None):
    started = time.monotonic()
    extra_paths = [Path(__file__), Path(pair.__file__), Path(compare.__file__), Path(preferred_numbers.__file__),
                   ROOT/'tools/route_board.py',
                   monitor_source.ROWS_PATH, Path(monitor_source.__file__),
                   ron_source.ROWS_PATH, Path(ron_source.__file__)]
    extra_before = source.snapshot(extra_paths)
    data = source.load_current()
    distribution = F(str(data['rail']['distribution_drop_v'])) if distribution_override is None else F(
        _decimal(distribution_override, 'distribution hypothesis'))
    monitors = monitor_hypotheses()
    rows = [trial(data, kind, distribution, monitor, FB_IMPEDANCE_WINDOWS[0])
            for monitor in monitors for kind in CLASSES]
    choices = portfolio(data, monitors, distribution, rows)
    portfolio_verification = verify_portfolio(data, monitors, distribution, choices)
    scope = ron_source.assess_main(data)
    pair._load_edg()  # Re-pin installed numerical sources after every search.
    if source.snapshot(data['paths']) != data['before'] or source.snapshot(extra_paths) != extra_before:
        raise ValueError('Sources changed during coupled synthesis')
    return {'schema_version': 1, 'status': 'not_qualified', 'qualified': False,
            'scope': 'Ideal zero-leakage pair selection plus separate signed-bias loaded post-validation; not a complete power cell',
            'invariant_demands': {key: str(value) for key, value in compare.demands(data).items() if key != 'cases'},
            'load_cases_a_exact': [[name, str(current)] for name, current in data['cases']],
            'checked_load_cases': len(data['cases']), 'projected_ron_ohm_exact': str(RON),
            'distribution_is_native': distribution_override is None,
            'model_decisions_inside_command': 0,
            'current_limit_model_combined': False, 'ron_source_scope': scope, 'rows': rows,
            'portfolio': choices, 'portfolio_verification': portfolio_verification,
            'selector': {'name': 'EDG ESeriesRatioUtil + DividerValues', 'version': pair.EDG_VERSION,
                         'series': 192, 'installed_implementation_sha256': dict(pair.EDG_SOURCE_SHA256)},
            'source_sha256': {**data['before'], **extra_before}, 'elapsed_s': round(time.monotonic()-started, 6),
            'limitations': [
                '8.4 mohm is projected from the TPS259814 reviewed 3 A row to 4.25 A, not a qualified maximum there',
                'New RON is NOT combined with the fitted TPS25974 current-limit equation; candidate current admission is unproved',
                'Both resistor classes are hypotheses; no selected MPN, stock/supply, solder/lifetime drift or availability qualification',
                'Ideal selection uses zero leakage; signed loaded checks use declared diagnostic hypotheses, not actual source bounds',
                'Zero response delay; monitor VDD/output loading, bias-source energy paths and safety wiring are unqualified',
                'VFB table VIN=12 V does not qualify actual VIN=6..8.4 V; ripple, distribution, compensation/stability and thermal remain open',
                'UV/OV recovery checks are static only; startup, delays, current limiting and routed behavior remain open',
                'Full branch loading is added conservatively without subtracting existing native allowances; replacement current admission remains unproved',
                '58 native load cases do not qualify a whole replacement cell or a battery/input-power budget',
                'EDG no-match is bounded search, not discrete infeasibility; the first positive pair is not an optimum']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--distribution-drop-v', help='Explicit counterfactual only; default preserves current native demand')
    args = parser.parse_args()
    try:
        def interrupted(*_):
            raise KeyboardInterrupt('coupled synthesis cancelled')
        signal.signal(signal.SIGTERM, interrupted)
        work = ROOT/'work'
        work.mkdir(exist_ok=True)
        if work.is_symlink() or work.resolve() != work:
            raise ValueError('Unsafe work directory')
        directory = Path(tempfile.mkdtemp(prefix='main-static-pair-', dir=work))
        started = time.monotonic()
        awake = {}
        with keep_awake(awake, directory):
            result = run(args.distribution_drop_v)
        result.update(caffeinate=awake, command_elapsed_s=round(time.monotonic()-started, 6))
        if source.snapshot([ROOT/path for path in result['source_sha256']]) != result['source_sha256']:
            raise ValueError('Sources changed before report publication')
        pair._load_edg()  # Installed runtime is outside the repository snapshot.
        report = directory/'result.json'
        with report.open('x') as stream:
            stream.write(json.dumps(result, indent=2, allow_nan=False)+'\n')
        if json.loads(report.read_text()) != result:
            raise ValueError('Persisted report differs')
        print(json.dumps({'status': result['status'], 'report': str(report), 'elapsed_s': result['elapsed_s'],
                          'rows': [[r['monitor'], r['resistor_class'], r['ideal_status'], r['loaded_diagnostic_status']]
                                   for r in result['rows']],
                          'selected_windows': {group['monitor']+'/'+group['resistor_class']: group['selected_window_index']
                                               for group in result['portfolio']['groups']}}))
        return 1
    except (Exception, KeyboardInterrupt) as error:
        cancelled = isinstance(error, KeyboardInterrupt)
        print(json.dumps({'status': 'cancelled' if cancelled else 'execution_error', 'error': str(error), 'report': None}))
        return 130 if cancelled else 2


if __name__ == '__main__':
    raise SystemExit(main())
