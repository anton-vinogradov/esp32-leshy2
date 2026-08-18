# DEC-0096 — exact Si4732 dual-input RF endpoint

- Статус: **Принято автоматически в пределах no-loss/cost полномочий; paper subblock проведён ревью**
- Дата: 2026-08-18
- Входы: [`FND-0101`](../findings/FND-0101-si4732-rf-inputs-remained-abstract.md), [`FND-0102`](../findings/FND-0102-si4732-soic16-contact-map-was-shifted.md), [`RXF-0001`](../architecture/RXF-0001-exact-si4732-dual-input-receive-frontend.md)

## Решение

1. Preserve two dedicated receive-only boundaries with no shared RF switch:
   Si4732 physical FMI contact 6 owns FM/SW and AMI contact 8 owns AM/LW;
   contact 7 is the adjacent RFGND return.
2. Protect each exposed boundary with its own exact
   `SESD0402X1UN-0020-090`; K is signal and A receives a shortest RF/ESD return.
3. Use `LQW15AN56NJ00D` 56-nH series matching plus
   `GRM1555C1H102JA01D` 1-nF C0G coupling as the FMI **FM** first target.
   The exact data short assigns SW to the same FMI input, but complete-path SW
   performance stays HIL rather than being inferred from the FM circuit.
4. Use `GRM155R71A474KE01D` 0.47-uF coupling as the AMI first target.
5. Keep AM/LW electrically non-50-Ohm despite the common standard-SMA
   mechanical family. Require a short direct ferrite-loop pod or qualified
   external air-loop/transformer pod; forbid arbitrary long coax.
6. Treat the family application circuit as a measured starting point, not as
   exact-Si4732 performance proof. Every band, antenna/pod and coexistence case
   remains HIL; do not transfer AN383's Si4734/35-only SW-on-AMI circuit to
   Si4732-A10.
7. Change no GPIO, rail, active signal-group rule or TX-safety contract. The
   receiver remains incapable of transmission.

## Последствия

- all nine antenna lines now terminate in reviewed base-side paper electrical
  paths; exact SMA bodies still wait for physical design;
- the former IR documents' statement that IR was the last separate I6 endpoint
  is corrected: both Si4732 RF inputs were still abstract at that time;
- the three new passive SKUs were availability-checked when selected and the
  existing ESD SKU is reused twice;
- the target receiver packaging is the electrically identical tape-and-reel
  `Si4732-A10-GSR`, JLCPCB/LCSC `C2155558`, available for SMT assembly at the
  selection check; out-of-stock tube `C1526102` is not the target order line;
- cost, pin and power budgets do not reopen;
- consolidated I6 coexistence/HIL remains active, and neither KiCad nor the
  paused integrated mockup is authorized.
