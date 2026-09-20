#!/usr/bin/env python3
"""Reconstruct all ten native indicator branches with EDG; never qualify hardware.

Uses the already-proven source-preserving LED pilot, existing EDG compiler and
fresh work directories. Ready Indicator{Sink,}Led blocks change resistor order
and require an unaccepted current target, so this adapter preserves 2.2 kohm.
Two independent workers verify native pads and generated topology before replay.
Exit 1 means mechanics passed but electrical qualification remains open.
"""

import argparse
from collections import Counter, defaultdict
from contextlib import redirect_stdout
from fractions import Fraction as F
import hashlib
from importlib import metadata
import json
import math
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
from threading import Event, Thread

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from synthesize_main_feedback import snapshot
from route_board import keep_awake
from hardware.layout.h6_r2_parallel_process import ProcessRegistry

PROJECT = "LESHY2-UI-R2"
PILOT = ROOT / "work/edg-pilot-XSChki"
DEFAULT_PYTHON = PILOT / "venv/bin/python"
DEFAULT_JAVA = Path("/Users/randoom/Library/Java/JavaVirtualMachines/corretto-17.0.11/Contents/Home")
DEFAULT_KICAD = Path("/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3")
PCB = f"hardware/ecad/kicad/{PROJECT}/{PROJECT}.kicad_pcb"
INPUTS = {
    "devices": "hardware/architecture/devices.json",
    "instances": "hardware/ecad/generated/H2-R2-native-instance-ledger.json",
    "nets": "hardware/ecad/generated/H2-R2-native-net-ledger.json",
    "material": "hardware/ecad/generated/H2-R2-contact-materialization.json",
    "bindings": "hardware/layout/generated/H6-R2-kicad-net-bindings.json",
    "rail": "hardware/verification/h3-r2-rail-margin-contract.json",
}
# An independently reviewed coverage/connection fixture, not inferred from output.
BRANCHES = {
    "s3_tx_led": ("R38", "D9", "S3_TX_LED_A", "EV_N0_S3"),
    "c5_tx_led": ("R26", "D1", "C5_TX_LED_A", "EV_N1_C5"),
    "nrf0_tx_led": ("R35", "D6", "NRF0_TX_LED_A", "EV_N2_NRF0"),
    "nrf1_tx_led": ("R36", "D7", "NRF1_TX_LED_A", "EV_N3_NRF1"),
    "nrf2_tx_led": ("R37", "D8", "NRF2_TX_LED_A", "EV_N4_NRF2"),
    "cc_tx_led": ("R27", "D2", "CC_TX_LED_A", "EV_N5_CC"),
    "voice_tx_led": ("R75", "D10", "VOICE_TX_LED_A", "EV_N6_VOICE"),
    "ir_tx_led": ("R33", "D5", "IR_TX_LED_A", "EV_N7_IR"),
    "ext_tx_led": ("R31", "D3", "EXT_TX_LED_A", "EV_N8_LORA_EXT"),
    "fault_led": ("R32", "D4", "FAULT_LED_A", "POWER_GROUND"),
}
RES_ID = "uniroyal_0402wgf2201tce"
RED_ID, AMBER_ID = "liteon_ltst_c190krkt", "liteon_ltst_c190kfkt"
RES_FP, LED_FP = "Resistor_SMD:R_0402_1005Metric", "LED_SMD:LED_0603_1608Metric"
ARTIFACTS = {"Indicators." + suffix for suffix in ("edg", "net", "csv", "svgpcb.js", "compiled.json")}
PROVENANCE_KEYS = {
    "instances": {"native_inventory", "exact_definition_ledger", "physical_source_table"},
    "material": {"exact_ledger", "device_register"},
    "nets": {"instances", "definitions", "h0", "dual_rp", "c5_mux", "pack_safety_boundary", "display_mount",
             "main_power_cell", "u219", "freeze_new_parts", "topology"},
}
EDG_FILES = {
    "electronics_model/footprint.py": "575d09768a1e8d64253d76d02b43b960bc2df1fdcd1933b66132a15011657bbb",
    "electronics_model/NetlistGenerator.py": "fb773b0f0416f9def2a2285ef52bad0cb629e1bc6ddaa0f6f8eb4bf14e9550d0",
    "core/HierarchyBlock.py": "3504959792523d2d15d719d99cbc50bfd892dc0055b9048f38a2e73202601052",
    "core/Core.py": "001e9d1b7597ac8e3826a954dd30102cda5dfa830195d233414f3e488b25d3b5",
    "hdl_server/__main__.py": "72584dd687a157e68fed97fb8625cc8f68c6437fb528586724e2ca1ddec3a73e",
    "BoardCompiler.py": "2ca1c482245b01e884b34f5825f4e95091179bdb4d6c056f4e8a027c0595a895",
    "core/ScalaCompilerInterface.py": "4c2ae5e127cd4d028373d76d6eacd1f6c18a3bc9f9989ec5ee7ca1230b45174c",
    "core/resources/edg-compiler-precompiled.jar": "e5f93609487968d964c5b04c8c46a38051d857a00e10552afeb4e0b9e576f968",
    "core/Range.py": "55a849aa25ea16ecdd66c4c16607a45ed2908e986b942be0e4e9fcc016e2a5dd",
    "electronics_model/NetlistBackend.py": "636e0658ac90449c6843a59bbabd5d17f12f9a58f556899530f62dcd3b734f13",
    "electronics_model/BomBackend.py": "7cd2be4364f26169d020db4bcc33fe20a360052f797f25df633a82b7305807ea",
    "electronics_model/CircuitBlock.py": "a59589f3a39b46ed49a6dea3934b63b29d6564c095ff8e144701df4dfb12b34c",
    "abstract_parts/Resistor.py": "6740592251aa08f6b0d71f40d6b7348a8bc535ccc84a054834c1a6748e2647ec",
    "abstract_parts/ESeriesUtil.py": "10b23014b3cdc803c833b9134d5ab64259bdac28641222c701d7796fd6190b05",
    "vendor_parts/generic/GenericResistor.py": "5c616c57df022f1ad278e5acd595a57626f5f85351d37d9e7cafa13be9f0dc0a",
    "electronics_interfaces/VoltagePorts.py": "f2d840b41205403f6ad485ae21739ced9c227b261ffcd29fe52f7a9de3123761",
    "electronics_interfaces/VoltageDummy.py": "9a72708051b03bfa760b5901368d234bc3c4569fb618c4e32c15716ad6857e59",
    "electronics_interfaces/DummyDevices.py": "83fdd0ea5917a47a32bfb1d26ec16ca29ad3dfc1b0639ff776c25e2aaa734ddf",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def unchanged(hashes):
    require(bool(hashes), "missing source hashes")
    require(snapshot([ROOT / path for path in hashes]) == hashes, "sources changed during reconstruction")


def source_declarations(data):
    declared = {}
    def add(path, value):
        require(path not in declared or declared[path] == value, "conflicting provenance hashes")
        declared[path] = value
    for key, names in PROVENANCE_KEYS.items():
        sources = data[key]["sources"]
        require({name for name, row in sources.items() if row.get("authority", True)} == names, "required source membership changed")
        for name in names:
            add(sources[name]["path"], sources[name]["sha256"])
    bindings = data["bindings"]["source_hashes"]
    required = {f"hardware/ecad/generated/H2-R2-{name}.json" for name in
                ("controlled-symbol-library", "native-instance-ledger", "native-kicad-projects", "native-net-ledger")}
    for project in ("LESHY2-UI-R2", "LESHY2-RF-R2"):
        required.update(str(p.relative_to(ROOT)) for p in (ROOT / "hardware/ecad/kicad" / project).glob("*.kicad_sch"))
    require(set(bindings) == required, "required net-binding source membership changed")
    for path, value in bindings.items():
        add(path, value)
    return declared


def load_sources():
    paths = [ROOT / p for p in (*INPUTS.values(), PCB, "tools/rebuild_indicators.py",
             "tools/synthesize_main_feedback.py", "tools/route_board.py", "hardware/layout/h6_r2_parallel_process.py")]
    before = snapshot(paths)  # Before reading any source JSON.
    data = {key: json.loads((ROOT / path).read_text()) for key, path in INPUTS.items()}
    # Check declared direct provenance too; these dependencies are not reinterpreted.
    declared = source_declarations(data)
    for path in declared:
        require(not Path(path).is_absolute() and ".." not in Path(path).parts, "unsafe provenance path")
    observed = snapshot([ROOT / p for p in declared])
    require(observed == declared, "stale declared source evidence")
    unchanged(before)
    return data, {**before, **observed}


def validate_sources(data):
    devices = data["devices"]["devices"]
    rows = [r for r in data["instances"]["rows"] if r["project"] == PROJECT]
    relevant = [r for r in rows if r["instance"].endswith("_tx_led") or r["instance"].endswith("_tx_led_series")
                or r["instance"] in {"fault_led", "fault_led_series"}]
    expected = {name + suffix for name in BRANCHES for suffix in ("", "_series")}
    require(Counter(r["instance"] for r in relevant) == Counter({n: 1 for n in expected}), "indicator coverage missing/duplicate/extra")
    instances = {r["instance"]: r for r in relevant}
    material = {g["device_id"]: g for g in data["material"]["groups"]}
    require(len(material) == len(data["material"]["groups"]), "duplicate material identity")
    bindings = data["bindings"]["projects"][PROJECT]["canonical_to_kicad"]
    endpoints = [r for r in data["nets"]["rows"] if r["project"] == PROJECT and r["instance"] in expected]
    require(len(endpoints) == 40 and len({r["endpoint"] for r in endpoints}) == 40, "indicator endpoint coverage changed")
    ledger = {r["endpoint"]: r for r in endpoints}
    terminal_nets, components, branches = {}, {}, []
    for name, (res_ref, led_ref, middle, return_net) in BRANCHES.items():
        supply = "FAULT_KILL" if name == "fault_led" else "AON_SAFE_3V3"
        parts = {}
        for position, instance, ref, device_id, mpn, footprint, contacts in (
            ("res", name + "_series", res_ref, RES_ID, "UNI-ROYAL 0402WGF2201TCE", RES_FP,
             {"END_1": ("1", supply), "END_2": ("2", middle)}),
            ("led", name, led_ref, AMBER_ID if name == "fault_led" else RED_ID,
             "LTST-C190KFKT" if name == "fault_led" else "LTST-C190KRKT", LED_FP,
             {"A": ("2", middle), "K": ("1", return_net)}),
        ):
            native, device, pads = instances[instance], devices[device_id], material[device_id]
            require(all(native.get(k) == v for k, v in {"reference": ref, "device_id": device_id, "mpn": mpn, "footprint": footprint}.items()), "exact indicator identity changed: " + instance)
            require(device["mpn"] == pads["mpn"] == mpn and pads["footprint"] == footprint, "register/material identity mismatch")
            padmap = {r["contact"]: r["pads"] for r in pads["contacts"]}
            require(len(padmap) == len(pads["contacts"]), "duplicate material contact")
            require(set(padmap) == set(contacts) and set(pads["pad_inventory"]) == {"1", "2"}, "physical pad coverage changed")
            if position == "res":
                require(device["kind"] == "2_2kohm_1pct_0402_i2c_pullup_resistor", "preserved resistor value/tolerance changed")
            for contact, (pin, net) in contacts.items():
                row = ledger[instance + "." + contact]
                require(padmap[contact] == [pin], "LED/resistor physical pad swapped")
                require(all(row.get(k) == v for k, v in {"reference": ref, "device_id": device_id,
                        "contact": contact, "net": net, "disposition": "connected"}.items()), "indicator native connection changed")
                require(net in bindings, "canonical net has no PCB binding")
                terminal_nets[ref + "." + pin] = net
            parts[position] = {"reference": ref, "mpn": mpn, "footprint": footprint}
            components[ref] = {**parts[position], "edg_path": name + "." + position,
                               "native_mpn_retained_not_reaccepted": True}
        branches.append({"name": name, "source_net": supply, "return_net": return_net, **parts})
    rail = data["rail"]["rails"]["AON_SAFE_3V3"]
    require((F(str(rail["load_min_v"])), F(str(rail["load_max_v"]))) == (F("2.7"), F("3.6")), "indicator rail stimulus changed; review required")
    external = {}
    selected_bindings = {n: bindings[n] for n in set(terminal_nets.values())}
    require(all(isinstance(n, str) and n.strip() for n in selected_bindings.values())
            and len(set(selected_bindings.values())) == len(selected_bindings), "PCB net bindings must be nonempty and distinct")
    for net in sorted(set(terminal_nets.values())):
        other = [r["project"] + ":" + r["endpoint"] for r in data["nets"]["rows"]
                 if r["net"] == net and (r["project"] != PROJECT or r["instance"] not in expected)]
        external[net] = sorted(other)
    return {"branches": branches, "components": components, "terminal_nets": terminal_nets,
            "bindings": selected_bindings,
            "external_endpoints_not_generated": external, "rail_limits_v": ["2.7", "3.6"]}


def validate_native(native, spec):
    require(set(native) == set(spec["components"]), "native component coverage mismatch")
    for ref, part in spec["components"].items():
        found = native[ref]
        require(found["value"] == part["mpn"] and found["footprint"] == part["footprint"], "native MPN/footprint mismatch")
        expected = {p.split(".")[1]: spec["bindings"][net] for p, net in spec["terminal_nets"].items() if p.startswith(ref + ".")}
        require(found["pads"] == expected, "native pad/net mismatch: " + ref)


def inspect_native(spec, executable):
    code = """import json, pcbnew, sys
b = pcbnew.LoadBoard(sys.argv[1]); refs = set(json.loads(sys.argv[2])); result = {}
for f in b.GetFootprints():
    ref = f.GetReference()
    if ref not in refs: continue
    if ref in result: raise ValueError('duplicate PCB reference')
    pads = {}
    for p in f.Pads():
        if p.GetNumber() in pads: raise ValueError('duplicate indicator pad')
        pads[p.GetNumber()] = p.GetNetname()
    result[ref] = dict(value=f.GetValue(), footprint=str(f.GetFPID().GetLibNickname()) + ':' + str(f.GetFPID().GetLibItemName()), pads=pads)
print(json.dumps(result, sort_keys=True))
"""
    proc = subprocess.run([str(executable), "-B", "-c", code, str(ROOT / PCB), json.dumps(sorted(spec["components"]))],
                          capture_output=True, text=True, timeout=45)
    require(proc.returncode == 0, "native reader failed: " + proc.stderr[-2000:])
    native = json.loads(proc.stdout)
    validate_native(native, spec)
    return native


def expected_generated_components(spec):
    return {ref: {"footprint": part["footprint"], "edg_path": part["edg_path"],
                  "edg_part": "" if ref.startswith("R") else part["mpn"],
                  "edg_value": "2.2k, 1%, 0.0625 W" if ref.startswith("R") else part["mpn"]}
            for ref, part in spec["components"].items()}


def validate_generated(components, groups, spec, terminal_nets=None):
    require(set(components) == set(spec["components"]), "generated component coverage mismatch")
    require(components == expected_generated_components(spec), "generated footprint/path/part/value mismatch")
    expected = defaultdict(list)
    for pin, net in spec["terminal_nets"].items():
        expected[net].append(pin)
    normalize = lambda values: sorted(tuple(sorted(group)) for group in values)
    require(normalize(groups) == normalize(expected.values()), "generated topology differs: omitted/swapped/shorted terminals")
    require(terminal_nets == spec["terminal_nets"], "generated canonical boundary/net identity differs")


def inspect_generated(path, spec):
    import sexpdata
    members = lambda expr, key: [n for n in expr[1:] if isinstance(n, list) and n[0] == sexpdata.Symbol(key)]
    def field(expr, key):
        found = members(expr, key)
        require(len(found) == 1, "ambiguous generated field")
        value = found[0][1]
        return value.value() if isinstance(value, sexpdata.Symbol) else value
    expr = sexpdata.loads(path.read_text())
    by_path = {v["edg_path"]: k for k, v in spec["components"].items()}
    refs, components = {}, {}
    for comp in members(members(expr, "components")[0], "comp"):
        properties = {field(p, "name"): field(p, "value") for p in members(comp, "property")}
        generated_ref, edg_path = field(comp, "ref"), properties["edg_path"]
        require(edg_path in by_path and generated_ref not in refs and by_path[edg_path] not in components, "duplicate/unexpected generated component")
        ref = refs[generated_ref] = by_path[edg_path]
        components[ref] = {"footprint": field(comp, "footprint"), "edg_path": edg_path,
                           "edg_part": properties["edg_part"], "edg_value": properties["edg_value"]}
    aliases = {"AON_SAFE_3V3": "AON_SAFE_3V3", "FAULT_KILL": "FAULT_KILL"}
    for name, (_, _, middle, return_net) in BRANCHES.items():
        aliases[name + ".res.b"] = middle
        aliases[return_net] = return_net
    groups, terminal_nets, seen_nets = [], {}, set()
    for net in members(members(expr, "nets")[0], "net"):
        if not members(net, "node"):
            continue
        name = field(net, "name")
        require(name in aliases and name not in seen_nets, "unknown/duplicate generated named net: " + name)
        seen_nets.add(name)
        group = []
        for node in members(net, "node"):
            pin = refs[field(node, "ref")] + "." + str(field(node, "pin"))
            require(pin not in terminal_nets, "duplicate generated terminal")
            terminal_nets[pin] = aliases[name]
            group.append(pin)
        groups.append(group)
    validate_generated(components, groups, spec, terminal_nets)
    return {"components": components, "terminal_groups": sorted(sorted(g) for g in groups), "terminal_nets": terminal_nets,
            "resistor_bom_identity": "generic EDG 2.2k/1% resistor; fitted UNI-ROYAL identity is comparison metadata only, never a selected production MPN"}


def prepare_runtime(directory, java_home):
    dist = metadata.distribution("edg")
    require(dist.version == "0.5.2", "unreviewed EDG version")
    package = Path(dist.locate_file("edg"))
    for name, expected in EDG_FILES.items():
        path = package / name
        require(path.is_file() and not path.is_symlink() and digest(path) == expected, "unreviewed installed EDG implementation: " + name)
    require(not (package / "core/../../compiler/target/scala-2.13/edg-compiler-assembly-0.1-SNAPSHOT.jar").exists(), "unreviewed development compiler would override pinned JAR")
    import edg
    import jdk
    from edg.core.ScalaCompilerInterface import ScalaCompiler
    require(Path(edg.__file__).resolve().parent == package.resolve(), "EDG import shadows pinned package")
    java = java_home.resolve() / "bin/java"
    proc = subprocess.run([str(java), "-version"], capture_output=True, text=True, check=True, timeout=5)
    require('version "17.' in proc.stderr, "prepared Java 17 required")
    jre = directory / "jre"
    jre.mkdir()
    (jre / "jdk-prepared").symlink_to(java_home.resolve(), target_is_directory=True)
    ScalaCompiler.kInstallJrePath = jre
    def no_download(*args, **kwargs):
        raise ValueError("automatic runtime downloads are forbidden")
    jdk.install = no_download
    return {"edg": dist.version, "installed_source_sha256": EDG_FILES, "java": str(java),
            "java_sha256": digest(java), "java_version": proc.stderr.strip()}


def compile_indicators(spec, directory):
    from edg import Block, DesignTop, FootprintBlock, GenericChipResistor, Passive, Range, RangeExpr, RangeLike, StringLike, VoltageSink, edgir
    from edg.BoardCompiler import compile_board
    from edg.core.ScalaCompilerInterface import ScalaCompiler, CompilerCheckError
    from edg.electronics_interfaces.VoltageDummy import DummyVoltageSource
    from edg.electronics_interfaces.DummyDevices import DummyPassive

    class ExistingLed(FootprintBlock):
        def __init__(self, part: StringLike):
            super().__init__()
            self.a, self.k = self.Port(Passive.empty()), self.Port(Passive.empty())
            self.footprint("D", LED_FP, {"2": self.a, "1": self.k}, part=part)

    class PreservedBranch(Block):
        def __init__(self, part: StringLike, limits: RangeLike):
            super().__init__()
            self.led_part, self.limits = self.ArgParameter(part), self.ArgParameter(limits)
            self.pwr, self.out = self.Port(VoltageSink.empty()), self.Port(Passive.empty())
            self.current_bound = self.Parameter(RangeExpr())

        def contents(self):
            super().contents()
            self.res = self.Block(GenericChipResistor(resistance=Range.from_tolerance(2200, .01),
                power=(0, 3.6 ** 2 / 2178), filter_footprints=[RES_FP], series=24, tolerance=.01))
            self.led = self.Block(ExistingLed(self.led_part))
            self.assign(self.current_bound, (0, self.pwr.link().voltage.upper() / self.res.actual_resistance.lower()))
            self.pwr.init_from(VoltageSink(voltage_limits=self.limits, current_draw=self.current_bound))
            self.connect(self.pwr.net, self.res.a)
            self.connect(self.res.b, self.led.a)
            self.connect(self.led.k, self.out)

    class Indicators(DesignTop):
        stimulus = (2.7, 3.6)
        def contents(self):
            super().contents()
            self.aon = self.Block(DummyVoltageSource(voltage=self.stimulus))
            self.fault_source = self.Block(DummyVoltageSource(voltage=(0, 3.6)))
            connections = {"AON_SAFE_3V3": [self.aon.io], "FAULT_KILL": [self.fault_source.io]}
            for part in spec["branches"]:
                limits = (0, 3.6) if part["name"] == "fault_led" else (2.7, 3.6)
                branch = self.Block(PreservedBranch(part["led"]["mpn"], limits))
                setattr(self, part["name"], branch)
                boundary = self.Block(DummyPassive())
                setattr(self, part["name"] + "_boundary", boundary)
                connections[part["source_net"]].append(branch.pwr)
                connections[part["return_net"]] = [branch.out, boundary.io]
            for net, ports in connections.items():
                setattr(self, net, self.connect(*ports))

    class WrongVoltage(Indicators):
        stimulus = (5, 5)

    # EDG's existing HDL server resolves classes by module + class name.
    globals().update({cls.__name__: cls for cls in (ExistingLed, PreservedBranch, Indicators, WrongVoltage)})
    if __name__ == "__main__":
        sys.modules[Path(__file__).stem] = sys.modules[__name__]
    try:
        compiled = compile_board(Indicators, (str(directory), "Indicators"))
        numerical = {}
        for part in spec["branches"]:
            resistance = compiled.get_value([part["name"], "res", "actual_resistance"])
            current = compiled.get_value([part["name"], "current_bound"])
            require(all(math.isclose(a, b, rel_tol=1e-9) for a, b in zip((resistance.lower, resistance.upper), (2178, 2222))), "generated resistance differs from source")
            require(current.lower == 0 and math.isclose(current.upper, float(F("3.6") / 2178), rel_tol=1e-9), "current propagation differs from independent arithmetic")
            numerical[part["name"]] = {"resistance_ohm": [resistance.lower, resistance.upper],
                "conditional_current_upper_a_exact": str(F("3.6") / 2178),
                "conditional_resistor_power_upper_w_exact": str(F("3.6") ** 2 / 2178)}
        rejected = False
        try:
            ScalaCompiler.compile(WrongVoltage)
        except CompilerCheckError as exc:
            rejected = "voltage out of limits" in str(exc)
        require(rejected, "wrong-voltage mutation was not rejected")
        binary = edgir.Design()
        binary.ParseFromString((directory / "Indicators.edg").read_bytes())
        canonical = hashlib.sha256(binary.SerializeToString(deterministic=True)).hexdigest()
        require(canonical == hashlib.sha256(compiled.design.SerializeToString(deterministic=True)).hexdigest(), "parsed compiler model differs")
        return numerical, canonical
    finally:
        process = ScalaCompiler.process
        if process is not None:
            if process.stdin:
                process.stdin.close()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
            if process.stdout:
                process.stdout.close()
            ScalaCompiler.process = None


def validate_result(report, spec):
    require(report.get("status") == "not_qualified" and report.get("mechanics_status") == "pass"
            and all(report.get(k) is False for k in ("qualified", "electrically_qualified", "production_promoted", "supply_checked")), "false physical qualification")
    require(report.get("branches") == 10 and report.get("components") == 20, "incomplete reconstruction")
    require(set(report.get("artifact_sha256", {})) == ARTIFACTS, "required generated artifacts missing")
    generated = report.get("generated", {})
    validate_generated(generated.get("components", {}), generated.get("terminal_groups", []), spec, generated.get("terminal_nets"))
    validate_native(report.get("native", {}), spec)
    numerical = report.get("numerical", {})
    require(set(numerical) == set(BRANCHES), "missing numerical branch evidence")
    for row in numerical.values():
        require(row == {"resistance_ohm": [2178.0, 2222.0],
                        "conditional_current_upper_a_exact": str(F("3.6") / 2178),
                        "conditional_resistor_power_upper_w_exact": str(F("3.6") ** 2 / 2178)}, "numerical evidence differs from independent bound")


def validate_artifacts(report, directory):
    require(set(report["artifact_sha256"]) == ARTIFACTS, "required artifact hashes missing")
    for name, expected in report["artifact_sha256"].items():
        path = directory / name
        require(path.is_file() and not path.is_symlink() and digest(path) == expected, "generated artifact changed: " + name)


def worker(args):
    directory = args.worker.resolve()
    require(directory.is_relative_to((ROOT / "work").resolve()) and directory.is_dir() and not any(directory.iterdir()), "worker needs a fresh empty work directory")
    data, hashes = load_sources()
    spec = validate_sources(data)
    runtime = prepare_runtime(directory, args.java_home)
    native = inspect_native(spec, args.kicad_python)
    with (directory / "compiler.log").open("w") as log, redirect_stdout(log):
        numerical, canonical = compile_indicators(spec, directory)
    generated = inspect_generated(directory / "Indicators.net", spec)
    unchanged(hashes)
    artifacts = {p.name: digest(p) for p in directory.iterdir() if p.name.startswith("Indicators.")}
    report = {"schema_version": 1, "status": "not_qualified", "mechanics_status": "pass", "qualified": False,
        "electrically_qualified": False, "production_promoted": False, "supply_checked": False,
        "branches": 10, "components": 20, "source_sha256": hashes, "runtime": runtime,
        "native": native, "generated": generated, "numerical": numerical,
        "canonical_edg_sha256": canonical, "artifact_sha256": artifacts,
        "external_endpoints_not_generated": spec["external_endpoints_not_generated"],
        "unqualified_reasons": ["No accepted brightness/minimum-current criterion or low-current/temperature LED Vf model",
            "Vf + driver drop is assumed between zero and stimulus; current lower bound is zero",
            "Comparator/latch drive, shared-net load and fault/off/startup states are not generated or qualified",
            "AON 2.7..3.6 V and FAULT_KILL 0..3.6 V are boundary stimuli, not delivered voltage guarantees",
            "Initial resistor tolerance only; TCR, aging, exact-part derating and routed rail remain unqualified",
            "Generic resistor identity is not an adopted replacement or exact production rating; no sourcing check"]}
    validate_result(report, spec)
    (directory / "worker-result.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return 0


def replay_result(reports, spec):
    require(len(reports) == 2, "two cold workers required")
    normalized, raw = [], []
    for report in reports:
        validate_result(report, spec)
        value = json.loads(json.dumps(report))
        raw.append(value["artifact_sha256"].pop("Indicators.edg"))
        normalized.append(json.dumps(value, sort_keys=True))
    require(normalized[0] == normalized[1], "fresh-process semantic/text replay differs")
    return {"fresh_processes": 2, "semantic_and_text_replay": "pass", "raw_protobuf_sha256": raw,
            "raw_protobuf_byte_identical": raw[0] == raw[1], "canonical_edg_sha256": reports[0]["canonical_edg_sha256"]}


def run_worker(command, directory, timeout, power):
    registry, done = ProcessRegistry(grace_seconds=1), Event()
    def watch_power():
        while not done.wait(.1):
            if power is not None and power.poll() is not None:
                registry.cancel_all()
                return
    watcher = Thread(target=watch_power, daemon=True)
    watcher.start()
    log = directory.parent / (directory.name + ".log")
    try:
        result = registry.run(command, log, timeout, cwd=ROOT)
    finally:
        done.set()
        watcher.join(timeout=2)
        registry.cancel_all()
    require(result["exit_code"] == 0 and not result["orphaned_descendants"], "worker failed/timed out/left descendants; see " + str(log))
    require(power is None or power.poll() is None, "idle-sleep assertion ended during generation")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edg-python", type=Path, default=DEFAULT_PYTHON)
    parser.add_argument("--java-home", type=Path, default=DEFAULT_JAVA)
    parser.add_argument("--kicad-python", type=Path, default=DEFAULT_KICAD)
    parser.add_argument("--timeout", type=int, default=60, help="seconds per fresh worker")
    parser.add_argument("--worker", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    def interrupted(signum, frame):
        raise KeyboardInterrupt("Indicator reconstruction cancelled")
    previous_sigterm = signal.signal(signal.SIGTERM, interrupted)
    try:
        require(1 <= args.timeout <= 300, "worker timeout must be 1..300 seconds")
        if args.worker:
            return worker(args)
        work = ROOT / "work"
        require(work.is_dir() and not work.is_symlink(), "existing real work directory required")
        directory = Path(tempfile.mkdtemp(prefix="indicator-rebuild-", dir=work))
        started, awake, reports = time.monotonic(), {}, []
        source_data, parent_hashes = load_sources()
        spec = validate_sources(source_data)
        with keep_awake(awake, directory) as power:
            for index in range(2):
                target = directory / f"cold-{index + 1}"
                target.mkdir()
                command = [str(args.edg_python), "-B", str(Path(__file__).resolve()), "--worker", str(target),
                           "--java-home", str(args.java_home), "--kicad-python", str(args.kicad_python)]
                run_worker(command, target, args.timeout, power)
                report = json.loads((target / "worker-result.json").read_text())
                require(report["source_sha256"] == parent_hashes, "worker source coverage/freshness differs")
                validate_result(report, spec)
                validate_artifacts(report, target)
                reports.append(report)
            replay = replay_result(reports, spec)
            unchanged(reports[0]["source_sha256"])
            for index, report in enumerate(reports):
                validate_artifacts(report, directory / f"cold-{index + 1}")
        report = {**reports[0], "replay": replay, "caffeinate": awake, "elapsed_s": round(time.monotonic() - started, 3),
                  "worker_directories": ["cold-1", "cold-2"]}
        path = directory / "result.json"
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(json.dumps({"status": report["status"], "mechanics_status": "pass", "branches": 10,
                          "components": 20, "replay": "pass", "report": str(path)}))
        return 1
    except BaseException as exc:
        if isinstance(exc, SystemExit):
            raise
        print(json.dumps({"status": "cancelled" if isinstance(exc, KeyboardInterrupt) else "execution_error",
                          "qualified": False, "report": None, "error": f"{type(exc).__name__}: {exc}"}))
        return 130 if isinstance(exc, KeyboardInterrupt) else 2
    finally:
        signal.signal(signal.SIGTERM, previous_sigterm)


if __name__ == "__main__":
    raise SystemExit(main())
