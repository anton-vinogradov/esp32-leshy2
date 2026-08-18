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
- Два IR-приёмника позволяют одновременно надёжно декодировать бытовые команды
  и измерять несущую неизвестного сигнала; отдельный передатчик воспроизводит
  изученные профили.
- Все девять бортовых антенных трактов выведены на собственные внешние порты:
  два RP-SMA для native Wi-Fi и семь standard SMA для остальных трактов.

### Интерфейсы и расширения

- Вертикальный сенсорный IPS-дисплей 3,5 дюйма, `320×480`, подключён прямым QSPI;
  критическое состояние и первый отклик меню появляются не позднее `100 мс`.
- microSD хранит записи эфира, аудио, профили, журналы и экспортируемые данные.
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
- Основной USB-C сохраняет прямые USB2-линии S3 и только принимает питание:
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
  USBC["MPN TBD<br/>основной USB-C: прямые USB2-линии S3 и только приём питания"]
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
  PCC1CAP["GRM1555C1H331JA01J #CC1<br/>конденсатор USB-C CC1: 330 пФ, C0G"]
  PCC2CAP["GRM1555C1H331JA01J #CC2<br/>конденсатор USB-C CC2: 330 пФ, C0G"]
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
  SLOW["TCA6424ARGJR<br/>24-line slow-control and UI expander"]
  LCD["HMX035CTFT-001<br/>3.5-inch QSPI IPS display and capacitive-touch assembly"]
  SD["DM3AT-SF-PEJM5<br/>push-push microSD card connector"]
  SI["Si4732-A10-GS<br/>AM/FM/SW/LW broadcast receiver"]
  CODEC["ES8311<br/>mono ADC/DAC audio codec"]
  RXMUX["SN74LVC1G3157DBVR<br/>receive-audio source selector"]
  BUF["TLV9061IDBVR<br/>active high-impedance capture buffer"]
  SPKSEL["TMUX1136DGSR<br/>dual differential speaker-path selector"]
  TXSEL["TS5A63157DCKR<br/>transmit-audio selector"]
  SAFE["SN74LVC2G08DCUR<br/>reset-safe selector-request gate"]
  PAM["PAM8302AASCR<br/>mono Class-D speaker amplifier"]
  SPK["MPN TBD<br/>internal loudspeaker"]
  MIC["MPN TBD<br/>electret microphone"]
  NRF0["E01-ML01IPX<br/>nRF24-compatible radio #0 compact IPEX reference"]
  NRF1["E01-ML01IPX<br/>nRF24-compatible radio #1 compact IPEX reference"]
  NRF2["E01-ML01IPX<br/>nRF24-compatible radio #2 compact IPEX reference"]
  CC["CC1101RGPR<br/>sub-GHz transceiver"]
  SA["NiceRF SA518<br/>VHF/UHF analog voice transceiver"]
  CAPDOCK["MPN TBD<br/>2×7 female 2.54-mm host Cap-Bus receptacle"]
  U214["M5Stack U214 Cap LoRa-1262<br/>external LoRa/GNSS Cap module"]
  ISO["TCA4307DGKR<br/>external I2C stuck-bus isolator"]
  UNIT["MPN TBD<br/>protected HY2.0-4P M5 Unit connector"]
  IR0["MPN TBD (TSOP38238 screened)<br/>38 kHz demodulating IR receiver"]
  IR1["MPN TBD (TSMP95000 screened)<br/>carrier-learning IR receiver"]
  IRTX["MPN TBD (TSAL6200 screened)<br/>IR transmit LED/driver endpoint"]
  STOPSW["MPN TBD<br/>normally-closed physical STOP control"]
  REARMSW["MPN TBD<br/>normally-open recessed RE-ARM control"]
  SUP["TPS3808G33DBVR<br/>AON rail supervisor and power-on reset"]
  COND["74LVC2G14GW,125<br/>STOP and RE-ARM Schmitt conditioner"]
  POROR["74LVC1G32GV,125<br/>STOP-dominant POR/clear combiner"]
  LATCH["SN74LVC1G74DCUR<br/>asynchronous latched hard STOP"]
  RSTBUF["SN74LVC3G34DCUR<br/>Ioff three-domain reset fan-out"]
  GATEA["SN74LVC08APWR #1<br/>four STOP-dominant nRF request gates"]
  GATEB["SN74LVC08APWR #2<br/>four STOP-dominant rail/IR/accessory gates"]
  PTTOR["74LVC1G32GV,125 #2<br/>active-low voice PTT force-RX gate"]
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
  USBC ~~~ VBUSPROT ~~~ PDCTRL ~~~ PDCFG ~~~ PVINCAP ~~~ PL3CAP ~~~ PL1CAP ~~~ PPHVC0 ~~~ PPHVC1
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
  SLOW ~~~ SAFE ~~~ SI ~~~ RXMUX ~~~ BUF ~~~ CODEC
  CODEC ~~~ SPKSEL ~~~ PAM ~~~ SPK ~~~ MIC ~~~ TXSEL
  TXSEL ~~~ LCD ~~~ SD ~~~ UNIT ~~~ C5 ~~~ IR0 ~~~ IR1 ~~~ IRTX
  IRTX ~~~ RP ~~~ NRF0 ~~~ NRF1 ~~~ NRF2 ~~~ CC ~~~ SA
  SA ~~~ ISO ~~~ CAPDOCK ~~~ U214 ~~~ STOPSW ~~~ REARMSW
  REARMSW ~~~ SUP ~~~ COND ~~~ POROR ~~~ LATCH ~~~ RSTBUF
  RSTBUF ~~~ GATEA ~~~ GATEB ~~~ PTTOR ~~~ STOPLED
  STOPLED ~~~ DS3 ~~~ DC5 ~~~ DN0 ~~~ DN1 ~~~ DN2
  DN2 ~~~ DCC ~~~ DVOICE ~~~ DIR ~~~ CMPA ~~~ CMPB
  CMPB ~~~ EVMASK ~~~ OR0 ~~~ OR1 ~~~ OR2 ~~~ OR3 ~~~ ANYLED
  USBC -->|"сырой VBUS к VBUS + VBUS_IN"| PDCTRL
  USBC -->|"шунтирующая защита VBUS"| VBUSPROT
  USBC <-->|"D-/D+ напрямую, без ответвления к PD/charger"| S3
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
  SWSD --> SD
  SWCODEC --> CODEC
  SWRX --> SI
  S3 <-->|"1-bit SDIO"| C5
  S3 <-->|"dedicated SPI3 + alert"| RP
  S3 <-->|"I²C0 + interrupt"| SLOW
  S3 -->|"direct QSPI + touch"| LCD
  S3 <-->|"scheduled SPI2"| SD
  S3 <-->|"I²S0 + I²C0"| CODEC
  S3 <-->|"I²C0"| SI
  S3 <-->|"profile port"| UNIT
  SI --> RXMUX --> BUF --> CODEC
  SA -->|"AFOUT"| RXMUX
  CODEC --> SPKSEL --> PAM
  PAM --> SPK
  CODEC --> TXSEL -->|"MIC_IN"| SA
  MIC --> TXSEL
  S3 -->|"GPIO6 AUDIO_ARM"| SAFE
  SLOW -->|"P11/P12 requests"| SAFE
  SAFE --> SPKSEL
  SAFE --> TXSEL
  C5 -->|"RMT RX0"| IR0
  C5 -->|"RMT RX1"| IR1
  RP <-->|"PIO0 SM0"| NRF0
  RP <-->|"PIO0 SM1"| NRF1
  RP <-->|"PIO0 SM2"| NRF2
  RP <-->|"PIO0 SM3"| CC
  RP <-->|"UART0/PTT request"| SA
  RP <-->|"PIO1/UART1"| CAPDOCK
  RP <-->|"I²C0"| ISO
  ISO <-->|"isolated I²C"| CAPDOCK
  CAPDOCK <-->|"14-pin Cap-Bus"| U214
  STOPSW --> COND --> LATCH
  REARMSW --> COND
  SUP --> POROR --> LATCH
  STOPSW --> POROR
  LATCH -->|"RUN_PERMIT"| RSTBUF
  RSTBUF -->|"CHIP_PU"| S3
  RSTBUF -->|"CHIP_PU"| C5
  RSTBUF -->|"RUN"| RP
  LATCH --> GATEA
  LATCH --> GATEB
  LATCH --> PTTOR
  LATCH --> STOPLED
  RP -->|"3×CE + nRF rail requests"| GATEA
  RP -->|"CC rail request"| GATEB
  C5 -->|"IR carrier request"| GATEB
  SLOW -->|"voice/accessory rail requests"| GATEB
  RP -->|"PTT request"| PTTOR --> SA
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
  `GPIO4,GPIO5,GPIO35,GPIO36,GPIO38,GPIO39,GPIO40,GPIO41,GPIO42` — direct QSPI
  и единственная планируемая high-rate shared pair.
- **Audio и Si4732:** S3 `GPIO1,GPIO2,GPIO15,GPIO16,GPIO17,GPIO18` — I²S0 и
  локальная I²C0. PD-контроллер также использует эту ограниченную control-шину
  и общий wired-low system IRQ, не занимая нового GPIO S3.
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
- **Ресурсный итог:** S3 `32 used / 3 reserved / 1 free`, C5 `14/6/1`, RP
  `48/0/0`, slow I/O `24/0/0`. Независимые SWD/USB/RUN/BOOTSEL не входят в
  этот GPIO-бюджет.

[Полная карта физических контактов и сетей](docs/review/architecture/generated/G2F-3I-principled-pinout.md)

</details>

## Конструкция и органы управления

- Экран расположен вертикально; водопад обновляется небольшими областями и не
  блокирует обслуживание радио.
- Девять подписанных антенных портов сохраняют однозначную связь между
  разъёмом, трактом и активным профилем антенны.
- Съёмный U214 устанавливается поперёк задней стороны над аккумуляторами; его
  собственные антенны и разъёмы остаются доступными.
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
