# ⚠️ IMP-0036 — task-based display performance instead of inherited full frames

- Статус: **Требуется решение владельца**
- Дата: 2026-08-17
- Finding: [`FND-0051`](../findings/FND-0051-legacy-display-interface-and-throughput.md)
- Evidence: [`DSP-0001`](../architecture/DSP-0001-display-storage-real-device-evidence.md)

## Контекст

Число `10 full-frame-equivalents/s` пришло из прежней architecture synthesis,
а не из принятого user scenario. Оно полезно как stress load, но не доказывает
полезность: waterfall обычно добавляет узкие строки, critical status меняет
небольшую область, а меню/текст используют dirty rectangles. В то же время
этот synthetic ceiling исключает дешёвые и хорошо поддержанные ST7796S modules
по их собственному datasheet и заставляет тратить GPIO/деньги на более широкую
шину либо smart display.

## A — task/dirty-rectangle contract, рекомендуется

- сохранить `320×480-class` как сравнимый reference, но не фиксировать сейчас
  3.5 против 4.0 inch и exact part;
- заменить полный-frame rate на scenario tests: critical status visible within
  100 ms, bounded navigation latency, continuous waterfall/recording без
  пропуска radio/audio deadlines, preemptible chunks и явный frame/drop counter;
- полный redraw остаётся измеряемым HIL result, а не причиной перерисовывать
  неизменившийся экран десять раз в секунду;
- сохранить текущий low-pin SPI/I2C envelope; Waveshare/Elecrow используются
  для раннего прототипа, outdoor Riverdi и другие exact production candidates
  сравниваются позже по sunlight/temperature/power/cost;
- отдельный SDMMC path не удалять до equal-performance proof.

Последствия: pin budget не растёт, старый 4-inch макет можно быстро проверить,
а стоимость не увеличивается ради невыведенного user requirement. Риск — UI
нужно тестировать сценариями и dirty renderer нельзя заменить субъективным
«кажется плавно».

## B — сохранить hard 10 full frames/s

Потребовать display path с честным measured payload ≥4.5 MB/s. ST7796S SPI
исключается. G2F возвращается к QSPI/8080/RGB/EVE candidates и заново считает
контакты, controller instances, shared U214 path, питание, механику и стоимость.

Последствия: проще синтетический benchmark и выше запас для animations, но
текущие zero-free-GPIO S3 maps почти наверняка меняются. Доступная Waveshare
AXS15231B QSPI board доказывает технологию, но не standalone panel connector
для нашей платы; EVE/RGB alternatives добавляют цену, толщину или много pins.

## Рекомендация

Принять `A`: это не снижение функции, а замена непроисходящего из сценариев
synthetic load на проверяемое пользовательское поведение. Если scenario HIL не
проходит, интерфейс автоматически переоткрывается до выбора target display.
