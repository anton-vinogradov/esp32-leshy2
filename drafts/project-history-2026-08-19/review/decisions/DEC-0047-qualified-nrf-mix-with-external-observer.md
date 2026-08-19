# DEC-0047 — qualified internal nRF mix with an external observer

- Статус: **Принято; measurements pending hardware**
- Дата: 2026-08-17
- Основание: владелец подтвердил известную self-desense проблему и заказал
  второй ESP32-DIV, чтобы слушать первый в nRF mode
- Proposal: [`IMP-0039`](../improvements/IMP-0039-three-nrf-full-mix-acceptance.md), вариант A
- Finding: [`FND-0054`](../findings/FND-0054-three-nrf-mix-needs-rf-acceptance.md)
- Fixture plan: [`N24H-0001`](../architecture/N24H-0001-two-device-full-mix-fixture.md)

## Решение

1. Base device реализует все одновременные роли `3R`, `1T+2R`, `2T+1R` и
   `3T` без automatic standby соседей и без скрытых RX gaps.
2. Mixed-TX/RX качество задаётся versioned qualified envelope: exact hardware
   revision, radio identity, channel separation, data rate, TX power, antenna
   pose, distance/path loss и minimum wanted/reference level.
3. Сохранение isolated weak-signal sensitivity при local TX на произвольном
   том же/соседнем канале не является обещанием base device. Unsupported point
   видим в UI/log и не подменяется time-sharing.
4. Два ESP32-DIV образуют ранний `L0 DIV↔DIV` observer/peer стенд. Он
   подтверждает test protocol, actual packets/loss и воспроизводит сам
   self-desense effect, но не закрывает Leshy2 RF/power acceptance: exact
   modules, rails, buses, antennas и enclosure иные.
5. Финальный `T1` HIL использует exact Leshy2 target revision: два сопоставимых
   экземпляра с reversible DUT/observer roles либо Leshy2 DUT и калиброванный
   conducted/OTA peer. Только `T1` закрывает production envelope.
6. Observer не является скрытой обязательной частью готового продукта и не
   «исправляет» внутренний receiver. Он является измерительным peer/fixture;
   base device сохраняет собственный full-mix runtime.
7. Same-channel packet collision является ожидаемым физическим результатом, а
   не firmware failure. Доказательством служит typed loss/collision/desense
   record, а не обещание full duplex одного nRF24.
8. Remote RF heads, conducted paths и shielded room остаются Laboratory
   extensions для более строгих измерений; они не входят в base BOM.

## Последствия

- product-policy blocker `IMP-0039` закрыт вариантом A;
- exact module/antenna/power choice и actual HIL results остаются открыты;
- conceptual placement может идти дальше, но не получает sensitivity pass до
  измерений target geometry;
- каждый peer должен иметь записанную identity/revision/calibration; `L0`
  ESP32-DIV evidence остаётся pre-HIL и не продвигается в target acceptance.
