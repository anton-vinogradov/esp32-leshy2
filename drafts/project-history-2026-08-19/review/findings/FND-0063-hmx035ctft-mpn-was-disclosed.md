# FND-0063 — HMX035CTFT-001 MPN был раскрыт в primary schematic

- Статус: **Закрыто исправлением source/register/machine map**
- Серьёзность: sourcing/provenance overstatement
- Обнаружено: 2026-08-17
- Исправление: [`DSP-0005`](../architecture/DSP-0005-hmx035ctft-electrical-fit.md) /
  [`REV-0005A`](../reviews/REV-0005A-hmx-display-electrical-fit.md)

## Находка

`DSP-0003`, `DSP-0004` и downstream status ошибочно утверждали, что primary
QDtech/Elecrow reference не публикует exact raw display/FPC MPN. В официальной
схеме `ES3C35P` 40-contact display/touch assembly явно обозначена
`HMX035CTFT-001`.

## Исправление и граница доказательства

- exact assembly marking и все 40 contacts внесены в `devices.json`;
- `G2F-3I` теперь заканчивает display/touch signals на реальных contacts этого
  assembly;
- register исправлен: MPN **известен**, а не `TBD`;
- production acceptance не выдумана: отдельная order page, manufacturer
  drawing, FPC mechanics, MOQ, lifecycle и second source всё ещё не найдены.

Следовательно, `HMX035CTFT-001` — exact disclosed **paper candidate** и primary
HIL specimen target, но пока не production-qualified BOM line.

## Primary source

- [QDtech ES3C35P official schematic](https://www.lcdwiki.com/res/ES3C35P/ESP32-S3%E5%8E%9F%E7%90%86%E5%9B%BE.pdf)
