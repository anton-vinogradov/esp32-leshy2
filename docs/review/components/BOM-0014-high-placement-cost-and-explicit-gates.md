# BOM-0014 — high-placement cost batch and explicit unpriced gates

- Статус: **проведено ревью второй партии; full cost coverage active**
- Дата: 2026-08-19
- Decisions: [`DEC-0105`](../decisions/DEC-0105-machine-readable-quantity-100-cost-evidence.md),
  [`DEC-0106`](../decisions/DEC-0106-explicit-unpriced-cost-gates.md)
- Review: [`REV-0005BM`](../reviews/REV-0005BM-second-cost-evidence-propagation.md)
- Generated review: [`G2F-3I-target-bom-review`](generated/G2F-3I-target-bom-review.md)
- Machine manifest: [`G2F-3I-target-bom.csv`](generated/G2F-3I-target-bom.csv)

## Результат

- exact published USD evidence: **23/187 purchase lines**;
- covered physical placements: **440/857**;
- still unpriced: **164/187 lines**;
- five unpriced lines now have explicit RFQ/retail comparability gates;
- covered base-product partial subtotal: **USD 68.8226 per device** at the
  quantity-100 component-price basis;
- orderability remains **186/187** and substitution-policy coverage remains
  **187/187**.

Это по-прежнему не COGS: component-price coverage не включает PCB, PCBA,
корпус, test/yield/tooling, логистику, налоги и четыре ещё не instantiated
physical families.

## Вторая ценовая партия

Восемь exact passive MPN дают **418** дополнительных placements и USD
**11.5724** к частичному subtotal. Для узкого экрана строки приведены
вертикальными карточками:

<details><summary><code>Yageo RC0402FR-0710KL</code> — 167 шт.</summary>

- USD/unit @100: `0.0097`.
- USD/device: `1.6199`.

</details>

<details><summary><code>TDK C1005X7R1H104K050BB</code> — 100 шт.</summary>

- USD/unit @100: `0.0258`.
- USD/device: `2.5800`.

</details>

<details><summary><code>Panasonic ERJ-2RKF22R0X</code> — 45 шт.</summary>

- USD/unit @100: `0.0155`.
- USD/device: `0.6975`.

</details>

<details><summary><code>TDK C1608X7R1C105K080AC</code> — 34 шт.</summary>

- USD/unit @100: `0.0392`.
- USD/device: `1.3328`.

</details>

<details><summary><code>Yageo RC0402FR-07100KL</code> — 28 шт.</summary>

- USD/unit @100: `0.0097`.
- USD/device: `0.2716`.

</details>

<details><summary><code>Murata GRM188R60J106ME47D</code> — 17 шт.</summary>

- USD/unit @100: `0.0377`.
- USD/device: `0.6409`.

</details>

<details><summary><code>Yageo RC0402FR-072K2L</code> — 14 шт.</summary>

- USD/unit @100: `0.0097`.
- USD/device: `0.1358`.

</details>

<details><summary><code>Murata GRM32ER71E226KE15L</code> — 13 шт.</summary>

- USD/unit @100: `0.3303`.
- USD/device: `4.2939`.

</details>

Таблица — batch summary. Канонические source URL, price-break wording, checked
date и placement list находятся в generated Markdown/CSV.

## Явные cost gates

- `Ebyte E01-ML01IPX ×3` — base product; quantity-100 RFQ; нужен numeric
  manufacturer quote для опубликованной ступени 100–999.
- `NiceRF SA518 ×1` — base product; quantity-100 RFQ; нужен production quote
  на exact current module.
- `HMX035CTFT-001 ×1` — base product; standalone assembly RFQ; нужна цена raw
  LCM+CTP, не donor board.
- `XTAR 18650 4000mAh ×2` — regional cell kit; regional retail only; нужен
  exact protected-cell production/lot quote.
- `M5Stack U214 ×1` — optional accessory; retail only; нужен quantity-100
  quote, остающийся вне base product.

U214 retail USD 14.50 intentionally does not enter either base subtotal or
quantity-100 evidence. The same rule prevents donor-board price from becoming
the raw-display cost and prevents RFQ-only radios from becoming zero.

## Открыто

1. Price the next high-value/base-product IC and interconnect lines.
2. Request the five explicit quotes without mixing scopes.
3. Instantiate SMA, RF cable, M5 connector and antenna-kit physical families.
4. Add PCB/PCBA/enclosure/test quotes only after component coverage is
   complete enough to define a stable factory package.

## Последующий статус

Этот artifact сохраняет проверенный second-batch checkpoint. Текущий итог
после восьмой партии находится в
[`BOM-0020`](BOM-0020-control-protection-rf-cost-evidence.md): 106/187 lines,
747/857 placements и partial base subtotal USD 140.7642.
