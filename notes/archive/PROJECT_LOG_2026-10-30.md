# Project Log

Status of each `plan.md` step. Update a row when a step is tested and done (see CLAUDE.md rule 11).
Status: ✅ done (tested) · 🟡 in progress · ⬜ not started

## Part A: Audio / DSP

### Phase 1: Get sound out
| Step | Status | Date | By | Sketch / file | Notes |
|---|---|---|---|---|---|
| 1.1 Toolchain + first sound | ✅ | 2026-10-30 | Allen | `sketches/01_first_sound` | 440 Hz sine on headphones, CPU/memory on Serial |
| 1.2 Waveform osc, on/off, volume, pitch | ✅ | 2026-10-30 | Allen | `sketches/02_waveform_osc` | Button cycles 3 waveforms, switch fades on/off, volume pot (A0, dB) and pitch pot (A2, 55–1760 Hz exp) tested on the board |
| 1.3 Playable voice (ADSR, piezo) | ⬜ | | | | Pitch pot moved into 1.2 |
| 1.4 Standalone sound (amp, power bank) | ⬜ | | | | Needs PAM8403-class amp (to buy) |
| 1.5 Baseline metrics | ⬜ | | | | |

### Phase 2: Effects and engine functions
| Step | Status | Date | By | Notes |
|---|---|---|---|---|
| 2.0 Move to F32 graph | ⬜ | | | |
| 2.1 Library effects chain | ⬜ | | | |
| 2.2 Own DSP from labs | ⬜ | | | |
| 2.3 Engine functions | ⬜ | | | |
| 2.4 Chain manager | ⬜ | | | |
| 2.5 Module detection prototype | ⬜ | | | |
| 2.6 Python reference tests | ⬜ | | | |

### Phase 3: Advanced DSP
| Step | Status | Date | By | Notes |
|---|---|---|---|---|
| 3.1 Modal voice | ⬜ | | | |
| 3.2 Spectral effects | ⬜ | | | |
| 3.3 Space module (Teensy #2) | ⬜ | | | |
| 3.4 Ear (NLMS, GCC-PHAT) | ⬜ | | | |
| 3.5 Speaker correction | ⬜ | | | |
| 3.6 Stretch | ⬜ | | | |
| 3.7 Evaluation | ⬜ | | | |

## Part B: CAD / Fabrication
| Phase | Status | Date | By | Notes |
|---|---|---|---|---|
| C1 Standards + form lock | ⬜ | | | |
| C2 Fit prototypes | ⬜ | | | |
| C3 Module enclosures | ⬜ | | | |
| C4 Final fabrication + docs | ⬜ | | | |
