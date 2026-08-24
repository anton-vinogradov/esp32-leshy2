# Аварийное отключение Leshy2

[English](fault-shutdown.md) · [На главную](../README.ru.md) · [Тихое состояние](quiet-state.ru.md)

Аварийное выключение не зависит от S3, меню или основного приложения и не перезапускает передатчики автоматически.

| Источник | Аппаратный результат |
|---|---|
| RUN переведён в KILL или провод оборван | асинхронный latch; TX/power gates safe; C5/RP reset |
| heartbeat отсутствует/неверен | TPS3435 либо lease-monitor защёлкивает fault |
| TX без действующей lease | physical evidence защёлкивает fault |
| POWER или RF/VOICE перегрет | всё опасное off; cool UI показывает причину |
| UI/DISPLAY перегрет | UI тоже off; остаётся независимый янтарный FAULT LED |
| AON brownout | supervisor и off-safe pulls удерживают безопасное состояние |

## Результат H2.5.5

✅ **Проведено ревью:** 56 safety-цепей проверены по полным KiCad-netlist; все 33 требуемые точки диагностики теперь существуют как медь.

[Машинное evidence](../hardware/ecad/generated/H2-REV55-fault-kill.json).
