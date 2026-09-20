#!/usr/bin/env python3
"""Conditional coupled MAIN feedback/monitor divider selection, never cell approval.

Run in the prepared EDG0.5.2 environment. Native voltage/load/ripple demands
are immutable; distribution defaults to the current source value. Changed
resistor classes, RON and monitor circuitry are explicit hypotheses, not MPN
adoption. The RON hypothesis is NOT combined with the old eFuse current law.
"""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction as F
import json
import math
from pathlib import Path
import signal
import tempfile
import time

import synthesize_main_feedback as source
import compare_main_feedback as compare
import edg_feedback_pair as pair
from h6_power_corner_math import Interval, resistor_interval, _decimal
import h6_main_monitor_window as monitor_source
import h6_ron_source_scope as ron_source
from route_board import keep_awake

ROOT = source.ROOT
RON = F('0.0084')
CLASSES = {'0.1pct_10ppm': '.001', '0.05pct_10ppm': '.0005'}
RESERVES = tuple(map(F, ('.000001', '.00001', '.00005', '.0001', '.0002', '.0005', '.001', '.002', '.003')))


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


def synthesize(data, resistor_class, distribution, monitor, solver=select_pair):
    if resistor_class not in CLASSES or not isinstance(distribution, F) or distribution < 0:
        raise ValueError('Explicit supported resistor class and nonnegative exact distribution required')
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
        fb_required, fb_impedance = interval(required_min, maximum), interval(5000, 10000)
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


def run(distribution_override=None):
    started = time.monotonic()
    extra_paths = [Path(__file__), Path(pair.__file__), Path(compare.__file__),
                   ROOT/'tools/route_board.py',
                   monitor_source.ROWS_PATH, Path(monitor_source.__file__),
                   ron_source.ROWS_PATH, Path(ron_source.__file__)]
    extra_before = source.snapshot(extra_paths)
    data = source.load_current()
    distribution = F(str(data['rail']['distribution_drop_v'])) if distribution_override is None else F(
        _decimal(distribution_override, 'distribution hypothesis'))
    monitors = monitor_hypotheses()
    rows = [synthesize(data, kind, distribution, monitor) for monitor in monitors for kind in CLASSES]
    scope = ron_source.assess_main(data)
    pair._load_edg()  # Re-pin installed numerical sources after every search.
    if source.snapshot(data['paths']) != data['before'] or source.snapshot(extra_paths) != extra_before:
        raise ValueError('Sources changed during coupled synthesis')
    return {'schema_version': 1, 'status': 'not_qualified', 'qualified': False,
            'scope': 'Coupled zero-leakage static feedback/monitor pair only; not a complete power cell',
            'invariant_demands': {key: str(value) for key, value in compare.demands(data).items() if key != 'cases'},
            'load_cases_a_exact': [[name, str(current)] for name, current in data['cases']],
            'checked_load_cases': len(data['cases']), 'projected_ron_ohm_exact': str(RON),
            'distribution_is_native': distribution_override is None,
            'model_decisions_inside_command': 0,
            'current_limit_model_combined': False, 'ron_source_scope': scope, 'rows': rows,
            'selector': {'name': 'EDG ESeriesRatioUtil + DividerValues', 'version': pair.EDG_VERSION,
                         'series': 192, 'installed_implementation_sha256': dict(pair.EDG_SOURCE_SHA256)},
            'source_sha256': {**data['before'], **extra_before}, 'elapsed_s': round(time.monotonic()-started, 6),
            'limitations': [
                '8.4 mohm is projected from the TPS259814 reviewed 3 A row to 4.25 A, not a qualified maximum there',
                'New RON is NOT combined with the fitted TPS25974 current-limit equation; candidate current admission is unproved',
                'Both resistor classes are hypotheses; no selected MPN, stock/supply, solder/lifetime drift or availability qualification',
                'Zero feedback/SENSE leakage and zero response delay; monitor supply, output loading and safety wiring are unqualified',
                'VFB table VIN=12 V does not qualify actual VIN=6..8.4 V; ripple, distribution, compensation/stability and thermal remain open',
                'UV/OV recovery checks are static only; startup, delays, current limiting and routed behavior remain open',
                'New divider loading is reported but not admitted; 58 source load cases do not qualify a whole replacement cell',
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
                          'rows': [[r['monitor'], r['resistor_class'], r['status']] for r in result['rows']]}))
        return 1
    except (Exception, KeyboardInterrupt) as error:
        cancelled = isinstance(error, KeyboardInterrupt)
        print(json.dumps({'status': 'cancelled' if cancelled else 'execution_error', 'error': str(error), 'report': None}))
        return 130 if cancelled else 2


if __name__ == '__main__':
    raise SystemExit(main())
