# Module Link (stack order detection)

Updated 2026-11-02. This replaces the UART daisy chain. Older versions are in `archive/`.

## Prototype 1: Hall ID + ESP-NOW
- **ID code.** The bottom face of every module (and the speaker cradle) has 3 small code magnets, each set to N, S or none. That gives 27 IDs. The holding magnets are separate and kept away from the code spots.
- **Reading.** The top face of every module (and the Core) has 3 linear Hall sensors right under the code spots. Each reading is thresholded into N / S / none, giving the ID of the block above, or "nothing".
- **Reporting.** Every ~50 ms, each XIAO broadcasts `{my_id, above_id, knob values}` over ESP-NOW to the Core's XIAO, which forwards it to the Teensy by UART.
- **Building the chain.** The Core starts from its own sensors (the block directly above it), then follows each module's `above_id` up to the speaker or empty. A module missing for more than ~200 ms counts as removed. The Core rebuilds the chain with a short fade.
- **Power.** 2 contacts (GND, 5 V): pogo pins on the bottom, flat pads on the top. Magnet polarity keys the rotation so 5 V can't touch GND.
- **Build order:**
  1. Breadboard 1 Hall sensor + 1 magnet and calibrate the N / S / none thresholds.
  2. ESP-NOW between 2 XIAOs.
  3. 3-sensor ID reading.
  4. Core chain building.
  5. Magnetic faces (CAD C2: check that the holding magnets don't swamp the code sensors).
