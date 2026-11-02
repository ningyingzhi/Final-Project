# Parts to Buy: Prototype 1

Updated 2026-11-02. These are only the parts we **don't own** (checked against `Parts List/parts_list.md`).
The links are Amazon searches, so pick a listing with good reviews. Diagram: `sketches/module_connections_v1.png`.

| # | Part | Qty to buy | Used for | Link |
|---|---|---|---|---|
| 1 | Seeed Studio XIAO ESP32-S3 (pre-soldered is easier) | 1 | ESP-NOW receiver in the Core. The 3 owned XIAOs go into the effect modules. | [Amazon](https://www.amazon.com/s?k=Seeed+Studio+XIAO+ESP32S3) |
| 2 | Linear Hall effect sensor 49E / SS49E (TO-92) | 1 pack (≥12; packs of 20–40 are cheap) | 3 per top face: Core + 3 modules = 12 | [Amazon](https://www.amazon.com/s?k=49E+linear+hall+effect+sensor) |
| 3 | Bluetooth audio transmitter module, KCX_BT_EMITTER (A2DP, 5 V) | 1–2 (cheap; get a spare) | In the Core, shield line out → owned Bluetooth speaker | [Amazon](https://www.amazon.com/s?k=KCX_BT_EMITTER+bluetooth+transmitter+module) |
| 4 | Neodymium disc magnets 10 × 3 mm | 1 pack (~50–100) | Holding magnets, 4 per face (~32 total) | [Amazon](https://www.amazon.com/s?k=neodymium+disc+magnets+10mm+x+3mm) |
| 5 | Neodymium disc magnets 3 × 2 mm (or 4 × 2 mm) | 1 pack (~50–100) | ID-code magnets, 3 per bottom face (12 total) | [Amazon](https://www.amazon.com/s?k=neodymium+disc+magnets+3mm+x+2mm) |
| 6 | 2-pin spring-loaded magnetic pogo connector, male + female pairs | ~5 pairs | Power contacts (5 V, GND): male on bottom faces, female on top faces | [Amazon](https://www.amazon.com/s?k=2+pin+magnetic+pogo+pin+connector+male+female) |
| 7 | Perfboard / prototype PCB assortment | 1 pack | Mounting the XIAO, pots and Hall sensors inside each module | [Amazon](https://www.amazon.com/s?k=perfboard+prototype+pcb+assortment) |
| 8 | Knob caps for 6 mm knurled shafts (fits WH148) | ~12 | The 9 effect knobs + 2 Core knobs | [Amazon](https://www.amazon.com/s?k=potentiometer+knob+6mm+knurled+shaft) |
| 9 | USB power bank, 5 V, ≥2 A *(later, only for the standalone demo)* | 1 | Powering the Core without the Mac | [Amazon](https://www.amazon.com/s?k=slim+usb+power+bank+5v+2a) |

## Notes
- **Hall sensors on 3.3 V.** Many 49E listings are rated from 3 V or 4 V. Check the listing's supply range. If it says 4.5 V minimum, buy **DRV5053** instead ([Amazon](https://www.amazon.com/s?k=DRV5053+hall+sensor)), which runs fine on 3.3 V.
- **Magnetic pogo connectors** come with their own small magnets. Place them away from the ID-code spots, or the Hall sensors will read them (test in CAD C2).
- **Already owned, no need to buy:** Teensy 4.1 + shield, 3 XIAO ESP32-S3, WH148 pots (15), tactile buttons, slide switches, breadboards, jumpers, hookup wire, soldering gear, Bluetooth speaker.
