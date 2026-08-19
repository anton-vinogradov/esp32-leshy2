# FND-0097 — native RF evidence stopped before the real feed

- Status: **corrected on paper by `NAT-0001/DEC-0092`; physical/HIL open**
- Scope: I6 native S3/C5 RF subblock

## Finding

The working design instantiated two `LTC5532ES6#TRMPBF` bodies but connected
them to `abstract:S3-qualified-RF-tap` and `abstract:C5-qualified-RF-tap`.
That did not specify a real exposed module contact, coupling direction,
termination, RF-input DC block, detector gain network or the connector needed
to bring an on-module first-generation U.FL path back onto the PCB. The target
page therefore showed detector MPNs while the claimed actual-TX evidence still
had no buildable RF source.

## Correction

- both module datasheets prove an actual first-generation external-antenna
  receptacle; C5 `ANT2` is an exposed pad but remains default-disabled;
- each `ANT/ANT1` now reaches a separate exact board-side
  `Hirose U.FL-R-SMT-1(10)` through a placement-length-qualified jumper;
- one exact `CP0603Q5425ENTR` per path takes the forward sample after the
  module connector and before the dedicated external-SMA boundary;
- all four manufacturer-named coupler lands, its 49.9-Ohm termination and the
  complete LTC5532 support network are machine routes;
- the old abstract tap routes are prohibited by regression test.

The jumper length, exact cable assembly and final RP-SMA MPN cannot be chosen
honestly before physical placement. They remain named gates rather than being
invented from a generic connector label.

