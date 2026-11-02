// 02_waveform_osc: plan step 1.2 (three-waveform oscillator, on/off, volume, pitch).
// An oscillator on the audio shield. The button cycles sine -> triangle ->
// band-limited saw, the slide switch mutes/unmutes with a short fade, the volume
// pot sets master gain on a dB curve and the pitch pot sets frequency on an
// exponential (octave) curve, both matching hearing perception (lectures 1-2).
// Class bonus (lab 1, Ex. 6 aliasing): type 'a' in Serial Monitor to swap the saw
// between band-limited and naive, then turn the pitch up to hear the aliasing.
// Hardware: Teensy 4.1 + audio shield (SGTL5000), headphones on the shield jack.
//   Button      pin 2  -> GND (INPUT_PULLUP)
//   Switch      pin 3  -> GND (INPUT_PULLUP, closed = sound on)
//   Volume pot  A0 (pin 14) wiper, ends to 3.3 V and GND
//   Pitch pot   A2 (pin 16) wiper, ends to 3.3 V and GND
// Author: Allen (with Claude)

#include <Audio.h>
#include <Bounce.h>

// ---- pins ----
const int PIN_BUTTON    = 2;
const int PIN_SWITCH    = 3;
const int PIN_VOL_POT   = A0;   // pin 14
const int PIN_PITCH_POT = A2;   // pin 16 (A1/pin 15 is the shield's optional VOL pad)

// ---- audio graph: osc -> fade (on/off) -> mixer (master gain) -> I2S L/R ----
AudioSynthWaveform   osc;
AudioEffectFade      fader;
AudioMixer4          master;
AudioOutputI2S       i2sOut;
AudioConnection      cord1(osc, 0, fader, 0);
AudioConnection      cord2(fader, 0, master, 0);
AudioConnection      cord3(master, 0, i2sOut, 0);
AudioConnection      cord4(master, 0, i2sOut, 1);
AudioControlSGTL5000 codec;

// ---- controls ----
Bounce button   = Bounce(PIN_BUTTON, 10);  // 10 ms debounce
Bounce onSwitch = Bounce(PIN_SWITCH, 10);

// ---- waveform state ----
const char *WAVE_NAMES[] = {"sine", "triangle", "saw"};
int  waveIndex   = 0;
bool naiveSaw    = false;   // class bonus: aliased saw instead of band-limited
int  pendingWave = -1;      // waveform waiting for the fade-out to finish
elapsedMillis sinceSwapFade;

const float OSC_AMP = 0.5;
const int   FADE_MS = 10;   // on/off fade
const int   SWAP_MS = 4;    // short dip when changing waveform

// ---- volume state ----
const float MIN_DB      = -60.0;
const float POT_ALPHA   = 0.05;   // one-pole smoothing of the pot readings
const float GAIN_ALPHA  = 0.1;    // one-pole smoothing of the applied gain (per ms)
const float POT_THRESH  = 0.004;  // ignore pot changes smaller than this (0..1)
float volSmooth  = 0.0;
float volUsed    = -1.0;
float gainTarget = 0.0;
float gainNow    = 0.0;

// ---- pitch state ----
const float MIN_FREQ = 55.0;      // A1
const float OCTAVES  = 5.0;       // 55 Hz .. 1760 Hz
float pitchSmooth = 0.0;
float pitchUsed   = -1.0;
float freqNow     = MIN_FREQ;

elapsedMillis sinceControlStep;
elapsedMillis sincePrint;

bool soundOn = false;

int waveType(int index) {
  switch (index) {
    case 0:  return WAVEFORM_SINE;
    case 1:  return WAVEFORM_TRIANGLE;
    default: return naiveSaw ? WAVEFORM_SAWTOOTH : WAVEFORM_BANDLIMIT_SAWTOOTH;
  }
}

// Pot position 0..1 -> linear gain, on a dB curve from MIN_DB to 0 dB.
// The bottom 1% of travel is full silence.
float potToGain(float pos) {
  if (pos < 0.01) return 0.0;
  float db = MIN_DB + (0.0 - MIN_DB) * pos;
  return powf(10.0, db / 20.0);
}

// Pot position 0..1 -> frequency, equal turn = equal number of octaves.
float potToFreq(float pos) {
  return MIN_FREQ * powf(2.0, OCTAVES * pos);
}

// Change waveform, dipping the level for a few ms so the swap doesn't click.
void requestWave(int index) {
  if (soundOn) {
    fader.fadeOut(SWAP_MS);
    pendingWave = index;
    sinceSwapFade = 0;
  } else {
    osc.begin(waveType(index));
  }
}

// One line with the four values; printed only when something changed.
void printStatus() {
  static bool  lastOn   = !soundOn;
  static int   lastWave = -1;
  static bool  lastNaive = false;
  static float lastDb   = 999.0;
  static float lastFreq = -1.0;

  float db = (gainNow > 0.001) ? 20.0 * log10f(gainNow) : -99.0;
  bool changed = soundOn != lastOn || waveIndex != lastWave || naiveSaw != lastNaive ||
                 fabsf(db - lastDb) >= 0.5 || fabsf(freqNow - lastFreq) >= 0.5;
  if (!changed) return;
  lastOn = soundOn; lastWave = waveIndex; lastNaive = naiveSaw;
  lastDb = db; lastFreq = freqNow;

  Serial.print("sound: ");
  Serial.print(soundOn ? "on " : "off");
  Serial.print("  wave: ");
  Serial.print(WAVE_NAMES[waveIndex]);
  if (waveIndex == 2) Serial.print(naiveSaw ? " (naive)" : " (band-limited)");
  Serial.print("  gain: ");
  if (db <= -99.0) Serial.print("-inf");
  else             Serial.print(db, 1);
  Serial.print(" dB  freq: ");
  Serial.print(freqNow, 1);
  Serial.println(" Hz");
}

void setup() {
  Serial.begin(115200);
  AudioMemory(12);

  pinMode(PIN_BUTTON, INPUT_PULLUP);
  pinMode(PIN_SWITCH, INPUT_PULLUP);

  codec.enable();
  codec.volume(0.6);         // fixed headphone ceiling; the pot does the rest
  codec.lineOutLevel(29);    // line out level for later (13 = loudest, 31 = quietest)

  // Start from the current pot and switch positions.
  volSmooth   = analogRead(PIN_VOL_POT) / 1023.0;
  pitchSmooth = analogRead(PIN_PITCH_POT) / 1023.0;
  pitchUsed   = pitchSmooth;
  freqNow     = potToFreq(pitchUsed);

  osc.begin(OSC_AMP, freqNow, waveType(waveIndex));
  master.gain(0, 0.0);

  soundOn = (digitalRead(PIN_SWITCH) == LOW);
  if (soundOn) fader.fadeIn(FADE_MS);
  else         fader.fadeOut(1);
}

void loop() {
  // ---- button: next waveform ----
  button.update();
  if (button.fallingEdge()) {
    waveIndex = (waveIndex + 1) % 3;
    requestWave(waveIndex);
  }

  // finish a waveform swap once the dip has faded out
  if (pendingWave >= 0 && sinceSwapFade >= SWAP_MS + 1) {
    osc.begin(waveType(pendingWave));
    pendingWave = -1;
    if (soundOn) fader.fadeIn(SWAP_MS);
  }

  // ---- switch: sound on/off with a fade ----
  onSwitch.update();
  if (onSwitch.fallingEdge() || onSwitch.risingEdge()) {
    soundOn = (onSwitch.read() == LOW);
    pendingWave = -1;
    osc.begin(waveType(waveIndex));
    if (soundOn) fader.fadeIn(FADE_MS);
    else         fader.fadeOut(FADE_MS);
  }

  // ---- pots, stepped once per ms ----
  if (sinceControlStep >= 1) {
    sinceControlStep = 0;

    // volume: smooth the reading, then glide the gain toward its target
    volSmooth += POT_ALPHA * (analogRead(PIN_VOL_POT) / 1023.0 - volSmooth);
    if (fabsf(volSmooth - volUsed) > POT_THRESH) {
      volUsed = volSmooth;
      gainTarget = potToGain(volUsed);
    }
    float step = GAIN_ALPHA * (gainTarget - gainNow);
    if (fabsf(step) > 1e-5) {
      gainNow += step;
      master.gain(0, gainNow);
    }

    // pitch: smooth the reading; the oscillator keeps its phase across changes
    pitchSmooth += POT_ALPHA * (analogRead(PIN_PITCH_POT) / 1023.0 - pitchSmooth);
    if (fabsf(pitchSmooth - pitchUsed) > POT_THRESH) {
      pitchUsed = pitchSmooth;
      freqNow = potToFreq(pitchUsed);
      osc.frequency(freqNow);
    }
  }

  // ---- Serial status, at most 4x per second ----
  if (sincePrint >= 250) {
    sincePrint = 0;
    printStatus();
  }

  // ---- Serial: aliasing demo ----
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'a') {
      naiveSaw = !naiveSaw;
      if (waveIndex == 2) requestWave(waveIndex);
    }
  }
}
