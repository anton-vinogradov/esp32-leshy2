"""Independent ideal fault-bus KCL regression, not semiconductor qualification.

Each bus is only a voltage source, resistor and signed diagnostic current
source. No IC/clamp/reset model is implied. Literal input thresholds are an
independent oracle; unavailable pin modes and actual currents stay unknown.
"""
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction as F
import hashlib
from itertools import product
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools'))
from tools import ngspice_worker as worker
from hardware.layout.h6_r2_parallel_process import ProcessRegistry


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def literal_thresholds(main, aon, resistance):
    """Exact independent simultaneous HIGH and recommended input ceiling."""
    high = F('0.7')*max(main, aon)
    ceiling = min(F('5.5'), aon+F('0.3'))
    low = F('0.3')*min(main, aon)
    return {'high': high, 'ceiling': ceiling, 'low': low,
            'minimum_current': (main-ceiling)/resistance,
            'maximum_current': (main-high)/resistance}


def literal_high(main, aon, resistance, sink):
    limits = literal_thresholds(main, aon, resistance)
    bus = main-resistance*sink
    return limits['high'] <= bus <= limits['ceiling']


@unittest.skipUnless(worker.DEFAULT_LIBRARY.is_file(), 'bundled KiCad ngspice needed')
class MainFaultBusSpiceTests(unittest.TestCase):
    def test_corners_and_emitted_boundaries_against_independent_spice(self):
        # Import the implementation only after the optional native-runtime gate.
        import main_fault_bus as tool

        paths = {*map(Path, tool.source_paths()), Path(__file__), Path(worker.__file__),
                 Path(sys.modules[ProcessRegistry.__module__].__file__)}
        source_before = {str(p): digest(p) for p in paths}
        runtime_paths = worker.runtime_paths()
        runtime_before = {str(p): digest(p) for p in runtime_paths}
        result = tool.screen(main_v=['3', '3.3'], aon_v=['2.7', '3.6'],
                             resistance_ohm=['9900', '10100'], temperature_c=['25', '25'])
        self.assertIs(result['qualified'], False)

        corners = list(product((F(3), F('3.3')), (F('2.7'), F('3.6')), (F(9900), F(10100))))
        self.assertEqual(len(result['corners']), len(corners))
        reported = {(F(r['main_v_exact']), F(r['aon_v_exact']), F(r['resistance_ohm_exact'])): r
                    for r in result['corners']}
        self.assertEqual(set(reported), set(corners))
        self.assertEqual(len(reported), len(result['corners']))
        expected = {corner: literal_thresholds(*corner) for corner in corners}
        for corner, row in reported.items():
            literal = expected[corner]
            with self.subTest(corner=corner):
                self.assertEqual(F(row['vih_min_v_exact']), literal['high'])
                self.assertEqual(F(row['input_max_v_exact']), literal['ceiling'])
                self.assertEqual(F(row['vil_max_v_exact']), literal['low'])
                interval = row['allowed_total_signed_current_a']
                self.assertEqual(F(interval['minimum_a_exact']), literal['minimum_current'])
                self.assertEqual(F(interval['maximum_a_exact']), literal['maximum_current'])
                self.assertIs(interval['empty'], literal['minimum_current'] > literal['maximum_current'])
                self.assertEqual(F(row['zero_current']['bus_v_exact']), corner[0])
                self.assertIs(row['zero_current']['high_compatible'], literal_high(*corner, F(0)))
                self.assertEqual(F(row['pullup_sink_current_at_vil_a_exact']),
                                 (corner[0]-literal['low'])/corner[2])

        minimum = max(v['minimum_current'] for v in expected.values())
        maximum = min(v['maximum_current'] for v in expected.values())
        interval = result['uniform_current_interval']
        self.assertEqual(F(interval['minimum_a_exact']), minimum)
        self.assertEqual(F(interval['maximum_a_exact']), maximum)
        self.assertIs(interval['empty'], False)
        self.assertIs(interval['sufficient_not_necessary'], True)
        self.assertEqual(set(interval['minimum_witnesses']),
                         {reported[c]['id'] for c, v in expected.items() if v['minimum_current'] == minimum})
        self.assertEqual(set(interval['maximum_witnesses']),
                         {reported[c]['id'] for c, v in expected.items() if v['maximum_current'] == maximum})

        currents = tuple(map(F, ('-.000100', '0', '.000030', '.000050', '.000100')))
        points = [{'main': m, 'aon': a, 'resistance': r, 'sink': current, 'label': 'grid'}
                  for m, a, r in corners for current in currents]
        nominal = tool.screen(main_v=['3.3', '3.3'], aon_v=['3.3', '3.3'],
                              resistance_ohm=['10000', '10000'], temperature_c=['25', '25'])
        self.assertEqual(len(nominal['corners']), 1)
        self.assertIs(nominal['corners'][0]['zero_current']['high_compatible'], True)
        points.extend({'main': F('3.3'), 'aon': F('3.3'), 'resistance': F(10000),
                       'sink': current, 'label': 'nominal'} for current in currents)

        # +/-1 nA moves voltage by >=9.9 uV: far beyond the comparison tolerance.
        # Both emitted intersection bounds and the just-outside witnesses are
        # simulated at every corner; a constant-pass classifier cannot pass.
        epsilon = F('0.000000001')
        for label, bound in (('minimum', minimum), ('maximum', maximum)):
            for delta in (-epsilon, F(0), epsilon):
                points.extend({'main': m, 'aon': a, 'resistance': r, 'sink': bound+delta,
                               'label': f'{label}:{delta}'} for m, a, r in corners)
        self.assertEqual(len(points), 93)
        self.assertLessEqual(len(points), 128)

        registry = ProcessRegistry(grace_seconds=1)
        with tempfile.TemporaryDirectory(prefix='main-fault-bus-spice-', dir=ROOT/'work') as folder:
            directory = Path(folder)

            def batch(item):
                batch_id, stimuli = item
                deck = ['Independent conditional signed-current fault-bus KCL', '.temp 25']
                vectors = []
                number = lambda value: format(float(value), '.17g')
                for index, point in enumerate(stimuli):
                    deck.extend((f'vmain{index} main{index} 0 {number(point["main"])}',
                                 f'rpull{index} main{index} bus{index} {number(point["resistance"])}',
                                 f'isink{index} bus{index} 0 {number(point["sink"])}'))
                    vectors.append(f'v(bus{index})')
                request = {'netlist': [*deck, '.end'], 'vectors': vectors}
                self.assertLessEqual(len(vectors), 24)
                request_path = directory/f'{batch_id}.request.json'
                request_path.write_text(json.dumps(request))
                request_file_hash = digest(request_path)
                output_path = directory/f'{batch_id}.result.json'
                execution = registry.run([sys.executable, '-B', str(ROOT/'tools/ngspice_worker.py'),
                                          '--request', str(request_path)], output_path, 20, cwd=ROOT,
                                         stderr_log=directory/f'{batch_id}.stderr.log')
                self.assertEqual(execution['exit_code'], 0)
                self.assertEqual(execution['returncode'], 0)
                self.assertIs(execution['orphaned_descendants'], False)
                self.assertEqual(digest(request_path), request_file_hash)
                observed = json.loads(output_path.read_text())
                self.assertEqual(observed['status'], 'worker_execution_success')
                self.assertIs(observed['qualified'], False)
                self.assertEqual(observed['analysis'], 'op')
                self.assertEqual(observed['worker_sha256'], source_before[str(Path(worker.__file__))])
                self.assertEqual(observed['library_sha256'], runtime_before[str(runtime_paths[0])])
                self.assertEqual(observed['code_model_sha256'], {str(p): runtime_before[str(p)] for p in runtime_paths[1:]})
                self.assertEqual(observed['request_sha256'], hashlib.sha256(
                    json.dumps(request, sort_keys=True, separators=(',', ':')).encode()).hexdigest())
                self.assertEqual(set(observed['values']), set(vectors))
                checks = []
                for vector, point in zip(vectors, stimuli):
                    voltage = observed['values'][vector]
                    main, aon, resistance, sink = (point[k] for k in ('main', 'aon', 'resistance', 'sink'))
                    expected_voltage = main-resistance*sink
                    self.assertAlmostEqual(voltage, float(expected_voltage), delta=1e-8,
                                           msg=f'batch={batch_id}, vector={vector}, point={point}')
                    limits = literal_thresholds(main, aon, resistance)
                    measured_high = float(limits['high'])-1e-8 <= voltage <= float(limits['ceiling'])+1e-8
                    expected_high = literal_high(main, aon, resistance, sink)
                    self.assertIs(measured_high, expected_high, msg=str(point))
                    checks.append((point['label'], measured_high))
                return checks

            batches = list(enumerate([points[i:i+24] for i in range(0, len(points), 24)]))
            self.assertEqual(len(batches), 4)
            with ThreadPoolExecutor(max_workers=4) as pool:
                try:
                    checks = [check for batch_checks in pool.map(batch, batches) for check in batch_checks]
                finally:
                    registry.cancel_all()
            self.assertEqual(registry.active_count, 0)
        self.assertEqual(len(checks), 93)
        for label, all_pass in ((f'minimum:{-epsilon}', False), ('minimum:0', True),
                                (f'minimum:{epsilon}', True), (f'maximum:{-epsilon}', True),
                                ('maximum:0', True), (f'maximum:{epsilon}', False)):
            results = [high for point_label, high in checks if point_label == label]
            self.assertEqual(len(results), 8)
            self.assertIs(all(results), all_pass)
        self.assertTrue(any(high for _, high in checks))
        self.assertTrue(any(not high for _, high in checks))
        self.assertEqual({str(p): digest(p) for p in paths}, source_before)
        self.assertEqual({str(p): digest(p) for p in worker.runtime_paths()}, runtime_before)


if __name__ == '__main__':
    unittest.main()
