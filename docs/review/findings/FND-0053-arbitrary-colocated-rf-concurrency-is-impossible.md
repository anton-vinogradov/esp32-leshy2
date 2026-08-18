# FND-0053 — arbitrary co-located RF concurrency is impossible

- Статус: **Cross-group закрыто `DEC-0045`; nRF intragroup выделено в `FND-0054`**
- Дата: 2026-08-17
- Вход: [`NIF-0001`](../architecture/NIF-0001-digital-noninterference-layout.md)
- Архитектурный анализ: [`RFQ-0002`](../architecture/RFQ-0002-g2f-3i-rf-concurrency-boundary.md)
- Предложение решения: [`IMP-0038`](../improvements/IMP-0038-visible-qualified-rf-arbiter.md)
- Review: [`REV-0004M`](../reviews/REV-0004M-g2f-3i-rf-concurrency-fact-review.md)

## Находка

`G2F-3I` устраняет ожидание соседнего radio bus, IRQ, controller и постоянного
DMA channel. Это необходимо, но не создаёт электромагнитную развязку.
Передатчик внутри того же handheld enclosure способен перегрузить или
десенситизировать другой приёмник до того, как firmware увидит пакет.

Наиболее жёсткие пересечения следуют из реальных диапазонов:

| Cluster | Реальные участники | Конфликт |
|---|---|---|
| 2.4 GHz | S3 Wi-Fi/BLE до +20 dBm, C5 2.4/802.15.4 до примерно +20 dBm, 3×E01-ML01S 0 dBm/−93 dBm | пять близких antenna/front-end paths; local TX закрывает weak-signal RX на той же или соседней частоте |
| 5 GHz/native C5 | один C5 1T1R dual-band RF domain | 2.4/5 GHz Wi-Fi и 802.15.4 не являются отдельными одновременными radios; native scheduler time-shares RF |
| 868/915 MHz | U214 +22 dBm, CC1101 779–928 MHz с чувствительностью порядка −112 dBm | диапазоны непосредственно перекрываются; same-channel filtering не помогает |
| 400–464 MHz | SA518 до 30 dBm и CC1101 387–464 MHz | до 1 W рядом с weak-signal receiver; произвольный simultaneous voice TX + CC RX не квалифицируем внутри корпуса |
| receive-only | Si473x broadcast RX и U214 GNSS | даже вне основной TX-полосы остаются harmonic, broadband-noise, common-rail и front-end-overload gates |

## Оптимистичный screening порядка величин

Для верхней оценки пользы одного только разнесения взяты 150 mm — полный
порядок legacy enclosure, а не реальная antenna-to-antenna дистанция. Формула
free-space loss является лишь screening; в ближнем поле, рядом с ground,
battery, display, shield seams и рукой она не является layout proof.

| Пара | TX / wanted RX | FSPL при 150 mm | Порядок недостающей развязки до sensitivity floor |
|---|---:|---:|---:|
| E01→E01, 2.44 GHz | 0 / −93 dBm | 23.7 dB | ≈69 dB |
| S3/C5→E01, 2.44 GHz | +20 / −93 dBm | 23.7 dB | ≈89 dB |
| U214→CC, 0.9 GHz | +22 / −112 dBm | 15.1 dB | ≈119 dB |
| SA518→CC, 0.45 GHz | +30 / −116 dBm | 9.0 dB | ≈137 dB |

Это не требования к конкретному shield can: таблица показывает, почему
пространственное разнесение внутри устройства не может доказать сохранение
предельной чувствительности. Band-pass/SAW-фильтр помогает против далёкой
полосы, но не отличает local interferer от wanted signal на той же частоте.

## Что остаётся достижимым

- три nRF обязаны одновременно выполнять любые независимые PTX/PRX роли без
  digital serialization или скрытых gaps; exact mixed-RF sensitivity вынесена
  в `FND-0054/IMP-0039` и не считается доказанной этой находкой;
- исторически рассматривалась qualification отдельных separated-band pairs,
  но `DEC-0045` выбрал более строгую границу: разные top-level signal groups
  не получают parallel runtime class после HIL;
- внутренние S3 Wi-Fi/BLE и C5 Wi-Fi/802.15.4 работают честным native
  time-sharing с видимыми dwell/gaps/loss;
- overlapping TX↔RX работает через заранее проверенный arbiter contract, а не
  через скрытую деградацию или ложное обещание full concurrency;
- Controlled Zone может использовать conducted, shielded-room или remote-head
  fixture для более сильной развязки, но authorization не отменяет RF physics.

## Вывод

Произвольная одновременность всех TX/RX paths внутри handheld enclosure
получает статус **невыполнимо как универсальная гарантия**. Это не сокращает
функции radios: каждый остаётся full-function, но допустимые комбинации,
preemption, gaps, stale/loss и qualification identity должны быть частью
готового продукта.

Владелец закрыл finding решением
[`DEC-0045`](../decisions/DEC-0045-one-active-signal-group.md): base runtime
активирует только одну versioned signal group. Cross-group simultaneous RF
больше не является product requirement. `SG-N24` при этом является одной
группой из трёх одновременно активных full-function transceivers; её
внутренняя физическая граница не закрыта cross-group policy.

## Первичные источники

- [ESP32-C5 datasheet](https://documentation.espressif.com/esp32-c5_datasheet_en.pdf)
- [ESP32-C5 RF coexistence guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-guides/coexist.html)
- [ESP32-S3 datasheet](https://documentation.espressif.com/esp32-s3_datasheet_en.pdf)
- [ESP32-S3 RF coexistence guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-guides/coexist.html)
- [Ebyte E01-ML01S product data](https://www.cdebyte.com/products/E01-ML01S/4)
- [TI CC1101 datasheet](https://www.ti.com/lit/ds/symlink/cc1101.pdf)
- [M5Stack U214 documentation](https://docs.m5stack.com/en/cap/Cap_LoRa-1262)
- [NiceRF SA518 datasheet](https://www.nicerf.com/pdf/sa518-1w-uv-dual-frequency-walkie-talkie-module-v1.1.pdf)
- [Skyworks Si473x-D60 datasheet](https://www.skyworksinc.com/-/media/Skyworks/SL/documents/public/data-sheets/Si4730-31-34-35-D60.pdf)
