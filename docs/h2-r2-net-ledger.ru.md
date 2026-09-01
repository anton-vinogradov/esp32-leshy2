# Сверка native nets H2-R2

[English](h2-r2-net-ledger.md) · [На главную](../README.ru.md) · [Роадмап](roadmap.ru.md)

**Net-checkpoint `H2-R2.1.3` пройден 30 августа 2026 года.** Каждый логический
контакт каждого устанавливаемого экземпляра R2 теперь имеет одно проверенное
физическое состояние: один native net либо явный board no-connect. Checkpoint
сверяет входные данные для native-схем и не разрешает placement, routing,
печать или заказ.

## Результат

| Элемент | Проверенный результат |
|---|---:|
| Контакты текущих устанавливаемых экземпляров | 4 239 |
| Контакты, назначенные native nets | 4 002 |
| Явные board no-connects | 237 |
| Неразрешённые или скрытые внешние контакты | 0 |
| Канонические native nets | 816 |
| Псевдонимы nets, объединённые в общем физическом узле | 46 |
| Ошибки сверки | 0 |

Текущие источники H0/H1 владеют GPIO-картами обоих RP, картой S3, стыком C5
SDIO/service mux, всеми 80 контактами M1 на обеих платах, прямым 50-контактным ZIF дисплея и
powered-off-границей Pack/Safety. Обе выведенные из корпуса stacked-flash-шины
явно оставлены board no-connect. Функциональные имена, сходящиеся на одном
физическом выводе, свёрнуты в один медный net: например, `AON_EFUSE_EN` и
`AON_RAW_3V3` — один узел, а не две дорожки.

Для переноса неизменившихся цепей обвязки использованы 3 162 подсказки
same-endpoint route из сохранённого контракта G2F R1 и ещё 4 подсказки
identical-device/same-pin из сохранённых KiCad-файлов R1. Остальные 143
историческая строка сохраняют только явные NC, reserved/free либо назначение
непродуктового controller contact. Все эти источники явно неавторитетны: они
допускаются только после совпадения текущего instance, точного device и contact
и не могут задавать R2 ownership, GPIO S3/двух RP, M1, C5 SDIO, дисплей или
topology Pack/Safety. Новым входом схем R2 служит сгенерированный проверенный
ledger.

## Машинное evidence

- [Контракт сверки nets](../hardware/ecad/h2-r2-net-ledger-contract.json)
- [Сгенерированный ledger 4 239 endpoints](../hardware/ecad/generated/H2-R2-native-net-ledger.json)
- [Генератор](../hardware/ecad/h2_r2_net_ledger.py)
- [Машинные тесты](../hardware/architecture/tests/test_h2_r2_net_ledger.py)

Два [native-проекта KiCad](h2-r2-native-kicad.ru.md) теперь материализуют этот
ledger и проходят ERC без замечаний. Сверка sheets и HW↔FW также прошла в
[H2-R2.1.5](h2-acceptance.ru.md). Теперь H3 фиксирует эти входы; placement,
routing, печать и заказ остаются заблокированы.
