# USB ↔ pack handover and brownout · historical R1

[Русский](power-handover.ru.md) · [Home](../README.md) · [H3.2 result](power-transition-result.md)

Seven transitions cover USB attach/detach, DPM, USB without a pack, KILL while USB remains, AON brownout and external reverse drive. BQ25798 reduces charge first and then permits pack supplement; ordinary handover does not need OTG/backup mode.

A source transition cannot enable RF: loss of AON clears permit, while SYS, USB and BATFET have no path to the latch clock. If no healthy pack exists, loss of the sole USB source is an expected safe shutdown rather than a hold-up promise.

The absolute SYS droop inside the proprietary BQ25798 control loop is not invented from the datasheet. It is an explicit H8 oscilloscope acceptance case at the H3.1 worst profiles.

**Status:** `H3.2.2` reviewed; 7/7 transitions pass. [Machine evidence](../hardware/verification/generated/H3-VRF22-handover-brownout.json).
