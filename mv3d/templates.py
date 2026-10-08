#!/usr/bin/env python3
"""五个风格模板，同一段剪辑（歌曲 137.4–150.0 秒：列车开走 → 空站台 → 她在站台上唱）。

    python3 templates.py woodcut|riso|paint|film|type [--still t]     # -> out/tpl_<name>.mp4
    python3 templates.py all

素材：B05（列车开走）、B06（站台，原绑定 137.4 秒的演唱镜头）。每一帧是歌曲时间的函数。
"""
import math, os, subprocess, sys
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PK = os.path.join(HERE, "..", "mvcut", "ALPHA_导演素材", "ALPHA_导演素材")
W, H, FPS = 1280, 720, 24
T0, T1 = 137.4, 150.0
F_SANS = os.path.join(HERE, "fonts", "NotoSansCJKsc-Black.otf")
F_SERIF = os.path.join(HERE, "fonts", "NotoSerifCJKsc-Regular.otf")
F_SERIFB = os.path.join(HERE, "fonts", "NotoSerifCJKsc-Bold.otf")
OUT = os.path.join(HERE, "out")
WORDS = [(137.80, "站台上"), (139.60, "忽然"), (140.40, "一阵风"), (141.68, "吹过"), (144.49, "一滴泪"), (146.25, "在我的眼角"), (147.95, "滑落")]
LINE1, LINE2 = "站台上忽然一阵风吹过", "一滴泪在我的眼角滑落"

def ease(u): u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)
def lerp(a, b, u): return a + (b - a) * u
_fc = {}
def font(path, sz):
    k = (path, sz)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, sz)
    return _fc[k]

# ------------------------------------------------------------------ the shared edit (source frames, 1280x720)
def load(path, t0, t1, crop=None):
    cap = cv2.VideoCapture(path); cap.set(cv2.CAP_PROP_POS_MSEC, t0 * 1000); fr = []
    while cap.get(cv2.CAP_PROP_POS_MSEC) < t1 * 1000 - 1:
        ok, f = cap.read()
        if not ok: break
        if crop: x, y, w, h = crop; f = f[y:y + h, x:x + w]
        fr.append(cv2.resize(f, (W, H), interpolation=cv2.INTER_LANCZOS4))
    return fr
_SRC = {}
def src():
    if not _SRC:
        _SRC["b05"] = load(os.path.join(PK, "01_原片_未定稿", "ALPHA_B05_G06_原片.mp4"), 5.3, 8.6)
        _SRC["b06a"] = load(os.path.join(PK, "01_原片_未定稿", "ALPHA_B06_G07_原片.mp4"), 3.2, 6.17, crop=(111, 62, 632, 356))
        _SRC["b06b"] = load(os.path.join(PK, "01_原片_未定稿", "ALPHA_B06_G07_原片.mp4"), 6.17, 12.7)
    return _SRC
CUTS = [(137.40, "b05", 0.0), (140.60, "b06a", 0.0), (143.57, "b06b", 0.0)]
def shot_at(t):
    for a, name, off in reversed(CUTS):
        if t >= a - 1e-6:
            fr = src()[name]; return name, fr[min(len(fr) - 1, int((t - a) * FPS))], t - a
def frame_src(t):
    name, f, u = shot_at(t)
    z = 1.0 + 0.012 * u                                   # slow push on every shot
    if z > 1.0:
        f = cv2.resize(f, None, fx=z, fy=z, interpolation=cv2.INTER_LINEAR)
        oy, ox = (f.shape[0] - H) // 2, (f.shape[1] - W) // 2; f = f[oy:oy + H, ox:ox + W]
    return name, f

def grain(f, k, seed):
    return np.clip(f.astype(np.float32) + np.random.default_rng(seed).normal(0, k, f.shape[:2])[..., None], 0, 255).astype(np.uint8)

# ------------------------------------------------------------------ 1. 木刻（黑白刀刻，只有她是青黄色）
PAPER = np.array([222, 236, 243], np.float32)      # BGR warm paper
INKC = np.array([24, 20, 22], np.float32)
def woodcut(t):
    name, f = frame_src(t)
    boil = int(t * 8)                                  # lines re-cut 8 times a second
    rng = np.random.default_rng(boil)
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    g = cv2.createCLAHE(2.0, (8, 8)).apply(g).astype(np.float32) / 255.0
    g = cv2.GaussianBlur(g, (0, 0), 1.2)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    wob = cv2.resize(rng.normal(0, 1, (H // 40 + 2, W // 40 + 2)).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
    a1 = math.radians(28)
    p1 = 0.5 + 0.5 * np.sin(2 * np.pi * ((xx * math.cos(a1) + yy * math.sin(a1)) + 1.4 * wob) / 6.0)
    a2 = math.radians(-62)
    p2 = 0.5 + 0.5 * np.sin(2 * np.pi * ((xx * math.cos(a2) + yy * math.sin(a2)) + 1.4 * wob) / 5.0)
    ink = (p1 > g * 1.55 + 0.05).astype(np.float32)                      # lines get thicker where it is darker
    ink = np.maximum(ink, ((p2 > g * 2.6) & (g < 0.33)).astype(np.float32))   # cross-hatch in the shadows
    ink[g < 0.10] = 1.0
    ed = cv2.Canny(cv2.GaussianBlur((g * 255).astype(np.uint8), (0, 0), 1.6), 40, 110)
    ink = np.maximum(ink, cv2.dilate(ed, np.ones((2, 2), np.uint8)).astype(np.float32) / 255.0)
    # her teal/yellow body stays in colour (flat spot inks under the black lines)
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    teal = cv2.inRange(hsv, (80, 110, 70), (100, 255, 255)); yel = cv2.inRange(hsv, (18, 130, 130), (33, 255, 255))
    k = np.ones((5, 5), np.uint8)
    teal = cv2.morphologyEx(teal, cv2.MORPH_OPEN, k); yel = cv2.morphologyEx(yel, cv2.MORPH_OPEN, k)
    base = np.broadcast_to(PAPER, (H, W, 3)).copy()
    base[teal > 0] = (172, 160, 34); base[yel > 0] = (40, 196, 246)
    fib = cv2.GaussianBlur(np.random.default_rng(3).normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.8) * 6
    out = base * (1 - ink[..., None]) + INKC * ink[..., None] + fib[..., None] * (1 - ink[..., None])
    out = np.clip(out, 0, 255).astype(np.uint8)
    pil = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)); d = ImageDraw.Draw(pil)
    # carved vertical title block on the right, red seal
    line = LINE1 if t < 143.9 else LINE2
    shown = sum(1 for tw, w in WORDS if tw <= t + 0.05 and (w in line))
    words = [w for tw, w in WORDS if w in line][:shown]
    txt = "".join(words)
    x0 = W - 92
    d.rectangle([x0 - 18, 40, x0 + 58, 60 + 56 * len(line)], fill=(243, 236, 222), outline=(22, 20, 24), width=3)
    for i, ch in enumerate(txt):
        d.text((x0 + 20, 70 + 56 * i), ch, font=font(F_SERIFB, 46), fill=(22, 20, 24), anchor="mt")
    d.rectangle([x0 - 4, 60 + 56 * len(line) + 20, x0 + 44, 60 + 56 * len(line) + 68], fill=(30, 40, 190))
    d.text((x0 + 20, 60 + 56 * len(line) + 44), "列", font=font(F_SERIFB, 34), fill=(243, 236, 222), anchor="mm")
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

# ------------------------------------------------------------------ 2. 孔版印刷（Riso：三色网点、错版、海报排版）
R_PAPER = np.array([228, 238, 246], np.float32)
R_NAVY = np.array([105, 45, 38], np.float32); R_TEAL = np.array([165, 150, 0], np.float32); R_YEL = np.array([0, 205, 255], np.float32)
def screen(dens, cell, ang, ox=0, oy=0):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); xx += ox; yy += oy
    c, s = math.cos(ang), math.sin(ang); u = xx * c + yy * s; v = -xx * s + yy * c
    du = (u % cell) - cell / 2; dv = (v % cell) - cell / 2
    r = np.sqrt(np.clip(dens, 0, 1)) * cell * 0.72
    return (np.sqrt(du * du + dv * dv) < r).astype(np.float32)
def riso(t):
    name, f = frame_src(t)
    lab = cv2.cvtColor(f, cv2.COLOR_BGR2LAB).astype(np.float32)
    L = lab[..., 0] / 255.0; A = (lab[..., 1] - 128) / 127.0; B = (lab[..., 2] - 128) / 127.0
    navy = np.clip((0.52 - L) * 2.1, 0, 1) ** 1.3
    teal = np.clip(-A * 3.2 - 0.04, 0, 1) * np.clip(L * 1.8, 0, 1)
    yel = np.clip(B * 2.6 - 0.12, 0, 1)
    jit = int(t * 6)
    rng = np.random.default_rng(jit)
    m = [rng.integers(-2, 3, 2) for _ in range(3)]
    n = screen(cv2.GaussianBlur(navy, (0, 0), 1.0), 5.0, math.radians(15), *m[0])
    te = screen(cv2.GaussianBlur(teal, (0, 0), 1.0), 5.5, math.radians(75), 3 + m[1][0], -2 + m[1][1])
    ye = screen(cv2.GaussianBlur(yel, (0, 0), 1.0), 6.0, math.radians(45), -3 + m[2][0], 2 + m[2][1])
    out = np.broadcast_to(R_PAPER, (H, W, 3)).copy()
    for msk, col in ((ye, R_YEL), (te, R_TEAL), (n, R_NAVY)):     # multiply inks
        out = out * (1 - msk[..., None]) + out * (col / 255.0) * msk[..., None]
    out = np.clip(out + cv2.GaussianBlur(np.random.default_rng(5).normal(0, 1, (H, W)).astype(np.float32), (0, 0), 1.0)[..., None] * 7, 0, 255).astype(np.uint8)
    # poster layout: the current key word huge in navy at the left edge, lyric line small, page furniture
    pil = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)).convert("RGBA")
    lay = Image.new("RGBA", pil.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    key = None
    for tw, w in WORDS:
        if t >= tw - 0.05: key = (tw, w)
    if key:
        tw, w = key; p = ease((t - tw) / 0.25)
        big = {"站台上": "站台", "忽然": "忽然", "一阵风": "风", "吹过": "风", "一滴泪": "泪", "在我的眼角": "泪", "滑落": "落"}[w]
        sz = 330 if len(big) == 1 else 210
        dy = 40 * (1 - p) + (60 * ease((t - 147.95) / 1.5) if big == "落" else 0)
        d.text((60, H / 2 + dy), big, font=font(F_SANS, sz), fill=(38, 45, 105, int(225 * p)), anchor="lm")
    line = LINE1 if t < 143.9 else LINE2
    bw = d.textlength(line, font=font(F_SERIFB, 34))
    d.rectangle([W - 80 - bw, H - 92, W - 44, H - 36], fill=(246, 238, 228, 255))
    d.text((W - 60, H - 64), line, font=font(F_SERIFB, 34), fill=(38, 45, 105, 255), anchor="rm")
    d.text((W - 60, 52), "ALPHA · 远去的列车 · 第 2 段", font=font(F_SERIF, 20), fill=(38, 45, 105, 230), anchor="rm")
    d.line([(60, 70), (W - 60, 70)], fill=(38, 45, 105, 200), width=2)
    pil.alpha_composite(lay)
    return cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)

# ------------------------------------------------------------------ 3. 油画笔触（会呼吸的画）
CANVAS = None
def paint(t):
    global CANVAS
    name, f = frame_src(t)
    if CANVAS is None:
        c = np.random.default_rng(9).normal(0, 1, (H, W)).astype(np.float32)
        CANVAS = (cv2.GaussianBlur(c, (0, 0), 0.7) * 5 + np.sin(np.mgrid[0:H, 0:W][1] * 1.3) * 2 + np.sin(np.mgrid[0:H, 0:W][0] * 1.3) * 2)
    rng = np.random.default_rng(int(t * 8))                       # strokes re-painted 8 times a second
    sm = cv2.bilateralFilter(f, 9, 40, 9)
    under = cv2.GaussianBlur(sm, (0, 0), 10)
    g = cv2.cvtColor(sm, cv2.COLOR_BGR2GRAY).astype(np.float32)
    gx = cv2.Sobel(cv2.GaussianBlur(g, (0, 0), 3), cv2.CV_32F, 1, 0); gy = cv2.Sobel(cv2.GaussianBlur(g, (0, 0), 3), cv2.CV_32F, 0, 1)
    ang = np.arctan2(gy, gx) + np.pi / 2; mag = np.sqrt(gx * gx + gy * gy)
    hsv = cv2.cvtColor(sm, cv2.COLOR_BGR2HSV).astype(np.float32); hsv[..., 1] = np.clip(hsv[..., 1] * 1.28, 0, 255); hsv[..., 2] = np.clip((hsv[..., 2] - 128) * 1.12 + 128, 0, 255)
    col = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    out = under.copy()
    for step, ln, th, thr in ((14, 34, 12, 0), (9, 20, 7, 0), (5, 10, 3, 30)):
        ys, xs = np.mgrid[0:H:step, 0:W:step]
        ys = (ys + rng.integers(0, step, ys.shape)).clip(0, H - 1).ravel(); xs = (xs + rng.integers(0, step, xs.shape)).clip(0, W - 1).ravel()
        keep = mag[ys, xs] > thr; ys, xs = ys[keep], xs[keep]
        order = rng.permutation(len(xs))
        for i in order:
            y, x = ys[i], xs[i]; a = ang[y, x]; l = ln * (0.6 + 0.6 * rng.random())
            dx, dy = math.cos(a) * l / 2, math.sin(a) * l / 2
            c = col[y, x].astype(int) + rng.integers(-16, 17, 3)
            cv2.line(out, (int(x - dx), int(y - dy)), (int(x + dx), int(y + dy)), tuple(int(v) for v in np.clip(c, 0, 255)), th, cv2.LINE_AA)
    out = np.clip(out.astype(np.float32) + CANVAS[..., None], 0, 255).astype(np.uint8)
    pil = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)); d = ImageDraw.Draw(pil)
    line = LINE1 if t < 143.9 else LINE2
    a = min(ease((t - (137.8 if line == LINE1 else 144.4)) / 0.6), 1 - ease((t - (143.6 if line == LINE1 else 149.6)) / 0.3))
    if a > 0:
        d.text((W / 2, H - 70), line, font=font(F_SERIFB, 40), fill=(250, 244, 230), stroke_width=3, stroke_fill=(40, 30, 30), anchor="mm")
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

# ------------------------------------------------------------------ 4. 胶片电影（宽银幕、晕光、颗粒、片门抖动、衬线小字幕）
def film(t):
    name, f = frame_src(t)
    # cross-dissolve 0.4 s into each cut
    for a, nm, _ in CUTS[1:]:
        if a <= t < a + 0.4:
            _, prev, _ = shot_at(a - 1 / FPS); f = cv2.addWeighted(f, ease((t - a) / 0.4), cv2.resize(prev, (W, H)), 1 - ease((t - a) / 0.4), 0)
    x = f.astype(np.float32) / 255.0
    # grade: lifted blacks, teal shadows, warm highlights, gentle desaturation
    lum = x.mean(-1, keepdims=True)
    x = x * 0.92 + 0.035
    x = x + (np.array([0.035, 0.012, -0.02]) * (1 - lum) + np.array([-0.04, 0.0, 0.05]) * lum)   # BGR
    x = lum + (x - lum) * 0.86
    # halation: red-orange bloom around highlights
    hi = np.clip(x - 0.72, 0, 1); hal = cv2.GaussianBlur(hi, (0, 0), 14) * np.array([0.25, 0.45, 1.2])
    x = x + hal
    # gate weave
    rng = np.random.default_rng(int(t * FPS))
    M = np.float32([[1, 0, rng.normal(0, 0.5)], [0, 1, rng.normal(0, 0.5)]])
    x = cv2.warpAffine(x, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    yy, xx = np.mgrid[0:H, 0:W]; v = 1 - 0.30 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.3
    x = x * v[..., None]
    g = rng.normal(0, 0.035, (H // 2, W // 2)).astype(np.float32); g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)
    x = x + g[..., None] * (0.6 + 0.4 * (1 - x.mean(-1, keepdims=True)))
    out = (np.clip(x, 0, 1) * 255).astype(np.uint8)
    bar = int((H - W / 2.39) / 2); out[:bar] = 0; out[H - bar:] = 0                 # 2.39:1
    pil = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)); d = ImageDraw.Draw(pil)
    line = LINE1 if t < 143.9 else LINE2
    a = min(ease((t - (137.8 if line == LINE1 else 144.4)) / 0.5), 1 - ease((t - (143.7 if line == LINE1 else 149.6)) / 0.3))
    if a > 0:
        spaced = " ".join(line)
        d.text((W / 2, H - bar / 2), spaced, font=font(F_SERIF, 24), fill=(int(235 * a), int(232 * a), int(225 * a)), anchor="mm")
    if t < 139.4:
        a = min(ease((t - 137.5) / 0.6), 1 - ease((t - 138.9) / 0.5))
        d.text((W / 2, bar / 2), "远 去 的 列 车", font=font(F_SERIF, 22), fill=(int(200 * a),) * 3, anchor="mm")
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

# ------------------------------------------------------------------ 5. 抖音讲道理（大字动态排版，画面在字里）
def type_(t):
    name, f = frame_src(t)
    bg = np.full((H, W, 3), (22, 14, 12), np.uint8)
    pil = Image.fromarray(cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)).convert("RGBA")
    def fimg(fr): return Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).convert("RGBA")
    YEL = (255, 204, 32, 255); WHITE = (245, 245, 245, 255)
    d = ImageDraw.Draw(pil)
    if t < 139.55:                                                       # hook
        a = ease((t - 137.45) / 0.3); b = ease((t - 138.3) / 0.3)
        d.text((W / 2, 290 - 20 * (1 - a)), "有些告别", font=font(F_SANS, 110), fill=(*WHITE[:3], int(255 * a)), anchor="mm")
        d.text((W / 2, 440 - 20 * (1 - b)), "连机器都记得", font=font(F_SANS, 110), fill=(*YEL[:3], int(255 * b)), anchor="mm")
    elif t < 141.68:                                                     # the platform footage seen through giant glyphs
        u = ease((t - 139.55) / 0.5)
        mask = Image.new("L", (W, H), 0); dm = ImageDraw.Draw(mask)
        dm.text((W / 2 + 40 * math.sin(t * 2), H / 2 - 10), "一阵风" if t >= 140.4 else "忽然", font=font(F_SANS, 300 if t >= 140.4 else 330), fill=255, anchor="mm")
        fi = fimg(f); fi.putalpha(mask.point(lambda v: int(v * u)))
        pil.alpha_composite(fi)
        d.text((W / 2, 70), "站台上", font=font(F_SANS, 54), fill=WHITE, anchor="mm")
    elif t < 143.57:                                                     # full frame, word blown off to the left
        pil.alpha_composite(fimg(f))
        u = ease((t - 141.68) / 1.2)
        d.text((W / 2 - 420 * u, H - 120), "吹过", font=font(F_SANS, 130), fill=(*WHITE[:3], int(255 * (1 - u))), stroke_width=6, stroke_fill=(20, 14, 12), anchor="mm")
    else:                                                                # card window + punchline + kinetic lyric
        u = ease((t - 143.57) / 0.5)
        cw, ch = int(lerp(1100, 920, u)), int(lerp(620, 518, u))
        card = fimg(cv2.resize(f, (cw, ch)))
        m = Image.new("L", (cw, ch), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, cw - 1, ch - 1], 26, fill=255); card.putalpha(m)
        pil.alpha_composite(card, ((W - cw) // 2, int(lerp(50, 70, u))))
        d = ImageDraw.Draw(pil)
        d.text((W / 2, 36), "她只是一台机器", font=font(F_SANS, 34), fill=(*WHITE[:3], int(220 * u)), anchor="mm")
        x = W / 2; y = H - 84; items = [(tw, w) for tw, w in WORDS if w in LINE2 and tw <= t + 0.05]
        txt = "".join(w for _, w in items)
        if txt:
            tw, last = items[-1]; p = ease((t - tw) / 0.18)
            d.text((x, y + (30 * ease((t - 147.95) / 1.2) if last == "滑落" else 0)), txt, font=font(F_SANS, int(lerp(78, 66, p))),
                   fill=YEL if last in ("一滴泪", "滑落") else WHITE, stroke_width=6, stroke_fill=(20, 14, 12), anchor="mm")
    out = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
    return grain(out, 3.0, int(t * FPS))

STYLES = {"woodcut": woodcut, "riso": riso, "paint": paint, "film": film, "type": type_}
TITLES = {"woodcut": "模板一 · 木刻版画（黑白里只有她有颜色）", "riso": "模板二 · 孔版印刷海报（三色网点、错版）",
          "paint": "模板三 · 油画笔触（会呼吸的画）", "film": "模板四 · 胶片电影（宽银幕、晕光、颗粒）",
          "type": "模板五 · 抖音讲道理（大字动态排版）"}

def render(name):
    fr = os.path.join(OUT, f"tpl_{name}"); os.makedirs(fr, exist_ok=True)
    n = int(round((T1 - T0) * FPS))
    for i in range(n):
        cv2.imwrite(os.path.join(fr, f"f{i:04d}.png"), STYLES[name](T0 + i / FPS))
    master = os.path.join(PK, "09_整首音乐候选", "远去的列车.mp3")
    out = os.path.join(OUT, f"tpl_{name}.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(fr, "f%04d.png"), "-ss", str(T0), "-t", str(T1 - T0),
                    "-i", master, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-b:v", "5M", "-maxrate", "7M", "-bufsize", "10M",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-af", "afade=t=in:d=0.25,afade=t=out:st=12.0:d=0.6", "-shortest",
                    "-movflags", "+faststart", out], check=True)
    return out

if __name__ == "__main__":
    which = sys.argv[1]
    if "--still" in sys.argv:
        t = float(sys.argv[sys.argv.index("--still") + 1]); cv2.imwrite(os.path.join(OUT, f"still_{which}_{t}.png"), STYLES[which](t))
    else:
        for nm in (STYLES if which == "all" else [which]): print(render(nm))
