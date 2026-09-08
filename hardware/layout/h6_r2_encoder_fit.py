"""Exact one-reference EC11 transition guard; no generic pin-rename waiver."""
from collections import Counter
import hashlib
import json
from pathlib import Path

FEATURE_ID = "RF-EC11-EXACT-AXIS-ENGINEERING-PTH-001"
PROJECT = "LESHY2-RF-R2"
REFERENCE = "SW3"
GEOMETRY_NAME = "h6-r2-encoder-fit-candidate.json"
BEFORE_ID = "Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm_MountingHoles"
AFTER_ID = "Leshy2_R2:EC11E18244AU-ENGINEERING-PTH"
RENAME = {"S1": "E", "S2": "D"}
GROUND = "/RF_01_USB_PD_CHARGE/POWER_GROUND"
EXPECTED_SIGNALS = {
    "A": ((68_500_000,57_750_000), "/RF_31_REAR_CONTROLS/ENCODER_A"),
    "C": ((71_000_000,57_750_000), GROUND),
    "B": ((73_500_000,57_750_000), "/RF_31_REAR_CONTROLS/ENCODER_B"),
    "D": ((68_500_000,43_250_000), GROUND),
    "E": ((73_500_000,43_250_000), "/RF_31_REAR_CONTROLS/UI_ENCODER_PUSH_N"),
}


def snapshot(fp, pcbnew):
    def xy(point):
        return [int(point.x), int(point.y)]
    return {
        "reference": fp.GetReference(),
        "footprint": str(fp.GetFPID().GetLibNickname()) + ":" + str(fp.GetFPID().GetLibItemName()),
        "side": "B.Cu" if fp.IsFlipped() else "F.Cu",
        "anchor_nm": xy(fp.GetPosition()), "rotation_deg": fp.GetOrientationDegrees(),
        "pads": [{"number": p.GetNumber(), "net": p.GetNetname(),
                  "at_nm": xy(p.GetPosition()), "size_nm": xy(p.GetSize()),
                  "drill_nm": xy(p.GetDrillSize()),
                  "pth": p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH,
                  "npth": p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH,
                  "both_copper_faces": p.IsOnLayer(pcbnew.F_Cu) and p.IsOnLayer(pcbnew.B_Cu),
                  "oval_drill": p.GetDrillShape() == pcbnew.PAD_DRILL_SHAPE_OBLONG}
                 for p in fp.Pads()],
    }


def verify_transition(before, after):
    for state, fpid, anchor, angle in (
        (before, BEFORE_ID, [68_500_000,57_750_000], 90),
        (after, AFTER_ID, [71_000_000,50_250_000], 0),
    ):
        if (state["reference"] != REFERENCE or state["footprint"] != fpid
                or state["side"] != "F.Cu" or state["anchor_nm"] != anchor
                or state["rotation_deg"] != angle):
            raise ValueError("encoder transition identity/shaft datum changed")
    for state, old in ((before, True), (after, False)):
        pads = state["pads"]
        npth = [p for p in pads if p["npth"]]
        if old:
            if (len(npth) != 2 or any(p["number"] or p["net"] for p in npth)
                    or sorted(p["at_nm"] for p in npth) != [[71_000_000,50_250_000],[71_000_000,54_750_000]]):
                raise ValueError("encoder old mechanical-hole inventory changed")
        elif npth:
            raise ValueError("encoder candidate has undocumented locating holes")
        electrical = [p for p in pads if not p["npth"]]
        expected_names = ["A","C","B","S1","S2","MP","MP"] if old else ["A","C","B","D","E","MP","MP"]
        if Counter(p["number"] for p in electrical) != Counter(expected_names):
            raise ValueError("encoder exact seven-terminal inventory changed")
        if any(not p["pth"] or not p["both_copper_faces"] for p in electrical):
            raise ValueError("encoder terminals must remain through-hole on both faces")
        signals = {RENAME.get(p["number"], p["number"]) if old else p["number"]: p
                   for p in electrical if p["number"] != "MP"}
        for name, (xy, net) in EXPECTED_SIGNALS.items():
            pad = signals[name]
            if tuple(pad["at_nm"]) != xy or pad["net"] != net or pad["size_nm"] != [2_000_000,2_000_000]:
                raise ValueError("encoder world signal pad/net pair changed: " + name)
            if not old and (pad["drill_nm"] != [1_100_000,1_100_000] or pad["oval_drill"]):
                raise ValueError("encoder standard signal-hole profile changed")
        mounts = [p for p in electrical if p["number"] == "MP"]
        expected_mount_x = [65_400_000,76_600_000] if old else [64_750_000,77_250_000]
        if (sorted(p["at_nm"] for p in mounts) != [[x,50_250_000] for x in expected_mount_x]
                or any(p["net"] for p in mounts)):
            raise ValueError("encoder mounting pitch or empty-net identity changed")
        if not old and any(p["size_nm"] != [2_800_000,4_800_000]
                           or p["drill_nm"] != [2_000_000,4_000_000]
                           or not p["oval_drill"] for p in mounts):
            raise ValueError("encoder engineering mounting PTH profile changed")
    return {"feature_id": FEATURE_ID, "reference": REFERENCE,
            "renames": RENAME, "unchanged_world_signal_pad_net_pairs": 5,
            "removed_undocumented_npth": 2, "fabrication_ready": False}


def verify_allowance(allowance, project, geometry_path):
    geometry_path = Path(geometry_path)
    expected = {"feature_id": FEATURE_ID,
                "source_geometry_sha256": hashlib.sha256(geometry_path.read_bytes()).hexdigest()}
    if allowance != expected or project != PROJECT:
        raise ValueError("unreviewed encoder geometry-transition authorization")
    geometry = json.loads(geometry_path.read_text())
    native = geometry["native_update_contract"]
    if (geometry["feature_id"] != FEATURE_ID or geometry["reference"] != REFERENCE
            or geometry["footprint"] != AFTER_ID
            or native["physical_pad_rename"] != RENAME
            or native["after_shaft_anchor_mm"] != [71,50.25]
            or geometry["engineering_pth_profile"]["mp_nominal_oval_mm"] != [2,4]):
        raise ValueError("encoder geometry contract no longer matches reviewed guard")
    return expected
