"""The real robot in a small live-house bar at night.

The robot comes from the user's photos of the physical ALPHA (cut out with IS-Net), relit and placed in a code-built room:
back-bar lights, a shelf glow, haze, a warm spotlight from above, a dark stage with a soft reflection, and out-of-focus
patrons in the foreground. The camera moves in 2.5D. On close shots the rigid jaw opens with the vocal (same mechanism as the
real head: lower lip + chin rotate about a hinge behind the cheek), the head nods with the phrasing and the lens eyes glow
with the voice.
"""
import math, os, sys
import cv2, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *

PHOTOS = {   # coordinates in photo pixels. ppm: photo pixels per metre at film scale (3.5 m robot). floor: photo y of the audience floor.
    "front": dict(f="becbd0", head=(540, 350, 200, 215), neck=(505, 570), eyes=[(432, 372), (560, 372)], ppm=850, floor=2980,
                  jaw=[(445, 482), (468, 485), (490, 484), (505, 482), (520, 479), (522, 500), (512, 530), (482, 546), (455, 540), (444, 515), (440, 495)],
                  hinge=None, lip=20, kill=[[(0, 1010), (75, 1010), (75, 1420), (0, 1420)], [(698, 330), (790, 250), (800, 640), (680, 640), (680, 500)]],
                  neck_add=[(880, 850), (1290, 720), (1300, 648), (1440, 636), (1440, 834), (1290, 812), (880, 952)]),
    "side": dict(f="14ea6d", head=(700, 560, 230, 260), neck=(740, 790), eyes=[(600, 610), (720, 612)], ppm=980, floor=3420,
                 jaw=[(622, 722), (650, 728), (680, 732), (705, 732), (722, 728), (722, 760), (702, 790), (662, 800), (630, 790), (614, 760)],
                 hinge=(800, 690), lip=24, kill=[[(470, 380), (560, 380), (556, 1050), (470, 1050)]]),
    "close": dict(f="6eb86e", head=(720, 900, 470, 520), neck=(760, 1450), eyes=[(565, 905), (790, 935)], ppm=2040, floor=6500,
                  jaw=[(606, 1176), (650, 1182), (700, 1188), (760, 1192), (785, 1188), (800, 1215), (800, 1280), (760, 1330), (640, 1330), (600, 1290), (590, 1220)],
                  hinge=(1010, 1100), lip=46, tear=[(560, 950), (552, 1010), (548, 1080), (552, 1150), (560, 1220)], kill=[[(470, 1240), (500, 1170), (538, 1170), (538, 1400), (440, 1400), (440, 1300)]]),
    "face": dict(f="20ea29", head=(720, 760, 470, 520), neck=(700, 1250), eyes=[(470, 700), (690, 700)], ppm=1900, floor=6200,
                 jaw=[(438, 958), (470, 966), (545, 970), (600, 966), (650, 955), (676, 976), (692, 1032), (672, 1102), (612, 1172), (470, 1174), (440, 1122), (420, 1042)],
                 hinge=(860, 905), lip=46, tear=[(445, 742), (437, 795), (427, 855), (419, 915), (414, 980)], add=[[(560, 1090), (880, 1090), (930, 1340), (500, 1340)], [(120, 1330), (1320, 1330), (1380, 1920), (60, 1920)]]),
}
_src = {}
def source(name):
    if name not in _src:
        p = PHOTOS[name]; img = cv2.imread(os.path.join(MV3D, "hero", p["f"] + ".png"))
        a = np.load(os.path.join(MV3D, "hero", p["f"] + "_a.npy")).astype(np.float32)
        a = cv2.resize(a, (img.shape[1], img.shape[0]))
        a = np.clip((a - 0.25) / 0.55, 0, 1)
        rgb = img[..., ::-1].astype(np.float32) / 255.0
        if p.get("neck_add"):                                                    # the guitar neck the matte lost: opaque, minus the yellow wall stripe behind it
            m = np.zeros(a.shape, np.float32); cv2.fillPoly(m, [np.array(p["neck_add"], np.int32)], 1.0)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            yel = ((hsv[..., 0] > 15) & (hsv[..., 0] < 40) & (hsv[..., 1] > 110)).astype(np.float32) * m
            yel = cv2.GaussianBlur(cv2.dilate(yel, np.ones((5, 5), np.uint8)), (0, 0), 2)[..., None]
            rgb = rgb * (1 - yel) + np.array([0.035, 0.035, 0.045], np.float32) * yel
            a = np.maximum(a, cv2.GaussianBlur(m, (0, 0), 2))
        if p.get("add"):                                                         # body under the chin: opaque, in deep shadow
            m = np.zeros(a.shape, np.float32)
            for poly in p["add"]: cv2.fillPoly(m, [np.array(poly, np.int32)], 1.0)
            bg = cv2.GaussianBlur(m * (a < 0.5), (0, 0), 6)[..., None]
            sh = cv2.GaussianBlur(m, (0, 0), 40)[..., None]
            rgb = rgb * (1 - bg * 0.9) * (1 - sh * 0.55); a = np.maximum(a, m)
        for poly in p.get("kill", []): cv2.fillPoly(a, [np.array(poly, np.int32)], 0.0)
        a = cv2.erode(a, np.ones((5, 5), np.uint8)); a = cv2.GaussianBlur(a, (0, 0), 1.2)
        hh, ww = a.shape; e = 60.0                                               # fade the photo borders: no hard cut lines
        fy = np.clip(np.minimum(np.arange(hh), hh - 1 - np.arange(hh)) / e, 0, 1); fx = np.clip(np.minimum(np.arange(ww), ww - 1 - np.arange(ww)) / e, 0, 1)
        a *= (fy[:, None] * fx[None, :]) ** 0.7
        _src[name] = (rgb, a)
    return _src[name]
_scaled = {}
def scaled(name, s):
    """Photo, alpha and masks resized to scale s (bucketed so consecutive frames reuse them)."""
    sb = round(s, 3)
    key = (name, sb)
    if key not in _scaled:
        if len(_scaled) > 6: _scaled.clear()
        rgb, a = source(name); p = PHOTOS[name]
        w, h = max(2, int(rgb.shape[1] * sb)), max(2, int(rgb.shape[0] * sb))
        R = cv2.resize(rgb, (w, h), interpolation=cv2.INTER_AREA); A = cv2.resize(a, (w, h), interpolation=cv2.INTER_AREA)
        hm = np.zeros((h, w), np.float32); cx, cy, rx, ry = p["head"]
        cv2.ellipse(hm, (int(cx * sb), int(cy * sb)), (int(rx * sb), int(ry * sb)), 0, 0, 360, 1.0, -1); hm = cv2.GaussianBlur(hm, (0, 0), max(1, 25 * sb))
        jm = None
        if p.get("jaw"):
            jm = np.zeros((h, w), np.float32); cv2.fillPoly(jm, [(np.array(p["jaw"]) * sb).astype(np.int32)], 1.0); jm = cv2.GaussianBlur(jm, (0, 0), max(0.6, 1.2 * sb))
        _scaled[key] = (R, A, hm, jm, sb)
    return _scaled[key]

def posed(name, s, t, nod, tilt, jaw=True, jaw_deg=None):
    """Rigid jaw (lower lip + chin) opened by the vocal, then the head nods/tilts about the neck."""
    R, A, hm, jm, sb = scaled(name, s); p = PHOTOS[name]
    out, al = R, A
    deg = jaw_deg if jaw_deg is not None else (jaw_at(t) if jaw else 0.0)
    if jm is not None and deg > 0.05:
        drop = deg / 9.0 * p["lip"] * sb
        if p["hinge"]:
            M = cv2.getRotationMatrix2D((p["hinge"][0] * sb, p["hinge"][1] * sb), deg * 0.55, 1.0); M[1, 2] += drop * 0.55
        else:                                                                    # seen from the front the hinge is behind the cheek: the chin drops
            M = np.float32([[1, 0, 0], [0, 1, drop * 0.8]])
        x0, y0, x1, y1 = (np.array(p["jaw"]).min(0) * sb - 30 * sb - 4).astype(int).tolist() + (np.array(p["jaw"]).max(0) * sb + 60 * sb + 4).astype(int).tolist()
        x0, y0 = max(0, x0), max(0, y0); x1, y1 = min(R.shape[1], x1), min(R.shape[0], y1)
        sub = R[y0:y1, x0:x1]
        moved = cv2.warpAffine(R, M, (x1, y1), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)[y0:y1, x0:x1]
        mj = cv2.warpAffine(jm, M, (x1, y1))[y0:y1, x0:x1, None]
        o = sub.copy()
        top = np.array(p["jaw"][:5], np.float32) * sb - [x0, y0]
        cav = np.vstack([top, top[::-1] + [0, drop + 3 * sb]]).astype(np.int32)
        cv2.fillPoly(o, [cav], (0.05, 0.04, 0.05))
        ym = top[:, 1].mean(); bw = (top[-1][0] - top[0][0]) / 8.5
        for k in range(6):                                                       # the grey servo brackets seen inside the open mouth
            x = top[0][0] + (top[-1][0] - top[0][0]) * (k + 0.6) / 7.0
            cv2.rectangle(o, (int(x), int(ym + 2 * sb)), (int(x + bw), int(ym + 2 * sb + min(9 * sb * p["lip"] / 46, drop * 0.4))), (0.30, 0.31, 0.33), -1)
        out = R.copy(); out[y0:y1, x0:x1] = o * (1 - mj) + moved * mj
    if abs(nod) > 0.01 or abs(tilt) > 0.01:
        nx, ny = p["neck"][0] * sb, p["neck"][1] * sb
        M = cv2.getRotationMatrix2D((nx, ny), tilt, 1.0); M[1, 2] += nod * 5 * sb
        rot = cv2.warpAffine(out, M, (out.shape[1], out.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        ra = cv2.warpAffine(al, M, (al.shape[1], al.shape[0]))
        out = out * (1 - hm[..., None]) + rot * hm[..., None]; al = al * (1 - hm) + ra * hm
    return out, al, sb, deg

# ------------------------------------------------------------------ the room (static layers cached per seed, moved by the camera)
_room = {}
def _bulbs(L, pts, rad, col):
    for (x, y), r, c in zip(pts, rad, col): cv2.circle(L, (int(x), int(y)), max(1, int(r)), tuple(float(v) for v in c), -1, cv2.LINE_AA)
def room_layers(seed):
    if seed in _room: return _room[seed]
    r = np.random.default_rng(seed); M = 420
    Wb, Hb = W + 2 * M, PH
    xx = np.arange(Wb)[None, :].astype(np.float32); yy = np.arange(Hb)[:, None].astype(np.float32)
    base = np.zeros((Hb, Wb, 3), np.float32) + np.array([0.012, 0.010, 0.012])
    wash = np.exp(-(((xx - Wb / 2) / 760) ** 2) - (((yy - Hb * 0.50) / 560) ** 2))        # spill of the stage light on a brick back wall
    bh = 24; brick = np.zeros((Hb, Wb), np.float32)
    for row in range(Hb // bh + 1):
        off = (row % 2) * 30
        for c in range(-1, Wb // 60 + 1):
            x0_ = c * 60 + off; cv2.rectangle(brick, (x0_ + 2, row * bh + 2), (x0_ + 57, row * bh + bh - 2), float(r.uniform(0.45, 1.0)), -1)
    brick = cv2.GaussianBlur(brick * (0.85 + 0.3 * cv2.resize(r.random((Hb // 40, Wb // 40)).astype(np.float32), (Wb, Hb))), (0, 0), 2.6)
    base += (wash * (0.25 + 0.75 * brick))[..., None] * np.array([0.13, 0.075, 0.045])
    for xs in (0.13, 0.87):                                                           # two dim wall sconces left and right
        g = np.exp(-(((xx - Wb * xs) / 140) ** 2) - (((yy - Hb * 0.36) / 210) ** 2))
        base += g[..., None] * np.array([0.10, 0.055, 0.025])
    far = np.zeros((Hb, Wb, 3), np.float32); mid = np.zeros_like(far)
    WARM = np.array([1.0, 0.62, 0.30]); AMB = np.array([1.0, 0.78, 0.50])
    for L, n, y0, sag, rr, k in ((far, 34, 0.10, 0.07, (4, 7), 0.9), (mid, 18, 0.03, 0.10, (10, 16), 0.6)):   # festoon strings sagging across the room
        xs_ = np.linspace(-0.05, 1.05, n) * Wb + r.uniform(-12, 12, n)
        u = (xs_ / Wb - 0.5) * 2; ys_ = Hb * (y0 + sag * (1 - u ** 2)) + r.uniform(-4, 4, n)
        _bulbs(L, zip(xs_, ys_), r.uniform(*rr, n), [(WARM if r.random() < 0.7 else AMB) * r.uniform(0.5, 1.0) * k for _ in range(n)])
    for cx in (0.06, 0.94):                                                           # back-bar bottles: clusters at the far left and right
        n = 26
        pts = [(Wb * (cx + r.normal(0, 0.035)), Hb * r.choice([0.30, 0.47]) - r.uniform(4, 40)) for _ in range(n)]
        cols = [np.array([1.0, 0.55, 0.22]) * r.uniform(0.2, 0.6) if r.random() < 0.75 else np.array([0.25, 0.65, 0.70]) * r.uniform(0.2, 0.5) for _ in range(n)]
        _bulbs(far, pts, r.uniform(3, 8, n), cols)
        shelf = np.zeros((Hb, Wb), np.float32)
        for y in (0.30, 0.47): cv2.line(shelf, (int(Wb * (cx - 0.09)), int(Hb * y)), (int(Wb * (cx + 0.09)), int(Hb * y)), 1.0, 5)
        base += cv2.GaussianBlur(shelf, (0, 0), 10)[..., None] * np.array([0.22, 0.12, 0.05])
    neon = np.zeros((Hb, Wb, 3), np.float32)                                            # one soft neon line on the right wall
    cv2.ellipse(neon, (int(Wb * 0.80), int(Hb * 0.18)), (90, 26), 0, 200, 340, (0.15, 0.55, 0.60), 3, cv2.LINE_AA)
    far = cv2.GaussianBlur(far, (0, 0), 4) + cv2.GaussianBlur(far, (0, 0), 18) * 0.7 + cv2.GaussianBlur(neon, (0, 0), 6) + cv2.GaussianBlur(neon, (0, 0), 30) * 1.5
    for px in (0.10, 0.27, 0.73, 0.90):                                              # pendant lamps over the tables, left and right
        x = int(Wb * px + r.uniform(-40, 40)); yb = int(Hb * r.uniform(0.30, 0.40))
        cv2.line(mid, (x, 0), (x, yb - 30), (0.05, 0.04, 0.035), 2)
        cv2.fillPoly(mid, [np.array([(x - 10, yb - 32), (x + 10, yb - 32), (x + 34, yb), (x - 34, yb)], np.int32)], (0.06, 0.045, 0.035))
        cv2.ellipse(mid, (x, yb + 2), (12, 7), 0, 0, 360, (1.3, 0.8, 0.4), -1, cv2.LINE_AA)
        pool = np.exp(-(((xx - x) / 260) ** 2) - (((yy - yb - 160) / 200) ** 2))
        base += pool[..., None] * np.array([0.10, 0.06, 0.03])
    mid = cv2.GaussianBlur(mid, (0, 0), 5) + cv2.GaussianBlur(mid, (0, 0), 24) * 0.6
    _room[seed] = (base, far, mid, M)
    return _room[seed]
def crop_layer(L, M, dx):
    x0 = int(np.clip(M + dx, 0, L.shape[1] - W)); return L[:, x0:x0 + W]
_haze = {}
def haze(t, seed):
    k = int(t * 0.8); f = t * 0.8 - k
    def fld(j):
        if (seed, j) not in _haze:
            if len(_haze) > 8: _haze.clear()
            _haze[(seed, j)] = cv2.resize(np.random.default_rng(seed * 1000 + j).random((5, 9)).astype(np.float32), (W, PH), interpolation=cv2.INTER_CUBIC)
        return _haze[(seed, j)]
    return np.clip(fld(k) * (1 - f) + fld(k + 1) * f, 0, 1)
def room(t, cam_x, seed=3, spot=1.0):
    base, far, mid, M = room_layers(seed)
    flick = 0.92 + 0.08 * math.sin(t * 0.7)
    return crop_layer(base, M, -cam_x * 0.2) + crop_layer(far, M, -cam_x * 0.25) * flick + crop_layer(mid, M, -cam_x * 0.45)

_XX = np.arange(W)[None, :].astype(np.float32); _YV = np.arange(PH)[:, None].astype(np.float32)
def beam(t, cx, top_y, spot, hz, width=1.0):
    """The top spot from the rig above the stage: a cone in the haze, narrow at the top, landing on her head and shoulders."""
    half = (70 + np.clip(_YV - top_y, 0, None) * 0.42) * width
    d = np.abs(_XX - cx) / half
    cone = np.clip(1 - d, 0, 1) ** 0.8 * (1 - 0.5 * np.clip(_YV / PH, 0, 1))
    return cone[..., None] * np.array([1.0, 0.82, 0.60]) * 0.10 * spot * (0.55 + 0.9 * hz[..., None])
def backlights(t, cx, hz, k=1.0):
    """Two cool shafts from behind her, crossing in the haze: depth behind the stage."""
    out = np.zeros((PH, W), np.float32)
    for sx, ang, ph in ((cx - 700, 0.42, 0.0), (cx + 760, -0.38, 1.7)):
        a = ang + 0.04 * math.sin(t * 0.25 + ph)
        px = sx + (_YV + 60) * math.tan(a)                                             # centre line of the shaft
        half = 40 + (_YV + 60) * 0.22
        out += np.clip(1 - np.abs(_XX - px) / half, 0, 1) ** 1.5 * (1 - 0.6 * _YV / PH)
    return out[..., None] * np.array([0.35, 0.55, 0.75]) * 0.075 * k * (0.5 + hz[..., None])
_dust = np.random.default_rng(11).random((420, 4)).astype(np.float32)
def dust(t, cx, spot, width=1.0):
    """Dust motes drifting in the beam (in front of her), slightly out of focus."""
    D = np.zeros((PH, W, 3), np.float32)
    x = cx + (_dust[:, 0] - 0.5) * 900 * width + np.sin(t * 0.3 + _dust[:, 2] * 9) * 30
    y = (_dust[:, 1] * PH + t * (8 + 14 * _dust[:, 3])) % PH
    inside = np.clip(1 - np.abs(x - cx) / ((90 + y * 0.55) * width), 0, 1)
    b = inside * (0.15 + 0.85 * _dust[:, 3]) * (0.5 + 0.5 * np.sin(t * 2 + _dust[:, 2] * 30)) * 0.9 * spot
    splat(D, x, y, np.tile(np.array([1.0, 0.85, 0.65], np.float32), (len(x), 1)), b.astype(np.float32))
    return cv2.GaussianBlur(D, (0, 0), 1.6) * 2.2

# ------------------------------------------------------------------ the audience
_crowd = {}
def crowd_people(seed, n):
    """Standing people at the foot of the stage, seen from behind, in metres relative to the stage centre."""
    if (seed, n) in _crowd: return _crowd[(seed, n)]
    r = np.random.default_rng(seed); P = []
    for i in range(n):
        P.append(dict(x=r.uniform(-2.6, 2.6), depth=r.uniform(1.12, 1.45), h=r.uniform(1.58, 1.82), hair=r.choice(["short", "long", "bun", "cap"], p=[0.4, 0.3, 0.15, 0.15]),
                      phone=r.random() < 0.35, side=r.choice([-1, 1]), ph=r.uniform(0, 6)))
    P.sort(key=lambda d: d["depth"]); _crowd[(seed, n)] = P
    return P
def audience(t, cam_x, px_m, floor_y, robot_cx, seed=5, n=9, phones=True):
    """Silhouettes with a warm rim from the followspot, a few raised phones. px_m: screen px per metre at the robot's depth."""
    A = np.zeros((PH, W), np.float32); G = np.zeros((PH, W, 3), np.float32)
    for d in crowd_people(seed, n):
        k = d["depth"]; s = px_m * k
        fx = robot_cx + d["x"] * px_m * 1.05 - cam_x * (k - 1) * 1.4
        fy = floor_y + (k - 1) * px_m * 1.2                                            # nearer -> feet lower on screen
        hy = fy - d["h"] * s                                                            # top of head
        if hy > PH + 10 or fx < -s or fx > W + s: continue
        sw = 0.02 * s * math.sin(t * 0.7 + d["ph"])
        hw, hh = 0.085 * s, 0.115 * s
        cx, cy = fx + sw, hy + hh
        cv2.ellipse(A, (int(cx), int(cy)), (int(hw), int(hh)), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
        if d["hair"] == "long": cv2.ellipse(A, (int(cx), int(cy + hh * 0.9)), (int(hw * 1.05), int(hh * 1.1)), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
        if d["hair"] == "bun": cv2.circle(A, (int(cx), int(hy + hh * 0.05)), int(hw * 0.5), 1.0, -1, cv2.LINE_AA)
        if d["hair"] == "cap": cv2.ellipse(A, (int(cx), int(cy - hh * 0.25)), (int(hw * 1.15), int(hh * 0.55)), 0, 180, 360, 1.0, -1, cv2.LINE_AA)
        cv2.rectangle(A, (int(cx - hw * 0.45), int(cy + hh * 0.6)), (int(cx + hw * 0.45), int(cy + hh * 1.6)), 1.0, -1)     # neck
        cv2.ellipse(A, (int(cx), int(cy + hh * 2.6)), (int(0.23 * s), int(0.16 * s)), 0, 0, 360, 1.0, -1, cv2.LINE_AA)       # shoulders
        cv2.rectangle(A, (int(cx - 0.21 * s), int(cy + hh * 2.6)), (int(cx + 0.21 * s), PH + 10), 1.0, -1)
        if phones and d["phone"]:
            sx, sy = cx + d["side"] * 0.17 * s, cy + hh * 2.2
            px, py = cx + d["side"] * 0.10 * s, hy - 0.10 * s
            cv2.line(A, (int(sx), int(sy)), (int(px), int(py + 0.06 * s)), 1.0, max(2, int(0.06 * s)), cv2.LINE_AA)
            pw, phh = 0.022 * s, 0.042 * s
            cv2.rectangle(A, (int(px - pw * 1.2), int(py - phh * 1.15)), (int(px + pw * 1.2), int(py + phh * 1.15)), 1.0, -1)
            cv2.rectangle(G, (int(px - pw), int(py - phh)), (int(px + pw), int(py + phh)), (0.13, 0.16, 0.21), -1)
    A = cv2.GaussianBlur(A, (0, 0), 3.0)
    rim = np.clip(A - np.vstack([np.zeros((4, W), np.float32), A[:-4]]), 0, 1)          # top edges catch the spot
    rim *= np.clip(1 - np.abs(np.arange(W)[None, :] - robot_cx) / (W * 0.7), 0.3, 1)    # stronger near the light
    col = np.zeros((PH, W, 3), np.float32) + np.array([0.014, 0.012, 0.013]) + rim[..., None] * np.array([0.80, 0.55, 0.34]) * 0.8
    G = cv2.GaussianBlur(G, (0, 0), 1.2); G = G + cv2.GaussianBlur(G, (0, 0), 10) * 0.8
    return col, A, G

def patrons(t, cam_x, n=3, seed=5, size=1.0):
    """Big, very out-of-focus heads and shoulders right in front of the lens (we sit among the audience)."""
    r = np.random.default_rng(seed)
    a = np.zeros((PH, W), np.float32)
    for i in range(n):
        x = r.uniform(0.05, 0.95) * W - cam_x * 1.9
        hr = r.uniform(130, 170) * size
        cy = PH - hr * r.uniform(0.1, 0.5)
        sway = 6 * math.sin(t * 0.5 + i * 2)
        cv2.ellipse(a, (int(x + sway), int(cy)), (int(hr * 0.78), int(hr)), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
        cv2.ellipse(a, (int(x + sway * 0.5), int(cy + hr * 1.9)), (int(hr * 2.4), int(hr * 1.3)), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
    a = cv2.GaussianBlur(a, (0, 0), 22 * size)
    rim = np.clip(a - np.vstack([np.zeros((14, W), np.float32), a[:-14]]), 0, 1)
    col = np.zeros((PH, W, 3), np.float32) + np.array([0.006, 0.005, 0.006]) + rim[..., None] * np.array([0.60, 0.40, 0.25]) * 0.8
    return col, np.clip(a * 1.1, 0, 1)

# ------------------------------------------------------------------ head motion (also exported as the animation reference channels)
def head_motion(t, phase=0.0):
    """nod: degrees-ish pitch (+ = down) following phrasing and voice; tilt: slow roll in degrees."""
    lv = vocal_level(t)
    return 0.8 * math.sin((t + phase) * 0.9) + 1.2 * lv, 0.8 * math.sin((t + phase) * 0.45)
def eye_glow(t): return 0.20 + 0.70 * vocal_level(t)

# ------------------------------------------------------------------ one shot
def shot(t, name, t0, t1, fr, spot=1.0, nod_phase=0.0, crowd=12, fg=0, fg_size=1.0, seed=3, exposure=1.0, amb=0.10, beam_w=1.0, phones=True, key_h=2.4, key_w=3.0, back=1.0, tear=None, glow_k=1.0):
    """fr: framing dict with start/end values: h (photo height on screen, px), cx (photo centre x), top (photo top y), camx (camera x)."""
    u = ease((t - t0) / max(0.01, t1 - t0))
    F = {k: lerp(fr[k + "0"], fr[k + "1"], u) for k in ("h", "cx", "top", "camx")}
    lv = vocal_level(t)
    nod, tilt = head_motion(t, nod_phase)
    p = PHOTOS[name]; srgb, _ = source(name)
    s = F["h"] / srgb.shape[0]
    R, A, sb, deg = posed(name, s, t, nod, tilt)
    hz = haze(t, seed)
    img = room(t, F["camx"], seed=seed, spot=spot) + backlights(t, W / 2 - F["camx"] * 0.3, hz, back)
    x0 = int(F["cx"] - R.shape[1] / 2 - F["camx"]); y0 = int(F["top"])
    hx, hy = x0 + p["head"][0] * sb, y0 + p["head"][1] * sb; px_m = p["ppm"] * sb
    L = np.zeros((PH, W, 3), np.float32); AL = np.zeros((PH, W), np.float32)
    sx0, sy0 = max(0, -x0), max(0, -y0); dx0, dy0 = max(0, x0), max(0, y0)
    ww, hh = min(R.shape[1] - sx0, W - dx0), min(R.shape[0] - sy0, PH - dy0)
    if ww > 0 and hh > 0:
        L[dy0:dy0 + hh, dx0:dx0 + ww] = R[sy0:sy0 + hh, sx0:sx0 + ww]; AL[dy0:dy0 + hh, dx0:dx0 + ww] = A[sy0:sy0 + hh, sx0:sx0 + ww]
    # light: one warm followspot on the face and chest, everything else falls into the dark
    xx = np.arange(W)[None, :].astype(np.float32); yv = np.arange(PH)[:, None].astype(np.float32)
    hr = p["head"][3] * sb                                                              # light sized in head radii
    key = np.exp(-(((xx - hx) / (key_w * hr)) ** 2) - (np.clip(yv - hy, 0, None) / (key_h * hr)) ** 2 - (np.clip(hy - 1.2 * hr - yv, 0, None) / (1.5 * hr)) ** 2)
    light = amb + (1 - amb) * key * spot
    lit = L * light[..., None] * np.array([1.05, 0.96, 0.84]) * exposure
    lum = lit.mean(-1, keepdims=True); lit = lum + (lit - lum) * 0.85
    edge = np.clip(AL - cv2.GaussianBlur(AL, (0, 0), 4), 0, 1)
    sh = np.zeros_like(edge); sh[:, :-3] = edge[:, 3:]; sh2 = np.zeros_like(edge); sh2[3:] = edge[:-3]
    lit += (sh * AL)[..., None] * np.array([0.25, 0.60, 0.70]) * 0.30 + (sh2 * AL * key)[..., None] * np.array([1.0, 0.8, 0.55]) * 0.35   # cool rim left, warm top rim
    for ex, ey in p["eyes"]:                                                            # lens eyes glow with the voice
        X, Y = int(x0 + ex * sb), int(y0 + ey * sb); r = int(max(6, 70 * sb))
        if -r <= X < W + r and -r <= Y < PH + r:
            ya, yb, xa, xb = max(0, Y - r), min(PH, Y + r), max(0, X - r), min(W, X + r)
            gy, gx = np.mgrid[ya:yb, xa:xb].astype(np.float32)
            g = np.exp(-((gx - X) ** 2 + (gy - Y) ** 2) / (2 * (max(2.0, 18 * sb)) ** 2))
            lit[ya:yb, xa:xb] += g[..., None] * np.array([0.35, 0.50, 1.0]) * eye_glow(t) * glow_k
    if tear is not None and p.get("tear"):                                              # a bead of light runs from the eye down the cheek seam
        tu = (t - tear) / 2.2
        if 0 < tu < 1.35:
            path = np.array(p["tear"], np.float32) * sb + [x0, y0]
            for j in range(26):
                s_ = min(1.0, eout(tu)) - j * 0.012
                if s_ < 0: break
                idx = s_ * (len(path) - 1); i0 = min(int(idx), len(path) - 2); f_ = idx - i0
                X, Y = path[i0] * (1 - f_) + path[i0 + 1] * f_
                X, Y = int(X), int(Y); r = int(max(5, 40 * sb))
                if not (r <= X < W - r and r <= Y < PH - r): continue
                gy, gx = np.mgrid[Y - r:Y + r, X - r:X + r].astype(np.float32)
                sig = max(1.2, (6 if j == 0 else 3) * sb)
                k_ = (1.0 if j == 0 else 0.35 * (1 - j / 26)) * (1 - ease((tu - 1.0) / 0.35))
                lit[Y - r:Y + r, X - r:X + r] += np.exp(-((gx - X) ** 2 + (gy - Y) ** 2) / (2 * sig ** 2))[..., None] * np.array([0.75, 0.88, 1.0]) * k_ * 1.4
    img = img * (1 - AL[..., None]) + lit * AL[..., None]
    floor_y = y0 + p["floor"] * sb
    if crowd:
        col, pa, G = audience(t, F["camx"], px_m, floor_y, x0 + R.shape[1] / 2, seed=seed + 1, n=crowd, phones=phones)
        img = img * (1 - pa[..., None]) + col * pa[..., None] + G
    img = img + beam(t, hx, -40, spot, hz, beam_w) + dust(t, hx, spot, beam_w)
    img = img + hz[..., None] * np.array([0.020, 0.016, 0.014])
    if fg:
        col, pa = patrons(t, F["camx"], n=fg, seed=seed + 2, size=fg_size)
        img = img * (1 - pa[..., None]) + col * pa[..., None]
    return img + cv2.GaussianBlur(img, (0, 0), 16) * 0.10
