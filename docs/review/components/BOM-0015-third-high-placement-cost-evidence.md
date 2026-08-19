# BOM-0015 — third high-placement cost-evidence batch

- Статус: **проведено ревью третьей партии; full cost coverage active**
- Дата: 2026-08-19
- Decision contract: [`DEC-0105`](../decisions/DEC-0105-machine-readable-quantity-100-cost-evidence.md)
- Review: [`REV-0005BN`](../reviews/REV-0005BN-third-cost-evidence-propagation.md)
- Generated review: [`G2F-3I-target-bom-review`](generated/G2F-3I-target-bom-review.md)
- Machine manifest: [`G2F-3I-target-bom.csv`](generated/G2F-3I-target-bom.csv)

## Результат

- exact published USD evidence: **39/187 purchase lines**;
- covered physical placements: **578/857**;
- still unpriced: **148/187 lines**;
- five unpriced lines retain explicit RFQ/retail comparability gates;
- covered base-product partial subtotal: **USD 79.0660 per device** at the
  quantity-100 component-price basis;
- orderability remains **186/187** and substitution-policy coverage remains
  **187/187**.

Третья партия добавляет **16 exact MPN**, **138 placements** и USD **10.2434**
к частичному base-product subtotal. Это всё ещё не COGS: PCB, PCBA, enclosure,
test/yield/tooling, logistics, tax и четыре не instantiated physical families
не входят в эту сумму.

## Третья ценовая партия

<details><summary><code>Texas Instruments TPD4E05U06DQAR</code> — 12 шт.</summary>

- Role: four-channel low-capacitance ESD protection.
- USD/unit @100: `0.3090`.
- USD/device: `3.7080`.

</details>

<details><summary><code>Murata GRM31CR71E106MA12L</code> — 12 шт.</summary>

- Role: 10-uF/25-V charger bulk capacitor.
- USD/unit @100: `0.1224`.
- USD/device: `1.4688`.

</details>

<details><summary><code>Yageo RC0402FR-07220KL</code> — 12 шт.</summary>

- Role: 220-kOhm accessory feedback resistor.
- USD/unit @100: `0.0097`.
- USD/device: `0.1164`.

</details>

<details><summary><code>onsemi 1N4148WT</code> — 10 шт.</summary>

- Role: compact switching diode.
- USD/unit @100: `0.0629`.
- USD/device: `0.6290`.

</details>

<details><summary><code>Yageo RC0402FR-071KL</code> — 10 шт.</summary>

- Role: service/debug current-limit resistor.
- USD/unit @100: `0.0097`.
- USD/device: `0.0970`.

</details>

<details><summary><code>Yageo RC0402FR-071ML</code> — 10 шт.</summary>

- Role: service-VBUS bleeder.
- USD/unit @100: `0.0097`.
- USD/device: `0.0970`.

</details>

<details><summary><code>Yageo RC0402FR-0747KL</code> — 9 шт.</summary>

- Role: eFuse OVLO divider resistor.
- USD/unit @100: `0.0097`.
- USD/device: `0.0873`.

</details>

<details><summary><code>Murata GRM155R71H103KA88D</code> — 8 шт.</summary>

- Role: ADC filter capacitor.
- USD/unit @100: `0.0121`.
- USD/device: `0.0968`.

</details>

<details><summary><code>Nexperia 74LVC126APW,118</code> — 8 шт.</summary>

- Role: quad partial-power-down-safe three-state buffer.
- USD/unit @100: `0.1341`.
- USD/device: `1.0728`.

</details>

<details><summary><code>Yageo RC0603FR-071KL</code> — 8 шт.</summary>

- Role: external-rail bleeder.
- USD/unit @100: `0.0122`.
- USD/device: `0.0976`.

</details>

<details><summary><code>Murata GRM1555C1H121JA01D</code> — 7 шт.</summary>

- Role: eFuse transient-timer C0G capacitor.
- USD/unit @100: `0.0197`.
- USD/device: `0.1379`.

</details>

<details><summary><code>Texas Instruments TPS22919DCKR</code> — 7 шт.</summary>

- Role: protected load switch with quick-output discharge.
- USD/unit @100: `0.1189`.
- USD/device: `0.8323`.

</details>

<details><summary><code>Yageo RC0402FR-07100RL</code> — 7 шт.</summary>

- Role: charger BATP series resistor.
- USD/unit @100: `0.0097`.
- USD/device: `0.0679`.

</details>

<details><summary><code>Alps Alpine SKQGADE010</code> — 6 шт.</summary>

- Role: service BOOT/RESET tactile switch.
- USD/unit @100: `0.2248`.
- USD/device: `1.3488`.

</details>

<details><summary><code>Texas Instruments SN74LVC1G126DCKR</code> — 6 шт.</summary>

- Role: single partial-power-down-safe three-state buffer.
- USD/unit @100: `0.0546`.
- USD/device: `0.3276`.

</details>

<details><summary><code>Yageo RC0402FR-07470RL</code> — 6 шт.</summary>

- Role: debug-contention current-limit resistor.
- USD/unit @100: `0.0097`.
- USD/device: `0.0582`.

</details>

Canonical source URL, price-break wording, checked date and placement list are
kept in the generated Markdown/CSV and the machine database.

## Исправленные несоответствия источников

- `TPS22919DCKR`: stale DigiKey product ID `10434801` replaced with current
  exact-MPN page `10435170`.
- `RC0402FR-07220KL`: wrong product ID `726686` replaced with exact-MPN page
  `726564`.
- `RC0402FR-071ML`: wrong product ID `729472` replaced with exact-MPN page
  `729462`.

MPN, quantity, electrical role, contacts, pin ownership and architecture are
unchanged. Therefore the principled vertical diagram does not require a
revision for this batch.

## Открыто

1. Price the remaining 148 purchase lines, prioritising expensive base-product
   IC, RF and connector lines rather than alphabetical order.
2. Request the five explicit quotes without mixing base, accessory and
   regional-cell scopes.
3. Instantiate SMA, RF cable, M5 connector and antenna-kit physical families.
4. Keep PCB/PCBA/enclosure/test quotes separate until the factory package is
   stable.
