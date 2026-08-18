# PWR-0022 — exact MAX17320 2S support profile

- Статус: **Проведено ревью paper electrical scope; physical/HIL open**
- Дата: 2026-08-19
- Решение: [`DEC-0100`](../decisions/DEC-0100-exact-max17320-2s-support-closure.md)
- Finding: [`FND-0109`](../findings/FND-0109-machine-map-was-not-a-complete-physical-bom.md)

## Проверенные первичные источники

- [MAX17320 Rev.12 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/max17320.pdf), включая Figure 24 для 2S;
- [MSPM0C1104 SLASF90D](https://www.ti.com/lit/ds/symlink/mspm0c1104.pdf), exact VSSOP-20 contacts и типы I/O;
- [Panasonic ERJ-P08F49R9V](https://industrial.panasonic.com/ww/products/pt/small-and-high-power-chip-resistors/models/ERJP08F49R9V), 49,9 Ω, 1%, 1206, 0,66 Вт;
- [Murata GRM188R71E474KA12](https://www.murata.com/products/productdetail?partno=GRM188R71E474KA12%23), 0,47 мкФ, 25 В, X7R, 0603.

## Exact 2S circuit

| Узел | Точная реализация | Проверенное свойство |
|---|---|---|
| `IN` | `ERJ-P08F10R0V` от fused stack positive; `C1005X7R1H104K050BB` на pack GND | 10 Ω и 0,1 мкФ как в application circuit |
| `CP` | `GRM188R71E474KA12D` между CP и IN | 0,47 мкФ, 25 В |
| `AOLDO`, `REG3`, `REG2` | по отдельному `GRM188R71E474KA12D` на pack GND | каждый выход имеет собственные 0,47 мкФ |
| 2S sense | `ERJ-P08F49R9V` на CELL1 и BATTS; CELL1/CELL2/CELL3 замкнуты в один midpoint-sense net | воспроизводит 2S Figure 24, а не 3S/4S ladder |
| sense filters | `C1005X7R1H104K050BB` от CELL1 к GND и от BATTS к CELL3 | две независимые 0,1-мкФ позиции сохранены |
| `PCKP` | `RC0402FR-071KL` к protected pack positive | точная 1-кОм серия |
| CHG/DIS | `C1005X7R1H104K050BB` gate-to-source на каждом ключе | оба внешних gate capacitors присутствуют |
| shunt | `WSL25125L000FEA`; SLOT0_NEG force к END1, END2 force к power ground, CSP/CSN Kelvin | sense не подменяет отсутствующий силовой путь |
| unused | ZVC NC; TH3/TH4 на pack GND | нет плавающих thermistor inputs |

Для CELL1 worst-screen расчёт при 4,3 В учитывает типичные 9 Ω внутреннего
пути MAX17320: `I ≈ 4,3/(49,9+9)=73 мА`, `P_R ≈ I²×49,9=0,267 Вт`.
Поэтому прежний маломощный 0402 не годился; exact 0,66-Вт 1206 имеет бумажный
запас. Температурный derating, copper spreading и непрерывный worst-case
баланс остаются HIL/thermal gates.

## Status, IRQ and controller support

`PFAIL` у MAX17320 — push-pull, поэтому прямой вход MSPM0 на admission rail
удалён. Первая половина отдельного `2N7002DW-7-F` преобразует его в безопасный
active-low `PACK_PFAIL_N`, подтянутый 10 кΩ к `PACK_ADMISSION_VDD`. Вторая
половина превращает active-high request PA23 в passive-drain `SYS_INT_N`; 10
кΩ gate pulldown сохраняет released IRQ при reset. PA23 не объявляется
несуществующим open-drain I/O: по exact datasheet 5-V-tolerant ODIO имеются
только на PA0/PA1.

Private SCL/SDA и ALRT имеют отдельные 10-кΩ pull-up. MSPM0 VDD получает
`GRM188R60J106ME47D` 10 мкФ и `C1005X7R1H104K050BB` 100 нФ. PA1/NRST получает
47 кΩ, 10 нФ и test point. Все позиции являются отдельными machine instances
и отдельными блоками вертикальной принципиальной диаграммы.

## Exit gates

Paper electrical scope имеет **«Проведено ревью»**. До physical freeze нужны:

1. MAX17320/MAX17320G20+T exact-lot programming and wrong/blank-NVM HIL;
2. startup/source handover, PFAIL levels and ALRT override measurement;
3. shunt Kelvin/force layout review и current accuracy across load/temperature;
4. balance-current/thermal HIL at cell-voltage corners;
5. CHG/DIS, I²C, open/short thermistor and reset/brownout fault injection.

