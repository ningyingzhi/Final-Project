# DSP Libraries

Updated 2026-11-02. Full research notes are in `archive/dsp_libraries_2026-10-30.md`.

## Prototype 1
**Teensy Audio Library only**, which comes with Teensyduino:
- `AudioSynthWaveform`
- `AudioEffectEnvelope`
- `AudioEffectFreeverb`
- `AudioFilterBiquad`
- `AudioMixer4`
- `AudioEffectFade`

## Later stack (validated, not needed yet)
| Library | Role | Key limits |
|---|---|---|
| [OpenAudio_ArduinoLibrary](https://github.com/chipaudette/OpenAudio_ArduinoLibrary) | float32 graph (`AudioStream_F32`), I/O, converters, FFT, LMS | Its own convolution is only 513 taps |
| [DaisySP_Teensy](https://github.com/rheslip/DaisySP_Teensy) | Voices (modalvoice, resonator, formantosc, KarplusString) and light effects | Its wrapper is int16 and one instance per type, so write our own F32 wrapper |
| [hexefx_audiolib_F32](https://github.com/hexeguitar/hexefx_audiolib_F32) | Plate / spring / FDN reverb, delay, dynamics | IR cabsim is only 2,048 taps |
| [ConvolutionUP](https://github.com/bmillier/FFT-Convolution-Filter-Uniformly-partitioned) | Long IR convolution | int16, 17,920 taps (~0.41 s), ~570 KB RAM, one per Teensy |
| CMSIS-DSP (`arm_math.h`) | Our own blocks: FFT, biquad, NLMS (`arm_lms_norm_f32`) | |

Keep added libraries in `code/arduino_code/libraries/`. Never edit the installed `Audio.h`.
