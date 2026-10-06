# ALPHA head rig — audio-driven jaw motion reference

A simplified mechanical model of ALPHA's head, built from the white-model photos, used to produce motion
references for video models (Seedance `@视频1`). It shows how the head moves, not how it looks; the look still
comes from the character card.

- `head.html` — three.js rig. Fixed: crown, forehead, nose, cheeks, upper lip, mouth cavity (gear motors + servos).
  One moving mouth part: the jaw (lower lip + chin) rotating down/back around a hinge axis behind the cheeks.
  Extras: stepped neck yaw, eyebrow lift and eyelid drop on loud notes, ear turbine spin.
  URL params: `view=34|front|side|mouth`, `mode=white|paint`, `w`, `h`.
- `jaw_curve.py` — vocal audio → jaw angle per frame (band envelope, gate, per-syllable size, servo dynamics with
  speed limit, hard stop and small rebound). Max 9° = gap equal to the upper-lip thickness.
- `render.cjs` — headless Chromium renders frames or the jaw-state stills (`--stills <dir>`).
- `make_ref.sh <vocal.wav> <name> [syllables.csv] [yaw_json]` — everything above, outputs `out/<name>_*.mp4`.
- `line08_syllables.csv` — example syllable table (start seconds, small/mid/big).

Setup: `npm install` here (three.js); Playwright and Chromium come from the global install
(`NODE_PATH=$(npm root -g)`).
