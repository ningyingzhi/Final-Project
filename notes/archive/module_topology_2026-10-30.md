# Free-form Module Connection Logic

Draft, 2026-10-30. The goal: 4 effect modules that attach to the Core or to each other on any face, in any order. The Core works out the signal chain from the shape.

## 1. Rule: sound flows outward from the Core like a tree
- **Distance from the Core = order.** Signal passes through modules in the order it reaches them, moving away from the Core.
- **A module with two or more modules attached further out = a split.** The signal goes down each branch in parallel.
- **Each branch ends at an outermost module (a leaf).** All leaf outputs are **summed** to the master output and the speaker. A dry/wet knob on the Core blends in the dry synth.
- **Shared parts are processed once.** In `Core → A → (B, C)`, A runs once and its output feeds both B and C.

Examples with 4 effects (L = Lo-fi, F = Filter, D = Delay, R = Reverb):
```
Stack:          Core─L─F─D─R               →  synth → L → F → D → R → out            (pure series)
Two arms:       Core─L─F   Core─D─R        →  synth → (L→F) + (D→R) → out             (2 parallel chains)
Fork:           Core─L─┬─F                 →  synth → L → ( F + (D→R) ) → out         (series, then split)
                       └─D─R
Star:           Core with L, F, D, R each on its own face  →  synth → (L + F + D + R) → out  (all parallel)
```
This generalizes "vertical = series, horizontal = parallel" without needing to know which way is up.

## 2. Discovery: how the Core learns the shape
- Each module has a small MCU (start with the 3 owned XIAO ESP32-S3s, then RP2040s *to buy*), with **one data line per face**.
- Faces are numbered on each module (0 to N-1).
- **Flood + spanning tree**, the same idea as network discovery:
  1. The Core sends `HELLO(from=Core, face=k)` out of each of its faces.
  2. A module that receives its first HELLO on face f records **parent = f**. It replies `I_AM(id, type, parent face)` back toward the Core, then forwards HELLO out of all its other faces.
  3. A module that receives a *second* HELLO on another face ignores it and marks that face as a non-tree link. That breaks any loops, for example when magnets close a ring.
  4. Replies are routed back through the parents. The Core ends up with the full tree: `Core.f2 → Filter#3.f0, Filter#3.f1 → Delay#1.f0, …`
- **Heartbeat** about every 50 ms. A missing reply, or a new I_AM, means the topology changed.
- **Knobs:** each module sends `PARAM(id, knob, value)` toward the Core whenever a knob moves, routed through its parents.

## 3. Rebuilding the audio graph
On every topology change, the Core:
1. Walks the tree depth-first and builds the series / split / sum graph from rule 1.
2. Checks the CPU / RAM budget against a per-effect cost table. If it's over budget, it bypasses the outermost heavy effects and lights a warning LED on them.
3. Crossfades from the old graph to the new one over about 20 ms, so there are no clicks. (OpenAudio patch cords can be connected and disconnected at runtime, or effects can be pre-instantiated and only the routing switched.)
4. Updates the display, and each module's LED shows its position (step number or color).

Duplicate types (e.g. two Delays) are fine, because each module has a unique ID and gets its own effect instance.

## 4. The heavy Space module (Teensy #2) placed anywhere
- Every face also carries a **shared analog audio bus** (SEND and RETURN), wired straight through every module.
- So wherever the Space module sits in the tree, the Core can send its branch's signal out on SEND and get the processed audio back on RETURN.
- Limit: only one bus pair, so one heavy module at a time.

## 5. Connector face (any face mates with any face)
Pins: **GND, 5 V, DATA (half-duplex, per face), AUDIO_SEND, AUDIO_RETURN**, so 5 contacts.
- **Hermaphroditic layout.** Use a mirror-symmetric arrangement of pogo pins and flat pads, so two identical faces mate.
- **Magnets do the keying.** An alternating N/S magnet pattern only lets faces join in the correct rotation. That protects the power pins from being reversed.
- Add a polyfuse or ideal diode on each module's 5 V in, in case of a bad contact.

## 6. Build order
1. On a breadboard, have 2 XIAOs + the Core exchange HELLO / I_AM over wires (no magnets yet).
2. Build the tree in Core code and print the graph to Serial.
3. Map the tree to the Teensy audio graph with crossfades.
4. Then build the physical faces (CAD C1.2 / C2.1).
