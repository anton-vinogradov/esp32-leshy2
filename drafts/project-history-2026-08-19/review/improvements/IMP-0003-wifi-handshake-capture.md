# IMP-0003 — переоткрыть EAPOL/PMKID capture

- Статус: **⚠️ Предложение к технической проверке**
- Связано: `OUT-01`, `C-W24-02`, `C-W5-02`
- Зона: `LAB-P`
- Обнаружено: 2026-08-15

## Почему legacy ceiling больше не доказан

Актуальная документация ESP32-C5 говорит, что promiscuous callback получает management, control и data frames. Официальный raw-TX API уже: он передаёт beacon, probe request, probe response, action и non-QoS data frames; arbitrary management, encrypted и QoS TX не обещаны.

Это не доказывает Pineapple-class full monitor/inject, но снимает основание автоматически исключать пассивный EAPOL capture и связанный PMKID workflow.

## Предлагаемая проверка

- на собственном тестовом AP доказать получение и сохранение EAPOL frames на 2.4 и 5 ГГц;
- отдельно проверить доступность RSN/PMKID material через штатные association/promiscuous APIs;
- записать PCAP и проверить его внешним анализатором;
- измерить packet loss при channel hop и записи на SD;
- не обещать decryption/cracking на устройстве.

## Гейты

Только собственная сеть или письменное разрешение; весь UI находится в «Лаборатории»; capture-файлы требуют privacy/storage policy.

## Источники

- [ESP32-C5 Wi-Fi driver](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-guides/wifi.html)
- [ESP32-C5 raw packet send](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-guides/wifi-driver/wifi-vendor-features.html)

До on-target proof статус — кандидат, не требование.
