"""Exact, project-selected microSD finger recess; no manufacturer fit waiver.

Pure geometry is shared by the seed writer and the tightly scoped stage guard.
The seven primitives replace one bottom-edge line, not the whole Edge.Cuts layer.
"""

import math

FEATURE_ID = "UI-MICROSD-RECESS-001"
PROJECT = "LESHY2-UI-R2"


def feature(contract, project):
    row = contract["mechanical"].get("microsd_recess")
    if row is None or project != PROJECT:
        return None
    if row["id"] != FEATURE_ID or row["board"] != PROJECT:
        raise ValueError("unsupported microSD recess identity")
    board = contract["board"]
    if (board["width_mm"], board["height_mm"], board["corner_radius_mm"]) != (80, 150, 2):
        raise ValueError("microSD recess is reviewed only for the 80 x 150 board")
    x0, x1 = row["bbox_mm"]["x"]
    y0, y1 = row["bbox_mm"]["y"]
    radius = row["internal_radius_mm"]
    values = (x0, x1, y0, y1, radius, row["card_axis_x_mm"])
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in values):
        raise ValueError("finite numeric microSD geometry required")
    if (abs(x1 - x0 - 10) > 1e-9 or abs(y0 - 148.8) > 1e-9 or y1 != 150
            or abs((x0 + x1) / 2 - row["card_axis_x_mm"]) > 1e-9
            or not 0.6 <= radius <= y1 - y0 or not 2 < x0 < x1 < 78):
        raise ValueError("unreviewed microSD notch dimensions or radius")
    sd = contract["placement_overrides"]["sd"]
    if (sd["frame"] != "ui-inner" or sd["rotation_deg"] != 180
            or sd.get("mechanical_locked") is not True
            or abs(sd["anchor_mm"][0] + 0.425 - row["card_axis_x_mm"]) > 1e-9
            or abs(sd["anchor_mm"][1] + 8.125 - row["shell_mouth_y_mm"]) > 1e-9):
        raise ValueError("microSD mouth/card axis is not bound to its native pose")
    if (row["positions_are_nominal_not_tolerance_bounds"] is not True
            or row["manufacturer_mandates_pcb_notch"] is not False):
        raise ValueError("microSD reference dimensions are not qualified tolerance bounds")
    return row


def bottom_edge_primitives(contract, project):
    """Clockwise outer contour: right to left across the lower board edge."""
    board = contract["board"]
    width, height, corner = (board[k] for k in ("width_mm", "height_mm", "corner_radius_mm"))
    row = feature(contract, project)
    if row is None:
        return [("gr_line", (width - corner, height), (corner, height))]
    x0, x1 = row["bbox_mm"]["x"]
    y0, _ = row["bbox_mm"]["y"]
    r = row["internal_radius_mm"]
    k = r / math.sqrt(2)
    return [
        ("gr_line", (width - corner, height), (x1, height)),
        ("gr_line", (x1, height), (x1, y0 + r)),
        ("gr_arc", (x1, y0 + r), (x1-r+k, y0+r-k), (x1-r, y0)),
        ("gr_line", (x1-r, y0), (x0+r, y0)),
        ("gr_arc", (x0+r, y0), (x0+r-k, y0+r-k), (x0, y0+r)),
        ("gr_line", (x0, y0+r), (x0, height)),
        ("gr_line", (x0, height), (corner, height)),
    ]
