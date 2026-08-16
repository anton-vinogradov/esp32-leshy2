# IMP-0029 — open personal FIDO authenticator, not a false certified token

- Статус: **Принят вариант A; `DEC-0035`**
- Дата: 2026-08-16
- Delta: `W-EXTRA-12`
- Evidence: [`AUD-0006`](../audits/AUD-0006-fido-authenticator-security-boundary.md)
- Finding: [`FND-0043`](../findings/FND-0043-open-multitool-is-not-a-hardware-security-key.md)

## Контекст

Leshy2 технически может стать USB authenticator, но U2F-only уже устаревший
scope. Современный public target — CTAP 2.3 over USB HID с CTAP1/U2F backward
compatibility. Главный риск не transport, а то, что security secrets окажутся
в одном runtime с Lab, radios, storage, scripts, updates and debug.

## Options

### A — open personal authenticator

Добавить в Main отдельный Authenticator Mode: clean transition/reboot в
минимальный CTAPHID-only runtime, CTAP 2.3 + U2F compatibility, client PIN,
discoverable/non-discoverable credentials, credential management, новый local
user-presence gesture для каждой регистрации/подписи и destructive reset.

Credentials device-bound и не экспортируются/не попадают в общий backup.
Recovery делается вторым заранее зарегистрированным authenticator/account
codes. Attestation — none/self; claims `FIDO Certified`, hardware-backed and
tamper-resistant запрещены без последующего proof. Owner-controlled open
firmware/recovery сохраняются, но custom/debug state честно снижает assurance.

- Плюсы: phishing-resistant practical capability, open source, почти без
  обязательного нового RF/BOM, современная совместимость.
- Минусы: требуется серьёзная isolation/crypto/persistence/conformance работа;
  потеря устройства означает потерю его credentials; физический доступ к
  общему unlocked compute не покрыт hardware-token claim.

### B — certification-ready hardware-backed first product

Сразу потребовать отдельный security domain, provisioning/attestation lifecycle
и certification-ready design. Остальная Leshy2 может оставаться открытой, но
security profile почти наверняка потребует собственной update/debug boundary и,
возможно, отдельной locked production variant.

- Плюсы: выше achievable assurance, enterprise/certification path.
- Минусы: новый BOM/board/resource/provisioning/test/certification burden,
  риск закрытых dependencies и задержки; certification всё равно не обещана до
  фактического прохождения процесса.

### C — defer

Не хранить реальные account credentials на первом Leshy2; оставить вопрос для
внешнего dedicated key или будущей revision.

- Плюсы: минимальный security/NRE risk.
- Минус: полезный competitor result отсутствует.

## Recommendation

**Принят A** в
[`DEC-0035`](../decisions/DEC-0035-open-personal-fido-authenticator.md). Это
сохраняет открытость устройства и даёт реальную современную
аутентификацию без ложной маркетинговой надстройки. Hardware-backed/certified
variant остаётся возможным позднейшим усилением, а не скрытым обязательным BOM.

## Acceptance boundary for A

- current CTAP Proposed Standard baseline + U2F compatibility;
- exclusive CTAPHID-only Authenticator Mode; Lab/radios/scripts/shared storage
  and other USB classes unavailable;
- explicit per-operation local user presence, RP/user display where available;
- PIN protocol 2, retries/lockout, `hmac-secret`, `credProtect`, credential
  management and published credential capacity;
- device-bound non-exportable secrets excluded from ordinary backup;
- none/self attestation, non-certified AAGUID, truthful firmware/certification
  metadata and no protected-security claims without proof;
- reset/update/rollback/debug/fault behavior cannot restore authorization,
  clone secrets or roll back a claimed non-zero counter;
- protocol conformance, Windows/macOS/Linux/browser interoperability, fuzzing,
  power-loss/update/reset and cross-interface isolation HIL before release.
