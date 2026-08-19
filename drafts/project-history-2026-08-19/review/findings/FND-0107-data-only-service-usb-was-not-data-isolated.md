# FND-0107 — data-only service USB was not data-isolated

Статус: **исправлено в `DEC-0099`; проведено ревью**.

## Несоответствие

Старый service contract запрещал C5/RP USB VBUS питать плату, но оставлял
D+/D− напрямую соединёнными с выключенными MCU. Поэтому подключённый host мог
вводить ток через pad protection, частично поднимать вычислительный домен,
создавать ложный attach или нарушать требование «неиспользуемые интерфейсы
электрически тихие». Одного VBUS no-connect для data-only порта недостаточно.

## Исправление

Каждый из двух service USB получил отдельный board-powered `FSUSB42MUX`:
`OE=0`, `SEL=0`, используется только HSD1. При живом `3V3_MAIN` путь прозрачен
для USB Full-Speed; при выключенной плате documented power-off I/O protection
делает D+/D− high-Z. Connector-side `TPD2EUSB30ADRTR`, exact MCU-side
`22 Ω` C5 / `27 Ω` RP и отдельная локальная развязка остаются физическими
instances. VBUS соединён только с `1 MΩ` bleeder и high-impedance test pad.

## Остаток

USB eye/edge, attach/detach, board-off leakage, ESD и три одновременно
подключённых host остаются HIL. Ни один service cable не является источником
питания продукта.

