# Аппаратная часть Leshy2

> **Целевой сайт продукта.** Здесь описан готовый Leshy2: назначение,
> возможности, интерфейсы, принципиальное устройство и обязательные гарантии.
> Ход разработки и открытые проверки вынесены в отдельные инженерные документы.

- [English version](README.md)
- [Целевой firmware-продукт](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/README.ru.md)
- [Состояние разработки](docs/status/current-state.ru.md)
- [Инженерные решения и доказательства](docs/review/README.md)

## Образ готового продукта

Leshy2 — открытый автономный портативный инструмент для наблюдения за
радиоэфиром, диагностики, связи и разрешённых исследований беспроводных и
контактных систем. Он объединяет несколько независимых радиотрактов, экран,
локальное управление, запись данных, аудио, сервисные интерфейсы и расширения
в одном ремонтопригодном устройстве.

Это полевой прибор, а не универсальный карманный компьютер: каждая аппаратная
возможность должна давать измеримый результат, иметь понятное безопасное
состояние и быть доступной для диагностики и восстановления владельцем.

## Три уровня функциональности

1. **Основной режим** — повседневные инструменты, приём, диагностика,
   навигация, обслуживание и законная связь.
2. **Лаборатория** — пассивные, защитные и ограниченные security-инструменты.
3. **Лаборатория → Контролируемая зона** — опасные active/disruptive функции.
   Каждый вход показывает новое неснимаемое предупреждение, а каждое действие
   отдельно требует авторизованной цели, изолированной/проводной среды или обоих.

При первичной установке отдельно принимается акт о ненападении. Ни он, ни
предупреждение не вооружают функцию и не отменяют требования законодательства,
лицензирования спектра, приватности и разрешения владельца цели.

## Возможности готового устройства

### Радио и связь

- Три независимых полнофункциональных nRF24 работают одновременно в любом
  сочетании `3R`, `1T2R`, `2T1R` и `3T`, без скрытого отключения соседних
  приёмников.
- Три разнесённых nRF-антенны дают калиброванное относительное sector/RPD
  сравнение. Результат не выдаётся за абсолютные dBm, угол или VSWR.
- Wi-Fi 2,4/5 ГГц, Bluetooth LE, ESP-NOW и IEEE 802.15.4 обеспечивают обычную
  связь, наблюдение и разрешённые диагностические сценарии.
- Отдельный Sub-GHz тракт работает с пакетными системами; широковещательный
  приёмник покрывает AM/FM/SW/LW; VHF/UHF voice-тракт поддерживает аналоговую
  связь и аудиообработку.
- Точный аудиотракт умеет направлять в кодек выбранный RX-звук или локальный
  электретный микрофон, воспроизводить через выключенный в reset 4-Ом динамик
  либо через определяемые по вставке наушники 3,5 мм. Шины кодека, приёмника и
  SA518 физически отсоединены при снятом питании; PTT остаётся отдельным
  STOP-доминируемым разрешением и никогда не выводится из наличия звука.
- Два IR-приёмника позволяют одновременно надёжно декодировать бытовые команды
  и измерять несущую неизвестного сигнала; отдельный передатчик воспроизводит
  изученные профили.
- Все девять бортовых антенных трактов выведены на собственные внешние порты:
  два RP-SMA для native Wi-Fi и семь standard SMA для остальных трактов.

### Интерфейсы и расширения

- Вертикальный сенсорный IPS-дисплей 3,5 дюйма, `320×480`, подключён прямым QSPI;
  критическое состояние и первый отклик меню появляются не позднее `100 мс`.
- Съёмная microSD хранит записи эфира, аудио, профили, журналы и экспортируемые
  данные. Питание включается только на время сессии накопителя; выключенная
  карта электрически изолирована, все доступные электрические контакты защищены,
  а наличие карты читается независимо от её питания. Штатное извлечение сначала
  завершает отложенную запись; неожиданное извлечение явно сообщается и не
  выдаёт незаписанный хвост данных за целый.
- Задний 14-контактный Cap-Bus принимает съёмный M5Stack U214 LoRa/GNSS и
  совместимые модули; отдельный защищённый M5 Unit-порт поддерживает GNSS,
  квалифицированные LoRa-модули, NFC, iButton/1-Wire и другие расширения.
- Квалифицированный raw-SDR или внешний RF-analysis модуль может определить
  отдельный high-throughput интерфейс; low-rate M5 command port не выдаётся за
  тракт сырых данных.
- Редкий длинный ввод текста может выполняться с локально сопряжённого телефона,
  но телефон не подтверждает опасные действия и не заменяет управление Leshy2.
- Внешний IMU может добавлять к измерениям положение и относительное движение;
  без квалифицированного крепления эти данные не выдаются за компас или пеленг.

### Обслуживание

- Каждый программируемый вычислительный домен имеет собственные пути прошивки,
  восстановления и диагностики, не зависящие от исправности соседнего домена.
- Основной USB-C сохраняет защищённые USB2 Full-Speed линии S3 (12 Мбит/с)
  и только принимает питание:
  fallback 5 В, 9 В при 3 А и 15 В при 2 А, до 30 Вт. Режимы power bank и
  USB-PD source отсутствуют.
- PD-контроллер прямо от сырого USB VBUS входит в аппаратный SafeMode,
  автономно загружается из отдельной восстанавливаемой EEPROM и не включает
  защищённый силовой тракт и заряд до появления валидного образа. Заводские
  площадки позволяют прошить пустую микросхему; полевое обновление проверяет
  подписанный владельцем образ и сохраняет rollback-регион.
- Зарядник 2S физически настроен на эффективный профиль `750 кГц` с дросселем
  `2,2 мкГн / 7 А`. После reset заряд начинается с консервативного `1 А`;
  штатно он не превышает `2 А`, сначала ограничивает вход по фактическому
  USB-контракту 5/9/15 В и прекращается при прямой ошибке температуры батареи.
- Контролируемая батарея 2S использует две отдельно заменяемые exact
  `XTAR 18650 4000mAh` защищённого button-top типа (`28,8 Вт·ч` nominal на
  пару) в точном поляризованном держателе `Keystone 1048P`; для работы от
  батарей нужны обе. Raw flat-top ячейки не поддерживаются, а квалифицированные
  аккумуляторы по умолчанию поставляются отдельным региональным комплектом. Переполюсовка
  исключается механически; аппаратная часть наблюдает и допускает пару до её
  подключения к системе и отказывает опасному сочетанию вместо принудительной
  работы или выравнивания. Глубоко разряженная банка также отклоняется:
  zero-volt/prequalification recovery в самом устройстве отключён, а любые
  исследования восстановления требуют отдельной изолированной оснастки
  Controlled Zone. Перед допуском общий тракт с нагрузкой 10 Ом прикладывает
  примерно `0,57…0,88 А` не дольше `50 мс`. Один non-retriggerable аппаратный
  канал не даёт растянуть импульс, а второй после него запрещает повтор минимум
  на `350 мс` даже при неисправной firmware. Две параллельные pulse-rated ветви
  по 20 Ом/2 Вт сохраняют суммарные 10 Ом и безопасно делят нагрев; штатная
  программа ждёт между попытками не менее 10 секунд. Это screen ячеек/контактов,
  а не обещание полной проверки под нагрузкой.
- Четыре независимые фиксированные шины разделяют always-on безопасность,
  вычислительное питание 3,3 В, голосовой тракт 4,0 В и защищённый порт
  расширения 5,0 В. Неиспользуемые ветви радио, накопителя и аудио физически
  отключаются и разряжаются до проверенного тихого состояния. Выход каждого
  преобразователя проходит собственную аппаратную отсечку перенапряжения,
  перегрузки и короткого замыкания до любого потребителя. Защищённая шина AON
  и её физический power-good удерживают supervisor 3,07 В в reset, и только
  его задержанный аппаратный POR включает основную шину. Firmware не может
  обойти допуск источника, brownout AON, любую внутреннюю границу защиты или
  этот порядок запуска.
  Runtime доверяет только power-good защищённой стороны. Защёлкнутая ошибка
  main требует полностью снять источник и заново пройти допуск. AON-отсечка
  может выполнять собственные ограниченные аппаратные попытки восстановления,
  но software не может их ускорить, а main остаётся выключенной до устойчиво
  исправной защищённой AON.
- Защищённый порт расширения запускается с управляемой скоростью нарастания
  напряжения и сразу действующим ограничением тока. Он поддерживает `1,25 А`
  постоянно и ограниченный по времени импульс `2,0 А` только после запуска;
  затянувшаяся перегрузка или иной fault eFuse защёлкивает порт выключенным без
  автоматических повторов.
- Подписанные обновления проверяют целевое устройство и поддерживают откат;
  ключи сборки и возможность установки владельческой прошивки остаются у
  владельца. Необратимая блокировка не включается по умолчанию.

## Принципиальный дизайн решения

Три вычислительных домена разделяют UI, широкополосные беспроводные функции и
детерминированное обслуживание радио. Независимые шины не заставляют активный
радиотракт ждать дисплей, карту памяти или соседнее радио. Неиспользуемые
интерфейсы переводятся в тихое аппаратное состояние.

Диаграмма поддерживается как узкая вертикальная проекция целевой начинки.
Каждый квадрат обозначает один физический компонент и содержит его MPN или
явный `MPN TBD`, а также роль в готовом устройстве.

```mermaid
flowchart TD
  USBC["DX07S016JA1R1500<br/>основной USB-C: защищённые USB2-линии S3 и только приём питания"]
  PORTPROT["TPD4S201RUKR<br/>защита CC1/CC2 и USB2 D+/D- от short-to-VBUS/ESD"]
  PORTDPR["ERJ-2RKF22R0X #USB-DP<br/>последовательный резистор 22 Ом линии D+ USB Full-Speed S3"]
  PORTDMR["ERJ-2RKF22R0X #USB-DM<br/>последовательный резистор 22 Ом линии D- USB Full-Speed S3"]
  PORTVBIAS["C1608X7S2A104K080AB<br/>конденсатор VBIAS защиты порта: 100 нФ, 100 В"]
  PORTVPWR["C1608X7R1C105K080AC #USB-PROT<br/>конденсатор VPWR защиты порта: 1 мкФ, 16 В"]
  PORTFLTPU["RC0402FR-0710KL #USB-PROT-FLT<br/>pull-up сигнала ошибки защиты порта: 10 кОм"]
  VBUSPROT["TVS2200DRVR<br/>22-В flat-clamp защита VBUS от импульсов"]
  PDCTRL["TPS25751DREFR<br/>sink-only USB-PD политика и защищённый high-voltage тракт"]
  PDCFG["CAT24C512WI-GT3<br/>отдельная EEPROM с patch/configuration PD"]
  PVINCAP["GRM188R60J106ME47D #VIN<br/>конденсатор VIN_3V3 PD-контроллера: 10 мкФ"]
  PL3CAP["GRM188R60J106ME47D #LDO3V3<br/>конденсатор LDO 3,3 В PD-контроллера: 10 мкФ"]
  PL1CAP["GRM188R60J106ME47D #LDO1V5<br/>конденсатор LDO 1,5 В PD-контроллера: 10 мкФ"]
  PPHVC0["GRM32ER71E226KE15L #PPHV0<br/>конденсатор защищённого VBUS №0: 22 мкФ, 25 В"]
  PPHVC1["GRM32ER71E226KE15L #PPHV1<br/>конденсатор защищённого VBUS №1: 22 мкФ, 25 В"]
  PPHVC2["GRM32ER71E226KE15L #PPHV2<br/>конденсатор защищённого VBUS №2: 22 мкФ, 25 В"]
  PPHVC3["GRM32ER71E226KE15L #PPHV3<br/>конденсатор защищённого VBUS №3: 22 мкФ, 25 В"]
  PVBUSCAP["CGA5L1X7R1E475K160AC #PD-VBUS<br/>конденсатор запуска от сырого VBUS: 4,7 мкФ, 25 В"]
  PCC1CAP["GRM1555C1H221JA01D #CC1<br/>конденсатор защищённой USB-C CC1: 220 пФ, C0G"]
  PCC2CAP["GRM1555C1H221JA01D #CC2<br/>конденсатор защищённой USB-C CC2: 220 пФ, C0G"]
  PEECAP["C1005X7R1H104K050BB #PD-EEPROM<br/>bypass-конденсатор EEPROM PD: 100 нФ"]
  PEEWPPU["RC0402FR-0710KL #PD-WP<br/>reset-high pull-up защиты записи EEPROM: 10 кОм"]
  PLSCLPU["RC0402FR-072K2L #PD-SCL<br/>pull-up SCL локальной PD-шины: 2,2 кОм"]
  PLSDAPU["RC0402FR-072K2L #PD-SDA<br/>pull-up SDA локальной PD-шины: 2,2 кОм"]
  PHSCLPU["RC0402FR-072K2L #SYS-SCL<br/>pull-up SCL системной host-шины: 2,2 кОм"]
  PHSDAPU["RC0402FR-072K2L #SYS-SDA<br/>pull-up SDA системной host-шины: 2,2 кОм"]
  PIRQPU["RC0402FR-0710KL #SYS-IRQ<br/>pull-up общего wired-low IRQ: 10 кОм"]
  CHARGER["BQ25798RQMR<br/>настроенный на 2S buck-boost зарядник и NVDC системный power path"]
  CHL["MWSA0503S-2R2MT<br/>дроссель зарядника 2,2 мкГн, 7 А, 750 кГц"]
  CVB0["GRM31CR71E106MA12L #VBUS0<br/>конденсатор VBUS зарядника №0: 10 мкФ, 25 В, X7R"]
  CVB1["GRM31CR71E106MA12L #VBUS1<br/>конденсатор VBUS зарядника №1: 10 мкФ, 25 В, X7R"]
  CVBHF["C1005X7R1H104K050BB #VBUS<br/>HF-конденсатор VBUS зарядника: 100 нФ, 50 В"]
  CPM0["GRM31CR71E106MA12L #PMID0<br/>конденсатор PMID зарядника №0: 10 мкФ, 25 В, X7R"]
  CPM1["GRM31CR71E106MA12L #PMID1<br/>конденсатор PMID зарядника №1: 10 мкФ, 25 В, X7R"]
  CPM2["GRM31CR71E106MA12L #PMID2<br/>конденсатор PMID зарядника №2: 10 мкФ, 25 В, X7R"]
  CPMHF["C1005X7R1H104K050BB #PMID<br/>HF-конденсатор PMID зарядника: 100 нФ, 50 В"]
  CSYS0["GRM31CR71E106MA12L #SYS0<br/>конденсатор SYS зарядника №0: 10 мкФ, 25 В, X7R"]
  CSYS1["GRM31CR71E106MA12L #SYS1<br/>конденсатор SYS зарядника №1: 10 мкФ, 25 В, X7R"]
  CSYS2["GRM31CR71E106MA12L #SYS2<br/>конденсатор SYS зарядника №2: 10 мкФ, 25 В, X7R"]
  CSYS3["GRM31CR71E106MA12L #SYS3<br/>конденсатор SYS зарядника №3: 10 мкФ, 25 В, X7R"]
  CSYS4["GRM31CR71E106MA12L #SYS4<br/>конденсатор SYS зарядника №4: 10 мкФ, 25 В, X7R"]
  CSYSHF["C1005X7R1H104K050BB #SYS<br/>HF-конденсатор SYS зарядника: 100 нФ, 50 В"]
  CBAT0["GRM31CR71E106MA12L #BAT0<br/>конденсатор BAT зарядника №0: 10 мкФ, 25 В, X7R"]
  CBAT1["GRM31CR71E106MA12L #BAT1<br/>конденсатор BAT зарядника №1: 10 мкФ, 25 В, X7R"]
  CBT1["GRM155R71E473KA88D #BTST1<br/>bootstrap-конденсатор зарядника №1: 47 нФ, 25 В"]
  CBT2["GRM155R71E473KA88D #BTST2<br/>bootstrap-конденсатор зарядника №2: 47 нФ, 25 В"]
  CREGN["CGA5L1X7R1E475K160AC #REGN<br/>конденсатор REGN зарядника: 4,7 мкФ, 25 В"]
  CSDRV["C0402C102K5RACTU<br/>конденсатор SDRV no-ship-FET: 1 нФ, 50 В"]
  CPROG["RC0402FR-078K2L<br/>резистор PROG 8,2 кОм, 1% для 2S/750 кГц"]
  CBATP["RC0402FR-07100RL<br/>резистор BATP sense 100 Ом, 1%"]
  CTSU["RC0402FR-075K23L<br/>верхний резистор TS зарядника 5,23 кОм, 1%"]
  CTSL["RC0402FR-0730K1L<br/>нижний резистор TS зарядника 30,1 кОм, 1%"]
  CTSN["B57332V5103F360 #CHARGER<br/>независимый NTC батареи зарядника 10 кОм"]
  CILU["RC0402FR-0744K2L<br/>верхний резистор аппаратного ILIM 44,2 кОм, 1%"]
  CILL["RC0402FR-07100KL<br/>нижний резистор аппаратного ILIM 100 кОм, 1%"]
  CINTPU["RC0402FR-0710KL #CHG-INT<br/>pull-up резистор INT зарядника 10 кОм"]
  CCEPU["RC0402FR-0710KL #CHG-CE<br/>reset-high pull-up резистор CE зарядника 10 кОм"]
  HOLDER["Keystone Electronics 1048P<br/>поляризованный держатель 2× protected button-top 18650"]
  CELL0["XTAR 18650 4000mAh #0<br/>квалифицированная защищённая button-top 4-А·ч ячейка"]
  FUSE0["0451005.MRL<br/>независимый 5-А fast fuse слота 0"]
  NTC0["B57332V5103F360<br/>датчик температуры банки 0"]
  CELL1["XTAR 18650 4000mAh #1<br/>квалифицированная защищённая button-top 4-А·ч ячейка"]
  FUSE1["0451005.MRL<br/>независимый 5-А fast fuse слота 1"]
  NTC1["B57332V5103F360<br/>датчик температуры банки 1"]
  PACKGAUGE["MAX17320G20+T<br/>high-side защита 2S, gauging, температура и балансировка"]
  SHUNT["WSL25125L000FEA<br/>5-mOhm Kelvin current shunt"]
  PACKFET["CSD87313DMST<br/>полностью переключаемая common-drain CHG/DIS пара"]
  PACKHOLD["2N7002DW-7-F<br/>reset-default ALRT hold и явное снятие"]
  SUPPLYOR["BAV70LT1G<br/>изоляция источников AOLDO/fixture"]
  SYSDIODE["BAT54-7-F<br/>изоляция и приоритет admitted-system source"]
  PACKADM["MSPM0C1104SDGS20R<br/>fail-closed допуск пары, watchdog и service bridge"]
  DIAGTMR["TPUL2G223BQBR<br/>non-retriggerable ограничитель импульса и аппаратный cooldown"]
  DIAGTR["RC0402FR-07169KL #DIAG-TIME<br/>169-кОм 1% резистор времени диагностического импульса"]
  DIAGTC["GRM31C5C1H224JE02L #DIAG-TIME<br/>220-нФ 50-В C0G конденсатор времени диагностического импульса"]
  DIAGLR["RC0402FR-07620KL<br/>620-кОм 1% резистор аппаратного cooldown"]
  DIAGLC["C1608X7R1C105K080AC<br/>1-мкФ 16-В X7R конденсатор аппаратного cooldown"]
  DIAGBP["C1005X7R1H104K050BB #DIAG<br/>100-нФ 50-В X7R bypass-конденсатор one-shot"]
  DIAGTRPD["RC0402FR-0710KL #DIAG-TRIG<br/>10-кОм 1% fail-low резистор диагностического trigger"]
  DIAGGPD["RC0402FR-0710KL #DIAG-GATE<br/>10-кОм 1% fail-low резистор затвора нагрузки"]
  DIAGQ["DMN2056U-7<br/>20-В MOSFET диагностической нагрузки с низким gate drive"]
  DIAGR0["CRM2512-FX-20R0ELF #0<br/>20-Ом 2-Вт pulse-rated ветвь диагностической нагрузки"]
  DIAGR1["CRM2512-FX-20R0ELF #1<br/>20-Ом 2-Вт pulse-rated ветвь диагностической нагрузки"]
  MIDADC0["RC0402FR-07220KL #MID-TOP0<br/>220-кОм 1% верхний резистор делителя midpoint №0"]
  MIDADC1["RC0402FR-07220KL #MID-TOP1<br/>220-кОм 1% верхний резистор делителя midpoint №1"]
  MIDADCB["RC0402FR-07169KL #MID-BOTTOM<br/>169-кОм 1% нижний резистор делителя midpoint"]
  MIDADCC["GRM155R71H103KA88D #MID<br/>10-нФ 50-В X7R фильтр ADC midpoint"]
  STACKADC0["RC0402FR-07220KL #STACK-TOP0<br/>220-кОм 1% верхний резистор делителя stack №0"]
  STACKADC1["RC0402FR-07220KL #STACK-TOP1<br/>220-кОм 1% верхний резистор делителя stack №1"]
  STACKADC2["RC0402FR-07220KL #STACK-TOP2<br/>220-кОм 1% верхний резистор делителя stack №2"]
  STACKADC3["RC0402FR-07220KL #STACK-TOP3<br/>220-кОм 1% верхний резистор делителя stack №3"]
  STACKADC4["RC0402FR-07220KL #STACK-TOP4<br/>220-кОм 1% верхний резистор делителя stack №4"]
  STACKADCB["RC0402FR-07169KL #STACK-BOTTOM<br/>169-кОм 1% нижний резистор делителя stack"]
  STACKADCC["GRM155R71H103KA88D #STACK<br/>10-нФ 50-В X7R фильтр ADC полного stack"]
  AONBUCK["TPS629203DRLR<br/>low-IQ always-on преобразователь безопасности 3,3 В"]
  AONL["WPN201612H2R2MT<br/>экранированный дроссель 2,2 мкГн шины AON"]
  AONMODE["RC0402FR-0742K2L<br/>42,2-кОм 1% резистор режима/конфигурации AON"]
  AONIN["CGA5L1X7R1E475K160AC<br/>4,7-мкФ 25-В X7R входной конденсатор AON"]
  AONOUT["GRM31CR71A226KE15L<br/>22-мкФ 10-В X7R конденсатор сырого выхода AON"]
  AONFUSE["TPS25961DRVR<br/>независимая отсечка AON по перенапряжению, току и КЗ"]
  AONRILIM["RC0402FR-07240KL<br/>240-кОм 1% резистор ограничения тока eFuse AON"]
  AONOVT["RC0402FR-07196KL<br/>196-кОм 1% верхний резистор OVLO eFuse AON"]
  AONOVB["RC0402FR-07100KL #AON-OVLO<br/>100-кОм 1% нижний резистор OVLO eFuse AON"]
  AONFIN["C1005X7R1H104K050BB #AON-EFUSE-IN<br/>100-нФ 50-В X7R входной конденсатор eFuse AON"]
  AONFOUT["GRM188R60J106ME47D #AON-SAFE<br/>10-мкФ 6,3-В X5R выходной конденсатор защищённой AON"]
  AONPGPU["RC0402FR-0747KL<br/>47-кОм 1% pull-up резистор power-good AON"]
  PORPU["RC0402FR-0710KL #AON-POR<br/>10-кОм 1% pull-up резистор AON POR"]
  MAINBUCK["TPS564252DRLR<br/>фиксированный 4-А преобразователь основной шины 3,3 В"]
  MAINL["MWSA0503S-3R3MT<br/>силовой дроссель 3,3 мкГн основной шины"]
  MAININ["GRM32ER71E226KE15L #MAIN-IN<br/>22-мкФ 25-В X7R входной bulk-конденсатор основной шины"]
  MAINHF["C1005X7R1H104K050BB #MAIN<br/>100-нФ 50-В X7R входной HF-конденсатор основной шины"]
  MAINFBT["RC0402FR-0745K3L<br/>45,3-кОм 1% верхний резистор FB основной шины"]
  MAINFBB["RC0402FR-0710KL<br/>10-кОм 1% нижний резистор FB основной шины"]
  MAINFF["C0402C330J5GACTU #MAIN<br/>33-пФ 50-В C0G feed-forward конденсатор основной шины"]
  MAINOUT0["GRM32ER71E226KE15L #MAIN-OUT0<br/>22-мкФ 25-В X7R конденсатор сырого выхода основной шины №0"]
  MAINOUT1["GRM32ER71E226KE15L #MAIN-OUT1<br/>22-мкФ 25-В X7R конденсатор сырого выхода основной шины №1"]
  MAINFUSE["TPS25974LRPWR #MAIN<br/>latch-off eFuse основной шины с OVLO, circuit breaker и защищённым PG"]
  MAINRILM["RC0402FR-071K65L<br/>1,65-кОм 1% резистор порога eFuse основной шины"]
  MAINDVDT["GRM155R71H472KA01D #MAIN<br/>4,7-нФ 50-В X7R конденсатор slew eFuse основной шины"]
  MAINIT["GRM1555C1H121JA01D #MAIN<br/>120-пФ 50-В C0G таймер transient eFuse основной шины"]
  MAINOVT["RT0402BRD07191KL<br/>191-кОм 0,1% верхний резистор OVLO eFuse основной шины"]
  MAINOVB["RT0402BRD07100KL<br/>100-кОм 0,1% нижний резистор OVLO eFuse основной шины"]
  MAINPGT["RC0402FR-0745K3L #MAIN-PGTH<br/>45,3-кОм 1% верхний резистор protected-PG основной шины"]
  MAINPGB["RC0402FR-0730KL #MAIN-PGTH<br/>30-кОм 1% нижний резистор protected-PG основной шины"]
  MAINFOUT["GRM188R60J106ME47D #MAIN-SAFE<br/>10-мкФ 6,3-В X5R выходной конденсатор защищённой основной шины"]
  MAINENPD["RC0402FR-07100KL #MAIN-EN<br/>100-кОм 1% fail-low резистор EN основной шины"]
  FAULTPU["RC0402FR-0710KL #POWER-FAULT<br/>10-кОм 1% pull-up резистор общей линии power-fault"]
  VOICEBUCK["TPS564252DRLR<br/>фиксированный 4-А преобразователь голосовой шины 4,0 В"]
  VOICEL["MWSA0503S-3R3MT<br/>силовой дроссель 3,3 мкГн голосовой шины"]
  VOICEIN["GRM32ER71E226KE15L #VOICE-IN<br/>22-мкФ 25-В X7R входной bulk-конденсатор voice"]
  VOICEHF["C1005X7R1H104K050BB #VOICE<br/>100-нФ 50-В X7R входной HF-конденсатор voice"]
  VOICEFBT["RC0402FR-0768KL<br/>68-кОм 1% верхний резистор FB voice"]
  VOICEFBB["RC0402FR-0712KL<br/>12-кОм 1% нижний резистор FB voice"]
  VOICEFF["C0402C330J5GACTU #VOICE<br/>33-пФ 50-В C0G feed-forward конденсатор voice"]
  VOICEOUT0["GRM32ER71E226KE15L #VOICE-OUT0<br/>22-мкФ 25-В X7R конденсатор сырого выхода voice №0"]
  VOICEOUT1["GRM32ER71E226KE15L #VOICE-OUT1<br/>22-мкФ 25-В X7R конденсатор сырого выхода voice №1"]
  VOICEFUSE["TPS25974LRPWR #VOICE<br/>latch-off eFuse voice с OVLO, circuit breaker и защищённым PG"]
  VOICERILIM["RC0402FR-073K32L<br/>3,32-кОм 1% резистор порога eFuse voice"]
  VOICEDVDT["GRM155R71H472KA01D #VOICE<br/>4,7-нФ 50-В X7R конденсатор slew eFuse voice"]
  VOICEIT["GRM1555C1H121JA01D #VOICE<br/>120-пФ 50-В C0G таймер transient eFuse voice"]
  VOICEOVT["RC0402FR-07270KL<br/>270-кОм 1% верхний резистор OVLO eFuse voice"]
  VOICEOVB["RC0402FR-07100KL #VOICE-OVLO<br/>100-кОм 1% нижний резистор OVLO eFuse voice"]
  VOICEPGT["RC0402FR-0768KL #VOICE-PGTH<br/>68-кОм 1% верхний резистор protected-PG voice"]
  VOICEPGB["RC0402FR-0733KL #VOICE-PGTH<br/>33-кОм 1% нижний резистор protected-PG voice"]
  VOICEFOUT["GRM188R60J106ME47D #VOICE-SAFE<br/>10-мкФ 6,3-В X5R выходной конденсатор защищённой voice"]
  VOICEENPD["RC0402FR-0710KL #VOICE-EN<br/>10-кОм 1% fail-low резистор EN голосовой шины"]
  VOICEPGPU["RC0402FR-0710KL #VOICE-PG<br/>10-кОм 1% pull-up резистор PG голосовой шины"]
  VOICEPGBR["RC0402FR-0768KL #VOICE-PG-BASE<br/>68-кОм 1% базовый резистор PG-квалификатора voice"]
  VOICEPGQ["MMBT3904-7-F<br/>EN-квалифицированный транзистор PG/fault голосовой шины"]
  EXTBUCK["TPS564252DRLR<br/>фиксированный 4-А преобразователь расширения 5,0 В"]
  EXTL["MWSA0503S-4R7MT<br/>силовой дроссель 4,7 мкГн шины расширения"]
  EXTBUCKIN["GRM32ER71E226KE15L #EXT-BUCK-IN<br/>22-мкФ 25-В X7R входной bulk-конденсатор buck расширения"]
  EXTBUCKHF["C1005X7R1H104K050BB #EXT-BUCK<br/>100-нФ 50-В X7R входной HF-конденсатор buck расширения"]
  EXTBUCKFBT["RC0402FR-07220KL<br/>220-кОм 1% верхний резистор FB расширения"]
  EXTBUCKFBB["RC0402FR-0730KL<br/>30-кОм 1% нижний резистор FB расширения"]
  EXTBUCKFF["C0402C330J5GACTU #EXT-BUCK<br/>33-пФ 50-В C0G feed-forward конденсатор расширения"]
  EXTBUCKOUT0["GRM32ER71E226KE15L #EXT-BUCK-OUT0<br/>22-мкФ 25-В X7R выходной конденсатор buck расширения №0"]
  EXTBUCKOUT1["GRM32ER71E226KE15L #EXT-BUCK-OUT1<br/>22-мкФ 25-В X7R выходной конденсатор buck расширения №1"]
  EXTENPD["RC0402FR-0710KL #EXT-EN<br/>10-кОм 1% fail-low резистор EN шины расширения"]
  EXTPGPU["RC0402FR-0710KL #EXT-PG<br/>10-кОм 1% pull-up резистор PG шины расширения"]
  EXTPGBR["RC0402FR-0768KL #EXT-PG-BASE<br/>68-кОм 1% базовый резистор PG-квалификатора расширения"]
  EXTPGQ["MMBT3904-7-F<br/>EN-квалифицированный транзистор PG/fault шины расширения"]
  EXTFUSE["TPS259470LRPWR<br/>latch-off eFuse расширения с true reverse blocking и измерением тока"]
  EXTRILM["RC0402FR-072K21L<br/>2,21-кОм 1% резистор ограничения тока eFuse"]
  EXTDVDT["GRM155R71H472KA01D<br/>4,7-нФ 50-В X7R конденсатор плавного запуска"]
  EXTITIMER["GRM188R71E224KA88D<br/>220-нФ 25-В X7R таймер импульса после запуска"]
  EXTOVLOT["RC0402FR-07169KL<br/>169-кОм 1% верхний резистор OVLO eFuse"]
  EXTOVLOB["RC0402FR-0747KL<br/>47-кОм 1% нижний резистор OVLO eFuse"]
  EXTINCAP["GRM21BR71E225KE11L #IN<br/>2,2-мкФ 25-В X7R локальный входной конденсатор eFuse"]
  EXTOUTCAP["GRM21BR71E225KE11L #OUT<br/>2,2-мкФ 25-В X7R локальный выходной конденсатор eFuse"]
  EXTBLEED["RC0603FR-071KL<br/>1-кОм 1% резистор разряда защищённого выхода"]
  SWNRF["TPS22919DCKR<br/>quiet-state ключ группы из трёх nRF"]
  SWCC["TPS22919DCKR<br/>quiet-state ключ CC1101"]
  SWSD["TPS22919DCKR<br/>quiet-state ключ microSD"]
  SWCODEC["TPS22919DCKR<br/>quiet-state ключ ES8311"]
  SWRX["TPS22919DCKR<br/>quiet-state ключ Si4732"]
  S3["ESP32-S3-WROOM-1U-N16R2<br/>application, UI, display/storage, audio, BLE/Wi-Fi owner"]
  C5["ESP32-C5-WROOM-1U-N8R8<br/>2.4/5 GHz, IEEE 802.15.4 and IR owner"]
  RP["RP2354B A4<br/>deterministic radio and voice owner"]
  SLOW["TCA6424ARGJR<br/>24-line main slow-control expander; three contacts free"]
  SLOWVCI["C1005X7R1H104K050BB #SLOW-VCCI<br/>100-нФ развязка VCCI главного slow-I/O"]
  SLOWVCP["C1005X7R1H104K050BB #SLOW-VCCP<br/>100-нФ развязка VCCP главного slow-I/O"]
  SLOWBULK["C1608X7R1C105K080AC #SLOW<br/>1-мкФ локальный bulk-конденсатор главного slow-I/O"]
  SLOWRSTPU["RC0402FR-0710KL #SLOW-RESET<br/>10-кОм pull-up RESET_N главного slow-I/O"]
  SLOWRST(("SLOW_IO_RESET_N<br/>защищённый fixture-reset узел"))
  SLOWSTOPISO["SN74LVC1G07DCKR #STOP-SENSE<br/>AON open-drain изолятор домена STOP-sense"]
  SLOWSTOPBP["C1005X7R1H104K050BB #STOP-SENSE<br/>100-нФ развязка изолятора STOP-sense"]
  SLOWSTOPPU["RC0402FR-0710KL #STOP-SENSE<br/>10-кОм main-domain pull-up STOP-sense"]
  SLOWEVISO["SN74LVC1G07DCKR #S3-EVIDENCE<br/>AON open-drain изолятор домена S3-evidence"]
  SLOWEVBP["C1005X7R1H104K050BB #S3-EVIDENCE<br/>100-нФ развязка изолятора S3-evidence"]
  SLOWEVPU["RC0402FR-0710KL #S3-EVIDENCE<br/>10-кОм main-domain pull-up S3-evidence"]
  UIMATRIX["TCA9534APWR #UI<br/>dedicated interrupt-capable 4x3 control expander"]
  UIMBP["C1005X7R1H104K050BB #UI<br/>100-nF UI-expander bypass capacitor"]
  UIR0PD["RC0603FR-071KL #UI-R0<br/>1-kOhm reset/idle row pull-down"]
  UIR1PD["RC0603FR-071KL #UI-R1<br/>1-kOhm reset/idle row pull-down"]
  UIR2PD["RC0603FR-071KL #UI-R2<br/>1-kOhm reset/idle row pull-down"]
  UIR3PD["RC0603FR-071KL #UI-R3<br/>1-kOhm reset/idle row pull-down"]
  UIC0PU["RC0402FR-0710KL #UI-C0<br/>10-kOhm matrix-column pull-up"]
  UIC1PU["RC0402FR-0710KL #UI-C1<br/>10-kOhm matrix-column pull-up"]
  UIC2PU["RC0402FR-0710KL #UI-C2<br/>10-kOhm matrix-column pull-up"]
  UIMESD["TPD8E003DQDR<br/>eight-channel keypad/GPIO ESD array for P0-P7"]
  UIDUP["onsemi 1N4148WT #UP<br/>D-pad UP matrix-isolation diode"]
  UIDDN["onsemi 1N4148WT #DOWN<br/>D-pad DOWN matrix-isolation diode"]
  UIDLEFT["onsemi 1N4148WT #LEFT<br/>D-pad LEFT matrix-isolation diode"]
  UIDRIGHT["onsemi 1N4148WT #RIGHT<br/>D-pad RIGHT matrix-isolation diode"]
  UIDOK["onsemi 1N4148WT #OK<br/>D-pad OK matrix-isolation diode"]
  UIDBACK["onsemi 1N4148WT #BACK<br/>BACK matrix-isolation diode"]
  UIDOPT["onsemi 1N4148WT #OPT<br/>OPT matrix-isolation diode"]
  UIDF1["onsemi 1N4148WT #F1<br/>F1 matrix-isolation diode"]
  UIDF2["onsemi 1N4148WT #F2<br/>F2 matrix-isolation diode"]
  UIDENC["onsemi 1N4148WT #ENC<br/>encoder-push matrix-isolation diode"]
  UIUP["Y78B23214FP<br/>D-pad UP ultra-low-current ordinary control"]
  UIDOWN["Y78B23214FP<br/>D-pad DOWN ultra-low-current ordinary control"]
  UILEFT["Y78B23214FP<br/>D-pad LEFT ultra-low-current ordinary control"]
  UIRIGHT["Y78B23214FP<br/>D-pad RIGHT ultra-low-current ordinary control"]
  UIOK["Y78B23214FP<br/>D-pad OK ultra-low-current ordinary control"]
  UIBACK["Y78B23214FP<br/>BACK ultra-low-current ordinary control"]
  UIOPT["Y78B23214FP<br/>OPT ultra-low-current ordinary control"]
  UIF1["Y78B23214FP<br/>F1 ultra-low-current ordinary control"]
  UIF2["Y78B23214FP<br/>F2 ultra-low-current ordinary control"]
  ENC["Alps Alpine EC11E18244AU<br/>36-detent/18-pulse encoder with push"]
  ENCAPU["RC0402FR-073K32L #ENC-A<br/>3.32-kOhm encoder-phase-A contact-current pull-up"]
  ENCBPU["RC0402FR-073K32L #ENC-B<br/>3.32-kOhm encoder-phase-B contact-current pull-up"]
  ENCPTTESD["TPD4E05U06DQAR<br/>four-channel encoder/PTT ESD array"]
  PTTPU["RC0402FR-0710KL<br/>10-kOhm direct-PTT pull-up"]
  PTTR["RC0603FR-071KL<br/>1-kOhm direct-PTT input series resistor"]
  PTTC["C1005X7R1H104K050BB<br/>100-nF direct-PTT hardware filter"]
  PTTRAW(("PTT_BUTTON_RAW_N<br/>active-low direct-PTT node"))
  TPIRQ["SN74LVC1G07DCKR<br/>open-drain touch-interrupt adapter"]
  TPIRQPU["RC0402FR-0710KL<br/>10-кОм pull-up сырого active-low TP_INT"]
  TPIRQRAW(("LCD_TOUCH_INT_RAW_N<br/>active-low touch-узел ST77922"))
  TPIRQBP["C1005X7R1H104K050BB #TP-IRQ<br/>100-nF touch-IRQ adapter bypass capacitor"]
  LCDCON["FH12-40S-0.5SH(55)<br/>первый кандидат 40-контактного ZIF 0,5 мм с нижними контактами для шлейфа экрана"]
  LCD["HMX035CTFT-001<br/>3.5-inch QSPI IPS display and capacitive-touch assembly"]
  LCDTDDI["Sitronix ST77922<br/>встроенный display и capacitive-touch TDDI COG"]
  LCDLBULK["GRM188R60J106ME47D #LCD-LOGIC<br/>10-мкФ буферный конденсатор логического питания экрана"]
  LCDLHF["C1005X7R1H104K050BB #LCD-LOGIC<br/>100-нФ ВЧ-развязка логического питания экрана"]
  LCDRPD["RC0402FR-0710KL #LCD-RESX<br/>10-кОм подтяжка reset экрана к неактивному состоянию"]
  TPRPD["RC0402FR-0710KL #TP-RESXP<br/>10-кОм подтяжка reset тач-контроллера к неактивному состоянию"]
  BLEFUSE["TPS2553DRVR-1<br/>защёлкиваемый ключ питания LEDA с блокировкой обратного тока"]
  BLILIM["RC0402FR-07133KL<br/>133-кОм 1% резистор лимита подсветки около 200 мА"]
  BLIN["C1005X7R1H104K050BB #BL-IN<br/>100-нФ входная ВЧ-развязка ключа подсветки"]
  BLOUT["GRM188R60J106ME47D #BL-OUT<br/>10-мкФ буферный конденсатор защищённого LEDA"]
  BLOUTHF["C1005X7R1H104K050BB #BL-OUT<br/>100-нФ ВЧ-развязка защищённого LEDA"]
  BLFPU["RC0402FR-0710KL #BL-FAULT<br/>10-кОм подтяжка open-drain ошибки подсветки"]
  BLR["ERJ-P08F10R0V<br/>10-Ом 0,66-Вт anti-surge резистор катодов LED"]
  BLQ["DMN2056U-7 #BACKLIGHT<br/>низкопороговый MOSFET ШИМ катодов LED"]
  BLGR["RC0402FR-07100RL #BL-GATE<br/>100-Ом последовательный резистор затвора ШИМ"]
  BLGPD["RC0402FR-0710KL #BL-GATE<br/>10-кОм reset-off подтяжка затвора"]
  SD["DM3AT-SF-PEJM5<br/>push-push microSD card connector"]
  SDHBUF["SN74LVC3G34DCUR<br/>трёхканальный Ioff-буфер SCK/CMD/CS со стороны карты"]
  SDMBUF["SN74LVC1G125DCKR<br/>CS-gated Ioff-буфер возврата DAT0/MISO"]
  SDESDA["TPD4E05U06DQAR #SD-A<br/>четырёхканальная ESD-сборка сигналов microSD"]
  SDESDB["TPD4E05U06DQAR #SD-B<br/>четырёхканальная ESD-сборка питания/сигналов/detect microSD"]
  SDINCAP["C1608X7R1C105K080AC #SD-IN<br/>1-мкФ входная развязка ключа накопителя"]
  SDBULK["GRM21BR60J226ME39L<br/>22-мкФ bulk-конденсатор включаемой карты"]
  SDHFCAP["C1005X7R1H104K050BB #SD-RAIL<br/>100-нФ ВЧ-развязка включаемой карты"]
  SDHBUFCAP["C1005X7R1H104K050BB #SD-HOST-BUF<br/>100-нФ развязка тройного буфера"]
  SDMBUFCAP["C1005X7R1H104K050BB #SD-MISO-BUF<br/>100-нФ развязка буфера возврата"]
  SDONPD["RC0402FR-0710KL #SD-ON<br/>10-кОм reset-off pull-down питания карты"]
  SDSCKPD["RC0402FR-0710KL #SD-SCK<br/>10-кОм reset-low pull-down общей тактовой"]
  SDD0PU["RC0402FR-0710KL #SD-D0<br/>10-кОм reset-high pull-up общей D0"]
  SDD1PU["RC0402FR-0710KL #SD-D1<br/>10-кОм reset-high pull-up общей D1"]
  SDHCS["RC0402FR-0710KL #SD-CS<br/>10-кОм reset-high pull-up CS карты"]
  LCDHCS["RC0402FR-0710KL #LCD-CS<br/>10-кОм reset-high pull-up CS дисплея"]
  SDCPUCMD["RC0402FR-0710KL #SD-CMD<br/>10-кОм pull-up CMD от питания карты"]
  SDCPUD0["RC0402FR-0710KL #SD-DAT0<br/>10-кОм pull-up DAT0 от питания карты"]
  SDCPUD1["RC0402FR-0710KL #SD-DAT1<br/>10-кОм pull-up DAT1 от питания карты"]
  SDCPUD2["RC0402FR-0710KL #SD-DAT2<br/>10-кОм pull-up DAT2 от питания карты"]
  SDCPUD3["RC0402FR-0710KL #SD-DAT3<br/>10-кОм pull-up DAT3/CS от питания карты"]
  SDSCKR["ERJ-2RKF22R0X #SD-SCK<br/>22-Ом последовательный резистор тактовой карты"]
  SDCMDR["ERJ-2RKF22R0X #SD-CMD<br/>22-Ом последовательный резистор CMD карты"]
  SDCSR["ERJ-2RKF22R0X #SD-CS<br/>22-Ом последовательный резистор CS карты"]
  SDMISOR["ERJ-2RKF22R0X #SD-MISO<br/>22-Ом последовательный резистор буфера возврата"]
  SDDETR["RC0603FR-071KL #SD-DETECT<br/>1-кОм входной резистор card-detect"]
  SDDETPU["RC0402FR-0710KL #SD-DETECT<br/>10-кОм pull-up всегда читаемого card-detect"]
  SDDETC["C1005X7R1H104K050BB #SD-DETECT<br/>100-нФ аппаратный фильтр card-detect"]
  SI["Si4732-A10-GS<br/>AM/FM/SW/LW broadcast receiver"]
  RXCLK["Q13FC13500005<br/>кварц приёмника 32,768 кГц"]
  RXCLKC0["GRM1555C1H220JA01D #RX-RCLK<br/>конденсатор кварца приёмника 22 пФ"]
  RXCLKC1["GRM1555C1H220JA01D #RX-GPO3<br/>конденсатор кварца приёмника 22 пФ"]
  RXSUP["TPS3839K33DBZR #RX<br/>супервизор приёмника 3,08 В / 200 мс"]
  RXI2C["SN74LVC2G66DCUR #RX-I2C<br/>развязка питания I²C приёмника"]
  CODEC["Everest Semiconductor ES8311<br/>монофонический аудиокодек ADC/DAC"]
  CODECSUP["TPS3839K33DBZR #CODEC<br/>супервизор интерфейсов кодека 3,08 В / 200 мс"]
  CODECI2C["SN74LVC2G66DCUR #ES8311-I2C<br/>развязка питания I²C кодека"]
  CODECBCLK["SN74LVC1G126DCKR #BCLK<br/>отдельный буфер развязки BCLK кодека"]
  CODECWS["SN74LVC1G126DCKR #WS<br/>отдельный буфер развязки WS кодека"]
  CODECDOUT["SN74LVC1G126DCKR #DOUT<br/>отдельный буфер данных воспроизведения"]
  CODECDIN["SN74LVC1G126DCKR #DIN<br/>отдельный буфер данных записи"]
  RXMUX["SN74LVC1G3157DBVR<br/>receive-audio source selector"]
  CAPSEL["TS5A63157DCKR #CAPTURE<br/>селектор записи RX/микрофон"]
  BUF["TLV9061IDBVR<br/>active high-impedance capture buffer"]
  SPKSEL["TMUX1136DGSR<br/>dual differential speaker-path selector"]
  TXSEL["TS5A63157DCKR #TX<br/>селектор электрет/кодек передаваемого аудио"]
  SAFE["SN74LVC2G08DCUR<br/>reset-safe selector-request gate"]
  PAM["PAM8302AASCR<br/>mono Class-D speaker amplifier"]
  SPKBEADP["BLM18PG181SN1D #SPK-P<br/>положительная EMI-бусина выхода класса D"]
  SPKBEADN["BLM18PG181SN1D #SPK-N<br/>отрицательная EMI-бусина выхода класса D"]
  SPK["AS02404PO<br/>внутренний динамик 24 × 12 мм, 4 Ом, 2 Вт"]
  MIC["CMEJ-0413-42-SMT-TR<br/>верхнепортовый аналоговый электретный микрофон"]
  MICFILT["RC0402FR-07220RL<br/>резистор фильтра смещения микрофона 220 Ом"]
  AGNDLINK["RC0402JR-070RL<br/>единственная звезда аудиоземли к силовой земле"]
  HPJACK["SJ1-3515-SMT-TR<br/>стереоразъём 3,5 мм с контактами вставки"]
  HPESD["TPD4E05U06DQAR #HEADPHONE<br/>IEC-ESD-защита tip/ring наушников"]
  NRF0["E01-ML01IPX<br/>nRF24-compatible radio #0 compact IPEX reference"]
  NRF1["E01-ML01IPX<br/>nRF24-compatible radio #1 compact IPEX reference"]
  NRF2["E01-ML01IPX<br/>nRF24-compatible radio #2 compact IPEX reference"]
  CC["CC1101RGPR<br/>sub-GHz transceiver"]
  SA["NiceRF SA518<br/>VHF/UHF analog voice transceiver"]
  VOICESUP["TPS3808G33DBVR #VOICE<br/>STOP-квалифицированный супервизор голосовой шины 4 В"]
  VOICEIOSW["TPS22919DCKR #VOICE-IO<br/>разряжаемый локальный источник интерфейсов SA518"]
  VOICEPTT["SN74LVC1G126DCKR #VOICE-PTT<br/>отдельный буфер развязки PTT модуля"]
  VOICEUART["SN74LVC1G126DCKR #VOICE-UART<br/>отдельный буфер UART к модулю"]
  VOICEHL["SN74LVC1G07DCKR #VOICE-HL<br/>драйвер low/open для SA518 H/L"]
  VOICEAUDIO["SN74LVC2G66DCUR #VOICE-AUDIO<br/>двухканальная развязка AFOUT/MIC_IN"]
  CAPDOCK["MPN TBD<br/>2×7 female 2.54-mm host Cap-Bus receptacle"]
  U214["M5Stack U214 Cap LoRa-1262<br/>external LoRa/GNSS Cap module"]
  ISO["TCA4307DGKR<br/>external I2C stuck-bus isolator"]
  UNIT["MPN TBD<br/>protected HY2.0-4P M5 Unit connector"]
  IR0["MPN TBD (TSOP38238 screened)<br/>38 kHz demodulating IR receiver"]
  IR1["MPN TBD (TSMP95000 screened)<br/>carrier-learning IR receiver"]
  IRTX["MPN TBD (TSAL6200 screened)<br/>IR transmit LED/driver endpoint"]
  PTTSW["Y78B23214FP<br/>separate normally-open hold-to-talk PTT control"]
  STOPSW["AEQ10410<br/>gold-clad low-level normally-closed hard-STOP control"]
  REARMSW["Y78B23214FP<br/>normally-open recessed RE-ARM control"]
  STOPPU["RC0402FR-0710KL<br/>10-kOhm AON STOP contact-current pull-up"]
  STOPC["GRM155R71H103KA88D<br/>10-nF X7R asynchronous STOP filter"]
  REARMPU["RC0402FR-0747KL<br/>47-kOhm AON RE-ARM contact-current pull-up"]
  REARMC["C1005X7R1H104K050BB<br/>100-nF X7R RE-ARM filter"]
  SAFEESD["TPD4E05U06DQAR<br/>dedicated STOP/RE-ARM ESD array"]
  STOPLOOP(("STOP_LOOP_SENSE<br/>fail-open AON STOP node"))
  REARMRAW(("REARM_RAW<br/>fresh-press AON node"))
  SUP["TPS3808G33DBVR<br/>AON rail supervisor and power-on reset"]
  COND["74LVC2G14GW,125<br/>STOP and RE-ARM Schmitt conditioner"]
  POROR["74LVC1G32GV,125<br/>STOP-dominant POR/clear combiner"]
  LATCH["SN74LVC1G74DCUR<br/>asynchronous latched hard STOP"]
  RSTBUF["SN74LVC3G34DCUR<br/>Ioff three-domain reset fan-out"]
  GATEA["SN74LVC08APWR #1<br/>four STOP-dominant nRF request gates"]
  GATEB["SN74LVC08APWR #2<br/>four STOP-dominant rail/IR/accessory gates"]
  PTTOR["74LVC1G32GV,125 #2<br/>active-low voice PTT force-RX gate"]
  STOPLEDR["RC0402FR-072K2L #STOP<br/>2,2-кОм ограничитель тока аппаратного STOP-индикатора"]
  STOPLED["LTST-C190KFKT<br/>orange physical latched-STOP indicator"]
  DS3["LTC5532ES6#TRMPBF #S3<br/>S3 2.4-GHz RF power detector"]
  DC5["LTC5532ES6#TRMPBF #C5<br/>C5 2.4/5-GHz RF power detector"]
  DN0["LTC5532ES6#TRMPBF #nRF0<br/>nRF0 2.4-GHz RF power detector"]
  DN1["LTC5532ES6#TRMPBF #nRF1<br/>nRF1 2.4-GHz RF power detector"]
  DN2["LTC5532ES6#TRMPBF #nRF2<br/>nRF2 2.4-GHz RF power detector"]
  DCC["LTC5507ES6#TRMPBF #CC<br/>CC1101 sub-GHz RF power detector"]
  DVOICE["LTC5507ES6#TRMPBF #voice<br/>SA518 VHF/UHF RF power detector"]
  DIR["VEMD1060X01<br/>IR optical-evidence photodiode"]
  CMPA["TLV1824PWR #1<br/>S3/C5/nRF0/nRF1 evidence thresholds"]
  CMPB["TLV1824PWR #2<br/>nRF2/CC/voice/IR evidence thresholds"]
  EVMASK["TCA9534APWR<br/>eight-bit evidence source mask on local RP I²C0"]
  OR0["BAT54ALT1G #0<br/>evidence diode-OR pair 0/1"]
  OR1["BAT54ALT1G #1<br/>evidence diode-OR pair 2/3"]
  OR2["BAT54ALT1G #2<br/>evidence diode-OR pair 4/5"]
  OR3["BAT54ALT1G #3<br/>evidence diode-OR pair 6/7"]
  ANYLED["LTST-C190KRKT<br/>red physical ANY-TX indicator"]
  %% Layout-only invisible spine: these links are not electrical connections.
  USBC ~~~ PORTPROT ~~~ PORTDPR ~~~ PORTDMR ~~~ PORTVBIAS ~~~ PORTVPWR ~~~ PORTFLTPU ~~~ VBUSPROT ~~~ PDCTRL ~~~ PDCFG ~~~ PVINCAP ~~~ PL3CAP ~~~ PL1CAP ~~~ PPHVC0 ~~~ PPHVC1
  PPHVC1 ~~~ PPHVC2 ~~~ PPHVC3 ~~~ PVBUSCAP ~~~ PCC1CAP ~~~ PCC2CAP ~~~ PEECAP ~~~ PEEWPPU
  PEEWPPU ~~~ PLSCLPU ~~~ PLSDAPU ~~~ PHSCLPU ~~~ PHSDAPU ~~~ PIRQPU ~~~ CHARGER
  CHARGER ~~~ CHL ~~~ CVB0 ~~~ CVB1 ~~~ CVBHF ~~~ CPM0 ~~~ CPM1 ~~~ CPM2 ~~~ CPMHF
  CPMHF ~~~ CSYS0 ~~~ CSYS1 ~~~ CSYS2 ~~~ CSYS3 ~~~ CSYS4 ~~~ CSYSHF ~~~ CBAT0 ~~~ CBAT1
  CBAT1 ~~~ CBT1 ~~~ CBT2 ~~~ CREGN ~~~ CSDRV ~~~ CPROG ~~~ CBATP ~~~ CTSU ~~~ CTSL ~~~ CTSN
  CTSN ~~~ CILU ~~~ CILL ~~~ CINTPU ~~~ CCEPU ~~~ HOLDER ~~~ CELL0 ~~~ FUSE0 ~~~ NTC0 ~~~ CELL1 ~~~ FUSE1 ~~~ NTC1
  NTC1 ~~~ PACKGAUGE ~~~ SHUNT ~~~ PACKFET ~~~ PACKHOLD ~~~ SUPPLYOR ~~~ SYSDIODE ~~~ PACKADM
  PACKADM ~~~ DIAGTMR ~~~ DIAGTR ~~~ DIAGTC ~~~ DIAGLR ~~~ DIAGLC ~~~ DIAGBP ~~~ DIAGTRPD ~~~ DIAGGPD ~~~ DIAGQ ~~~ DIAGR0 ~~~ DIAGR1
  DIAGR1 ~~~ MIDADC0 ~~~ MIDADC1 ~~~ MIDADCB ~~~ MIDADCC ~~~ STACKADC0 ~~~ STACKADC1 ~~~ STACKADC2 ~~~ STACKADC3 ~~~ STACKADC4 ~~~ STACKADCB ~~~ STACKADCC
  STACKADCC ~~~ AONBUCK ~~~ AONL ~~~ AONMODE ~~~ AONIN ~~~ AONOUT ~~~ AONFUSE ~~~ AONRILIM ~~~ AONOVT ~~~ AONOVB ~~~ AONFIN ~~~ AONFOUT ~~~ AONPGPU ~~~ PORPU
  PORPU ~~~ MAINBUCK ~~~ MAINL ~~~ MAININ ~~~ MAINHF ~~~ MAINFBT ~~~ MAINFBB ~~~ MAINFF ~~~ MAINOUT0 ~~~ MAINOUT1 ~~~ MAINFUSE ~~~ MAINRILM ~~~ MAINDVDT ~~~ MAINIT ~~~ MAINOVT ~~~ MAINOVB ~~~ MAINPGT ~~~ MAINPGB ~~~ MAINFOUT ~~~ MAINENPD ~~~ FAULTPU
  FAULTPU ~~~ VOICEBUCK ~~~ VOICEL ~~~ VOICEIN ~~~ VOICEHF ~~~ VOICEFBT ~~~ VOICEFBB ~~~ VOICEFF ~~~ VOICEOUT0 ~~~ VOICEOUT1 ~~~ VOICEFUSE ~~~ VOICERILIM ~~~ VOICEDVDT ~~~ VOICEIT ~~~ VOICEOVT ~~~ VOICEOVB ~~~ VOICEPGT ~~~ VOICEPGB ~~~ VOICEFOUT ~~~ VOICEENPD ~~~ VOICEPGPU ~~~ VOICEPGBR ~~~ VOICEPGQ
  VOICEPGQ ~~~ EXTBUCK ~~~ EXTL ~~~ EXTBUCKIN ~~~ EXTBUCKHF ~~~ EXTBUCKFBT ~~~ EXTBUCKFBB ~~~ EXTBUCKFF ~~~ EXTBUCKOUT0 ~~~ EXTBUCKOUT1 ~~~ EXTENPD ~~~ EXTPGPU ~~~ EXTPGBR ~~~ EXTPGQ ~~~ EXTFUSE ~~~ EXTRILM ~~~ EXTDVDT ~~~ EXTITIMER
  EXTITIMER ~~~ EXTOVLOT ~~~ EXTOVLOB ~~~ EXTINCAP ~~~ EXTOUTCAP ~~~ EXTBLEED ~~~ SWNRF ~~~ SWCC ~~~ SWSD ~~~ SWCODEC ~~~ SWRX ~~~ S3 ~~~ SLOW
  SLOW ~~~ SLOWVCI ~~~ SLOWVCP ~~~ SLOWBULK ~~~ SLOWRSTPU ~~~ SLOWRST ~~~ SLOWSTOPISO ~~~ SLOWSTOPBP ~~~ SLOWSTOPPU
  SLOWSTOPPU ~~~ SLOWEVISO ~~~ SLOWEVBP ~~~ SLOWEVPU ~~~ UIMATRIX ~~~ UIMBP ~~~ UIR0PD ~~~ UIR1PD ~~~ UIR2PD ~~~ UIR3PD ~~~ UIC0PU ~~~ UIC1PU ~~~ UIC2PU ~~~ UIMESD
  UIMESD ~~~ UIDUP ~~~ UIUP ~~~ UIDDN ~~~ UIDOWN ~~~ UIDLEFT ~~~ UILEFT
  UILEFT ~~~ UIDRIGHT ~~~ UIRIGHT ~~~ UIDOK ~~~ UIOK ~~~ UIDBACK ~~~ UIBACK
  UIBACK ~~~ UIDOPT ~~~ UIOPT ~~~ UIDF1 ~~~ UIF1 ~~~ UIDF2 ~~~ UIF2
  UIF2 ~~~ UIDENC ~~~ ENC ~~~ ENCAPU ~~~ ENCBPU ~~~ ENCPTTESD ~~~ PTTPU ~~~ PTTR ~~~ PTTC ~~~ PTTRAW ~~~ TPIRQPU ~~~ TPIRQRAW ~~~ TPIRQ ~~~ TPIRQBP
  TPIRQBP ~~~ SI ~~~ RXCLK ~~~ RXCLKC0 ~~~ RXCLKC1 ~~~ RXSUP ~~~ RXI2C ~~~ RXMUX ~~~ CAPSEL ~~~ BUF
  BUF ~~~ CODEC ~~~ CODECSUP ~~~ CODECI2C ~~~ CODECBCLK ~~~ CODECWS ~~~ CODECDOUT ~~~ CODECDIN ~~~ SAFE ~~~ SPKSEL ~~~ PAM
  PAM ~~~ SPKBEADP ~~~ SPKBEADN ~~~ SPK ~~~ MIC ~~~ MICFILT ~~~ AGNDLINK ~~~ HPJACK ~~~ HPESD ~~~ TXSEL
  TXSEL ~~~ SA ~~~ VOICESUP ~~~ VOICEIOSW ~~~ VOICEPTT ~~~ VOICEUART ~~~ VOICEHL ~~~ VOICEAUDIO ~~~ LCDCON ~~~ LCD ~~~ LCDTDDI ~~~ LCDLBULK ~~~ LCDLHF ~~~ LCDRPD ~~~ TPRPD ~~~ BLEFUSE ~~~ BLILIM ~~~ BLIN ~~~ BLOUT ~~~ BLOUTHF
  BLOUTHF ~~~ BLFPU ~~~ BLR ~~~ BLQ ~~~ BLGR ~~~ BLGPD ~~~ SD ~~~ SDHBUF ~~~ SDMBUF ~~~ SDESDA ~~~ SDESDB
  SDESDB ~~~ SDINCAP ~~~ SDBULK ~~~ SDHFCAP ~~~ SDHBUFCAP ~~~ SDMBUFCAP ~~~ SDONPD ~~~ SDSCKPD ~~~ SDD0PU ~~~ SDD1PU
  SDD1PU ~~~ SDHCS ~~~ LCDHCS ~~~ SDCPUCMD ~~~ SDCPUD0 ~~~ SDCPUD1 ~~~ SDCPUD2 ~~~ SDCPUD3
  SDCPUD3 ~~~ SDSCKR ~~~ SDCMDR ~~~ SDCSR ~~~ SDMISOR ~~~ SDDETR ~~~ SDDETPU ~~~ SDDETC ~~~ UNIT ~~~ C5 ~~~ IR0 ~~~ IR1 ~~~ IRTX
  IRTX ~~~ RP ~~~ NRF0 ~~~ NRF1 ~~~ NRF2 ~~~ CC ~~~ SA
  SA ~~~ ISO ~~~ CAPDOCK ~~~ U214 ~~~ PTTSW ~~~ STOPSW ~~~ REARMSW ~~~ STOPPU ~~~ STOPC ~~~ REARMPU ~~~ REARMC ~~~ SAFEESD
  SAFEESD ~~~ STOPLOOP ~~~ REARMRAW ~~~ SUP ~~~ COND ~~~ POROR ~~~ LATCH ~~~ RSTBUF
  RSTBUF ~~~ GATEA ~~~ GATEB ~~~ PTTOR ~~~ STOPLEDR ~~~ STOPLED
  STOPLED ~~~ DS3 ~~~ DC5 ~~~ DN0 ~~~ DN1 ~~~ DN2
  DN2 ~~~ DCC ~~~ DVOICE ~~~ DIR ~~~ CMPA ~~~ CMPB
  CMPB ~~~ EVMASK ~~~ OR0 ~~~ OR1 ~~~ OR2 ~~~ OR3 ~~~ ANYLED
  USBC -->|"сырой VBUS к VBUS + VBUS_IN"| PDCTRL
  USBC -->|"шунтирующая защита VBUS"| VBUSPROT
  USBC <-->|"CC1/CC2 + D+/D-"| PORTPROT
  PORTPROT <-->|"защищённая D+"| PORTDPR <-->|"Full-Speed GPIO20"| S3
  PORTPROT <-->|"защищённая D-"| PORTDMR <-->|"Full-Speed GPIO19"| S3
  PORTPROT <-->|"защищённые CC1/CC2"| PDCTRL
  PORTPROT -->|"bias 100 нФ / 100 В"| PORTVBIAS
  PDCTRL -->|"LDO_3V3"| PORTVPWR --> PORTPROT
  PDCTRL --> PORTFLTPU --> PORTPROT
  PDCTRL <-->|"локальная I²C, boot image"| PDCFG
  PDCTRL <-->|"защищённый VBUS + локальные I²C/IRQ"| CHARGER
  S3 <-->|"SYS I²C0 + общий wired-low IRQ"| PDCTRL
  PDCTRL -->|"энергия VIN_3V3 / внутренних LDO"| PVINCAP
  PDCTRL --> PL3CAP
  PDCTRL --> PL1CAP
  PDCTRL -->|"номинально 88 мкФ PPHV"| PPHVC0
  PDCTRL --> PPHVC1
  PDCTRL --> PPHVC2
  PDCTRL --> PPHVC3
  PDCTRL -->|"энергия VBUS dead-battery"| PVBUSCAP
  PDCTRL -->|"шунты CC1 / CC2"| PCC1CAP
  PDCTRL --> PCC2CAP
  PDCTRL -->|"bypass питания EEPROM"| PEECAP --> PDCFG
  PDCTRL -->|"reset-high open-drain WP"| PEEWPPU --> PDCFG
  PDCTRL -->|"pull-up полной локальной I²C"| PLSCLPU --> PDCFG
  PDCTRL --> PLSDAPU --> CHARGER
  S3 -->|"pull-up полной host I²C/IRQ"| PHSCLPU --> PDCTRL
  S3 --> PHSDAPU --> PDCTRL
  S3 --> PIRQPU --> PDCTRL
  CHARGER -->|"SW1/SW2"| CHL
  CHARGER -->|"bulk/HF VBUS"| CVB0
  CHARGER --> CVB1
  CHARGER --> CVBHF
  CHARGER -->|"bulk/HF PMID"| CPM0
  CHARGER --> CPM1
  CHARGER --> CPM2
  CHARGER --> CPMHF
  CHARGER -->|"bulk/HF SYS"| CSYS0
  CHARGER --> CSYS1
  CHARGER --> CSYS2
  CHARGER --> CSYS3
  CHARGER --> CSYS4
  CHARGER --> CSYSHF
  CHARGER -->|"bulk BAT"| CBAT0
  CHARGER --> CBAT1
  CHARGER -->|"BTST1/SW1"| CBT1
  CHARGER -->|"BTST2/SW2"| CBT2
  CHARGER -->|"REGN"| CREGN
  CHARGER -->|"SDRV на землю"| CSDRV
  CHARGER -->|"POR 2S/750 кГц"| CPROG
  PACKFET -->|"sense допущенного BATP"| CBATP --> CHARGER
  CHARGER -->|"прямой TS без ignore"| CTSU --> CTSN
  CTSN --> CTSL
  CHARGER -->|"аппаратный предел 2,71…3,29 А"| CILU --> CILL
  PDCTRL --> CINTPU --> CHARGER
  CHARGER -->|"reset-high CE от REGN"| CCEPU --> CHARGER
  CELL0 -->|"поляризованный слот 0"| HOLDER
  CELL1 -->|"поляризованный слот 1"| HOLDER
  HOLDER -->|"независимые контакты слота 0"| FUSE0 --> PACKGAUGE
  NTC0 -->|"TH1"| PACKGAUGE
  HOLDER -->|"независимые контакты слота 1"| FUSE1 --> PACKGAUGE
  NTC1 -->|"TH2"| PACKGAUGE
  NTC0 -.->|"изолированный поджатый контакт с серединой банки"| CELL0
  NTC1 -.->|"изолированный поджатый контакт с серединой банки"| CELL1
  CTSN -.->|"одна индексированная позиция на худшем по нагреву слоте"| HOLDER
  SHUNT -->|"Kelvin evidence CSP/CSN"| PACKGAUGE
  PACKGAUGE -->|"CHG/DIS gates; без prequal"| PACKFET
  PACKFET <-->|"защищённая силовая граница 2S"| CHARGER
  PACKHOLD -->|"ALRT low по умолчанию"| PACKGAUGE
  PACKADM -->|"явное снятие hold"| PACKHOLD
  PACKGAUGE -->|"AOLDO"| SUPPLYOR --> PACKADM
  SYSDIODE -->|"admitted 3V3"| PACKADM
  PACKGAUGE <-->|"локальная I²C + fault"| PACKADM
  PACKADM <-->|"SYS I²C0 + общий IRQ"| S3
  PACKADM -->|"фронт PA22"| DIAGTMR
  PACKADM --> DIAGTRPD
  SUPPLYOR -->|"питание admission"| DIAGTMR
  DIAGTMR -->|"169 кОм / 220 нФ; ≤50 мс"| DIAGTR --> DIAGTC
  DIAGTMR -->|"спад Q; аппаратный cooldown ≥350 мс"| DIAGLR --> DIAGLC
  DIAGTMR --> DIAGBP
  DIAGTMR -->|"ограниченный gate pulse"| DIAGQ
  DIAGTMR --> DIAGGPD
  FUSE1 -->|"полный stack после fuse; суммарно 10 Ом"| DIAGR0 --> DIAGQ
  FUSE1 --> DIAGR1 --> DIAGQ
  FUSE0 --> MIDADC0 --> MIDADC1 -->|"PA25/A2"| PACKADM
  PACKADM --> MIDADCB
  PACKADM --> MIDADCC
  FUSE1 --> STACKADC0 --> STACKADC1 --> STACKADC2 --> STACKADC3 --> STACKADC4 -->|"PA26/A1"| PACKADM
  PACKADM --> STACKADCB
  PACKADM --> STACKADCC
  CHARGER -->|"SYS"| AONBUCK --> AONL -->|"AON_RAW_3V3"| AONFUSE -->|"AON_SAFE_3V3"| SUP
  AONFUSE -->|"AON_SAFE_3V3, runtime source"| PVINCAP
  AONBUCK -->|"MODE/S-CONF"| AONMODE
  CHARGER -->|"локальный bypass SYS"| AONIN
  AONL -->|"локальный сырой выход"| AONOUT
  AONL --> AONFIN
  AONFUSE -->|"ILIM"| AONRILIM
  AONL -->|"делитель OVLO"| AONOVT --> AONOVB
  AONFUSE --> AONFOUT
  AONFUSE -->|"источник pull-up PG"| AONPGPU --> AONBUCK
  AONPGPU -->|"AON_PG_N к MR_N"| SUP
  AONFUSE -->|"pull-up POR"| PORPU --> SUP
  SUP -->|"задержанный POR_N включает main"| MAINBUCK
  CHARGER -->|"SYS"| MAINBUCK --> MAINL -->|"MAIN_RAW_3V3"| MAINFUSE -->|"3V3_MAIN"| S3
  CHARGER -->|"локальный bulk SYS"| MAININ
  CHARGER -->|"локальный HF SYS"| MAINHF
  MAINL -->|"feedback"| MAINFBT --> MAINFBB
  MAINL -->|"feed-forward"| MAINFF
  MAINL -->|"локальный выходной банк"| MAINOUT0
  MAINL -->|"локальный выходной банк"| MAINOUT1
  MAINFUSE -->|"ILM"| MAINRILM
  MAINFUSE -->|"dVdt"| MAINDVDT
  MAINFUSE -->|"ITIMER"| MAINIT
  MAINL -->|"делитель OVLO"| MAINOVT --> MAINOVB
  MAINFUSE -->|"делитель PGTH"| MAINPGT --> MAINPGB
  MAINFUSE --> MAINFOUT
  MAINBUCK -->|"100-кОм fail-low EN"| MAINENPD
  MAINFUSE -->|"защищённый PG в fault aggregate"| SLOW
  MAINFUSE -->|"источник pull-up POWER_FAULT_N"| FAULTPU --> SLOW
  MAINFUSE -->|"3V3_MAIN: VCCI/VCCP"| SLOW
  MAINFUSE --> SLOWVCI --> SLOW
  MAINFUSE --> SLOWVCP --> SLOW
  MAINFUSE --> SLOWBULK --> SLOW
  MAINFUSE --> SLOWRSTPU --> SLOWRST --> SLOW
  MAINFUSE --> C5
  MAINFUSE --> RP
  MAINFUSE --> SWNRF
  MAINFUSE --> SWCC
  MAINFUSE --> SWSD
  MAINFUSE --> SWCODEC
  MAINFUSE --> SWRX
  CHARGER -->|"SYS"| VOICEBUCK --> VOICEL -->|"VVOICE_RAW_4V"| VOICEFUSE -->|"защищённые 4,0 В"| SA
  CHARGER -->|"локальный bulk SYS"| VOICEIN
  CHARGER -->|"локальный HF SYS"| VOICEHF
  VOICEL -->|"feedback"| VOICEFBT --> VOICEFBB
  VOICEL -->|"feed-forward"| VOICEFF
  VOICEL -->|"локальный выходной банк"| VOICEOUT0
  VOICEL -->|"локальный выходной банк"| VOICEOUT1
  VOICEFUSE -->|"ILM"| VOICERILIM
  VOICEFUSE -->|"dVdt"| VOICEDVDT
  VOICEFUSE -->|"ITIMER"| VOICEIT
  VOICEL -->|"делитель OVLO"| VOICEOVT --> VOICEOVB
  VOICEFUSE -->|"делитель PGTH"| VOICEPGT --> VOICEPGB
  VOICEFUSE --> VOICEFOUT
  VOICEBUCK -->|"fail-low EN"| VOICEENPD
  MAINFUSE -->|"pull-up PG"| VOICEPGPU --> VOICEFUSE
  GATEB -->|"EN"| VOICEPGBR --> VOICEPGQ
  VOICEFUSE -->|"защищённый PG"| VOICEPGQ -->|"квалифицированный POWER_FAULT_N"| SLOW
  CHARGER -->|"SYS"| EXTBUCK --> EXTL --> EXTFUSE -->|"защищённые фиксированные 5,0 В"| U214
  CHARGER -->|"локальный bulk SYS"| EXTBUCKIN
  CHARGER -->|"локальный HF SYS"| EXTBUCKHF
  EXTL -->|"feedback"| EXTBUCKFBT --> EXTBUCKFBB
  EXTL -->|"feed-forward"| EXTBUCKFF
  EXTL -->|"локальный выходной банк"| EXTBUCKOUT0
  EXTL -->|"локальный выходной банк"| EXTBUCKOUT1
  EXTBUCK -->|"fail-low EN"| EXTENPD
  MAINFUSE -->|"pull-up PG"| EXTPGPU --> EXTBUCK
  GATEB -->|"EN"| EXTPGBR --> EXTPGQ
  EXTBUCK -->|"PG"| EXTPGQ -->|"квалифицированный POWER_FAULT_N"| SLOW
  EXTFUSE -->|"ILM"| EXTRILM
  EXTFUSE -->|"dVdt"| EXTDVDT
  EXTFUSE -->|"ITIMER"| EXTITIMER
  EXTL -->|"делитель OVLO"| EXTOVLOT --> EXTOVLOB
  EXTL --> EXTINCAP
  EXTFUSE --> EXTOUTCAP
  EXTFUSE --> EXTBLEED
  SWNRF --> NRF0
  SWNRF --> NRF1
  SWNRF --> NRF2
  SWCC --> CC
  MAINFUSE --> SDINCAP
  SWSD -->|"включаемые 3,3 В + QOD"| SD
  SWSD --> SDBULK
  SWSD --> SDHFCAP
  SWSD -->|"VCC с Ioff"| SDHBUF
  SWSD -->|"VCC с Ioff"| SDMBUF
  SWSD --> SDHBUFCAP
  SWSD --> SDMBUFCAP
  SDONPD -->|"reset off"| SWSD
  SWCODEC --> CODEC
  SWRX --> SI
  S3 <-->|"1-bit SDIO"| C5
  S3 <-->|"dedicated SPI3 + alert"| RP
  S3 <-->|"I²C0 + interrupt"| SLOW
  LATCH -->|"полярность Q сохранена"| SLOWSTOPISO --> SLOW
  AONFUSE --> SLOWSTOPBP --> SLOWSTOPISO
  MAINFUSE --> SLOWSTOPPU --> SLOW
  CMPA -->|"active-low полярность сохранена"| SLOWEVISO --> SLOW
  AONFUSE --> SLOWEVBP --> SLOWEVISO
  MAINFUSE --> SLOWEVPU --> SLOW
  S3 -->|"direct QSPI + touch"| LCDCON
  LCDCON <-->|"40-контактный FPC; HIL физического сопряжения открыт"| LCD
  LCD -->|"встроенный exact COG"| LCDTDDI
  LCDTDDI -->|"TP_INT low при touch"| TPIRQRAW
  TPIRQPU -->|"10 кОм к 3V3_MAIN"| TPIRQRAW
  TPIRQRAW --> TPIRQ -->|"open-drain SYS_INT_N"| S3
  TPIRQBP --> TPIRQ
  SLOW -->|"P06/P07 release reset"| LCDCON
  S3 <-->|"SYS I²C0 + wired-low IRQ"| UIMATRIX
  UIMBP --> UIMATRIX
  UIR0PD -->|"reset/idle low"| UIMATRIX
  UIR1PD -->|"reset/idle low"| UIMATRIX
  UIR2PD -->|"reset/idle low"| UIMATRIX
  UIR3PD -->|"reset/idle low"| UIMATRIX
  UIMATRIX --> UIMESD
  UIMATRIX --> UIDUP --> UIUP -->|"P4 столбец 0"| UIMATRIX
  UIMATRIX --> UIDDN --> UIDOWN -->|"P5 столбец 1"| UIMATRIX
  UIMATRIX --> UIDLEFT --> UILEFT -->|"P6 столбец 2"| UIMATRIX
  UIMATRIX --> UIDRIGHT --> UIRIGHT -->|"P4 столбец 0"| UIMATRIX
  UIMATRIX --> UIDOK --> UIOK -->|"P5 столбец 1"| UIMATRIX
  UIMATRIX --> UIDBACK --> UIBACK -->|"P6 столбец 2"| UIMATRIX
  UIMATRIX --> UIDOPT --> UIOPT -->|"P4 столбец 0"| UIMATRIX
  UIMATRIX --> UIDF1 --> UIF1 -->|"P5 столбец 1"| UIMATRIX
  UIMATRIX --> UIDF2 --> UIF2 -->|"P6 столбец 2"| UIMATRIX
  UIMATRIX --> UIDENC -->|"нажатие"| ENC -->|"P4 столбец 0"| UIMATRIX
  UIC0PU --> UIMATRIX
  UIC1PU --> UIMATRIX
  UIC2PU --> UIMATRIX
  ENCAPU --> ENC
  ENCBPU --> ENC
  ENC --> ENCPTTESD
  ENC -->|"GPIO39/GPIO47 PCNT0 quadrature"| S3
  LCDRPD -->|"RESX по умолчанию low"| LCDCON
  TPRPD -->|"TP_RESXP по умолчанию low"| LCDCON
  MAINFUSE -->|"защищённые 3,3 В логики"| LCDLBULK --> LCDCON
  MAINFUSE --> LCDLHF --> LCDCON
  MAINFUSE -->|"ветвь LEDA"| BLEFUSE --> LCDCON
  BLEFUSE --> BLILIM
  BLEFUSE --> BLIN
  BLEFUSE --> BLOUT
  BLEFUSE --> BLOUTHF
  BLFPU --> BLEFUSE
  LCDCON -->|"3 × LEDK"| BLR --> BLQ
  S3 -->|"GPIO40 PWM"| BLGR --> BLQ
  BLGPD -->|"reset off"| BLQ
  SDSCKPD -->|"reset low"| S3
  MAINFUSE --> SDD0PU --> S3
  MAINFUSE --> SDD1PU --> S3
  MAINFUSE --> SDHCS --> S3
  MAINFUSE --> LCDHCS --> S3
  S3 -->|"общие SCK/CMD + CS карты"| SDHBUF
  SDHBUF -->|"SCK"| SDSCKR --> SD
  SDHBUF -->|"CMD"| SDCMDR --> SD
  SDHBUF -->|"CS"| SDCSR --> SD
  SD -->|"DAT0 только при CS low"| SDMBUF --> SDMISOR --> S3
  S3 -->|"SD_CS_N разрешает выход"| SDMBUF
  SWSD --> SDCPUCMD --> SD
  SWSD --> SDCPUD0 --> SD
  SWSD --> SDCPUD1 --> SD
  SWSD --> SDCPUD2 --> SD
  SWSD --> SDCPUD3 --> SD
  SDESDA -.->|"shunt ESD для CLK/CMD/DAT0/DAT3"| SD
  SDESDB -.->|"shunt ESD для DAT1/DAT2/VDD/detect"| SD
  SD -->|"всегда читаемый detect"| SDDETR --> SLOW
  MAINFUSE --> SDDETPU --> SLOW
  SLOW --> SDDETC
  S3 <-->|"host-сторона I²C0"| CODECI2C <-->|"локальная шина с питанием; 0x19"| CODEC
  S3 -->|"I²S0 BCLK"| CODECBCLK --> CODEC
  S3 -->|"I²S0 WS"| CODECWS --> CODEC
  S3 -->|"I²S0 воспроизведение"| CODECDOUT --> CODEC
  CODEC -->|"I²S0 запись"| CODECDIN --> S3
  S3 <-->|"host-сторона I²C0"| RXI2C <-->|"локальная шина с питанием"| SI
  S3 <-->|"profile port"| UNIT
  RXCLK --> SI
  RXCLKC0 --> SI
  RXCLKC1 --> SI
  RXSUP -->|"reset и задержка интерфейсов 200 мс"| RXI2C
  CODECSUP -->|"задержка интерфейсов 200 мс"| CODECI2C
  CODECSUP --> CODECBCLK
  SI --> RXMUX --> CAPSEL --> BUF --> CODEC
  MIC --> CAPSEL
  SA -->|"AFOUT"| VOICEAUDIO --> RXMUX
  CODEC --> SPKSEL --> PAM
  PAM --> SPKBEADP --> SPK
  PAM --> SPKBEADN --> SPK
  CODEC --> HPJACK --> HPESD
  CODEC --> TXSEL --> VOICEAUDIO -->|"MIC_IN"| SA
  MICFILT --> MIC --> TXSEL
  AGNDLINK --> CODEC
  S3 -->|"GPIO6 AUDIO_ARM"| SAFE
  SLOW -->|"P00 запись; P01 динамик; P02 наушники; P11/P12 селекторы"| SAFE
  SAFE --> SPKSEL
  SAFE --> TXSEL
  VOICESUP --> VOICEIOSW --> VOICEAUDIO
  VOICEIOSW --> VOICEPTT
  VOICEIOSW --> VOICEUART
  SLOW -->|"P14 запрос low/open мощности"| VOICEHL --> SA
  C5 -->|"RMT RX0"| IR0
  C5 -->|"RMT RX1"| IR1
  RP <-->|"PIO0 SM0"| NRF0
  RP <-->|"PIO0 SM1"| NRF1
  RP <-->|"PIO0 SM2"| NRF2
  RP <-->|"PIO0 SM3"| CC
  RP <-->|"UART0/PTT request"| SA
  PTTPU -->|"10 кОм к 3V3_MAIN"| PTTRAW
  PTTC -->|"100 нФ к power ground"| PTTRAW
  PTTSW -->|"NO-контакт к power ground"| PTTRAW
  PTTRAW --> ENCPTTESD
  PTTRAW -->|"прямой GPIO21 через 1 кОм; никогда не входит в UI-матрицу"| PTTR --> RP
  RP <-->|"PIO1/UART1"| CAPDOCK
  RP <-->|"I²C0"| ISO
  ISO <-->|"isolated I²C"| CAPDOCK
  CAPDOCK <-->|"14-pin Cap-Bus"| U214
  STOPPU -->|"10 кОм к AON_SAFE_3V3"| STOPLOOP
  STOPC -->|"10 нФ к safety ground"| STOPLOOP
  STOPSW -->|"COM+NC к safety ground"| STOPLOOP
  STOPLOOP --> SAFEESD
  STOPLOOP --> COND --> LATCH
  REARMPU -->|"47 кОм к AON_SAFE_3V3"| REARMRAW
  REARMC -->|"100 нФ к safety ground"| REARMRAW
  REARMSW -->|"NO-контакт к safety ground"| REARMRAW
  REARMRAW --> SAFEESD
  REARMRAW --> COND
  SUP --> POROR --> LATCH
  STOPLOOP --> POROR
  LATCH -->|"RUN_PERMIT"| RSTBUF
  RSTBUF -->|"CHIP_PU"| S3
  RSTBUF -->|"CHIP_PU"| C5
  RSTBUF -->|"RUN"| RP
  LATCH --> GATEA
  LATCH --> GATEB
  LATCH --> PTTOR
  LATCH --> STOPLEDR --> STOPLED
  RP -->|"3×CE + nRF rail requests"| GATEA
  RP -->|"CC rail request"| GATEB
  C5 -->|"IR carrier request"| GATEB
  SLOW -->|"voice/accessory rail requests"| GATEB
  RP -->|"PTT request"| PTTOR --> VOICEPTT --> SA
  GATEA --> NRF0
  GATEA --> NRF1
  GATEA --> NRF2
  GATEA --> SWNRF
  GATEB --> SWCC
  GATEB --> VOICEBUCK
  GATEB --> IRTX
  GATEB --> EXTBUCK
  GATEB --> EXTFUSE
  S3 --> DS3 --> CMPA
  C5 --> DC5 --> CMPA
  NRF0 --> DN0 --> CMPA
  NRF1 --> DN1 --> CMPA
  NRF2 --> DN2 --> CMPB
  CC --> DCC --> CMPB
  SA --> DVOICE --> CMPB
  IRTX --> DIR --> CMPB
  CMPA --> EVMASK
  CMPB --> EVMASK
  CMPA --> OR0
  CMPA --> OR1
  CMPB --> OR2
  CMPB --> OR3
  OR0 --> ANYLED
  OR1 --> ANYLED
  OR2 --> ANYLED
  OR3 --> ANYLED
  EVMASK <-->|"local I²C0 source mask"| RP
  ANYLED -->|"GPIO22 RP_ANY_TX_N"| RP
```

<details>
<summary><strong>Принципиальная распиновка</strong></summary>

- **S3↔C5:** S3 `GPIO10,GPIO11,GPIO12,GPIO13`; C5
  `GPIO7,GPIO8,GPIO9,GPIO10` — выделенная 1-bit SDIO.
- **S3↔RP:** S3 `GPIO3,GPIO9,GPIO14,GPIO21,GPIO48`; RP
  `GPIO19,GPIO24,GPIO25,GPIO26,GPIO27` — выделенная SPI + alert.
- **Дисплей и microSD:** S3
  `GPIO4,GPIO5,GPIO35,GPIO36,GPIO38,GPIO40,GPIO41,GPIO42` — direct QSPI
  и единственная планируемая high-rate shared pair. Ioff-буферы со стороны
  карты и CS-gated возврат MISO исключают конфликт выключенной карты с D1 экрана.
- **Локальные органы управления:** S3 `GPIO39,GPIO47` — выделенные входы
  quadrature PCNT0. Отдельный `TCA9534APWR` `P0…P6` сканирует
  диодно-изолированную матрицу 4×3 с D-pad/OK, BACK, OPT, F1, F2 и нажатием
  энкодера; `P7` — локальный резерв. В reset/idle все строки низкие, поэтому
  любая кнопка вызывает wired-low interrupt. PTT подключён прямо к RP `GPIO21`,
  а STOP и RE-ARM остаются независимыми AON-трактами.
- **Главный slow I/O:** точный `TCA6424ARGJR` работает по адресу `0x22` от
  защищённого `3V3_MAIN`; RESET доступен fixture, а продукт умеет полностью
  перезапустить main-rail. Наблюдение STOP/evidence переходит из AON через
  отдельные open-drain буферы и не подпитывает выключенный расширитель.
- **Audio и Si4732:** S3 `GPIO1,GPIO2,GPIO15,GPIO16,GPIO17,GPIO18` — I²S0 и
  локальная I²C0 через физическую power-valid развязку. Slow I/O `P00,P01,P02`
  выбирают запись RX/микрофона, включают выключенный в reset динамик и
  определяют отсутствие наушников. PD-контроллер также использует ограниченную
  host-шину и общий wired-low system IRQ, не занимая нового GPIO S3.
- **M5 Unit:** S3 `GPIO7,GPIO8` — отдельный конфигурируемый profile-port.
- **IR:** C5 `GPIO0,GPIO1,GPIO4,GPIO6,GPIO24` — два RX, TX, power и evidence.
- **nRF24 #0:** RP `GPIO0,GPIO1,GPIO2,GPIO30,GPIO31,GPIO32`.
- **nRF24 #1:** RP `GPIO3,GPIO4,GPIO5,GPIO33,GPIO34,GPIO35`.
- **nRF24 #2:** RP `GPIO6,GPIO7,GPIO8,GPIO36,GPIO37,GPIO38`.
- **CC1101:** RP `GPIO9,GPIO10,GPIO11,GPIO23,GPIO39,GPIO42,GPIO43`.
- **SA518/PTT:** RP `GPIO16,GPIO17,GPIO18,GPIO20,GPIO21`; восьмибитная маска
  evidence делит локальную RP I²C0, а аппаратный aggregate использует `GPIO22`.
- **U214 LoRa/GNSS:** RP
  `GPIO12,GPIO13,GPIO14,GPIO28,GPIO29,GPIO40,GPIO41,GPIO44,GPIO45,GPIO46,GPIO47`.
- **Ресурсный итог:** S3 `33 used / 3 reserved / 0 free`, C5 `14/6/1`, RP
  `48/0/0`, main slow I/O `21/0/3`, UI matrix I/O `7/1/0`. Независимые
  SWD/USB/RUN/BOOTSEL не входят в этот GPIO-бюджет.

[Полная карта физических контактов и сетей](docs/review/architecture/generated/G2F-3I-principled-pinout.md)

</details>

## Конструкция и органы управления

- Экран расположен вертикально; водопад обновляется небольшими областями и не
  блокирует обслуживание радио.
- Сборка QSPI/touch подключается через кандидат 40-контактного ZIF, имеет
  reset-low состояния по умолчанию, локальную развязку логики и отдельно
  защищённую защёлкиваемым ключом ШИМ-подсветку. Внутри находится единый exact
  `Sitronix ST77922` display/touch TDDI: touch использует I²C-адрес `0x38`, а
  его active-low interrupt входит в общую линию через подтянутый
  non-inverting open-drain buffer. Окончательная ориентация разъёма требует
  реального шлейфа экрана: электрическая карта не подменяет механическую
  квалификацию.
- Push-push microSD получает изолированное включаемое питание, безопасные
  reset-состояния и всегда читаемый card-detect. После каждого цикла питания
  прошивка переводит карту в SPI mode до возобновления обмена с дисплеем.
  Размещение гнезда, доступ к карте, ресурс носителей и fault-тесты вставки и
  извлечения остаются физическим HIL.
- Девять подписанных антенных портов сохраняют однозначную связь между
  разъёмом, трактом и активным профилем антенны.
- Съёмный U214 устанавливается поперёк задней стороны над аккумуляторами; его
  собственные антенны и разъёмы остаются доступными.
- Полный локальный набор сохранён: направления D-pad и OK, BACK, OPT, F1, F2,
  энкодер с нажатием, отдельный PTT с удержанием, аппаратный STOP и утопленный
  RE-ARM. Ни touch, ни телефон не заменяют эти органы управления.
- Девять дискретных обычных кнопок, PTT и RE-ARM используют exact low-current
  `Y78B23214FP`; gold-clad `AEQ10410` даёт нормально-замкнутый контакт STOP.
  У matrix, encoder/PTT и safety inputs отдельные exact ESD arrays, причём
  защита STOP/RE-ARM возвращается только в safety ground.
- Физические PTT, STOP и утопленный RE-ARM являются разными органами управления.
  STOP имеет независимую индикацию и не зависит от экрана.
- Разъёмы прошивки и диагностики доступны при собранном прототипе и не требуют
  исправной основной прошивки.

## Безопасность и честность измерений

- Каждый передатчик и лабораторное действие стартуют разоружёнными после
  включения, reset, watchdog, brownout или обновления.
- Первая передача использует консервативный профиль. Максимальная мощность
  появляется только после явного выбора для текущего сценария.
- Физический STOP доминирует над firmware и межпроцессорной связью. Отпускание
  STOP не восстанавливает прежние цель, канал, мощность или TX-lease.
- Нормально-замкнутая STOP-петля асинхронно защёлкивает reset всех трёх
  вычислительных доменов и независимо блокирует nRF CE, radio/accessory rails,
  voice PTT и IR waveform. Только новое нажатие утопленного RE-ARM или полное
  выключение питания начинают новый TX-off boot.
- Семь отдельных RF detectors и один оптический IR detector формируют восемь
  source-specific состояний и diode-isolated красный физический индикатор
  `ANY TX`. Аксессуар без собственного qualified evidence остаётся `Unknown`.
- Команда передачи, ток тракта, сообщение самого радио и независимое
  фактическое evidence отображаются как разные состояния. Неизвестное не
  превращается в успешное или безопасное.
- Неиспользуемые интерфейсы обесточиваются или переводятся в проверенное тихое
  состояние, чтобы не тормозить и не заглушать активную группу сигналов.
- Снижение стоимости допустимо только при сохранении функций, производительности,
  безопасности, надёжности, автономности, ремонтопригодности и тестируемости.

## Границы продукта

В базовый продукт не входят 6 ГГц/Wi-Fi 6E, generic USB host, персональный
FIDO/U2F-аутентификатор, встроенная клавиатура, мотор и встроенный IMU.
BadUSB/DuckyScript может существовать только как необязательная программная
функция Контролируемой зоны поверх уже имеющегося USB device-пути и не влияет
на аппаратную архитектуру радио-прибора.

## Документация проекта

- [Текущее состояние аппаратной проработки](docs/status/current-state.ru.md)
- [Принципиальная карта контактов](docs/review/architecture/PIN-0003-g2f-3i-principled-pinout.md)
- [Полный журнал требований, решений и проверок](docs/review/README.md)
- [Целевое описание прошивки](https://github.com/anton-vinogradov/esp32-leshy2-firmware/blob/main/README.ru.md)
