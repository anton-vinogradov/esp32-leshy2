"""Independent DC equation regression with existing ngspice, not IC qualification.

The voltage source uses the proposed regulated voltage; SPICE independently
checks the feedback node, protected node, sense node and both branch currents.
Signed bias stimuli are diagnostic, never claimed as actual IC limits.
"""
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction as F
import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import synthesize_main_static_pair as tool
from tools import ngspice_worker as worker
from hardware.layout.h6_r2_parallel_process import ProcessRegistry


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@unittest.skipUnless(importlib.util.find_spec('edg') and worker.DEFAULT_LIBRARY.is_file(),
                     'prepared EDG and bundled KiCad ngspice needed')
class MainLoadedSpiceTests(unittest.TestCase):
    def test_signed_bias_resistor_load_and_ripple_corners_against_native_spice(self):
        data = tool.source.load_current()
        monitor = next(m for m in tool.monitor_hypotheses() if m['id'] == 'tps3703a7330')
        candidate = tool.synthesize(data, '0.1pct_10ppm', F('.05'), monitor)
        self.assertEqual(candidate['status'], 'conditional_joint_candidate')
        self.assertFalse(candidate['qualified'])
        fb = candidate['feedback']['selected_nominal_ohm_exact']
        mon = candidate['monitor_pair']['selected_nominal_ohm_exact']
        factors = tuple(map(F, candidate['factor_interval_exact']))
        loads = tuple(sorted({min(i for _, i in data['cases']), max(i for _, i in data['cases'])}))
        corners = list(product(
            (F(data['reference'].minimum), F(data['reference'].maximum)),
            factors, factors, (F('-.000001'), F('.000001')),
            factors, factors, (F('-.0000015'), F('.0000015')),
            loads, (F('-.01'), F(0), F('.01'))))
        self.assertEqual(len(corners), 768)
        runtime_before = {str(p): digest(p) for p in worker.runtime_paths()}
        worker_before = digest(worker.__file__)
        registry = ProcessRegistry(grace_seconds=1)
        with tempfile.TemporaryDirectory(prefix='main-loaded-spice-', dir=ROOT / 'work') as folder:
            directory = Path(folder)

            def batch(item):
                batch_id, points = item
                deck, vectors, expected = ['Conditional MAIN signed-bias DC equation regression'], [], {}
                for j, (ref, ft, fb_factor, ifb, mt, mb, imon, load, ripple) in enumerate(points):
                    rt, rb = F(fb['top']) * ft, F(fb['bottom']) * fb_factor
                    rmt, rmb = F(mon['top']) * mt, F(mon['bottom']) * mb
                    value = tool.loaded_point(ref, rt, rb, ifb, rmt, rmb, imon,
                                              load, tool.RON, raw_ripple_v=ripple)
                    n = lambda val: format(float(val), '.17g')
                    deck.extend([
                        f'vraw{j} raw{j} 0 {n(value["raw_v"])}',
                        f'rft{j} raw{j} fb{j} {n(rt)}', f'rfb{j} fb{j} 0 {n(rb)}',
                        f'ifb{j} fb{j} 0 {n(ifb)}',
                        f'refuse{j} raw{j} shunt{j} {n(tool.RON)}',
                        f'vbranch{j} shunt{j} local{j} 0',
                        f'iload{j} local{j} 0 {n(load)}',
                        f'rmt{j} local{j} sense{j} {n(rmt)}', f'rmb{j} sense{j} 0 {n(rmb)}',
                        f'isense{j} sense{j} 0 {n(imon)}',
                    ])
                    # Feedback reference is independently known, not copied
                    # from the proposed raw voltage used as the stimulus.
                    expected.update({f'v(fb{j})': ref + ripple * rb / (rt + rb),
                                     f'v(local{j})': value['local_v'],
                                     f'v(sense{j})': value['sense_v'],
                                     f'i(vraw{j})': -value['converter_current_a'],
                                     f'i(vbranch{j})': value['efuse_current_a']})
                    vectors.extend(list(expected)[-5:])
                request = {'netlist': [*deck, '.end'], 'vectors': vectors}
                request_path = directory / f'{batch_id}.request.json'
                request_path.write_text(json.dumps(request))
                result_path = directory / f'{batch_id}.result.json'
                execution = registry.run(
                    [sys.executable, '-B', str(ROOT / 'tools/ngspice_worker.py'),
                     '--request', str(request_path)], result_path, 30, cwd=ROOT,
                    stderr_log=directory / f'{batch_id}.stderr.log')
                self.assertEqual(execution['exit_code'], 0)
                self.assertFalse(execution['orphaned_descendants'])
                result = json.loads(result_path.read_text())
                self.assertEqual(result['status'], 'worker_execution_success')
                self.assertIs(result['qualified'], False)
                self.assertEqual(result['worker_sha256'], worker_before)
                self.assertEqual(result['library_sha256'], runtime_before[str(worker.runtime_paths()[0])])
                self.assertEqual(result['code_model_sha256'], {k: v for k, v in runtime_before.items()
                                                              if k != str(worker.runtime_paths()[0])})
                self.assertEqual(result['request_sha256'], hashlib.sha256(
                    json.dumps(request, sort_keys=True, separators=(',', ':')).encode()).hexdigest())
                self.assertEqual(set(result['values']), set(expected))
                for name, value in expected.items():
                    self.assertAlmostEqual(result['values'][name], float(value), delta=1e-8,
                                           msg=f'batch={batch_id}, vector={name}')
                return len(points)

            # At most 120 vectors per worker (existing protocol cap 128).
            batches = list(enumerate([corners[i:i+24] for i in range(0, len(corners), 24)]))
            with ThreadPoolExecutor(max_workers=4) as pool:
                try:
                    self.assertEqual(sum(pool.map(batch, batches)), len(corners))
                finally:
                    registry.cancel_all()
        self.assertEqual({str(p): digest(p) for p in worker.runtime_paths()}, runtime_before)
        self.assertEqual(digest(worker.__file__), worker_before)
        self.assertEqual(tool.source.snapshot(data['paths']), data['before'])


if __name__ == '__main__':
    unittest.main()
