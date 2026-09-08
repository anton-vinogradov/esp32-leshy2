"""No generic drawing admission may hide in the finite speaker-body stage."""
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'hardware/layout'))
try:
    import pcbnew
except ImportError:
    pcbnew=None
if pcbnew is not None:
    import h6_r2_stage_placement_update as target
    import h6_r2_speaker_fit as body


@unittest.skipUnless(pcbnew,'KiCad runtime required')
class SpeakerStageTests(unittest.TestCase):
    def setUp(self):
        class Grid:
            def add(self,*args):pass
        spec=json.loads(target.placement.SPEAKER_BODY_PATH.read_text())
        board=pcbnew.BOARD()
        body.add_speaker_assembly_geometry(board,'LESHY2-UI-R2',{'mechanical':{'speaker_body':spec}},{'B.Cu':Grid()},pcbnew)
        text=target.placement.board_bytes('test-speaker',board).decode()
        self.native_text=text
        self.graphs=[f for head,f in target.forms(text) if head.startswith('gr_')]
        self.before='(kicad_pcb)'
        self.after=self.pcb(self.graphs)
        self.allowance={'feature_id':'H6-R2-SPEAKER-BODY-001','source_sha256':target.sha(target.placement.SPEAKER_BODY_PATH.read_bytes()),'helper_sha256':target.sha(target.placement.SPEAKER_HELPER_PATH.read_bytes())}

    @staticmethod
    def pcb(graphs):return '(kicad_pcb\n'+'\n'.join(graphs)+'\n)'
    def check(self,before=None,after=None,allowance=None,project='LESHY2-UI-R2',refs=None):
        return target.reviewed_speaker_graphics(before or self.before,after or self.after,allowance or self.allowance,project,refs or ['C54'])

    def test_exact_native_coordinates_layer_and_text(self):
        self.assertEqual(len(self.check()),5)
        board=target.load_board_bytes(self.native_text.encode(),'speaker.kicad_pcb')
        lines=[x for x in board.GetDrawings() if isinstance(x,pcbnew.PCB_SHAPE)]
        xy=lambda pt:(round(pcbnew.ToMM(pt.x),6),round(pcbnew.ToMM(pt.y),6))
        self.assertEqual({(xy(x.GetStart()),xy(x.GetEnd())) for x in lines},
            {((9.6,111.9),(21.8,111.9)),((21.8,111.9),(21.8,136.1)),((21.8,136.1),(9.6,136.1)),((9.6,136.1),(9.6,111.9))})
        self.assertTrue(all(x.GetLayer()==pcbnew.B_Fab and x.GetWidth()==100000 for x in lines))
        txt=next(x for x in board.GetDrawings() if isinstance(x,pcbnew.PCB_TEXT))
        self.assertEqual((xy(txt.GetPosition()),txt.GetText(),txt.GetTextAngleDegrees(),txt.IsMirrored()),((15.7,124.0),'SPEAKER / ASSEMBLY',90,True))
        self.assertEqual(body.check_native_speaker_geometry(board,'LESHY2-UI-R2',pcbnew)['observed_count'],5)

    def test_native_missing_moved_mirrored_and_extra_body_rejected(self):
        for mutation in ('missing','move','mirror','duplicate','wrong_board'):
            board=target.load_board_bytes(self.native_text.encode(),'speaker.kicad_pcb')
            txt=next(x for x in board.GetDrawings() if isinstance(x,pcbnew.PCB_TEXT))
            if mutation=='missing':board.Remove(txt)
            elif mutation=='move':txt.SetPosition(pcbnew.VECTOR2I(15700000,124000001))
            elif mutation=='mirror':txt.SetMirrored(False)
            elif mutation=='duplicate':board.Add(txt.Duplicate())
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):
                body.check_native_speaker_geometry(board,'LESHY2-RF-R2' if mutation=='wrong_board' else 'LESHY2-UI-R2',pcbnew)

    def test_legitimate_RF_port_label_not_mistaken_for_assembly_body(self):
        board=pcbnew.BOARD();text=pcbnew.PCB_TEXT(board)
        text.SetText('SPEAKER');text.SetLayer(pcbnew.F_SilkS);board.Add(text)
        self.assertEqual(body.check_native_speaker_geometry(board,'LESHY2-RF-R2',pcbnew)['status'],'not_applicable')

    def test_hash_or_project_or_scope_mismatch_fails(self):
        for key in self.allowance:
            bad=copy.deepcopy(self.allowance);bad[key]='wrong'
            with self.subTest(key=key),self.assertRaises(ValueError):self.check(allowance=bad)
        with self.assertRaises(ValueError):self.check(project='LESHY2-RF-R2')
        with self.assertRaises(ValueError):self.check(refs=['C54','C55'])

    def test_removed_extra_duplicate_or_shifted_object_rejected(self):
        variants=[self.graphs[:-1], self.graphs+self.graphs[:1],
                  self.graphs+['(gr_line (start 1 1) (end 2 2) (stroke (width 0.1) (type default)) (layer "B.Fab"))'],
                  [x.replace('9.6','9.7') for x in self.graphs],
                  [x.replace('SPEAKER / ASSEMBLY','SPEAKER') for x in self.graphs]]
        for graphs in variants:
            with self.subTest(graphs=graphs),self.assertRaises(ValueError):self.check(after=self.pcb(graphs))

    def test_replacing_or_duplicating_existing_body_rejected(self):
        with self.assertRaises(ValueError):self.check(before=self.after)
        with self.assertRaises(ValueError):self.check(before=self.pcb(self.graphs[:1]))

    def test_other_Bfab_removal_rejected(self):
        old='(gr_line (start 1 1) (end 2 2) (stroke (width 0.1) (type default)) (layer "B.Fab"))'
        with self.assertRaises(ValueError):self.check(before=self.pcb([old]))
        self.assertEqual(len(self.check(before=self.pcb([old]),after=self.pcb([old]+self.graphs))),5)

    def test_source_snapshot_contains_both_inputs(self):
        source=ROOT/'hardware/ecad/kicad/LESHY2-UI-R2/LESHY2-UI-R2.kicad_pcb'
        snap=target.input_snapshot(source)
        for path in (target.placement.SPEAKER_BODY_PATH,target.placement.SPEAKER_HELPER_PATH):
            self.assertEqual(snap[str(path.resolve())],target.sha(path.read_bytes()))


if __name__=='__main__':unittest.main()
