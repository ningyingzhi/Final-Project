# Architecture

Updated 2026-11-02. Older versions are in `archive/`.

## Prototype 1
- **Core** (Teensy 4.1 + audio shield, sits on the ground).
  - The raw synth engine. It also runs **every effect's DSP**, in stack order.
- **Effect modules** (ADSR, Reverb, Parametric EQ). Each has an owned XIAO ESP32-S3 that reads its knobs and sends them to the Core over **ESP-NOW**. **No audio passes through the modules.**
- **Stack order comes from Hall sensors.**
  - Every bottom face carries a 3-magnet ID code (each magnet N, S, or none, so 27 IDs).
  - Every top face has 3 linear Hall sensors that read the code of whatever sits on it.
  - Each module reports "I am X, above me is Y". The Core reads its own top-face sensors and links the reports into the chain.
- **Power.** 2 contacts per face (GND, 5 V) carry the Core's 5 V (Teensy VIN: from the Mac's USB while testing, a power bank for the standalone demo) up through every module. Data is wireless, so there are no data contacts.
- **Speaker** (owned Bluetooth speaker) on top, in a cradle with an ID code. Audio comes from a Bluetooth transmitter in the Core.

```
synth → [effect at level 1] → [level 2] → [level 3] → shield line out → BT transmitter → speaker
```

## What goes in each module
| Block | Electronics | Faces |
|---|---|---|
| **Core** | Teensy 4.1 + shield, button, slide switch, 2 pots (owned). **XIAO ESP32-S3 as the ESP-NOW receiver**, linked to the Teensy by UART (*to buy*, since all 3 owned XIAOs go into modules). BT transmitter (*to buy*). USB power bank + power switch. 3 Hall sensors read by the Teensy. | Top: 3 Hall sensors, holding magnets, 2 power pads |
| **ADSR** | XIAO ESP32-S3 (owned), 4 pots + 1 button, 3 Hall sensors | Bottom: ID magnets, holding magnets, 2 pogo pins. Top: 3 Hall sensors, holding magnets, 2 power pads |
| **Reverb** | XIAO ESP32-S3 (owned), 2 pots, 3 Hall sensors | Same as ADSR |
| **Parametric EQ** | XIAO ESP32-S3 (owned), 3 pots, 3 Hall sensors | Same as ADSR |
| **Speaker cradle** | No electronics | Bottom: ID magnets + holding magnets only |

- **Pin budget.** The XIAO ESP32-S3 has 9 analog pins (D0–D5, D8–D10), all on ADC1, which still works while ESP-NOW is running (ADC2 doesn't). The ADSR module, the busiest, uses 7: 4 pots + 3 Hall sensors.
- **Hall sensors.** Use linear sensors (DRV5053 or SS49E) on 3.3 V, so the ADC can tell N, S and nothing apart. 12 in total (Core 3 + 3 modules × 3).

## DSP per module (Teensy Audio Library)
| Module | Controls | Object |
|---|---|---|
| ADSR | A, D, S, R pots + gate button | `AudioEffectEnvelope` |
| Reverb | decay, mix | `AudioEffectFreeverb` + mixer (dry/wet) |
| Parametric EQ | freq, gain, Q | `AudioFilterBiquad`, our own peaking-EQ coefficients (lab 2) |

## Later vision (not prototype 1)
- Free-form attachment on side faces, with tree routing (series along a branch, parallel at splits).
- More effects from the labs.
- The F32 library stack with DaisySP voices.
- A heavy Space/Ear module on Teensy #2 (Tull-IR convolution + FDN reverb, NLMS listening).
- BRS40 speaker cabinet with measured EQ correction.
