#!/usr/bin/env python3
"""Audio -> servo jaw curve for the ALPHA head rig.

The physical head has one degree of freedom at the mouth: the lower jaw (lower lip + chin) rotates down/back
around two side hinges; the upper lip and cheek panels are fixed. So singing is described completely by one
angle over time. This script derives that angle the way an animatronic audio-servo board would:

  1. band-limited vocal envelope (300-3500 Hz, 10 ms frames)
  2. noise gate + level -> openness 0..1
  3. optional syllable table (start, size) scales each syllable: small / mid / big (vowel height)
  4. servo dynamics: slightly under-damped 2nd-order response with a speed limit and a hard mechanical stop
     at "closed", so the jaw starts fast, stops hard and shows a tiny rebound

Output: JSON {fps, max_deg, frames:[deg,...]} plus a CSV for editing.

    python3 jaw_curve.py vocal.wav --syllables syllables.csv --out curve.json
"""
import argparse, array, csv, json, math, subprocess

ap = argparse.ArgumentParser()
ap.add_argument("audio")
ap.add_argument("--syllables", help="CSV: start_s,size (size = small|mid|big|0..1)")
ap.add_argument("--out", default="curve.json")
ap.add_argument("--fps", type=float, default=24)
ap.add_argument("--max-deg", type=float, default=9.0, help="jaw angle at full open (the gap then equals the upper-lip height)")
ap.add_argument("--gate-db", type=float, default=-24.0)
ap.add_argument("--full-db", type=float, default=-13.0)
ap.add_argument("--lead", type=float, default=0.04, help="seconds the jaw command leads the sound (servo latency)")
a = ap.parse_args()

SR = 8000
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", a.audio, "-af", "highpass=f=300,lowpass=f=3500",
                      "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
x = array.array("f"); x.frombytes(raw)
HOP = SR // 100
env = []
for i in range(0, len(x) - HOP, HOP):
    s = sum(v * v for v in x[i:i + HOP]) / HOP
    env.append(10 * math.log10(s + 1e-12))
dur = len(env) / 100.0

# level -> openness
lvl = [min(1.0, max(0.0, (d - a.gate_db) / (a.full_db - a.gate_db))) for d in env]
lvl = [v ** 0.8 for v in lvl]

# syllable sizes
SIZE = {"small": 0.38, "mid": 0.68, "big": 1.0}
scale = [0.75] * len(lvl)
if a.syllables:
    rows = [r for r in csv.reader(open(a.syllables, encoding="utf-8-sig")) if r and not r[0].startswith("#")]
    rows = [(float(r[0]), SIZE.get(r[1].strip(), None) or float(r[1])) for r in rows if r[0].replace(".", "", 1).isdigit()]
    rows.sort()
    for k in range(len(scale)):
        t = k / 100.0
        cur = [s for st, s in rows if st - 0.05 <= t]
        scale[k] = cur[-1] if cur else rows[0][1]
target = [l * s for l, s in zip(lvl, scale)]

# servo: 2nd-order, under-damped, speed-limited, hard stop at 0
dt = 0.001
wn, zeta, vmax = 2 * math.pi * 7.0, 0.55, 9.0   # natural freq (Hz->rad/s), damping, max speed (openness/s)
pos, vel, out = 0.0, 0.0, []
n = int(dur / dt)
for i in range(n):
    t = i * dt + a.lead
    k = min(len(target) - 1, int(t * 100))
    acc = wn * wn * (target[k] - pos) - 2 * zeta * wn * vel
    vel = max(-vmax, min(vmax, vel + acc * dt))
    pos += vel * dt
    if pos < 0:                      # hits the closed stop: small bounce
        pos, vel = 0.0, -vel * 0.25
    out.append(pos)
frames = []
for f in range(int(dur * a.fps)):
    i = min(len(out) - 1, int(f / a.fps / dt))
    frames.append(round(out[i] * a.max_deg, 3))
json.dump({"fps": a.fps, "max_deg": a.max_deg, "duration": dur, "frames": frames}, open(a.out, "w"))
with open(a.out.rsplit(".", 1)[0] + ".csv", "w") as f:
    f.write("frame,time_s,jaw_deg\n")
    for k, d in enumerate(frames):
        f.write(f"{k},{k / a.fps:.3f},{d}\n")
print(f"{len(frames)} frames, {dur:.2f}s, peak {max(frames):.1f} deg")
