# Предложения по улучшениям

Здесь фиксируются доказуемые способы обойти ограничения legacy-дизайна или существенно улучшить получение артефактов.

Каждое `IMP-*` должно содержать:

- точную формулировку старого ограничения и ссылку на legacy-артефакт;
- почему ограничение больше не обязательно;
- предлагаемый обход;
- подтверждающие источники, расчёт или эксперимент;
- стоимость, сложность и новые риски;
- затрагиваемые требования, решения и этапы;
- решение владельца проекта: принять, отклонить или отложить.

Предложение не меняет scope и не становится архитектурным решением до явного согласия владельца проекта.

Последнее закрытое предложение в активной цепочке
[`IMP-0042`](IMP-0042-external-sma-gender-and-feed-policy.md) принято вариантом
B/`DEC-0050`: две native-Wi-Fi RP-SMA и семь standard SMA.

[`IMP-0043`](IMP-0043-profiled-antenna-kit.md) принято как `DEC-0055`:
профилированный комплект с общими MPN для S3/C5 и трёх nRF, combined 868/915,
но отдельными 315/433, VHF/UHF и Si4732 whip/loop profiles. Availability теперь
проверяется при выборе exact MPN. `FND-0058` по-прежнему не позволяет считать
sourcing shortlist production qualification, а `FND-0057` требует specimen
proof generic Ebyte `IPX` mating family.

⚠️ Предложение [`IMP-0047`](IMP-0047-one-stop-pcba-antenna-kitting-policy.md)
открыто: считать one-stop PCBA + antenna kitting жёстким требованием,
предпочтением с fallback или всегда разделять закупки. `MFG-0001` подтверждает
техническую доступность turnkey kitting, но не выбирает поставщика.

[`IMP-0046`](IMP-0046-es8311-analog-routing-topology.md) принято вариантом A
как `DEC-0054`: active high-Z ES8311 capture, differential speaker selector,
отдельный TX selector и reset-safe GPIO6 `AUDIO_ARM`. Passive capture остаётся
только HIL-gated cost-down option; analog values и HIL не закрыты решением.
