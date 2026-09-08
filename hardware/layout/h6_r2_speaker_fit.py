"""Finite AS02404PO mechanical registration, not a PCB footprint or acoustic PASS.

The caller inserts the separately loaded authoritative speaker JSON under an
in-memory mechanical.speaker_body key. It must hash that input and this helper;
no side input is loaded here and no persisted duplicate of the spec is needed.
"""
import math
import json
from collections import Counter
from pathlib import Path


def checked_speaker_body(contract):
    spec = contract['mechanical']['speaker_body']
    body, bed, screen = (spec[k] for k in ('body_registration', 'mounting_bed', 'z_screen'))
    if (spec['device_id'] != 'pui_as02404po' or spec['mpn'] != 'PUI Audio AS02404PO'
            or body['project'] != 'LESHY2-UI-R2' or body['side'] != 'B.Cu'
            or spec['assembly_qualified'] is not False or spec['fabrication_authorized'] is not False):
        raise ValueError('Unexpected speaker identity/face or unsupported assembly authority')
    for key, expected in (('nominal_size_xy_mm', [12.0, 24.0]),
                          ('maximum_size_xy_mm', [12.2, 24.2]),
                          ('centre_mm', [15.7, 124.0])):
        if body[key] != expected:
            raise ValueError('Review the finite speaker body datum before changing ' + key)
    def positive(value):
        return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value) and value > 0
    numeric = [body['maximum_body_thickness_mm'], body['minimum_front_motion_clearance_mm'],
               bed['maximum_total_thickness_mm'], screen['interboard_gap_design_lower_mm'],
               screen['opposing_rf_metadata_maximum_height_mm'], screen['remaining_after_front_motion_mm']]
    if not all(positive(value) for value in numeric):
        raise ValueError('Speaker dimensions and budget must be finite positive numbers')
    if (screen['interboard_gap_design_lower_mm'] != 10.9
            or screen['opposing_rf_metadata_maximum_height_mm'] != 3.0):
        raise ValueError('Review current opposing-body/source geometry before changing the finite Z screen')
    if body['maximum_body_thickness_mm'] != 4.8 or body['minimum_front_motion_clearance_mm'] < 0.8:
        raise ValueError('Speaker body tolerance and front excursion must not be reduced')
    for index, axis in enumerate(('x', 'y')):
        center, size = body['centre_mm'][index], body['maximum_size_xy_mm'][index]
        expected = [round(center-size/2, 6), round(center+size/2, 6)]
        if body['maximum_bbox_mm'][axis] != expected:
            raise ValueError('Speaker keepout must represent the complete maximum body')
    depth = bed['maximum_total_thickness_mm']
    if isinstance(depth, bool) or not isinstance(depth, (int, float)) or not math.isfinite(depth) or not 0 < depth <= 1.12:
        raise ValueError('PSA/bed exceeds the reviewed geometric ceiling')
    if (bed['proposed_patch_size_mm'] != [7.0, 16.0] or bed['no_wraparound'] is not True
            or bed['no_covering_terminal_or_vent_relief'] is not True):
        raise ValueError('Review the rear fixed-surface PSA patch; do not cover the perimeter')
    remaining = (screen['interboard_gap_design_lower_mm'] - body['maximum_body_thickness_mm']
                 - depth - body['minimum_front_motion_clearance_mm']
                 - screen['opposing_rf_metadata_maximum_height_mm'])
    if remaining <= 1.0 or abs(remaining-screen['remaining_after_front_motion_mm']) > 1e-8:
        raise ValueError('Speaker provisional Z budget no longer retains the reviewed margin')
    return body


def add_speaker_assembly_geometry(board, project, contract, grids, pcbnew):
    """Add B-only placement reservation and five B.Fab drawing objects.

    No footprint, net, pad, drill, copper keepout or BOM item is created. Actual
    speaker wire termination remains RF LS1. The separate body must be rendered.
    """
    body = checked_speaker_body(contract)
    if project != body['project']:
        return
    rect = body['maximum_bbox_mm']
    grids['B.Cu'].add('speaker_assembly_body', rect, 'external_component_keepout')
    point = lambda x, y: pcbnew.VECTOR2I(round(x*1e6), round(y*1e6))
    x0, x1 = rect['x']; y0, y1 = rect['y']
    corners = ((x0,y0),(x1,y0),(x1,y1),(x0,y1))
    for i in range(4):
        item = pcbnew.PCB_SHAPE(board)
        item.SetShape(pcbnew.SHAPE_T_SEGMENT)
        item.SetStart(point(*corners[i])); item.SetEnd(point(*corners[(i+1)%4]))
        item.SetWidth(round(.10*1e6)); item.SetLayer(pcbnew.B_Fab)
        board.Add(item)
    text = pcbnew.PCB_TEXT(board)
    text.SetText('SPEAKER / ASSEMBLY')
    text.SetPosition(point(*body['centre_mm']))
    text.SetLayer(pcbnew.B_Fab)
    text.SetMirrored(True)
    text.SetTextAngle(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
    text.SetTextSize(point(1,1)); text.SetTextThickness(round(.15*1e6))
    text.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
    board.Add(text)


def native_speaker_geometry_key(item, pcbnew):
    """Exact native geometry and text presentation, excluding object UUID only."""
    xy = lambda point: (point.x, point.y)
    if isinstance(item, pcbnew.PCB_TEXT):
        if item.GetFont() is not None:
            raise ValueError('Speaker assembly label requires the default native stroke font')
        return ('text', item.GetText(), xy(item.GetPosition()), xy(item.GetTextSize()),
                item.GetTextThickness(), item.GetTextAngleDegrees(), item.IsMirrored(),
                item.IsVisible(), item.IsBold(), item.IsItalic(), item.GetLayer(),
                int(item.GetHorizJustify()), int(item.GetVertJustify()))
    if isinstance(item, pcbnew.PCB_SHAPE) and item.GetShape() == pcbnew.SHAPE_T_SEGMENT:
        return ('segment', xy(item.GetStart()), xy(item.GetEnd()), item.GetWidth(), item.GetLayer())
    raise ValueError('Unsupported native object in the finite speaker body registration')


def check_native_speaker_geometry(board, project, pcbnew, spec=None):
    """Verify exact five UI B.Fab objects; no solder, acoustic or 3D authority.

    Callers must freshness-bind this module and the sole JSON source. The
    explicit optional spec is for controlled callers/tests, not a second file.
    Other remote assembly drawings are outside this finite feature, but any
    extra object inside its rectangle or duplicate/misplaced label is rejected.
    """
    if spec is None:
        spec = json.loads(Path(__file__).with_name('h6-r2-speaker-body.json').read_text())
    contract = {'mechanical': {'speaker_body': spec}}
    body = checked_speaker_body(contract)
    labels = [item for item in board.GetDrawings() if isinstance(item, pcbnew.PCB_TEXT)
              and item.GetText() == 'SPEAKER / ASSEMBLY']
    if project != body['project']:
        if labels:
            raise ValueError('Speaker assembly body label is on the wrong board')
        return {'status': 'not_applicable', 'required_count': 0, 'observed_count': 0}

    class Grid:
        def add(self, *args):
            pass

    reference = pcbnew.BOARD()
    add_speaker_assembly_geometry(reference, project, contract, {'B.Cu': Grid()}, pcbnew)
    expected = Counter(native_speaker_geometry_key(item, pcbnew) for item in reference.GetDrawings())
    rect = body['maximum_bbox_mm']
    def in_region(item):
        box = item.GetBoundingBox()
        return (box.GetLeft() <= round(rect['x'][1]*1e6)
                and box.GetRight() >= round(rect['x'][0]*1e6)
                and box.GetTop() <= round(rect['y'][1]*1e6)
                and box.GetBottom() >= round(rect['y'][0]*1e6))
    observed_items = [item for item in board.GetDrawings()
                      if (item.GetLayer() == pcbnew.B_Fab and in_region(item))
                      or (isinstance(item, pcbnew.PCB_TEXT) and item.GetText() == 'SPEAKER / ASSEMBLY')]
    observed = Counter(native_speaker_geometry_key(item, pcbnew) for item in observed_items)
    if len(expected) != 5 or sum(expected.values()) != 5 or observed != expected:
        raise ValueError('Native speaker body must contain exactly the reviewed four B.Fab lines and mirrored label')
    return {'status': 'pass_scoped_native_registration', 'required_count': 5,
            'observed_count': 5, 'assembly_qualified': False, 'maximum_bbox_mm': rect}
