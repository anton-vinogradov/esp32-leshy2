"""Historical fifty-part review and twenty-six retained current requirements.

The seven bottom-microphone and seventeen under-Cap replacement poses have
separate exact owners. None of these placement fixtures qualifies the audio.
"""
import copy
import hashlib
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
MICROPHONE_SUPERSEDED_REFS=frozenset('MK1 R206 C232 R205 U85 C229 R202'.split())
ENCODER_SUPERSEDED_REFS=frozenset('C144 C145 C199 C230 C256 C257 R201 R203 R242 R267 R287 R288 R56 U48 U68 U82 U83'.split())
SUPERSEDED_REFS=MICROPHONE_SUPERSEDED_REFS | ENCODER_SUPERSEDED_REFS
HISTORICAL_ROWS_SHA='c78af09eff2278743b42ed5c1d3018b686e4d70c2670ff64d3ba8a36d9bb6330'
MICROPHONE_REVIEW='hardware/layout/h6-r2-microphone-bottom-candidate.json'
ENCODER_REVIEW='hardware/layout/h6-r2-encoder-under-cap-review.json'
REPLACEMENT_REVIEWS={MICROPHONE_REVIEW:sorted(MICROPHONE_SUPERSEDED_REFS),
                     ENCODER_REVIEW:sorted(ENCODER_SUPERSEDED_REFS)}
ENCODER_REPLACEMENT_REFS=frozenset('C114 C122 C125 C130 C131 C132 C136 C142 C144 C145 C149 C195 C199 C230 C244 C245 C250 C251 C252 C253 C256 C257 C258 C264 C265 C266 C268 C271 C276 C282 C58 C69 J3 Q6 R105 R115 R116 R117 R118 R119 R120 R121 R134 R138 R140 R171 R185 R201 R203 R224 R225 R230 R236 R237 R239 R242 R243 R244 R249 R251 R255 R256 R260 R261 R264 R267 R271 R279 R281 R282 R283 R284 R286 R287 R288 R49 R54 R56 R68 SW3 U100 U103 U109 U110 U111 U114 U119 U123 U126 U128 U15 U19 U30 U31 U32 U39 U40 U41 U42 U47 U48 U49 U68 U82 U83 U94'.split())

def validate(review,contract,ledger,replacement):
    rows=review['placement_rows']
    assert len(rows)==len(REFS)==50
    assert {r['reference'] for r in rows}==REFS
    assert review['baseline_board_sha256']==EXPECTED_NATIVE_SHA
    assert review['status']=='placement_partially_superseded_not_audio_qualified'
    scope=review['placement_scope']
    assert scope['historical_status']=='placement_adopted_not_audio_qualified'
    assert scope['historical_fields']==['placement_rows','constraints']
    assert scope['superseded_references']==sorted(SUPERSEDED_REFS)
    assert scope['retained_current_reference_count']==len(REFS-SUPERSEDED_REFS)==26
    assert scope['current_replacement_reviews']==REPLACEMENT_REVIEWS
    assert MICROPHONE_SUPERSEDED_REFS.isdisjoint(ENCODER_SUPERSEDED_REFS)
    assert 'current_replacement_review' not in scope
    assert scope['historical_placement_rows_sha256']==HISTORICAL_ROWS_SHA
    assert hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()==HISTORICAL_ROWS_SHA
    assert review['authority'] and all(v is False for v in review['authority'].values())
    assert review['unresolved']
    assert isinstance(replacement,dict), 'current under-Cap replacement review is missing'
    new_rows=replacement['placement_rows']
    assert len(new_rows)==len(ENCODER_REPLACEMENT_REFS)==106
    assert {row['reference'] for row in new_rows}==ENCODER_REPLACEMENT_REFS
    new={row['reference']:row for row in new_rows}
    assert REFS & new.keys()==ENCODER_SUPERSEDED_REFS
    index={r['reference']:r for r in ledger if r['project']=='LESHY2-RF-R2'}
    for row in rows:
        assert row['device_id']==index[row['reference']]['device_id']
        assert row['instance']==index[row['reference']]['instance']
        assert row['mpn']==index[row['reference']]['mpn']
        assert row['footprint']==index[row['reference']]['footprint']
        side='F.Cu' if row['reference']=='MK1' else 'B.Cu'
        # This is the preserved historical side, not today's MK1 requirement.
        assert row['after']['side']==side
        if row['reference'] in MICROPHONE_SUPERSEDED_REFS:
            continue
        expected=row['after']
        angle=expected['angle']
        if row['reference'] in ENCODER_SUPERSEDED_REFS:
            replacement_row=new[row['reference']]
            assert replacement_row['instance']==row['instance']
            expected=replacement_row['after']
            angle=expected['rotation_deg']
            assert expected['side']=='B.Cu'
        target=contract['placement_overrides'][row['instance']]
        assert target['frame']==('rear-outer' if side=='F.Cu' else 'rear-inner')
        assert target['anchor_mm']==expected['anchor_mm']
        assert target['rotation_deg'] % 360==angle % 360
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
        path=ROOT/ENCODER_REVIEW
        self.replacement=json.loads(path.read_text()) if path.exists() else None
    def check(self):validate(self.review,self.contract,self.ledger,self.replacement)
    def test_historical_scope_and_exact_current_retained_26(self):self.check()
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
    def test_historical_mk1_side_mutation_rejected_not_current_inward_pose(self):
        row=next(r for r in self.review['placement_rows'] if r['reference']=='MK1');row['after']['side']='B.Cu'
        with self.assertRaises(AssertionError):self.check()
    def test_seven_replacement_contract_poses_do_not_rewrite_history(self):
        historical=copy.deepcopy(self.review['placement_rows'])
        current={
            'MK1':(0,[47,147.4]),'R206':(180,[47,144]),'C232':(90,[49.25,143.3]),
            'R205':(270,[49.25,140.65]),'U85':(90,[16.5,113.75]),
            'C229':(90,[18.55,113.75]),'R202':(90,[14.7,113.25])}
        for row in self.review['placement_rows']:
            if row['reference'] in current:
                angle,at=current[row['reference']]
                target=self.contract['placement_overrides'][row['instance']]
                target.update(frame='rear-inner',anchor_mm=at,rotation_deg=angle)
        self.check()
        self.assertEqual(historical,self.review['placement_rows'])
        # Passing this historical validator does not qualify those new poses:
        # the separate current review and placement/intent admission must do so.
        self.assertFalse(self.review['authority']['main_promotion_authorized_by_this_report'])
    def test_superseded_scope_cannot_expand_or_shrink_to_hide_retained_drift(self):
        self.check()
        for mutation in ('remove','add','duplicate','count','owner','shared_owner'):
            review=copy.deepcopy(self.review)
            scope=review['placement_scope']
            if mutation=='remove':scope['superseded_references'].pop()
            elif mutation=='add':scope['superseded_references'].append('C197')
            elif mutation=='duplicate':scope['superseded_references'].append('MK1')
            elif mutation=='count':scope['retained_current_reference_count']=25
            elif mutation=='owner':scope['current_replacement_reviews']['unreviewed.json']=scope['current_replacement_reviews'].pop(ENCODER_REVIEW)
            else:scope['current_replacement_reviews'][ENCODER_REVIEW].append('MK1')
            with self.subTest(mutation=mutation),self.assertRaises(AssertionError):
                validate(review,self.contract,self.ledger,self.replacement)
    def test_retained_reference_still_requires_current_contract_pose(self):
        self.check()
        self.contract['placement_overrides']['audio_capture_mic_coupling']['anchor_mm']=[13.35,111.25]
        with self.assertRaises(AssertionError):self.check()
    def test_encoder_replacement_needs_exact_unique_inventory_and_current_pose(self):
        self.check()
        for mutation in ('missing','duplicate','extra','wrong_ref','wrong_instance','side','pose','angle'):
            replacement=copy.deepcopy(self.replacement)
            rows=replacement['placement_rows']
            row=next(r for r in rows if r['reference']=='U83')
            if mutation=='missing':rows.remove(row)
            elif mutation=='duplicate':rows.append(copy.deepcopy(row))
            elif mutation=='extra':rows.append({**copy.deepcopy(row),'reference':'R169'})
            elif mutation=='wrong_ref':row['reference']='C197'
            elif mutation=='wrong_instance':row['instance']='headset_mic_selector'
            elif mutation=='side':row['after']['side']='F.Cu'
            elif mutation=='pose':row['after']['anchor_mm']=[.8,99.9]
            else:row['after']['rotation_deg']=180
            with self.subTest(mutation=mutation),self.assertRaises(AssertionError):
                validate(self.review,self.contract,self.ledger,replacement)
    def test_before_after_and_all_pad_nets_remain_immutable_history(self):
        for field in ('before','after','pad_net_multiset'):
            review=copy.deepcopy(self.review)
            row=next(r for r in review['placement_rows'] if r['reference']=='U85')
            if field=='pad_net_multiset':row[field][0][1]='another_net'
            else:row[field]['anchor_mm'][0]+=.1
            with self.subTest(field=field),self.assertRaises(AssertionError):
                validate(review,self.contract,self.ledger,self.replacement)
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
        # Never reapply historical poses over the actual current native board.
        # Current seven-part microphone geometry is tested by its own review.

    def test_all_fifty_native_pad_net_multisets_keep_exact_electrical_identity(self):
        for row in self.review['placement_rows']:
            fp=self.fps[row['reference']]
            with self.subTest(reference=row['reference']):
                self.assertEqual(row['mpn'],fp.GetValue())
                self.assertEqual(row['footprint'],fp.GetFPIDAsString())
                self.assertEqual(sorted(row['pad_net_multiset']),
                                 sorted([p.GetNumber(),p.GetNetname()] for p in fp.Pads()))

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
