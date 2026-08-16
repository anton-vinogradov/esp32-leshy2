# DEC-0019 — калиброванный трёхантенный RPD-hunt

- Статус: **Принято владельцем**
- Источник: `IMP-0016`, вариант A
- Дата: 2026-08-16

## Решение

Три принятых nRF24 сохраняются как три одновременных приёмных тракта ESP32-C5. Базовая функция поиска сравнивает не RSSI, а калиброванную долю срабатываний бинарного RPD по трём антеннам/секторам.

Для каждого тракта запись и UI обязаны показывать:

- `hits / samples`, dwell, channel, data rate и общий временной интервал;
- radio/antenna ID, возраст результата, calibration ID и состояние calibration;
- `stronger`, `comparable` либо `unknown` только после fixture normalization трёх трактов на одной частоте и в сопоставимом временном окне.

Нельзя выводить из RPD dBm, RSSI, угол, bearing/azimuth, точное направление или VSWR. Occupancy/hunt является статистикой выбранного окна и может пропустить сигнал короче scan cycle.

## Границы

- Новое RF-измерительное железо в baseline не добавляется.
- Вариант B — coupler/power detector или отдельный measurement frontend — остаётся возможным будущим расширением и требует отдельного решения владельца, новой RF-архитектуры, calibration и HIL.
- Constant-carrier/sweep остаётся только bounded source для внешнего прибора в Controlled Zone `BOTH`, а не встроенным измерителем VSWR.
- Три radio не заменяются одним radio+RF switch: такая замена теряет одновременность и не является zero-loss.

## Последствия для артефактов

- `REQ-N24-0001` получает статус **«Проведено ревью»**.
- `FND-0020` закрывается на уровне требований: ложные измерительные claims исключены контрактом.
- `FND-0019` остаётся открытой implementation finding до выбора exact modules, доказательства C5 transport/resource budget, power/RF/antenna path, STOP/TX state и HIL.
- `FND-0021` остаётся открытой implementation finding; `IMP-0017` рассматривается отдельно на BLE-owner review.

## Первичный источник

- [Nordic nRF24L01+ Product Specification](https://docs-be.nordicsemi.com/bundle/nRF24L01P_PS_v1.0/raw/resource/enus/nRF24L01P_PS_v1.0.pdf)
