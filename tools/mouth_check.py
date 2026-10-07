#!/usr/bin/env python3
"""Measure a generated singing clip against its reference vocal.

    python3 tools/mouth_check.py clip.mp4 vocal.mp3 --crop W:H:X:Y [--thr 70]

Reports (all measured, nothing inferred):
  * audio offset: how far the clip's own soundtrack is shifted against the reference vocal
  * mouth openness per frame: share of dark pixels inside the crop around the mouth (cavity shows dark)
  * open/close cycles: number of separate openings during the sung part
  * onset match: share of jaw-opening starts within +-0.15 s of a vocal syllable onset (after offset correction)
"""
import argparse, array, math, subprocess

ap = argparse.ArgumentParser()
ap.add_argument("clip"); ap.add_argument("vocal")
ap.add_argument("--crop", required=True, help="W:H:X:Y box around the mouth, in clip pixels")
ap.add_argument("--thr", type=int, default=70, help="grey level counted as cavity")
ap.add_argument("--fps", type=float, default=24)
a = ap.parse_args()

def env(src, rate=100):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-af", "highpass=f=200,lowpass=f=4000", "-ac", "1", "-ar", "8000",
                        "-f", "f32le", "-"], capture_output=True).stdout
    x = array.array("f"); x.frombytes(r); hop = 8000 // rate
    return [10 * math.log10(sum(v * v for v in x[i:i + hop]) / hop + 1e-12) for i in range(0, len(x) - hop, hop)]

ref = env(a.vocal); out = env(a.clip)
def err(s):
    p = [(out[i + s], ref[i]) for i in range(len(ref)) if 0 <= i + s < len(out) and ref[i] > -50]
    return sum(abs(u - v) for u, v in p) / max(1, len(p))
off = min(range(-150, 300), key=err) / 100.0
print(f"audio offset: clip soundtrack = reference shifted by {off:+.2f} s")

W, H, X, Y = (int(v) for v in a.crop.split(":"))
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", a.clip, "-vf", f"crop={W}:{H}:{X}:{Y},format=gray", "-f", "rawvideo", "-"],
                     capture_output=True).stdout
n = len(raw) // (W * H)
dark = [sum(1 for b in raw[i * W * H:(i + 1) * W * H] if b < a.thr) / (W * H) for i in range(n)]
base = sorted(dark)[n // 10]; peak = max(dark)
opn = [(d - base) / max(1e-6, peak - base) for d in dark]
state, cycles, starts = False, 0, []
for i, v in enumerate(opn):
    if not state and v > 0.35: state = True; cycles += 1; starts.append(i / a.fps)
    elif state and v < 0.15: state = False
print(f"frames {n}; openness baseline {base:.3f}, peak {peak:.3f}; open/close cycles: {cycles}")
on = []
for i in range(6, len(ref)):
    if ref[i] > -26 and ref[i] - min(ref[i - 6:i]) > 7 and (not on or i / 100 - on[-1] > 0.18): on.append(i / 100)
on_clip = [t + off for t in on]
hit = sum(1 for s in starts if any(abs(s - t) <= 0.15 for t in on_clip))
print(f"syllable onsets in reference: {len(on)} -> in clip time {[round(t, 2) for t in on_clip]}")
print(f"jaw opening starts: {[round(s, 2) for s in starts]}")
print(f"onset match: {hit}/{len(starts)} openings within 0.15 s of a syllable onset")
