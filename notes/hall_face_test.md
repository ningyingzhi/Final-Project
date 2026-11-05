# Face hardware test: Hall sensors, ID magnets, pogo connectors

Written 2026-11-05. Covers `module_topology.md` build steps 1 + 3 and the bench half of CAD C2.
Sketch: `code/arduino_code/sketches/03_hall_id_test`. Results here set the numbers for the C1 face standard.

**Bring:** Teensy 4.1 on the breadboard, Hall sensors, 3×2 mm magnets, the 2 pogo pairs, a multimeter, a ruler or calipers, paper/card spacers (or 1 mm 3D-printed shims), a marker.

## 1. One sensor (thresholds)
1. Wire 1 Hall: VCC → 3.3 V, GND → GND, OUT → A10 (pin 24). Set `NUM_SENSORS = 1`, upload, open Serial Monitor at 115200.
2. Baseline should be ~1650 mV with no magnet. If it sits near 0 or 3300, or the part says 4.5 V min, it won't work on 3.3 V (switch to DRV5053).
3. Hold a magnet flat over the sensor's face. Note which face gives `S` (delta > 0) and mark that face of the magnet with marker. Flip it and check you get `N`.
4. Noise: with no magnet, watch the delta for ~10 s. Threshold must sit well above it (default 80 mV on, 50 off; `+`/`-` changes it).

## 2. Signal vs gap
The real gap = bottom-face wall + top-face wall + air. Measure with spacers between magnet and sensor, using the peak value (`r` resets it).

| Gap (mm) | S peak (mV) | N peak (mV) |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

**Pass:** at the gap you plan to print (likely 2–3 mm), |peak| ≥ 3× the threshold. If not, thin the walls under the code spots or stack 2 magnets.

## 3. Three sensors (ID code + crosstalk)
1. Wire Hall 1 → A11 (pin 25), Hall 2 → A12 (pin 26). Set `NUM_SENSORS = 3`, upload, `c` to calibrate with no magnets near.
2. Crosstalk: put a magnet over H0 only, at the real gap. H1 and H2 should stay `-`. Try sensor spacings of 10, 15, 20 mm and note the smallest one that stays clean.
3. ID code: tape 3 magnets on a card in a pattern (e.g. S, none, N) and slide it over. `ID` should be stable and match `state0 + 3·state1 + 9·state2` (none 0, N 1, S 2).

| Spacing (mm) | H1/H2 delta with magnet on H0 (mV) | Clean? |
|---|---|---|
| 10 | | |
| 15 | | |
| 20 | | |

## 4. Pogo connectors (power contacts)
Do this with the Teensy **unplugged** until step 3.
1. Continuity: snap a pair together, multimeter beep mode, check each pin goes to the matching pin only. Note which pin you'll call 5 V and mark it.
2. Keying: try flipping one half 180°. If the magnets repel, it's self-keyed. If it snaps on reversed, the face magnets must do the keying (note this for C1).
3. Live: wire the female half to Teensy VIN (5 V from USB) and GND. Snap the male half on and measure: should read ~5 V. Wiggle and tilt it while watching the meter for dropouts.
4. Magnet leak: hold a connector at 5, 10, 15 mm from a calibrated Hall (in plotter mode `p`) and note the delta. That's the minimum distance between connectors and code spots.

| Pogo → Hall distance (mm) | Delta (mV) |
|---|---|
| 5 | |
| 10 | |
| 15 | |

## Results to carry into C1
- Gap at the code spots: ___ mm. Threshold on/off: ___ / ___ mV.
- Min spacing between code sensors: ___ mm. Min pogo-to-sensor distance: ___ mm.
- Pogo self-keyed: yes / no. 5 V pin marked: ___.
