#!/usr/bin/env python3
"""Reconcile every intentional no-connect with a physical pin, marker and rationale."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from h2_symbol_library import embedded_symbols, matching_paren


REPO = Path(__file__).resolve().parents[2]
ECAD = REPO / "hardware/ecad"
GENERATED = ECAD / "generated"
CANDIDATE = REPO / "hardware/architecture/candidates/G2F-3I.json"
ACCESSORY = REPO / "hardware/accessories/leshy2-lora-cap-01.json"
OUTPUT = GENERATED / "H2-REV62-no-connects.json"
DOC_EN = REPO / "docs/no-connects.md"
DOC_RU = REPO / "docs/no-connects.ru.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def top_symbol_blocks(text: str) -> list[str]:
    blocks = []
    cursor = 0
    marker = "\n\t(symbol\n"
    while True:
        found = text.find(marker, cursor)
        if found < 0:
            return blocks
        start = found + 2
        end = matching_paren(text, start)
        blocks.append(text[start:end])
        cursor = end


def pin_map(definition: str) -> dict[str, list[tuple[str, float, float]]]:
    result: dict[str, list[tuple[str, float, float]]] = {}
    cursor = 0
    while True:
        match = re.search(r"\(pin\s+[^\s()]+\s+[^\s()]+", definition[cursor:])
        if not match:
            return result
        start = cursor + match.start()
        block = definition[start:matching_paren(definition, start)]
        name = re.search(r'\(name "([^"]+)"', block)
        number = re.search(r'\(number "([^"]+)"', block)
        at = re.search(r"\(at (-?[0-9.]+) (-?[0-9.]+) (-?[0-9.]+)\)", block)
        if name and number and at:
            result.setdefault(name.group(1), []).append((number.group(1), float(at.group(1)), float(at.group(2))))
        cursor = start + len(block)


def nc_points(text: str) -> set[tuple[float, float]]:
    return {
        (round(float(x), 2), round(float(y), 2))
        for x, y in re.findall(r"\(no_connect \(at (-?[0-9.]+) (-?[0-9.]+)\)", text)
    }


def route_rationales() -> dict[str, str]:
    result = {}
    for path in (CANDIDATE, ACCESSORY):
        for route in json.loads(path.read_text(encoding="utf-8"))["fixed_routes"]:
            abstract_from = route["from"].startswith("abstract:no-connect")
            abstract_to = route["to"].startswith("abstract:no-connect")
            if abstract_from ^ abstract_to:
                endpoint = route["to"] if abstract_from else route["from"]
                result[endpoint] = route.get("safety", "").strip()
    return result


def fallback_rationale(endpoint: str) -> str:
    instance, contact = endpoint.split(".", 1)
    if endpoint.startswith("display_panel_connector.FITTING_"):
        return "mechanical hold-down contact has no electrical function"
    if endpoint in {"cap_header.PIN_1", "cap_header.PIN_2"}:
        return "stock U214 GNSS UART contact is deliberately unused by the radio-only Leshy Cap"
    if endpoint.startswith("s3.NC_PSRAM_GPIO"):
        return "N16R8 octal PSRAM consumes this package-visible carrier pad internally"
    if endpoint.startswith("display.NC_"):
        return "display assembly identifies this physical tail contact as no-connect"
    if endpoint in {"display.TE", "display_touch_controller.TE"}:
        return "tearing-effect output is not required by the bounded direct-QSPI update contract"
    if endpoint == "display.RD_UNUSED":
        return "the selected direct-QSPI display path is write-only and needs no parallel read strobe"
    if re.match(r"(?:u214_esd_[abc]|unit_esd)\.NC_", endpoint):
        return "manufacturer NC pad of the fitted ESD protector remains open"
    if endpoint in {"slow_io_fault_sense_iso.NC", "slow_io_s3_evidence_iso.NC"}:
        return "manufacturer NC pad of the selected isolation device remains open"
    if endpoint == "evidence_driver.NC":
        return "manufacturer NC pad of the open-drain evidence driver remains open"
    if endpoint == "rf_detector.FLTR":
        return "optional detector filter pin is left open for the selected fast envelope response"
    if endpoint == "rf_detector.V_DN":
        return "optional detector output-divider pin is unused for the selected full-scale output"
    if endpoint == "variant_module.DIO3_TCXO":
        return "the selected module owns TCXO control internally; the host leaves DIO3 open"
    if endpoint.startswith("variant_module.NC_"):
        return "manufacturer NC module pad remains open"
    if endpoint in {"identity.NC", "local_regulator.NC"}:
        return "manufacturer NC package pad remains open"
    if instance == "c5" and contact in {"GPIO2", "GPIO3", "GPIO5", "GPIO25", "GPIO26"}:
        return "unallocated physical C5 GPIO remains open and has no hidden product role"
    if instance == "c5" and contact.startswith("NC_"):
        return "module/package contract marks this physical C5 contact unavailable or no-connect"
    if endpoint == "ir_power_switch.NC":
        return "manufacturer NC pad of the IR load switch remains open"
    raise ValueError(f"no written rationale for {endpoint}")


def schematic_for(manifest: dict) -> Path:
    project = manifest["project"]
    sheet = manifest.get("sheet") or manifest.get("root_sheet")
    if project in {"LESHY2-LORA-CAP-01", "L2-DISP-ADP-001-A"} and sheet in {"CAP_00_ROOT", "ADP_00_DISPLAY_ADAPTER"}:
        return ECAD / f"kicad/{project}/{project}.kicad_sch"
    return ECAD / f"kicad/{project}/{sheet}.kicad_sch"


def review_manifest(path: Path, rationales: dict[str, str]) -> tuple[dict, list[dict]]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    count = manifest.get("summary", {}).get("intentional_no_connect_pins")
    endpoints = manifest.get("intentional_no_connect_endpoints")
    if count is None and endpoints is not None:
        count = len(endpoints)
    if count is None:
        return {}, []
    if count == 0:
        if endpoints:
            raise ValueError(f"{path.name} claims zero NC but lists endpoints")
        return {"artifact": str(path.relative_to(REPO)), "sheet": manifest.get("sheet"), "count": 0}, []
    if endpoints is None or len(endpoints) != count or len(endpoints) != len(set(endpoints)):
        raise ValueError(f"{path.name} NC endpoint accounting differs from count={count}")
    schematic = schematic_for(manifest)
    text = schematic.read_text(encoding="utf-8")
    definitions = dict(embedded_symbols(text))
    instances = {row["instance"]: row for row in manifest.get("instances", [])}
    if "host_connector" in manifest:
        host = manifest["host_connector"]
        instances[host["instance"]] = {"symbol_uuid": host["symbol_uuid"], "reference": host["reference"]}
    blocks = {}
    for block in top_symbol_blocks(text):
        uuid = re.search(r'\(uuid "([^"]+)"\)', block)
        lib_id = re.search(r'\(lib_id "Leshy2:([^"]+)"\)', block)
        at = re.search(r"\(at (-?[0-9.]+) (-?[0-9.]+) (-?[0-9.]+)\)", block)
        if uuid and lib_id and at:
            blocks[uuid.group(1)] = (lib_id.group(1), float(at.group(1)), float(at.group(2)), float(at.group(3)))
    markers = nc_points(text)
    rows = []
    for endpoint in endpoints:
        instance, contact = endpoint.split(".", 1)
        if instance not in instances:
            raise ValueError(f"{path.name}/{endpoint}: instance absent from manifest")
        symbol_uuid = instances[instance]["symbol_uuid"]
        if symbol_uuid not in blocks:
            raise ValueError(f"{path.name}/{endpoint}: placed symbol UUID absent")
        lib_id, sx, sy, rotation = blocks[symbol_uuid]
        if rotation != 0:
            raise ValueError(f"{path.name}/{endpoint}: unsupported generated symbol rotation {rotation}")
        pins = pin_map(definitions[lib_id]).get(contact, [])
        if not pins:
            raise ValueError(f"{path.name}/{endpoint}: physical contact absent from {lib_id}")
        matched = [number for number, px, py in pins if (round(sx + px, 2), round(sy - py, 2)) in markers]
        if len(matched) != 1:
            raise ValueError(f"{path.name}/{endpoint}: exact NC marker does not map to one physical pin")
        rationale = rationales.get(endpoint) or fallback_rationale(endpoint)
        if not rationale:
            raise ValueError(f"{path.name}/{endpoint}: empty rationale")
        rows.append({
            "endpoint": endpoint,
            "physical_pin": matched[0],
            "symbol": lib_id,
            "marker": "present",
            "rationale": rationale,
        })
    if len(markers) != count:
        raise ValueError(f"{path.name}: schematic has {len(markers)} NC markers, expected {count}")
    return {
        "artifact": str(path.relative_to(REPO)),
        "schematic": str(schematic.relative_to(REPO)),
        "sheet": manifest.get("sheet") or manifest.get("root_sheet"),
        "count": count,
    }, rows


def render_doc(manifest: dict, russian: bool) -> str:
    if russian:
        title = "# Намеренно неподключённые контакты Leshy2"
        nav = "[English](no-connects.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md)"
        intro = "Это полный реестр физических NC H2.6.2. Каждая строка проверена по символу, точному контакту и NC-маркеру KiCad; причина не заменяется общим словом «резерв»."
        headers = "| Лист | Контакт | Физический pin | Обоснование |\n|---|---|---:|---|"
    else:
        title = "# Leshy2 intentional no-connect register"
        nav = "[Русский](no-connects.ru.md) · [Home](../README.md) · [Roadmap](roadmap.md)"
        intro = "This is the complete H2.6.2 physical NC register. Every row is checked against its symbol, exact contact and KiCad NC marker; no generic reserve rationale is accepted."
        headers = "| Sheet | Contact | Physical pin | Rationale |\n|---|---|---:|---|"
    body = []
    for sheet in manifest["sheets"]:
        for row in sheet["endpoints"]:
            body.append(f"| `{sheet['sheet']}` | `{row['endpoint']}` | `{row['physical_pin']}` | {row['rationale']} |")
    close = (
        f"✅ **{'Проведено ревью' if russian else 'Reviewed'}:** "
        f"{manifest['summary']['intentional_no_connects']} NC / {manifest['summary']['nonzero_nc_sheets']} "
        f"{'листов; отсутствующих контактов, маркеров и обоснований нет.' if russian else 'sheets; no contact, marker or rationale is missing.'}"
    )
    evidence = "[Машинное evidence](../hardware/ecad/generated/H2-REV62-no-connects.json)." if russian else "[Machine evidence](../hardware/ecad/generated/H2-REV62-no-connects.json)."
    return "\n\n".join((title, nav, intro, headers + "\n" + "\n".join(body), close, evidence)) + "\n"


def build() -> tuple[dict[Path, str], dict]:
    rationales = route_rationales()
    sheets = []
    zero_sheets = []
    sources = {str(CANDIDATE.relative_to(REPO)): sha256(CANDIDATE), str(ACCESSORY.relative_to(REPO)): sha256(ACCESSORY)}
    for path in sorted(GENERATED.glob("H2-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if "intentional_no_connect_pins" not in data.get("summary", {}) and "intentional_no_connect_endpoints" not in data:
            continue
        sheet, endpoints = review_manifest(path, rationales)
        sources[str(path.relative_to(REPO))] = sha256(path)
        if endpoints:
            sheet["endpoints"] = endpoints
            sheets.append(sheet)
        else:
            zero_sheets.append(sheet)
    total = sum(row["count"] for row in sheets)
    if total != 189:
        raise ValueError(f"reviewed NC total drifted: {total} != 189")
    manifest = {
        "schema_version": 1,
        "stage": "H2.6.2",
        "status": "reviewed_every_intentional_no_connect",
        "method": "manifest-to-symbol-to-physical-pin-to-coordinate NC-marker reconciliation plus one written rationale per endpoint",
        "source_hashes": sources,
        "summary": {
            "reviewed_sheet_manifests": len(sheets) + len(zero_sheets),
            "nonzero_nc_sheets": len(sheets),
            "zero_nc_sheets": len(zero_sheets),
            "intentional_no_connects": total,
            "missing_physical_contacts": 0,
            "missing_kicad_markers": 0,
            "missing_rationales": 0,
        },
        "corrected_findings": [{
            "id": "H2.6.2-F01",
            "finding": "UI10 counted seven NC contacts but did not publish their exact endpoint names",
            "correction": "UI10 now emits the same explicit intentional_no_connect_endpoints register as every other populated sheet",
        }],
        "sheets": sheets,
        "zero_nc_sheet_manifests": zero_sheets,
        "open_findings": [],
    }
    outputs = {
        OUTPUT: json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        DOC_EN: render_doc(manifest, False),
        DOC_RU: render_doc(manifest, True),
    }
    return outputs, manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs, manifest = build()
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"wrote {path.relative_to(REPO)}")
    else:
        stale = [path for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            for path in stale:
                print(f"stale: {path.relative_to(REPO)}")
            return 1
        print(f"ok: H2.6.2 NC register is current; {manifest['summary']['intentional_no_connects']} endpoints")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
