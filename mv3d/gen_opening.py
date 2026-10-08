#!/usr/bin/env python3
"""《远去的列车》纯代码版 · 开场样片（歌曲 0–27.6 秒：前奏 + “望着你坐上远去的列车 / 汽笛声将悲伤情绪淹没”）。

不用任何视频素材：画面全部由代码生成，原生 1920x1080。
- 她：从实物照片提取轮廓，重建成粒子线稿；下颌那一块粒子随转换后的机器人人声分轨（口型_G01.mp3）逐帧开合。
- 列车：远处的一点灯光，沿两条铁轨退向地平线。
- 前奏每一个吉他音（母带起音检测）在灯光处激起一圈涟漪。
- HUD 标注她的机械结构，下颌舵机角度是实时读数。

    python3 gen_opening.py [--still t] [--scale 0.5]
"""
import json, math, os, subprocess, sys
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PK = os.path.join(HERE, "..", "mvcut", "ALPHA_导演素材", "ALPHA_导演素材")
SC = float(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 1.0
W, H, FPS = int(1920 * SC), int(1080 * SC), 24
T0, T1 = 0.0, 27.6
F_SERIF = os.path.join(HERE, "fonts", "NotoSerifCJKsc-Regular.otf")
F_SANS = os.path.join(HERE, "fonts", "NotoSansCJKsc-Black.otf")
F_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
JAW = json.load(open(os.path.join(HERE, "jaw_G01.json")))           # robot vocal stem, song time 0
WARM = np.array([0.93, 0.86, 0.78]); TEAL = np.array([0.18, 0.80, 0.82]); YEL = np.array([1.0, 0.80, 0.22]); LAMP = np.array([1.0, 0.70, 0.42])
ONSETS = [1.25, 2.07, 2.89, 3.36, 3.74, 4.16, 4.59, 5.4, 5.85, 6.13, 6.66, 6.94, 7.21, 7.49, 7.78, 8.3, 8.71, 9.0, 9.26, 9.58,
          10.0, 10.38, 11.28, 12.09, 12.52, 12.81, 13.16, 13.53, 13.8, 14.27]
LYR = [(14.43, 21.03, "望着你坐上远去的列车", "watching you board the train that carries you away"),
       (21.03, 27.81, "汽笛声将悲伤情绪淹没", "the whistle drowns out all my sorrow")]

def ease(u): u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)
def eout(u): u = max(0.0, min(1.0, u)); return 1 - (1 - u) ** 3
def lerp(a, b, u): return a + (b - a) * u
_f = {}
def font(p, s):
    s = int(s * SC)
    if (p, s) not in _f: _f[(p, s)] = ImageFont.truetype(p, s)
    return _f[(p, s)]
def jaw_at(t):
    i = t * JAW["fps"]
    if i < 0 or i >= len(JAW["frames"]) - 1: return 0.0
    i0 = int(i); f = i - i0; return JAW["frames"][i0] * (1 - f) + JAW["frames"][i0 + 1] * f

# ------------------------------------------------------------------ her portrait as particles (from the real robot photo)
PHOTO = cv2.imread(os.path.join(HERE, "look", "face_src.png"))            # 1440x1920
CROP = (250, 180, 1250, 1380)                                             # x0, y0, x1, y1 in the photo
JAW_POLY = np.array([(438, 958), (470, 966), (545, 970), (600, 966), (650, 955), (676, 976), (692, 1032), (672, 1102),
                     (612, 1172), (470, 1174), (440, 1122), (420, 1042)], np.int32)
HINGE = np.array([860.0, 905.0])
def build_points():
    x0, y0, x1, y1 = CROP; img = PHOTO[y0:y1, x0:x1]
    sm = cv2.bilateralFilter(img, 9, 50, 9); g = cv2.cvtColor(sm, cv2.COLOR_BGR2GRAY)
    ed = cv2.Canny(g, 45, 120)
    ys, xs = np.nonzero(ed)
    rng = np.random.default_rng(1)
    keep = rng.random(len(xs)) < min(1.0, 15000 / max(1, len(xs))); xs, ys = xs[keep], ys[keep]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # a sparse fill of the coloured armour, so the teal/yellow reads as surfaces, not just outlines
    teal = cv2.inRange(hsv, (80, 90, 60), (100, 255, 255)); yel = cv2.inRange(hsv, (18, 120, 120), (34, 255, 255))
    fy, fx = np.nonzero((teal | yel) > 0); k = rng.random(len(fx)) < 0.012; fx, fy = fx[k], fy[k]
    X = np.concatenate([xs, fx]).astype(np.float32) + x0; Y = np.concatenate([ys, fy]).astype(np.float32) + y0
    h = hsv[(Y - y0).astype(int), (X - x0).astype(int)]
    col = np.tile(WARM, (len(X), 1))
    isT = (h[:, 0] >= 80) & (h[:, 0] <= 100) & (h[:, 1] > 90); isY = (h[:, 0] >= 18) & (h[:, 0] <= 34) & (h[:, 1] > 120)
    col[isT] = TEAL; col[isY] = YEL
    bri = np.where(np.arange(len(X)) < len(xs), 0.55, 0.35) * (0.7 + 0.6 * rng.random(len(X)))
    eyes = (((X - 470) / 80) ** 2 + ((Y - 700) / 45) ** 2 < 1) | (((X - 690) / 90) ** 2 + ((Y - 700) / 45) ** 2 < 1)
    col[eyes] = np.array([0.55, 0.62, 1.0]); bri[eyes] *= 1.8
    onjaw = cv2.pointPolygonTest  # placeholder for readability
    jm = np.zeros(PHOTO.shape[:2], np.uint8); cv2.fillPoly(jm, [JAW_POLY], 1)
    jaw = jm[Y.astype(int).clip(0, PHOTO.shape[0] - 1), X.astype(int).clip(0, PHOTO.shape[1] - 1)] > 0
    return X, Y, col, bri, jaw, eyes
PX, PY, PCOL, PBRI, PJAW, PEYE = build_points()
N = len(PX)
RNG = np.random.default_rng(4)
START = np.stack([RNG.uniform(-0.1, 1.1, N) * W, RNG.uniform(-0.1, 1.1, N) * H], 1)   # scattered dust
DELAY = RNG.uniform(0, 1, N)
# photo -> frame mapping: portrait on the right, head height ~ 0.95 H
PS = 0.84 * H / (CROP[3] - CROP[1]); POX = W * 0.735 - (CROP[0] + CROP[2]) / 2 * PS; POY = H * 0.50 - (CROP[1] + CROP[3]) / 2 * PS + 0.02 * H

def portrait(t):
    """Particle positions (frame px) + per-particle brightness at song time t."""
    deg = jaw_at(t)
    X, Y = PX.copy(), PY.copy()
    if deg > 0.01:                                         # rigid jaw: rotate about the hinge + small drop, same as the real mechanism
        a = math.radians(deg * 0.55); c, s = math.cos(a), math.sin(a)
        dx, dy = X[PJAW] - HINGE[0], Y[PJAW] - HINGE[1]
        X[PJAW] = HINGE[0] + dx * c - dy * s; Y[PJAW] = HINGE[1] + dx * s + dy * c + deg / 9 * 46 * 0.55
    fx = POX + X * PS; fy = POY + Y * PS
    # breathing: tiny drift so the drawing is alive
    fx += np.sin(t * 1.3 + PY * 0.01) * 0.6 * SC; fy += np.cos(t * 1.1 + PX * 0.01) * 0.6 * SC
    u = np.clip((t - 8.6 - DELAY * 4.2) / 1.6, 0, 1); u = 1 - (1 - u) ** 3     # assemble 8.6 -> ~14.4
    x = START[:, 0] + (fx - START[:, 0]) * u; y = START[:, 1] + (fy - START[:, 1]) * u
    b = PBRI * (0.15 + 0.85 * u)
    b = b * np.where(PEYE, 1.0 + 0.8 * min(1.0, deg / 5), 1.0)
    if t >= 21.0:                                          # the whistle: a slow scatter from the edges, like steam
        v = ease((t - 21.0) / 6.6) * (1 - np.clip(PBRI, 0, 1)) * 0.0
    return x, y, b

# ------------------------------------------------------------------ drawing helpers (float RGB canvas)
def splat(img, x, y, col, b):
    m = (x >= 0) & (x < W - 1) & (y >= 0) & (y < H - 1) & (b > 0.005)
    x, y, col, b = x[m], y[m], col[m], b[m]
    xi, yi = x.astype(int), y.astype(int); fx, fy = x - xi, y - yi
    for ox, oy, w in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        np.add.at(img, (yi + oy, xi + ox), col * (b * w)[:, None])
def glow(img):
    return img + cv2.GaussianBlur(img, (0, 0), 2.2 * SC) * 0.9 + cv2.GaussianBlur(img, (0, 0), 14 * SC) * 0.55 + cv2.GaussianBlur(img, (0, 0), 46 * SC) * 0.25
VP = np.array([0.30 * W, 0.60 * H])                                     # vanishing point of the rails
def rails(img, t):
    k = ease((t - 1.0) / 6.0)
    for side in (-1, 1):
        a = VP; b = np.array([VP[0] + side * 0.42 * W, H * 1.05])
        e = a + (b - a) * k
        cv2.line(img, tuple(int(v) for v in a), tuple(int(v) for v in e), (0.20, 0.19, 0.17), max(1, int(1.2 * SC)), cv2.LINE_AA)
    hz = ease((t - 0.6) / 4.0)                                          # faint horizon
    cv2.line(img, (int(VP[0] - 0.9 * W * hz), int(VP[1])), (int(VP[0] + 0.9 * W * hz), int(VP[1])), (0.07, 0.065, 0.06), max(1, int(SC)), cv2.LINE_AA)
    for i in range(1, 16):                                              # sleepers, perspective-spaced, drawn in as the rails reach them
        z = (i / 16) ** 2.4
        if z > k: break
        y = VP[1] + (H * 1.05 - VP[1]) * z; hw = 0.42 * W * z * 1.10
        c = 0.045 + 0.05 * z
        cv2.line(img, (int(VP[0] - hw), int(y)), (int(VP[0] + hw), int(y)), (c, c * 0.95, c * 0.9), max(1, int(SC)), cv2.LINE_AA)
def train_light(img, t):
    """Headlight: still in the intro, then recedes along the rails toward the horizon from the first line on."""
    if t < 0.4: return None
    u = ease((t - 14.4) / 13.0) if t > 14.4 else 0.0
    z = lerp(0.22, 0.0, u)                                              # depth along the rails (0 = horizon)
    p = VP + np.array([0.0, (H * 1.05 - VP[1]) * z])
    r = lerp(5.0, 1.4, u) * SC; a = ease((t - 0.4) / 1.6) * lerp(1.0, 0.25, ease((t - 24.0) / 3.6))
    cv2.circle(img, tuple(int(v) for v in p), int(r + 1), tuple(LAMP * 3.0 * a), -1, cv2.LINE_AA)
    return p, a
def ripples(img, t, p):
    for o in ONSETS:
        d = t - o
        if 0 <= d < 2.2:
            r = (14 + 260 * eout(d / 2.2)) * SC; a = (1 - d / 2.2) ** 2 * 0.55
            cv2.ellipse(img, tuple(int(v) for v in p), (int(r), int(r * 0.32)), 0, 0, 360, tuple(LAMP * a), max(1, int(SC)), cv2.LINE_AA)

# ------------------------------------------------------------------ HUD + type (PIL on top)
CALLOUTS = [  # photo point, label (zh), label (en), value function, appears at
    ((470, 700), "镜头眼", "LENS EYE", lambda t: f"f/{1.8 + 0.6 * math.sin(t * 0.7):.1f}", 11.2),
    ((560, 1070), "下颌舵机", "JAW SERVO", lambda t: f"{jaw_at(t):4.1f}°", 12.0),
    ((1080, 640), "耳侧涡轮", "EAR TURBINE", lambda t: f"{1180 + int(260 * min(1, jaw_at(t) / 5)):4d} rpm", 12.8),
    ((640, 330), "ALPHA-01", "STAGE UNIT · 3.5 m", lambda t: "ONLINE" if t > 14.0 else "BOOT", 13.4),
]
def hud(d, t):
    for (px, py), zh, en, val, t0 in CALLOUTS:
        a = ease((t - t0) / 0.6)
        if a <= 0: continue
        ax, ay = POX + px * PS, POY + py * PS
        lx = ax - (330 if px < 900 else -40) * SC; ly = ay - (70 if px < 900 else 190) * SC
        A = int(200 * a)
        d.ellipse([ax - 4 * SC, ay - 4 * SC, ax + 4 * SC, ay + 4 * SC], outline=(235, 220, 200, A), width=max(1, int(SC)))
        k = ease((t - t0) / 0.5)
        mx = ax + (lx - ax) * k; my = ay + (ly - ay) * k
        d.line([(ax, ay), (mx, my)], fill=(235, 220, 200, int(140 * a)), width=max(1, int(SC)))
        if k >= 1:
            ex = lx + (-150 if px < 900 else 120) * SC
            d.line([(lx, ly), (ex, ly)], fill=(235, 220, 200, int(140 * a)), width=max(1, int(SC)))
            tx = min(lx, ex); n = int(len(zh) * ease((t - t0 - 0.5) / 0.4) + 0.999)
            d.text((tx, ly - 34 * SC), zh[:n], font=font(F_SERIF, 22), fill=(240, 232, 220, A))
            d.text((tx, ly + 8 * SC), en, font=font(F_MONO, 12), fill=(190, 180, 168, int(A * 0.8)))
            d.text((tx, ly + 26 * SC), val(t), font=font(F_MONO, 16), fill=(255, 204, 60, A) if "JAW" in en else (200, 220, 230, A))
def titles(d, t):
    a = ease((t - 2.2) / 1.5) * (1 - ease((t - 8.4) / 1.4))
    if a > 0:
        d.text((0.30 * W, 0.34 * H), "远 去 的 列 车", font=font(F_SERIF, 54), fill=(240, 232, 220, int(235 * a)), anchor="mm")
        d.text((0.30 * W, 0.34 * H + 58 * SC), "T H E   D E P A R T I N G   T R A I N", font=font(F_SERIF, 16), fill=(200, 190, 178, int(200 * a)), anchor="mm")
    for t0, t1, zh, en in LYR:
        a = ease((t - t0 + 0.1) / 0.7) * (1 - ease((t - t1 + 0.6) / 0.5))
        if a <= 0: continue
        n = len(zh); shown = sum(1 for i in range(n) if t >= t0 + (t1 - 0.8 - t0) * i / n)
        x = 0.30 * W; y = 0.80 * H
        txt = " ".join(zh)
        full_w = d.textlength(txt, font=font(F_SERIF, 40))
        d.text((x - full_w / 2, y), " ".join(zh[:shown]), font=font(F_SERIF, 40), fill=(244, 236, 226, int(250 * a)))
        d.text((x, y + 74 * SC), en, font=font(F_SERIF, 18), fill=(180, 172, 162, int(220 * a)), anchor="mm")
    d.text((48 * SC, H - 48 * SC), "ALPHA  ·  远去的列车", font=font(F_SERIF, 15), fill=(150, 142, 134, 160), anchor="lm")
    d.text((W - 48 * SC, H - 48 * SC), f"{int(t // 60):02d}:{t % 60:05.2f}", font=font(F_MONO, 13), fill=(150, 142, 134, 150), anchor="rm")

def frame(t):
    img = np.zeros((H, W, 3), np.float32)
    rails(img, t)
    tl = train_light(img, t)
    if tl: ripples(img, t, tl[0])
    x, y, b = portrait(t)
    splat(img, x, y, PCOL, b * (0.0 if t < 8.4 else 1.0) * (SC / 0.5) ** 1.3 * 1.05)
    if t < 9.6:                                                         # loose dust before the portrait assembles
        dx = (START[::7, 0] + np.sin(t * 0.2 + DELAY[::7] * 9) * 20 * SC); dy = START[::7, 1] - t * 6 * SC * DELAY[::7]
        splat(img, dx, dy % H, PCOL[::7] * 0.6 + 0.4, np.full(len(dx), 0.12 * ease(t / 3)) * (1 - ease((t - 8.4) / 1.2)))
    img = glow(img)
    img = img / (1 + img * 0.35)                                        # soft highlight roll-off
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = 1 - 0.35 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    img = img * v[..., None] + np.array([0.012, 0.012, 0.016])
    img += np.random.default_rng(int(t * FPS)).normal(0, 0.012, (H, W))[..., None]
    out = (np.clip(img, 0, 1) ** (1 / 1.05) * 255).astype(np.uint8)
    pil = Image.fromarray(out).convert("RGBA")                           # colours are RGB throughout
    lay = Image.new("RGBA", pil.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    hud(d, t); titles(d, t)
    pil.alpha_composite(lay)
    fade = ease(t / 1.2) * (1 - ease((t - (T1 - 0.5)) / 0.5))
    arr = np.array(pil.convert("RGB")).astype(np.float32) * fade
    return arr.astype(np.uint8)

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    if "--still" in sys.argv:
        t = float(sys.argv[sys.argv.index("--still") + 1])
        Image.fromarray(frame(t)).save(os.path.join(HERE, "out", f"open_{t}.png")); sys.exit()
    fr = os.path.join(HERE, "out", "open_frames"); os.makedirs(fr, exist_ok=True)
    n = int(round((T1 - T0) * FPS))
    for i in range(n):
        Image.fromarray(frame(T0 + i / FPS)).save(os.path.join(fr, f"f{i:04d}.png"), compress_level=1)
    master = os.path.join(PK, "09_整首音乐候选", "远去的列车.mp3")
    out = os.path.join(HERE, "out", "opening_code_1080p.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(fr, "f%04d.png"), "-ss", "0", "-t", str(T1),
                    "-i", master, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-af", f"afade=t=out:st={T1 - 0.6}:d=0.6", "-shortest", "-movflags", "+faststart", out], check=True)
    print(out)
