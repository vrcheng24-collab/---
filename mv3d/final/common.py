"""Shared constants and helpers for the final MV.

Frame: 1920x1080 with a 2.39:1 picture (1920x804) between black bars; lyrics sit in the lower bar.
Every segment renders the 1920x804 picture as float RGB in [0,1]; the assembler adds grade, bars and type.
"""
import csv, json, math, os, subprocess
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
MV3D = os.path.dirname(HERE)
ROOT = os.path.dirname(MV3D)
PK = os.path.join(ROOT, "mvcut", "ALPHA_导演素材", "ALPHA_导演素材")
MASTER = os.path.join(PK, "09_整首音乐候选", "远去的列车.mp3")
STEMS = {"G01": 0.0, "G04": 60.70, "G07": 137.40, "G09": 164.00, "G10": 177.35, "G11": 184.00, "G12": 197.40}
W, H, FPS = 1920, 1080, 24
PH = 804; BAR = (H - PH) // 2
SONG_END = 240.456
F_SERIF = os.path.join(MV3D, "fonts", "NotoSerifCJKsc-Regular.otf")
F_SERIFB = os.path.join(MV3D, "fonts", "NotoSerifCJKsc-Bold.otf")
F_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

EN = {
 "L01": "Watching you board the train that carries you away", "L02": "The whistle drowns out all my sorrow",
 "L03": "A sudden wind sweeps across the platform", "L04": "A tear slides from the corner of my eye",
 "L05": "I want to sing you a song of yesterday", "L06": "I want time to stop at this moment",
 "L07": "In this world where people come and go", "L08": "How many hearts are truly sincere",
 "L09": "Aren't we all just passing through each other's lives", "L10": "Whose life is destined to be free of regret",
 "L11": "My dear friend, don't be sad", "L12": "Someday we will meet again",
 "L25": "In tears, I finish this song", "L26": "I hope you will always remember me",
 "L27": "On some sleepless winter night", "L28": "On some day when spring flowers bloom",
}
for a, b in zip(range(13, 25), range(1, 13)): EN[f"L{a:02d}"] = EN[f"L{b:02d}"]
LINES = [(r["line_id"], float(r["song_in"]), float(r["song_out"]), r["lyrics"], EN[r["line_id"]])
         for r in csv.DictReader(open(os.path.join(ROOT, "v8", "audio", "song_lines.csv"), encoding="utf-8-sig"))]

def ease(u): u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)
def eout(u): u = max(0.0, min(1.0, u)); return 1 - (1 - u) ** 3
def lerp(a, b, u): return a + (b - a) * u
_fc = {}
def font(p, s):
    if (p, s) not in _fc: _fc[(p, s)] = ImageFont.truetype(p, s)
    return _fc[(p, s)]

# ------------------------------------------------------------------ audio-driven jaw over the whole song
def _env(path, ss=0.0, t=None, band=(300, 3500)):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss)] + (["-t", str(t)] if t else []) + ["-i", path, "-af", f"highpass=f={band[0]},lowpass=f={band[1]}", "-ac", "1", "-ar", "8000", "-f", "f32le", "-"]
    x = np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32); h = 80; n = len(x) // h
    return 10 * np.log10((x[:n * h].reshape(n, h) ** 2).mean(1) + 1e-12)          # 100 Hz
def _servo(target, fps=100, max_deg=9.0):
    """2nd-order, slightly under-damped, speed-limited servo with a hard stop at 0 (as rig/jaw_curve.py)."""
    out = np.zeros(len(target)); x = v = 0.0; w = 2 * math.pi * 7.0; z = 0.55; dt = 1 / fps
    for i, tg in enumerate(target):
        for _ in range(4):
            a = w * w * (tg * max_deg - x) - 2 * z * w * v; v += a * dt / 4; v = max(-140, min(140, v)); x += v * dt / 4
            if x < 0: x = 0.0; v = max(0.0, v) * -0.15
        out[i] = x
    return out
def build_jaw():
    path = os.path.join(HERE, "jaw_full.json")
    if os.path.exists(path): return json.load(open(path))
    n = int(SONG_END * 100) + 1
    tgt = np.zeros(n); have = np.zeros(n, bool)
    for g, a in STEMS.items():
        e = _env(os.path.join(PK, "06_原音轨_未改时长", f"口型_{g}.mp3"))
        lv = np.clip((e - (-24)) / (-13 - (-24)), 0, 1) ** 0.8
        i0 = int(round(a * 100)); m = min(len(lv), n - i0)
        tgt[i0:i0 + m] = np.maximum(tgt[i0:i0 + m], lv[:m]); have[i0:i0 + m] |= e[:m] > -60
    em = _env(MASTER)
    for lid, a, b, zh, en in LINES:                                              # gaps: master vocal band, normalised per line
        i0, i1 = int(a * 100), min(n, int(b * 100))
        if have[i0:i1].mean() > 0.5: continue
        seg = em[i0:i1]; lo, hi = np.percentile(seg, 25), np.percentile(seg, 92)
        tgt[i0:i1] = np.clip((seg - lo) / (hi - lo + 1e-6), 0, 1) ** 1.2 * 0.85
    deg = _servo(tgt)
    fr = [float(deg[min(n - 1, int(i * 100 / FPS))]) for i in range(int(SONG_END * FPS) + 1)]
    json.dump({"fps": FPS, "frames": fr}, open(path, "w"))
    return {"fps": FPS, "frames": fr}
_JAW = None
def jaw_at(t):
    global _JAW
    if _JAW is None: _JAW = build_jaw()
    f = _JAW["frames"]; i = t * FPS
    if i < 0 or i >= len(f) - 1: return 0.0
    i0 = int(i); u = i - i0; return f[i0] * (1 - u) + f[i0 + 1] * u
def vocal_level(t): return min(1.0, jaw_at(t) / 5.0)

# ------------------------------------------------------------------ film finish (applied to every segment's picture)
_GR = {}
def finish(img, t, warmth=0.0, lift=0.03, grain=0.03, halation=1.0, vignette=0.32):
    """img: HxWx3 float RGB. Lifted blacks, split-tone, halation, vignette, grain."""
    x = img.astype(np.float32)
    lum = x.mean(-1, keepdims=True)
    x = x * (1 - lift) + lift
    x = x + (np.array([-0.02, 0.005, 0.03]) * (1 - lum) + np.array([0.035 + warmth, 0.0, -0.035 - warmth]) * lum)
    if halation:
        hi = np.clip(x - 0.70, 0, 1)
        x = x + cv2.GaussianBlur(hi, (0, 0), 12) * np.array([1.1, 0.45, 0.22]) * halation + cv2.GaussianBlur(hi, (0, 0), 40) * np.array([0.35, 0.22, 0.15]) * halation
    hh, ww = x.shape[:2]
    if (hh, ww) not in _GR:
        yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
        _GR[(hh, ww)] = (1 - vignette * (((xx - ww / 2) / (ww / 2)) ** 2 + ((yy - hh / 2) / (hh / 2)) ** 2) ** 1.25)[..., None]
    x = x * _GR[(hh, ww)]
    rng = np.random.default_rng(int(t * FPS) + 7)
    g = cv2.resize(rng.normal(0, grain, (hh // 2, ww // 2)).astype(np.float32), (ww, hh), interpolation=cv2.INTER_LINEAR)
    x = x + g[..., None] * (0.55 + 0.45 * (1 - np.clip(x.mean(-1, keepdims=True), 0, 1)))
    return np.clip(x, 0, 1)

def lyric_bar(pil, t, lyrics=True):
    """Bilingual lyric in the lower bar; fades per line."""
    if not lyrics: return
    d = ImageDraw.Draw(pil)
    for lid, a, b, zh, en in LINES:
        if a - 0.2 <= t < b:
            al = ease((t - a + 0.2) / 0.45) * (1 - ease((t - b + 0.35) / 0.35))
            if al <= 0: continue
            y = PH + BAR + BAR / 2
            d.text((W / 2, y - 16), "  ".join(zh), font=font(F_SERIF, 30), fill=(int(238 * al), int(232 * al), int(222 * al)), anchor="mm")
            d.text((W / 2, y + 26), en, font=font(F_SERIF, 17), fill=(int(150 * al), int(146 * al), int(140 * al)), anchor="mm")

def splat(img, x, y, col, b):
    hh, ww = img.shape[:2]
    m = (x >= 0) & (x < ww - 1) & (y >= 0) & (y < hh - 1) & (b > 0.002)
    x, y, col, b = x[m], y[m], col[m], b[m]
    xi, yi = x.astype(np.int32), y.astype(np.int32); fx, fy = (x - xi).astype(np.float32), (y - yi).astype(np.float32)
    for ox, oy, w in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        np.add.at(img, (yi + oy, xi + ox), col * (b * w)[:, None])
def glow(img, k=1.0):
    return img + (cv2.GaussianBlur(img, (0, 0), 3) * 0.6 + cv2.GaussianBlur(img, (0, 0), 18) * 0.35 + cv2.GaussianBlur(img, (0, 0), 60) * 0.18) * k
