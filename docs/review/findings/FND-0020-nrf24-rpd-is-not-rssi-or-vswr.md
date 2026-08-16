# FND-0020 — nRF24 RPD не доказывает RSSI-пеленг или VSWR

- Статус: **Открыто до решения по `IMP-0016`**
- Серьёзность: measurement capability overclaim
- Затрагивает: `C-N24-02`, `C-N24-03`, `C-N24-10`, waterfall/occupancy/hunt/test UI и HIL
- Обнаружено: 2026-08-16

## Несоответствие

Legacy обещает `RSSI`-hunt на трёх антеннах и помощь VSWR. nRF24L01+ предоставляет только однобитный `RPD`:

- `1` означает сигнал выше примерно −64 dBm, `0` — ниже порога;
- корректный snapshot требует RX и ожидания `Tstby2a + Tdelay_AGC = 130 + 40 µs`;
- threshold меняется примерно на ±5 dB по температурному диапазону ещё до допуска внешнего PA/LNA module и антенны;
- канал задаётся с шагом 1 MHz, но RPD не сообщает ни dBm, ни modulation/protocol, ни направление прихода.

Повторные samples позволяют вычислить только долю срабатываний порога за известный dwell. Три одинаковых и откалиброванных тракта могут сравнивать такую долю по трём antenna sectors, но это не RSSI и не bearing/azimuth.

Встроенный `CONT_WAVE` создаёт unmodulated carrier для проверки передатчика внешним spectrum/power instrument. Без directional coupler и forward/reflected detector Leshy2 не измеряет return loss или VSWR и может называться лишь bounded external-instrument test source.

Отдельная ошибка legacy UI — «128 channels»: documented `RF_CH` range составляет 0–125. Даже этот silicon tuning range не разрешает передачу на всех частотах; TX channel/power задаются exact module и региональным профилем.

## Реалистичные варианты

- честный calibrated `RPD hit-rate` comparison без dBm/angle claim — `IMP-0016/A`;
- отдельные power detectors/couplers и calibrated antenna geometry — `IMP-0016/B`, новая RF/BOM работа;
- внешний измерительный прибор остаётся обязательным для VSWR при любом варианте без встроенного reflectometer.

## Критерий закрытия

Requirement/UI/exports обязаны назвать точную величину, dwell, sample count, channel, age, radio/antenna ID, calibration и saturation/unknown state. Любой dBm, angle, direction или VSWR требует traceable fixture/calibration и соответствующего hardware; иначе поле отсутствует, а не оценивается декоративно.

## Первичные источники

- [Nordic nRF24L01+ Product Specification: RF channel, RPD and constant-carrier test](https://docs-be.nordicsemi.com/bundle/nRF24L01P_PS_v1.0/raw/resource/enus/nRF24L01P_PS_v1.0.pdf)

