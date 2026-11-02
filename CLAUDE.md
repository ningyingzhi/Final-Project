# Final Project: Noguchi-inspired Modular Synth

MIT 21M.389/589 Audio Computing (Fall 2026) final project by Allen + teammate. It's a modular synth: one central Core sound engine plus snap-on effect modules, each in a sculptural Noguchi-inspired enclosure. **Prototype 1** is a vertical stack: the Core synth on the ground, then ADSR / Reverb / Parametric EQ modules in any order, with the speaker on top. The Core (Teensy 4.1) runs all the DSP in stack order.

## Files
- **Everything for this project lives in this folder.**
- `notes/central_engine.md` is the architecture. `notes/module_topology.md` covers stack-order detection. `notes/dsp_libraries.md` covers libraries.
- `notes/archive/` holds old brainstorms and earlier plan versions. Archive, don't delete.
- `plan.md` holds the phased DSP + CAD plan. `parts_to_buy.md` lists the extra parts to order. `PROJECT_LOG.md` tracks the status of each step.
- Concept sketch images are in `sketches/`, reference images in `reference/`.
- **All code lives in `code/`** (see rule 10).
- Course slides and syllabus: `/Users/ningyingzhi/Desktop/Grad School/MIT/Audio Computing/Slides`.

## Rules
1. **Parts first.** Before planning or suggesting hardware, check `/Users/ningyingzhi/Desktop/All Projects/Parts List/parts_list.md` and use owned parts first. If something isn't owned and is needed, suggest it and mark it *to buy*.
2. **Standalone.** The finished system runs with no laptop: Teensy-based and powered by a power bank. The Mac (Max, SuperCollider, Python) is for prototyping and analysis only.
3. **Tied to the class.** Every major feature should connect to course content (labs, lectures). Say which topic it comes from.
4. **Start from lab code.** Prototype DSP in Python from our lab code, then port it to the Teensy (Teensy Audio Library, then the F32 stack in `notes/dsp_libraries.md`). Keep the Python version as the reference for testing. Using AI for help with code is fine.
5. **Team.** Each teammate writes their own code and contributes an equal share. Keep track of who did what for the required collaboration note.
6. **Deadlines can't be extended.** Favor getting a working minimum version early over polish.
7. **Software stack.** Prototype 1 uses only the Teensy Audio Library. The later F32 stack (OpenAudio, DaisySP, hexefx, ConvolutionUP, CMSIS) is in `notes/dsp_libraries.md`. Check there before adding a library.
8. **Teensy hygiene.** Don't use the audio shield's pins (6–8, 10–13, 18–21, 23). Pots go to 3.3 V, never 5 V. Ramp gain changes to avoid clicks.
9. **Writing style.** Keep docs and plans concise. Move superseded docs to `notes/archive/` instead of overwriting design history.
10. **Code layout.** Every piece of code goes in `code/`, with Arduino and Python kept separate:
   - `arduino_code/`: this is the Arduino IDE sketchbook, so set the sketchbook location to it.
     - `sketches/NN_name/NN_name.ino`: one sketch per folder, numbered in build order (e.g. `01_waveform_osc`). The folder name must match the `.ino`.
     - `libraries/`: third-party Teensy libraries (OpenAudio, hexefx, DaisySP, ConvolutionUP) plus our own, such as the DaisySP F32 wrapper and shared code. Never edit the installed Teensy `Audio.h`.
   - `python_code/`:
     - `prototypes/`: DSP prototypes started from lab code.
     - `tests/`: Python-vs-Teensy comparisons.
     - `export/`: scripts that write C headers (coefficients, wavetables, IRs) into `arduino_code/`.
     - `tools/`: helper scripts, e.g. the `watercolor/` sketch generators.
   - `data/`: IRs, measurements and recordings shared by both.
   - Give each sketch or script a short header comment saying what it does, which plan step it's for, and who wrote it.
11. **Project log.** When a `plan.md` step is tested and done, update its row in `PROJECT_LOG.md` (status, date, who, sketch/file, one-line note). Mark partly working steps 🟡.
