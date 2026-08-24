# Audio electrical verification

[Русский](audio-electrical-verification.ru.md) · [Home](../README.md) · [Schematics](schematics.md) · [Virtual verification](virtual-verification.md)

H3.3.2 checks the complete analog chain: internal/headset microphone and RX → ES8311 → headset/speaker, plus calibrated codec-audio injection into SA518. This is a serial-part calculation; routed-board noise, acoustics and RF immunity remain H8 measurements.

## Capture and microphones

- Independent bias filters give each capsule `1.886410…2.087758 V`; a grounded TRS sleeve no longer pulls down the internal microphone.
- The `33 kΩ` MIC1P/MIC1N parts are removed: they cost `-16.258 dB`. Serial `0 Ω` links now follow the ES8311 reference while PGA remains programmable from `0…30 dB`.
- Safe startup is `0 dB`; loud-input gain is capped at `21 dB` until HIL. Public component noise limits do not replace an assembled-board measurement.

## Headset

The jack is CTIA/AHJ mono dual-ear plus microphone, not a stereo codec. Even with a conservative `17.600 uF` effective capacitor, the lower corner is `239.357 Hz` at 16 ohm and `168.146 Hz` at 32 ohm: voice is preserved while low bass remains physical. Detect-only P02 retains at least `0.830537·VCC`; DC through inserted 16-ohm headphones is at most `0.331 mA`.

## Speaker

At the real `4 ohm −15% = 3.400 ohm` corner, the theoretical BTL ceiling is `1.587581 W`, below the speaker's 2-W rating. PAM8302A needs at most `576.453 mA`; the branch receives `625.000 mA`. Calculated junction at 85 C ambient is `99.679 C`, but the speaker itself is limited to a 50 C local environment, so playback is muted above that threshold while later H3.6 governs the remaining product. SD is not released until at least 10 ms after rail validity.

## Codec audio into SA518

`Vishay CRCW0402160KFKED` with 2.2 kohm/10 nF produces `10.454…12.797 mVrms` against the published `10.000-mV target. Calibration only turns codec volume down; selecting audio never asserts PTT.

## 3V3_MAIN cross-check

The corrected worst case is `2493.000 mA` inside the 2500-mA admission and retains `28.359%` to the guaranteed hardware limit. Normal display/backlight is now `200 mA`, audio is `625 mA`; a backlight fault threshold is no longer counted as an operating load.

The final analog configuration adds `0.0436 USD` per unit at quantity 100. **H3.3.2 is verified; the exact current marker is `H3.4.2`.**

[Machine H3-VRF32 package](../hardware/verification/generated/H3-VRF32-audio.json).
