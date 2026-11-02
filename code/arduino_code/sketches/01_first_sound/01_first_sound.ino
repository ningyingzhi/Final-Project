// 01_first_sound: plan step 1.1 (toolchain + first sound).
// Plays a 440 Hz test sine on the audio shield's headphone jack and prints
// audio CPU / memory use to Serial once a second.
// Hardware: Teensy 4.1 + audio shield (SGTL5000), headphones on the shield jack.
// Author: Allen (with Claude)

#include <Audio.h>

AudioSynthWaveformSine sine1;
AudioOutputI2S         i2sOut;
AudioConnection        cordL(sine1, 0, i2sOut, 0);
AudioConnection        cordR(sine1, 0, i2sOut, 1);
AudioControlSGTL5000   codec;

elapsedMillis sincePrint;

void setup() {
  Serial.begin(115200);
  AudioMemory(8);

  codec.enable();
  codec.volume(0.5);        // headphone level, 0.0-1.0; keep it low at first

  sine1.frequency(440);
  sine1.amplitude(0.3);

  Serial.println("01_first_sound: 440 Hz sine running");
}

void loop() {
  if (sincePrint >= 1000) {
    sincePrint = 0;
    Serial.print("CPU: ");
    Serial.print(AudioProcessorUsage());
    Serial.print("%  max ");
    Serial.print(AudioProcessorUsageMax());
    Serial.print("%   Mem: ");
    Serial.print(AudioMemoryUsage());
    Serial.print(" blocks  max ");
    Serial.println(AudioMemoryUsageMax());
  }
}
