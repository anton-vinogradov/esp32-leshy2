# BOM-0016 — high-value IC/RF cost-evidence batch

- Статус: **проведено ревью четвёртой партии; full cost coverage active**
- Дата: 2026-08-19
- Decision contract: [`DEC-0105`](../decisions/DEC-0105-machine-readable-quantity-100-cost-evidence.md)
- Review: [`REV-0005BO`](../reviews/REV-0005BO-high-value-cost-evidence-propagation.md)
- Generated review: [`G2F-3I-target-bom-review`](generated/G2F-3I-target-bom-review.md)
- Machine manifest: [`G2F-3I-target-bom.csv`](generated/G2F-3I-target-bom.csv)

## Результат

- exact published USD evidence: **52/187 purchase lines**;
- covered physical placements: **614/857**;
- still unpriced: **135/187 lines**;
- five unpriced lines retain explicit RFQ/retail comparability gates;
- covered base-product partial subtotal: **USD 102.2205 per device**;
- orderability remains **186/187** and substitution-policy coverage remains
  **187/187**.

Четвёртая партия добавляет **13 exact MPN**, **36 placements** и USD
**23.1545**. Приоритетом были expensive base-product IC, RF and interconnect
lines, поэтому небольшой прирост placement coverage даёт больший прирост
полезности subtotal. Это всё ещё component-price coverage, а не COGS.

## Четвёртая ценовая партия

<details><summary><code>Samtec FTSH-105-01-L-DV-K-P-TR</code> — 3 шт.</summary>

- Role: keyed 10-contact programming/recovery header.
- USD/unit @100: `1.6991`; USD/device: `5.0973`.

</details>

<details><summary><code>Texas Instruments TPS3808G33DBVR</code> — 4 шт.</summary>

- Role: adjustable-delay supply supervisor.
- USD/unit @100: `1.0984`; USD/device: `4.3936`.

</details>

<details><summary><code>TTM Technologies DC2337J5010AHF</code> — 3 шт.</summary>

- Role: nRF forward-power directional coupler.
- USD/unit @100: `1.0291`; USD/device: `3.0873`.

</details>

<details><summary><code>Texas Instruments TLV1824PWR</code> — 2 шт.</summary>

- Role: quad open-drain hardware threshold comparator.
- USD/unit @100: `1.0518`; USD/device: `2.1036`.

</details>

<details><summary><code>Texas Instruments TPS259470LRPWR</code> — 2 шт.</summary>

- Role: reverse-blocking latch-off eFuse.
- USD/unit @100: `1.0196`; USD/device: `2.0392`.

</details>

<details><summary><code>Texas Instruments TPS25974LRPWR</code> — 2 шт.</summary>

- Role: 7-A latch-off eFuse with power-good.
- USD/unit @100: `0.7929`; USD/device: `1.5858`.

</details>

<details><summary><code>Nexperia 74LVC2G126DC,125</code> — 5 шт.</summary>

- Role: dual partial-power-down-safe three-state buffer.
- USD/unit @100: `0.2086`; USD/device: `1.0430`.

</details>

<details><summary><code>onsemi FSUSB42MUX</code> — 2 шт.</summary>

- Role: powered-off-protected USB 2.0 isolation switch.
- USD/unit @100: `0.4663`; USD/device: `0.9326`.

</details>

<details><summary><code>Texas Instruments TPS564252DRLR</code> — 3 шт.</summary>

- Role: 4-A synchronous buck regulator.
- USD/unit @100: `0.2953`; USD/device: `0.8859`.

</details>

<details><summary><code>KYOCERA AVX CP0603Q5425ENTR</code> — 2 шт.</summary>

- Role: dual-band native-radio directional coupler.
- USD/unit @100: `0.4271`; USD/device: `0.8542`.

</details>

<details><summary><code>Texas Instruments MSPM0C1104SDGS20R</code> — 1 шт.</summary>

- Role: independently recoverable admission/safety controller.
- USD/unit @100: `0.4523`; USD/device: `0.4523`.

</details>

<details><summary><code>Infineon BGS13SN8E6327XTSA1</code> — 2 шт.</summary>

- Role: 100-MHz-to-6-GHz SP3T RF switch.
- USD/unit @100: `0.2126`; USD/device: `0.4252`.

</details>

<details><summary><code>Texas Instruments SN74LVC1G07DCKR</code> — 5 шт.</summary>

- Role: open-drain partial-power-down-safe observation buffer.
- USD/unit @100: `0.0509`; USD/device: `0.2545`.

</details>

Canonical price source, basis, checked date and placements remain in the
machine database and generated artifacts.

No MPN, physical device, function, contact, pin owner, rail or signal changed;
the vertical principled diagram therefore remains current.

## Открыто

1. Price the remaining 135 purchase lines, continuing with the largest
   base-product material uncertainty.
2. Add explicit gates for exact lines whose MOQ/RFQ structure cannot produce a
   comparable quantity-100 value.
3. Close standalone display orderability and four uninstantiated physical
   families before claiming complete I8 or factory COGS.
