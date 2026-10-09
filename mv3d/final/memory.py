"""Memories: the user's footage, shown as small-gauge film projected in the dark.

Inside the bar everything is 2.39:1 and sharp; her memories are a smaller, warmer, softer gate with weave, flicker and dust.
The low resolution of the source becomes part of the language: memories are never as sharp as the present.
"""
import os, sys
import cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

CLIPS = {
    "B02": "01_原片_未定稿/ALPHA_B02_G03_原片.mp4", "B03": "01_原片_未定稿/ALPHA_B03_G05_原片.mp4", "B04": "01_原片_未定稿/ALPHA_B04_G05_原片.mp4",
    "B05": "01_原片_未定稿/ALPHA_B05_G06_原片.mp4", "B06": "01_原片_未定稿/ALPHA_B06_G07_原片.mp4", "B07": "01_原片_未定稿/ALPHA_B07_G11B_原片.mp4",
    "B09": "01_原片_未定稿/ALPHA_B09_G13_原片.mp4", "B11": "01_原片_未定稿/ALPHA_B11_G14_原片.mp4", "B12": "01_原片_未定稿/ALPHA_B12_G00_原片.mp4",
    "B13": "01_原片_未定稿/ALPHA_B13_G04_原片.mp4", "B14": "01_原片_未定稿/ALPHA_B14_G12_原片.mp4", "B15": "01_原片_未定稿/ALPHA_B15_G01_原片.mp4",
}
CROPS = {"B06": (111, 62, 632, 356)}                 # B06 opens with a baked-in vignette: use the clean centre
_frames = {}
def clip_frame(clip, src_t):
    """Frame of a clip at source time src_t (s), cached per clip for sequential access."""
    if clip not in _frames:
        _frames.clear()
        cap = cv2.VideoCapture(os.path.join(PK, CLIPS[clip])); fr = []
        while True:
            ok, f = cap.read()
            if not ok: break
            if clip in CROPS:
                x, y, w, h = CROPS[clip]; f = cv2.resize(f[y:y + h, x:x + w], (854, 480), interpolation=cv2.INTER_CUBIC)
            fr.append(f)
        _frames[clip] = fr
    fr = _frames[clip]; i = int(np.clip(round(src_t * FPS), 0, len(fr) - 1))
    return fr[i]

GH = 610                                             # gate height on the 804 picture
_gate = {}
def gate_mask(w, h):
    if (w, h) not in _gate:
        m = np.zeros((h + 80, w + 80), np.float32); r = 26
        cv2.rectangle(m, (40 + r, 40), (40 + w - r, 40 + h), 1.0, -1); cv2.rectangle(m, (40, 40 + r), (40 + w, 40 + h - r), 1.0, -1)
        for cx, cy in ((40 + r, 40 + r), (40 + w - r, 40 + r), (40 + r, 40 + h - r), (40 + w - r, 40 + h - r)): cv2.circle(m, (cx, cy), r, 1.0, -1, cv2.LINE_AA)
        _gate[(w, h)] = cv2.GaussianBlur(m, (0, 0), 3.5)
    return _gate[(w, h)]

def memory(t, clip, src0, t0, t1, speed=1.0, zoom=(1.0, 1.05), pan=(0.0, 0.0), blur=None, warm=1.0):
    """Picture (PH x W float RGB) for song time t of a memory segment that starts at song t0, playing `clip` from src0."""
    src_t = src0 + (t - t0) * speed
    f = clip_frame(clip, src_t).astype(np.float32) / 255.0
    if blur:                                         # privacy blur boxes in source pixels
        for bx, by, bw, bh in blur:
            f[by:by + bh, bx:bx + bw] = cv2.GaussianBlur(f[by:by + bh, bx:bx + bw], (0, 0), 9)
    u = ease((t - t0) / max(0.01, t1 - t0))
    z = lerp(zoom[0], zoom[1], u); px, py = lerp(0, pan[0], u), lerp(0, pan[1], u)
    gw = int(GH * 854 / 480)
    rng = np.random.default_rng(int(t * FPS) * 7 + 3)
    wx, wy = rng.normal(0, 0.8), rng.normal(0, 1.1)                                      # gate weave
    M = np.float32([[gw / 854 * z, 0, gw / 2 * (1 - z) + px * gw + wx], [0, GH / 480 * z, GH / 2 * (1 - z) + py * GH + wy]])
    img = cv2.warpAffine(f[..., ::-1].copy(), M, (gw, GH), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    # film memory: softer, warmer, faded blacks, a breath of halation
    img = cv2.GaussianBlur(img, (0, 0), 0.7)
    lum = img.mean(-1, keepdims=True); img = lum + (img - lum) * 0.78
    img = img * np.array([1.0, 0.94, 0.82]) ** warm * 0.92 + np.array([0.055, 0.040, 0.030])
    img = img + bblur(np.clip(img - 0.7, 0, 1), 10) * np.array([0.9, 0.45, 0.2])
    img *= 0.94 + 0.06 * rng.random()                                                    # flicker
    for _ in range(rng.integers(0, 4)):                                                  # dust and hair
        x, y = int(rng.uniform(0, gw)), int(rng.uniform(0, GH))
        if rng.random() < 0.8: cv2.circle(img, (x, y), int(rng.uniform(1, 3)), (0.02, 0.02, 0.02), -1, cv2.LINE_AA)
        else: cv2.ellipse(img, (x, y), (int(rng.uniform(8, 30)), 2), rng.uniform(0, 180), 0, 200, (0.03, 0.03, 0.03), 1, cv2.LINE_AA)
    if rng.random() < 0.25:
        x = int(rng.uniform(0.1, 0.9) * gw); cv2.line(img, (x, 0), (x + int(rng.normal(0, 6)), GH), (0.75, 0.72, 0.66), 1, cv2.LINE_AA)
    yy, xx = np.mgrid[0:GH, 0:gw].astype(np.float32)
    img *= (1 - 0.45 * (((xx - gw / 2) / (gw / 2)) ** 2 + ((yy - GH / 2) / (GH / 2)) ** 2) ** 1.4)[..., None]
    # into the dark frame, with the projector's spill around the gate
    m = gate_mask(gw, GH)
    out = np.zeros((PH, W, 3), np.float32) + np.array([0.008, 0.007, 0.008])
    X0, Y0 = W // 2 - gw // 2 - 40, PH // 2 - GH // 2 - 40
    canvas = np.zeros((GH + 80, gw + 80, 3), np.float32); canvas[40:40 + GH, 40:40 + gw] = img
    spill = cv2.GaussianBlur(cv2.resize(img, (gw // 8, GH // 8)), (0, 0), 6)
    spill = cv2.resize(spill, (gw, GH)).mean((0, 1)) * 0.20
    big = np.zeros((PH, W), np.float32); cv2.rectangle(big, (X0 + 40, Y0 + 40), (X0 + 40 + gw, Y0 + 40 + GH), 1.0, -1)
    out += bblur(big, 70)[..., None] * spill
    reg = out[Y0:Y0 + GH + 80, X0:X0 + gw + 80]
    out[Y0:Y0 + GH + 80, X0:X0 + gw + 80] = reg * (1 - m[..., None]) + canvas * m[..., None]
    # the gate opens and closes with a quick flicker
    a = ease((t - t0) / 0.18) * (1 - ease((t - t1 + 0.12) / 0.12))
    if t - t0 < 0.25: a *= 0.6 + 0.4 * rng.random()
    return out * a
