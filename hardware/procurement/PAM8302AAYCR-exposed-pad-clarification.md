# PAM8302AAYCR — exposed-pad clarification / уточнение центральной площадки

Status: draft, not sent. No order, component substitution or assembly release.

Статус: черновик, не отправлен. Заказ, замена компонента и выпуск сборки не разрешаются.

## English draft

Subject: PAM8302AAYCR U-DFN3030-8 Type E — exposed-pad electrical connection

Hello,

We are laying out a PCB using the exact PAM8302AAYCR in U-DFN3030-8 Type E.
DS41333 Rev. 6-2 shows the central exposed pad and a 2.35 × 1.60 mm
recommended PCB land, but we could not find its electrical connection in
the pin descriptions. The evaluation-board guide appears to use a leaded
package, so it does not resolve this package-specific point.

Could you please confirm for PAM8302AAYCR:

1. Is the central exposed pad internally connected to GND or another circuit,
   or is it electrically isolated? Which PCB connection is required or allowed:
   GND, unconnected copper, or another net?
2. Must that pad be soldered, and are thermal vias required for this package?

A reference to the applicable package/application drawing would be helpful.
Thank you.

## Русский смысл запроса

Уточнить для **точного PAM8302AAYCR**, с чем внутри соединена центральная
площадка, к какой сети её нужно или разрешено подключать на плате, обязательны
ли её пайка и тепловые переходные отверстия. До ответа не объявлять площадку
землёй, NC или исключительно механической/тепловой.

## Sources / Источники

- [Diodes PAM8302A datasheet](https://www.diodes.com/datasheet/download/PAM8302A.pdf): DS41333 Rev. 6-2, package and land-pattern drawings on pp. 11–12.
- [Diodes evaluation-board guide](https://www.diodes.com/assets/Evaluation-Boards/PAM8302A-User-Guide.pdf): schematic, photograph and layout do not establish the AYCR central-pad net.
- Current device: `diodes_pam8302a_aycr`; RF-board `U86` / `speaker_amp`.
- Review date: 2026-09-07. The existing unnamed native pad remains electrically unassigned; this draft is not an instruction to connect it.
