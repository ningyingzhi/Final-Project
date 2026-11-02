# Final Project Brainstorm v2: Noguchi-inspired Modular Synth

21M.389/589 Audio Computing, Fall 2026 · Allen + teammate · updated 2026-10-26
Earlier version: `brainstorm_v1.md`. Status: proposed direction, not decided.

## The idea in one line
**A set of Noguchi-style sculptures that together make up the physical chain of sound, from what excites it, to the body that resonates, to the room, to the listener. You compose by stacking and arranging them.**

The course is basically about that same chain: sources and vibrations, filtering, rooms, 3D hearing, microphones, and adaptive cleanup. Making each sculpture one link in it means the class is the structure of the project rather than an add-on. It also suits Noguchi, whose work is about objects, the space around them, and the people moving through it.

## The four families of modules
| Family | What it does | Class roots | Form idea |
|---|---|---|---|
| **Excite** | Makes the raw energy: tap it (piezo / PVDF), a glottal pulse, oscillators, noise, chirps | Lab 1 (signals), lab 2 (Rosenberg pulse) | A small dense "striker" stone with a contact face |
| **Body** | Resonates. Each body is a modal synthesizer built from the measured modes of its *own* enclosure (strike it, record it, fit the modes). Stacking bodies chains resonators. Formant / EQ filters live here too | Lecture 6 (vibrations, damped oscillators, Q), lab 2 (filters, EQ, formants), lecture 8 (piezo pickups) | Interlocking slabs in different materials (plywood, acrylic, stone/jesmonite), each sounding different |
| **Room** | Puts the sound in a space: the Tull room IR, with *physical* curtains/panels on the sculpture that switch between the three measured conditions, the St Andrews church IR, or an algorithmic reverb | Lab 3, reverb lectures | An Akari-like lantern / room model with a fabric "curtain" you can open and close |
| **Ear** | The listener. It listens to the room with a mic, uses NLMS echo cancellation to remove its own output so it hears only people, uses GCC-PHAT to find where a clap came from, and drives the binaural (KEMAR HRTF) headphone output | Adaptive filtering (new lecture), mic arrays (lecture 9), 3D audio (lecture 7), denoising (lecture 10) | A head-like Noguchi form (a nod to his *Radio Nurse*, 1937) with two "ears" |

**Interaction loop.** You tap a striker. The bodies ring, the room spreads the sound, and the Ear hears the room. When a person claps or speaks, the Ear localizes it and feeds it back into the system as a new excitation, steering pan or modes. The whole thing behaves like an instrument that listens.

## Hardware: fully standalone, all parts owned
- **Teensy A + audio shield ("Source" base): Excite + Body.** Reads the piezos, does modal synthesis (many resonators, which costs a lot of compute), and handles the stack's resistor IDs and pots.
- **Teensy B + audio shield ("Space" base): Room + Ear.** Audio from A comes in on line in over a real cable between the two halves. It runs the reverb/convolution, the NLMS canceller, GCC-PHAT on 2 INMP441 mics, and the HRTF / headphone and line outputs.
- **Power.** One USB power bank. Boot time under 1 s, no laptop.
- **Module ID.** Resistor-ID through magnetic pogo connectors on each stacking face, which gives identity *and* order. **RFID is optional,** for pieces you *place* rather than stack (for example strikers on a plinth: PN532 + NTAG stickers). The caveats: RFID carries no audio, stacked tags confuse a single reader, and several MFRC522 readers close together interfere.
- **Display / feedback.** A ST7789 on the Space base showing the current chain plus localization. WS2812 LEDs in the Room lantern.
- **Fallback.** A Pi 5 running SuperCollider headless, with a Teensy as its USB audio interface, if the Teensys run out of compute.

## Loudspeaker: BOSS BRS40 (owned)
We own a BOSS Audio BRS40, a 4" full-range dual-cone car speaker (4 Ω, about 25 W RMS). It becomes the system's main acoustic output, so the piece plays into the room and doesn't need headphones.
- **Placement.** In the v4 sketch, put it in the uniform base column. That's the largest volume, and the magnet's weight also counterbalances the cantilevered beam. The alternative is the lantern cube, so the "Room" literally radiates. A 4" driver needs roughly 1–3 L of enclosure.
- **Amp.** The Keyes 8002 is too small. Use a PAM8403-class class-D board at 5 V, which runs from the same USB power bank (a few watts into 4 Ω, plenty for a tabletop). A TPA3116 needs 12–24 V, which would mean a USB-PD trigger board.
- **The class angle (lecture 8, hardware).** Design the enclosure as a real loudspeaker cabinet:
  - Choose sealed or Helmholtz-ported, and tune the port with the lecture 6 resonator formula.
  - Measure the finished cabinet's frequency response with the lab 3 sine-sweep method.
  - Correct it with an inverse EQ filter (lab 2) running on the Teensy.
  This gives a clean before/after result for the report.
- **Effect on the Ear.** The speaker is now right next to the Ear's mic, so the NLMS echo canceller has a real, strong echo path to learn. That makes the adaptive filtering demo harder and more convincing. Start with the speaker muted (headphones) while the canceller is being developed.

## Team split (equal and natural)
- **Person 1: Source half.** Excite + Body modules, modal analysis of the enclosures, Teensy A.
- **Person 2: Space half.** Room + Ear modules, adaptive filter, localization, Teensy B.
- **Shared.** Form language, fabrication, the connector/ID system, integration, and the report.

## Workflow
1. Prototype every block in Python, starting from our lab code (STFT, filters, vowel synthesis, reverb / HRTF).
2. Port each block to a custom Teensy `AudioStream` in C++. Use 128-sample blocks, which is the real-time processing model from lecture.
3. Evaluate against the Python reference: output error, latency, CPU per block, how well the canceller converges (ERLE), and localization accuracy.
4. A nice evaluation hook: **measure the real Tull room with the finished system** and compare it with the class measurements.

## Minimum version and stretch goals
- **MVP (must demo).** 1 striker + 2 bodies + Room (Tull IR) + Ear with the NLMS canceller. Two Teensys, resistor-ID stacking.
- **Stretch 1.** GCC-PHAT localization driving the HRTF pan.
- **Stretch 2.** More bodies in different materials, the physical curtain switch on the Room.
- **Stretch 3.** Upcoming lectures: pitch tracking (the Ear makes the bodies retune to a singer), classification (the Ear recognizes clap vs. voice vs. knock).

## Rough timeline (deadline TBD; assumes about mid-December)
| Week | Focus |
|---|---|
| Oct 27 – Nov 2 | Lock the concept. Teensy audio hello-world. Python prototypes from labs. Strike and record test materials |
| Nov 3 – 9 | Modal fitting + modal synth on Teensy A. Reverb on Teensy B. Connector/ID test |
| Nov 10 – 16 | NLMS canceller + mic. First enclosures (Rhino/Grasshopper → laser cut) |
| Nov 17 – 23 | Integration of the two halves. Stacking works end to end |
| Nov 24 – 30 | Localization / HRTF stretch. Final fabrication |
| Dec 1 – 7 | Evaluation, polish, demo rehearsal |
| Dec 8 → | Report + demo |

## To buy
- Magnetic pogo connectors (4–6 pin)
- 3.5 mm jacks
- WS2812 LEDs
- PSRAM for both Teensys
- Class-D amp for the BRS40 (PAM8403-class, 5 V); optional 2nd small speaker if we want stereo
- Headphones jack/amp
- Perfboard
- Optional: PN532 + NTAG tags

## Risks
- **Fabrication eating DSP time.** Build forms after the MVP sounds right.
- **Acoustic feedback in the Ear.** This is exactly what the adaptive filter solves. Start with headphone output as a safe fallback.
- **Teensy compute.** Keep modal synthesis to about 32–64 modes per Teensy, and trim IRs to about 1 s (partitioned FFT).
- **Ground noise and hot-plug pops.** Common ground plane through the pogo pins, and mute the audio while the chain re-reads.

## Precedents
littleBits / Korg Synth Kit, Percussa AudioCubes, Reactable, Ciat-Lonbarde, Bastl, Teenage Engineering, Moog Werkstatt. On the Noguchi side: *Kouros*, the Akari lamps, the gardens/playscapes, the Noguchi table, *Radio Nurse*.

## Open questions
- Speaker location: base column vs. lantern cube.
- The final project brief / rubric and the deadline (not seen yet).
- Whether the excite → body → room → ear framing works for both of us.
- Materials and fab access (laser cutter, CNC, casting).
