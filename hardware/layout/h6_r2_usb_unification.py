"""Finite RF J1 JAE→GCT migration; not a generic anonymous-pad waiver."""
from collections import Counter
import hashlib
import json

FEATURE_ID = "RF-J1-EXACT-GCT-USB-UNIFICATION-001"
PROJECT = "LESHY2-RF-R2"
REFERENCE = "J1"
REVIEW_NAME = "h6-r2-usb-unification.json"
BEFORE_ID = "Leshy2_R2:USB_C_Receptacle_JAE_DX07S016JA1R1500_EdgeSilk"
AFTER_ID = "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal"
BEFORE_GEOMETRY_SHA256 = "e364829bf9de8cd747a3d8f5a04c8ecad5508803f6c2b7b09c86252bd94c5485"
AFTER_GEOMETRY_SHA256 = "7367cd9c27f1c486eb22a019b596c43be3e8053749de0180398f98b42346d7c6"
GROUND = "/RF_01_USB_PD_CHARGE/POWER_GROUND"
SIGNALS = {
    "A1": GROUND, "A12": GROUND, "B1": GROUND, "B12": GROUND,
    "A4": "/RF_01_USB_PD_CHARGE/USB_C_VBUS_RAW", "A9": "/RF_01_USB_PD_CHARGE/USB_C_VBUS_RAW",
    "B4": "/RF_01_USB_PD_CHARGE/USB_C_VBUS_RAW", "B9": "/RF_01_USB_PD_CHARGE/USB_C_VBUS_RAW",
    "A5": "/RF_01_USB_PD_CHARGE/USB_C_CC1_CONNECTOR", "B5": "/RF_01_USB_PD_CHARGE/USB_C_CC2_CONNECTOR",
    "A6": "/RF_01_USB_PD_CHARGE/USB2_CONNECTOR_P", "B6": "/RF_01_USB_PD_CHARGE/USB2_CONNECTOR_P",
    "A7": "/RF_01_USB_PD_CHARGE/USB2_CONNECTOR_N", "B7": "/RF_01_USB_PD_CHARGE/USB2_CONNECTOR_N",
    "A8": "", "B8": "", "SH": GROUND,
}


def snapshot(fp, pcbnew):
    def xy(v):
        return [int(v.x), int(v.y)]
    return {"reference": fp.GetReference(), "footprint": fp.GetFPIDAsString(),
            "value": fp.GetValue(), "side": "B.Cu" if fp.IsFlipped() else "F.Cu",
            "anchor_nm": xy(fp.GetPosition()), "rotation_deg": fp.GetOrientationDegrees() % 360,
            "pads": [{"number": p.GetNumber(), "net": p.GetNetname(),
                      "at_nm": xy(p.GetPosition()), "size_nm": xy(p.GetSize()),
                      "drill_nm": xy(p.GetDrillSize()), "shape": int(p.GetShape()),
                      "drill_shape": int(p.GetDrillShape()), "angle_deg": p.GetOrientationDegrees() % 360,
                      "roundrect_radius_nm": int(p.GetRoundRectCornerRadius()),
                      # Ignore disabled KiCad copper-layer bits: *.Cu is
                      # expanded differently before/after serialization. All
                      # six actual copper layers and every mask/paste face are
                      # independently retained in the fingerprint.
                      "layers": [name for name, layer in (("F.Cu", pcbnew.F_Cu),
                          ("In1.Cu", pcbnew.In1_Cu), ("In2.Cu", pcbnew.In2_Cu),
                          ("In3.Cu", pcbnew.In3_Cu), ("In4.Cu", pcbnew.In4_Cu),
                          ("B.Cu", pcbnew.B_Cu), ("F.Mask", pcbnew.F_Mask), ("B.Mask", pcbnew.B_Mask),
                          ("F.Paste", pcbnew.F_Paste), ("B.Paste", pcbnew.B_Paste)) if p.IsOnLayer(layer)],
                      "kind": "npth" if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH else
                              "pth" if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH else
                              "smd" if p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD else "unsupported"}
                     for p in fp.Pads()]}


def geometry_sha256(state):
    # Full per-pad 2D copper/drill/layer geometry, multiplicity and name. Native
    # UUIDs intentionally are absent; only these two footprint trees get new IDs.
    rows = [{k: (float(v) if k == "angle_deg" else v)
             for k, v in p.items() if k != "net"} for p in state["pads"]]
    raw = json.dumps(sorted(rows, key=lambda p: json.dumps(p, sort_keys=True)),
                     sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def verify_transition(before, after, project):
    if project != PROJECT:
        raise ValueError("USB migration is restricted to the exact RF project")
    expected_names = Counter({name: 4 if name == "SH" else 1 for name in SIGNALS})
    for state, fpid, value, anchor, geometry_hash, anonymous_counts in (
        (before, BEFORE_ID, "JAE DX07S016JA1R1500", [16_469_999,146_200_000], BEFORE_GEOMETRY_SHA256, {"npth": 2, "smd": 2}),
        (after, AFTER_ID, "GCT USB4105-GF-A", [16_469_999,146_325_000], AFTER_GEOMETRY_SHA256, {"npth": 2}),
    ):
        if (state["reference"] != REFERENCE or state["footprint"] != fpid
                or state["value"] != value or state["side"] != "B.Cu"
                or state["anchor_nm"] != anchor or state["rotation_deg"] % 360 != 180):
            raise ValueError("USB migration identity or exact mouth pose changed")
        named = [p for p in state["pads"] if p["number"]]
        if Counter(p["number"] for p in named) != expected_names:
            raise ValueError("USB migration lost or added a named electrical pad")
        for pad in named:
            if pad["net"] != SIGNALS[pad["number"]]:
                raise ValueError("USB migration changed an exact product pad/net binding")
            if pad["kind"] != ("pth" if pad["number"] == "SH" else "smd"):
                raise ValueError("USB named pad technology changed")
        anonymous = [p for p in state["pads"] if not p["number"]]
        if any(p["net"] for p in anonymous) or Counter(p["kind"] for p in anonymous) != Counter(anonymous_counts):
            raise ValueError("USB migration permits only two exact anonymous no-net JAE SMD lands to disappear")
        if geometry_sha256(state) != geometry_hash:
            raise ValueError("USB exact reviewed pad/drill/layer geometry changed")
    return {"feature_id": FEATURE_ID, "reference": REFERENCE,
            "named_pad_net_occurrences_preserved": 20, "logical_contacts_preserved": 17,
            "removed_anonymous_no_net_smd_lands": 2, "npth_locators_before_after": [2,2],
            "fabrication_ready": False}


def verify_allowance(allowance, project, review_path):
    expected = {"feature_id": FEATURE_ID,
                "source_review_sha256": hashlib.sha256(review_path.read_bytes()).hexdigest()}
    if project != PROJECT or allowance != expected:
        raise ValueError("unreviewed exact USB migration allowance")
    review = json.loads(review_path.read_text())
    if (review["feature_id"] != FEATURE_ID or review["project"] != PROJECT
            or review["before_footprint"] != BEFORE_ID or review["after_footprint"] != AFTER_ID
            or review["changed_references"] != ["J1", "U5"]
            or review["production_release_authorized"] is not False):
        raise ValueError("USB review no longer describes the finite two-reference migration")
    return expected


def verify_companion(before, after, project):
    """U5 is only the reviewed 0.15-mm translation, not a general repack."""
    if project != PROJECT:
        raise ValueError("USB companion move is RF-only")
    for state, anchor in ((before, [16_500_000,139_500_000]),
                          (after, [16_500_000,139_350_000])):
        if (state["reference"] != "U5" or state["side"] != "B.Cu"
                or state["rotation_deg"] % 360 != 0 or state["anchor_nm"] != anchor
                or state["value"] != "Texas Instruments TPD4S201RUKR"
                or state["footprint"] != "Package_DFN_QFN:Texas_RUK0020B_WQFN-20-1EP_3x3mm_P0.4mm_EP1.7x1.7mm"):
            raise ValueError("USB companion identity or exact 0.15-mm move changed")
    normalized = []
    for state in (before, after):
        pads = [{**p, "at_nm": [p["at_nm"][i]-state["anchor_nm"][i] for i in (0,1)]}
                for p in state["pads"]]
        normalized.append((geometry_sha256({"pads": pads}), Counter((p["number"],p["net"]) for p in pads)))
    if normalized[0] != normalized[1]:
        raise ValueError("USB companion changed pad geometry or net rather than translating")
    return {"reference": "U5", "translation_nm": [0,-150000], "pad_geometry_and_nets_preserved": True}


def require_no_old_copper_attachments(board, references, pcbnew):
    """Moving an already routed pad is not authorized by raw-copper retention."""
    if sorted(references) != ["J1", "U5"]:
        raise ValueError("USB transition requires exactly J1 and its U5 clearance move")
    board.BuildConnectivity()
    connectivity = board.GetConnectivity()
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    for ref in references:
        for pad in fps[ref].Pads():
            if any(isinstance(item, pcbnew.PCB_TRACK) for item in connectivity.GetConnectedItems(pad)):
                raise ValueError(f"USB migration would detach existing copper from {ref}.{pad.GetNumber()}")
            # KiCad's electrical graph omits no-net copper. Anonymous JAE lands
            # therefore also need a physical intersection check, not a graph
            # assertion which would silently ignore an attached no-net track.
            for layer in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu,
                          pcbnew.In3_Cu, pcbnew.In4_Cu, pcbnew.B_Cu):
                if not pad.IsOnLayer(layer):
                    continue
                shape = pad.GetEffectiveShape(layer)
                for copper in board.GetTracks():
                    if copper.IsOnLayer(layer) and shape.Collide(copper.GetEffectiveShape(), 0):
                        raise ValueError(f"USB migration would move a pad touching existing copper at {ref}.{pad.GetNumber()}")


def named_connectivity(board):
    """Stable full named-pad/copper adjacency, independent of changed pad UUIDs."""
    board.BuildConnectivity()
    conn = board.GetConnectivity()
    items, keys = [], {}
    for fp in board.GetFootprints():
        counts = Counter()
        for pad in fp.Pads():
            if not pad.GetNumber():
                continue
            name = pad.GetNumber(); occurrence = counts[name]; counts[name] += 1
            items.append(pad)
            keys[pad.m_Uuid.AsString()] = ("pad", fp.GetReference(), name, occurrence)
    for item in board.GetTracks():
        items.append(item); keys[item.m_Uuid.AsString()] = ("copper", item.m_Uuid.AsString())
    return {keys[item.m_Uuid.AsString()]: (item.GetNetname(), tuple(sorted(
                keys[other.m_Uuid.AsString()] for other in conn.GetConnectedItems(item)
                if other.m_Uuid.AsString() in keys))) for item in items}
