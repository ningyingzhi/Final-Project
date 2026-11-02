# Final Project Brainstorm: Noguchi-inspired Modular Synth

21M.389/589 Audio Computing, Fall 2026 · Allen + teammate · started 2026-10-26
Status: early brainstorm, nothing decided yet.

## Concept
A modular synth plus audio effects, where every module lives in a sculptural enclosure inspired by Isamu Noguchi (interlocking slab sculptures such as *Kouros*, the Akari lamps, his gardens and playscapes, the Noguchi table). Modules are put together like a sculpture, toy or robot, and the way they are assembled sets the signal chain.
Fun precedent: Noguchi designed an actual audio device, the Zenith *Radio Nurse* (1937).

## Constraints
- **Fully standalone at runtime.** No laptop. Max, SuperCollider and the Mac are for prototyping only.
- **Grounded in the class.** The project is 40% of the grade and must be "a significant project exploring a subject related to the class in detail". Final project deadlines can't be extended.
- **Team rule.** Each person writes their own code and contributes an equal share, and the submission needs a collaboration note.
- **Starting point.** We begin from our own lab code and build from there.

## Architecture (current recommendation)
- **Teensy 4.1 #1 + audio shield, in the base.** This is the effects brain. It reads every module's knobs and IDs and runs the effect chain in stack order.
- **Teensy 4.1 #2 + audio shield, in the voice sculpture.** This is the active source. Its audio goes to Teensy #1's line in over a real cable.
- **Power.** One USB power bank. Boot time is under a second.
- **Fallback if the Teensys run out of compute.** A Pi 5 running SuperCollider headless, with a Teensy as its USB audio interface.
- **Workflow.** Prototype each algorithm in Python using the lab notebooks, then port it as a custom Teensy `AudioStream` block in C++. The Python version becomes the reference for testing: does the Teensy output match? Measure latency and CPU per module.

### Module detection
- **Default.** A unique resistor per module, read through the stacking connector (a voltage divider into an analog pin). We already own the parts, and it gives both identity and order.
- **Optional.** RFID / NFC for tokens placed on a plinth. Buy a PN532 reader and NTAG stickers. We don't own any RFID yet.
- **Caveat.** RFID gives identity only, never audio. Stacked tags confuse a single reader, and several MFRC522 readers close together interfere.

## Modules mapped to lectures
| Module | Class topic | Notes |
|---|---|---|
| **Listening sculpture** | Adaptive filtering (NLMS echo cancellation, real-time) | The mic and speaker share one body. It cancels its own output so it only hears people. **Core** |
| Sound localization | Mic arrays (lecture 9, GCC-PHAT, beamforming) | 2–3 INMP441 mics. Direction steers panning or lights |
| **Modal voice** | Vibrations (lecture 6) + hardware / piezo (lecture 8) | Strike the sculpture, measure its modes, then resynthesize. Tapping the piezo excites it. **Core** |
| Vowel voice | Filtering (lab 2: Rosenberg pulse + formants) | Knobs morph between vowels |
| Lo-fi slab | Sampling (lab 1, Exercise 6) | Sample-rate and bit-depth reduction |
| EQ / filter slab | Filtering (lab 2) | 6-band EQ plus a resonant filter |
| Spectral slab | STFT (lab 1) | Spectral freeze or gate |
| Space slab | Reverb + 3D audio (lectures 4, 5, 7, lab 3) | Tull-room IRs (curtains/panels switch), St Andrews church IR, KEMAR HRTF panner. Algorithmic reverb is cheaper on a Teensy. Convolution needs partitioned FFT, PSRAM and IRs trimmed to about 1 s |
| Denoise slab | Denoising (lecture 10) | Spectral subtraction, or exaggerated musical noise as an effect |
| (later) Autotune / classifier | Pitch, classification (upcoming lectures) | |

A natural team split: one person owns the listening sculpture and the mic array, the other owns the voices and the effect slabs.

## Form directions
1. **Kouros totem (current favorite).** Interlocking laser-cut plywood or acrylic slabs designed in Rhino/Grasshopper. Each slab is one effect, and stacking order is the chain. A VL53L5X ToF sensor on top tracks hand gestures.
2. **Akari lanterns.** Washi-and-wire modules lit from inside to show signal level. Needs WS2812 LEDs.
3. **Stone garden.** Biomorphic stones on a plinth, where position and rotation set parameters. Could use RFID or the XIAO ESP32-S3s over ESP-NOW.
4. **Noguchi table.** Two interlocking halves that only sound when joined.

## Precedents
littleBits / Korg Synth Kit, Percussa AudioCubes, Reactable, Ciat-Lonbarde, Bastl, Teenage Engineering, Moog Werkstatt.

## Owned parts that matter here
2× Teensy 4.1 + audio shield, Pi 5, 3× XIAO ESP32-S3, 3× INMP441 mics, Mic6 array, PVDF/piezo sensors, LSM6DSOX IMU, VL53L5X ToF, CAP1188, 2× ST7789 TFT, 15× WH148 pots, switches/buttons, passive kits, MCP6002 op-amp, Keyes 8002 amp. Full list: `All Projects/Parts List/parts_list.md`.

## To buy
- Magnetic pogo connectors (4–6 pin)
- 3.5 mm jacks
- WS2812 LEDs
- PSRAM for the Teensy 4.1
- Small speakers / amp (e.g. PAM8302 or MAX98357A)
- Perfboard
- Optional: PN532 + NTAG tags

## Risks
- Fabrication eating DSP time. Plan a minimum version: base + voice + listening sculpture + 1 slab.
- Teensy compute for convolution and STFT.
- Acoustic feedback in the listening sculpture (which is also exactly what the adaptive filter has to handle).
- Ground noise and pops when hot-plugging modules.

## Open questions
- What exactly is the final project brief / rubric? (Not seen yet.)
- Which form direction?
- How the work splits between the two of us.
