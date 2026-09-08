"""Exact EC11 axes, declared engineering PTH bounds and narrow transition guard."""
import copy
from fractions import Fraction as F
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'hardware/layout'))
sys.path.insert(0,str(ROOT/'hardware/ecad'))
import h6_r2_encoder_fit as guard
import h2_r2_encoder_footprint as generator

spec=importlib.util.spec_from_file_location('encoder_fixture',Path(__file__).with_name('test_h6_r2_encoder_geometry.py'))
fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
parse,children,field=fixture.parse,fixture.children,fixture.field
GEOMETRY=ROOT/'hardware/layout/h6-r2-encoder-fit-candidate.json'


def native_states():
    # Independent world fixture read from pre-change native SW3. No generator
    # output or guard constant is used to manufacture the expected coordinates.
    xy={'A':[68_500_000,57_750_000],'C':[71_000_000,57_750_000],
        'B':[73_500_000,57_750_000],'D':[68_500_000,43_250_000],'E':[73_500_000,43_250_000]}
    nets={'A':'/RF_31_REAR_CONTROLS/ENCODER_A','B':'/RF_31_REAR_CONTROLS/ENCODER_B',
          'C':'/RF_01_USB_PD_CHARGE/POWER_GROUND','D':'/RF_01_USB_PD_CHARGE/POWER_GROUND',
          'E':'/RF_31_REAR_CONTROLS/UI_ENCODER_PUSH_N'}
    def pad(name,at,net='',size=(2_000_000,2_000_000),drill=(1_100_000,1_100_000),oval=False):
        return dict(number=name,at_nm=list(at),net=net,size_nm=list(size),drill_nm=list(drill),
                    pth=True,npth=False,both_copper_faces=True,oval_drill=oval)
    after={'reference':'SW3','footprint':'Leshy2_R2:EC11E18244AU-ENGINEERING-PTH',
           'side':'F.Cu','anchor_nm':[71_000_000,50_250_000],'rotation_deg':0,
           'pads':[pad(n,xy[n],nets[n]) for n in xy]}
    after['pads'] += [pad('MP',[x,50_250_000],size=(2_800_000,4_800_000),
                         drill=(2_000_000,4_000_000),oval=True) for x in (64_750_000,77_250_000)]
    before=copy.deepcopy(after)
    before.update(footprint='Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm_MountingHoles',
                  anchor_nm=[68_500_000,57_750_000],rotation_deg=90)
    for p in before['pads']:
        p['number']={'D':'S2','E':'S1'}.get(p['number'],p['number'])
        if p['number']=='MP':p['at_nm'][0]+=(650_000 if p['at_nm'][0]<71_000_000 else -650_000)
    for at in ([71_000_000,50_250_000],[71_000_000,54_750_000]):
        q=pad('',at);q.update(pth=False,npth=True);before['pads'].append(q)
    return before,after


class EncoderFitTests(unittest.TestCase):
    def test_native_snapshot_reads_library_id_fields_not_swig_proxy_repr(self):
        fp=Mock();fp.GetReference.return_value='SW3';fp.IsFlipped.return_value=False
        fp.GetFPID.return_value.GetLibNickname.return_value='Leshy2_R2'
        fp.GetFPID.return_value.GetLibItemName.return_value='EC11E18244AU-ENGINEERING-PTH'
        fp.GetPosition.return_value.x=71_000_000;fp.GetPosition.return_value.y=50_250_000
        fp.GetOrientationDegrees.return_value=0;fp.Pads.return_value=[]
        self.assertEqual('Leshy2_R2:EC11E18244AU-ENGINEERING-PTH',guard.snapshot(fp,Mock())['footprint'])

    def test_exact_source_and_no_r1_or_native_outputs(self):
        self.assertEqual({generator.OUTPUT:generator.footprint_text()},generator.build())
        self.assertEqual(generator.OUTPUT.read_text(),generator.footprint_text())
        self.assertIn('Leshy2_R2.pretty',str(generator.OUTPUT))
        root=parse(generator.footprint_text())
        self.assertEqual([],children(root,'model'))
        pads=children(root,'pad')
        self.assertEqual(7,len(pads))
        self.assertTrue(all(p[2]=='thru_hole' for p in pads))
        expected={'A':[-2.5,7.5],'C':[0,7.5],'B':[2.5,7.5],'D':[-2.5,-7],'E':[2.5,-7]}
        for name,xy in expected.items():
            p,=[p for p in pads if p[1]==name]
            self.assertEqual(xy,list(map(float,field(p,'at'))))
            self.assertEqual(['1.1'],field(p,'drill'))
            self.assertEqual(['2','2'],field(p,'size'))
        mounts=[p for p in pads if p[1]=='MP']
        self.assertEqual([[-6.25,0],[6.25,0]],sorted(list(map(float,field(p,'at'))) for p in mounts))
        for p in mounts:
            self.assertEqual(['oval','2','4'],field(p,'drill'))
            self.assertEqual(['2.8','4.8'],field(p,'size'))

    def test_reference_rectangle_insertion_all_finished_corners(self):
        # Conditional envelope is min recommended1.5x2.6; unlike the older
        # candidate it does not enlarge the maximum hole into another hole.
        # Pitch +/- .05 contributes +/- .025 per lug only under the explicit
        # symmetric-pair assumption. Do not silently fold it into hole error.
        count=0
        worst_minimum_capsule_q=F(0)
        for w,l,sx,sy,dx,dy,px in itertools.product(map(F,['1.92','2.13']),map(F,['3.92','4.13']),(-1,1),(-1,1),(-1,1),(-1,1),(-1,1)):
            x=F('.75')*sx+F('.05')*dx+F('.025')*px
            y=F('1.3')*sy+F('.05')*dy
            q=x*x+max(abs(y)-(l-w)/2,F(0))**2
            self.assertLess(q,(w/2)**2)
            count+=1
            if w==F('1.92') and l==F('3.92'):
                worst_minimum_capsule_q=max(worst_minimum_capsule_q,q)
        e=json.loads(GEOMETRY.read_text())['engineering_pth_profile']
        self.assertEqual(128,count)
        self.assertEqual(count,e['evaluated_finished_and_position_corners'])
        self.assertEqual(F('.803125'),worst_minimum_capsule_q)
        self.assertEqual(worst_minimum_capsule_q,F(str(e['minimum_capsule_corner_q_mm2'])))
        self.assertGreater(.96-math.sqrt(float(worst_minimum_capsule_q)),.0638)
        self.assertEqual(.0638,e['minimum_capsule_radial_margin_mm_rounded_down'])
        self.assertEqual(.05,e['hole_position_allowance_each_axis_mm'])
        self.assertEqual(.025,e['lug_pitch_allowance_per_lug_x_mm'])
        self.assertEqual([.075,.05],e['combined_relative_centre_allowance_xy_mm'])
        self.assertIn('symmetric',e['pitch_boundary'])
        self.assertIn('Unknown lug-to-shaft',e['pitch_boundary'])
        self.assertGreater(.4-.13/2-math.sqrt(2)*.05,.2642)
        self.assertGreater(.45-.13/2-math.sqrt(2)*.05,.3142)

    def test_mount_pitch_perturbation_cannot_reuse_conditional_pass(self):
        # An extra .10 mm per-lug registration would exceed the current hole;
        # the calculation is sensitive to error bounds, not a blanket fit PASS.
        x=F('.75')+F('.05')+F('.125')
        q=x*x+F('.35')**2
        self.assertGreater(q,F('.96')**2)
        self.assertFalse(json.loads(GEOMETRY.read_text())['fabrication_ready'])

    def test_standard_signal_hole_and_explicit_acceptance_boundary(self):
        d=json.loads(GEOMETRY.read_text());e=d['engineering_pth_profile']
        self.assertEqual([1.02,1.23],e['signal_finished_interval_mm'])
        self.assertFalse(e['factory_precision_option_selected'])
        self.assertFalse(e['manufacturer_approved_rounded_profile'])
        self.assertFalse(d['fabrication_ready'])
        self.assertIsNone(d['exact_manufacturer_geometry']['lug_thickness_mm'])
        self.assertIn('exceeds Alps recommended upper',e['signal_upper_limit_boundary'])

    def test_native_transition_preserves_five_world_pairs(self):
        before,after=native_states()
        r=guard.verify_transition(before,after)
        self.assertEqual(5,r['unchanged_world_signal_pad_net_pairs'])
        self.assertEqual({'S1':'E','S2':'D'},r['renames'])
        self.assertFalse(r['fabrication_ready'])

    def test_reversed_commutative_mapping_does_not_hide_world_net_swap(self):
        before,after=native_states()
        d,e=[p for p in after['pads'] if p['number'] in ('D','E')]
        d['net'],e['net']=e['net'],d['net']
        with self.assertRaisesRegex(ValueError,'world signal pad/net'):guard.verify_transition(before,after)

    def test_quadrature_swap_and_one_nanometre_pad_move_are_rejected(self):
        for kind in ('swap','move'):
            before,after=native_states()
            a=next(p for p in after['pads'] if p['number']=='A')
            if kind=='swap':a['net']='/RF_31_REAR_CONTROLS/ENCODER_B'
            else:a['at_nm'][0]+=1
            with self.assertRaisesRegex(ValueError,'world signal pad/net'):guard.verify_transition(before,after)

    def test_wrong_axis_old_mount_pitch_extra_pad_and_smd_are_rejected(self):
        for kind in ('axis','pitch','extra','smd','drill'):
            before,after=native_states()
            mp=next(p for p in after['pads'] if p['number']=='MP')
            if kind=='axis':after['anchor_nm'][1]+=250_000
            elif kind=='pitch':mp['at_nm'][0]+=650_000
            elif kind=='extra':after['pads'].append(copy.deepcopy(before['pads'][-1]))
            elif kind=='smd':mp['pth']=False
            else:mp['drill_nm']=[1_900_000,3_800_000]
            with self.subTest(kind=kind),self.assertRaises(ValueError):guard.verify_transition(before,after)

    def test_plan_is_bound_to_exact_geometry_and_project(self):
        a={'feature_id':'RF-EC11-EXACT-AXIS-ENGINEERING-PTH-001',
           'source_geometry_sha256':hashlib.sha256(GEOMETRY.read_bytes()).hexdigest()}
        self.assertEqual(a,guard.verify_allowance(a,'LESHY2-RF-R2',GEOMETRY))
        for invalid,project in (({},'LESHY2-RF-R2'),(a,'LESHY2-UI-R2'),({**a,'source_geometry_sha256':'0'*64},'LESHY2-RF-R2')):
            with self.assertRaises(ValueError):guard.verify_allowance(invalid,project,GEOMETRY)

    def test_current_r2_alias_is_deliberate_without_a_b_changes(self):
        d=json.loads((ROOT/'hardware/ecad/h2-r2-contact-materialization-contract.json').read_text())
        self.assertEqual({'SW1':['E'],'SW2':['D']},d['contact_to_pad_overrides']['alps_ec11e18244au'])
        import h2_r2_symbol_footprint_ledger as ledger
        record=ledger.local_footprint_record('Leshy2_R2:EC11E18244AU-ENGINEERING-PTH')
        self.assertFalse(record['mechanics_qualified'])
        self.assertFalse(record['production_release_authorized'])
        self.assertEqual('current_exact_terminal_axes_engineered_pth_profile_mechanics_open',record['status'])

    def test_exact_shaft_and_support_overrides_are_locked_without_other_repack(self):
        d=json.loads(GEOMETRY.read_text())['local_fit_review']
        c=json.loads((ROOT/'hardware/layout/h6-r2-placement-contract.json').read_text())['placement_overrides']
        self.assertEqual(17,len(d['supports']))
        self.assertEqual({'U90','U38','U89','U134','C288','R143','C152','C240','R104','R285','R213','R221','R111','R112','R209','R180','C153'},set(d['supports']))
        self.assertEqual([71,50.25],c['encoder']['anchor_mm'])
        self.assertEqual(0,c['encoder']['rotation_deg'])
        self.assertTrue(c['encoder']['mechanical_locked'])
        self.assertNotIn('centre_mm',c['encoder'])
        for ref,row in d['supports'].items():
            v=c[row['instance']]
            self.assertEqual(row['after_anchor_mm'],v['anchor_mm'],ref)
            self.assertEqual(row['after_rotation_deg'],v['rotation_deg'],ref)
            self.assertEqual('rear-inner',v['frame'],ref)
            self.assertTrue(v['mechanical_locked'],ref)
        self.assertEqual(0,d['old_pad_track_attachments'])
        self.assertFalse(json.loads(GEOMETRY.read_text())['fabrication_ready'])

    def test_hold_locality_is_bound_to_actual_enbl_not_rf_output(self):
        c=json.loads((ROOT/'hardware/layout/h6-r2-placement-contract.json').read_text())
        pairs=[p for p in c['placement_policy']['critical_pad_pairs'] if p['canonical_net']=='VOICE_V_EVIDENCE_HOLD']
        got={(p['first_instance'],p['first_pad_number'],p['second_instance'],p['second_pad_number']):p['maximum_distance_mm'] for p in pairs}
        self.assertEqual({('voice_v_evidence_hold_cap','1','det_voice_v','2'):3,
                          ('voice_v_evidence_hold_diode','3','voice_v_evidence_hold_cap','1'):8,
                          ('voice_v_evidence_hold_pulldown','1','det_voice_v','2'):10},got)
        for p in pairs:self.assertEqual('LESHY2-RF-R2',p['project'])

    def test_signals_coaxial_comparison_is_not_position_corner_proof(self):
        e=json.loads(GEOMETRY.read_text())['engineering_pth_profile']
        self.assertGreater(.5+math.hypot(.05,.05),.51)
        self.assertFalse(e['signal_position_corner']['full_reference_aperture_containment'])
        self.assertFalse(e['signal_position_corner']['actual_terminal_nonfit_proven'])
        self.assertIn('coaxial',e['signal_upper_limit_boundary'])

    def test_filter_loop_and_assembly_requirements_are_explicit(self):
        d=json.loads(GEOMETRY.read_text());r=d['assembly_requirements']
        self.assertTrue(r['both_metal_mounting_lugs_solder_required'])
        self.assertTrue(r['body_seated_flush_and_level'])
        self.assertFalse(r['washing_permitted'])
        self.assertFalse(r['three_dimensional_clearance_verified'])
        self.assertFalse(r['solder_fill_or_torque_qualified'])
        self.assertAlmostEqual(3.5-1.6,r['inward_protrusion_nominal_on_1p6mm_pcb_mm'])
        self.assertIn('Solder BOTH metal mounting lugs',generator.footprint_text())
        c=json.loads((ROOT/'hardware/layout/h6-r2-placement-contract.json').read_text())
        pairs=[p for p in c['placement_policy']['critical_pad_pairs'] if p['first_instance']=='voice_v_detector_filter']
        self.assertEqual({('1','4','VOICE_V_DETECT_FILTER'),('2','6','VOICE_V_DETECT_V')},
                         {(p['first_pad_number'],p['second_pad_number'],p['canonical_net']) for p in pairs})
        self.assertTrue(all(p['maximum_distance_mm']==3 for p in pairs))


if __name__=='__main__':unittest.main()
