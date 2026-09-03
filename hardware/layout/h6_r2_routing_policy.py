#!/usr/bin/env python3
"""Generate the fail-closed H6.0.2 routing-class audit for both R2 boards."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "hardware/layout/h6-r2-routing-policy.json"
AUDIT = ROOT / "hardware/layout/generated/H6-R2-routing-policy-audit.json"
DOC_EN = ROOT / "docs/h6-r2-routing-policy.md"
DOC_RU = ROOT / "docs/h6-r2-routing-policy.ru.md"
GENERAL_ROUTING_AUDIT = ROOT / "hardware/layout/generated/H6-R2-general-routing-audit.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


SWITCHING_NODES = {
    "AON_BUCK_SW",
    "CHARGER_BTST1",
    "CHARGER_BTST2",
    "CHARGER_PMID",
    "CHARGER_REGN",
    "CHARGER_SW1",
    "CHARGER_SW2",
    "EXT_BUCK_SW",
    "HUB_RP_VREG_LX_SW",
    "MAIN_BUCK_BST",
    "MAIN_BUCK_BST_LINK",
    "MAIN_BUCK_SW",
    "PACK_CHARGE_PUMP",
    "RF_RP_VREG_LX_SW",
    "VOICE_BUCK_SW",
}

PRIMARY_POWER_EXTRA = {
    "BATTERY_STACK_NEGATIVE_CELL_SIDE",
    "PACK_FET_COMMON_DRAIN",
    "PD_DRAIN_COPPER",
}

DISPLAY_I8080 = {"LCD_DC", "LCD_WR_N", *(f"LCD_DB{index}" for index in range(8))}

EXTERNAL_USB_PAIR_STEMS = {
    "C5_SERVICE_USB_DX_CONNECTOR",
    "HUB_RP_SERVICE_USB_DX_CONNECTOR",
    "RF_RP_SERVICE_USB_DX_CONNECTOR",
    "USB_DX_CONNECTOR",
}

RF_EXACT = {
    "AIR_LO_AC",
    "AIR_LO_CLK_RAW",
    "AIR_LO_MATCHED",
    "AIR_LO_PAD",
    "AIR_SELECTOR_RFC",
    "C5_COUPLER_TERMINATION",
    "NRF0_COUPLER_TERMINATION",
    "NRF0_REVERSE_ISOLATED_PORT",
    "NRF1_COUPLER_TERMINATION",
    "NRF1_REVERSE_ISOLATED_PORT",
    "NRF2_COUPLER_TERMINATION",
    "NRF2_REVERSE_ISOLATED_PORT",
    "S3_COUPLER_TERMINATION",
}


def is_ground(name: str) -> bool:
    return "GROUND" in name or name.endswith("_GND")


def is_rf(name: str) -> bool:
    if name in RF_EXACT:
        return True
    if name.endswith(("_RF", "_RF_50R", "_RF_SAMPLE", "_RF_SAMPLE_RAW")):
        return True
    if name.startswith(("AIR_BPF_", "AIR_LNA_", "AIR_MIXER_", "AIR_T1_", "AIR_T2_", "CC_RF_")):
        return True
    return False


def is_usb(name: str) -> bool:
    return "USB_DM" in name or "USB_DP" in name or name.startswith(("USB2_DM", "USB2_DP"))


def is_oscillator(name: str) -> bool:
    return bool(
        "XOSC" in name
        or name.endswith(("_XA", "_XB", "_XIN", "_XOUT", "_XOUT_CRYSTAL"))
        or name.startswith("RX_XTAL_")
    )


def is_clocked_digital(name: str) -> bool:
    if name.startswith(("S3_HUB_", "C5_SDIO_", "HUB_C5_SDIO_", "CAP_SPI_")):
        return True
    if name in {
        "AUDIO_BCLK", "AUDIO_DIN", "AUDIO_DOUT", "AUDIO_WS",
        "CODEC_I2S_BCLK", "CODEC_I2S_DIN_LOCAL", "CODEC_I2S_DOUT", "CODEC_I2S_WS",
        "HUB_RF_ALERT_N", "HUB_RF_CS_N", "HUB_RF_MISO", "HUB_RF_MOSI", "HUB_RF_SCK",
    }:
        return True
    if re.match(r"^NRF[0-2]_(CE|CSN|IRQ|MISO|MOSI|SCK)(_|$)", name):
        return True
    if re.match(r"^CC_(CSN|GDO[02]|MISO|MOSI|SCK|SCLK|SI|SO)(_|$)", name):
        return True
    if re.match(r"^SD_(CLK|CMD|CS|DAT[0-3]|MISO|MOSI|SCK)(_|$)", name):
        return True
    if re.match(r"^U214_(MISO|MOSI|NSS|SCK)(_|$)", name):
        return True
    if name.startswith("IR_") and "CARRIER" in name:
        return True
    return False


def is_safety(name: str) -> bool:
    tokens = (
        "SAFETY", "SAFE", "FAULT", "WATCHDOG", "ANY_TX", "EV_N", "EV_THRESH",
        "KILL_GATE", "RUN_", "POWER_COMMAND_OFF", "POWER_FAULT", "PFAIL",
        "EN_LOW_PROOF", "RESET_LOW_PROOF", "PTT", "FET_OVERRIDE", "EVIDENCE",
        "_PWR_EN", "_DOMAIN_EN", "_5V_EN", "_5V_REQ", "CHARGE_EN",
    )
    return any(token in name for token in tokens) or name in {
        "PACK_CHG_GATE", "PACK_DIAG_GATE", "PACK_DIS_GATE", "PACK_HOLD_GATE"
    }


def is_serial_control(name: str) -> bool:
    tokens = ("I2C", "UART", "SWCLK", "SWDIO", "DBG", "SERVICE_CC", "GNSS")
    return any(token in name for token in tokens)


def is_analogue(name: str) -> bool:
    tokens = (
        "ADC", "SENSE", "DETECT", "FILTER", "VMID", "MIC", "AUDIO", "HEADPHONE",
        "SPEAKER", "BTL", "BIAS", "VREF", "THRESH", "_FB", "_ILIM", "_ILM",
        "ITIMER", "DVDT", "OVLO", "PGTH", "PAM_", "TERMINATION", "SAMPLE",
        "BAND_V", "RBIAS", "DCOUPL", "NFC_", "OPTICAL_SUM", "_AC", "AC_",
        "TEMP", "DIVIDED", "QUAL_BASE", "USB_C_CC",
    )
    return any(token in name for token in tokens)


def classify(name: str, primary_power: set[str], all_rails: set[str]) -> str:
    if is_ground(name):
        return "GROUND_REFERENCE"
    if name in primary_power or name in PRIMARY_POWER_EXTRA:
        return "PRIMARY_POWER"
    if name in all_rails:
        return "POWER_BRANCH"
    if name in SWITCHING_NODES:
        return "SWITCHING_NODE"
    if is_rf(name):
        return "RF_CONTROLLED"
    if is_usb(name):
        return "USB_DIFFERENTIAL"
    if name in DISPLAY_I8080:
        return "DISPLAY_I8080"
    if is_oscillator(name):
        return "OSCILLATOR"
    if is_clocked_digital(name):
        return "CLOCKED_DIGITAL"
    if is_safety(name):
        return "SAFETY_CONTROL"
    if is_serial_control(name):
        return "SERIAL_CONTROL"
    if is_analogue(name):
        return "ANALOG_AUDIO_SENSE"
    return "GENERAL_CONTROL"


def pair_key(name: str) -> tuple[str, str] | None:
    for negative, positive in (("USB_DM", "USB_DP"), ("USB2_DM", "USB2_DP")):
        if negative in name:
            return name.replace(negative, "USB_DX"), "N"
        if positive in name:
            return name.replace(positive, "USB_DX"), "P"
    return None


def build() -> dict:
    contract = load(CONTRACT)
    bindings_path = ROOT / contract["inputs"]["net_bindings"]
    ledger_path = ROOT / contract["inputs"]["net_ledger"]
    power_path = ROOT / contract["inputs"]["power_binding"]
    placement_path = ROOT / contract["inputs"]["placement"]
    bindings = load(bindings_path)
    ledger = load(ledger_path)
    power = load(power_path)
    placement = load(placement_path)
    all_rails = set(power["rail_nets"])
    primary_power = set(power["required_reviewed_power_nets"])
    errors: list[str] = []

    if bindings["status"] != "pass" or ledger["status"] != "pass":
        errors.append("one or more exact net sources are not passing")
    if contract["stackup_binding"]["official_stackup_id"] != placement["board"]["factory_stack_candidate"]["official_stackup_id"]:
        errors.append("routing and placement stackup identities differ")
    if contract["stackup_binding"]["core_each_mm"] != placement["board"]["factory_stack_candidate"]["core_each_mm"]:
        errors.append("routing and placement stackup core thicknesses differ")

    roles_by_net: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in ledger["rows"]:
        if row["disposition"] == "connected":
            roles_by_net[(row["project"], row["net"])].add(row["role"])

    rows = []
    board_counts = {}
    seen_canonical = set()
    pair_members: dict[tuple[str, str], set[str]] = defaultdict(set)
    for project, project_data in sorted(bindings["projects"].items()):
        counts = Counter()
        for canonical, kicad_name in sorted(project_data["canonical_to_kicad"].items()):
            route_class = classify(canonical, primary_power, all_rails)
            if route_class not in contract["classes"]:
                errors.append(f"{project}:{canonical}: unknown routing class {route_class}")
            policy = contract["classes"][route_class]
            pair = pair_key(canonical)
            if pair:
                pair_members[(project, pair[0])].add(pair[1])
            rows.append({
                "project": project,
                "canonical_net": canonical,
                "kicad_net": kicad_name,
                "routing_class": route_class,
                "route_mode": policy["route_mode"],
                "geometry_release": policy["geometry_release"],
                "endpoint_roles": sorted(roles_by_net[(project, canonical)]),
            })
            counts[route_class] += 1
            seen_canonical.add(canonical)
        board_counts[project] = {
            "physical_net_count": len(project_data["canonical_to_kicad"]),
            "class_counts": {name: counts[name] for name in contract["class_order"]},
        }

    expected_global = {row["net"] for row in ledger["rows"] if row["disposition"] == "connected"}
    missing = sorted(expected_global - seen_canonical)
    unexpected = sorted(seen_canonical - expected_global)
    if missing:
        errors.append(f"{len(missing)} reviewed physical nets are not classified: {missing[:10]}")
    if unexpected:
        errors.append(f"{len(unexpected)} classified nets are absent from the reviewed ledger: {unexpected[:10]}")
    incomplete_pairs = [f"{project}:{stem}" for (project, stem), members in pair_members.items() if members != {"N", "P"}]
    if incomplete_pairs:
        errors.append("incomplete USB differential pairs: " + ", ".join(incomplete_pairs))
    display_rows = [row for row in rows if row["routing_class"] == "DISPLAY_I8080"]
    if {row["canonical_net"] for row in display_rows} != DISPLAY_I8080:
        errors.append("direct i8080 routing class does not contain exactly DB0..DB7, WR_N and DC")
    helper = contract["automatic_helper"]
    automatic_classes = set(helper["allowed_classes"])
    if automatic_classes != {"GENERAL_CONTROL"}:
        errors.append("automatic helper allow-list expanded beyond GENERAL_CONTROL")
    if any(row["route_mode"].startswith("automatic") and row["routing_class"] not in automatic_classes for row in rows):
        errors.append("a protected routing class permits automatic routing")
    copper_layers = {item.split(":", 1)[0] for item in placement["board"]["layer_intent"]}
    routable_layers = set(helper["routable_layers"])
    reserved_layers = set(helper["reserved_reference_layers"])
    if routable_layers | reserved_layers != copper_layers or routable_layers & reserved_layers:
        errors.append("automatic-helper routable and reserved layers do not partition the stack")
    if reserved_layers != {"In1.Cu", "In4.Cu"}:
        errors.append("automatic helper does not preserve both uninterrupted ground-reference layers")
    if set(helper["preferred_directions"]) != copper_layers:
        errors.append("automatic-helper preferred directions do not cover the complete copper stack")
    if helper["via_costs"] < 100 or helper["plane_via_costs"] < helper["via_costs"]:
        errors.append("automatic-helper via cost does not discourage unnecessary layer changes")
    external_pair_stems = {stem for _project, stem in pair_members if stem in EXTERNAL_USB_PAIR_STEMS}
    if external_pair_stems != EXTERNAL_USB_PAIR_STEMS:
        errors.append("the four external USB connector pairs are not all present")

    total_counts = Counter(row["routing_class"] for row in rows)
    return {
        "schema_version": 1,
        "artifact": "H6-R2 fail-closed routing-class audit",
        "marker": contract["marker"],
        "status": "pass" if not errors else "fail",
        "source_hashes": {
            str(path.relative_to(ROOT)): sha256(path)
            for path in (CONTRACT, bindings_path, ledger_path, power_path, placement_path)
        },
        "stackup_binding": contract["stackup_binding"],
        "summary": {
            "project_net_count": len(rows),
            "global_canonical_net_count": len(seen_canonical),
            "routing_class_count": len(contract["classes"]),
            "usb_pair_count": len(pair_members),
            "external_usb_port_count": len(external_pair_stems),
            "display_i8080_net_count": len(display_rows),
            "automatic_helper_class_count": len(automatic_classes),
            "unclassified_net_count": len(missing),
            "unexpected_net_count": len(unexpected),
        },
        "class_counts": {name: total_counts[name] for name in contract["class_order"]},
        "boards": board_counts,
        "automatic_helper": contract["automatic_helper"],
        "rows": rows,
        "authorization": contract["authorization"],
        "errors": errors,
    }


def doc(audit: dict, bootstrap: dict, *, ru: bool) -> str:
    ui = next(row for row in bootstrap["boards"] if row["project"] == "LESHY2-UI-R2")
    rf = next(row for row in bootstrap["boards"] if row["project"] == "LESHY2-RF-R2")
    ru_track_items = f"{bootstrap['summary']['track_item_count']:,}".replace(",", " ")
    ru_ui_unconnected = f"{ui['routed_total_unconnected_count']:,}".replace(",", " ")
    ru_rf_unconnected = f"{rf['routed_total_unconnected_count']:,}".replace(",", " ")
    if ru:
        title = "# H6.0.2-R1 · Политика трассировки"
        nav = "[Главная](../README.ru.md) · [Роадмап](roadmap.ru.md) · [English](h6-r2-routing-policy.md)"
        lead = (
            f"**Статус:** 🟡 все {audit['summary']['project_net_count']} физических сетей двух плат "
            f"({audit['summary']['global_canonical_net_count']} канонических) распределены по 13 классам. "
            "Проверенные `GENERAL_CONTROL` и все 12 кварцевых/генераторных сетей уже разведены полностью; "
            "в текущей H6.0.2 остаются safety-control и аналоговые/audio/sense-сети. RF, USB, питание, i8080 и "
            "тактируемые шины защищены до своих следующих ручных срезов."
        )
        headers = "| Класс | Сетей | Способ | Геометрия |\n| --- | ---: | --- | --- |"
        labels = {"manual_only": "вручную", "plane_or_local_pour_manual": "плоскость/полигон вручную", "automatic_helper_allowed_then_manual_review": "автопредложение + ручная проверка"}
        notes = (
            "## Что зафиксировано\n\n"
            f"- точный стек: `{audit['stackup_binding']['official_stackup_id']}`, заказной номинал 1,6 мм, расчётная готовая толщина 1,54 мм ±10 %, два core по 0,55 мм;\n"
            f"- четыре внешних USB-порта разворачиваются в `{audit['summary']['usb_pair_count']}` полных сегментов диффпар, и ровно 10 линий прямого i8080-8 найдены автоматически;\n"
            "- абстрактные RF-, safety-, ESD- и силовые ground-якоря физически сведены в сплошной `POWER_GROUND`; отдельной остаётся только `AUDIO_GROUND`, соединённая с ним явной 0-Ω перемычкой `R172`;\n"
            "- текущий калькулятор JLCPCB задаёт внешнюю RF CPWG 50 Ом как 5,31 mil ширины / 6 mil до боковой меди, а USB 90 Ом — как 5,31 mil ширины / 6 mil между линиями;\n"
            "- канонические `DP/DM` сохранены в контрактах, но физические KiCad-сети заканчиваются на `_P/_N`, поэтому штатный дифференциальный роутер видит все 12 пар;\n"
            "- результат автотрассировки не принимается без импорта в KiCad, визуального ревью и штатного DRC; полнота соединений проверяется полным native connectivity count, а не ограниченным 499 строками JSON-списком DRC.\n\n"
            "## Одноразовая рабочая область помощника\n\n"
            "`hardware/layout/h6_r2_routing_workspace.py` экспортирует временные DSN без описаний защищённых сетей. "
            "Площадки и компоненты остаются физическими препятствиями, но Freerouting видит только `GENERAL_CONTROL`: "
            f"`{audit['boards']['LESHY2-UI-R2']['class_counts']['GENERAL_CONTROL']}` сеть на передней плате и "
            f"`{audit['boards']['LESHY2-RF-R2']['class_counts']['GENERAL_CONTROL']}` на RF/power-плате. Такой явный "
            "фильтр нужен потому, что Freerouting 2.3.0 разбирает исключения классов и активность слоёв в "
            "headless-режиме, но применяет их только в GUI-загрузчике. Поэтому временный DSN также объявляет "
            "`In1.Cu`/`In4.Cu` несигнальными слоями. Полученные DSN и сессии служат лишь для ревью, а не являются "
            "исходниками или релизными файлами. Автотрассировщик может использовать только `F.Cu`, `In2.Cu`, "
            "`In3.Cu` и `B.Cu`; `In1.Cu`/`In4.Cu` остаются непрерывными опорными плоскостями, а стоимость via "
            f"повышена до `{audit['automatic_helper']['via_costs']}`.\n\n"
            "## Принятый срез H6.0.2\n\n"
            "Автопредложения `GENERAL_CONTROL` после импорта исправлены и проверены в KiCad; генераторные "
            "цепи проложены вручную с короткими локальными ветвями. В сохранённых PCB теперь замкнуты все "
            f"**{bootstrap['summary']['resolved_allowed_connection_count']}/{bootstrap['summary']['expected_allowed_connection_count']}** "
            f"физических соединений во всех **{bootstrap['summary']['allowed_net_count']}** разрешённых сетях: "
            f"{ui['resolved_allowed_connection_count']} соединений на UI и {rf['resolved_allowed_connection_count']} на RF/power. "
            f"В них {ru_track_items} элементов дорожек/via, включая "
            f"{bootstrap['summary']['via_count']} via; использованы только четыре разрешённых слоя, не затронута ни одна "
            "защищённая сеть, а `In1.Cu`/`In4.Cu` остались нетронутыми. Свежий DRC KiCad "
            f"{ui['drc']['kicad_version']} показывает **ноль нарушений** и ноль ошибок схема↔PCB на обеих платах. "
            f"Точные native-остатки неподключённых соединений — {ru_ui_unconnected} на UI и "
            f"{ru_rf_unconnected} на RF/power; 499 строк каждого JSON — только лимит вывода KiCad.\n\n"
            "[Аудит принятой трассировки](../hardware/layout/generated/H6-R2-general-routing-audit.json) привязывает "
            "результат к точным хешам PCB и freeze всех 1 208 позиций. Это срез внутри H6.0.2, а не завершение "
            "фазы: `SAFETY_CONTROL` и `ANALOG_AUDIO_SENSE` ещё разводятся вручную.\n\n"
            "Экспорт запускается встроенным Python из KiCad:\n\n"
            "```sh\n"
            "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 hardware/layout/h6_r2_routing_workspace.py --output-dir /private/tmp/leshy2-routing\n"
            "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 hardware/layout/h6_r2_general_routing.py --check\n"
            "```\n\n"
            "[Машинный аудит и все назначения](../hardware/layout/generated/H6-R2-routing-policy-audit.json)"
        )
    else:
        title = "# H6.0.2-R1 · Routing policy"
        nav = "[Home](../README.md) · [Roadmap](roadmap.md) · [Русский](h6-r2-routing-policy.ru.md)"
        lead = (
            f"**Status:** 🟡 all {audit['summary']['project_net_count']} physical nets across both boards "
            f"({audit['summary']['global_canonical_net_count']} canonical) are assigned to 13 classes. "
            "The reviewed `GENERAL_CONTROL` set and all 12 crystal/oscillator nets are now routed completely; "
            "manual H6.0.2 work on safety control and analogue/audio/sense nets remains current. RF, USB, power, i8080 "
            "and clocked buses remain protected for their later manual releases."
        )
        headers = "| Class | Nets | Method | Geometry release |\n| --- | ---: | --- | --- |"
        labels = {"manual_only": "manual", "plane_or_local_pour_manual": "manual plane/pour", "automatic_helper_allowed_then_manual_review": "automatic proposal + manual review"}
        notes = (
            "## What is locked\n\n"
            f"- exact stack: `{audit['stackup_binding']['official_stackup_id']}`, 1.6-mm order nominal, 1.54-mm ±10% calculated finished thickness, and two 0.55-mm cores;\n"
            f"- four external USB ports expand to `{audit['summary']['usb_pair_count']}` complete differential-pair segments, and exactly ten direct i8080-8 nets are detected automatically;\n"
            "- abstract RF, safety, ESD and power-ground anchors are physically canonicalized onto the solid `POWER_GROUND`; only `AUDIO_GROUND` remains local and joins it through explicit 0-ohm link `R172`;\n"
            "- the current JLCPCB calculator sets outer 50-ohm RF CPWG to 5.31-mil width / 6-mil lateral copper gap and 90-ohm USB to 5.31-mil width / 6-mil pair gap;\n"
            "- canonical `DP/DM` identities remain in the contracts, while physical KiCad net names end in `_P/_N`, allowing the native differential router to discover all 12 pairs;\n"
            "- no automatic result is accepted before KiCad import, visual review and native DRC; completeness uses the full native connectivity count rather than the DRC JSON list capped at 499 rows.\n\n"
            "## Disposable helper workspace\n\n"
            "`hardware/layout/h6_r2_routing_workspace.py` exports temporary DSNs without the protected net definitions. "
            "Pads and components remain as physical obstacles, but Freerouting can see only `GENERAL_CONTROL` nets: "
            f"`{audit['boards']['LESHY2-UI-R2']['class_counts']['GENERAL_CONTROL']}` on the UI board and "
            f"`{audit['boards']['LESHY2-RF-R2']['class_counts']['GENERAL_CONTROL']}` on the RF/power board. This "
            "explicit filter is required because Freerouting 2.3.0 parses ignore-class and layer-active settings in "
            "headless mode but applies them only in the GUI loader. The disposable DSN therefore also declares "
            "`In1.Cu`/`In4.Cu` as non-signal layers. Generated DSNs and sessions are review inputs, never source or "
            "release artifacts. The helper may use only `F.Cu`, `In2.Cu`, `In3.Cu` and `B.Cu`; `In1.Cu`/`In4.Cu` "
            "remain uninterrupted reference planes, and the via cost is raised to "
            f"`{audit['automatic_helper']['via_costs']}`.\n\n"
            "## Accepted H6.0.2 slice\n\n"
            "The imported `GENERAL_CONTROL` proposals were repaired and reviewed in KiCad; oscillator branches "
            "were routed manually with short local geometry. The checked-in boards now resolve all "
            f"**{bootstrap['summary']['resolved_allowed_connection_count']}/{bootstrap['summary']['expected_allowed_connection_count']}** "
            f"physical connections across all **{bootstrap['summary']['allowed_net_count']}** allowed nets: "
            f"{ui['resolved_allowed_connection_count']} connections on UI and {rf['resolved_allowed_connection_count']} on RF/power. "
            f"They contain {bootstrap['summary']['track_item_count']:,} track/via items, including "
            f"{bootstrap['summary']['via_count']} vias, use only the four permitted routing layers, touch zero protected "
            "nets and leave `In1.Cu`/`In4.Cu` untouched. Fresh KiCad "
            f"{ui['drc']['kicad_version']} DRC reports contain **zero violations** and zero schematic-parity errors on both boards. "
            f"The exact native unconnected totals are {ui['routed_total_unconnected_count']:,} (UI) and "
            f"{rf['routed_total_unconnected_count']:,} (RF/power); the 499 rows shown by each JSON report are only KiCad's output cap.\n\n"
            "The [accepted-routing audit](../hardware/layout/generated/H6-R2-general-routing-audit.json) binds those "
            "results to the exact PCB hashes and to the 1,208-position freeze. This is a slice inside H6.0.2, "
            "not completion of the phase: `SAFETY_CONTROL` and `ANALOG_AUDIO_SENSE` are still routed manually.\n\n"
            "Run the exporter with KiCad's bundled Python:\n\n"
            "```sh\n"
            "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 hardware/layout/h6_r2_routing_workspace.py --output-dir /private/tmp/leshy2-routing\n"
            "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3 hardware/layout/h6_r2_general_routing.py --check\n"
            "```\n\n"
            "[Machine audit and every assignment](../hardware/layout/generated/H6-R2-routing-policy-audit.json)"
        )
    rows = [headers]
    contract = load(CONTRACT)
    for name in contract["class_order"]:
        policy = contract["classes"][name]
        rows.append(f"| `{name}` | {audit['class_counts'][name]} | {labels[policy['route_mode']]} | `{policy['geometry_release']}` |")
    return "\n\n".join((title, nav, lead, "\n".join(rows), notes)) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    audit = build()
    bootstrap = load(GENERAL_ROUTING_AUDIT)
    if bootstrap.get("status") != "pass":
        raise SystemExit("accepted GENERAL_CONTROL routing audit is missing or failed")
    outputs = {
        AUDIT: json.dumps(audit, indent=2, ensure_ascii=False) + "\n",
        DOC_EN: doc(audit, bootstrap, ru=False),
        DOC_RU: doc(audit, bootstrap, ru=True),
    }
    if args.write:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    else:
        stale = [str(path.relative_to(ROOT)) for path, content in outputs.items() if not path.is_file() or path.read_text(encoding="utf-8") != content]
        if stale:
            print("stale outputs: " + ", ".join(stale))
            return 1
    print(
        f"H6-R2 routing policy {audit['status']}: {audit['summary']['project_net_count']} project nets / "
        f"{audit['summary']['global_canonical_net_count']} global; {audit['summary']['routing_class_count']} classes; "
        f"{audit['summary']['unclassified_net_count']} unclassified"
    )
    for error in audit["errors"]:
        print("- " + error)
    return 0 if audit["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
