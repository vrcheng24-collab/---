"""Interlude (93.59–124.38): who she is. The real robot, annotated like an exhibit — then the scale, then the jaw mechanism.

S1 front figure: lens eyes / rigid jaw / ear turbine / mechanical guitar / hip mount, camera pulls back from the face to the figure.
S2 the workshop photo: she stands 3.5 m tall among benches and a worker.
S3 the face close-up: the jaw opens and closes through its range (animation reference), hinge and range annotated.
"""
import math, os, sys
import cv2, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import hero

INK = (236, 230, 220); DIM = (150, 144, 136); YEL = (255, 204, 60)

def overlay(img, draw_fn):
    """Draw with PIL on a transparent layer and composite onto the float picture."""
    lay = Image.new("RGBA", (W, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); draw_fn(d)
    a = np.asarray(lay).astype(np.float32) / 255.0
    return img * (1 - a[..., 3:]) + a[..., :3] * a[..., 3:]

def callout(d, p, q, zh, en, u, side):
    """A dot at p, an elbow line to q, then the label. u in [0,1+] animates it."""
    if u <= 0: return
    a = int(255 * min(1, u * 3))
    d.ellipse((p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5), outline=INK + (a,), width=2)
    k = ease(u / 0.5)
    mid = (q[0] - side * 60, q[1])
    l1 = (p[0] + (mid[0] - p[0]) * min(1, k * 2), p[1] + (mid[1] - p[1]) * min(1, k * 2))
    d.line([p, l1], fill=INK + (a,), width=1)
    if k > 0.5:
        l2 = (mid[0] + (q[0] - mid[0]) * (k - 0.5) * 2, q[1]); d.line([mid, l2], fill=INK + (a,), width=1)
    ta = int(255 * ease((u - 0.45) / 0.35))
    if ta > 0:
        anchor = "ls" if side > 0 else "rs"
        x = q[0] + side * 14
        d.text((x, q[1] - 6), zh, font=font(F_SERIF, 30), fill=INK + (ta,), anchor=anchor)
        d.text((x, q[1] + 22), en, font=font(F_MONO, 15), fill=DIM + (ta,), anchor=anchor)

def grid_bg(t, k=1.0):
    img = np.zeros((PH, W, 3), np.float32) + np.array([0.012, 0.012, 0.014])
    yy, xx = np.mgrid[0:PH, 0:W]
    g = ((xx % 80) < 1) | ((yy % 80) < 1)
    img += g[..., None] * np.array([0.020, 0.022, 0.026]) * k
    glow_ = np.exp(-(((xx - W * 0.5) / 700.0) ** 2) - (((yy - PH * 0.35) / 500.0) ** 2))
    return img + glow_[..., None] * np.array([0.05, 0.045, 0.04])

def place(name, h, cx, top, light=None, jaw_deg=None, t=0.0):
    rgb, a = hero.source(name); s = h / rgb.shape[0]
    if jaw_deg is not None:
        R, A, sb, _ = hero.posed(name, s, t, 0, 0, jaw=False, jaw_deg=jaw_deg)
    else:
        R, A, sb = hero.scaled(name, s)[0], hero.scaled(name, s)[1], round(s, 3)
    x0, y0 = int(cx - R.shape[1] / 2), int(top)
    L = np.zeros((PH, W, 3), np.float32); AL = np.zeros((PH, W), np.float32)
    sx0, sy0 = max(0, -x0), max(0, -y0); dx0, dy0 = max(0, x0), max(0, y0)
    ww, hh = min(R.shape[1] - sx0, W - dx0), min(R.shape[0] - sy0, PH - dy0)
    if ww > 0 and hh > 0:
        L[dy0:dy0 + hh, dx0:dx0 + ww] = R[sy0:sy0 + hh, sx0:sx0 + ww]; AL[dy0:dy0 + hh, dx0:dx0 + ww] = A[sy0:sy0 + hh, sx0:sx0 + ww]
    return L, AL, x0, y0, sb

def s1(t, t0=98.0, t1=105.6):
    """Front figure with callouts; the camera pulls back from the head to the full figure."""
    u = ease((t - t0) / (t1 - t0))
    h, top = lerp(1900, 900, u), lerp(-170, -40, u)
    L, AL, x0, y0, sb = place("front", h, W * 0.5, top)
    yv = np.arange(PH)[:, None, None].astype(np.float32)
    lit = L * (0.95 - 0.35 * yv / PH) * np.array([0.98, 0.98, 1.0])
    img = grid_bg(t); img = img * (1 - AL[..., None]) + lit * AL[..., None]
    P = lambda x, y: (x0 + x * sb, y0 + y * sb)
    items = [  # photo point, label side, zh, en, start
        ((432, 372), -1, "镜头眼", "LENS EYES", 0.6, 190),
        ((482, 505), +1, "刚性下颌", "RIGID JAW · LOWER LIP + CHIN, ONE PIECE", 1.6, 300),
        ((650, 420), +1, "耳侧涡轮", "EAR TURBINE", 2.6, 150),
        ((560, 980), -1, "机械电吉他", "MECHANICAL ELECTRIC GUITAR", 4.0, 470),
        ((505, 1400), +1, "髋下支撑座", "HIP MOUNT · SEATED PERFORMANCE", 5.0, 600),
    ]
    def draw(d):
        for (px, py), side, zh, en, st, ly in items:
            p = P(px, py)
            if not (0 < p[1] < PH - 10): continue
            q = (W * 0.5 + side * 560, ly)
            callout(d, p, q, zh, en, (t - t0 - st) / 1.0, side)
        a = int(255 * ease((t - t0 - 0.2) / 0.6) * (1 - ease((t - t1 + 0.4) / 0.4)))
        d.text((80, 70), "ALPHA", font=font(F_MONO, 22), fill=YEL + (a,))
        d.text((80, 104), "演 出 机 器 人  ·  实 物", font=font(F_SERIF, 22), fill=INK + (a,))
    img = overlay(img, draw)
    return img * ease((t - t0) / 0.5) * (1 - ease((t - t1 + 0.25) / 0.25))

WS = cv2.imread(os.path.join(MV3D, "hero", "44d4c8.png"))[..., ::-1].astype(np.float32) / 255.0      # workshop, she stands among benches
def s2(t, t0=105.6, t1=111.6):
    u = ease((t - t0) / (t1 - t0))
    z = lerp(1.0, 1.08, u)
    ph = WS[160:1920, :]                                                              # photo region
    sc = PH / ph.shape[0] * 1.02 * z; w, h = int(ph.shape[1] * sc), int(ph.shape[0] * sc)
    R = cv2.resize(ph, (w, h), interpolation=cv2.INTER_AREA)
    lum = R.mean(-1, keepdims=True); R = (lum + (R - lum) * 0.8) * np.array([1.0, 0.97, 0.92]) * 0.92
    img = grid_bg(t, 0.5)
    x0 = int(W * 0.40 - w / 2); y0 = int(PH / 2 - h / 2 + lerp(10, -20, u))
    sx0, sy0 = max(0, -x0), max(0, -y0); dx0, dy0 = max(0, x0), max(0, y0)
    ww, hh = min(w - sx0, W - dx0), min(h - sy0, PH - dy0)
    img[dy0:dy0 + hh, dx0:dx0 + ww] = R[sy0:sy0 + hh, sx0:sx0 + ww]
    img = cv2.rectangle(img, (dx0, dy0), (dx0 + ww - 1, dy0 + hh - 1), (0.5, 0.48, 0.45), 1)
    rx = x0 + w + 70
    def draw(d):
        a = int(255 * ease((t - t0 - 0.8) / 0.6))
        d.text((rx, PH * 0.42), "3.5 m", font=font(F_SERIF, 72), fill=YEL + (a,), anchor="ls")
        d.text((rx + 2, PH * 0.42 + 40), "影 片 中 的 身 高", font=font(F_SERIF, 24), fill=INK + (a,), anchor="ls")
        d.text((rx + 2, PH * 0.42 + 70), "HEIGHT IN THE FILM", font=font(F_MONO, 15), fill=DIM + (a,), anchor="ls")
        b = int(255 * ease((t - t0 - 1.8) / 0.5))
        d.text((rx + 2, PH * 0.42 + 140), "工 作 室  ·  实 物 照 片", font=font(F_SERIF, 22), fill=INK + (b,), anchor="ls")
        d.text((rx + 2, PH * 0.42 + 168), "WORKSHOP · REAL PHOTOGRAPH", font=font(F_MONO, 13), fill=DIM + (b,), anchor="ls")
    img = overlay(img, draw)
    return img * ease((t - t0) / 0.3) * (1 - ease((t - t1 + 0.25) / 0.25))

def jaw_demo(t, t0):
    """Three slow open/close cycles through the full range, then speech-like flutter."""
    x = t - t0
    if x < 4.2: return 9.0 * (0.5 - 0.5 * math.cos(2 * math.pi * x / 1.4))
    return 4.5 * (0.5 - 0.5 * math.cos(2 * math.pi * x * 2.6)) * (0.6 + 0.4 * math.sin(x * 5.1))
def s3(t, t0=111.6, t1=118.0):
    u = ease((t - t0) / (t1 - t0))
    deg = jaw_demo(t, t0)
    L, AL, x0, y0, sb = place("close", lerp(1700, 1850, u), W * 0.40, lerp(-330, -400, u), jaw_deg=deg, t=t)
    yv = np.arange(PH)[:, None, None].astype(np.float32)
    lit = L * (1.0 - 0.45 * yv / PH)
    for ex, ey in hero.PHOTOS["close"]["eyes"]:
        X, Y = int(x0 + ex * sb), int(y0 + ey * sb); r = 90
        if r <= X < W - r and r <= Y < PH - r:
            gy, gx = np.mgrid[Y - r:Y + r, X - r:X + r].astype(np.float32)
            lit[Y - r:Y + r, X - r:X + r] += np.exp(-((gx - X) ** 2 + (gy - Y) ** 2) / (2 * 22.0 ** 2))[..., None] * np.array([0.35, 0.5, 1.0]) * (0.2 + 0.7 * deg / 9)
    img = grid_bg(t, 0.6); img = img * (1 - AL[..., None]) + lit * AL[..., None]
    p = hero.PHOTOS["close"]; hx, hy = x0 + p["hinge"][0] * sb, y0 + p["hinge"][1] * sb
    jx, jy = x0 + 700 * sb, y0 + 1290 * sb
    def draw(d):
        a = int(255 * ease((t - t0 - 0.4) / 0.5))
        r = math.hypot(jx - hx, jy - hy)
        ang0 = math.degrees(math.atan2(jy - hy, jx - hx))
        d.arc((hx - r, hy - r, hx + r, hy + r), ang0 - 2, ang0 + 9 * 0.55 + 2, fill=YEL + (a,), width=2)
        d.ellipse((hx - 7, hy - 7, hx + 7, hy + 7), outline=YEL + (a,), width=2)
        d.text((hx + 22, hy - 6), "铰点", font=font(F_SERIF, 26), fill=INK + (a,), anchor="ls")
        d.text((hx + 22, hy + 20), "HINGE", font=font(F_MONO, 14), fill=DIM + (a,), anchor="ls")
        tx = W * 0.72
        d.text((tx, 160), "下 颌 舵 机", font=font(F_SERIF, 34), fill=INK + (a,))
        d.text((tx, 208), "JAW SERVO · 0–9°", font=font(F_MONO, 16), fill=DIM + (a,))
        d.text((tx, 290), f"{deg:4.1f}°", font=font(F_MONO, 64), fill=YEL + (a,))
        bw = 340; d.rectangle((tx, 380, tx + bw, 388), outline=DIM + (a,)); d.rectangle((tx, 380, tx + bw * deg / 9, 388), fill=YEL + (a,))
        b = int(255 * ease((t - t0 - 1.4) / 0.5))
        d.text((tx, 450), "下唇与下巴一体，绕耳后铰点转动", font=font(F_SERIF, 22), fill=INK + (b,))
        d.text((tx, 484), "LOWER LIP + CHIN ROTATE AS ONE RIGID PART", font=font(F_MONO, 13), fill=DIM + (b,))
        d.text((tx, 530), "没有软嘴唇，没有牙齿", font=font(F_SERIF, 22), fill=INK + (b,))
        d.text((tx, 564), "NO SOFT LIPS · NO TEETH", font=font(F_MONO, 13), fill=DIM + (b,))
    img = overlay(img, draw)
    return img * ease((t - t0) / 0.3) * (1 - ease((t - t1 + 0.35) / 0.35))
