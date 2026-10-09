#!/usr/bin/env python3
"""视觉升级样片（歌曲 137.7–152.7 秒）：素材变成三维粒子“记忆”，被风吹散，再聚成她的三维点云肖像。

- 前半（站台上忽然一阵风吹过）：B06 站台素材逐帧估计深度，重建为三维粒子场，镜头缓慢推进；“一阵风”时一道风从右向左扫过，把记忆吹散。
- 后半（一滴泪在我的眼角滑落）：实物照片的三维点云（真实颜色），镜头环绕 + 景深；下颌粒子随机器人人声分轨开合；“滑落”时一道光从眼角流下。

    python3 gen_upgrade.py [--still t] [--scale 0.5]
"""
import json, math, os, subprocess, sys
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from depth import depth

HERE = os.path.dirname(os.path.abspath(__file__))
PK = os.path.join(HERE, "..", "mvcut", "ALPHA_导演素材", "ALPHA_导演素材")
SC = float(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 1.0
W, H, FPS = int(1920 * SC), int(1080 * SC), 24
T0, T1 = 137.7, 152.7
GUST = 140.4; FACE_T = 144.36
F_SERIF = os.path.join(HERE, "fonts", "NotoSerifCJKsc-Regular.otf"); F_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
JAW = json.load(open(os.path.join(HERE, "jaw_G07.json"))); JAW_T0 = 137.4
LYR = [(137.70, 144.36, "站台上忽然一阵风吹过", "a sudden wind sweeps across the platform"),
       (144.36, 149.85, "一滴泪在我的眼角滑落", "a tear slides from the corner of my eye")]
def ease(u): u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)
def lerp(a, b, u): return a + (b - a) * u
_f = {}
def font(p, s):
    s = int(s * SC)
    if (p, s) not in _f: _f[(p, s)] = ImageFont.truetype(p, s)
    return _f[(p, s)]
def jaw_at(t):
    i = (t - JAW_T0) * JAW["fps"]
    if i < 0 or i >= len(JAW["frames"]) - 1: return 0.0
    i0 = int(i); f = i - i0; return JAW["frames"][i0] * (1 - f) + JAW["frames"][i0 + 1] * f

# ------------------------------------------------------------------ renderer: perspective points with depth of field
def render_points(P, C, B, cam_yaw, cam_dist, focus, fov=0.9, coc_k=9.0, center=(0, 0, 0), falloff=True):
    """P: Nx3 world (x right, y down, z away). Returns float RGB canvas."""
    x, y, z = P[:, 0] - center[0], P[:, 1] - center[1], P[:, 2] - center[2]
    c, s = math.cos(cam_yaw), math.sin(cam_yaw)
    xr = x * c + z * s; zr = -x * s + z * c + cam_dist
    ok = zr > 0.1
    f = (W / 2) / math.tan(fov / 2)
    u = W / 2 + f * xr[ok] / zr[ok]; v = H / 2 + f * y[ok] / zr[ok]
    col = C[ok]; b = B[ok] * ((cam_dist / zr[ok]) ** 2 * 0.9 if falloff else 1.0)
    coc = np.abs(1 / zr[ok] - 1 / focus) * coc_k * W / 1920 * 60
    out = np.zeros((H, W, 3), np.float32)
    for lo, hi, sig in ((0, 0.8, 0), (0.8, 2.0, 1.4), (2.0, 4.5, 3.2), (4.5, 99, 7.0)):
        m = (coc >= lo) & (coc < hi)
        if not m.any(): continue
        layer = np.zeros((H, W, 3), np.float32); splat(layer, u[m], v[m], col[m], b[m])
        out += cv2.GaussianBlur(layer, (0, 0), sig * SC) if sig else layer
    return out
def splat(img, x, y, col, b):
    m = (x >= 0) & (x < W - 1) & (y >= 0) & (y < H - 1) & (b > 0.002)
    x, y, col, b = x[m], y[m], col[m], b[m]
    xi, yi = x.astype(np.int32), y.astype(np.int32); fx, fy = (x - xi).astype(np.float32), (y - yi).astype(np.float32)
    for ox, oy, w in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        np.add.at(img, (yi + oy, xi + ox), col * (b * w)[:, None])
def glow(img):
    return img + cv2.GaussianBlur(img, (0, 0), 3 * SC) * 0.6 + cv2.GaussianBlur(img, (0, 0), 18 * SC) * 0.35 + cv2.GaussianBlur(img, (0, 0), 60 * SC) * 0.18

# ------------------------------------------------------------------ memory: the platform footage as a particle field
cap = cv2.VideoCapture(os.path.join(PK, "01_原片_未定稿", "ALPHA_B06_G07_原片.mp4"))
MEM = []                                                       # B06 0.3–6.13 s (wide platform), vignette cropped
cap.set(cv2.CAP_PROP_POS_MSEC, 300)
while cap.get(cv2.CAP_PROP_POS_MSEC) < 6130:
    ok, fr = cap.read()
    if not ok: break
    MEM.append(fr[62:418, 111:743])
STEP = 2
_mem_cache = {}
def mem_points(k):
    if k in _mem_cache: return _mem_cache[k]
    fr = MEM[min(k, len(MEM) - 1)]; d = depth(fr)
    hh, ww = fr.shape[:2]; ys, xs = np.mgrid[0:hh:STEP, 0:ww:STEP]
    xs = xs.ravel().astype(np.float32); ys = ys.ravel().astype(np.float32)
    dd = d[ys.astype(int), xs.astype(int)]
    col = fr[ys.astype(int), xs.astype(int)][:, ::-1].astype(np.float32) / 255.0
    Z = 1.6 + (1 - dd) * 5.0                                    # near objects at z ~1.6, far at ~6.6
    X = (xs / ww - 0.5) * Z * 0.966 * 1.04; Y = (ys / hh - 0.5) * Z * 0.966 * (hh / ww) * 1.04     # fills the frame from a camera at the origin
    P = np.stack([X, Y, Z], 1).astype(np.float32)
    lum = col.mean(1)
    B = (0.35 + 0.9 * lum).astype(np.float32)
    _mem_cache.clear(); _mem_cache[k] = (P, col, B)
    return _mem_cache[k]
RNG = np.random.default_rng(3)
def wind(P, t, seed_x):
    """Gust front sweeps right->left starting at GUST; particles behind the front are carried left and up, with swirl."""
    if t < GUST: return P, np.ones(len(P), np.float32)
    front = 1.6 - (t - GUST) * 1.1                              # in normalised screen x (1.6 -> -1.6 over ~3 s)
    nx = P[:, 0] / (P[:, 2] * 0.6)
    age = np.clip((nx - front) / 1.1, 0, None)                  # time since the gust reached this particle (~s)
    a2 = age ** 1.6
    Q = P.copy()
    Q[:, 0] -= a2 * (1.2 + seed_x * 1.4)
    Q[:, 1] += -a2 * (0.25 + 0.4 * seed_x) + np.sin(a2 * 3 + seed_x * 20) * 0.08 * age
    Q[:, 2] += np.cos(a2 * 2 + seed_x * 15) * 0.25 * age
    fade = np.clip(1 - age / 2.4, 0, 1).astype(np.float32)
    return Q, fade

# ------------------------------------------------------------------ her face as a 3D point cloud (true colours) from the real photo
PH = cv2.imread(os.path.join(HERE, "look", "face_src.png"))
CROP = (230, 160, 1270, 1420)
JAW_POLY = np.array([(438, 958), (470, 966), (545, 970), (600, 966), (650, 955), (676, 976), (692, 1032), (672, 1102),
                     (612, 1172), (470, 1174), (440, 1122), (420, 1042)], np.int32)
HINGE = np.array([860.0, 905.0])
def build_face():
    x0, y0, x1, y1 = CROP; img = PH[y0:y1, x0:x1]
    d = depth(img)
    ys, xs = np.mgrid[0:img.shape[0]:4, 0:img.shape[1]:4]; ys, xs = ys.ravel() + np.random.default_rng(2).integers(0, 4, ys.size), xs.ravel() + np.random.default_rng(3).integers(0, 4, xs.size)
    ys = ys.clip(0, img.shape[0] - 1); xs = xs.clip(0, img.shape[1] - 1)
    dd = d[ys, xs]; keep = dd > 0.42; ys, xs, dd = ys[keep], xs[keep], dd[keep]
    col = img[ys, xs][:, ::-1].astype(np.float32) / 255.0
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[ys, xs]
    col = np.clip((col - col.mean(1, keepdims=True)) * 1.25 + col.mean(1, keepdims=True), 0, 1)
    eyes = ((((xs + x0) - 470) / 80) ** 2 + (((ys + y0) - 700) / 45) ** 2 < 1) | ((((xs + x0) - 690) / 90) ** 2 + (((ys + y0) - 700) / 45) ** 2 < 1)
    s = 1.0 / 1000
    X = ((xs + x0) - 640) * s; Y = ((ys + y0) - 800) * s; Z = (1 - dd) * 0.55
    P = np.stack([X, Y, Z], 1).astype(np.float32)
    jm = np.zeros(PH.shape[:2], np.uint8); cv2.fillPoly(jm, [JAW_POLY], 1)
    onjaw = jm[ys + y0, xs + x0] > 0
    B = (0.18 + 0.55 * col.mean(1)).astype(np.float32); B[eyes] *= 2.2
    return P, col.astype(np.float32), B, onjaw, eyes, (xs + x0).astype(np.float32), (ys + y0).astype(np.float32)
FP, FC, FB, FJ, FE, FSX, FSY = build_face()
NF = len(FP)
FSTART = None
def face_points(t):
    P = FP.copy()
    deg = jaw_at(t)
    if deg > 0.01:                                             # rigid jaw about the hinge (in photo coords), same as the real mechanism
        a = math.radians(deg * 0.55); c, s_ = math.cos(a), math.sin(a)
        dx, dy = FSX[FJ] - HINGE[0], FSY[FJ] - HINGE[1]
        nx = HINGE[0] + dx * c - dy * s_; ny = HINGE[1] + dx * s_ + dy * c + deg / 9 * 46 * 0.55
        P[FJ, 0] = (nx - 640) / 1000; P[FJ, 1] = (ny - 800) / 1000
    B = FB * np.where(FE, 1.0 + 0.7 * min(1, deg / 5), 1.0)
    return P, B, deg

# ------------------------------------------------------------------ frames
TEAR_PATH = np.array([(445, 742), (437, 795), (427, 855), (419, 915), (414, 980)], np.float32)
def frame(t):
    img = np.zeros((H, W, 3), np.float32)
    seed = None
    if t < FACE_T + 0.8:                                       # memory field (and its blown-away particles)
        k = int((min(t, GUST) - T0) * FPS)                       # footage plays until the gust, then the memory freezes and is blown away
        P, C, B = mem_points(min(k, len(MEM) - 1))
        global _seed
        if "_seed" not in globals() or len(_seed) != len(P): _seed = RNG.random(len(P)).astype(np.float32)
        Q, fade = wind(P, t, _seed)
        u = (t - T0) / (FACE_T - T0)
        a = ease((t - T0) / 0.8) * (1 - ease((t - FACE_T + 0.2) / 1.0))
        img += render_points(Q, C, B * fade * a * 2.4 * (SC / 0.5) ** 1.6, cam_yaw=lerp(-0.04, 0.05, ease(u)), cam_dist=lerp(3.0, 2.55, ease(u)), focus=lerp(2.6, 2.2, ease(u)), coc_k=1.2, center=(0, 0, 3.0), falloff=False)
    if t >= FACE_T - 0.7:                                      # the face assembles from drifting dust, camera orbits slowly
        P, B, deg = face_points(t)
        u = (t - FACE_T + 0.7) / 1.8; uu = 1 - (1 - np.clip(u - RNG_DELAY * 0.5, 0, 1)) ** 3
        start = FACE_START
        Q = start + (P - start) * uu[:, None]
        v = ease((t - FACE_T) / (T1 - FACE_T))
        yaw = lerp(0.30, -0.10, v); dist = lerp(2.35, 1.95, v)
        img += render_points(Q, FC, B * 3.0 * (SC / 0.5) ** 1.6 * np.clip(uu * 1.3, 0, 1), cam_yaw=yaw, cam_dist=dist, focus=dist - 0.05, coc_k=3.5, center=(0.07, 0.07, 0.2))
        # tear: a stream of light from her eye down the cheek seam on "滑落"
        tu = (t - 147.7) / 1.9
        if 0 < tu < 1.4:
            n = 60; s = np.linspace(0, min(1, tu), n)
            idx = s * (len(TEAR_PATH) - 1); i0 = np.minimum(idx.astype(int), len(TEAR_PATH) - 2); f = idx - i0
            pts = TEAR_PATH[i0] * (1 - f[:, None]) + TEAR_PATH[i0 + 1] * f[:, None]
            TP = np.stack([(pts[:, 0] - 640) / 1000, (pts[:, 1] - 800) / 1000, np.full(n, -0.02)], 1).astype(np.float32)
            tb = (0.25 + 2.5 * (s / max(1e-3, s.max())) ** 6) * (1 - ease((tu - 1.0) / 0.4)) * 4 * (SC / 0.5) ** 1.6
            img += render_points(TP, np.tile(np.array([0.7, 0.85, 1.0], np.float32), (n, 1)), tb.astype(np.float32), cam_yaw=yaw, cam_dist=dist, focus=dist - 0.05, coc_k=3.5, center=(0.07, 0.07, 0.2))
    img = glow(img); img = img / (1 + img * 0.3)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    img *= (1 - 0.38 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2))[..., None]
    img += np.array([0.010, 0.010, 0.014]) + np.random.default_rng(int(t * FPS)).normal(0, 0.010, (H, W))[..., None]
    pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", pil.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for t0, t1, zh, en in LYR:
        a = ease((t - t0 + 0.05) / 0.6) * (1 - ease((t - t1 + 0.5) / 0.45))
        if a <= 0: continue
        n = len(zh); shown = sum(1 for i in range(n) if t >= t0 + (t1 - 0.9 - t0) * i / n)
        txt = " ".join(zh); fw = d.textlength(txt, font=font(F_SERIF, 40))
        d.text((W / 2 - fw / 2, H * 0.84), " ".join(zh[:shown]), font=font(F_SERIF, 40), fill=(244, 236, 226, int(250 * a)))
        d.text((W / 2, H * 0.84 + 74 * SC), en, font=font(F_SERIF, 18), fill=(180, 172, 162, int(220 * a)), anchor="mm")
    if t >= FACE_T + 0.6:
        a = ease((t - FACE_T - 0.6) / 0.5)
        d.text((80 * SC, 90 * SC), "JAW SERVO", font=font(F_MONO, 12), fill=(190, 180, 168, int(200 * a)))
        d.text((80 * SC, 108 * SC), f"{jaw_at(t):4.1f}°", font=font(F_MONO, 22), fill=(255, 204, 60, int(240 * a)))
        d.text((80 * SC, 150 * SC), "MEMORY", font=font(F_MONO, 12), fill=(190, 180, 168, int(200 * a)))
        d.text((80 * SC, 168 * SC), "站台 · 黄昏 · 列车", font=font(F_SERIF, 18), fill=(220, 214, 204, int(220 * a)))
    pil.alpha_composite(lay)
    fade = ease((t - T0) / 0.5) * (1 - ease((t - (T1 - 0.6)) / 0.6))
    return (np.array(pil.convert("RGB")).astype(np.float32) * fade).astype(np.uint8)

RNG_DELAY = RNG.random(NF).astype(np.float32)
_ang = RNG.random(NF) * 2 * np.pi
FACE_START = np.stack([np.cos(_ang) * (0.6 + RNG.random(NF)), np.sin(_ang) * 0.5 + RNG.normal(0, 0.2, NF), RNG.uniform(-0.6, 0.8, NF)], 1).astype(np.float32) + FP * 0.3

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    if "--still" in sys.argv:
        for tt in sys.argv[sys.argv.index("--still") + 1].split(","):
            Image.fromarray(frame(float(tt))).save(os.path.join(HERE, "out", f"up_{tt}.png"))
        sys.exit()
    fr = os.path.join(HERE, "out", "up_frames"); os.makedirs(fr, exist_ok=True)
    n = int(round((T1 - T0) * FPS))
    for i in range(n):
        Image.fromarray(frame(T0 + i / FPS)).save(os.path.join(fr, f"f{i:04d}.png"), compress_level=1)
    master = os.path.join(PK, "09_整首音乐候选", "远去的列车.mp3")
    out = os.path.join(HERE, "out", "upgrade_1080p.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(fr, "f%04d.png"), "-ss", str(T0), "-t", str(T1 - T0),
                    "-i", master, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow", "-b:v", "13M", "-maxrate", "16M", "-bufsize", "24M",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-af", f"afade=t=in:d=0.3,afade=t=out:st={T1 - T0 - 0.6}:d=0.6",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    print(out)
