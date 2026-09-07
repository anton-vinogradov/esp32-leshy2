# PAM8302AAYCR — exposed-pad clarification / уточнение центральной площадки

Status (2026-09-07): submitted through the official
[Diodes Technical Support form](https://www.diodes.com/about/contact-us/technical-support)
(HubSpot). On-page receipt was verified at 14:29 UTC: “Your request has been
sent to our internal team for your region.” No ticket number was displayed.
Awaiting a technical answer; receipt alone does not resolve the pad connection.
No order, component substitution or assembly release is authorized.

Статус (2026-09-07): отправлен через официальную форму технической поддержки
Diodes (HubSpot). В 14:29 UTC проверено подтверждение на странице: запрос
передан внутренней региональной команде. Номер обращения не показан.
Ожидается технический ответ; приём запроса не подтверждает подключение площадки.
Заказ, замена компонента и выпуск сборки не разрешаются.

## Submitted text / Отправленный текст

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

Anton Vinogradov

Phone is a placeholder (a reserved German fictional number); please reply by
email only. The country selection refers to that placeholder; no physical
address is provided.

## Submission notes / Примечания к отправке

The reply email was explicitly approved by the user and is not published here.
At the user's request, the form used a reserved fictional phone number, clearly
disclosed as a placeholder in the submitted text; Germany referred to that
placeholder, not a declared physical address. State/Region was “Not provided
(email contact only)”. The project was described as independent/hobby, with
estimated usage of one unit per year; no commercial volume was promised.

Адрес для ответа явно согласован пользователем и здесь не публикуется.
По просьбе пользователя указан зарезервированный вымышленный номер, прямо
обозначенный в тексте как заглушка; Германия относится к этой заглушке,
а не к заявленному физическому адресу. Регион не указан: «Not provided
(email contact only)». Проект обозначен как независимый хобби-проект,
ожидаемый объём — один экземпляр в год; коммерческие объёмы не обещаны.

## Русский смысл запроса

Уточнить для **точного PAM8302AAYCR**, с чем внутри соединена центральная
площадка, к какой сети её нужно или разрешено подключать на плате, обязательны
ли её пайка и тепловые переходные отверстия. До ответа не объявлять площадку
землёй, NC или исключительно механической/тепловой.

## Sources / Источники

- [Diodes PAM8302A datasheet](https://www.diodes.com/datasheet/download/PAM8302A.pdf): DS41333 Rev. 6-2, package and land-pattern drawings on pp. 11–12.
- [Diodes evaluation-board guide](https://www.diodes.com/assets/Evaluation-Boards/PAM8302A-User-Guide.pdf): schematic, photograph and layout do not establish the AYCR central-pad net.
- [Bundesnetzagentur reserved fictional numbers](https://www.bundesnetzagentur.de/DE/Fachthemen/Telekommunikation/Nummerierung/_DL/mittlg148_2021.pdf?__blob=publicationFile&v=1): source for the non-subscriber phone placeholder, not a claim that Diodes endorses placeholder contact data.
- Current device: `diodes_pam8302a_aycr`; RF-board `U86` / `speaker_amp`.
- Review date: 2026-09-07. The existing unnamed native pad remains electrically unassigned; this inquiry is not an instruction to connect it.
