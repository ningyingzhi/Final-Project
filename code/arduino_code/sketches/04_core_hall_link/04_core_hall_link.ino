// 04_core_hall_link: combined test of both breadboards (module_topology.md build
// step 3 + 5, preview of P5). Sketch 02's synth, gated by what sits on top of the Core.
// The XIAO test board (sketch 03_hall_id_test) is powered by the Core through the
// pogo pair and reports the Hall ID of the "block above" every 50 ms over a UART wire
// (stand-in for ESP-NOW). Here:
//   ID 0 (nothing above) or link lost -> sound fades out
//   ID 1..26 (a block above)          -> sound fades in, waveform = (ID - 1) % 3
// Unplug the pogo pair or lift the magnet card and the sound stops within ~200 ms.
// Class link: envelopes / click-free gain ramps (lab 1), stack order = signal order.
// Hardware: everything from sketch 02 (unchanged), plus 3 wires to the XIAO board:
//   Teensy VIN (5 V from USB) -> female pogo 5V   -> male pogo -> XIAO 5V
//   Teensy GND                -> female pogo GND  -> male pogo -> XIAO GND
//   Teensy pin 0 (RX1)        <- XIAO D6 (TX)     (jumper; ESP-NOW replaces it in P5)
//   XIAO USB unplugged while pogo-powered (flash it first, then unplug).
// Serial Monitor @115200 on the Teensy: synth status + link/ID changes. 'a' = naive saw.
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

bool soundOn  = false;
bool switchOn = false;

// ---- link to the XIAO test board ----
const int LINK_TIMEOUT_MS = 200;  // no report for this long = block removed
int  aboveId = 0;                 // Hall ID of the block above, 0 = nothing
bool linkUp  = false;
elapsedMillis sinceLink;
char linkBuf[40];
int  linkLen = 0;

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

// Fade the sound in or out; plays only when the switch is on and a block is above.
void updateSound() {
  bool want = switchOn && aboveId != 0;
  if (want == soundOn) return;
  soundOn = want;
  pendingWave = -1;
  osc.begin(waveType(waveIndex));
  if (soundOn) fader.fadeIn(FADE_MS);
  else         fader.fadeOut(FADE_MS);
}

void setAbove(int id) {
  if (id == aboveId) return;
  aboveId = id;
  Serial.print("above Core: ");
  if (id == 0) Serial.println("nothing");
  else { Serial.print("block ID "); Serial.println(id); }
  if (id != 0) {
    waveIndex = (id - 1) % 3;
    requestWave(waveIndex);
  }
  updateSound();
}

// Read "ID,<id>,<d0>,<d1>,<d2>" lines from the XIAO on Serial1.
void readLink() {
  while (Serial1.available()) {
    char c = Serial1.read();
    if (c == '\n') {
      linkBuf[linkLen] = 0;
      linkLen = 0;
      if (strncmp(linkBuf, "ID,", 3) != 0) continue;
      int id = atoi(linkBuf + 3);
      if (id < 0 || id > 26) continue;
      sinceLink = 0;
      if (!linkUp) { linkUp = true; Serial.println("link: up"); }
      setAbove(id);
    } else if (c != '\r' && linkLen < (int)sizeof(linkBuf) - 1) {
      linkBuf[linkLen++] = c;
    }
  }
  if (linkUp && sinceLink > LINK_TIMEOUT_MS) {
    linkUp = false;
    Serial.println("link: lost (pogo unplugged or XIAO off)");
    setAbove(0);
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
  Serial1.begin(115200);     // RX1 = pin 0, from XIAO D6
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

  switchOn = (digitalRead(PIN_SWITCH) == LOW);
  soundOn  = false;          // waits for a block on top
  fader.fadeOut(1);
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
    switchOn = (onSwitch.read() == LOW);
    updateSound();
  }

  // ---- link: what sits on top of the Core ----
  readLink();

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
