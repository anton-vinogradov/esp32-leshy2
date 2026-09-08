#!/usr/bin/env python3
"""Stage a reviewed placement change without ever writing the production PCB.

The seed generator is not a routed-board updater. This adapter admits only
explicitly named footprint changes, retains the original copper S-expressions,
and verifies both the generated placement projection and native copper after a
KiCad round trip. A fresh DRC and a separate reviewed promotion remain required.
Run with KiCad's bundled Python. The plan is a JSON file, not executable code.
"""

import argparse
from collections import Counter
import hashlib
import json
import difflib
from pathlib import Path
import re
import tempfile
import uuid

import pcbnew
import h6_r2_placement as placement
from h6_r2_manual_copper import copper_signature
import h6_r2_microsd_recess as microsd
import h6_r2_encoder_fit as encoder
import h6_r2_speaker_fit as speaker
import h6_r2_usb_unification as usb

ROOT = Path(__file__).resolve().parents[2]
UUID_FORM = re.compile(r'(\(uuid\s+)"([^"\\]*)"')
STAGE_UUID_NAMESPACE = uuid.UUID("f045ab10-0a1b-4b7a-82d6-013d4e8bc4f2")
PLACEMENT_INPUT_ATTRIBUTES = (
    "CONTRACT_PATH", "FREEZE_PATH", "PLACEMENT_PATH", "COORDINATE_PATH",
    "INSTANCE_PATH", "NET_PATH", "SYMBOL_PATH", "NET_BINDING_PATH",
    "SPEAKER_BODY_PATH", "SPEAKER_HELPER_PATH",
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def forms(text):
    start = text.index("(kicad_pcb")
    end = placement._balanced_form_end(text, start)
    cursor = start + len("(kicad_pcb")
    while cursor < end - 1:
        while text[cursor].isspace():
            cursor += 1
        if cursor == end - 1:
            break
        stop = placement._balanced_form_end(text, cursor)
        form = text[cursor:stop]
        head = re.match(r"\(\s*([^\s()]+)", form).group(1)
        yield head, form
        cursor = stop


def canonical(form):
    return re.sub(r'(\(uuid\s+)"[0-9a-fA-F-]+"', r'\1"<uuid>"', form)


def normalize_interform_whitespace(text):
    """Clean gaps left by removed labels, never whitespace inside an object.

    Top-level form contents and order remain byte-identical, including copper,
    multiline strings and UUIDs. Native serialization is not needed for this
    purely inter-object formatting operation.
    """
    original_forms = list(forms(text))
    result = "(kicad_pcb\n\t" + "\n\t".join(form for _, form in original_forms) + "\n)\n"
    if list(forms(result)) != original_forms:
        raise ValueError("inter-object formatting altered a native object")
    return result


def native_uuids(text):
    return [str(uuid.UUID(match.group(2))) for match in UUID_FORM.finditer(text)]


def require_unique_uuids(text):
    counts = Counter(native_uuids(text))
    duplicates = sorted(value for value, count in counts.items() if count != 1)
    if duplicates:
        raise ValueError("duplicate native object UUIDs: " + ", ".join(duplicates[:8]))


def fresh_object_uuids(form, identity, occupied):
    """Replace only UUID declarations, never schematic paths or other fields.

    The seed numbers UUIDs across the entire board. Its IDs cannot be spliced
    into an older board: changed object counts shift IDs into untouched parts.
    A separate deterministic namespace plus an explicit occupied-set test keeps
    every untouched native object and copper identity intact.
    """
    if re.search(r'\(\s*group(?:\s|\))', form):
        raise ValueError("grouped native objects require explicit UUID-membership migration")
    index = 0

    def replace(match):
        nonlocal index
        attempt = 0
        while True:
            value = str(uuid.uuid5(STAGE_UUID_NAMESPACE, f"{identity}:{index}:{attempt}"))
            if value not in occupied:
                break
            attempt += 1
        occupied.add(value)
        index += 1
        return match.group(1) + json.dumps(value)

    return UUID_FORM.sub(replace, form)


def footprint_forms(text):
    result = {}
    for head, form in forms(text):
        if head != "footprint":
            continue
        match = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', form)
        if not match or match.group(1) in result:
            raise ValueError("missing or duplicate native footprint reference")
        result[match.group(1)] = form
    return result


def footprints(text):
    return {ref: canonical(form) for ref, form in footprint_forms(text).items()}


def copper_forms(text):
    return [form for head, form in forms(text)
            if head in {"segment", "arc", "via", "group"}
            or (head == "zone" and "(keepout" not in form)]


def edge_cut_forms(text):
    return [(head, form) for head, form in forms(text)
            if re.search(r'\(layer\s+"Edge\.Cuts"\)', form) and head.startswith("gr_")]


def edge_cut_key(head, form):
    """Native geometric identity, including width; no UUID/format dependence."""
    if head not in {"gr_line", "gr_arc"}:
        raise ValueError("unsupported Edge.Cuts object in reviewed recess update")
    result = [head]
    for field in ("start", "mid", "end") if head == "gr_arc" else ("start", "end"):
        match = re.search(r'\(' + field + r'\s+([-\d.eE+]+)\s+([-\d.eE+]+)\)', form)
        if not match:
            raise ValueError("malformed Edge.Cuts geometry")
        result.append(tuple(round(float(v) * 1_000_000) for v in match.groups()))
    widths = re.findall(r'\(width\s+([-\d.eE+]+)\)', form)
    if len(widths) != 1:
        raise ValueError("malformed Edge.Cuts width")
    result.append(round(float(widths[0]) * 1_000_000))
    return tuple(result)


def primitive_edge_keys(primitives):
    board = pcbnew.BOARD()
    for primitive in primitives:
        if primitive[0] == "gr_line":
            placement.add_segment(board, pcbnew.Edge_Cuts, *primitive[1:], 0.05)
        else:
            placement.add_arc(board, pcbnew.Edge_Cuts, *primitive[1:], 0.05)
    text = placement.board_bytes("reviewed-microsd-edge", board).decode()
    return Counter(edge_cut_key(head, form) for head, form in edge_cut_forms(text))


def reviewed_edge_cut_changes(before, seed, allowance, project, contract):
    """Only UI-MICROSD-RECESS-001 may replace its one original bottom line.

    The full old/new Edge.Cuts multiset must differ by precisely the reviewed
    seven primitives. FPC, corner arcs, extra holes, width changes and arbitrary
    hash-only board edits cannot hide behind this allowance.
    """
    old = [(edge_cut_key(h, f), f) for h, f in edge_cut_forms(before)]
    new = [(edge_cut_key(h, f), f) for h, f in edge_cut_forms(seed)]
    old_keys, new_keys = Counter(k for k, _ in old), Counter(k for k, _ in new)
    if allowance is None:
        if old_keys != new_keys:
            raise ValueError("unreviewed Edge.Cuts change")
        return [], []
    expected_allowance = {
        "feature_id": microsd.FEATURE_ID,
        "source_contract_sha256": sha(placement.CONTRACT_PATH.read_bytes()),
    }
    if allowance != expected_allowance or project != microsd.PROJECT:
        raise ValueError("invalid exact microSD Edge.Cuts authorization")
    if microsd.feature(contract, project) is None:
        raise ValueError("microSD recess contract missing")
    expected_old = primitive_edge_keys([("gr_line", (78, 150), (2, 150))])
    expected_new = primitive_edge_keys(microsd.bottom_edge_primitives(contract, project))
    if old_keys - new_keys != expected_old or new_keys - old_keys != expected_new:
        raise ValueError("Edge.Cuts delta is not exactly the reviewed microSD recess")
    if any(old_keys[k] != 1 for k in expected_old) or any(new_keys[k] != 1 for k in expected_new):
        raise ValueError("duplicate microSD Edge.Cuts primitive")
    return ([form for key, form in old if key in expected_old],
            [form for key, form in new if key in expected_new])


def reviewed_label_forms(text, allowed):
    result = []
    for head, form in forms(text):
        if head != "gr_text":
            continue
        match = re.match(r'\(gr_text\s+("(?:\\.|[^"\\])*")', form)
        if match and json.loads(match.group(1)) in allowed:
            # KiCad serializes the same front layer as F.SilkS or
            # F.Silkscreen across supported native-file versions.
            if not re.search(r'\(layer\s+"F\.(?:SilkS|Silkscreen)"\)', form):
                raise ValueError("label migration may only touch outward F.Silkscreen")
            result.append((json.loads(match.group(1)), form))
    return result


def reviewed_label_changes(before, seed, moves, additions):
    """Admit named moves and exactly one new outward label per added text.

    Additions are not a rename/removal escape hatch. The final full placement
    projection still rejects every other board-graphics difference.
    """
    for allowance in (moves, additions):
        if (not isinstance(allowance, list)
                or not all(isinstance(text, str) and text for text in allowance)
                or len(allowance) != len(set(allowance))):
            raise ValueError("silkscreen allowance must be a unique list of exact texts")
    if set(moves) & set(additions):
        raise ValueError("silkscreen move and addition allowances must be disjoint")
    allowed = set(moves) | set(additions)
    old_labels = reviewed_label_forms(before, allowed)
    new_labels = reviewed_label_forms(seed, allowed)
    old_count = Counter(text for text, _ in old_labels)
    new_count = Counter(text for text, _ in new_labels)
    for text in moves:
        if old_count[text] == 0 or old_count[text] != new_count[text]:
            raise ValueError("label population changed; review additions/removals separately")
    for text in additions:
        if old_count[text] != 0 or new_count[text] != 1:
            raise ValueError("added silkscreen text must be absent before and occur exactly once after")
    return old_labels, new_labels


def pad_nets(fp):
    # Unnumbered copper pads can still be conductive; never silently drop them
    # from electrical preservation. Only genuinely mechanical NPTH are exempt.
    return Counter((p.GetNumber(), p.GetNetname()) for p in fp.Pads()
                   if p.GetAttribute() != pcbnew.PAD_ATTRIB_NPTH or p.GetNetname())


def reviewed_speaker_graphics(before, seed, allowance, project, allowed_references):
    """Only the reviewed C54/body step may add exactly five B.Fab objects.

    This is not a general assembly-drawing allowance: complete native B.Fab
    multisets, geometry, text, layers and input hashes are compared. Removing,
    replacing or duplicating an existing object is rejected.
    """
    if allowance is None:
        return []
    expected_allowance = {
        "feature_id": "H6-R2-SPEAKER-BODY-001",
        "source_sha256": sha(placement.SPEAKER_BODY_PATH.read_bytes()),
        "helper_sha256": sha(placement.SPEAKER_HELPER_PATH.read_bytes()),
    }
    if (allowance != expected_allowance or project != "LESHY2-UI-R2"
            or allowed_references != ["C54"]):
        raise ValueError("invalid finite speaker-body drawing authorization")

    def bfab(text):
        return [form for head, form in forms(text)
                if head.startswith("gr_") and re.search(r'\(layer\s+"B\.Fab"\)', form)]

    class Grid:
        def add(self, *args):
            pass

    spec = json.loads(placement.SPEAKER_BODY_PATH.read_text())
    reference = pcbnew.BOARD()
    speaker.add_speaker_assembly_geometry(reference, project,
        {"mechanical": {"speaker_body": spec}}, {"B.Cu": Grid()}, pcbnew)
    expected = bfab(placement.board_bytes("speaker-body-reference", reference).decode())
    if len(expected) != 5:
        raise ValueError("speaker helper no longer emits the reviewed five objects")
    old_forms, new_forms = bfab(before), bfab(seed)
    old = Counter(canonical(form) for form in old_forms)
    new = Counter(canonical(form) for form in new_forms)
    required = Counter(canonical(form) for form in expected)
    if (len(required) != 5 or any(old[key] for key in required)
            or old-new or new-old != required):
        raise ValueError("B.Fab delta is not exactly the reviewed speaker body and label")
    return [form for form in new_forms if canonical(form) in required]


def verify_pad_nets(reference, before, after, allowance):
    if isinstance(allowance, list):
        if not all(isinstance(pin, str) and pin for pin in allowance):
            raise ValueError(f"{reference}: removal needs identified pad numbers")
        expected = Counter(allowance)
    elif isinstance(allowance, dict):
        if not all(isinstance(pin, str) and pin and type(count) is int and count > 0
                   for pin, count in allowance.items()):
            raise ValueError(f"{reference}: invalid exact pad-removal multiplicity")
        expected = Counter(allowance)
    else:
        raise ValueError(f"{reference}: invalid pad-removal allowance")
    if after - before:
        raise ValueError(f"{reference}: added or reassigned electrical pad")
    removed = before - after
    for (pin, net), count in removed.items():
        if not pin or net:
            raise ValueError(f"{reference}.{pin}: unidentified or connected pad removal")
    actual = Counter({pin: count for (pin, _net), count in removed.items()})
    if actual != expected:
        raise ValueError(f"{reference}: unreviewed pad-removal multiplicity; actual={dict(actual)}, reviewed={dict(expected)}")


def input_snapshot(source):
    """Snapshot the actual generator inputs before, after build and publication."""
    paths = {source, Path(__file__), *(getattr(placement, name) for name in PLACEMENT_INPUT_ATTRIBUTES)}
    paths.update(ROOT / "hardware/layout" / name for name in (
        "h6_r2_placement.py", "h6_r2_coordinates.py", "h6_r2_user_silkscreen.py",
        "h6_r2_microsd_recess.py", "h6_r2_encoder_fit.py", encoder.GEOMETRY_NAME,
        "h6_r2_usb_unification.py", usb.REVIEW_NAME))
    paths.add(ROOT / "hardware/ecad/h2_r2_encoder_footprint.py")
    paths.update((ROOT / "hardware/ecad/libraries").rglob("*.kicad_mod"))
    rows = json.loads(placement.INSTANCE_PATH.read_text())["rows"]
    for row in rows:
        library, name = placement.footprint_library(row["footprint"])
        paths.add(Path(library) / (name + ".kicad_mod"))
    paths.add(placement.KICAD_FOOTPRINT_ROOT / "MountingHole.pretty/MountingHole_2.7mm_M2.5.kicad_mod")
    return {str(path.resolve()): sha(path.read_bytes()) for path in sorted(paths)}


def require_same_inputs(source, before):
    if input_snapshot(source) != before:
        raise ValueError("placement inputs changed concurrently; discard this candidate")


def load_board_bytes(data, name):
    with tempfile.TemporaryDirectory(prefix="leshy2-stage-validation-") as temporary:
        path = Path(temporary) / name
        path.write_bytes(data)
        return pcbnew.LoadBoard(str(path))


def roundtrip_copper_forms(board):
    with tempfile.TemporaryDirectory(prefix="leshy2-stage-copper-") as temporary:
        path = Path(temporary) / "copper.kicad_pcb"
        if not pcbnew.SaveBoard(str(path), board):
            raise ValueError("KiCad failed to serialize native copper for comparison")
        return Counter(copper_forms(path.read_text()))


def verify_changed_references(before, after, allowed):
    if (not isinstance(allowed, list) or not all(isinstance(ref, str) and ref for ref in allowed)
            or len(allowed) != len(set(allowed))):
        raise ValueError("allowed references must be a unique list of exact references")
    if set(before) != set(after):
        raise ValueError("footprint population changed; this updater cannot add/remove components")
    if set(allowed) - set(before):
        raise ValueError("allowed references include unknown native components")
    changed = {ref for ref in before if before[ref] != after[ref]}
    unexpected = changed - set(allowed)
    if unexpected:
        first = sorted(unexpected)[0]
        delta = "\n".join(difflib.unified_diff(before[first].splitlines(), after[first].splitlines()))
        raise ValueError("unreviewed footprint changes: " + ", ".join(sorted(unexpected))
                         + "\nFirst footprint diff (" + first + "):\n" + delta)
    return sorted(changed)


def stage(plan, directory):
    plan = json.loads(json.dumps(plan))
    directory = Path(directory)
    project = plan["project"]
    if project not in {"LESHY2-UI-R2", "LESHY2-RF-R2"}:
        raise ValueError("unsupported board")
    source = ROOT / f"hardware/ecad/kicad/{project}/{project}.kicad_pcb"
    original = source.read_bytes()
    if sha(original) != plan["baseline_board_sha256"]:
        raise ValueError("production board changed since the placement review")
    require_unique_uuids(original.decode())
    target = directory / source.name
    receipt_path = directory / "stage-review.json"
    if target.resolve() == source.resolve() or target.exists() or receipt_path.exists():
        raise ValueError("staging requires a new scratch output, never the live PCB")

    inputs_before = input_snapshot(source)
    outputs, audit = placement.build()
    require_same_inputs(source, inputs_before)
    scoped = next(row for row in audit["boards"] if row["project"] == project)
    if (scoped["hard_conflicts"] or scoped["placement_failures"]
            or scoped["net_or_footprint_errors"]
            or scoped["locality"]["status"] != "pass"
            or scoped["critical_pad_pairs"]["status"] != "pass"):
        raise ValueError("selected board placement audit is not passing")
    seed = outputs[source].decode()
    require_unique_uuids(seed)
    old = load_board_bytes(original, source.name)
    # KiCad supplies omitted defaults (e.g. hidden-field font thickness) on
    # reload. Compare both after the same native normalization, never suppress
    # a real geometry/property difference with a blanket allow-list.
    before_projection = placement.placement_signature_bytes(project, old)
    seed_projection = placement.placement_signature_from_board_bytes(project, outputs[source])
    changed = verify_changed_references(footprints(before_projection.decode()),
                                        footprints(seed_projection.decode()), plan["allowed_references"])
    if plan.get("allowed_speaker_body_addition") is not None and changed != ["C54"]:
        raise ValueError("speaker-body stage requires exactly the reviewed C54 relocation")
    if copper_forms(seed):
        raise ValueError("unexpected copper/group in placement seed")
    if re.search(r'\(\s*group(?:\s|\))', original.decode()):
        raise ValueError("grouped native objects require explicit UUID-membership migration")
    preserved = copper_forms(original.decode())
    # Keep every unchanged footprint, drawing, rule area and copper form byte
    # for byte. A generator-wide UUID churn must not become the user-facing
    # diff for eleven local placements. The final projection check rejects any
    # independent board-graphics/setup change that needs its own review.
    old_forms, new_forms = footprint_forms(original.decode()), footprint_forms(seed)
    merged = original.decode()
    occupied = set(native_uuids(merged))
    for ref in changed:
        replacement = fresh_object_uuids(new_forms[ref], f"{sha(original)}:footprint:{ref}:{sha(new_forms[ref].encode())}", occupied)
        merged = merged.replace(old_forms[ref], replacement, 1)
    labels = plan.get("allowed_silkscreen_texts", [])
    additions = plan.get("allowed_added_silkscreen_texts", [])
    old_labels, new_labels = reviewed_label_changes(original.decode(), seed, labels, additions)
    for _, form in old_labels:
        merged = merged.replace(form, "", 1)
    if new_labels:
        replacement_labels = [fresh_object_uuids(form, f"{sha(original)}:label:{index}:{sha(form.encode())}", occupied)
                              for index, (_, form) in enumerate(new_labels)]
        merged = merged.rstrip()[:-1] + "\n" + "\n".join(replacement_labels) + "\n)\n"
    old_edges, new_edges = reviewed_edge_cut_changes(
        original.decode(), seed, plan.get("allowed_edge_cut_change"), project,
        json.loads(placement.CONTRACT_PATH.read_text()))
    for form in old_edges:
        merged = merged.replace(form, "", 1)
    if new_edges:
        replacements = [fresh_object_uuids(form, f"{sha(original)}:microsd-edge:{index}:{sha(form.encode())}", occupied)
                        for index, form in enumerate(new_edges)]
        merged = merged.rstrip()[:-1] + "\n" + "\n".join(replacements) + "\n)\n"
    speaker_forms = reviewed_speaker_graphics(original.decode(), seed,
        plan.get("allowed_speaker_body_addition"), project, plan["allowed_references"])
    if speaker_forms:
        replacements = [fresh_object_uuids(form,
                        f"{sha(original)}:speaker-body:{index}:{sha(form.encode())}", occupied)
                        for index, form in enumerate(speaker_forms)]
        merged = merged.rstrip()[:-1] + "\n" + "\n".join(replacements) + "\n)\n"
    merged = normalize_interform_whitespace(merged)
    require_unique_uuids(merged)
    if copper_forms(merged) != preserved:
        raise ValueError("serialized copper/group changed while replacing footprints")
    new = load_board_bytes(merged.encode(), source.name)
    if speaker_forms:
        speaker.check_native_speaker_geometry(new, project, pcbnew)
    old_fps = {fp.GetReference(): fp for fp in old.GetFootprints()}
    new_fps = {fp.GetReference(): fp for fp in new.GetFootprints()}
    removals = plan.get("allowed_removed_nc_pads", {})
    if not isinstance(removals, dict) or set(removals) - set(changed):
        raise ValueError("pad-removal allowances must identify changed footprints only")
    usb_review = None
    usb_allowance = plan.get("usb_unification_update")
    if usb_allowance is not None:
        usb.verify_allowance(usb_allowance, project, ROOT / "hardware/layout" / usb.REVIEW_NAME)
        if changed != ["J1", "U5"] or sorted(plan["allowed_references"]) != changed or removals:
            raise ValueError("USB migration must change exactly J1/U5 without any generic pad-removal waiver")
        usb.require_no_old_copper_attachments(old, changed, pcbnew)
        usb_review = usb.verify_transition(usb.snapshot(old_fps[usb.REFERENCE], pcbnew),
                                          usb.snapshot(new_fps[usb.REFERENCE], pcbnew), project)
        usb_review["companion"] = usb.verify_companion(usb.snapshot(old_fps["U5"], pcbnew),
                                                       usb.snapshot(new_fps["U5"], pcbnew), project)
        before_graph, after_graph = usb.named_connectivity(old), usb.named_connectivity(new)
        if before_graph != after_graph:
            raise ValueError("USB migration changed named-pad/copper connectivity")
        usb_review["named_pad_copper_adjacency_nodes_preserved"] = len(before_graph)
        usb_review["old_copper_attachments_at_changed_references"] = 0
    encoder_review = None
    encoder_allowance = plan.get("encoder_geometry_update")
    if encoder_allowance is not None:
        encoder.verify_allowance(encoder_allowance, project, ROOT / "hardware/layout" / encoder.GEOMETRY_NAME)
        if encoder.REFERENCE not in changed or encoder.REFERENCE in removals:
            raise ValueError("encoder transition must be a changed footprint without pad-removal waiver")
        encoder_review = encoder.verify_transition(encoder.snapshot(old_fps[encoder.REFERENCE], pcbnew),
                                                   encoder.snapshot(new_fps[encoder.REFERENCE], pcbnew))
    for ref in old_fps:
        if usb_review is not None and ref == usb.REFERENCE:
            continue
        if encoder_review is not None and ref == encoder.REFERENCE:
            continue
        verify_pad_nets(ref, pad_nets(old_fps[ref]), pad_nets(new_fps[ref]), removals.get(ref, []))
    if (copper_signature(old) != copper_signature(new)
            or roundtrip_copper_forms(old) != roundtrip_copper_forms(new)):
        raise ValueError("copper/net geometry changed while staging")
    if placement.placement_signature_bytes(project, new) != seed_projection:
        raise ValueError("staged board does not match generated placement")
    if source.read_bytes() != original:
        raise ValueError("production changed concurrently; discard this candidate")
    require_same_inputs(source, inputs_before)
    result = {"schema_version": 1, "status": "staged_pending_fresh_drc",
              "fabrication_ready": False, "production_written": False,
              "project": project, "baseline_board_sha256": sha(original),
              "candidate_sha256": sha(merged.encode()),
              "candidate": str(target), "changed_references": changed,
              "reviewed_silkscreen_texts": sorted(labels),
              "reviewed_added_silkscreen_texts": sorted(additions),
              "reviewed_edge_cut_change": plan.get("allowed_edge_cut_change"),
              "reviewed_encoder_geometry_change": encoder_review,
              "reviewed_usb_unification": usb_review,
              "reviewed_speaker_body_addition": plan.get("allowed_speaker_body_addition"),
              "speaker_body_graphics_added": len(speaker_forms),
              "edge_cut_primitives_removed_added": [len(old_edges), len(new_edges)],
              "unchanged_reference_count": len(old_fps) - len(changed),
              "copper_objects_preserved": len(copper_signature(old)),
              "copper_forms_preserved_exact": len(preserved),
              "native_uuid_uniqueness": "pass",
              "placement_projection": "pass", "electrical_pad_net_preservation": "pass",
              "source_contract_sha256": inputs_before[str(placement.CONTRACT_PATH.resolve())],
              "placement_inputs_sha256": inputs_before,
              "limits": ["No new routing, full DRC, optical, mechanical or factory qualification is implied.",
                         "Moved pad/copper attachments require a separately reviewed local-change audit."]}
    # Publish no candidate until all native checks and input guards have passed.
    # Exclusive creation also refuses an output supplied concurrently by another
    # task; no previous scratch candidate or review receipt is overwritten.
    directory.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as stream:
        stream.write(merged)
    with receipt_path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(stage(json.loads(args.plan.read_text()), args.output_directory), indent=2))


if __name__ == "__main__":
    main()
