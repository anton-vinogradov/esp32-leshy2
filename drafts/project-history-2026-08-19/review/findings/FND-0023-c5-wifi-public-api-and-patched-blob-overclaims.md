# FND-0023 — C5 Wi-Fi public API не даёт simultaneous dual-band и arbitrary management TX

- Статус: **Открыто; overclaim снят в draft-требованиях**
- Серьёзность: capability/security/licence/update blocker
- Затрагивает: `C-W5-01`–`C-W5-08`, `OUT-01`, `IMP-0003`, draft `REQ-W5-0001`
- Обнаружено: 2026-08-16

## Несоответствие

Legacy одновременно переоценил и недооценил ESP32-C5:

- `WIFI_BAND_MODE_AUTO` выбирает подходящую полосу, но не делает 1T1R C5 одновременно работающим в 2.4 и 5 GHz;
- promiscuous callback действительно отдаёт management, control и data packets, поэтому passive packet capture нельзя исключать заранее;
- публичный `esp_wifi_80211_tx()` передаёт только beacon, probe request, probe response, action и non-QoS data frames. Это не arbitrary management injection: deauth/disassociation/authentication/association frames этим контрактом не обещаны; encrypted и QoS frames не поддержаны;
- наличие callback не доказывает lossless monitor, radiotap fidelity, EAPOL/PMKID completeness или пригодность PCAP без on-target HIL;
- сторонний C5 deauth proof использует patched `libnet80211.a`, привязанный к точной ESP-IDF version. Лицензия открытой wrapper-части не устанавливает происхождение и права распространения patched vendor binary.

## Обязательное разделение

1. Public-IDF baseline содержит scan/STA/SoftAP, promiscuous RX и документированные raw-TX frame classes.
2. EAPOL/PMKID остаются conditional experiment `IMP-0003`, а не обещанием до packet fixture/HIL.
3. Deauth/disassoc/arbitrary injection не входят в baseline. Возможный private-patch backend требует отдельного решения, exact IDF pin, cryptographic hash/signature, provenance/redistribution review, SBOM, rollback, owner-controlled update lifecycle и regression HIL.
4. Ни один backend не получает маркетинговый ярлык «full monitor+inject» без измеримого packet-class/loss/timestamp contract.

## Критерий закрытия

Public и patched backend разнесены в architecture/build/UI; каждая packet class проверена fixture PCAP; unsupported явно показан; patched binary при наличии имеет доказанные source/provenance/rights/version/update/rollback свойства и никогда не является обязательным условием сборки открытого базового продукта.

## Первичные источники

- [ESP32-C5 Wi-Fi driver guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c5/api-guides/wifi.html)
- [`esp_wifi_80211_tx()` API](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c5/api-reference/network/esp_wifi.html)
- [Third-party ESP32-C5 patched-library proof](https://github.com/maxbrito500/esp32-c5-deauth)

