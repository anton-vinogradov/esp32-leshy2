# DEC-0047 — qualified internal nRF mix with an external observer

- Статус: **Принято; measurements pending hardware**
- Дата: 2026-08-17
- Основание: владелец подтвердил известную self-desense проблему и заказал
  второй device, чтобы слушать первый в nRF mode
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
4. Второй device становится внешним observer/peer для разработки и HIL. Он
   подтверждает actual packets/emissions первого, подаёт wanted traffic на его
   PRX paths и позволяет менять DUT/observer ролями.
5. Observer не является скрытой обязательной частью готового продукта и не
   «исправляет» внутренний receiver. Он является измерительным peer/fixture;
   base device сохраняет собственный full-mix runtime.
6. Same-channel packet collision является ожидаемым физическим результатом, а
   не firmware failure. Доказательством служит typed loss/collision/desense
   record, а не обещание full duplex одного nRF24.
7. Remote RF heads, conducted paths и shielded room остаются Laboratory
   extensions для более строгих измерений; они не входят в base BOM.

## Последствия

- product-policy blocker `IMP-0039` закрыт вариантом A;
- exact module/antenna/power choice и actual HIL results остаются открыты;
- conceptual placement может идти дальше, но не получает sensitivity pass до
  измерений target geometry;
- второй device должен иметь записанную identity/revision/calibration; generic
  «другой nRF board» без provenance не закрывает acceptance.
