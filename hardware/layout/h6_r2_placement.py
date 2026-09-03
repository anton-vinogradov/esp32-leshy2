#!/usr/bin/env python3
"""Generate the first exact-footprint H6 placement for both R2 boards.

Run this script with KiCad's bundled Python 3.9 runtime.  The board writer uses
pcbnew only for native object construction; placement policy and its audit stay
plain JSON so the normal repository test suite can validate the result without
loading KiCad.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
import tempfile
import uuid
from collections import Counter, defaultdict
from pathlib import Path

try:
    import pcbnew  # type: ignore
except ModuleNotFoundError as exc:  # pragma: no cover - exercised by the wrapper command
    raise SystemExit(
        "pcbnew is unavailable; run with "
        "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/"
        "Versions/3.9/bin/python3"
    ) from exc


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "hardware/layout/h6-r2-placement-contract.json"
PLACEMENT_PATH = ROOT / "hardware/product-design/h1-r2-placement.json"
COORDINATE_PATH = ROOT / "hardware/product-design/generated/H1-unified-coordinate-table.json"
INSTANCE_PATH = ROOT / "hardware/ecad/generated/H2-R2-native-instance-ledger.json"
NET_PATH = ROOT / "hardware/ecad/generated/H2-R2-native-net-ledger.json"
SYMBOL_PATH = ROOT / "hardware/ecad/generated/H2-R2-controlled-symbol-library.json"
NET_BINDING_PATH = ROOT / "hardware/layout/generated/H6-R2-kicad-net-bindings.json"
AUDIT_PATH = ROOT / "hardware/layout/generated/H6-R2-placement-audit.json"
SVG_PATH = ROOT / "docs/images/h6-r2-exact-placement.svg"
KICAD_FOOTPRINT_ROOT = Path(
    "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
)
UUID_NAMESPACE = uuid.UUID("2ffbe908-136d-4ffd-b1f1-c20a0e8600e2")
SCHEMATIC_UUID_NAMESPACE = uuid.UUID("55d78bc6-bb67-4c34-aa29-29952908dcf4")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def stable_uuid(scope: str) -> str:
    return str(uuid.uuid5(UUID_NAMESPACE, scope))


def schematic_uuid(scope: str) -> str:
    return str(uuid.uuid5(SCHEMATIC_UUID_NAMESPACE, scope))


def natural_key(value: str) -> tuple:
    return tuple(int(part) if part.isdigit() else part for part in re.split(r"(\d+)", value))


def mm(value: float) -> int:
    return pcbnew.FromMM(value)


def point(x: float, y: float):
    return pcbnew.VECTOR2I_MM(x, y)


def box_mm(box) -> dict[str, list[float]]:
    return {
        "x": [round(pcbnew.ToMM(box.GetX()), 4), round(pcbnew.ToMM(box.GetRight()), 4)],
        "y": [round(pcbnew.ToMM(box.GetY()), 4), round(pcbnew.ToMM(box.GetBottom()), 4)],
    }


def rect_centre(rect: dict) -> tuple[float, float]:
    return (
        (rect["x"][0] + rect["x"][1]) / 2,
        (rect["y"][0] + rect["y"][1]) / 2,
    )


def rect_size(rect: dict) -> tuple[float, float]:
    return rect["x"][1] - rect["x"][0], rect["y"][1] - rect["y"][0]


def rectangles_overlap(a: dict, b: dict, margin: float = 0.0) -> bool:
    return (
        a["x"][0] < b["x"][1] + margin
        and a["x"][1] + margin > b["x"][0]
        and a["y"][0] < b["y"][1] + margin
        and a["y"][1] + margin > b["y"][0]
    )


class OccupancyGrid:
    """Fast exact-enough rectangle occupancy on the contract grid."""

    def __init__(self, width: float, height: float, step: float, gap: float):
        self.width = width
        self.height = height
        self.step = step
        self.gap = gap
        self.columns = int(math.ceil(width / step))
        self.rows = int(math.ceil(height / step))
        self.bits = [0] * self.rows
        self.items: list[dict] = []

    def indices(self, rect: dict, *, add_gap: bool = True) -> tuple[int, int, int, int]:
        gap = self.gap if add_gap else 0.0
        x0 = math.floor((rect["x"][0] - gap) / self.step)
        x1 = math.ceil((rect["x"][1] + gap) / self.step)
        y0 = math.floor((rect["y"][0] - gap) / self.step)
        y1 = math.ceil((rect["y"][1] + gap) / self.step)
        return x0, x1, y0, y1

    def inside(self, rect: dict, edge: float = 0.0) -> bool:
        return (
            rect["x"][0] >= edge
            and rect["y"][0] >= edge
            and rect["x"][1] <= self.width - edge
            and rect["y"][1] <= self.height - edge
        )

    def conflicts(self, rect: dict, *, allow_outside: bool = False) -> list[dict]:
        if not allow_outside and not self.inside(rect):
            return [{"id": "BOARD_EDGE", "kind": "boundary", "rect": rect}]
        x0, x1, y0, y1 = self.indices(rect)
        x0c, x1c = max(0, x0), min(self.columns, x1)
        y0c, y1c = max(0, y0), min(self.rows, y1)
        if x0c >= x1c or y0c >= y1c:
            return [] if allow_outside else [{"id": "BOARD_EDGE", "kind": "boundary", "rect": rect}]
        mask = ((1 << (x1c - x0c)) - 1) << x0c
        if not any(self.bits[row] & mask for row in range(y0c, y1c)):
            return []
        return [item for item in self.items if rectangles_overlap(rect, item["rect"], self.gap)]

    def is_free(self, rect: dict) -> bool:
        if not self.inside(rect):
            return False
        x0, x1, y0, y1 = self.indices(rect)
        if x0 < 0 or y0 < 0 or x1 > self.columns or y1 > self.rows:
            return False
        mask = ((1 << (x1 - x0)) - 1) << x0
        return not any(self.bits[row] & mask for row in range(y0, y1))

    def add(self, item_id: str, rect: dict, kind: str) -> None:
        x0, x1, y0, y1 = self.indices(rect)
        x0c, x1c = max(0, x0), min(self.columns, x1)
        y0c, y1c = max(0, y0), min(self.rows, y1)
        if x0c < x1c and y0c < y1c:
            mask = ((1 << (x1c - x0c)) - 1) << x0c
            for row in range(y0c, y1c):
                self.bits[row] |= mask
        self.items.append({"id": item_id, "kind": kind, "rect": rect})


def footprint_library(footprint: str) -> tuple[str, str]:
    library, name = footprint.split(":", 1)
    if library == "Leshy2":
        return str(ROOT / "hardware/ecad/libraries/Leshy2.pretty"), name
    if library == "Leshy2_R2":
        return str(ROOT / "hardware/ecad/libraries/Leshy2_R2.pretty"), name
    return str(KICAD_FOOTPRINT_ROOT / f"{library}.pretty"), name


def footprint_rect(fp, side: str) -> dict:
    # The NFC pickup is a routed board feature, not a component courtyard.  Its
    # Dwgs.User reserve must still drive placement centring after the deliberate
    # removal of the misleading F.CrtYd rectangle.
    if str(fp.GetFPID().GetLibItemName()) == "NFC_Pickup_Loop_R2":
        return {"x": [-36.0, 36.0], "y": [-11.2, 11.2]}
    courtyard_layer = pcbnew.B_CrtYd if side == "B.Cu" else pcbnew.F_CrtYd
    courtyard = fp.GetCourtyard(courtyard_layer)
    box = courtyard.BBox()
    if box.GetWidth() <= 0 or box.GetHeight() <= 0:
        box = fp.GetBoundingBox(False)
    return box_mm(box)


def footprint_pose(fp, side: str, rotation: float) -> dict:
    fp.SetPosition(point(0.0, 0.0))
    fp.SetOrientationDegrees(rotation)
    local = footprint_rect(fp, side)
    opposite_layer = pcbnew.F_Cu if side == "B.Cu" else pcbnew.B_Cu
    opposite_pads = [
        pad
        for pad in fp.Pads()
        if pad.IsOnLayer(opposite_layer) or pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH
    ]
    cross_rects = sorted(
        (box_mm(pad.GetBoundingBox()) for pad in opposite_pads),
        key=lambda rect: (rect["y"][0], rect["x"][0], rect["y"][1], rect["x"][1]),
    )
    cross_body_rects = sorted(
        (
            box_mm(pad.GetBoundingBox())
            for pad in opposite_pads
            if pad.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH
        ),
        key=lambda rect: (rect["y"][0], rect["x"][0], rect["y"][1], rect["x"][1]),
    )
    return {
        "rotation": rotation,
        "local_rect": local,
        "local_centre": rect_centre(local),
        "size": rect_size(local),
        "cross_rects": cross_rects,
        "cross_body_rects": cross_body_rects,
    }


def rect_at_centre(pose: dict, centre: tuple[float, float]) -> dict:
    width, height = pose["size"]
    return {
        "x": [centre[0] - width / 2, centre[0] + width / 2],
        "y": [centre[1] - height / 2, centre[1] + height / 2],
    }


def cross_rects_at_centre(
    pose: dict,
    centre: tuple[float, float],
    key: str = "cross_rects",
) -> list[dict]:
    """Translate copper exposed on the opposite face with the same footprint anchor."""
    offset_x = centre[0] - pose["local_centre"][0]
    offset_y = centre[1] - pose["local_centre"][1]
    return [
        {
            "x": [local["x"][0] + offset_x, local["x"][1] + offset_x],
            "y": [local["y"][0] + offset_y, local["y"][1] + offset_y],
        }
        for local in pose[key]
    ]


def cross_rects_at_anchor(
    pose: dict,
    anchor: tuple[float, float],
    key: str = "cross_rects",
) -> list[dict]:
    return [
        {
            "x": [local["x"][0] + anchor[0], local["x"][1] + anchor[0]],
            "y": [local["y"][0] + anchor[1], local["y"][1] + anchor[1]],
        }
        for local in pose[key]
    ]


def apply_centre(fp, pose: dict, centre: tuple[float, float]) -> dict:
    fp.SetOrientationDegrees(pose["rotation"])
    offset_x, offset_y = pose["local_centre"]
    fp.SetPosition(point(centre[0] - offset_x, centre[1] - offset_y))
    return rect_at_centre(pose, centre)


def rect_at_anchor(pose: dict, anchor: tuple[float, float]) -> dict:
    local = pose["local_rect"]
    return {
        "x": [local["x"][0] + anchor[0], local["x"][1] + anchor[0]],
        "y": [local["y"][0] + anchor[1], local["y"][1] + anchor[1]],
    }


def apply_anchor(fp, pose: dict, anchor: tuple[float, float]) -> dict:
    fp.SetOrientationDegrees(pose["rotation"])
    fp.SetPosition(point(*anchor))
    return rect_at_anchor(pose, anchor)


def add_segment(board, layer: int, start: tuple[float, float], end: tuple[float, float], width: float) -> None:
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_SEGMENT)
    shape.SetLayer(layer)
    shape.SetWidth(mm(width))
    shape.SetStart(point(*start))
    shape.SetEnd(point(*end))
    board.Add(shape)


def add_arc(
    board,
    layer: int,
    start: tuple[float, float],
    mid: tuple[float, float],
    end: tuple[float, float],
    width: float,
) -> None:
    shape = pcbnew.PCB_SHAPE(board)
    shape.SetShape(pcbnew.SHAPE_T_ARC)
    shape.SetLayer(layer)
    shape.SetWidth(mm(width))
    shape.SetArcGeometry(point(*start), point(*mid), point(*end))
    board.Add(shape)


def add_rounded_outline(board, width: float, height: float, radius: float) -> None:
    line = 0.05
    k = radius / math.sqrt(2)
    add_segment(board, pcbnew.Edge_Cuts, (radius, 0), (width - radius, 0), line)
    add_arc(board, pcbnew.Edge_Cuts, (width - radius, 0), (width - radius + k, radius - k), (width, radius), line)
    add_segment(board, pcbnew.Edge_Cuts, (width, radius), (width, height - radius), line)
    add_arc(board, pcbnew.Edge_Cuts, (width, height - radius), (width - radius + k, height - radius + k), (width - radius, height), line)
    add_segment(board, pcbnew.Edge_Cuts, (width - radius, height), (radius, height), line)
    add_arc(board, pcbnew.Edge_Cuts, (radius, height), (radius - k, height - radius + k), (0, height - radius), line)
    add_segment(board, pcbnew.Edge_Cuts, (0, height - radius), (0, radius), line)
    add_arc(board, pcbnew.Edge_Cuts, (0, radius), (radius - k, radius - k), (radius, 0), line)


def add_capsule_slot(board, rect: dict) -> None:
    x0, x1 = rect["x"]
    y0, y1 = rect["y"]
    radius = (y1 - y0) / 2
    cy = (y0 + y1) / 2
    k = radius
    add_segment(board, pcbnew.Edge_Cuts, (x0 + radius, y0), (x1 - radius, y0), 0.05)
    add_arc(board, pcbnew.Edge_Cuts, (x1 - radius, y0), (x1, cy), (x1 - radius, y1), 0.05)
    add_segment(board, pcbnew.Edge_Cuts, (x1 - radius, y1), (x0 + radius, y1), 0.05)
    add_arc(board, pcbnew.Edge_Cuts, (x0 + radius, y1), (x0, cy), (x0 + radius, y0), 0.05)


def add_silk_rect(board, rect: dict, layer: int, width: float = 0.15) -> None:
    x0, x1 = rect["x"]
    y0, y1 = rect["y"]
    add_segment(board, layer, (x0, y0), (x1, y0), width)
    add_segment(board, layer, (x1, y0), (x1, y1), width)
    add_segment(board, layer, (x1, y1), (x0, y1), width)
    add_segment(board, layer, (x0, y1), (x0, y0), width)


def add_text(
    board,
    value: str,
    at: tuple[float, float],
    layer: int,
    size: float,
    thickness: float = 0.15,
) -> None:
    item = pcbnew.PCB_TEXT(board)
    item.SetText(value)
    item.SetPosition(point(*at))
    item.SetLayer(layer)
    item.SetTextSize(point(size, size))
    item.SetTextThickness(mm(thickness))
    item.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
    board.Add(item)


def configure_board(board, contract: dict, project: str) -> None:
    geometry = contract["board"]
    board.SetCopperLayerCount(geometry["copper_layers"])
    settings = board.GetDesignSettings()
    settings.SetBoardThickness(mm(geometry["thickness_mm"]))
    # JLCPCB Standard PCBA production minima.  Keep the ordinary board rules
    # explicit here; the few intentional edge-mount exceptions belong in a
    # reference-scoped custom-rule file rather than weakening the whole board.
    settings.m_MinClearance = mm(0.15)
    settings.m_MinThroughDrill = mm(0.20)
    settings.m_CopperEdgeClearance = mm(0.20)
    settings.m_MinSilkTextHeight = mm(1.00)
    settings.m_MinSilkTextThickness = mm(0.15)
    title = board.GetTitleBlock()
    title.SetTitle(f"Leshy2 {project} R2 exact placement")
    title.SetRevision(contract["marker"])
    title.SetCompany("ESP32-Leshy2 open hardware")
    add_rounded_outline(
        board,
        geometry["width_mm"],
        geometry["height_mm"],
        geometry["corner_radius_mm"],
    )


def add_mechanical_geometry(board, project: str, contract: dict, grids: dict) -> list[dict]:
    result = []
    holes = contract["mechanical"]["mounting_holes"]
    hole_library = str(KICAD_FOOTPRINT_ROOT / "MountingHole.pretty")
    for index, centre in enumerate(holes["centres_mm"], 1):
        fp = pcbnew.FootprintLoad(hole_library, "MountingHole_2.7mm_M2.5")
        if fp is None:
            raise ValueError("KiCad mounting-hole footprint could not be loaded")
        board.Add(fp)
        fp.SetReference(f"MH{index}")
        fp.SetValue("M2.5 compression-stop axis")
        fp.SetPosition(point(*centre))
        fp.SetAttributes(
            fp.GetAttributes()
            | pcbnew.FP_BOARD_ONLY
            | pcbnew.FP_EXCLUDE_FROM_BOM
            | pcbnew.FP_EXCLUDE_FROM_POS_FILES
        )
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
        rect = {
            "x": [centre[0] - holes["head_keepout_radius_mm"], centre[0] + holes["head_keepout_radius_mm"]],
            "y": [centre[1] - holes["head_keepout_radius_mm"], centre[1] + holes["head_keepout_radius_mm"]],
        }
        for grid in grids.values():
            grid.add(f"mounting_keepout_{index}", rect, "mechanical_keepout")
        result.append({"id": f"MH{index}", "centre_mm": centre, "keepout_mm": rect})
    if project == "LESHY2-UI-R2":
        slot = contract["mechanical"]["display_slot"]["bbox_mm"]
        add_capsule_slot(board, slot)
        grids["B.Cu"].add("display_fpc_slot", slot, "board_cutout")
        grids["F.Cu"].add("display_fpc_slot", slot, "board_cutout")
        panel = contract["mechanical"]["display_bed"]["panel_bbox_mm"]
        grids["F.Cu"].add("display_panel_bed", panel, "external_component_keepout")
    return result


def add_user_silkscreen(board, project: str, placement: dict, contract: dict) -> None:
    if project == "LESHY2-UI-R2":
        panel = contract["mechanical"]["display_bed"]["panel_bbox_mm"]
        psa = contract["mechanical"]["display_bed"]["psa_bbox_mm"]
        add_silk_rect(
            board,
            {"x": [panel["x"][0] - 0.30, panel["x"][1] + 0.30], "y": [panel["y"][0] - 0.30, panel["y"][1] + 0.30]},
            pcbnew.F_SilkS,
        )
        add_silk_rect(
            board,
            {"x": [psa["x"][0] - 0.25, psa["x"][1] + 0.25], "y": [psa["y"][0] - 0.25, psa["y"][1] + 0.25]},
            pcbnew.F_SilkS,
        )
        add_text(board, "DISPLAY · FPC ↑", (37.5, 105.4), pcbnew.F_SilkS, 1.00, 0.15)
        add_text(board, "Леший", (37.5, 108.0), pcbnew.F_SilkS, 2.35, 0.32)
        add_text(board, "ESP32-LESHY2 · UI PCB · R2-EVT1 · REV A", (37.5, 110.6), pcbnew.F_SilkS, 1.00, 0.15)
        antenna_rows = placement["antenna_silkscreen"]["front"]
    else:
        add_text(board, "ESP32-LESHY2", (37.5, 136.0), pcbnew.F_SilkS, 1.55, 0.23)
        add_text(board, "RF/PWR PCB · R2-EVT1 · REV A", (37.5, 139.0), pcbnew.F_SilkS, 1.00, 0.15)
        add_text(board, "github.com/anton-vinogradov/esp32-leshy2", (37.5, 142.0), pcbnew.F_SilkS, 1.00, 0.15)
        antenna_rows = placement["antenna_silkscreen"]["rear"]
    antenna_positions = list(contract["antenna_ports"][project].values())
    for row, position in zip(antenna_rows, antenna_positions):
        add_text(board, row["text"], (position[0], 15.2), pcbnew.F_SilkS, 1.00, 0.15)


def build_target_index(contract: dict, placement: dict, coordinate: dict) -> dict[str, dict]:
    targets: dict[str, dict] = {}
    for row in coordinate["rows"]:
        targets[row["instance"]] = {
            "source": "H1 coordinate seed",
            "frame": row["source_frame"],
            "bbox": row["world_bbox_mm"],
            "direction": row.get("direction", "not applicable"),
        }
    for row in placement["placements"]:
        if row["kind"] != "fixed_body":
            continue
        x, y = row["world_xy_mm"]
        width, height, _ = row["size_mm"]
        target = {
            "source": "H1-R2 exact body seed",
            "frame": row["frame"],
            "bbox": {"x": [x, x + width], "y": [y, y + height]},
            "direction": row.get("role", "not applicable"),
        }
        aliases = {row["id"]}
        if row["id"].endswith("_r2"):
            aliases.add(row["id"][:-3])
        aliases.update(row.get("replaces", []))
        for alias in aliases:
            targets[alias] = target
    for current, target_name in contract["instance_aliases"].items():
        if target_name not in targets:
            raise ValueError(f"placement alias target is unknown: {current} -> {target_name}")
        targets[current] = targets[target_name]
    return targets


def target_for_instance(
    project: str,
    instance: str,
    contract: dict,
    targets: dict[str, dict],
) -> dict | None:
    override = contract.get("placement_overrides", {}).get(instance)
    if override:
        return {
            "source": "H6 exact-courtyard correction",
            "frame": override["frame"],
            "centre": override["centre_mm"],
            "rotation": override["rotation_deg"],
            "direction": override["reason"],
        }
    antennas = contract["antenna_ports"].get(project, {})
    if instance in antennas:
        return {
            "source": "H1-R2 5+5 antenna bank",
            "frame": "front-outer" if project == "LESHY2-UI-R2" else "rear-outer",
            "anchor": antennas[instance],
            "rotation": 0.0,
            "direction": "board-edge antenna port",
        }
    if project == "LESHY2-RF-R2" and instance == contract["mechanical"]["rear_battery_holder"]["instance"]:
        holder = contract["mechanical"]["rear_battery_holder"]
        return {
            "source": "H1-R2 battery-holder mechanics",
            "frame": "rear-outer",
            "centre": holder["centre_mm"],
            "rotation": holder["rotation_deg"],
            "direction": "rear battery face",
        }
    if project == "LESHY2-RF-R2" and instance == contract["mechanical"]["u219_pickup_loop"]["instance"]:
        loop = contract["mechanical"]["u219_pickup_loop"]
        return {
            "source": "H1-R2 U219 pickup-loop reserve",
            "frame": "rf-outer-face",
            "bbox": loop["bbox_mm"],
            "rotation": 0.0,
            "direction": "board copper under optional Cap",
            "nonphysical_overlap": True,
        }
    return targets.get(instance)


def target_side(target: dict | None) -> str:
    if not target:
        return "B.Cu"
    return "F.Cu" if target["frame"] in {"front-outer", "rear-outer", "ui-outer-face", "rf-outer-face", "rf-outer-right-edge"} else "B.Cu"


def opposite_side(side: str) -> str:
    return "B.Cu" if side == "F.Cu" else "F.Cu"


def desired_rotation(poses: dict[float, dict], target: dict) -> float:
    if "rotation" in target:
        return float(target["rotation"])
    if "bbox" not in target:
        return 0.0
    wanted = rect_size(target["bbox"])
    zsize = poses[0.0]["size"]
    nsize = poses[90.0]["size"]
    zerror = abs(zsize[0] - wanted[0]) + abs(zsize[1] - wanted[1])
    nerror = abs(nsize[0] - wanted[0]) + abs(nsize[1] - wanted[1])
    return 0.0 if zerror <= nerror else 90.0


def candidate_centres(preferred: tuple[float, float], step: float, width: float, height: float):
    base_x = int(round(preferred[0] / step))
    base_y = int(round(preferred[1] / step))
    max_ring = int(math.ceil(max(width, height) / step)) + 2
    yielded = set()
    for ring in range(max_ring + 1):
        if ring == 0:
            offsets = [(0, 0)]
        else:
            offsets = []
            for dx in range(-ring, ring + 1):
                offsets.append((dx, -ring))
                offsets.append((dx, ring))
            for dy in range(-ring + 1, ring):
                offsets.append((-ring, dy))
                offsets.append((ring, dy))
        for dx, dy in offsets:
            key = (base_x + dx, base_y + dy)
            if key in yielded:
                continue
            yielded.add(key)
            x, y = key[0] * step, key[1] * step
            if 0 <= x <= width and 0 <= y <= height:
                yield x, y


def nearest_grid_slot(
    grid: OccupancyGrid,
    poses: dict[float, dict],
    preferred: tuple[float, float],
) -> tuple[dict, tuple[float, float], dict] | None:
    """Find the nearest free rectangular cell run without probing pcbnew."""
    full_mask = (1 << grid.columns) - 1
    best = None
    best_score = math.inf
    for rotation in (0.0, 90.0):
        pose = poses[rotation]
        width, height = pose["size"]
        span_x = max(1, math.ceil((width + 2 * grid.gap) / grid.step))
        span_y = max(1, math.ceil((height + 2 * grid.gap) / grid.step))
        if span_x > grid.columns or span_y > grid.rows:
            continue
        possible_starts = grid.columns - span_x + 1
        start_mask = (1 << possible_starts) - 1
        preferred_x0 = int(round((preferred[0] - grid.gap - width / 2) / grid.step))
        preferred_x0 = min(max(0, preferred_x0), possible_starts - 1)
        y_starts = list(range(grid.rows - span_y + 1))
        y_starts.sort(
            key=lambda y0: abs(
                y0 * grid.step + grid.gap + height / 2 - preferred[1]
            )
        )
        for y0 in y_starts:
            centre_y = y0 * grid.step + grid.gap + height / 2
            vertical_score = (centre_y - preferred[1]) ** 2
            if vertical_score >= best_score:
                break
            blocked = 0
            for row in range(y0, y0 + span_y):
                blocked |= grid.bits[row]
            available = full_mask ^ blocked
            valid_starts = available
            for shift in range(1, span_x):
                valid_starts &= available >> shift
                if not valid_starts:
                    break
            valid_starts &= start_mask
            if not valid_starts:
                continue
            lower_bits = valid_starts & ((1 << (preferred_x0 + 1)) - 1)
            lower = lower_bits.bit_length() - 1 if lower_bits else None
            higher_bits = valid_starts >> preferred_x0
            higher = (
                preferred_x0 + ((higher_bits & -higher_bits).bit_length() - 1)
                if higher_bits
                else None
            )
            starts = [value for value in (lower, higher) if value is not None]
            x0 = min(starts, key=lambda value: abs(value - preferred_x0))
            centre = (
                x0 * grid.step + grid.gap + width / 2,
                centre_y,
            )
            rect = rect_at_centre(pose, centre)
            if not grid.is_free(rect):
                continue
            score = (centre[0] - preferred[0]) ** 2 + vertical_score
            if score < best_score:
                best_score = score
                best = rect, centre, pose
    return best


def is_edge_interface(instance: str, target: dict | None, contract: dict) -> bool:
    if any(token in instance for token in contract["placement_policy"]["edge_anchor_names"]):
        return True
    direction = (target or {}).get("direction", "")
    return "enclosure exit" in direction or "board-edge" in direction


def add_nets_and_footprints(
    board,
    project: str,
    instance_rows: list[dict],
    net_rows: list[dict],
    symbols: dict[str, dict],
    net_bindings: dict[str, str],
) -> tuple[list[dict], dict[str, set[str]], list[str]]:
    contact_to_pin = {
        device_id: {contact: pin["number"] for pin in symbol["pin_map"] for contact in pin["contacts"]}
        for device_id, symbol in symbols.items()
    }
    instance_by_name = {row["instance"]: row for row in instance_rows}
    pin_nets: dict[tuple[str, str], str] = {}
    instance_nets: dict[str, set[str]] = defaultdict(set)
    errors = []
    for row in net_rows:
        if row["project"] != project or row["disposition"] != "connected":
            continue
        instance = instance_by_name[row["instance"]]
        pin = contact_to_pin[instance["device_id"]].get(row["contact"])
        if pin is None:
            if row["contact"] in {"ANT", "ANT1"}:
                continue
            errors.append(f"{row['instance']}.{row['contact']} has no controlled-symbol pad number")
            continue
        key = (row["instance"], pin)
        previous = pin_nets.get(key)
        if previous and previous != row["net"]:
            errors.append(f"{row['instance']} pad {pin} maps to both {previous} and {row['net']}")
        pin_nets[key] = row["net"]
        instance_nets[row["instance"]].add(row["net"])

    net_names = sorted(set(pin_nets.values()))
    missing_bindings = sorted(set(net_names) - set(net_bindings))
    extra_bindings = sorted(set(net_bindings) - set(net_names))
    if missing_bindings:
        errors.append(f"missing exact KiCad names for {len(missing_bindings)} canonical nets")
    if extra_bindings:
        errors.append(f"net binding contains {len(extra_bindings)} unused canonical nets")
    board_nets = {}
    for net_name in net_names:
        if net_name not in net_bindings:
            continue
        net = pcbnew.NETINFO_ITEM(board, net_bindings[net_name])
        board.Add(net)
        board_nets[net_name] = net

    entries = []
    for row in sorted(instance_rows, key=lambda item: natural_key(item["reference"])):
        library, name = footprint_library(row["footprint"])
        fp = pcbnew.FootprintLoad(library, name)
        if fp is None:
            errors.append(f"could not load {row['footprint']} for {row['instance']}")
            continue
        board.Add(fp)
        fp.SetFPIDAsString(row["footprint"])
        fp.SetReference(row["reference"])
        fp.SetValue(row["mpn"])
        fp.SetField("Leshy2Instance", row["instance"])
        fp.GetField("Leshy2Instance").SetVisible(False)
        fp.SetSheetname(row["sheet"])
        fp.SetSheetfile(f"{row['sheet']}.kicad_sch")
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
        path = pcbnew.KIID_PATH()
        path.push_back(pcbnew.KIID(schematic_uuid(f"hierarchy:{project}:{row['sheet']}")))
        path.push_back(pcbnew.KIID(schematic_uuid(f"symbol:{project}:{row['sheet']}:{row['instance']}")))
        fp.SetPath(path)
        if row.get("bom_excluded"):
            fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
        pad_numbers = {pad.GetNumber() for pad in fp.Pads()}
        for (instance_name, pin), net_name in pin_nets.items():
            if instance_name != row["instance"]:
                continue
            if pin not in pad_numbers:
                errors.append(f"{row['instance']} controlled pin {pin} is absent from {row['footprint']}")
                continue
            for pad in fp.Pads():
                if pad.GetNumber() == pin:
                    if net_name in board_nets:
                        pad.SetNet(board_nets[net_name])
        entries.append({"row": row, "fp": fp})
    return entries, instance_nets, errors


def preferred_centre(
    entry: dict,
    project_contract: dict,
    instance_nets: dict[str, set[str]],
    net_members: dict[str, set[str]],
    placed_centres: dict[str, tuple[float, float]],
) -> tuple[float, float]:
    neighbours = []
    # Sort set-backed connectivity before floating-point accumulation. Python's
    # per-process hash seed must never move a footprint between two equal grid
    # candidates or change the generated native-board bytes.
    for net in sorted(instance_nets.get(entry["row"]["instance"], set())):
        if len(net_members[net]) > 12:
            continue
        for instance in sorted(net_members[net]):
            if instance in placed_centres:
                neighbours.append((placed_centres[instance], 1.0 / max(2, len(net_members[net]))))
    if neighbours:
        weight = sum(item[1] for item in neighbours)
        return (
            sum(item[0][0] * item[1] for item in neighbours) / weight,
            sum(item[0][1] * item[1] for item in neighbours) / weight,
        )
    return tuple(project_contract["sheet_anchors_mm"][entry["row"]["sheet"]])


def place_project(
    project: str,
    contract: dict,
    placement: dict,
    coordinate: dict,
    instance_rows: list[dict],
    net_rows: list[dict],
    symbols: dict[str, dict],
    net_bindings: dict[str, str],
) -> tuple[object, dict]:
    board = pcbnew.BOARD()
    configure_board(board, contract, project)
    geometry = contract["board"]
    grids = {
        side: OccupancyGrid(
            geometry["width_mm"],
            geometry["height_mm"],
            geometry["packing_grid_mm"],
            geometry["minimum_courtyard_gap_mm"],
        )
        for side in ("F.Cu", "B.Cu")
    }
    mechanics = add_mechanical_geometry(board, project, contract, grids)
    add_user_silkscreen(board, project, placement, contract)
    entries, instance_nets, errors = add_nets_and_footprints(
        board, project, instance_rows, net_rows, symbols, net_bindings
    )
    targets = build_target_index(contract, placement, coordinate)
    hard_locked = set(contract["placement_policy"]["hard_locked"])
    net_members: dict[str, set[str]] = defaultdict(set)
    for instance, nets in instance_nets.items():
        for net in nets:
            net_members[net].add(instance)
    placed_centres: dict[str, tuple[float, float]] = {}
    placed_rows = []
    conflicts = []
    boundary_exceptions = []
    failures = []

    for entry in entries:
        target = target_for_instance(project, entry["row"]["instance"], contract, targets)
        entry["target"] = target
        entry["side"] = target_side(target)
        if entry["side"] == "B.Cu":
            entry["fp"].Flip(point(0.0, 0.0), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        entry["poses"] = {
            rotation: footprint_pose(entry["fp"], entry["side"], rotation)
            for rotation in (0.0, 90.0)
        }
        entry["area"] = math.prod(entry["poses"][0.0]["size"])
        entry["hard"] = bool(
            target
            and (
                entry["row"]["instance"] in hard_locked
                or "_external_sma" in entry["row"]["instance"]
                or target.get("nonphysical_overlap")
            )
        )

    def commit(
        entry: dict,
        rect: dict,
        pose: dict,
        method: str,
        moved_mm: float = 0.0,
        cross_rects: list[dict] | None = None,
    ) -> None:
        instance = entry["row"]["instance"]
        target = entry["target"]
        if not (target and target.get("nonphysical_overlap")):
            grids[entry["side"]].add(instance, rect, "component")
        centre = rect_centre(rect)
        if cross_rects is None:
            cross_rects = cross_rects_at_centre(pose, centre)
        for index, cross_rect in enumerate(cross_rects, 1):
            grids[opposite_side(entry["side"])].add(
                f"{instance}:cross:{index}", cross_rect, "opposite-face copper or hole keepout"
            )
        placed_centres[instance] = centre
        placed_rows.append(
            {
                "instance": instance,
                "reference": entry["row"]["reference"],
                "sheet": entry["row"]["sheet"],
                "side": entry["side"],
                "footprint": entry["row"]["footprint"],
                "method": method,
                "courtyard_bbox_mm": rect,
                "opposite_face_keepout_bboxes_mm": cross_rects,
                "courtyard_centre_mm": [round(centre[0], 4), round(centre[1], 4)],
                "footprint_anchor_mm": [
                    round(pcbnew.ToMM(entry["fp"].GetPosition().x), 4),
                    round(pcbnew.ToMM(entry["fp"].GetPosition().y), 4),
                ],
                "rotation_deg": round(entry["fp"].GetOrientationDegrees(), 3),
                "moved_from_seed_mm": round(moved_mm, 4),
            }
        )

    fixed = sorted(
        [entry for entry in entries if entry["target"]],
        key=lambda entry: (not entry["hard"], -entry["area"], natural_key(entry["row"]["reference"])),
    )
    automatic = sorted(
        [entry for entry in entries if not entry["target"]],
        key=lambda entry: (-entry["area"], natural_key(entry["row"]["reference"])),
    )

    for entry in fixed:
        target = entry["target"]
        side = entry["side"]
        rotation = desired_rotation(entry["poses"], target)
        pose = entry["poses"][rotation]
        if "anchor" in target:
            rect = apply_anchor(entry["fp"], pose, tuple(target["anchor"]))
            desired = rect_centre(rect)
            cross_rects = cross_rects_at_anchor(pose, tuple(target["anchor"]))
            cross_body_rects = cross_rects_at_anchor(
                pose, tuple(target["anchor"]), "cross_body_rects"
            )
        else:
            desired = tuple(target.get("centre") or rect_centre(target["bbox"]))
            rect = apply_centre(entry["fp"], pose, desired)
            cross_rects = cross_rects_at_centre(pose, desired)
            cross_body_rects = cross_rects_at_centre(pose, desired, "cross_body_rects")
        allow_outside = is_edge_interface(entry["row"]["instance"], target, contract)
        collisions = (
            []
            if target.get("nonphysical_overlap")
            else grids[side].conflicts(rect, allow_outside=allow_outside)
        )
        for cross_rect in cross_body_rects:
            collisions += grids[opposite_side(side)].conflicts(
                cross_rect, allow_outside=allow_outside
            )
        if not collisions:
            if allow_outside and not grids[side].inside(rect):
                boundary_exceptions.append(
                    {"instance": entry["row"]["instance"], "reason": target["direction"], "bbox_mm": rect}
                )
            commit(
                entry,
                rect,
                pose,
                "hard H1 datum" if entry["hard"] else "exact H1 seed",
                cross_rects=cross_rects,
            )
            continue
        if entry["hard"]:
            conflicts.append(
                {
                    "instance": entry["row"]["instance"],
                    "side": side,
                    "bbox_mm": rect,
                    "conflicts": [row["id"] for row in collisions],
                }
            )
            commit(entry, rect, pose, "hard H1 datum with conflict", cross_rects=cross_rects)
            continue
        placed = False
        for centre in candidate_centres(desired, geometry["packing_grid_mm"], geometry["width_mm"], geometry["height_mm"]):
            for candidate_rotation in (rotation, (rotation + 90.0) % 180.0):
                candidate_pose = entry["poses"][candidate_rotation]
                candidate = rect_at_centre(candidate_pose, centre)
                candidate_cross = cross_rects_at_centre(candidate_pose, centre)
                candidate_cross_body = cross_rects_at_centre(
                    candidate_pose, centre, "cross_body_rects"
                )
                if grids[side].is_free(candidate) and (
                    not candidate_cross_body
                    or not any(
                        grids[opposite_side(side)].conflicts(rect)
                        for rect in candidate_cross_body
                    )
                ):
                    moved = math.dist(desired, centre)
                    apply_centre(entry["fp"], candidate_pose, centre)
                    commit(
                        entry,
                        candidate,
                        candidate_pose,
                        "nearest exact-footprint correction",
                        moved,
                        candidate_cross,
                    )
                    placed = True
                    break
            if placed:
                break
        if not placed:
            failures.append(entry["row"]["instance"])

    for entry in automatic:
        desired = preferred_centre(
            entry,
            contract["boards"][project],
            instance_nets,
            net_members,
            placed_centres,
        )
        slot = nearest_grid_slot(grids[entry["side"]], entry["poses"], desired)
        if slot is not None:
            candidate, centre, candidate_pose = slot
            candidate_cross = cross_rects_at_centre(candidate_pose, centre)
            candidate_cross_body = cross_rects_at_centre(
                candidate_pose, centre, "cross_body_rects"
            )
            if candidate_cross_body and any(
                grids[opposite_side(entry["side"])].conflicts(rect)
                for rect in candidate_cross_body
            ):
                slot = None
        if slot is None and any(pose["cross_rects"] for pose in entry["poses"].values()):
            for centre in candidate_centres(
                desired,
                geometry["packing_grid_mm"],
                geometry["width_mm"],
                geometry["height_mm"],
            ):
                for candidate_pose in entry["poses"].values():
                    candidate = rect_at_centre(candidate_pose, centre)
                    candidate_cross = cross_rects_at_centre(candidate_pose, centre)
                    candidate_cross_body = cross_rects_at_centre(
                        candidate_pose, centre, "cross_body_rects"
                    )
                    if grids[entry["side"]].is_free(candidate) and (
                        not candidate_cross_body
                        or not any(
                            grids[opposite_side(entry["side"])].conflicts(rect)
                            for rect in candidate_cross_body
                        )
                    ):
                        slot = candidate, centre, candidate_pose
                        break
                if slot is not None:
                    break
        if slot is None:
            failures.append(entry["row"]["instance"])
            continue
        candidate, centre, candidate_pose = slot
        candidate_cross = cross_rects_at_centre(candidate_pose, centre)
        apply_centre(entry["fp"], candidate_pose, centre)
        commit(
            entry,
            candidate,
            candidate_pose,
            "connectivity/sheet automatic seed",
            cross_rects=candidate_cross,
        )

    placed_rows.sort(key=lambda row: natural_key(row["reference"]))
    return board, {
        "project": project,
        "schematic_instance_count": len(instance_rows),
        "placed_instance_count": len(placed_rows),
        "side_counts": dict(sorted(Counter(row["side"] for row in placed_rows).items())),
        "method_counts": dict(sorted(Counter(row["method"] for row in placed_rows).items())),
        "net_count": len({net for nets in instance_nets.values() for net in nets}),
        "mechanical": mechanics,
        "boundary_exceptions": boundary_exceptions,
        "hard_conflicts": conflicts,
        "placement_failures": failures,
        "net_or_footprint_errors": errors,
        "placements": placed_rows,
    }


def normalize_board_uuids(project: str, text: str) -> str:
    index = 0

    def replace(match: re.Match) -> str:
        nonlocal index
        value = stable_uuid(f"{project}:board-item:{index}")
        index += 1
        return f'{match.group(1)}"{value}"'

    return re.sub(r'(\(uuid\s+)"[0-9a-fA-F-]+"', replace, text)


def board_bytes(project: str, board) -> bytes:
    with tempfile.TemporaryDirectory(prefix="leshy2-h6-") as directory:
        path = Path(directory) / f"{project}.kicad_pcb"
        if not pcbnew.SaveBoard(str(path), board):
            raise ValueError(f"KiCad failed to save {project}")
        text = normalize_board_uuids(project, path.read_text(encoding="utf-8"))
    return (text.rstrip() + "\n").encode()


def _balanced_form_end(text: str, start: int) -> int:
    depth = 0
    quoted = False
    escaped = False
    for index in range(start, len(text)):
        character = text[index]
        if quoted:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                quoted = False
        elif character == '"':
            quoted = True
        elif character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth == 0:
                return index + 1
    raise ValueError("unterminated KiCad S-expression")


def placement_projection(text: str) -> bytes:
    """Canonicalize KiCad board structure while excluding routed copper."""
    root = text.find("(kicad_pcb")
    if root < 0:
        raise ValueError("not a KiCad PCB document")
    outer_end = _balanced_form_end(text, root)
    cursor = root + len("(kicad_pcb")
    forms = []
    while cursor < outer_end - 1:
        while cursor < outer_end - 1 and text[cursor].isspace():
            cursor += 1
        if cursor >= outer_end - 1:
            break
        if text[cursor] != "(":
            raise ValueError(f"unexpected KiCad board token at offset {cursor}")
        end = _balanced_form_end(text, cursor)
        form = text[cursor:end]
        match = re.match(r"\(\s*([^\s()]+)", form)
        if not match:
            raise ValueError(f"cannot identify KiCad form at offset {cursor}")
        head = match.group(1)
        if head in {"segment", "via", "arc", "group"}:
            cursor = end
            continue
        if head == "zone" and "(keepout" not in form:
            cursor = end
            continue
        # Generated UUIDs are serialization identities, not placement data.
        form = re.sub(r'(\(uuid\s+)"[0-9a-fA-F-]+"', r'\1"<uuid>"', form)
        forms.append(form)
        cursor = end
    return ("(kicad_pcb\n" + "\n".join(sorted(forms)) + "\n)\n").encode()


def placement_signature_bytes(project: str, board) -> bytes:
    """Return a stable board projection that deliberately excludes routed copper.

    The H6 placement generator remains the authority for footprints, pads, nets,
    board graphics and setup.  Tracks, vias and ordinary copper zones belong to
    the routed board and must neither make ``--check`` fail nor be erased by a
    routine placement verification.  Rule areas are retained because they are
    placement/routing constraints rather than routed copper.
    """
    with tempfile.TemporaryDirectory(prefix="leshy2-h6-placement-") as directory:
        staged = Path(directory) / f"{project}-staged.kicad_pcb"
        if not pcbnew.SaveBoard(str(staged), board):
            raise ValueError(f"KiCad failed to stage {project} for placement signature")
        return placement_projection(staged.read_text(encoding="utf-8"))


def placement_signature_from_board_bytes(project: str, data: bytes) -> bytes:
    """Project already-normalized serialized board bytes through KiCad once."""
    with tempfile.TemporaryDirectory(prefix="leshy2-h6-seed-") as directory:
        path = Path(directory) / f"{project}.kicad_pcb"
        path.write_bytes(data)
        return placement_signature_bytes(project, pcbnew.LoadBoard(str(path)))


def svg_bytes(audit: dict) -> bytes:
    width_px, height_px = 1680, 1050
    scale = 5.35
    board_w, board_h = 75.0, 150.0
    origins = {"LESHY2-UI-R2": (120, 140), "LESHY2-RF-R2": (920, 140)}
    palette = {
        "hard H1 datum": ("#dce8ff", "#2563eb"),
        "exact H1 seed": ("#e9eef5", "#64748b"),
        "nearest exact-footprint correction": ("#fff4d6", "#d97706"),
        "connectivity/sheet automatic seed": ("#e7f8ef", "#059669"),
        "hard H1 datum with conflict": ("#fee2e2", "#dc2626"),
    }
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_px}" height="{height_px}" viewBox="0 0 {width_px} {height_px}">',
        '<rect width="100%" height="100%" fill="#f8fafc"/>',
        '<text x="60" y="55" font-family="Inter,Arial,sans-serif" font-size="34" font-weight="700" fill="#0f172a">Leshy2 · H6.0.1 exact-footprint placement</text>',
        '<text x="60" y="88" font-family="Inter,Arial,sans-serif" font-size="17" fill="#475569">Accessible inner faces in shared assembly coordinates · exact KiCad courtyards · routing not started</text>',
    ]
    for board in audit["boards"]:
        ox, oy = origins[board["project"]]
        title = "UI PCB · inner" if board["project"] == "LESHY2-UI-R2" else "RF / power PCB · inner"
        out.append(
            f'<text x="{ox + board_w * scale / 2:.1f}" y="120" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="24" font-weight="700" fill="#0f172a">{title}</text>'
        )
        out.append(
            f'<rect x="{ox}" y="{oy}" width="{board_w * scale}" height="{board_h * scale}" rx="{2 * scale}" fill="#ffffff" stroke="#334155" stroke-width="3"/>'
        )
        for hole in board["mechanical"]:
            x, y = hole["centre_mm"]
            out.append(
                f'<circle cx="{ox + x * scale:.2f}" cy="{oy + y * scale:.2f}" r="{4 * scale:.2f}" fill="none" stroke="#f97316" stroke-width="1.5" stroke-dasharray="5 4"/>'
            )
            out.append(
                f'<circle cx="{ox + x * scale:.2f}" cy="{oy + y * scale:.2f}" r="{1.35 * scale:.2f}" fill="#fff" stroke="#475569" stroke-width="2"/>'
            )
        for row in board["placements"]:
            if row["side"] != "B.Cu":
                continue
            rect = row["courtyard_bbox_mm"]
            x = ox + rect["x"][0] * scale
            y = oy + rect["y"][0] * scale
            w = (rect["x"][1] - rect["x"][0]) * scale
            h = (rect["y"][1] - rect["y"][0]) * scale
            fill, stroke = palette[row["method"]]
            out.append(
                f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="1.5" fill="{fill}" stroke="{stroke}" stroke-width="0.65"/>'
            )
            if w >= 28 and h >= 15:
                out.append(
                    f'<text x="{x + w / 2:.2f}" y="{y + h / 2 + 3:.2f}" text-anchor="middle" font-family="ui-monospace,monospace" font-size="8" fill="#1e293b">{html.escape(row["reference"])}</text>'
                )
        out.append(
            f'<text x="{ox + board_w * scale / 2:.1f}" y="{oy + board_h * scale + 30:.1f}" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="17" font-weight="700" fill="#0f172a">{board["placed_instance_count"]} positions · {board["net_count"]} nets · {board["side_counts"].get("B.Cu", 0)} inner</text>'
        )
    legend_y = 1025
    x = 60
    for label, (fill, stroke) in palette.items():
        if label == "hard H1 datum with conflict" and not any(b["hard_conflicts"] for b in audit["boards"]):
            continue
        out.append(f'<rect x="{x}" y="{legend_y - 13}" width="18" height="12" fill="{fill}" stroke="{stroke}"/>')
        out.append(f'<text x="{x + 25}" y="{legend_y - 2}" font-family="Inter,Arial,sans-serif" font-size="14" fill="#334155">{label}</text>')
        x += 250
    out.append("</svg>")
    return ("\n".join(out) + "\n").encode()


def build() -> tuple[dict[Path, bytes], dict]:
    # KiCad assigns random UUIDs while footprints and board graphics are
    # constructed. Seed that generator so identical reviewed inputs produce
    # byte-identical native boards and stable audit hashes.
    pcbnew.KIID.SeedGenerator(0x4C455348)
    contract = load(CONTRACT_PATH)
    placement = load(PLACEMENT_PATH)
    coordinate = load(COORDINATE_PATH)
    instances = load(INSTANCE_PATH)["rows"]
    net_rows = load(NET_PATH)["rows"]
    symbols = {row["device_id"]: row for row in load(SYMBOL_PATH)["symbols"]}
    binding_artifact = load(NET_BINDING_PATH)
    outputs: dict[Path, bytes] = {}
    board_audits = []
    for project in contract["boards"]:
        project_instances = [row for row in instances if row["project"] == project]
        board, audit = place_project(
            project,
            contract,
            placement,
            coordinate,
            project_instances,
            net_rows,
            symbols,
            binding_artifact["projects"][project]["canonical_to_kicad"],
        )
        data = board_bytes(project, board)
        output_path = ROOT / contract["boards"][project]["output"]
        outputs[output_path] = data
        audit["output"] = str(output_path.relative_to(ROOT))
        audit["unrouted_seed_sha256"] = sha256_bytes(data)
        audit["placement_signature_sha256"] = sha256_bytes(
            placement_signature_from_board_bytes(project, data)
        )
        board_audits.append(audit)
    errors = [
        f"{board['project']}: {message}"
        for board in board_audits
        for message in (
            [f"hard placement conflict: {row}" for row in board["hard_conflicts"]]
            + [f"unplaced instance: {row}" for row in board["placement_failures"]]
            + board["net_or_footprint_errors"]
        )
    ]
    audit = {
        "schema_version": 2,
        "artifact": "H6-R2 exact-footprint placement audit",
        "marker": contract["marker"],
        "status": "pass" if not errors else "fail",
        "sources": {
            "contract": str(CONTRACT_PATH.relative_to(ROOT)),
            "contract_sha256": sha256(CONTRACT_PATH),
            "placement": str(PLACEMENT_PATH.relative_to(ROOT)),
            "placement_sha256": sha256(PLACEMENT_PATH),
            "coordinate_model": str(COORDINATE_PATH.relative_to(ROOT)),
            "coordinate_model_sha256": sha256(COORDINATE_PATH),
            "instance_ledger": str(INSTANCE_PATH.relative_to(ROOT)),
            "instance_ledger_sha256": sha256(INSTANCE_PATH),
            "net_ledger": str(NET_PATH.relative_to(ROOT)),
            "net_ledger_sha256": sha256(NET_PATH),
            "symbol_library": str(SYMBOL_PATH.relative_to(ROOT)),
            "symbol_library_sha256": sha256(SYMBOL_PATH),
            "kicad_net_bindings": str(NET_BINDING_PATH.relative_to(ROOT)),
            "kicad_net_bindings_sha256": sha256(NET_BINDING_PATH),
        },
        "summary": {
            "board_count": len(board_audits),
            "copper_layers_per_board": contract["board"]["copper_layers"],
            "schematic_instance_count": sum(row["schematic_instance_count"] for row in board_audits),
            "placed_instance_count": sum(row["placed_instance_count"] for row in board_audits),
            "hard_conflict_count": sum(len(row["hard_conflicts"]) for row in board_audits),
            "placement_failure_count": sum(len(row["placement_failures"]) for row in board_audits),
            "net_or_footprint_error_count": sum(len(row["net_or_footprint_errors"]) for row in board_audits),
            "routing_authorized": False,
            "routing_started": False,
        },
        "stackup": contract["board"]["factory_stack_candidate"],
        "boards": board_audits,
        "authorization": contract["authorization"],
        "errors": errors,
    }
    outputs[AUDIT_PATH] = (json.dumps(audit, indent=2, ensure_ascii=False) + "\n").encode()
    outputs[SVG_PATH] = svg_bytes(audit)
    return outputs, audit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write",
        action="store_true",
        help="DESTRUCTIVE after routing: replace both PCB files with unrouted seeds, audit and SVG",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify placement/setup while preserving and ignoring routed copper",
    )
    args = parser.parse_args()
    if args.write == args.check:
        parser.error("choose exactly one of --write or --check")
    outputs, audit = build()
    if args.write:
        for path, data in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    else:
        expected_signatures = {
            ROOT / row["output"]: row["placement_signature_sha256"]
            for row in audit["boards"]
        }
        stale = []
        for path, data in outputs.items():
            expected = sha256_bytes(data)
            if not path.exists():
                stale.append((str(path.relative_to(ROOT)), "missing", expected))
                continue
            if path.suffix == ".kicad_pcb":
                actual_board = pcbnew.LoadBoard(str(path))
                actual = sha256_bytes(
                    placement_signature_bytes(path.stem, actual_board)
                )
                expected = expected_signatures[path]
            else:
                actual = sha256_bytes(path.read_bytes())
            if actual != expected:
                stale.append((str(path.relative_to(ROOT)), actual, expected))
        if stale:
            details = ", ".join(
                f"{path} (actual {actual}, expected {expected})"
                for path, actual, expected in stale
            )
            raise SystemExit("stale H6 placement outputs: " + details)
    print(
        f"H6-R2 placement {audit['status']}: "
        f"{audit['summary']['placed_instance_count']}/{audit['summary']['schematic_instance_count']} positions; "
        f"{audit['summary']['hard_conflict_count']} hard conflicts; "
        f"{audit['summary']['placement_failure_count']} unplaced"
    )
    return 0 if audit["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
