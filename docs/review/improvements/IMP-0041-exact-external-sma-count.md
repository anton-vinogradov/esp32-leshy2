# IMP-0041 — exact external-SMA count and Si4732 split

- Статус: **Ожидает решения владельца**
- Дата: 2026-08-17
- Основание: [`DEC-0048`](../decisions/DEC-0048-external-sma-antenna-bank.md)
- Evidence: [`ANT-0001`](../architecture/ANT-0001-external-sma-path-inventory.md)
- Finding: [`FND-0055`](../findings/FND-0055-si4732-two-antenna-input-domains.md)

## Контекст решения

Владелец подтвердил, что все бортовые antenna endpoints внешние и механически
SMA. Старый clamshell уже имел девять мест. После удаления onboard LoRa одно
место освободилось, но exact Si4732 оказался не одним generic antenna input:
у него отдельные `FMI` для FM/SW и `AMI` для AM/LW.

Фиксированные endpoints дают шесть SMA: S3, C5, три nRF и SA518. CC1101
добавляет один candidate SMA за exact switched frontend. Si4732 добавляет
один либо два connector в зависимости от решения ниже.

## Вариант A — девять SMA, отдельные `RX-FM/SW` и `RX-AM/LW` (рекомендуется)

Портовый банк:

1. `S3-2G4`;
2. `C5-2G4/5`;
3. `N24-0`;
4. `N24-1`;
5. `N24-2`;
6. `CC-SUB`;
7. `VOICE-V/U`;
8. `RX-FM/SW`;
9. `RX-AM/LW`.

Удалённый `LoRa` slot старого корпуса переименовывается в `RX-AM/LW`, поэтому
внешний envelope остаётся девятипортовым. Si4732 pins не соединяются через
дополнительный RF switch, обе antennas могут быть установлены, а mode меняет
только внутренний receiver mux. `RX-AM/LW` остаётся SMA по механическому
решению владельца, но имеет яркую маркировку и свой direct plug-in loop/pod
profile: это не generic 50-ohm TX/coax port.

Цена — один SMA/pigtail/ESD/interface по сравнению с восьмипортовым вариантом.
Зато это не новая механическая нагрузка относительно макета и не добавляет
switch insertion loss, shared-port ambiguity или обязательную смену антенны
при переходе FM/SW↔AM/LW.

## Вариант B — восемь SMA, один mode-switched `RX` port

Один SMA по выбранному режиму подключается к `FMI` либо `AMI`; пользователь
меняет whip и loop/pod, а firmware проверяет declared antenna profile.

Экономится один внешний connector и отверстие. Взамен появляются RF switch,
две matching/protection ветви, additional parasitics на особенно чувствительном
AMI, риск неправильной antenna и обязательная user operation при смене mode.
До bench proof этот вариант не является zero-loss и может оказаться дороже по
BOM/NRE, чем отдельный SMA.

## Вариант C — dedicated CC band ports сверх девяти

Отдельные CC SMA для 315/433/868/915 упрощают часть band-specific antenna
truth, но дают 12 connectors total, увеличивают корпус/ошибки пользователя и
не нужны для одного последовательно работающего CC1101, если qualified
50-ohm switched frontend проходит proof. В baseline не рекомендуется.

## Рекомендация

Принять **A**. Он сохраняет всю функцию, не увеличивает старый mechanical
envelope, честно отражает реальные Si4732 pins и использует удаление onboard
LoRa для исправления старого скрытого ограничения. Exact connector gender,
mounting и antenna pod MPN останутся следующей отдельной квалификацией.

## Вопрос владельцу

Принимаем вариант **A: девять внешних SMA с отдельными `RX-FM/SW` и
`RX-AM/LW`, а бывший LoRa slot отдаём второму Si4732 input domain**?

