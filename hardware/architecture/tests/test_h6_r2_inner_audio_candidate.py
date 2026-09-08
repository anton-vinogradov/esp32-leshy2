"""Finite inward-audio candidate boundary; does not qualify the audio circuit."""
import json
import math
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PATH=ROOT/'hardware/layout/h6-r2-inner-audio-candidate.json'
# Independently enumerated review scope: deleting a row must never silently
# restore one displaced component or an old outward support.
REFS=frozenset('C113 C144 C145 C197 C199 C217 C218 C229 C230 C231 C232 C233 C234 C256 C257 C270 C272 C285 C286 C65 MK1 R169 R201 R202 R203 R204 R205 R206 R242 R258 R267 R287 R288 R56 U112 U113 U115 U116 U118 U120 U131 U132 U18 U28 U48 U68 U80 U82 U83 U85'.split())
EXPECTED_NATIVE_SHA='cb5855cf3d9c534bfdbd5190a86f54f4d800b8c594c717257463fd81033f4e9f'

def validate(review,contract,ledger):
    rows=review['placement_rows']
    assert len(rows)==len(REFS)==50
    assert {r['reference'] for r in rows}==REFS
    assert review['baseline_board_sha256']==EXPECTED_NATIVE_SHA
    assert review['status']=='placement_adopted_not_audio_qualified'
    assert review['authority'] and all(v is False for v in review['authority'].values())
    assert review['unresolved']
    index={r['reference']:r for r in ledger if r['project']=='LESHY2-RF-R2'}
    for row in rows:
        assert row['device_id']==index[row['reference']]['device_id']
        assert row['instance']==index[row['reference']]['instance']
        assert row['mpn']==index[row['reference']]['mpn']
        assert row['footprint']==index[row['reference']]['footprint']
        side='F.Cu' if row['reference']=='MK1' else 'B.Cu'
        assert row['after']['side']==side
        target=contract['placement_overrides'][row['instance']]
        assert target['frame']==('rear-outer' if side=='F.Cu' else 'rear-inner')
        assert target['anchor_mm']==row['after']['anchor_mm']
        assert target['rotation_deg']==row['after']['angle']
        assert target['mechanical_locked'] is True
        assert 'centre_mm' not in target
    byref={r['reference']:r for r in rows}
    assert byref['U83']['after']=={'side':'B.Cu','angle':0,'anchor_mm':[.8,99.9]}
    assert byref['MK1']['after']=={'side':'F.Cu','angle':180,'anchor_mm':[8,112]}
    jack=byref['U83']
    assert jack['mpn']=='Same Sky SJ-43515TS-SMT-TR'
    assert jack['footprint']=='Leshy2_R2:SJ-43515TS-SMT-TR'
    assert [p[0] for p in jack['pad_net_multiset']]==['','','1','2','3','4','5']
    expected={'1':'HEADSET_MIC_RAW','2':'HEADPHONE_LEFT_TIP','3':'HEADPHONE_RIGHT_RING1','4':'AUDIO_GROUND','5':'HEADSET_SWITCH_STATE'}
    assert {p:n.rsplit('/',1)[-1] for p,n in jack['pad_net_multiset'] if p}==expected
    esd=byref['U82']['pad_net_multiset']
    assert {p:n.rsplit('/',1)[-1] for p,n in esd if p in ('3','8')}=={'3':'POWER_GROUND','8':'POWER_GROUND'}
    for ref,ground in [('C217','POWER_GROUND'),('C218','AUDIO_GROUND'),('C233','POWER_GROUND'),('C234','AUDIO_GROUND')]:
        assert dict(byref[ref]['pad_net_multiset'])['2'].rsplit('/',1)[-1]==ground
    pairs=[p for p in contract['placement_policy']['critical_pad_pairs'] if p['first_instance']=='safe_fault_reset_buffer_bypass']
    assert {(p['canonical_net'],p['first_pad_number'],p['second_instance'],p['second_pad_number'],p['maximum_distance_mm']) for p in pairs}=={
        ('AON_SAFE_3V3','1','safe_fault_reset_buffer','8',3.0),
        ('POWER_GROUND','2','safe_fault_reset_buffer','4',3.0)}
    assert len(pairs)==2

class InnerAudioCandidateTests(unittest.TestCase):
    def setUp(self):
        self.review=json.loads(PATH.read_text())
        self.contract=json.loads((ROOT/'hardware/layout/h6-r2-placement-contract.json').read_text())
        self.ledger=json.loads((ROOT/'hardware/ecad/generated/H2-R2-native-instance-ledger.json').read_text())['rows']
    def check(self):validate(self.review,self.contract,self.ledger)
    def test_exact_current_candidate(self):self.check()
    def test_baseline_is_explicit_not_current_board_authority(self):
        self.assertEqual(EXPECTED_NATIVE_SHA,self.review['baseline_board_sha256'])
        self.assertFalse(self.review['authority']['main_promotion_authorized_by_this_report'])
    def test_missing_reference_rejected(self):
        self.review['placement_rows'].pop()
        with self.assertRaises(AssertionError):self.check()
    def test_outward_jack_rejected(self):
        row=next(r for r in self.review['placement_rows'] if r['reference']=='U83');row['after']['side']='F.Cu'
        with self.assertRaises(AssertionError):self.check()
    def test_outward_passive_rejected(self):
        row=next(r for r in self.review['placement_rows'] if r['reference']=='C144');row['after']['side']='F.Cu'
        with self.assertRaises(AssertionError):self.check()
    def test_inward_acoustic_port_rejected(self):
        row=next(r for r in self.review['placement_rows'] if r['reference']=='MK1');row['after']['side']='B.Cu'
        with self.assertRaises(AssertionError):self.check()
    def test_identity_swap_rejected(self):
        self.review['placement_rows'][0]['device_id']='different_same_package'
        with self.assertRaises(AssertionError):self.check()
    def test_same_package_mpn_swap_rejected(self):
        self.review['placement_rows'][0]['mpn']='another part'
        with self.assertRaises(AssertionError):self.check()
    def test_footprint_swap_rejected(self):
        self.review['placement_rows'][0]['footprint']='another same-pad footprint'
        with self.assertRaises(AssertionError):self.check()
    def test_distinct_return_domains_preserved(self):
        row=next(r for r in self.review['placement_rows'] if r['reference']=='C218')
        next(p for p in row['pad_net_multiset'] if p[0]=='2')[1]='POWER_GROUND'
        with self.assertRaises(AssertionError):self.check()
    def test_esd_ground_relabel_rejected(self):
        row=next(r for r in self.review['placement_rows'] if r['reference']=='U82')
        next(p for p in row['pad_net_multiset'] if p[0]=='3')[1]='AUDIO_GROUND'
        with self.assertRaises(AssertionError):self.check()
    def test_contact_swap_rejected(self):
        row=next(r for r in self.review['placement_rows'] if r['reference']=='U83')
        next(p for p in row['pad_net_multiset'] if p[0]=='1')[1]='HEADPHONE_LEFT_TIP'
        with self.assertRaises(AssertionError):self.check()
    def test_production_admission_rejected(self):
        self.review['authority']['fabrication_ready']=True
        with self.assertRaises(AssertionError):self.check()

try:
    import pcbnew
except ImportError:
    pcbnew=None

@unittest.skipUnless(pcbnew,'Requires native KiCad Python; no CLI or board save')
class NativeInnerAudioLocalityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.board=pcbnew.LoadBoard(str(ROOT/'hardware/ecad/kicad/LESHY2-RF-R2/LESHY2-RF-R2.kicad_pcb'))
        cls.fps={f.GetReference():f for f in cls.board.GetFootprints()}
        cls.review=json.loads(PATH.read_text())
        for row in cls.review['placement_rows']:
            f=cls.fps[row['reference']];target=row['after']
            if f.IsFlipped()!=(target['side']=='B.Cu'):
                f.Flip(pcbnew.VECTOR2I(0,0),False)
            f.SetOrientationDegrees(target['angle'])
            f.SetPosition(pcbnew.VECTOR2I(*(pcbnew.FromMM(v) for v in target['anchor_mm'])))

    def pair(self,a,ap,b,bp,net,limit):
        aa=[p for p in self.fps[a].Pads() if p.GetNumber()==ap]
        bb=[p for p in self.fps[b].Pads() if p.GetNumber()==bp]
        self.assertTrue(aa and bb)
        self.assertEqual({net},{p.GetNetname().rsplit('/',1)[-1] for p in aa+bb})
        distance=min(math.hypot(pcbnew.ToMM(x.GetPosition().x-y.GetPosition().x),pcbnew.ToMM(x.GetPosition().y-y.GetPosition().y)) for x in aa for y in bb)
        self.assertLessEqual(distance,limit)

    def test_actual_power_switch_and_amp_pad_locality(self):
        # Output AGND and upstream PG are intentionally not conflated. These
        # distances qualify placement only, not a complete routed return loop.
        for pair in [('C217','1','U80','1','3V3_MAIN'),('C217','2','U80','2','POWER_GROUND'),
                     ('C218','1','U80','6','3V3_CODEC_SWITCHED'),
                     ('C144','1','U48','1','3V3_MAIN'),('C144','2','U48','2','POWER_GROUND'),
                     ('C145','1','U48','6','VVOICE_IO_3V3'),
                     ('C234','1','U86','6','3V3_MAIN'),('C234','2','U86','7','AUDIO_GROUND'),
                     ('C272','1','U120','8','AON_SAFE_3V3'),('C272','2','U120','4','POWER_GROUND'),
                     ('C270','1','U118','8','AON_SAFE_3V3'),('C270','2','U118','4','POWER_GROUND')]:
            with self.subTest(pair=pair):self.pair(*pair,3.0)
        self.pair('C233','1','U86','6','3V3_MAIN',3.4)

    def test_moving_input_cap_back_to_old_far_position_fails(self):
        f=self.fps['C217'];saved=f.GetPosition()
        try:
            f.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(57.625),pcbnew.FromMM(77.125)))
            with self.assertRaises(AssertionError):self.pair('C217','1','U80','1','3V3_MAIN',3.0)
        finally:f.SetPosition(saved)

    def silk_clear(self):
        first=[g.GetEffectiveShape() for g in self.fps['U118'].GraphicalItems() if g.GetLayer()==pcbnew.B_SilkS]
        second=[g.GetEffectiveShape() for g in self.fps['U28'].GraphicalItems() if g.GetLayer()==pcbnew.B_SilkS]
        self.assertEqual((3,3),(len(first),len(second)))
        self.assertFalse(any(a.Collide(b,pcbnew.FromMM(.15)) for a in first for b in second))

    def test_actual_stroked_silk_gap_not_courtyard_surrogate(self):
        self.silk_clear()

    def test_original_0p065_silk_gap_rejected(self):
        f=self.fps['U118'];saved=f.GetPosition();angle=f.GetOrientationDegrees()
        try:
            f.SetOrientationDegrees(180)
            f.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(17.5),pcbnew.FromMM(114)))
            with self.assertRaises(AssertionError):self.silk_clear()
        finally:f.SetPosition(saved);f.SetOrientationDegrees(angle)

    def test_old_courtyard_local_but_4p08mm_vcc_span_rejected(self):
        refs=('U118','C270');saved={r:(self.fps[r].GetPosition(),self.fps[r].GetOrientationDegrees()) for r in refs}
        try:
            for r,angle,at in [('U118',180,[17.5,114]),('C270',270,[18.895,116.695])]:
                self.fps[r].SetOrientationDegrees(angle)
                self.fps[r].SetPosition(pcbnew.VECTOR2I(*(pcbnew.FromMM(v) for v in at)))
            with self.assertRaises(AssertionError):self.pair('C270','1','U118','8','AON_SAFE_3V3',3.0)
        finally:
            for r,(at,angle) in saved.items():self.fps[r].SetPosition(at);self.fps[r].SetOrientationDegrees(angle)

    def test_reset_pair_all_neighbor_silkscreen_at_0p20(self):
        for ref in ('U118','C270'):
            shapes=[g.GetEffectiveShape() for g in self.fps[ref].GraphicalItems() if g.GetLayer()==pcbnew.B_SilkS]
            for other,f in self.fps.items():
                if other==ref or not f.IsFlipped():continue
                foreign=[g.GetEffectiveShape() for g in f.GraphicalItems() if g.GetLayer()==pcbnew.B_SilkS]
                with self.subTest(first=ref,second=other):
                    self.assertFalse(any(a.Collide(b,pcbnew.FromMM(.20)) for a in shapes for b in foreign))

if __name__=='__main__':unittest.main()
