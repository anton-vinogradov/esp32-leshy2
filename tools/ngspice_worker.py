#!/usr/bin/env python3
"""One headless ngspice operating point per fresh process; never qualification.

Read {"netlist": [title, ... , ".end"], "vectors": ["v(out)"]} from stdin.
Use the existing shared library, no init files, model files or user commands.
The caller must impose a subprocess timeout on untrusted/nonconvergent models.
"""

import argparse
import ctypes as C
import hashlib
import json
import math
import os
from pathlib import Path
import pwd
import re
import sys

DEFAULT_LIBRARY = Path("/Applications/KiCad/KiCad.app/Contents/PlugIns/sim/libngspice.0.dylib")
MAX_INPUT = 2_000_000
MAX_LOG = 32_768
DIRECTIVES = {".subckt", ".ends", ".model", ".param", ".func", ".temp", ".global", ".op", ".end"}
VECTOR = re.compile(r"(?:[vi]\([a-z0-9_][a-z0-9_.:#-]*\)|[a-z0-9_][a-z0-9_.:#-]*)", re.I)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_request(request):
    require(type(request) is dict and set(request) == {"netlist", "vectors"}, "expected only netlist and vectors")
    lines, vectors = request["netlist"], request["vectors"]
    require(type(lines) is list and 3 <= len(lines) <= 20_000, "bounded nonempty netlist required")
    require(all(type(line) is str and len(line) <= 4096 and not any(c in line for c in "\x00\r\n")
                and line.isascii() for line in lines), "netlist lines must be bounded single-line ASCII")
    require(lines[0].strip() and not lines[0].lstrip().startswith((".", "+")), "netlist title required")
    ended, prior = False, False
    for line in lines[1:]:
        text = line.strip()
        if not text or text.startswith("*"):
            continue
        require(not ended, "content after .end")
        require(not any(token in text for token in ("`", "$(", "\\", ";")), "unsafe netlist token")
        require(not re.search(r"\b(?:file|filename|rfile|wfile)\s*=|\bpwlfile\b", text, re.I), "external model data forbidden")
        token = text.split()[0].lower()
        if token.startswith("."):
            require(token in DIRECTIVES, "unsupported directive: " + token)
            if token == ".end":
                require(text.lower() == ".end", "bare .end required")
                ended = True
        elif token.startswith("+"):
            require(prior and not text[1:].lstrip().startswith("."), "orphan or directive continuation")
        else:
            # In particular exclude XSPICE A/code-model file sources and HDL.
            require(token[0] in "rclkvibefghdqjmswxt", "unsupported element: " + token)
        prior = True
    require(ended, "final .end required")
    require(type(vectors) is list and 1 <= len(vectors) <= 128, "bounded nonempty vectors required")
    require(all(type(v) is str and len(v) <= 160 and VECTOR.fullmatch(v) for v in vectors), "unsafe or empty vector")
    require(len({v.lower() for v in vectors}) == len(vectors), "duplicate vectors")
    return lines, vectors


class Complex(C.Structure):
    _fields_ = [("real", C.c_double), ("imag", C.c_double)]


class VectorInfo(C.Structure):
    _fields_ = [("name", C.c_char_p), ("type", C.c_int), ("flags", C.c_short),
                ("realdata", C.POINTER(C.c_double)), ("compdata", C.POINTER(Complex)), ("length", C.c_int)]


SendChar = C.CFUNCTYPE(C.c_int, C.c_char_p, C.c_int, C.c_void_p)
ControlledExit = C.CFUNCTYPE(C.c_int, C.c_int, C.c_bool, C.c_bool, C.c_int, C.c_void_p)
SendData = C.CFUNCTYPE(C.c_int, C.c_void_p, C.c_int, C.c_int, C.c_void_p)
SendInit = C.CFUNCTYPE(C.c_int, C.c_void_p, C.c_int, C.c_void_p)
BgRunning = C.CFUNCTYPE(C.c_int, C.c_bool, C.c_int, C.c_void_p)


class Messages:
    def __init__(self):
        self.errors, self.version, self.written = [], None, 0

    def error(self, message):
        if len(self.errors) < 8:
            self.errors.append(message[:512])

    def receive(self, raw, _ident, _user):
        text = raw.decode("utf-8", errors="replace") if raw else ""
        match = re.search(r"ngspice-([0-9][\w.-]*)", text, re.I)
        if match:
            self.version = match[1]
        if text == "stderr Warning: can't find the initialization file spinit.":
            pass  # Expected: SPICE_SCRIPTS is forced to /dev/null below.
        elif re.search(r"\b(error|fatal|failed|unknown|unrecognized|unsupported|ignored)\b|can't|cannot|singular matrix", text, re.I):
            self.error(text)
        elif text.startswith("stderr ") and not text.startswith(("stderr Warning:", "stderr Note:")):
            self.error(text)
        remaining = MAX_LOG - self.written
        if remaining > 0:
            segment = (text + "\n")[:remaining]
            sys.stderr.write(segment)
            self.written += len(segment)
        return 0

    def controlled_exit(self, status, immediate, _quit, _ident, _user):
        self.error(f"ngspice controlled exit: status={status}, immediate={immediate}")
        return 0

    def check(self, result, stage):
        require(result == 0 and not self.errors, stage + " failed: " + "; ".join(self.errors or [str(result)]))


def read_vector(library, name):
    info = library.ngGet_Vec_Info(name.encode("ascii"))
    require(bool(info), "missing vector: " + name)
    value = info.contents
    require(value.length == 1, "not one operating-point value: " + name)
    require(bool(value.realdata) and not bool(value.compdata) and not value.flags & 2,
            "complex or non-real vector: " + name)
    number = value.realdata[0]
    require(math.isfinite(number), "nonfinite vector: " + name)
    return number


def reject_init_files():
    # ngspice 45.2's no-spinit API crashes before Init. Its shared Init checks
    # cwd then the OS account home (not $HOME); refuse either file, never edit it.
    directories = {Path.cwd(), Path(pwd.getpwuid(os.getuid()).pw_dir)}
    directories.update(Path(os.environ[key]) for key in ("HOME", "SPICE_USERINIT_DIR") if os.environ.get(key))
    for directory in directories:
        require(not os.path.lexists(directory / ".spiceinit"), "external init file present: " + str(directory / ".spiceinit"))


def runtime_paths(library_path=DEFAULT_LIBRARY):
    library = Path(library_path).resolve(strict=True)
    models = [library.parent / "ngspice" / name for name in ("analog.cm", "xtradev.cm")]
    require(library.is_file(), "shared library file required")
    for path in models:
        require(path.is_file() and not path.is_symlink(), "packaged code model required: " + path.name)
        require(not any(c.isspace() or c in '\";`$' for c in str(path)), "unsafe packaged code-model path")
    return [library, *models]


def run_request(request, library_path=DEFAULT_LIBRARY):
    lines, vectors = validate_request(request)
    path, *models = runtime_paths(library_path)
    # The native PSpice translator uses the packaged aswitch model. Load only
    # fixed adjacent bundles (aswitch is in xtradev), never request-selected paths.
    def hashes():
        return {"worker_sha256": sha(__file__), "library_sha256": sha(path),
                "code_model_sha256": {str(model): sha(model) for model in models}}
    before = hashes()
    library = C.CDLL(str(path))
    messages = Messages()
    # The callbacks and line storage remain strongly referenced throughout every
    # synchronous native call. This worker never starts a background simulation.
    callbacks = (SendChar(messages.receive), SendChar(lambda *_: 0), ControlledExit(messages.controlled_exit),
                 SendData(lambda *_: 0), SendInit(lambda *_: 0), BgRunning(lambda *_: 0))
    library.ngSpice_Init.argtypes = [SendChar, SendChar, ControlledExit, SendData, SendInit, BgRunning, C.c_void_p]
    library.ngSpice_Init.restype = C.c_int
    library.ngSpice_Command.argtypes, library.ngSpice_Command.restype = [C.c_char_p], C.c_int
    library.ngSpice_Circ.argtypes, library.ngSpice_Circ.restype = [C.POINTER(C.c_char_p)], C.c_int
    library.ngGet_Vec_Info.argtypes, library.ngGet_Vec_Info.restype = [C.c_char_p], C.POINTER(VectorInfo)
    reject_init_files()
    old_scripts = os.environ.get("SPICE_SCRIPTS")
    os.environ["SPICE_SCRIPTS"] = "/dev/null"
    try:
        messages.check(library.ngSpice_Init(*callbacks, None), "initialization")
    finally:
        if old_scripts is None:
            os.environ.pop("SPICE_SCRIPTS", None)
        else:
            os.environ["SPICE_SCRIPTS"] = old_scripts
    reject_init_files()
    require(messages.version is not None, "ngspice version missing")
    messages.check(library.ngSpice_Command(b"set ngbehavior=psa"), "PSpice whole-deck compatibility selection")
    for model in models:
        messages.check(library.ngSpice_Command(("codemodel " + str(model)).encode()), "packaged code model")
    encoded = [line.encode("ascii") for line in lines]
    circuit = (C.c_char_p * (len(encoded) + 1))(*encoded, None)
    messages.check(library.ngSpice_Circ(circuit), "circuit parse")
    messages.check(library.ngSpice_Command(b"op"), "operating point")
    values = {name: read_vector(library, name) for name in vectors}
    messages.check(0, "vector extraction")
    require(before == hashes(), "worker/library/code model changed during execution")
    return {"schema_version": 1, "status": "worker_execution_success", "qualified": False,
            "scope": "One modeled DC operating point only; not hardware qualification", "analysis": "op",
            "ngspice_version": messages.version, "library": str(path), **before,
            "request_sha256": hashlib.sha256(json.dumps(request, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "values": values}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--request", type=Path, help="read this JSON request instead of stdin (no SPICE file loading)")
    args = parser.parse_args(argv)
    try:
        if args.request is None:
            raw = sys.stdin.read(MAX_INPUT + 1)
        else:
            require(args.request.is_file() and not args.request.is_symlink(), "real request JSON file required")
            with args.request.open(encoding="utf-8") as stream:
                raw = stream.read(MAX_INPUT + 1)
        require(len(raw) <= MAX_INPUT, "request too large")
        request = json.loads(raw)
        result = run_request(request, args.library)
    except Exception as error:
        result = {"schema_version": 1, "status": "execution_error", "qualified": False,
                  "error": f"{type(error).__name__}: {error}"[:2048]}
        print(json.dumps(result, allow_nan=False))
        return 2
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
