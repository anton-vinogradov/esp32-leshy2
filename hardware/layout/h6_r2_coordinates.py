"""Explicit assembly-world to native-PCB XY boundary for H1 placement seeds.

Both native boards are viewed from their own exterior. H1 world coordinates
are viewed from the UI exterior. Frame names select the PCB/face; they do not
make a world_bbox an exterior-local box. Native overrides, antenna anchors and
frozen positions have already crossed this boundary and must not cross again.
"""

from __future__ import annotations


UI_FRAMES = frozenset({"front-outer", "ui-inner", "ui-outer-face"})
RF_FRAMES = frozenset({"rear-outer", "rf-inner", "rear-inner", "rf-outer-face", "rf-outer-right-edge"})


def world_bbox_to_native(frame: str, box: dict, board_width: float) -> dict:
    if frame not in UI_FRAMES | RF_FRAMES:
        raise ValueError(f"unknown assembly-world seed frame: {frame}")
    result = {axis: list(values) for axis, values in box.items()}
    if frame in RF_FRAMES:
        result["x"] = [round(board_width - box["x"][1], 6),
                       round(board_width - box["x"][0], 6)]
    return result
