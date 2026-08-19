# FND-0036 — current CAD source cannot represent target compute platform

- Статус: **Закрыто на уровне CAD representation решением DEC-0030; проведено ревью**
- Дата: 2026-08-16
- Затрагивает: `C-001…007`, stage-4 CAD evidence, future schematic implementation

## Несоответствие

Current `hardware/tscircuit` identifies S3 N8R2, depends on mutable `jlcpcb:` parts-engine identities, contains legacy buses/owners and has no RP2354A domain. Installed KiCad 10.0.5 has no C5 WROOM-1U library entry and its available S3 symbol defaults to the wrong antenna variant footprint. Therefore neither current source path is a reproducible exact representation of accepted `PKG-0001/SYN-3A`.

## Impact

- a mechanically similar module footprint could silently retain the wrong memory MPN;
- a parts-engine or global-library update could change pads without a repository diff;
- C5 v1.2 procurement identity cannot be expressed by generic footprint alone;
- RP clock, exposed pad and recovery cannot receive ERC/DRC evidence from the current source;
- patching the legacy board would reintroduce owners/buses already rejected by the zero-based architecture.

## Applied correction

1. owner selected repository-vendored option A in `IMP-0025`;
2. exact project symbol/footprint assets, provenance, attribution and CI checks
   now live under `hardware/kicad`;
3. all five rows pass pin/type, pad/geometry, file-hash and KiCad 10.0.5 parser
   validation in `REV-0004E`;
4. legacy tsCircuit outputs remain noncanonical;
5. the reviewed libraries become inputs only when stage 8 creates the new
   target schematic.

No accepted capability or owner changed. Component Q, final schematic,
ERC/DRC, assembly, antenna/thermal and HIL proof remain open; they are not part
of this now-closed CAD representation defect.
