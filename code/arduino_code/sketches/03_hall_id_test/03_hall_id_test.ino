// 03_hall_id_test: module-link build steps 1 + 3 (notes/module_topology.md),
// also feeds CAD C1/C2 (face standard, test face pair).
// Reads 3 linear Hall sensors, zeroes them with no magnet nearby, and turns each
// reading into N / S / none with a threshold + hysteresis. The 3 states form the
// base-3 ID of the block above (0 = nothing, 1..26 = a module).
// Use it to: calibrate thresholds, measure signal vs gap, check crosstalk between
// sensor spots, and check that the pogo connectors' magnets don't fool the sensors.
// Class link: sampling / quantization (ADC counts -> mV), noise and averaging (lab 1).
// Hardware: XIAO ESP32-S3 / S3 Plus on its own breadboard (the module's real reader),
// or Teensy 4.1. Board > XIAO_ESP32S3 picks the XIAO pins automatically.
//              XIAO ESP32-S3          Teensy 4.1
//   Hall 0 out  D0 (A0, GPIO1)        A10 (pin 24)
//   Hall 1 out  D1 (A1, GPIO2)        A11 (pin 25)
//   Hall 2 out  D2 (A2, GPIO3)        A12 (pin 26)
//   Hall VCC -> 3V3 (check your part runs at 3.3 V), Hall GND -> GND
//   Only 1 sensor wired? Set NUM_SENSORS to 1 (unwired pins float and read noise).
// Serial Monitor @115200, keys:
//   c = recalibrate (no magnets near!)   r = reset peaks   p = plotter mode on/off
//   + / - = threshold up / down 10 mV
// Author: Allen (with Claude)

const int NUM_SENSORS = 3;
#if defined(ARDUINO_ARCH_ESP32)
const int HALL_PINS[3] = { A0, A1, A2 };     // XIAO D0, D1, D2 (ADC1, OK with WiFi on)
#else
const int HALL_PINS[3] = { A10, A11, A12 };  // Teensy pins 24, 25, 26
#endif

const float VREF_MV  = 3300.0;
const int   ADC_BITS = 12;
const float ADC_MAX  = (1 << ADC_BITS) - 1;

float thOnMv  = 80.0;   // |delta| above this -> magnet detected
float thOffMv = 50.0;   // falls back to none below this (hysteresis)

float baseMv[3];        // reading with no magnet
float peakMv[3];        // largest |delta| since last reset, keeps sign
int   state[3];         // 0 = none, 1 = N, 2 = S
bool  plotMode = false;

float readMv(int pin) {
#if defined(ARDUINO_ARCH_ESP32)
  uint32_t sum = 0;                             // ESP32: factory-calibrated mV, avg of 16
  for (int k = 0; k < 16; k++) sum += analogReadMilliVolts(pin);
  return sum / 16.0;
#else
  return analogRead(pin) * VREF_MV / ADC_MAX;   // Teensy: hardware averaging set in setup
#endif
}

void calibrate() {
  for (int i = 0; i < NUM_SENSORS; i++) {
    float sum = 0;
    for (int k = 0; k < 256; k++) { sum += readMv(HALL_PINS[i]); delay(1); }
    baseMv[i] = sum / 256.0;
    peakMv[i] = 0;
    state[i]  = 0;
  }
  if (!plotMode) {
    Serial.print("Calibrated, baseline mV:");
    for (int i = 0; i < NUM_SENSORS; i++) { Serial.print(" "); Serial.print(baseMv[i], 0); }
    Serial.println("  (expect ~1650 for a ratiometric sensor on 3.3 V)");
  }
}

// 49E / DRV5053-style: output goes UP for one pole and DOWN for the other.
// "S" here just means delta > 0; check with a marked magnet and swap if needed.
int classify(int prev, float d) {
  float a = fabsf(d);
  if (prev == 0) return (a > thOnMv) ? (d > 0 ? 2 : 1) : 0;
  return (a < thOffMv) ? 0 : (d > 0 ? 2 : 1);
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(ADC_BITS);
#if !defined(ARDUINO_ARCH_ESP32)
  analogReadAveraging(16);
#endif
  delay(500);
  calibrate();
}

void handleKeys() {
  while (Serial.available()) {
    char ch = Serial.read();
    if (ch == 'c') calibrate();
    else if (ch == 'r') { for (int i = 0; i < NUM_SENSORS; i++) peakMv[i] = 0; }
    else if (ch == 'p') plotMode = !plotMode;
    else if (ch == '+' || ch == '-') {
      float step = (ch == '+') ? 10.0 : -10.0;
      thOnMv  = max(20.0f, thOnMv + step);
      thOffMv = thOnMv * 0.6;
      Serial.print("Threshold on/off mV: "); Serial.print(thOnMv, 0);
      Serial.print(" / "); Serial.println(thOffMv, 0);
    }
  }
}

void loop() {
  handleKeys();

  float d[3];
  int id = 0, mult = 1;
  for (int i = 0; i < NUM_SENSORS; i++) {
    d[i] = readMv(HALL_PINS[i]) - baseMv[i];
    if (fabsf(d[i]) > fabsf(peakMv[i])) peakMv[i] = d[i];
    state[i] = classify(state[i], d[i]);
    id += state[i] * mult;
    mult *= 3;
  }

  static uint32_t last = 0;
  uint32_t period = plotMode ? 20 : 200;
  if (millis() - last < period) return;
  last = millis();

  if (plotMode) {                       // Serial Plotter: one line per sample
    for (int i = 0; i < NUM_SENSORS; i++) {
      Serial.print("h"); Serial.print(i); Serial.print(":"); Serial.print(d[i], 1);
      Serial.print(i < NUM_SENSORS - 1 ? "," : "\n");
    }
    return;
  }

  const char* NAMES[3] = { "-", "N", "S" };
  for (int i = 0; i < NUM_SENSORS; i++) {
    Serial.print("H"); Serial.print(i); Serial.print(" ");
    Serial.print(d[i] >= 0 ? "+" : ""); Serial.print(d[i], 0); Serial.print(" mV ");
    Serial.print(NAMES[state[i]]);
    Serial.print(" (peak "); Serial.print(peakMv[i], 0); Serial.print(")   ");
  }
  Serial.print("ID "); Serial.println(id);
}
