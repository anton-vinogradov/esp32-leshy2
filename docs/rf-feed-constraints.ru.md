# Ограничения антенных трактов · historical R1

`H3.5.1` проведён ревью: `75` машинных checks охватывают все десять внешних антенных портов, незакрытых аналитических findings нет. Исторический маркер прогресса R1 — `H3.6.1`.

## Контракт каждого тракта

| Порт | Электрическая граница | Pre-layout acceptance target |
|---|---|---|
| S3-2G4 | 50 Ом module -> 30-мм UMCC -> U.FL -> dual-band coupler -> RP-SMA | полный feed <=1,5 дБ, return loss >=10 дБ |
| C5-2G4/5 | тот же тракт до 5,885 ГГц | <=1,5 дБ на 2,4 ГГц, <=2,0 дБ на 5 ГГц, return loss >=10 дБ |
| N24-0/1/2 | три независимых 50-омных module -> UMCC/U.FL -> 10-dB coupler -> SMA | каждый <=1,5 дБ и return loss >=10 дБ до 2525 МГц |
| CC-SUB | differential match CC1101 -> balun -> выбранная с двух концов branch -> SMA | настроенный полный тракт <=3 дБ и return loss >=10 дБ на 315/433/868/915 МГц |
| VOICE-VHF | native 50-омный ANT 12 SA818S-V -> короткая защищённая трасса -> отдельный SMA | <=0,75 дБ и return loss >=10 дБ на 134-174 МГц |
| VOICE-UHF | native 50-омный ANT 12 SA818S-U -> короткая защищённая трасса -> отдельный SMA | <=0,75 дБ и return loss >=10 дБ на 400-480 МГц; alternate CE ограничен 470 МГц |
| RX-FM/SW | 50-омный SMA corridor только до первого корпуса 56 нГн, затем receiver-specific match | деградация sensitivity полного fixture <=1,5 дБ; FM и SW проверяются отдельно |
| RX-AM/LW | **не 50-омный тракт**; SMA служит только серийной механической границей короткой петли/pod | внешняя ёмкость <=`19.500 пФ` вместе с connector, PCB, ESD и pod |

AM/LW bound использует corner pod 300 мкГн +5% и верхнюю границу 1710 кГц: полная резонансная ёмкость равна `27.500 пФ`. Вход Si4732 занимает 8 пФ, зарегистрированный ESD — до 0,25 пФ; на SMA, PCB и parasitics pod остаётся `19.250 пФ`. Поэтому произвольный длинный coax на этом порту запрещён.

Известная потеря компонента не выдаётся за потерю полного feed. Например, на CC 868/915 бумажный максимум balun и двух switches уже равен `1.840 дБ` до matching passives, launches и trace; все четыре branches остаются conducted/VNA gates.

Машинное evidence: [`H3-VRF51-rf-feed-constraints.json`](../hardware/verification/generated/H3-VRF51-rf-feed-constraints.json).
