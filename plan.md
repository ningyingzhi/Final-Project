# Plan

Updated 2026-11-02. Architecture: `notes/central_engine.md`. Status: `PROJECT_LOG.md`.

## Prototype 1 scope
A vertical stack only. Every block has two faces at most, top and bottom.

```
 [ Speaker ]   top: owned Bluetooth speaker, bottom face only
 [ EQ      ]   ┐
 [ Reverb  ]   ├ effect modules, in any order; stack order = signal order
 [ ADSR    ]   ┘
 [ Core    ]   on the ground, top face only: the raw synth engine (sketch 02)
```

- **Core (done).** Waveform button (sine/tri/saw), on/off switch, volume pot, pitch pot. Keep it raw.
- **Power.** While testing, the Teensy is on the Mac's USB, and its 5 V passes up through the face contacts to every module. The speaker has its own battery. The power bank only matters for the standalone demo (P6).
- **All DSP runs on the Core.** Effect modules only report what they are and their knob values. The Core runs the effects in stack order.
- **Teensy Audio Library only.** No extra libraries for prototype 1.

| Module | Controls | DSP on the Core | Class link |
|---|---|---|---|
| ADSR | 4 pots (A, D, S, R) + 1 gate button | `AudioEffectEnvelope` | Envelopes (lab 1) |
| Reverb | 2 pots (decay, mix) | `AudioEffectFreeverb` + dry/wet mixer | Reverb lectures |
| Parametric EQ | 3 pots (freq, gain, Q), one peaking band | `AudioFilterBiquad` with **our own** peaking-EQ coefficients | Filter design (lab 2) |

- **Parts.** That's 9 pots plus the Core's 2. You own 15 WH148 pots, so they're covered.
- **The gate button.** It's needed because the synth has no keyboard: pressing it plays the envelope.
- **A nice order demo.** ADSR *below* the reverb lets the tail ring out. ADSR *above* the reverb chops the tail off.

### Audio out (decided 2026-11-02: Bluetooth, so no cables show)
A **Bluetooth audio transmitter module** (*to buy*), e.g. a KCX_BT_EMITTER-type A2DP board, goes inside the Core.
- It takes the shield's line out and runs on the Core's 5 V. Its pairing button needs to stay reachable.
- The Teensy has no Bluetooth, and the XIAO ESP32-S3 is BLE-only (no A2DP), so neither can do this job.
- Expect **~100–200 ms latency**. That's fine for drones, but the ADSR gate button will feel a little late. If it bothers us, look for an aptX Low Latency transmitter, which only helps if the speaker supports aptX LL.

## DSP steps
**P1** ✅ First sound (`01_first_sound`).

**P2** ✅ Synth engine (`02_waveform_osc`).

**P3** Effects on one breadboard:
- Wire the 9 effect pots and the gate button straight to the Core Teensy.
- Free analog pins: 15, 17, 22, 24–27, 38–41. Avoid the shield's pins.
- Run ADSR → Reverb → EQ in a fixed order.

**P4** Reorderable chain:
- Pre-build all three effects and switch the routing between them.
- Set the order from Serial for now, with a short fade on change.

**P5** Module link (Hall ID + ESP-NOW, `notes/module_topology.md`):
- One owned XIAO ESP32-S3 per effect module reads its pots and its 3 top-face Hall sensors, then sends `{id, above_id, knobs}` over ESP-NOW.
- A 4th XIAO in the Core (*to buy*) receives it and passes it to the Teensy by UART.
- The Core builds the chain from the reports and rebuilds it with a fade when the stack changes.

**P6** Standalone:
- BT transmitter in the Core (see above), paired with the speaker. A USB power bank feeds the stack through the faces.

## CAD steps
- **C1** Face standard (one shared Grasshopper definition):
  - Holding magnets (also the keying).
  - 3 ID-code magnet spots on the bottom, 3 Hall sensor spots on the top.
  - 2 power contacts.
- **C2** 3D-print a test face pair. Check magnet hold, power-contact alignment and polarity, and that the holding magnets don't disturb the Hall readings.
- **C3** Shells:
  - Core (Teensy, controls, power bank)
  - 3 effect modules (XIAO + pots)
  - A speaker cradle with a bottom face
- **C4** Final material, finish, renders.

## To buy
The full list with links is in `parts_to_buy.md`. The connection diagram is `sketches/module_connections_v1.png`.

## After prototype 1 (later, not now)
- Move to the F32 stack (`notes/dsp_libraries.md`) with DaisySP voices.
- More effects from the labs (lo-fi, delay, spectral).
- Free-form attachment (side faces, tree routing).
- Space/Ear module on Teensy #2 (convolution reverb with the Tull IRs, NLMS listening).
- Evaluation against the Python lab references.
