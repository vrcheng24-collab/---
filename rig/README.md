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

## Film-grade version (Blender / Cycles) — `blender/alpha_head.py`

The three.js rig above is a quick mechanism preview. The Blender build is the production asset:

- Face plates are cut from one sculpted face surface along drawn seam lines (`SEAMS_R`, `SEAMS_C`), so the plates
  conform to the face and meet with even seams; each plate gets thickness and bevelled edges. Regions are named and
  coloured by seed points (`REGIONS`): teal lips and forehead "A", silver plates, the jaw plates.
- Mechanics: fixed upper lip / nose / cheeks; one hinged jaw (lower lip + chin plates) with jaw arms and two pistons
  that track the jaw; mouth cavity with gold gear motors and red servos; lens eyes with glass, glowing iris, eight
  aperture blades, lens ring, three upper and two lower shutter lids; 13-link chain eyebrows; ear turbines;
  yellow helmet, fins, neck rods.
- Expressions (`EXPR`): neutral, tender, high, closing — brow inner/outer lift, lids, iris aperture, lip-corner drop.
- Animation reads the same `jaw_curve.py` output; neck turns in servo steps; expression changes over the line.

Run with the `bpy` wheel (`pip install bpy` into a Python 3.11 venv):

    python blender/alpha_head.py --still out/s.png --view 34|front|mouth|eye|low --jaw 6 --expr tender
    python blender/alpha_head.py --anim out/frames --curve out/line08_curve.json --view 34 --res 960x402 --samples 24
