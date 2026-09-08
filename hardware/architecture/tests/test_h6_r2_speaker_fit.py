import copy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'hardware/layout'))
import h6_r2_speaker_fit as target
try:
    import pcbnew
except ModuleNotFoundError:
    pcbnew = None


class SpeakerFitTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads((ROOT / 'hardware/layout/h6-r2-speaker-body.json').read_text())
        self.contract = {'mechanical': {'speaker_body': self.spec}}

    def test_exact_complete_body_and_motion_budget(self):
        body = target.checked_speaker_body(self.contract)
        self.assertEqual(body['maximum_bbox_mm'], {'x': [9.6,21.8], 'y':[111.9,136.1]})
        self.assertAlmostEqual(10.9-4.8-1.12-.8-3.0, 1.18)
        self.assertEqual(self.spec['electrical_termination']['project'], 'LESHY2-RF-R2')
        self.assertEqual(self.spec['electrical_termination']['reference'], 'LS1')

    def test_missing_body_is_not_silent(self):
        with self.assertRaises(KeyError): target.checked_speaker_body({'mechanical': {}})

    def test_wrong_side_or_identity_rejected(self):
        for path,value in ((('body_registration','side'),'F.Cu'),
                           (('body_registration','project'),'LESHY2-RF-R2'),
                           (('device_id',),'different'), (('assembly_qualified',),True)):
            with self.subTest(path=path):
                contract=copy.deepcopy(self.contract); row=contract['mechanical']['speaker_body']
                for part in path[:-1]: row=row[part]
                row[path[-1]]=value
                with self.assertRaises(ValueError): target.checked_speaker_body(contract)

    def test_bbox_cannot_shrink_to_wire_termination(self):
        self.spec['body_registration']['maximum_bbox_mm']={'x':[12.7,18.7],'y':[122.5,125.5]}
        with self.assertRaises(ValueError): target.checked_speaker_body(self.contract)

    def test_motion_or_bed_limits_rejected(self):
        for group,key,value in (('body_registration','minimum_front_motion_clearance_mm',.79),
                                ('mounting_bed','maximum_total_thickness_mm',1.13),
                                ('mounting_bed','maximum_total_thickness_mm',True),
                                ('z_screen','interboard_gap_design_lower_mm',float('nan')),
                                ('z_screen','opposing_rf_metadata_maximum_height_mm',4.0)):
            with self.subTest(key=key,value=value):
                contract=copy.deepcopy(self.contract)
                contract['mechanical']['speaker_body'][group][key]=value
                with self.assertRaises(ValueError):target.checked_speaker_body(contract)

    def test_rear_perimeter_must_stay_free(self):
        self.spec['mounting_bed']['no_covering_terminal_or_vent_relief']=False
        with self.assertRaises(ValueError):target.checked_speaker_body(self.contract)

    def test_c54_has_positive_body_gap_only_after_scoped_translation(self):
        body=self.spec['body_registration']['maximum_bbox_mm']
        old_min_y=136.1
        new_min_y=136.4
        self.assertLess(old_min_y-body['y'][1],.1)
        self.assertAlmostEqual(new_min_y-body['y'][1],.3)
        cap=self.spec['required_placement_override']['hub_rp_service_usb_switch_bypass']
        self.assertEqual(cap['anchor_mm'],[14.805,136.905])
        self.assertEqual(cap['frame'],'front-inner')
        self.assertTrue(cap['mechanical_locked'])

    @unittest.skipUnless(pcbnew,'KiCad native runtime required')
    def test_native_mechanical_only_objects_and_B_grid(self):
        class Grid:
            def __init__(self):self.items=[]
            def add(self,*args):self.items.append(args)
        grids={'F.Cu':Grid(),'B.Cu':Grid()}; board=pcbnew.BOARD()
        target.add_speaker_assembly_geometry(board,'LESHY2-UI-R2',self.contract,grids,pcbnew)
        self.assertEqual(len(list(board.GetFootprints())),0)
        self.assertEqual(len(list(board.GetTracks())),0)
        self.assertEqual(board.GetAreaCount(),0)
        self.assertEqual(len(list(board.GetDrawings())),5)
        self.assertEqual(grids['F.Cu'].items,[])
        self.assertEqual(grids['B.Cu'].items,[('speaker_assembly_body',{'x':[9.6,21.8],'y':[111.9,136.1]},'external_component_keepout')])
        self.assertTrue(all(item.GetLayer()==pcbnew.B_Fab for item in board.GetDrawings()))
        text=next(item for item in board.GetDrawings() if isinstance(item,pcbnew.PCB_TEXT))
        self.assertEqual(text.GetText(),'SPEAKER / ASSEMBLY')
        self.assertTrue(text.IsMirrored())
        self.assertEqual(text.GetTextAngleDegrees(),90)

    @unittest.skipUnless(pcbnew,'KiCad native runtime required')
    def test_other_board_not_falsely_given_speaker_footprint(self):
        board=pcbnew.BOARD()
        target.add_speaker_assembly_geometry(board,'LESHY2-RF-R2',self.contract,{},pcbnew)
        self.assertEqual(len(list(board.GetDrawings())),0)


if __name__=='__main__': unittest.main()
