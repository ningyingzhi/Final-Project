# Direction v3: Central Sound Engine + Modular Effects

Updated 2026-10-26 after Allen's ask, with the software stack added 2026-10-29. This replaces the "Excite → Body → Room → Ear" split from v2 with one **Core** that holds the synth, plus effect modules that snap onto it. The Noguchi forms (the v4 slim column, the cantilever, the lantern cube, the head) all still apply.

## The Core (central sound engine)
It lives in the uniform base column from the v4 sketch, and holds:
- **Teensy 4.1 #1 + audio shield.** Runs the synth voices, a small sequencer/arpeggiator, and the effect chain for whatever is snapped on.
- **BOSS BRS40 speaker + 5 V class-D amp.** The column is the speaker cabinet (sealed or Helmholtz-ported, then measured and EQ-corrected).
- **Power bank.** Powers everything that snaps on through the pogo connectors.
- **Play surface.** Pots, a few buttons, piezo "strike" pads, a ST7789 showing the chain.
- **Class-grounded voices,** switchable:
  - Subtractive: oscillators and noise from lab 1 into your own filters from lab 2. DaisySP `blosc` / `oscillator` → `svf` / `moogladder`
  - Vowel / formant: Rosenberg pulse + formant filters (lab 2). Our own block, with DaisySP `formantosc` / `vosim` to compare against
  - Modal: modes measured from the sculpture itself (lecture 6), excited by the piezo pads. DaisySP `modalvoice` / `resonator` loaded with our fitted modes
  - Karplus-Strong / plucked: DaisySP `KarplusString` / `stringvoice`
  - Later: additive / STFT resynthesis (lab 1)

## Software stack
- **OpenAudio_ArduinoLibrary:** the float32 graph (blocks + patch cords). Snapping a module on or off rewires the cords.
- **DaisySP** (our `AudioStream_F32` wrapper): voices and light effects.
- **hexefx_audiolib_F32:** reverbs, delay, dynamics.
- **ConvolutionUP:** long IRs, Teensy #2 only.
- **CMSIS-DSP:** our own STFT / NLMS blocks.
- Full notes are in `dsp_libraries.md`.

## Effect modules (candidates)
| Module | DSP | Class topic | Cost | Library |
|---|---|---|---|---|
| Lo-fi | Sample-rate / bit-depth crush | Lab 1 (sampling) | light | DaisySP bitcrush / decimator, or our lab 1 port |
| Filter / EQ | Resonant filter, 6-band EQ | Lab 2 | light | DaisySP svf / moogladder, our 6-band EQ |
| Delay | Feedback delay, ping-pong | Filtering / echo | light (memory) | hexefx stereo delay |
| Spectral | STFT freeze, gate, blur | Lab 1 (STFT) | heavy | Own block (CMSIS FFT) |
| Space | Tull-room / church convolution or algorithmic reverb, HRTF pan | Lab 3, lectures 4, 5, 7 | heavy | ConvolutionUP + hexefx ReverbSc tail |
| Ear (listening input) | Mic in, NLMS echo cancel against the Core's own output, GCC-PHAT direction | Adaptive filtering, lecture 9 | heavy | CMSIS NLMS + own GCC-PHAT |
| Denoise / "musical noise" | Spectral subtraction as an effect | Lecture 10 | medium | Own block (OpenAudio has spectral denoise to reference) |
| Modulators (not audio) | LFO, IMU tilt, ToF hand height, which modulate a neighbor's parameters | Interaction | none | DaisySP LFO / smoothing |
| Later: Pitch | Autotune / harmonizer | Upcoming pitch lecture | medium | DaisySP pitchshifter + own tracker |

## Where the effect DSP runs (three architectures)
**A. Smart Core, passive effects.** All DSP runs on the Core Teensy. Each effect module is just an ID, knobs and LEDs, and the Core builds the chain in snap order.
- For: cheap, one firmware, no audio crossing connectors, no noise.
- Against: one Teensy's compute caps how many heavy effects can run at once, and the modules are "remote controls" rather than truly separate units.

**B. Smart effects.** Every effect module has its own processor, and audio is passed module to module as digital I2S over the pogo pins. That avoids analog noise and gives about one block (~3 ms) of latency per hop.
- Fits what you own: the 3 XIAO ESP32-S3 boards (two I2S ports each) plus Teensy #2.
- For: truly modular, and you can add modules without hitting a Core compute limit.
- Against: four firmwares, clock and sync issues, and the most debugging.

**C. Hybrid (recommended).** The Core runs the synth and all the *light* effects. **Teensy #2 lives inside one "heavy" module,** the Space/Ear module (the lantern cube or the head), and handles reverb, the HRTF and the NLMS listening. Audio goes Core → Space → back over the shield's line in/out through the connector.
- Uses exactly the two Teensys you own.
- Puts the hard, most class-relevant DSP in its own body.
- Splits the work evenly between the two of you.

## How assembly sets the routing
Modules attach to the Core or to each other on any face. Sound flows **outward from the Core as a tree**:
- Distance from the Core sets the order (series).
- A branch is a parallel split.
- The outputs of all outermost modules are summed to the speaker.

Stacking straight up gives a pure series chain. Modules on separate Core faces run in parallel. Modulators snap on anywhere and modulate whatever they touch. Pulling a module out triggers a rebuild with a ~20 ms crossfade. Full logic: `module_topology.md`.

## Connector / bus (per magnetic face, 5 contacts)
GND · 5 V · DATA (half-duplex, one per face) · AUDIO_SEND · AUDIO_RETURN
- **Discovery.** A HELLO flood from the Core builds a spanning tree. Each module records the face the HELLO arrived on as its "parent". It then replies with its ID, type and knob values, and forwards the HELLO outward. A heartbeat every ~50 ms catches changes.
- **Module MCU.** Start with the 3 owned XIAO ESP32-S3s, then RP2040s (*to buy*) for more modules.
- **Audio.** AUDIO_SEND / RETURN is one shared analog bus wired through every module, so the Teensy #2 Space module works wherever it sits. Only one heavy module at a time.
- **Faces.** Hermaphroditic (mirror-symmetric pogo pins and pads), keyed by an N/S magnet pattern so a face can't be connected at the wrong rotation.
- **RFID** stays optional, for pieces that are *placed* rather than snapped (PN532 + NTAG).

## Team split
- **Person 1: the Core.** Voices, sequencer, play surface, chain/bus firmware, speaker cabinet + EQ.
- **Person 2: the effects.** The light effect blocks plus the Space/Ear module on Teensy #2 (reverb, HRTF, NLMS).
- **Shared:** form, fabrication, connector, integration, report.

## Minimum version
Core (2 voices + speaker) + 3 snap-on modules: Lo-fi/Filter (light, top stack), Delay (side send), and Space/Ear on Teensy #2 (side send). Two vertical and one horizontal is enough to demo both routing modes.

## New things to buy for this direction
- XIAO RP2040 / RP2040-Zero for modules beyond the 3 owned XIAO ESP32-S3s
- Polyfuse or ideal diode per module (5 V protection)
- Plus what's already listed: pogo/magnet connectors, PAM8403 amp, PSRAM, WS2812 LEDs

## Open questions
- Is the Core's play surface knobs + pads, or also a small keyboard / touch strip (CAP1188)?
- How many effect modules for the final demo (3 for the MVP, 5–6 as a stretch)?
