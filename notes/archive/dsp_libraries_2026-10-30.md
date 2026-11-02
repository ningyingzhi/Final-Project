# Teensy 4.1 DSP / Convolution Libraries

Researched 2026-10-29. Everything here plugs into the Teensy Audio Library graph (`AudioConnection`) unless noted otherwise.

| Library | What we'd use it for | Notes |
|---|---|---|
| **Teensy Audio Library** (built in, PJRC) | Phase 1–2 basics: `AudioSynthWaveform`, `AudioEffectEnvelope`, `AudioFilterBiquad`, `AudioFilterStateVariable`, `AudioFilterFIR` (short FIR), `AudioEffectDelay`, `AudioEffectBitcrusher`, `AudioEffectFreeverb`, `AudioEffectGranular`, `AudioAnalyzeFFT1024`, `AudioMixer4` | 16-bit integer, 128-sample blocks. No long convolution. |
| **AudioFilterConvolutionUP** ([bmillier](https://github.com/bmillier/FFT-Convolution-Filter-Uniformly-partitioned)) | **Convolution reverb with our IRs** (Tull / St Andrews), speaker-correction FIR | Uniformly partitioned FFT convolution, **Teensy 4 only**, up to **18,000 taps (~0.41 s at 44.1 kHz)**. Fixed ~6.8 ms latency, under 1 ms compute per cycle. Install by copying the .h/.cpp into the Audio library and including it in `Audio.h`. The example says to add a 100 Ω series resistor on MCLK. Tested on older Teensyduino (1.47), so check it compiles on the current one. No license stated. |
| **hexefx_audiolib_F32** ([hexeguitar](https://github.com/hexeguitar/hexefx_audiolib_F32)) | Ready-made effects modules: plate / spring / FDN (`ReverbSc`, PSRAM option) reverbs, ping-pong delay, phaser, compressor, noise gate, 3-band EQ, IR cab sim (uniformly partitioned, IR WAVs up to 8K samples from SD) | 32-bit float, Teensy 4.x, MIT license. Needs OpenAudio_ArduinoLibrary. |
| **OpenAudio_ArduinoLibrary** ([chipaudette](https://github.com/chipaudette/OpenAudio_ArduinoLibrary)) | Float32 versions of FIR / biquad / IIR / EQ / FFT / overlapped FFT, **LMS denoising**, spectral denoising, compressor | Teensy 4 compatible since 2020. F32↔I16 converters let it mix with the standard library. |
| **CMSIS-DSP (`arm_math.h`)** | Building our own blocks: `arm_rfft_fast_f32` (STFT), `arm_biquad_cascade_df1_f32`, `arm_fir_f32`, **`arm_lms_norm_f32` (NLMS for the Ear)** | Ships with Teensyduino. Optimized for the M7 core. |
| **Faust → Teensy** ([faust docs](https://faustdoc.grame.fr/tutorials/teensy/)) | Writing an effect in a high-level DSP language and compiling it to a Teensy Audio object | Optional. Good for quick experiments. |

## Implications for our plan
- **Space module reverb.** 18K taps (~0.4 s) is shorter than a full Tull IR, so use a **hybrid reverb**: convolution for the measured early part (first ~0.4 s) plus an FDN tail (`AudioEffectReverbSc_F32`) matched to the measured RT60. That's lecture 4/5 material, and it's a good report topic. A second Teensy, or two convolution instances, can do stereo or longer IRs.
- **Speaker correction (3.5).** Use the same convolution object with a minimum-phase inverse filter designed in Python.
- **Ear (3.4).** Use CMSIS `arm_lms_norm_f32` for NLMS echo cancellation, or the OpenAudio LMS block as a reference.
- **Spectral effects (3.2).** Write our own `AudioStream` block using `arm_rfft_fast_f32` with overlap-add.
- **PSRAM (to buy).** Needed for long delays, FDN reverb buffers and IR storage.

## Recommended engine stack (2026-10-29)
No single library covers everything, so the most complete *and* efficient setup is a layered stack:

1. **Backbone: Teensy Audio Library.** I/O, the block graph (`AudioConnection`), the Design Tool, the SGTL5000 driver, USB audio, and quick integer effects.
2. **Main DSP path: float32 via OpenAudio_ArduinoLibrary + hexefx_audiolib_F32.**
   - The M7's hardware FPU makes float32 fast.
   - Float math matches our Python lab code, so porting is nearly line by line, with no fixed-point scaling.
   - It gives better headroom and quality than the 16-bit integer path.
   - hexefx adds well-tuned reverbs, delays and a 24-bit SGTL5000 / I2S driver.
3. **Synth voices: [DaisySP_Teensy](https://github.com/rheslip/DaisySP_Teensy)** (MIT).
   - DaisySP (Electrosmith) brings antialiased polyBLEP oscillators, envelopes, filters, physical modelling, reverbs and delays, drawn from Csound, Soundpipe and Mutable Instruments.
   - It's wrapped as `AudioSynthDaisySP` / `AudioEffectDaisySP`, which you write per-sample code inside.
   - Caveats: one instance of each wrapper only; compile just the DaisySP .cpp files you use (the whole library is about 500 KB); resonator objects have compile issues; the author may not track future Audio library changes.
4. **Our own blocks: CMSIS-DSP** (FFT, biquad, FIR, NLMS) inside custom `AudioStream_F32` blocks.
5. **Long IR convolution:** AudioFilterConvolutionUP (above).

Skip for now: Teensy4i2s (bare I2S only), Faust (optional).

## Also checked: ML_SynthTools ([marcel-licence](https://github.com/marcel-licence/ML_SynthTools))
- **What it is:** a multi-platform Arduino synth library (ESP32, RP2040, Teensy 4.1, …). It has an organ (9 drawbars), saw/square PWM oscillators, an arpeggiator, MIDI in, a MIDI file / MOD player, and a simple delay and reverb.
- **License:** GPL-3.0.
- **Not adopted as the engine,** for three reasons:
  1. It runs its own audio loop and codec drivers rather than plugging into the Teensy Audio Library graph.
  2. Parts of it ship as precompiled `.a` files, so we can't read or modify all of the DSP.
  3. Its effects are basic next to hexefx / OpenAudio.
- **Useful as a reference** for the arpeggiator, MIDI and organ code.

## Validation of the proposed roles (2026-10-29, source code inspected)
| Role | Library | Verdict | Key facts from the code |
|---|---|---|---|
| Main DSP engine / graph | OpenAudio_ArduinoLibrary | ✅ Yes | Active (last commit Aug 2026). Provides `AudioStream_F32`, F32 I2S in/out, `AudioConvert_I16toF32` / `F32toI16`, FFT / overlapped FFT, LMS denoise, an F32 delay. Its own `AudioFilterConvolution_F32` is only **513 taps**, so it's not for reverb. |
| Long IR convolution | FFT-Convolution-Filter-Uniformly-partitioned | ✅ Yes, with caveats | Up to **140 partitions × 128 = 17,920 taps (~0.41 s)**. It's an **int16 `AudioStream` object** (float inside), so it needs F32↔I16 converters around it. The filter masks plus the FFT buffer take roughly **570 KB of the 1 MB RAM**, so plan one per Teensy and put it on Teensy #2 (Space). Old code (Teensyduino 1.47), so test that it compiles first. |
| Effects | hexefx_audiolib_F32 | ✅ Yes | Native F32, built on OpenAudio. Reverbs (plate, spring, ReverbSc FDN with a PSRAM option), stereo delay, phaser, compressor, gate, EQ, biquads, LFO / allpass / delay building blocks, 24-bit SGTL5000 driver. Its IR cabsim is only **2,048 taps** (SD version up to 8K), so it's not a replacement for the long-IR convolution. Last commit May 2025. |
| Synth engine | DaisySP_Teensy | ✅ Yes, and **give it a bigger role** | See below. |

### Giving DaisySP a bigger role
DaisySP is a full DSP toolbox, not just oscillators:
- **Synthesis:** blosc, oscillator, fm2, formantosc, vosim, harmonic_osc, oscillatorbank, variablesaw / variableshape, zoscillator
- **Physical modelling:** **modalvoice, resonator**, KarplusString, stringvoice, pluck, drip
- **Filters:** svf, moogladder, biquad, comb, fir, **mode** (modal filter), allpass, tone / atone
- **Effects:** bitcrush, decimator, sampleratereducer, chorus, flanger, phaser, overdrive, fold, autowah, tremolo, pitchshifter, reverbsc
- **Control, drums, noise, utility:** adsr / adenv, delayline, smooth, metro, dust / particle / grainlet, analog / synth drums

Its classes are plain C++ (`Init(sr)` + `Process(float)`). That means it can feed **every** module (voices, light effects, modal synthesis) rather than only the oscillators.

**Wrapper caveat.** The provided wrapper is int16 and allows only one instance per type. **Write our own thin `AudioStream_F32` wrapper template** instead, about 30 lines that loop `Process()` over the 128-sample float block. That gives multiple instances, float end to end, and DaisySP blocks that drop straight into the OpenAudio graph next to the hexefx effects.

### Final stack
- **OpenAudio:** graph, I/O, converters, FFT, LMS
- **DaisySP (via our F32 wrapper):** voices, modal synthesis, light effects
- **hexefx:** polished reverbs, delay, dynamics, codec
- **ConvolutionUP:** long IR, on Teensy #2
- **CMSIS-DSP:** our own blocks (STFT, NLMS)
- **Overlaps to choose between:** reverbsc exists in both DaisySP and hexefx (prefer hexefx, which is stereo with PSRAM). Bitcrush exists in DaisySP and the Teensy Audio Library.

### Install hygiene
DaisySP_Teensy and ConvolutionUP both tell you to copy files into the Teensy Audio library and edit `Audio.h`. **Don't do that.** Teensyduino updates overwrite it. Put the files in the sketch folder, or in our own local library under `libraries/`, and `#include` them directly.
