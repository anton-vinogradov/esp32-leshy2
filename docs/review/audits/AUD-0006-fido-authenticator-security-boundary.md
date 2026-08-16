# AUD-0006 — U2F/FIDO authenticator capability and security boundary

- Статус: **Проведено ревью; вариант A принят `DEC-0035`**
- Дата snapshot: 2026-08-16
- Delta: `W-EXTRA-12`
- Предложение: [`IMP-0029`](../improvements/IMP-0029-open-personal-fido-authenticator.md)
- Finding: [`FND-0043`](../findings/FND-0043-open-multitool-is-not-a-hardware-security-key.md)
- Решение: [`DEC-0035`](../decisions/DEC-0035-open-personal-fido-authenticator.md)

## Короткий вывод

Функция технически реализуема и полезна, но её нельзя честно называть только
`U2F`: актуальный target — roaming FIDO2 authenticator по CTAP 2.3 через USB
HID, а CTAP1/U2F остаётся backward compatibility. Leshy2 реализует CTAP side;
WebAuthn API выполняют browser/platform и relying party, не прошивка устройства.

Открытое устройство может быть совместимым personal authenticator и оставаться
полностью open source. Оно не становится автоматически FIDO Certified,
hardware-backed или tamper-resistant. Эти claims требуют отдельной security
architecture, provisioning/evaluation/certification и доказательств.

## Актуальная protocol baseline

На дату snapshot официальный index FIDO публикует CTAP 2.3 Proposed Standard от
2026-02-26 и более новый 2.3.1 Working Draft. Стабильной implementation baseline
выбирается Proposed Standard 2.3; moving Working Draft не становится product
contract молча.

CTAP 2.3:

- определяет CTAP2/FIDO2 authenticator и CTAP1/U2F compatibility;
- использует CTAPHID для driverless USB transport;
- рекомендует public authenticator поддерживать CTAP1/U2F, иначе часть сайтов
  может воспринимать его как сломанный;
- при объявлении `FIDO_2_3` требует `hmac-secret`; discoverable credentials
  требуют PIN либо built-in UV и credential management; UV требует
  `credProtect`, а PIN/UV использует protocol 2;
- требует, чтобы credentials, counters и PIN, доступные через FIDO interfaces,
  не были observable/alterable через другие undefined interfaces.

ESP-IDF/TinyUSB подтверждает техническую USB-device/HID достижимость для
ESP32-S3-class candidate, но это только transport evidence. Target compute и
USB owner ещё не выбраны; USB HID example не доказывает CTAP, secret lifecycle
или isolation.

## Почему многофункциональность меняет threat model

Обычный Leshy2 должен иметь radios, storage, Lab tools, scripts, update,
recovery и diagnostic interfaces. FIDO же требует, чтобы auth state не
просматривался и не менялся через иные interfaces. Если authenticator работает
рядом с shell, mass storage, BadUSB/keyboard, vendor RPC или Lab parser в одном
runtime, одна ошибка превращает security key в канал утечки или неподтверждённой
подписи.

Поэтому software-only вариант допустим только как отдельный **Authenticator
Mode**:

1. явный вход из Main и clean reboot/transition в минимальный runtime;
2. USB exposes CTAPHID only; CDC/MSC/keyboard/vendor commands отсутствуют;
3. radios, Lab/Controlled Zone, scripts/plugins and shared removable storage
   недоступны;
4. каждая завершённая registration/assertion, заявляющая user presence,
   требует нового local action; cached presence по умолчанию отсутствует;
5. display показывает доступные RP/user data и различает registration,
   assertion, PIN management, credential deletion и reset;
6. выход, fault, update, debug/recovery transition or reset очищает volatile
   authorization and CTAP transactions.

Это уменьшает remote/software attack surface, но не создаёт физическую
tamper-resistance общего MCU.

## Credentials, backup and recovery truth

WebAuthn различает single-device и multi-device credentials флагами BE/BS. Для
single-device credential generating authenticator обещает, что credential не
будет backup-eligible. Стандарт не задаёт protocol backup/private-key sharing и
в общем случае ожидает, что credential private key не покидает authenticator.

Следовательно, ordinary full-device backup Leshy2 не должен содержать FIDO
private keys, wrapping master secret, PIN state или counters. Restore такого
backup на другое устройство иначе клонирует authenticator и разрушает честную
single-device semantics. Рекомендуемый recovery — заранее зарегистрировать
второй authenticator и сохранить account recovery codes.

Настоящий multi-device/backup credential manager возможен технически, но это
другой security product: он должен ставить BE/BS правдиво, проектировать
encrypted sync/import/export, conflict/revocation/audit and endpoint trust. Он
не добавляется как скрытая опция к первой версии.

Non-discoverable credentials могут храниться как encrypted credential IDs у
relying party, но их wrapping master secret всё равно является device secret.
Discoverable credentials хранятся локально и требуют published capacity,
atomic persistence and credential-management behavior.

## User presence, PIN and reset

- USB insertion itself is not user presence; a distinct local gesture is
  required for each registration/assertion.
- PIN provides user verification but does not replace USB user presence.
- PIN retries, lockout and protocol-two state follow CTAP 2.3 and are not
  shared with general device unlock.
- authenticator reset requires a destructive on-device ceremony; long hold
  plus explicit display confirmation is the product candidate.
- factory reset wipes every credential, wrapping secret, PIN and pending state;
  it never silently restores them from general backup.

## Attestation, counters and claims

For an open personal authenticator the honest privacy default is no attestation
or self attestation, a non-certified AAGUID, monotonic firmware version and no
claimed certification entries. Shared batch attestation keys are not placed in
source or ordinary owner backups.

`FIDO Certified` marks require the Alliance process, supporting documents and
the applicable security/privacy requirements. Conformance with wire protocol
alone does not grant that claim.

Signature counters are either protected from rollback across supported update
paths or reported as zero. A rollbackable non-zero counter is worse than an
honest zero because relying parties can draw false clone-detection conclusions.

## Openness versus assurance

Open hardware/firmware and owner-controlled signed updates are compatible with
an authenticator. SoloKeys is a current public example of open source firmware
with distinct Secure and Hacker provisioning profiles. The lesson is not to
copy its architecture, but to separate openness from claims:

- owner-buildable firmware remains possible;
- a firmware image that can access the authenticator trust domain can also
  exfiltrate or misuse its secrets;
- code signing authenticates the accepted updater, not the goodness of code;
- active debug or owner-custom firmware lowers assurance and must never retain
  a certified/hardware-backed label by inertia.

A later dedicated security domain can improve the boundary without closing the
rest of Leshy2, but only if it enforces credential policy and user presence
rather than acting as a generic signing oracle. It adds BOM, provisioning,
update/recovery and possibly separate locked/unlocked product profiles.

## Sources

- [FIDO specification index](https://fidoalliance.org/specifications/download/)
- [CTAP 2.3 Proposed Standard, 2026-02-26](https://fidoalliance.org/specs/fido-v2.3-ps-20260226/fido-client-to-authenticator-protocol-v2.3-ps-20260226.html)
- [W3C Web Authentication Level 3](https://www.w3.org/TR/webauthn-3/)
- [FIDO Authenticator Security and Privacy Requirements v1.6](https://fidoalliance.org/specs/fido-security-requirements/fido-authenticator-security-requirements-v1.6-fd-20250312.html)
- [FIDO Authenticator Certification Levels](https://fidoalliance.org/certification/authenticator-certification-levels/)
- [ESP-IDF ESP32-S3 USB Device Stack](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/usb_device.html)
- [Flipper Zero U2F documentation](https://docs.flipper.net/zero/u2f)
- [Solo 2 open-source security-key firmware](https://github.com/solokeys/solo2)

## Audit gate

- [x] current protocol family/version checked;
- [x] U2F compatibility separated from modern target;
- [x] transport feasibility separated from authenticator security;
- [x] Main/Lab/Controlled-Zone interaction addressed;
- [x] backup, user presence, PIN, reset, attestation and certification boundaries;
- [x] openness preserved without false hardware-token assurance;
- [x] owner accepted option A in `DEC-0035`;
- [x] accepted scope became `REQ-FIDO-0001`.
