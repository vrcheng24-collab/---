#!/usr/bin/env python3
"""方向 C 风格测试（歌曲 135.4–151.4 秒，“站台上忽然一阵风吹过 / 一滴泪在我的眼角滑落”）。

2.5D 混合：她的形象来自实物照片与现有素材，统一做赛璐珞+墨线处理；演唱特写用实物脸部照片做刚性下颌木偶，
下颌由转换后的机器人人声分轨逐帧驱动（jaw_G07.json）。字幕、风、记忆照片、眼泪都是代码画的。

    python3 test_c.py            # -> out/test_c_16x9.mp4
"""
import json, math, os, subprocess, sys
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "look"))
from celify import celify

HERE = os.path.dirname(os.path.abspath(__file__))
PK = os.path.join(HERE, "..", "mvcut", "ALPHA_导演素材", "ALPHA_导演素材")
W, H, FPS = 1280, 720, 24
T0, T1 = 135.4, 151.4
FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
YEL = (255, 206, 30); INK = (18, 22, 40)
JAW = json.load(open(os.path.join(HERE, "jaw_G07.json"))); JAW_T0 = 137.4
OUT = os.path.join(HERE, "out"); FR = os.path.join(OUT, "test_c_frames"); os.makedirs(FR, exist_ok=True)

def ease(u): u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)
def lerp(a, b, u): return a + (b - a) * u
def jaw_at(t):
    i = (t - JAW_T0) * JAW["fps"]
    if i < 0 or i >= len(JAW["frames"]) - 1: return 0.0
    i0 = int(i); f = i - i0; return JAW["frames"][i0] * (1 - f) + JAW["frames"][i0 + 1] * f

# ------------------------------------------------------------------ sources
def video_frames(path, t0, t1, crop=None):
    cap = cv2.VideoCapture(path); cap.set(cv2.CAP_PROP_POS_MSEC, t0 * 1000); fr = []
    while cap.get(cv2.CAP_PROP_POS_MSEC) < t1 * 1000:
        ok, f = cap.read()
        if not ok: break
        if crop: x, y, w, h = crop; f = f[y:y + h, x:x + w]
        fr.append(f)
    return fr
B05 = video_frames(os.path.join(PK, "01_原片_未定稿", "ALPHA_B05_G06_原片.mp4"), 5.3, 10.04)
B06 = video_frames(os.path.join(PK, "01_原片_未定稿", "ALPHA_B06_G07_原片.mp4"), 0.0, 6.13, crop=(111, 62, 632, 356))
FACE = cv2.imread(os.path.join(HERE, "look", "face_src.png"))           # real robot photo, 1440x1920
CARD = Image.open(os.path.join(HERE, "memory_card.png")).convert("RGBA")
cel_cache = {}
def cel_of(img, key, k=1.0):
    if key not in cel_cache:
        im = cv2.resize(img, (W, H), interpolation=cv2.INTER_LANCZOS4)
        cel_cache[key] = celify(im)
    return cel_cache[key]

# ------------------------------------------------------------------ the face puppet: rigid jaw cut from the photo
JAW_POLY = np.array([(438, 958), (470, 966), (545, 970), (600, 966), (650, 955), (676, 976), (692, 1032), (672, 1102),
                     (612, 1172), (470, 1174), (440, 1122), (420, 1042)], np.int32)
MOUTH = np.array([(438, 958), (470, 966), (545, 970), (600, 966), (650, 955)], np.float32)   # contact line (upper lip bottom)
jmask = np.zeros(FACE.shape[:2], np.uint8); cv2.fillPoly(jmask, [JAW_POLY], 255)
jmask = cv2.GaussianBlur(jmask, (3, 3), 0)
HINGE = np.array([860.0, 905.0])                                       # behind the cheek, toward the visible ear
def face_frame(t):
    deg = jaw_at(t)                                                     # 0..~7 degrees from the vocal stem
    img = FACE.copy()
    # cavity: dark mechanical interior revealed above the moved jaw
    drop = deg / 9.0 * 46.0                                            # px at full open = upper-lip thickness
    if drop > 0.5:
        cav = np.vstack([MOUTH, MOUTH[::-1] + [0, drop + 4]]).astype(np.int32)
        cv2.fillPoly(img, [cav], (20, 16, 18))
        # grey brackets along the upper edge of the cavity (the hardware the state card shows)
        for k in range(6):
            x = int(470 + k * 30); cv2.rectangle(img, (x, int(964)), (x + 18, int(964 + min(10, drop * 0.4))), (90, 92, 98), -1)
    # move the jaw: rotate about the hinge (opens down and slightly back) + small downward travel
    ang = deg * 0.55
    Mx = cv2.getRotationMatrix2D(tuple(HINGE), ang, 1.0); Mx[1, 2] += drop * 0.55
    jaw_img = cv2.warpAffine(FACE, Mx, (FACE.shape[1], FACE.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    jaw_m = cv2.warpAffine(jmask, Mx, (FACE.shape[1], FACE.shape[0]))[..., None] / 255.0
    img = (img * (1 - jaw_m) + jaw_img * jaw_m).astype(np.uint8)
    return img, deg
def tear_overlay(pil, t, sx, sy, ox, oy):
    """A drop sliding from under her right eye down the cheek seam (source coords mapped by scale/offset)."""
    u = (t - 147.6) / 1.9
    if not 0 <= u <= 1.05: return
    path = [(445, 738), (437, 790), (427, 850), (419, 910)]
    k = ease(min(1, u)) * (len(path) - 1); i = min(int(k), len(path) - 2); f = k - i
    x = lerp(path[i][0], path[i + 1][0], f) * sx + ox; y = lerp(path[i][1], path[i + 1][1], f) * sy + oy
    d = ImageDraw.Draw(pil, "RGBA"); r = 9 * sx / 0.6
    y0 = path[0][1] * sy + oy
    d.line([(path[0][0] * sx + ox, y0), (x, y - r)], fill=(200, 230, 255, 110), width=max(2, int(r * 0.5)))
    d.ellipse([x - r, y - r * 1.4, x + r, y + r], fill=(205, 232, 255, 230), outline=(30, 40, 70, 255), width=2)
    d.ellipse([x - r * 0.45, y - r * 0.9, x - r * 0.05, y - r * 0.4], fill=(255, 255, 255, 255))

# ------------------------------------------------------------------ captions (Douyin-style), hook, overlays
def font(sz): return ImageFont.truetype(FONT, sz)
def text(d, xy, s, sz, fill=(255, 255, 255), stroke=6, anchor="mm", alpha=255):
    d.text(xy, s, font=font(sz), fill=(*fill, alpha), stroke_width=stroke, stroke_fill=(*INK, alpha), anchor=anchor)
CAP = [  # (song time the word lands, text, highlight)
    [(137.80, "站台上", False), (139.60, "忽然", False), (140.40, "一阵风", True), (141.68, "吹过", False)],
    [(144.49, "一滴泪", True), (146.25, "在我的眼角", False), (147.95, "滑落", True)],
]
def captions(pil, t):
    d = ImageDraw.Draw(pil, "RGBA")
    line = CAP[0] if t < 144.30 else CAP[1]
    if t < line[0][0] - 0.1: return
    end = 144.30 if line is CAP[0] else 150.6
    fade = 1 - ease((t - end + 0.25) / 0.25) if t > end - 0.25 else 1.0
    sz = 64; widths = [d.textlength(w, font=font(sz)) + 18 for _, w, _ in line]
    x = W / 2 - sum(widths) / 2; y = H - 118
    for (tw, w, hi), wd in zip(line, widths):
        if t >= tw - 0.06:
            p = ease((t - tw + 0.06) / 0.18)                             # pop in
            s = int(sz * lerp(1.25, 1.0, p))
            dy = 0
            if w == "滑落": dy = 26 * ease((t - tw) / 1.2)                 # the word itself slides down
            if w == "吹过": x_shift = -14 * ease((t - tw) / 0.6)
            else: x_shift = 0
            text(d, (x + wd / 2 + x_shift, y + dy), w, s, YEL if hi else (255, 255, 255), stroke=7, alpha=int(255 * p * fade))
        x += wd
def hook(pil, t):
    """Opening hook line, the "讲道理" punchline, over the first shot."""
    if t > 137.9: return
    d = ImageDraw.Draw(pil, "RGBA"); a = int(255 * min(ease((t - T0) / 0.35), 1 - ease((t - 137.5) / 0.4)))
    text(d, (W / 2, 150), "有些告别", 74, (255, 255, 255), 8, alpha=a)
    text(d, (W / 2, 240), "连机器都记得", 74, YEL, 8, alpha=a)
def badge(pil):
    d = ImageDraw.Draw(pil, "RGBA")
    d.rounded_rectangle([28, 24, 330, 72], 10, fill=(18, 22, 40, 170))
    d.text((44, 48), "ALPHA ｜ 远去的列车", font=font(26), fill=(255, 255, 255, 235), anchor="lm")
SCR = np.random.default_rng(11).random((14, 4))
def wind(pil, t):
    g = (t - 140.1) / 3.4
    if not -0.2 < g < 1.4: return
    d = ImageDraw.Draw(pil, "RGBA")
    for k, (a, b, c, e) in enumerate(SCR):
        u = g * (1.1 + 0.6 * a) - b * 0.9
        if not 0 <= u <= 1: continue
        x = lerp(W + 60, -80, u) + 300 * (c - 0.5); y = lerp(60 + 560 * c, 40 + 600 * e, u) + 40 * math.sin(u * 10 + k)
        ang = u * 9 + k; w_, h_ = 26 + 18 * a, 16 + 10 * b
        pts = [(x + math.cos(ang + q) * w_ * (1 if i % 2 else 0.6), y + math.sin(ang + q) * h_) for i, q in enumerate((0, 1.7, 3.14, 4.8))]
        d.polygon(pts, fill=(240, 236, 226, 235), outline=(*INK, 255))
    cu = (t - 140.9) / 2.6                                                # the memory photo tumbles through the frame
    if 0 <= cu <= 1:
        sc = 0.55 + 0.25 * math.sin(cu * 3.14); im = CARD.resize((int(CARD.width * sc), int(CARD.height * sc)))
        im = im.rotate(lerp(-18, 24, cu) + 8 * math.sin(cu * 7), expand=True, resample=Image.BICUBIC)
        x = int(lerp(W + 40, -im.width - 40, ease(cu))); y = int(150 + 70 * math.sin(cu * 3.6))
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.split()[3].point(lambda v: v * 0.45))
        pil.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)), (x + 14, y + 18)); pil.alpha_composite(im, (x, y))
def rain(arr, t, k=0.35):
    rng = np.random.default_rng(int(t * FPS))
    for _ in range(140):
        x = rng.integers(0, W); y = rng.integers(-40, H); L = rng.integers(14, 34)
        cv2.line(arr, (int(x), int(y)), (int(x - L * 0.25), int(y + L)), (225, 230, 240), 1, cv2.LINE_AA)
def finish(arr, t):
    """Glow on highlights, warm-cool split, paper grain, soft vignette."""
    f = arr.astype(np.float32)
    hi = np.clip(f - 200, 0, 55) * 2.2; f += cv2.GaussianBlur(hi, (0, 0), 9) * 0.6
    yy, xx = np.mgrid[0:H, 0:W]; v = 1 - 0.22 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    f *= v[..., None]
    f += np.random.default_rng(int(t * 1000)).normal(0, 5.5, f.shape[:2])[..., None]
    return np.clip(f, 0, 255).astype(np.uint8)

# ------------------------------------------------------------------ shots
def frame(i):
    t = T0 + i / FPS
    if t < 137.70:                                                        # S1: train leaving in the rain (B05), slow push
        u = (t - T0) / 2.3; src = B05[min(len(B05) - 1, int(u * 2.3 * 24))]
        z = lerp(1.0, 1.08, u); base = cel_of(src, ("b05", id(src)))
        base = cv2.resize(base, None, fx=z, fy=z)[int((H * z - H) / 2):][:H, int((W * z - W) / 2):][:, :W]
        base = base.copy(); rain(base, t)
    elif t < 144.36:                                                      # S2: dusk platform wide (B06, vignette cropped), drift
        u = (t - 137.70) / 6.66; src = B06[min(len(B06) - 1, int(u * len(B06)))]
        base = cel_of(src, ("b06", id(src))).copy()
        z = lerp(1.04, 1.12, ease(u)); base = cv2.resize(base, None, fx=z, fy=z)
        ox = int(lerp(0, base.shape[1] - W, ease(u))); oy = int((base.shape[0] - H) / 2); base = base[oy:oy + H, ox:ox + W].copy()
    else:                                                                 # S3: face puppet, jaw driven by the robot vocal
        u = ease((t - 144.36) / 7.04)
        img, deg = face_frame(t)
        # framing on the face: slow push-in, tiny head drift on phrase starts
        cx, cy = 600 + 6 * math.sin(t * 0.9), lerp(900, 880, u); span = lerp(1100, 900, u)
        ang = 1.2 * math.sin((t - 144.36) * 0.7) + lerp(0, 3.0, ease((t - 149.0) / 1.5))
        Mx = cv2.getRotationMatrix2D((cx, cy), ang, W / span); Mx[0, 2] += W / 2 - cx; Mx[1, 2] += H / 2 - cy
        crop = cv2.warpAffine(img, Mx, (W, H), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REFLECT)
        base = celify(crop, soft=True)
        # dusk light: a warm wash from the right, cool shadow on the left (gentle, keeps the silver silver)
        g = np.linspace(0, 1, W)[None, :, None]
        tint = np.array([0.97, 0.99, 1.06]) * (1 - g) + np.array([1.02, 1.0, 0.95]) * g
        base = np.clip(base.astype(np.float32) * tint * (0.92 + 0.12 * g), 0, 255).astype(np.uint8)
        sx = W / span; tear_src = (sx, sx, W / 2 - cx * sx, H / 2 - cy * sx)
    pil = Image.fromarray(cv2.cvtColor(base, cv2.COLOR_BGR2RGB)).convert("RGBA")
    if t >= 144.36: tear_overlay(pil, t, *tear_src)
    wind(pil, t); hook(pil, t); captions(pil, t); badge(pil)
    arr = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
    arr = finish(arr, t)
    if t > T1 - 0.6: arr = (arr * (1 - ease((t - (T1 - 0.6)) / 0.6))).astype(np.uint8)
    cv2.imwrite(os.path.join(FR, f"f{i:04d}.png"), arr)

if __name__ == "__main__":
    n = int((T1 - T0) * FPS)
    for i in range(n): frame(i)
    master = os.path.join(PK, "09_整首音乐候选", "远去的列车.mp3")
    out = os.path.join(OUT, "test_c_16x9.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(FR, "f%04d.png"), "-ss", str(T0), "-t", str(T1 - T0),
                    "-i", master, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-af", "afade=t=in:d=0.3,afade=t=out:st=15.4:d=0.6", "-shortest", "-movflags", "+faststart", out], check=True)
    print(out)
