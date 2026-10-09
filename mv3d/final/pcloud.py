"""Inside the machine: her face as a 3D point cloud (true colours from the real photo), and memories as particle fields.

Three moments in the film:
  write  (L12, 87.69–98.0)   the face assembles from dust while the day's memories are written; then it disperses.
  wind   (L15–L16, 137.7–151.02)  the platform memory becomes a particle field, a gust blows it away, the face forms, a tear runs.
  snow   (L27, 217.8–224.31) the face sings one last line, then drifts down like snow on a winter night.
"""
import math, os, sys
import cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
sys.path.insert(0, MV3D)
from depth import depth
from memory import clip_frame

def render_points(P, C, B, cam_yaw, cam_dist, focus, fov=0.9, coc_k=9.0, center=(0, 0, 0), falloff=True, cy=0.0):
    """P: Nx3 world (x right, y down, z away). Returns float RGB canvas PH x W."""
    x, y, z = P[:, 0] - center[0], P[:, 1] - center[1], P[:, 2] - center[2]
    c, s = math.cos(cam_yaw), math.sin(cam_yaw)
    xr = x * c + z * s; zr = -x * s + z * c + cam_dist
    ok = zr > 0.1
    f = (W / 2) / math.tan(fov / 2)
    u = W / 2 + f * xr[ok] / zr[ok]; v = PH / 2 + cy + f * y[ok] / zr[ok]
    col = C[ok]; b = B[ok] * ((cam_dist / zr[ok]) ** 2 * 0.9 if falloff else 1.0)
    coc = np.abs(1 / zr[ok] - 1 / focus) * coc_k * 60
    out = np.zeros((PH, W, 3), np.float32)
    for lo, hi, sig in ((0, 0.8, 0), (0.8, 2.0, 1.4), (2.0, 4.5, 3.2), (4.5, 99, 7.0)):
        m = (coc >= lo) & (coc < hi)
        if not m.any(): continue
        layer = np.zeros((PH, W, 3), np.float32); splat(layer, u[m], v[m], col[m], b[m])
        out += cv2.GaussianBlur(layer, (0, 0), sig) if sig else layer
    return out

# ------------------------------------------------------------------ the face
FACE = cv2.imread(os.path.join(MV3D, "look", "face_src.png"))
CROP = (230, 160, 1270, 1420)
JAW_POLY = np.array([(438, 958), (470, 966), (545, 970), (600, 966), (650, 955), (676, 976), (692, 1032), (672, 1102),
                     (612, 1172), (470, 1174), (440, 1122), (420, 1042)], np.int32)
HINGE = np.array([860.0, 905.0])
TEAR_PATH = np.array([(445, 742), (437, 795), (427, 855), (419, 915), (414, 980)], np.float32)
_face = None
def face_cloud():
    global _face
    if _face is not None: return _face
    x0, y0, x1, y1 = CROP; img = FACE[y0:y1, x0:x1]
    d = depth(img)
    ys, xs = np.mgrid[0:img.shape[0]:4, 0:img.shape[1]:4]
    ys = (ys.ravel() + np.random.default_rng(2).integers(0, 4, ys.size)).clip(0, img.shape[0] - 1)
    xs = (xs.ravel() + np.random.default_rng(3).integers(0, 4, xs.size)).clip(0, img.shape[1] - 1)
    dd = d[ys, xs]; keep = dd > 0.42; ys, xs, dd = ys[keep], xs[keep], dd[keep]
    col = img[ys, xs][:, ::-1].astype(np.float32) / 255.0
    col = np.clip((col - col.mean(1, keepdims=True)) * 1.25 + col.mean(1, keepdims=True), 0, 1)
    eyes = ((((xs + x0) - 470) / 80) ** 2 + (((ys + y0) - 700) / 45) ** 2 < 1) | ((((xs + x0) - 690) / 90) ** 2 + (((ys + y0) - 700) / 45) ** 2 < 1)
    P = np.stack([((xs + x0) - 640) / 1000, ((ys + y0) - 800) / 1000, (1 - dd) * 0.55], 1).astype(np.float32)
    jm = np.zeros(FACE.shape[:2], np.uint8); cv2.fillPoly(jm, [JAW_POLY], 1)
    onjaw = jm[ys + y0, xs + x0] > 0
    B = (0.18 + 0.55 * col.mean(1)).astype(np.float32); B[eyes] *= 2.2
    r = np.random.default_rng(3); n = len(P)
    ang = r.random(n) * 2 * np.pi
    start = np.stack([np.cos(ang) * (0.6 + r.random(n)), np.sin(ang) * 0.5 + r.normal(0, 0.2, n), r.uniform(-0.6, 0.8, n)], 1).astype(np.float32) + P * 0.3
    _face = dict(P=P, C=col.astype(np.float32), B=B, J=onjaw, E=eyes, SX=(xs + x0).astype(np.float32), SY=(ys + y0).astype(np.float32),
                 start=start, delay=r.random(n).astype(np.float32), seed=r.random(n).astype(np.float32))
    return _face
def face_points(t):
    F = face_cloud(); P = F["P"].copy(); deg = jaw_at(t)
    if deg > 0.01:                                   # rigid jaw about the hinge, as the real mechanism
        a = math.radians(deg * 0.55); c, s_ = math.cos(a), math.sin(a)
        dx, dy = F["SX"][F["J"]] - HINGE[0], F["SY"][F["J"]] - HINGE[1]
        nx = HINGE[0] + dx * c - dy * s_; ny = HINGE[1] + dx * s_ + dy * c + deg / 9 * 46 * 0.55
        P[F["J"], 0] = (nx - 640) / 1000; P[F["J"], 1] = (ny - 800) / 1000
    B = F["B"] * np.where(F["E"], 1.0 + 0.7 * min(1, deg / 5), 1.0)
    return P, B, deg
def tear_layer(t, t_start, yaw, dist, center, k=1.0):
    tu = (t - t_start) / 1.9
    if not 0 < tu < 1.4: return 0
    n = 60; s = np.linspace(0, min(1, tu), n)
    idx = s * (len(TEAR_PATH) - 1); i0 = np.minimum(idx.astype(int), len(TEAR_PATH) - 2); f = idx - i0
    pts = TEAR_PATH[i0] * (1 - f[:, None]) + TEAR_PATH[i0 + 1] * f[:, None]
    TP = np.stack([(pts[:, 0] - 640) / 1000, (pts[:, 1] - 800) / 1000, np.full(n, -0.02)], 1).astype(np.float32)
    tb = (0.25 + 2.5 * (s / max(1e-3, s.max())) ** 6) * (1 - ease((tu - 1.0) / 0.4)) * 12.0 * k
    return render_points(TP, np.tile(np.array([0.7, 0.85, 1.0], np.float32), (n, 1)), tb.astype(np.float32), cam_yaw=yaw, cam_dist=dist * 1.25, focus=dist * 1.25 - 0.05, coc_k=3.5, center=center)

# ------------------------------------------------------------------ memories as particle fields
STEP = 2
_mem = {}
def mem_points(clip, src_t, crop=None):
    key = (clip, round(src_t * FPS))
    if key in _mem: return _mem[key]
    fr = clip_frame(clip, src_t)
    if crop: x, y, w, h = crop; fr = fr[y:y + h, x:x + w]
    d = depth(fr)
    hh, ww = fr.shape[:2]; ys, xs = np.mgrid[0:hh:STEP, 0:ww:STEP]
    xs = xs.ravel().astype(np.float32); ys = ys.ravel().astype(np.float32)
    dd = d[ys.astype(int), xs.astype(int)]
    col = fr[ys.astype(int), xs.astype(int)][:, ::-1].astype(np.float32) / 255.0
    Z = 1.6 + (1 - dd) * 5.0
    X = (xs / ww - 0.5) * Z * 0.966 * 1.04; Y = (ys / hh - 0.5) * Z * 0.966 * (hh / ww) * 1.04
    P = np.stack([X, Y, Z], 1).astype(np.float32)
    B = (0.35 + 0.9 * col.mean(1)).astype(np.float32)
    _mem.clear(); _mem[key] = (P, col, B)
    return _mem[key]
def wind(P, t, gust, seed_x):
    if t < gust: return P, np.ones(len(P), np.float32)
    front = 1.6 - (t - gust) * 1.1
    nx = P[:, 0] / (P[:, 2] * 0.6)
    age = np.clip((nx - front) / 1.1, 0, None); a2 = age ** 1.6
    Q = P.copy()
    Q[:, 0] -= a2 * (1.2 + seed_x * 1.4)
    Q[:, 1] += -a2 * (0.25 + 0.4 * seed_x) + np.sin(a2 * 3 + seed_x * 20) * 0.08 * age
    Q[:, 2] += np.cos(a2 * 2 + seed_x * 15) * 0.25 * age
    return Q, np.clip(1 - age / 2.4, 0, 1).astype(np.float32)

def finish_pc(img):
    img = glow(img); return img / (1 + img * 0.3) + np.array([0.008, 0.008, 0.011])

# ------------------------------------------------------------------ the three moments
def face_shot(t, t_form, yaw, dist, scatter=None, fall=None, k=1.0):
    F = face_cloud(); P, B, deg = face_points(t)
    u = (t - t_form) / 1.8; uu = 1 - (1 - np.clip(u - F["delay"] * 0.5, 0, 1)) ** 3
    Q = F["start"] + (P - F["start"]) * uu[:, None]
    fade = np.clip(uu * 1.3, 0, 1)
    if scatter is not None and t > scatter:          # disperse outward (memories leave the frame)
        a = np.clip((t - scatter) / 2.4 - F["delay"] * 0.35, 0, None) ** 1.5
        Q = Q + (F["start"] - Q.mean(0)) * a[:, None] * 1.2 + np.stack([np.zeros_like(a), -a * 0.2, a * 0.4], 1)
        fade = fade * np.clip(1 - a / 1.6, 0, 1)
    if fall is not None and t > fall:                # winter night: the cloud drifts down like snow
        a = np.clip((t - fall) / 3.5 - F["delay"] * 0.5, 0, None)
        Q = Q + np.stack([np.sin(a * 2 + F["seed"] * 30) * 0.05 * a, a ** 1.3 * (0.35 + 0.3 * F["seed"]), np.cos(a * 1.5 + F["seed"] * 20) * 0.05 * a], 1)
        fade = fade * np.clip(1 - a / 2.2, 0, 1) ** 0.7
    center = (0.07, 0.07, 0.2)
    img = render_points(Q, F["C"], B * 9.0 * fade * k, cam_yaw=yaw, cam_dist=dist * 1.25, focus=dist * 1.25 - 0.05, coc_k=3.5, center=center)
    return img, center

def write_seq(t, t0=87.69, t1=98.0):
    """L12: the face forms from dust, slow orbit, then disperses into the spec section."""
    v = ease((t - t0) / (t1 - t0))
    yaw, dist = lerp(-0.28, 0.22, v), lerp(2.25, 1.95, v)
    img, _ = face_shot(t, t0 - 0.2, yaw, dist, scatter=t1 - 3.2)
    return finish_pc(img) * ease((t - t0) / 0.4)

_seed = {}
def wind_seq(t, t0=137.7, t1=151.02, gust=140.4, face_t=144.36):
    img = np.zeros((PH, W, 3), np.float32)
    if t < face_t + 0.8:                             # the platform memory as a field; frozen and blown away by the gust
        P, C, B = mem_points("B06", 0.3 + (min(t, gust) - t0))
        if len(P) not in _seed: _seed[len(P)] = np.random.default_rng(3).random(len(P)).astype(np.float32)
        Q, fade = wind(P, t, gust, _seed[len(P)])
        u = (t - t0) / (face_t - t0)
        a = ease((t - t0) / 0.6) * (1 - ease((t - face_t + 0.2) / 1.0))
        img += render_points(Q, C, B * fade * a * 7.0, cam_yaw=lerp(-0.04, 0.05, ease(u)), cam_dist=lerp(3.0, 2.55, ease(u)), focus=lerp(2.6, 2.2, ease(u)), coc_k=1.2, center=(0, 0, 3.0), falloff=False)
    if t >= face_t - 0.7:
        v = ease((t - face_t) / (t1 - face_t))
        yaw, dist = lerp(0.30, -0.10, v), lerp(2.35, 1.95, v)
        f, center = face_shot(t, face_t - 0.7, yaw, dist)
        img += f + tear_layer(t, 147.7, yaw, dist, center)
    return finish_pc(img) * (1 - ease((t - t1 + 0.5) / 0.5))

def snow_seq(t, t0=217.8, t1=224.31):
    v = ease((t - t0) / (t1 - t0))
    yaw, dist = lerp(0.18, -0.05, v), lerp(2.0, 2.3, v)
    img, _ = face_shot(t, t0 - 1.6, yaw, dist, fall=t0 + 2.6)
    return finish_pc(img) * ease((t - t0) / 0.5)
